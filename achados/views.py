import hmac
import re
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from bson import json_util
from flask import Blueprint, Response, abort, flash, redirect, render_template, request, session, url_for
from pymongo.errors import DuplicateKeyError

from .database import collection
from .identity import BRAND_GUIDE_URL, LOGO_PATH, LOGO_URL, UNIT_URL
from .queries import report_definitions
from .institutional import fatec_news
from .item_photos import item_photo, photo_catalog
from .validation import AFFILIATIONS, CATEGORIES, LOCATIONS, STATUSES, TYPES, ValidationError, form_from_document, today_utc, validate_item, validate_return

bp = Blueprint("web", __name__)


@bp.app_context_processor
def helpers():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return {
        "csrf_token": session["csrf_token"], "categories": CATEGORIES, "statuses": STATUSES,
        "types": TYPES, "affiliations": AFFILIATIONS, "locations": LOCATIONS, "today": today_utc(),
        "logo_url": url_for("static", filename="brand/fatec-itapetininga.png") if LOGO_PATH.exists() else LOGO_URL,
        "unit_url": UNIT_URL, "brand_guide_url": BRAND_GUIDE_URL, "fatec_news": fatec_news(),
        "item_photo": item_photo, "photo_credits": photo_catalog(),
    }


@bp.before_request
def check_csrf():
    if request.method == "POST":
        token = session.get("csrf_token", "")
        supplied = request.form.get("csrf_token", "")
        if not token or not hmac.compare_digest(token.encode(), supplied.encode()):
            abort(400, description="O formulário expirou. Recarregue a página e tente novamente.")


def get_item(code):
    doc = collection().find_one({"codigo": code})
    if doc is None:
        abort(404)
    return doc


@bp.get("/")
def dashboard():
    coll = collection()
    stats = {row["_id"]: row["total"] for row in coll.aggregate([{"$group": {"_id": "$status", "total": {"$sum": 1}}}])}
    found = coll.count_documents({"tipo": "encontrado", "status": "aguardando"})
    lost = coll.count_documents({"tipo": "perdido", "status": "aguardando"})
    late = coll.count_documents({"status": "aguardando", "data_ocorrencia": {"$lte": today_utc() - timedelta(days=7)}})
    categories = list(coll.aggregate(report_definitions()[1]["pipeline"]))
    recent = list(coll.find({"status": "aguardando"}).sort([("criado_em", -1), ("codigo", 1)]).limit(6))
    return render_template("dashboard.html", page="dashboard", stats=stats, total=sum(stats.values()),
                           found=found, lost=lost, late=late, recent=recent, category_stats=categories,
                           max_category=max([row["registros"] for row in categories], default=1))


