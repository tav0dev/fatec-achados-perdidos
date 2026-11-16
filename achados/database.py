from flask import current_app
from pymongo import ASCENDING, MongoClient


def collection():
    return current_app.extensions["achados_collection"]


def connect_database(app):
    client = MongoClient(app.config["MONGO_URI"], serverSelectionTimeoutMS=3000, tz_aware=True)
    app.extensions["achados_client"] = client
    app.extensions["achados_collection"] = client[app.config["MONGO_DB"]]["ocorrencias"]


def create_indexes(coll):
    coll.create_index([("codigo", ASCENDING)], unique=True)
    coll.create_index([("status", ASCENDING), ("data_ocorrencia", ASCENDING)])
    coll.create_index([("categoria", ASCENDING)])
    coll.create_index([("tipo", ASCENDING), ("local.nome", ASCENDING)])
