# mypy: ignore-errors

"""Service for managing members email addresses."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from people_api.schemas import FirebaseToken
from people_api.database.models.models import EmailInput, Emails, Registration



class EmailService:
    """Service for managing members email addresses."""
    @staticmethod
    def add_email(mb: int, email: EmailInput, token_data: FirebaseToken, session: Session):
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
        token_data: FirebaseToken,
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
    def delete_email(mb: int, email_id: int, token_data: FirebaseToken, session: Session):
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
