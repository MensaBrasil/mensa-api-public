"""UTILS
Misc helpers/utils functions
"""

# # Native # #
from time import time
from uuid import uuid4
from typing import Union
import json

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from babel.dates import format_date, Locale
import io

__all__ = ("get_time", "get_uuid")


def get_time(seconds_precision=True) -> Union[int, float]:
    """Returns the current time as Unix/Epoch timestamp, seconds precision by default"""
    return time() if not seconds_precision else int(time())


def get_uuid() -> str:
    """Returns an unique UUID (UUID4)"""
    return str(uuid4())

from fastapi import FastAPI, File
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from babel.dates import format_date, Locale
import io


def create_certificate(nome: str, MB: int, expiration: datetime):
    data = datetime.now()
    meio = 2500

    img = Image.open('certificado.png')
    I1 = ImageDraw.Draw(img)

    font = ImageFont.truetype("arialbd.ttf", 130)
    nomex = meio - font.getlength(nome) / 2
    I1.text((nomex, 1150), nome, font=font, fill=(0, 0, 0))

    font = ImageFont.truetype("arialbd.ttf", 90)
    I1.text((2900, 1625), str(MB), font=font, fill=(0, 0, 0))

    locale = Locale('pt_BR')
    formatted_date = format_date(data, format='long', locale=locale)
    font = ImageFont.truetype("arialbd.ttf", 90)
    datax = meio - font.getlength(formatted_date) / 2
    I1.text((datax, 2100), formatted_date, font=font, fill=(0, 0, 0))
    # add expiration date on format dd/mm/yyyy
    expiration = f"Certificado válido até {format_date(expiration, format='dd/MM/yyyy', locale=locale)}"
    font = ImageFont.truetype("arialbd.ttf", 60)
    datax = meio - font.getlength(expiration) / 2
    I1.text((datax, 3250), expiration, font=font, fill=(0, 0, 0))
    # Save the edited image in memory
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf



from datetime import datetime, date

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()  # Convert datetime and date to ISO format string
        return super().default(obj)
