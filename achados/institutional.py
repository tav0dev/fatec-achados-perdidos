"""Referências institucionais locais; nenhuma consulta remota durante o cadastro."""
import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def fatec_news():
    path = Path(__file__).resolve().parent.parent / "data/fatec_news.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"items": [], "checked_at": "", "source": "https://fatecitapetininga.cps.sp.gov.br/"}
