# mypy: ignore-errors

"""UTILS
Misc helpers/utils functions
"""

# # Native # #
import io
import json
import logging
from datetime import date, datetime
from time import time
from uuid import uuid4

import boto3
from babel.dates import Locale, format_date
from botocore.exceptions import ClientError
from PIL import Image, ImageDraw, ImageFont

from .settings import get_settings

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


def get_s3_client():
    return boto3.client(
        "s3",
        region_name=get_settings().region_name,
        aws_access_key_id=get_settings().aws_access_key_id,
        aws_secret_access_key=get_settings().aws_secret_access_key,
    )


def get_aws_client(service: str):
    """Returns a boto3 client for the specified AWS service."""
    return boto3.client(
        service,
        region_name=get_settings().region_name,
        aws_access_key_id=get_settings().aws_sqs_access_key,
        aws_secret_access_key=get_settings().aws_sqs_secret_access_key,
    )


def upload_media_to_s3(bucket: str, key: str, content: bytes, content_type: str) -> str:
    """
    Uploads content to S3 under the given bucket and key,
    then returns the S3 URL.
    """
    s3 = get_s3_client()
    s3.put_object(Bucket=bucket, Key=key, Body=content, ContentType=content_type)
    return f"s3://{bucket}/{key}"


def generate_presigned_media_url(media_path: str | None) -> str | None:
    """Generate a presigned URL for a media path stored in S3."""
    if not media_path:
        return None

    bucket_name = get_settings().volunteer_s3_bucket
    s3_client = get_s3_client()

    try:
        if media_path.startswith("s3://"):
            prefix = f"s3://{bucket_name}/"
            if media_path.startswith(prefix):
                key = media_path[len(prefix) :]
            else:
                key = media_path.split("s3://")[-1].split("/", 1)[-1]
        else:
            key = media_path

        return s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": bucket_name, "Key": key},
            ExpiresIn=3600,
        )
    except ClientError as e:
        logging.error(f"Error generating presigned URL: {e}")
        return None
