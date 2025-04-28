# mypy: ignore-errors

"""Service for managing members email addresses."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from people_api.dbs import AsyncSessionsTuple
from people_api.schemas import UserToken

from ..database.models.models import EmailInput, Emails, Registration
from ..services.workspace_service import WorkspaceService


class EmailService:
    """Service for managing members email addresses."""

    @staticmethod
    def add_email(mb: int, email: EmailInput, token_data: UserToken, session: Session):
        """Add email to member."""
        reg_stmt = Registration.select_stmt_by_email(token_data.email)
        member_data = session.exec(reg_stmt).first()
        if not member_data or member_data.registration_id != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")
        if email.email_type in ("main", "alternative"):
            stmt = Emails.get_emails_for_member(mb)
            existing_emails = session.exec(stmt).all()
            for e in existing_emails:
                if e.email_type == email.email_type:
                    raise HTTPException(
                        status_code=400,
                        detail="User already has email of type " + email.email_type,
                    )
        insert_stmt = Emails.insert_stmt_for_email(mb, email)
        session.exec(insert_stmt)
        return {"message": "Email added successfully"}

    @staticmethod
    def update_email(
        mb: int,
        email_id: int,
        updated_email: EmailInput,
        token_data: UserToken,
        session: Session,
    ):
        """Update email for member."""
        reg_stmt = Registration.select_stmt_by_email(token_data.email)
        member_data = session.exec(reg_stmt).first()
        if not member_data or member_data.registration_id != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if updated_email.email_type == "mensa":
            raise HTTPException(status_code=400, detail="Email type cannot be mensa")

        update_stmt = Emails.update_stmt_for_email(mb, email_id, updated_email)
        result = session.exec(update_stmt)
        if result.rowcount is None or result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Email not found")
        return {"message": "Email updated successfully"}

    @staticmethod
    def delete_email(mb: int, email_id: int, token_data: UserToken, session: Session):
        """Delete email from member."""
        reg_stmt = Registration.select_stmt_by_email(token_data.email)
        member_data = session.exec(reg_stmt).first()

        if not member_data or member_data.registration_id != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")

        stmt = Emails.get_emails_for_member(mb)
        existing_emails = session.exec(stmt).all()

        for e in existing_emails:
            if e.email_id == email_id and e.email_type == "mensa":
                raise HTTPException(status_code=400, detail="Cannot delete email of type mensa")

        delete_stmt = Emails.delete_stmt_for_email(mb, email_id)
        result = session.exec(delete_stmt)

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Email not found")

        return {"message": "Email deleted successfully"}

    @staticmethod
    async def request_email_creation(registration_id: int, sessions: AsyncSessionsTuple):
        """Request email creation for a member."""

        return await WorkspaceService.create_mensa_email(
            registration_id=registration_id, sessions=sessions
        )

    @staticmethod
    async def request_password_reset(email: str, registration_id: int, session: AsyncSession):
        """Request password reset for a member."""
        try:
            if not email.endswith("@mensa.org.br"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email must be a Mensa email",
                )

            db_emails = (await session.exec(Emails.get_emails_for_member(registration_id))).all()
            for e in db_emails:
                if e.email_address.endswith("@mensa.org.br"):
                    email = str(e.email_address)
                    break
            else:
                email = None

            if not email:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No matching Mensa email found for this member",
                )
        except Exception as e:
            raise HTTPException(
                status_code=getattr(e, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
                detail=getattr(
                    e,
                    "detail",
                    {
                        "message": "Failed to fetch member information",
                        "error": str(e),
                    },
                ),
            ) from e

        return await WorkspaceService.reset_email_password(
            registration_id=registration_id,
            mensa_email=email,
            session=session,
        )
