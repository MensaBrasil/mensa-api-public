# mypy: ignore-errors

"""UTILS
Misc helpers/utils functions
"""

# # Native # #
import io
import json
from datetime import date, datetime
from time import time
from uuid import uuid4

from babel.dates import Locale, format_date
from PIL import Image, ImageDraw, ImageFont

__all__ = ("get_time", "get_uuid")

# Cache static resources if they don't change
CERT_TEMPLATE = Image.open("certificado.png")
FONT_LARGE = ImageFont.truetype("arialbd.ttf", 130)
FONT_MEDIUM = ImageFont.truetype("arialbd.ttf", 90)
FONT_SMALL = ImageFont.truetype("arialbd.ttf", 60)
LOCALE = Locale("pt_BR")


def get_time(seconds_precision: bool = True) -> int | float:
    return time() if not seconds_precision else int(time())


def get_uuid() -> str:
    return str(uuid4())


def create_certificate(nome: str, MB: int, expiration: datetime) -> io.BytesIO:
    img = CERT_TEMPLATE.copy()
    draw = ImageDraw.Draw(img)
    meio = 2500

    today = format_date(datetime.now(), format="long", locale=LOCALE)
    expiration_text = (
        f"Certificado válido até {format_date(expiration, format='dd/MM/yyyy', locale=LOCALE)}"
    )

    nomex = meio - FONT_LARGE.getlength(nome) / 2
    datax = meio - FONT_MEDIUM.getlength(today) / 2
    expiration_x = meio - FONT_SMALL.getlength(expiration_text) / 2

    draw.text((nomex, 1150), nome, font=FONT_LARGE, fill=(0, 0, 0))
    draw.text((2900, 1625), str(MB), font=FONT_MEDIUM, fill=(0, 0, 0))
    draw.text((datax, 2100), today, font=FONT_MEDIUM, fill=(0, 0, 0))
    draw.text((expiration_x, 3250), expiration_text, font=FONT_SMALL, fill=(0, 0, 0))

    buf = io.BytesIO()
    img.save(buf, format="WEBP", lossless=True)
    buf.seek(0)
    return buf


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)
