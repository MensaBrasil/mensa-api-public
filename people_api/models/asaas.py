"""This module defines models for payment methods and choices used in the Asaas API."""

from enum import StrEnum

from pydantic import BaseModel


class AnuityType(StrEnum):
    """Enum for different types of annuities."""

    ONE_ANNUAL_FEE = "1A"
    ONE_ANNUAL_FEE_PLUS_PRO_RATA = "1A+PR"
    FIVE_ANNUAL_FEES_PLUS_PRO_RATA = "5A+PR"
    TEN_ANNUAL_FEES_PLUS_PRO_RATA = "10A+PR"
    LIFETIME = "LIFETIME"

    @property
    def text(self) -> str:
        """Return a human readable description for the anuity type in Portuguese."""
        mapping = {
            AnuityType.ONE_ANNUAL_FEE: "1 anuidade",
            AnuityType.ONE_ANNUAL_FEE_PLUS_PRO_RATA: "1 anuidade + pró-rata",
            AnuityType.FIVE_ANNUAL_FEES_PLUS_PRO_RATA: "5 anuidades + pró-rata",
            AnuityType.TEN_ANNUAL_FEES_PLUS_PRO_RATA: "10 anuidades + pró-rata",
            AnuityType.LIFETIME: "Vitalício",
        }
        return mapping[self]


class PaymentChoice(BaseModel):
    """Model representing a payment choice for member onboarding payment."""

    anuityType: AnuityType
    externalReference: str
