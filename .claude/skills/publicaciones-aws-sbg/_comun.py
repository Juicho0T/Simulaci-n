"""Rutas compartidas por los scripts del skill, para que funcionen en cualquier computadora.

- ASSETS: carpeta assets/ del skill (logos y fuentes).
- PATRO: logos de patrocinadores (assets/patrocinadores/).
- Las fuentes se cargan desde assets/fonts/ aunque el script pida una ruta de sistema
  (por ejemplo /usr/share/fonts/.../Inter-Bold.otf): se busca el archivo por nombre en assets/fonts/.
"""

from pathlib import Path

from PIL import ImageFont

SKILL = Path(__file__).resolve().parent
ASSETS = SKILL / "assets"
FUENTES = ASSETS / "fonts"
PATRO = ASSETS / "patrocinadores"
LOGO_SBG = ASSETS / "logo.png"
LOGO_ACISTI = ASSETS / "acisti.png"

_truetype_original = ImageFont.truetype


def _truetype(fuente=None, *args, **kwargs):
    if isinstance(fuente, (str, Path)):
        local = FUENTES / Path(str(fuente)).name
        if local.exists():
            fuente = str(local)
    return _truetype_original(fuente, *args, **kwargs)


if getattr(ImageFont.truetype, "__name__", "") != "_truetype":
    ImageFont.truetype = _truetype
