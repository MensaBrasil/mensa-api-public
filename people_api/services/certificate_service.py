# mypy: ignore-errors

"""Service for generating certificates."""

import asyncio

from fastapi.responses import StreamingResponse

from ..repositories import MemberRepository
from ..static import download_cert
from ..utils import create_certificate


class CertificateService:
    @staticmethod
    async def generate_certificate(MB: int, key: str):
        member = MemberRepository.getFromFirebase(MB)
        if member.CertificateToken != key:
            return {"error": "Chave inválida"}
        cert = await asyncio.to_thread(
            create_certificate, member.display_name, MB, member.expiration_date
        )
        return StreamingResponse(
            cert,
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=certificate.png"},
        )

    @staticmethod
    def show_download_button(MB: int, key: str):
        return download_cert(MB, key)
