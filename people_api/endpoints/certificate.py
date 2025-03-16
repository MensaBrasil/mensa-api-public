"""Endpoints for generating and downloading certificates."""

import asyncio
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from ..services import CertificateService

certificate_router = APIRouter()


@certificate_router.get(
    "/download_certificate.png", description="Gerar certificado", tags=["certificado"]
)
async def _get_certificado(MB: int, key: str):
    return await CertificateService.generate_certificate(MB, key)


@certificate_router.get(
    "/certificado",
    response_class=HTMLResponse,
    description="Gerar botão certificado",
    tags=["certificado"],
)
async def _show_download_button(MB: int, key: str):
    return CertificateService.show_download_button(MB, key)
