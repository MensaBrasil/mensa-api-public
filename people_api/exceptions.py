"""EXCEPTIONS
Custom exceptions that will make the API return certain HTTP responses to the client.
Each exception has a message, statuscode and response model (from models.errors).
Each exception must be raised using the kwargs (fields) of the associated model.
Exceptions can return the HTTP response model (Response/JSONResponse) and part of the response model definition.
"""

# # Native # #
from typing import Type

from fastapi import status as statuscode

# # Installed # #
from fastapi.responses import JSONResponse

# # Package # #
from .models.errors import (
    AlreadyExistsError,
    BaseError,
    BaseIdentifiedError,
    NotFoundError,
)

__all__ = (
    "BaseAPIException", "BaseIdentifiedException",
    "NotFoundException", "AlreadyExistsException",
    "PersonNotFoundException", "PersonAlreadyExistsException",
    "get_exception_responses", "PersonAlreadyExistsException",
    "AddressNotFoundException", "AddressAlreadyExistsException",
    "PhoneNotFoundException", "PhoneAlreadyExistsException",
    "EmailNotFoundException", "EmailAlreadyExistsException",
    "LegalRepresentativeNotFoundException", "LegalRepresentativeAlreadyExistsException"
)


class BaseAPIException(Exception):
    """Base error for custom API exceptions"""
    message = "Generic error"
    code = statuscode.HTTP_500_INTERNAL_SERVER_ERROR
    model = BaseError

    def __init__(self, **kwargs):
        kwargs.setdefault("message", self.message)
        self.message = kwargs["message"]
        self.data = self.model(**kwargs)

    def __str__(self):
        return self.message

    def response(self):
        return JSONResponse(
            content=self.data.dict(),
            status_code=self.code
        )

    @classmethod
    def response_model(cls):
        return {cls.code: {"model": cls.model}}


class BaseIdentifiedException(BaseAPIException):
    """Base error for exceptions related with entities, uniquely identified"""
    message = "Entity error"
    code = statuscode.HTTP_500_INTERNAL_SERVER_ERROR
    model = BaseIdentifiedError

    def __init__(self, identifier, **kwargs):
        super().__init__(identifier=identifier, **kwargs)


class NotFoundException(BaseIdentifiedException):
    """Base error for exceptions raised because an entity does not exist"""
    message = "The entity does not exist"
    code = statuscode.HTTP_404_NOT_FOUND
    model = NotFoundError


class AlreadyExistsException(BaseIdentifiedException):
    """Base error for exceptions raised because an entity already exists"""
    message = "The entity already exists"
    code = statuscode.HTTP_409_CONFLICT
    model = AlreadyExistsError


class PersonNotFoundException(NotFoundException):
    """Error raised when a person does not exist"""
    message = "The person does not exist"

class AddressNotFoundException(NotFoundException):
    """Error raised when a person does not exist"""
    message = "The address does not exist"

class PhoneNotFoundException(NotFoundException):
    """Error raised when a person does not exist"""
    message = "The phone does not exist"

class EmailNotFoundException(NotFoundException):
    """Error raised when a person does not exist"""
    message = "The email does not exist"

class LegalRepresentativeNotFoundException(NotFoundException):
    """Error raised when a person does not exist"""
    message = "The legal representative does not exist"


class PersonAlreadyExistsException(AlreadyExistsException):
    """Error raised when a person already exists"""
    message = "The person already exists"

class AddressAlreadyExistsException(AlreadyExistsException):
    """Error raised when a person already exists"""
    message = "The address already exists"

class PhoneAlreadyExistsException(AlreadyExistsException):
    """Error raised when a person already exists"""
    message = "The phone already exists"

class EmailAlreadyExistsException(AlreadyExistsException):
    """Error raised when a person already exists"""
    message = "The email already exists"

class LegalRepresentativeAlreadyExistsException(AlreadyExistsException):
    """Error raised when a person already exists"""
    message = "The legal representative already exists"



def get_exception_responses(*args: Type[BaseAPIException]) -> dict:
    """Given BaseAPIException classes, return a dict of responses used on FastAPI endpoint definition, with the format:
    {statuscode: schema, statuscode: schema, ...}"""
    responses = dict()
    for cls in args:
        responses.update(cls.response_model())
    return responses
