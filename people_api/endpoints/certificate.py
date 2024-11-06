"""
Endpoints for generating and downloading certificates.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, StreamingResponse

from people_api.repositories import MemberRepository
from people_api.static import download_cert
from people_api.utils import create_certificate

certificate_router = APIRouter()


@certificate_router.get(
    "/download_certificate.png", description="Gerar certificado", tags=["certificado"]
)
async def _get_certificado(MB: int, key: str):  # Note that I changed the type of MB to int
    # check if key matches CertificateKey in the database
    member = MemberRepository.getFromFirebase(MB)
    if member.CertificateToken != key:
        return {"error": "Chave inválida"}
    cert = create_certificate(member.display_name, MB, member.expiration_date)
    return StreamingResponse(
        cert,
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=certificate.png"},
    )


@certificate_router.get(
    "/certificado",
    response_class=HTMLResponse,
    description="Gerar botão certificado",
    tags=["certificado"],
)
async def _show_download_button(MB: int, key: str):
    return download_cert(MB, key)
