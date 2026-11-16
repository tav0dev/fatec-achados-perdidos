"""Copia a imagem oficial da unidade sem modificar o arquivo original."""
from urllib.error import URLError
from urllib.request import Request, urlopen

from achados.identity import LOGO_PATH, LOGO_URL


def ensure_logo():
    if LOGO_PATH.exists() and LOGO_PATH.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    try:
        request = Request(LOGO_URL, headers={"User-Agent": "AchadosFatec/1.0"})
        with urlopen(request, timeout=8) as response:
            data = response.read(2_000_001)
        if len(data) > 2_000_000 or not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("O endereço não retornou o arquivo PNG esperado.")
        LOGO_PATH.parent.mkdir(parents=True, exist_ok=True)
        temporary = LOGO_PATH.with_suffix(".download")
        temporary.write_bytes(data)
        temporary.replace(LOGO_PATH)
        print("Logo oficial da Fatec Itapetininga salvo para uso local.")
        return True
    except (URLError, OSError, ValueError) as error:
        print(f"Não foi possível salvar a marca localmente ({type(error).__name__}). A interface usará o endereço oficial da imagem.")
        return False
