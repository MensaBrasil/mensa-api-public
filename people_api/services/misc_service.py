# mypy: ignore-errors

"""Service for miscellaneous member operations."""

import json

from fastapi import HTTPException
from sqlmodel import Session

from people_api.schemas import UserToken

from ..models.member import PostgresMemberRead, PronounsCreate
from ..models.member_data import MemberProfessionFacebookUpdate
from ..repositories import MemberRepository


class MiscService:
    """Service for miscellaneous member operations."""

    @staticmethod
    def get_member(mb: int, token_data: UserToken, session: Session) -> PostgresMemberRead:
        MB = MemberRepository.getMBByEmail(token_data.email, session)
        member_data = MemberRepository.getAllMemberDataFromPostgres(MB, session)

        member_data_dict = json.loads(member_data)
        validated_data = PostgresMemberRead(**member_data_dict)

        return validated_data

    @staticmethod
    def set_pronouns(pronouns: PronounsCreate, token_data: UserToken, session: Session):
        """Set pronouns for a member."""
        MB = MemberRepository.getMBByEmail(token_data.email, session)
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
        token_data: UserToken,
        session: Session,
    ):
        """Update profession and facebook for a member."""
        MB = MemberRepository.getMBByEmail(token_data.email, session)
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
