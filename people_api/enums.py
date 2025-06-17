from enum import StrEnum


class Gender(StrEnum):
    """Available genders"""

    MALE = "Masculino"
    FEMALE = "Feminino"
    NON_BINARY = "Não-binário"
    RATHER_NOT_SAY = "Prefiro não dizer"
    OTHER = "Outros"
