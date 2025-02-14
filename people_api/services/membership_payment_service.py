"""Service for handling MembershipPayment database operations."""

from sqlalchemy.engine import TupleResult

from ..database.models.models import MembershipPayments
from sqlmodel.ext.asyncio.session import AsyncSession


class MembershipPaymentService:
    """Service for handling MembershipPayment database operations."""

    @staticmethod
    async def get_last_payment(registration_id: int, session: AsyncSession) -> MembershipPayments | None:
        """Return the last payment record for a given registration ID asynchronously."""
        statement = MembershipPayments.select_stmt_last_payment(registration_id)
        results = await session.exec(statement)
        return results.first()
