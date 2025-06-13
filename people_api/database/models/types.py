"Types for the database models."

import re

import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat


class PhoneNumber(str):
    "A custom type for phone number with E.164 format."

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_phone

    @classmethod
    def validate_phone(cls, value, info):
        if not isinstance(value, str):
            raise TypeError("Phone number must be a string.")
        if not re.match(r"^\+?[\d\s\-\(\)]+$", value):
            raise ValueError("Phone number contains invalid characters.")
        try:
            parsed_number = phonenumbers.parse(value, "BR")
        except NumberParseException as e:
            raise ValueError("Invalid phone number format.") from e
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValueError("Invalid phone number.")
        return phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)


class CPFNumber(str):
    "A custom type for CPF number."

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_cpf

    @classmethod
    def validate_cpf(cls, value, info):
        """Validates a Brazilian CPF (Cadastro de Pessoas Físicas), allowing formatted input."""
        if value is not None:
            if not isinstance(value, str):
                raise TypeError("CPF must be a string.")
            cleaned = re.sub(r"\D", "", value)
            if len(cleaned) != 11:
                raise ValueError("CPF must be exactly 11 digits long.")
        return cleaned


class ZipNumber(str):
    "A custom type for zip code."

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_zip

    @classmethod
    def validate_zip(cls, value, info):
        """Validates a zip code, allowing only numbers and letters. Removes any symbols."""
        if value is None:
            return value
        cleaned = re.sub(r"[^A-Za-z0-9]", "", value)
        if len(cleaned) > 12:
            raise ValueError("Zip code must be at most 12 characters long.")
        return cleaned
