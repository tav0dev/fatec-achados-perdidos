"""Ferramentas de preparação. Execute `python manage.py --help`."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def export_files():
    from achados.seed_data import generate_documents
    from achados.queries import report_definitions
    from datetime import datetime

    def extended_json(obj):
        if isinstance(obj, datetime):
            return {"$date": obj.isoformat(timespec="milliseconds").replace("+00:00", "Z")}
        raise TypeError(f"Tipo não suportado: {type(obj)}")

    documents = generate_documents()
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data/ocorrencias.json").write_text(json.dumps(documents, ensure_ascii=False, indent=2, default=extended_json) + "\n", encoding="utf-8")
    queries = {item["slug"]: item["pipeline"] for item in report_definitions()}
    (ROOT / "data/consultas.json").write_text(json.dumps(queries, ensure_ascii=False, indent=2, default=extended_json) + "\n", encoding="utf-8")
    print(f"JSON exportado: {len(documents)} documentos e quatro consultas em data/.")


def initialize_database():
    import os
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
    from achados.database import create_indexes
    from achados.queries import report_definitions
    from achados.seed_data import generate_documents

    uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    database_name = os.environ.get("MONGO_DB", "fatec_achados_perdidos")
    try:
        with MongoClient(uri, serverSelectionTimeoutMS=4000, tz_aware=True) as client:
            client.admin.command("ping")
            database = client[database_name]
            schema = json.loads((ROOT / "data/schema.json").read_text(encoding="utf-8"))
            if "ocorrencias" not in database.list_collection_names():
                database.create_collection("ocorrencias", validator=schema, validationLevel="strict")
            else:
                database.command("collMod", "ocorrencias", validator=schema, validationLevel="strict")
            coll = database["ocorrencias"]
            create_indexes(coll)
            if coll.count_documents({}) == 0:
                coll.insert_many(generate_documents())
                print("Carga inicial criada: 36 ocorrências fictícias.")
            else:
                print("A coleção já possui dados. Os registros existentes foram preservados.")
            print(f"MongoDB conectado. Banco: {database_name}; coleção: ocorrencias; documentos: {coll.count_documents({})}.")
            for report in report_definitions():
                list(coll.aggregate(report["pipeline"]))
            print("As quatro consultas foram executadas com sucesso no MongoDB.")
        from scripts.sync_identity import ensure_logo
        ensure_logo()
    except PyMongoError as error:
        print(f"Não foi possível preparar o MongoDB ({type(error).__name__}).", file=sys.stderr)
        if type(error).__name__ in ("OperationFailure", "WriteError", "BulkWriteError"):
            print(f"O servidor recusou uma operação de configuração ou validação. Código: {getattr(error, 'code', 'não informado')}. Confira as permissões e o formato dos documentos.", file=sys.stderr)
        else:
            print("Inicie o serviço MongoDB no Windows e teste localhost:27017 no Compass. Confira MONGO_URI e MONGO_DB, se configurados.", file=sys.stderr)
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description="Preparação e documentação do Achados e Perdidos — Fatec Itapetininga")
    parser.add_argument("command", choices=["init", "export", "pdf", "identity"])
    parser.add_argument("--github", help="URL do repositório já publicado, para incluir no PDF")
    args = parser.parse_args()
    if args.command == "init":
        return initialize_database()
    if args.command == "export":
        export_files()
    if args.command == "identity":
        from scripts.sync_identity import ensure_logo
        return 0 if ensure_logo() else 1
    if args.command == "pdf":
        from scripts.generate_report import build_report
        build_report(args.github)
    return 0


if __name__ == "__main__":
    sys.exit(main())