@bp.get("/itens")
def items():
    query = {}
    term = request.args.get("q", "").strip()[:100]
    category = request.args.get("categoria", "")
    status = request.args.get("status", "")
    kind = request.args.get("tipo", "")
    place = request.args.get("local", "").strip()[:100]
    if term:
        regex = {"$regex": re.escape(term), "$options": "i"}
        query["$or"] = [{field: regex} for field in ("codigo", "titulo", "descricao", "cor", "marca", "caracteristicas")]
    if category in CATEGORIES:
        query["categoria"] = category
    if status == "antigos":
        query.update({"status": "aguardando", "data_ocorrencia": {"$lte": today_utc() - timedelta(days=7)}})
    elif status in STATUSES:
        query["status"] = status
    if kind in TYPES:
        query["tipo"] = kind
    if place:
        query["local.nome"] = place
    if request.args.get("prioridade") == "1":
        query["prioridade"] = True
    try:
        number = max(1, int(request.args.get("pagina", 1)))
    except ValueError:
        number = 1
    count = collection().count_documents(query)
    pages = max(1, (count + 11) // 12)
    number = min(number, pages)
    docs = list(collection().find(query).sort([("criado_em", -1), ("codigo", 1)]).skip((number - 1) * 12).limit(12))
    filters = {"q": term, "categoria": category, "status": status, "tipo": kind, "local": place, "prioridade": request.args.get("prioridade", "")}
    return render_template("items.html", page="items", items=docs, total=count, filters=filters, number=number, pages=pages)


@bp.route("/itens/novo", methods=["GET", "POST"])
def create_item():
    kind = request.args.get("tipo", "encontrado")
    data = {"quantidade": 1, "status": "aguardando", "tipo": kind if kind in TYPES else "encontrado", "data_ocorrencia": today_utc().strftime("%Y-%m-%d")}
    errors = {}
    if request.method == "POST":
        data = request.form.to_dict()
        try:
            doc = validate_item(data)
            now = datetime.now(timezone.utc)
            doc.update({"codigo": "AP-" + uuid4().hex[:12].upper(), "criado_em": now, "atualizado_em": now})
            collection().insert_one(doc)
            flash("Ocorrência registrada. Um pequeno cuidado pode fazer a diferença.", "success")
            return redirect(url_for("web.detail", code=doc["codigo"]))
        except ValidationError as error:
            errors = error.errors
        except DuplicateKeyError:
            errors = {"geral": "O protocolo gerado já existe. Tente salvar novamente."}
    return render_template("form.html", page="items", data=data, errors=errors, editing=False), 422 if errors else 200


@bp.get("/itens/<code>")
def detail(code):
    return render_template("detail.html", page="items", item=get_item(code), errors={}, return_data={"data_devolucao": today_utc().strftime("%Y-%m-%d")})


@bp.route("/itens/<code>/editar", methods=["GET", "POST"])
def edit_item(code):
    item = get_item(code)
    data = form_from_document(item)
    errors = {}
    if request.method == "POST":
        data = request.form.to_dict()
        try:
            changes = validate_item(data)
            changes["atualizado_em"] = datetime.now(timezone.utc)
            result = collection().update_one({"codigo": code}, {"$set": changes})
            if not result.matched_count:
                abort(404)
            flash("Informações do item atualizadas.", "success")
            return redirect(url_for("web.detail", code=code))
        except ValidationError as error:
            errors = error.errors
    return render_template("form.html", page="items", data=data, errors=errors, editing=True, code=code), 422 if errors else 200


@bp.post("/itens/<code>/devolver")
def return_item(code):
    item = get_item(code)
    if item["status"] != "aguardando":
        flash("Este registro já foi concluído. Confira sua situação antes de alterar.", "error")
        return redirect(url_for("web.detail", code=code))
    try:
        returned = validate_return(request.form, item["data_ocorrencia"])
    except ValidationError as error:
        return render_template("detail.html", page="items", item=item, errors=error.errors, return_data=request.form), 422
    result = collection().update_one({"codigo": code, "status": "aguardando"}, {"$set": {**returned, "status": "devolvido", "atualizado_em": datetime.now(timezone.utc)}})
    flash("Mais um reencontro! A devolução foi registrada." if result.matched_count else "O registro já foi atualizado. Recarregue para conferir.", "success" if result.matched_count else "error")
    return redirect(url_for("web.detail", code=code))


@bp.post("/itens/<code>/excluir")
def delete_item(code):
    get_item(code)
    collection().delete_one({"codigo": code})
    flash("Ocorrência excluída.", "success")
    return redirect(url_for("web.items"))


@bp.get("/consultas")
def reports():
    definitions = [{**report, "results": list(collection().aggregate(report["pipeline"])), "code": json_util.dumps(report["pipeline"], indent=2, ensure_ascii=False)} for report in report_definitions()]
    return render_template("reports.html", page="reports", reports=definitions)


@bp.get("/exportar.json")
def export_json():
    docs = list(collection().find({}, {"_id": 0}).sort("codigo", 1))
    return Response(json_util.dumps(docs, ensure_ascii=False, indent=2), mimetype="application/json", headers={"Content-Disposition": 'attachment; filename="fatec_achados_perdidos.json"'})


@bp.get("/sobre")
def about():
    return render_template("about.html", page="about")


@bp.get("/design-system")
def design_system():
    return render_template("design_system.html", page="design")


@bp.get("/emprestimos")
def legacy_list():
    return redirect(url_for("web.items"), code=301)
