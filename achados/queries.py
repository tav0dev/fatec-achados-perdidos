"""Quatro consultas MongoDB para a gestão de achados e perdidos."""
from datetime import datetime, timedelta, timezone


def report_definitions(now=None):
    today = (now or datetime.now(timezone.utc)).replace(hour=0, minute=0, second=0, microsecond=0)
    return [
        {
            "slug": "pendentes", "title": "Pendentes há pelo menos 7 dias", "icon": "clock",
            "description": "Itens perdidos ou encontrados ainda sem resolução, registrados há sete dias ou mais. O tempo é calculado a partir da data da ocorrência.",
            "operators": "$and · $in · $lte · $match · $project · $subtract · $divide · $floor",
            "columns": [("codigo", "Protocolo"), ("titulo", "Item"), ("local", "Local"), ("dias", "Dias em aberto"), ("prioridade", "Prioritário")],
            "pipeline": [
                {"$match": {"$and": [{"status": "aguardando"}, {"tipo": {"$in": ["perdido", "encontrado"]}}, {"data_ocorrencia": {"$lte": today - timedelta(days=7)}}]}},
                {"$project": {"_id": 0, "codigo": 1, "titulo": 1, "local": "$local.nome", "prioridade": 1, "dias": {"$floor": {"$divide": [{"$subtract": [today, "$data_ocorrencia"]}, 86400000]}}}},
                {"$sort": {"prioridade": -1, "dias": -1, "codigo": 1}},
            ],
        },
        {
            "slug": "categorias", "title": "Itens por categoria", "icon": "grid",
            "description": "Distribui as ocorrências não encerradas por categoria e conta pendências, devoluções e unidades registradas.",
            "operators": "$nin · $match · $group · $sum · $cond · $eq · $project · $sort",
            "columns": [("categoria", "Categoria"), ("registros", "Registros"), ("pendentes", "Pendentes"), ("devolvidos", "Devolvidos"), ("unidades", "Unidades")],
            "pipeline": [
                {"$match": {"status": {"$nin": ["encerrado"]}}},
                {"$group": {"_id": "$categoria", "registros": {"$sum": 1}, "unidades": {"$sum": "$quantidade"}, "pendentes": {"$sum": {"$cond": [{"$eq": ["$status", "aguardando"]}, 1, 0]}}, "devolvidos": {"$sum": {"$cond": [{"$eq": ["$status", "devolvido"]}, 1, 0]}}}},
                {"$project": {"_id": 0, "categoria": "$_id", "registros": 1, "unidades": 1, "pendentes": 1, "devolvidos": 1}},
                {"$sort": {"registros": -1, "categoria": 1}},
            ],
        },
        {
            "slug": "locais", "title": "Ocorrências por local", "icon": "pin",
            "description": "Identifica os espaços com mais registros, separa perdidos e encontrados e apresenta a primeira e a última ocorrência de cada local.",
            "operators": "$exists · $ne · $group · $sum · $cond · $min · $max · $project",
            "columns": [("local", "Local"), ("registros", "Registros"), ("encontrados", "Encontrados"), ("perdidos", "Perdidos"), ("primeira", "Primeira ocorrência")],
            "pipeline": [
                {"$match": {"data_ocorrencia": {"$exists": True}, "status": {"$ne": "encerrado"}}},
                {"$group": {"_id": "$local.nome", "registros": {"$sum": 1}, "encontrados": {"$sum": {"$cond": [{"$eq": ["$tipo", "encontrado"]}, 1, 0]}}, "perdidos": {"$sum": {"$cond": [{"$eq": ["$tipo", "perdido"]}, 1, 0]}}, "primeira": {"$min": "$data_ocorrencia"}, "ultima": {"$max": "$data_ocorrencia"}}},
                {"$project": {"_id": 0, "local": "$_id", "registros": 1, "encontrados": 1, "perdidos": 1, "primeira": 1, "ultima": 1}},
                {"$sort": {"registros": -1, "local": 1}},
            ],
        },
        {
            "slug": "caracteristicas", "title": "Características mais registradas", "icon": "tag",
            "description": "Desmembra as características dos itens pendentes para facilitar a identificação por cor, material ou detalhe marcante.",
            "operators": "$exists · $ne · $unwind · $group · $addToSet · $size · $project",
            "columns": [("caracteristica", "Característica"), ("registros", "Registros"), ("categorias", "Categorias distintas")],
            "pipeline": [
                {"$match": {"status": "aguardando", "caracteristicas": {"$exists": True, "$ne": []}}},
                {"$unwind": "$caracteristicas"},
                {"$group": {"_id": "$caracteristicas", "registros": {"$sum": 1}, "categorias": {"$addToSet": "$categoria"}}},
                {"$project": {"_id": 0, "caracteristica": "$_id", "registros": 1, "categorias": {"$size": "$categorias"}}},
                {"$sort": {"registros": -1, "caracteristica": 1}},
            ],
        },
    ]
