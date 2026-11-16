"""Validação de ocorrências e da comprovação de propriedade na devolução."""
import re
from datetime import datetime, timezone

CATEGORIES = ("Eletrônicos", "Documentos", "Chaves", "Roupas e acessórios", "Materiais de estudo", "Garrafas e recipientes", "Outros")
STATUSES = {"aguardando": "Aguardando identificação", "devolvido": "Devolvido", "encerrado": "Encerrado"}
TYPES = {"encontrado": "Achado", "perdido": "Perdido"}
AFFILIATIONS = ("Aluno", "Docente", "Servidor", "Visitante")
LOCATIONS = ("Biblioteca", "Laboratórios", "Salas de aula", "Cantina", "Pátio", "Estacionamento", "Outros espaços")


class ValidationError(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("Confira os campos destacados.")


def today_utc():
    return datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)


def validate_return(form, occurrence_date):
    errors = {}
    name = str(form.get("retirante_nome", "")).strip()
    proof = str(form.get("comprovacao", "")).strip()
    if not 3 <= len(name) <= 100:
        errors["retirante_nome"] = "Informe o nome de quem recuperou o item (3 a 100 caracteres)."
    if not 10 <= len(proof) <= 500:
        errors["comprovacao"] = "Descreva como a propriedade foi confirmada (10 a 500 caracteres)."
    try:
        returned = datetime.strptime(str(form.get("data_devolucao", "")), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if returned < occurrence_date:
            errors["data_devolucao"] = "A devolução não pode ser anterior à ocorrência."
        if returned > today_utc():
            errors["data_devolucao"] = "A devolução não pode estar no futuro."
    except ValueError:
        returned = None
        errors["data_devolucao"] = "Informe uma data válida."
    if errors:
        raise ValidationError(errors)
    return {"retirante": {"nome": name, "comprovacao": proof}, "data_devolucao": returned}


def validate_item(form):
    errors = {}

    def text(key, label, limit=160, required=True, minimum=1):
        value = str(form.get(key, "")).strip()
        if required and len(value) < minimum:
            errors[key] = f"Informe {label}."
        if len(value) > limit:
            errors[key] = f"Use no máximo {limit} caracteres."
        return value

    title = text("titulo", "o nome do item", 100, minimum=3)
    description = text("descricao", "uma descrição com pelo menos 10 caracteres", 1000, minimum=10)
    color = text("cor", "a cor", 50, required=False)
    brand = text("marca", "a marca", 60, required=False)
    location = text("local_nome", "o local da ocorrência", 100)
    block = text("bloco", "o bloco ou setor", 50, required=False)
    reference = text("referencia", "a referência do local", 160, required=False)
    name = text("relator_nome", "o nome de quem registrou", 100, minimum=3)
    email = text("email", "um e-mail de contato", 120)
    if email and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        errors["email"] = "Informe um e-mail válido."
    affiliation = str(form.get("vinculo", ""))
    if affiliation not in AFFILIATIONS:
        errors["vinculo"] = "Selecione um vínculo com a Fatec."
    category = str(form.get("categoria", ""))
    if category not in CATEGORIES:
        errors["categoria"] = "Selecione uma categoria válida."
    kind = str(form.get("tipo", ""))
    if kind not in TYPES:
        errors["tipo"] = "Selecione perdido ou encontrado."
    status = str(form.get("status", "aguardando"))
    if status not in STATUSES:
        errors["status"] = "Selecione uma situação válida."
    try:
        quantity = int(str(form.get("quantidade", "")))
        if not 1 <= quantity <= 100:
            raise ValueError
    except ValueError:
        quantity = 0
        errors["quantidade"] = "Informe um inteiro entre 1 e 100."
    try:
        occurred = datetime.strptime(str(form.get("data_ocorrencia", "")), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if occurred > today_utc():
            errors["data_ocorrencia"] = "A ocorrência não pode estar no futuro."
    except ValueError:
        occurred = None
        errors["data_ocorrencia"] = "Informe uma data válida."
    custody = text("local_guarda", "onde o item está guardado", 120, required=kind == "encontrado")
    tags = list(dict.fromkeys(x.strip().lower() for x in str(form.get("caracteristicas", "")).split(",") if x.strip()))
    if len(tags) > 12 or any(len(x) > 40 for x in tags):
        errors["caracteristicas"] = "Use até 12 características de até 40 caracteres cada."
    notes = text("observacoes", "as observações", 1000, required=False)
    returned = {"retirante": {"nome": "", "comprovacao": ""}, "data_devolucao": None}
    if status == "devolvido" and occurred:
        try:
            returned = validate_return(form, occurred)
        except ValidationError as error:
            errors.update(error.errors)
    elif form.get("data_devolucao") or form.get("retirante_nome") or form.get("comprovacao"):
        errors["data_devolucao"] = "Preencha dados de devolução somente para itens devolvidos."
    if errors:
        raise ValidationError(errors)
    checked = lambda key: form.get(key) in ("on", "true", "1", True)
    return {
        "titulo": title, "descricao": description, "categoria": category, "tipo": kind,
        "status": status, "data_ocorrencia": occurred,
        "local": {"nome": location, "bloco": block, "referencia": reference},
        "relator": {"nome": name, "email": email, "vinculo": affiliation},
        "caracteristicas": tags, "quantidade": quantity, "cor": color, "marca": brand,
        "local_guarda": custody, "prioridade": checked("prioridade"),
        "contato_autorizado": checked("contato_autorizado"), **returned, "observacoes": notes,
    }


def form_from_document(doc):
    return {
        **doc, "relator_nome": doc["relator"]["nome"], "email": doc["relator"]["email"],
        "vinculo": doc["relator"]["vinculo"], "local_nome": doc["local"]["nome"],
        "bloco": doc["local"]["bloco"], "referencia": doc["local"]["referencia"],
        "caracteristicas": ", ".join(doc["caracteristicas"]),
        "data_ocorrencia": doc["data_ocorrencia"].strftime("%Y-%m-%d"),
        "data_devolucao": doc["data_devolucao"].strftime("%Y-%m-%d") if doc.get("data_devolucao") else "",
        "retirante_nome": doc["retirante"]["nome"], "comprovacao": doc["retirante"]["comprovacao"],
    }
