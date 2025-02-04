"""Service for handling Registration database operations."""

from fastapi import HTTPException
from sqlalchemy.engine import TupleResult
from sqlmodel import Session

from ..database.models.models import Registration


class RegistrationService:
    """Service for handling Registration database operations."""

    @staticmethod
    def get_registration_by_id(registration_id: int, session: Session) -> Registration:
        """Return a registration record by ID."""
        statement = Registration.select_stmt_by_id(registration_id)
        results: TupleResult = session.exec(statement)
        if not results:
            raise HTTPException(
                status_code=404, detail=f"Registration ID {registration_id} not found"
            )
        registration = results.first()
        if registration is None:
            raise HTTPException(
                status_code=404, detail=f"Registration ID {registration_id} not found"
            )
        return registration

    @staticmethod
    def get_first_name(registration_id: int, session: Session) -> str:
        """
        Return the first name of a user registration.
        If social_name is not empty, use it as the first name.
        If not, split the name and return the first part.
        """
        registration = RegistrationService.get_registration_by_id(registration_id, session)
        if registration.social_name:
            return registration.social_name
        if registration.name:
            return registration.name.split(" ")[0]
        raise HTTPException(status_code=404, detail="Registration name not found")

    @staticmethod
    def get_by_email(email: str, session: Session) -> Registration | None:
        """
        Return the registration record associated with the given email.
        This uses a join with the Emails table.
        """
        statement = Registration.select_stmt_by_email(email)
        result: TupleResult = session.exec(statement)
        return result.first()

    @staticmethod
    def update_discord_id(registration_id: int, discord_id: str, session: Session) -> None:
        """
        Update the discord_id for the given registration.
        """
        statement = Registration.update_stmt_discord_id(registration_id, discord_id)
        session.exec(
            statement, params={"discord_id": discord_id, "registration_id": registration_id}
        )
