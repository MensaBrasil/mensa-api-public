"""Service for handling Registration database operations."""

from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException

from ..database.models.models import Registration
from sqlalchemy import text


class RegistrationService:
    """Service for handling Registration database operations."""
    @staticmethod
    async def get_registration_by_id(registration_id: int, session: AsyncSession) -> Registration:
        """Return a registration record by ID asynchronously."""
        statement = Registration.select_stmt_by_id(registration_id)
        results = await session.exec(statement)
        registration = results.first()
        if registration is None:
            raise HTTPException(
                status_code=404, detail=f"Registration ID {registration_id} not found"
            )
        return registration

    @staticmethod
    async def get_first_name(registration_id: int, session: AsyncSession) -> str:
        """
        Return the first name of a user registration.
        If social_name is not empty, use it as the first name.
        If not, split the name and return the first part.
        """
        registration = await RegistrationService.get_registration_by_id(registration_id, session)
        if registration.social_name:
            return registration.social_name
        if registration.name:
            return registration.name.split(" ")[0]
        raise HTTPException(status_code=404, detail="Registration name not found")

    @staticmethod
    async def get_by_email(email: str, session: AsyncSession) -> Registration | None: 
        """
        Return the registration record associated with the given email.
        This uses a join with the Emails table.
        """
        statement = Registration.select_stmt_by_email(email)
        result = await session.execute(statement)
        row = result.first()
        return row[0] if row else None

    @staticmethod
    async def update_discord_id(registration_id: int, discord_id: str, session: AsyncSession) -> None:
        """
        Update the discord_id for the given registration asynchronously.
        """
        statement = Registration.update_stmt_discord_id(registration_id, discord_id)
        await session.exec(
            statement, params={"discord_id": discord_id, "registration_id": registration_id}
        )
