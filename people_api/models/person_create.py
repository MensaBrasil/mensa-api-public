"""MODELS - PERSON - CREATE
Person Create model. Inherits from PersonUpdate, but all the required fields must be re-defined
"""

# # Package # #
from .fields import PersonFields
from .member_data import Address
from .person_update import PersonUpdate

__all__ = ("PersonCreate",)


class PersonCreate(PersonUpdate):
    """Body of Person POST requests"""

    name: str = PersonFields.name
    address: Address = PersonFields.address
    # Birth remains Optional, so is not required to re-declare
