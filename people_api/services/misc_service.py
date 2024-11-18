"""Service for miscellaneous member operations."""

import json

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from ..models.member import PostgresMemberRead, PronounsCreate
from ..models.member_data import MemberProfessionFacebookUpdate
from ..repositories import MemberRepository


class MiscService:
    @staticmethod
    def get_member(mb: int, token_data: dict, session: Session) -> PostgresMemberRead:
        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        member_data = MemberRepository.getAllMemberDataFromPostgres(MB, session)

        try:
            member_data_dict = json.loads(member_data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")

        try:
            validated_data = PostgresMemberRead(**member_data_dict)
        except ValidationError as e:
            print(e.json())
            raise HTTPException(status_code=400, detail="Data validation failed")

        return validated_data

    @staticmethod
    def set_pronouns(pronouns: PronounsCreate, token_data: dict, session: Session):
        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        if pronouns.pronouns not in [
            "Ele/dele",
            "Ela/dela",
            "Elu/delu",
            "Nenhuma das opções",
        ]:
            raise HTTPException(
                status_code=400,
                detail="Pronouns must be Ele/dele, Ela/dela or Elu/delu or Nenhuma das opções",
            )
        MemberRepository.setPronounsOnPostgres(MB, pronouns.pronouns, session)
        return {"message": "Pronouns set successfully"}

    @staticmethod
    def update_fb_profession(
        mb: int,
        updated_member: MemberProfessionFacebookUpdate,
        token_data: dict,
        session: Session,
    ):
        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        if MB != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")

        profession = updated_member.profession
        facebook = updated_member.facebook
        success = MemberRepository.updateProfessionAndFacebookOnPostgres(
            mb, profession, facebook, session
        )
        if not success:
            raise HTTPException(status_code=404, detail="Member not found")

        return {"message": "Member updated successfully"}
