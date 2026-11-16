"""Fotos ilustrativas da demonstração, com procedência e créditos locais."""
import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def photo_catalog():
    path = Path(__file__).resolve().parent / "static/items/photos.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def item_photo(item):
    # Imagens de referência representam somente a carga fictícia identificada.
    # Um item cadastrado depois não recebe uma fotografia que não é a dele.
    if not str(item.get("observacoes", "")).startswith("Registro fictício."):
        return None
    return photo_catalog().get(item.get("titulo", ""))
