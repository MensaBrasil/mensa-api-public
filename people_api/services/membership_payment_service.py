"""Service for handling MembershipPayment database operations."""

from sqlalchemy.engine import TupleResult
from sqlmodel import Session

from ..database.models.models import MembershipPayments


class MembershipPaymentService:
    """Service for handling MembershipPayment database operations."""

    @staticmethod
    def get_last_payment(registration_id: int, session: Session) -> MembershipPayments | None:
        """Return the last payment record for a given registration ID."""
        statement = MembershipPayments.select_stmt_last_payment(registration_id)
        results: TupleResult = session.exec(statement)
        return results.first()
