"""Service for handling MembershipPayment database operations."""

from sqlmodel.ext.asyncio.session import AsyncSession

from ..database.models.models import MembershipPayments


class MembershipPaymentService:
    """Service for handling MembershipPayment database operations."""

    @staticmethod
    async def get_last_payment(
        registration_id: int, session: AsyncSession
    ) -> MembershipPayments | None:
        """Return the last payment record for a given registration ID asynchronously."""
        statement = MembershipPayments.select_stmt_last_payment(registration_id)
        results = await session.exec(statement)
        return results.first()
