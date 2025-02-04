# mypy: ignore-errors

"""Service for managing members email addresses."""

import json

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from ..models.member import PostgresMemberRead
from ..models.member_data import EmailCreate, EmailUpdate
from ..repositories import MemberRepository


class EmailService:
    @staticmethod
    def add_email(mb: int, email: EmailCreate, token_data: dict, session: Session):
        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        if MB != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")
        # user can only have one mail from types main and alternative. no other type is allowed
        if email.email_type == "main" or email.email_type == "alternative":
            # check if user already has email of type main or alternative
            member_data = MemberRepository.getAllMemberDataFromPostgres(mb, session)
            try:
                # Parse the JSON string into a Python dictionary
                member_data_dict = json.loads(member_data)
            except json.JSONDecodeError:
                # Handle JSON decoding errors
                raise HTTPException(status_code=400, detail="Invalid JSON format")

            try:
                # Validate the data with your Pydantic model
                validated_data = PostgresMemberRead(**member_data_dict)
            except ValidationError as e:
                # If validation fails, print the error details
                print(e.json())
                # Optionally, raise an HTTPException to notify about a failure
                raise HTTPException(status_code=400, detail="Data validation failed")
            # check if user already has email of type main or alternative, according to what he is trying to do. he can only have one of each
            for e in validated_data.emails:
                if e.email_type == email.email_type:
                    raise HTTPException(
                        status_code=400,
                        detail="User already has email of type " + email.email_type,
                    )

        MemberRepository.addEmailToPostgres(mb, email, session)
        return {"message": "Email added successfully"}

    @staticmethod
    def update_email(
        mb: int,
        email_id: int,
        updated_email: EmailUpdate,
        token_data: dict,
        session: Session,
    ):
        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        if MB != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")
        # check and deny update if email_type is equal to mensa
        if updated_email.email_type == "mensa":
            raise HTTPException(status_code=400, detail="Email type cannot be mensa")

        # Call the update method to modify the email
        success = MemberRepository.updateEmailInPostgres(mb, email_id, updated_email, session)
        if not success:
            raise HTTPException(status_code=404, detail="Email not found")

        return {"message": "Email updated successfully"}

    @staticmethod
    def delete_email(mb: int, email_id: int, token_data: dict, session: Session):
        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        if MB != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")
        # user cannot delete email of type mensa. if trying to, deny
        member_data = MemberRepository.getEmailsFromPostgres(mb, session)
        for e in member_data:
            if e.email_id == email_id:
                if e.email_type == "mensa":
                    raise HTTPException(status_code=400, detail="Cannot delete email of type mensa")

        # Call the delete method to remove the email
        success = MemberRepository.deleteEmailFromPostgres(mb, email_id, session)
        if not success:
            raise HTTPException(status_code=404, detail="Email not found")

        return {"message": "Email deleted successfully"}
