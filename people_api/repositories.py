# mypy: ignore-errors

"""REPOSITORIES
Methods to interact with the database
"""

# # Package # #
import json
import re
from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy import text
from sqlmodel import Session, func, or_, select, union_all, update
from sqlmodel.ext.asyncio.session import AsyncSession

from people_api.database.models.models import (
    GroupList,
    GroupRequests,
    LegalRepresentatives,
    MemberGroups,
    Phones,
    Registration,
)

from .dbs import firebase_collection
from .exceptions import (
    AddressNotFoundException,
    EmailNotFoundException,
    LegalRepresentativeNotFoundException,
    PersonNotFoundException,
    PhoneNotFoundException,
)
from .models import (
    Address,
    Email,
    FirebaseMemberRead,
    LegalRepresentative,
    Phone,
    PostgresMemberRegistration,
)
from .utils import CustomJSONEncoder

__all__ = ["MemberRepository"]


class MemberRepository:
    @staticmethod
    def setPronounsOnPostgres(mb: int, pronouns: str, session: Session) -> bool:
        query = text("""UPDATE registration SET pronouns = :pronouns WHERE registration_id = :mb""")
        session.execute(query, {"pronouns": pronouns, "mb": mb})
        return True

    @staticmethod
    async def getCanParticipate(registration: Registration, session: AsyncSession) -> list:
        """Retrieve a list of groups that the member can participate in."""
        try:
            birth_date = registration.birth_date

            if not birth_date:
                raise HTTPException(
                    status_code=400,
                    detail="Birth date is required to determine group participation.",
                )

            today = datetime.today().date()
            age = (
                today.year
                - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day))
            )

            should_show_RJB_groups_in_app = False

            if age < 10:
                user_classification = "MJB"
            elif 10 <= age < 18:
                user_classification = "JB"
            else:
                user_classification = "MB"

            if user_classification in ("MJB", "JB"):
                legal_representatives = (
                    await session.exec(
                        LegalRepresentatives.get_legal_representatives_for_member(
                            member_id=registration.registration_id
                        )
                    )
                ).all()
                legal_rep_mensans = []
                for legal_rep in legal_representatives:
                    legal_mensan = (
                        await session.exec(
                            Registration.get_registration_by_last_8_phone_digits(legal_rep.phone)
                        )
                    ).first()
                    if legal_mensan:
                        legal_rep_mensans.append(legal_mensan)
                if len(legal_rep_mensans) < len(legal_representatives):
                    should_show_RJB_groups_in_app = True

            if user_classification == "MB":
                member_phones = (
                    await session.exec(
                        Phones.select_stmt_by_registration_id(registration.registration_id)
                    )
                ).all()
                for phone in member_phones:
                    legal_rep_correspondence = (
                        await session.exec(
                            select(LegalRepresentatives).where(
                                LegalRepresentatives.phone == phone.phone_number
                            )
                        )
                    ).first()
                    if legal_rep_correspondence:
                        should_show_RJB_groups_in_app = True

            all_groups = (await session.exec(select(GroupList))).all()
            result_list = []

            for group in all_groups:
                name = group.group_name
                group_id = group.group_id

                if re.search(r"^M[\s\.]*JB", name, re.IGNORECASE):
                    group_classification = "MJB"
                elif re.search(r"^R[\s\.]*JB", name, re.IGNORECASE):
                    group_classification = "RJB"
                elif re.search(r"^(?!R[\s\.]*JB)(?!M[\s\.]*JB)JB", name, re.IGNORECASE):
                    group_classification = "JB"
                elif re.search(r"^OrgMB", name, re.IGNORECASE):
                    group_classification = "OrgMB"
                elif re.search(r"^MB", name, re.IGNORECASE) or re.search(
                    r"^Mensa", name, re.IGNORECASE
                ):
                    group_classification = "MB"
                else:
                    group_classification = "NotMensa"

                if should_show_RJB_groups_in_app and group_classification == "RJB":
                    result_list.append({"group_id": group_id, "group_name": name})
                if user_classification == "MJB" and group_classification == "MJB":
                    result_list.append({"group_id": group_id, "group_name": name})
                elif user_classification == "JB" and group_classification == "JB":
                    result_list.append({"group_id": group_id, "group_name": name})
                elif user_classification == "MB" and group_classification == "MB":
                    result_list.append({"group_id": group_id, "group_name": name})

            result_list = sorted(result_list, key=lambda x: x["group_name"])
            return result_list

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="Error while fetching groups.",
            ) from e

    @staticmethod
    async def getParticipateIn(mb: int, session: AsyncSession):
        """Retrieve a list of groups that the member is participating in."""

        query = (
            select(MemberGroups, GroupList.group_name)
            .join(GroupList, MemberGroups.group_id == GroupList.group_id)
            .where(
                MemberGroups.registration_id == mb,
                or_(
                    MemberGroups.entry_date > MemberGroups.exit_date,
                    MemberGroups.exit_date.is_(None),
                ),
                MemberGroups.group_id.in_(select(GroupList.group_id)),
                func.right(MemberGroups.phone_number, 8).in_(
                    select(func.right(Phones.phone_number, 8)).where(Phones.registration_id == mb)
                ),
            )
        )

        result = (await session.exec(query)).all()

        if result:
            group_info = []
            for group, group_name in result:
                entry_date = group.entry_date.strftime("%d/%m/%Y")
                group_info.append(
                    {
                        "group_name": group_name,
                        "entry_date": entry_date,
                    }
                )
                return group_info
        return []

    @staticmethod
    async def getPendingRequests(mb: int, session: AsyncSession):
        """Retrieve a list of pending group join requests for a member"""
        subquery = (
            select(
                GroupRequests.group_id,
                func.max(GroupRequests.last_attempt).label("last_attempt"),
                func.max(GroupRequests.no_of_attempts).label("no_of_attempts"),
            )
            .where(
                GroupRequests.registration_id == mb,
                GroupRequests.fulfilled == False,  # noqa: E712
                or_(
                    GroupRequests.no_of_attempts < 3,
                    GroupRequests.no_of_attempts.is_(None),
                ),
            )
            .group_by(GroupRequests.group_id)
            .subquery()
        )

        query = (
            select(
                GroupList.group_name,
                subquery.c.last_attempt,
                subquery.c.no_of_attempts,
            )
            .join(GroupList, GroupList.group_id == subquery.c.group_id)
            .order_by(subquery.c.last_attempt.desc().nulls_last())
        )
        result = await session.exec(query)
        data = result.mappings().all()

        return [
            {
                "group_name": row["group_name"],
                "last_attempt": row["last_attempt"].strftime("%d/%m/%Y")
                if row["last_attempt"]
                else row["last_attempt"],
                "no_of_attempts": row["no_of_attempts"],
            }
            for row in data
        ]

    @staticmethod
    async def getFailedRequests(mb: int, session: AsyncSession):
        subq = (
            select(
                GroupRequests.group_id,
                func.max(GroupRequests.last_attempt).label("last_attempt"),
            )
            .where(
                GroupRequests.registration_id == mb,
                GroupRequests.fulfilled == False,  # noqa: E712
                GroupRequests.no_of_attempts >= 3,
            )
            .group_by(GroupRequests.group_id)
            .subquery()
        )

        query = (
            select(GroupList.group_name, subq.c.last_attempt)
            .join(subq, GroupList.group_id == subq.c.group_id)
            .order_by(subq.c.last_attempt.desc())
        )

        result = await session.exec(query)
        rows = result.mappings().all()

        return [
            {
                "group_name": row["group_name"],
                "last_attempt": row["last_attempt"].strftime("%d/%m/%Y")
                if row["last_attempt"]
                else None,
            }
            for row in rows
        ]

    @staticmethod
    async def getUnfullfilledGroupRequests(mb: int, session: AsyncSession) -> list:
        """Retrieve a list of unfulfilled group requests for a member"""
        stmt = select(GroupRequests.group_id).where(
            (GroupRequests.fulfilled == False)  # noqa: E712
            & (GroupRequests.registration_id == mb)
            & (GroupRequests.no_of_attempts < 3)
        )

        result = (await session.exec(stmt)).all()
        return result if result else []

    @staticmethod
    async def getFailedGroupRequests(mb: int, session: AsyncSession) -> list:
        """Retrieve a list of failed group requests for a member"""
        stmt = select(GroupRequests.group_id).where(
            (GroupRequests.fulfilled == False)  # noqa: E712
            & (GroupRequests.registration_id == mb)
            & (GroupRequests.no_of_attempts >= 3)
        )

        result = (await session.exec(stmt)).all()
        return result if result else []

    @staticmethod
    async def updateFailedGroupRequests(mb: int, session: AsyncSession):
        subquery = select(GroupRequests.group_id).where(
            (GroupRequests.fulfilled == False)  # noqa: E712
            & (GroupRequests.registration_id == mb)
            & (GroupRequests.no_of_attempts >= 3)
        )

        stmt = (
            update(GroupRequests)
            .where(
                (GroupRequests.registration_id == mb)
                & (GroupRequests.fulfilled == False)  # noqa: E712
                & (GroupRequests.group_id.in_(subquery))
            )
            .values(no_of_attempts=0)
        )

        await session.exec(stmt)
        return True

    @staticmethod
    async def addGroupRequest(
        registration_id: int,
        group_id: str,
        created_at: datetime,
        last_attempt: datetime,
        fulfilled: bool,
        session: AsyncSession,
    ) -> int:
        new_request = GroupRequests(
            registration_id=registration_id,
            group_id=group_id,
            created_at=created_at,
            last_attempt=last_attempt,
            fulfilled=fulfilled,
        )

        session.add(new_request)
        await session.flush()
        return new_request.id

    @staticmethod
    async def getAllMemberAndLegalRepPhonesFromPostgres(mb: int, session: AsyncSession) -> list:
        stmt1 = select(Phones.phone_number.label("phone")).where(Phones.registration_id == mb)
        stmt2 = select(LegalRepresentatives.phone.label("phone")).where(
            LegalRepresentatives.registration_id == mb
        )
        stmt3 = select(LegalRepresentatives.alternative_phone.label("phone")).where(
            (LegalRepresentatives.registration_id == mb)
            & (LegalRepresentatives.alternative_phone.isnot(None))
        )

        result = (await session.exec(union_all(stmt1, stmt2, stmt3))).all()
        if result:
            return [phone.phone for phone in result]
        return []

    @staticmethod
    def getMissingFieldsFromPostgres(mb: int, session: Session) -> list:
        query = text(
            """SELECT registration_id, cpf, birth_date FROM registration WHERE registration_id = :mb"""
        )
        result = session.execute(query, {"mb": mb})
        data = result.fetchone()
        if data:
            missing_fields = []
            if not data.cpf:
                missing_fields.append("cpf")
            if not data.birth_date:
                missing_fields.append("birth_date")
            return missing_fields
        else:
            raise PersonNotFoundException(mb)

    @staticmethod
    def setBirthDateOnPostgres(mb: int, birthdate: date, session: Session):
        query = text(
            """UPDATE registration SET birth_date = :birthdate WHERE registration_id = :mb"""
        )
        session.execute(query, {"birthdate": birthdate, "mb": mb})
        return True

    @staticmethod
    def setCPFOnPostgres(mb: int, cpf: str, session: Session):
        query = text("""UPDATE registration SET cpf = :cpf WHERE registration_id = :mb""")
        session.execute(query, {"cpf": cpf, "mb": mb})
        return True

    @staticmethod
    def addAddressToPostgres(mb: int, address: Address, session: Session):
        query = text("""INSERT INTO addresses (registration_id, state, city, address, neighborhood, zip)
                    VALUES (:registration_id, :state, :city, :address, :neighborhood, :zip)""")
        data = {
            "registration_id": mb,
            "state": address.state,
            "city": address.city,
            "address": address.address,
            "neighborhood": address.neighborhood,
            "zip": address.zip,
        }
        session.execute(query, data)
        return True

    @staticmethod
    def addEmailToPostgres(mb: int, email: Email, session: Session):
        query = text(
            """INSERT INTO emails (registration_id, email_type, email_address) VALUES (:registration_id, :email_type, :email_address)"""
        )
        session.execute(
            query,
            {
                "registration_id": mb,
                "email_type": email.email_type,
                "email_address": email.email_address,
            },
        )
        return True

    @staticmethod
    def addPhoneToPostgres(mb: int, phone: Phone, session: Session):
        query = text(
            """INSERT INTO phones (registration_id, phone_number) VALUES (:registration_id, :phone_number)"""
        )
        session.execute(query, {"registration_id": mb, "phone_number": phone.phone_number})
        return True

    @staticmethod
    def addLegalRepresentativeToPostgres(
        mb: int, legal_representative: LegalRepresentative, session: Session
    ):
        query = text("""INSERT INTO legal_representatives (registration_id, cpf, full_name, email, phone, alternative_phone, observations)
                       VALUES (:registration_id, :cpf, :full_name, :email, :phone, :alternative_phone, :observations)""")
        session.execute(
            query,
            {
                "registration_id": mb,
                "cpf": legal_representative.cpf,
                "full_name": legal_representative.full_name,
                "email": legal_representative.email,
                "phone": legal_representative.phone,
                "alternative_phone": legal_representative.alternative_phone,
                "observations": legal_representative.observations,
            },
        )
        return True

    @staticmethod
    def deleteAddressFromPostgres(mb: int, address_id: int, session: Session):
        query = text(
            "DELETE FROM addresses WHERE registration_id = :mb AND address_id = :address_id RETURNING address_id"
        )
        result = session.execute(query, {"mb": mb, "address_id": address_id})
        deleted_row = result.fetchone()
        if deleted_row:
            return True
        else:
            raise AddressNotFoundException(str(address_id))

    @staticmethod
    def deleteEmailFromPostgres(mb: int, email_id: int, session: Session):
        query = text(
            "DELETE FROM emails WHERE registration_id = :mb AND email_id = :email_id RETURNING email_id"
        )
        result = session.execute(query, {"mb": mb, "email_id": email_id})
        deleted_row = result.fetchone()
        if deleted_row:
            return True
        else:
            raise EmailNotFoundException(str(email_id))

    @staticmethod
    def deletePhoneFromPostgres(mb: int, phone_id: int, session: Session):
        query = text(
            "DELETE FROM phones WHERE registration_id = :mb AND phone_id = :phone_id RETURNING phone_id"
        )
        result = session.execute(query, {"mb": mb, "phone_id": phone_id})
        deleted_row = result.fetchone()
        if deleted_row:
            return True
        else:
            raise PhoneNotFoundException(str(phone_id))

    @staticmethod
    def deleteLegalRepresentativeFromPostgres(mb: int, legal_rep_id: int, session: Session):
        query = text(
            "DELETE FROM legal_representatives WHERE registration_id = :mb AND representative_id = :legal_rep_id RETURNING representative_id"
        )
        result = session.execute(query, {"mb": mb, "legal_rep_id": legal_rep_id})
        deleted_row = result.fetchone()
        if deleted_row:
            return True
        else:
            raise LegalRepresentativeNotFoundException(str(legal_rep_id))

    @staticmethod
    def updateAddressInPostgres(mb: int, address_id: int, new_address: Address, session: Session):
        query = text("""
                UPDATE addresses
                SET state = :state, city = :city, address = :address, neighborhood = :neighborhood, zip = :zip
                WHERE registration_id = :mb AND address_id = :address_id
            """)
        data = {
            "state": new_address.state,
            "city": new_address.city,
            "address": new_address.address,
            "neighborhood": new_address.neighborhood,
            "zip": new_address.zip,
            "mb": mb,
            "address_id": address_id,
        }

        session.execute(query, data)

        return True

    @staticmethod
    def updateEmailInPostgres(mb: int, email_id: int, new_email: Email, session: Session):
        query = text("""
                UPDATE emails
                SET email_type = :email_type, email_address = :email_address
                WHERE registration_id = :mb AND email_id = :email_id
            """)
        data = {
            "email_type": new_email.email_type,
            "email_address": new_email.email_address,
            "mb": mb,
            "email_id": email_id,
        }

        session.execute(query, data)

        return True

    @staticmethod
    def updatePhoneInPostgres(mb: int, phone_id: int, new_phone: Phone, session: Session):
        query = text("""
                UPDATE phones
                SET phone_number = :phone_number
                WHERE registration_id = :mb AND phone_id = :phone_id
            """)
        data = {"phone_number": new_phone.phone_number, "mb": mb, "phone_id": phone_id}

        session.execute(query, data)

        return True

    @staticmethod
    def updateLegalRepresentativeInPostgres(
        mb: int, legal_rep_id: int, new_legal_rep: LegalRepresentative, session: Session
    ):
        query = text("""
                UPDATE legal_representatives
                SET cpf = :cpf, full_name = :full_name, email = :email, phone = :phone, alternative_phone = :alternative_phone, observations = :observations
                WHERE registration_id = :mb AND representative_id = :legal_rep_id
            """)
        data = {
            "cpf": new_legal_rep.cpf,
            "full_name": new_legal_rep.full_name,
            "email": new_legal_rep.email,
            "phone": new_legal_rep.phone,
            "alternative_phone": new_legal_rep.alternative_phone,
            "observations": new_legal_rep.observations,
            "mb": mb,
            "legal_rep_id": legal_rep_id,
        }

        session.execute(query, data)

        return True

    @staticmethod
    def getAllMemberDataFromPostgres(
        mb: int, session: Session
    ) -> str:  # Return type changed to str
        # Retrieve information from the database
        address = MemberRepository.getAddressesFromPostgres(mb, session)
        phone = MemberRepository.getPhonesFromPostgres(mb, session)
        email = MemberRepository.getEmailsFromPostgres(mb, session)
        member_data = MemberRepository.getFromPostgres(mb, session)
        legal_representatives = MemberRepository.getLegalRepresentativesFromPostgres(mb, session)

        # Convert Address objects to dictionaries
        address_data = [address.__dict__ for address in address]

        # Convert Phone objects to dictionaries
        phone_data = [phone.__dict__ for phone in phone]

        # Convert Email objects to dictionaries
        email_data = [email.__dict__ for email in email]

        legal_representatives_data = [
            legal_representative.__dict__ for legal_representative in legal_representatives
        ]

        # Create a dictionary to store the information
        member_info = {
            "addresses": address_data,
            "phones": phone_data,
            "emails": email_data,
            "member": member_data.__dict__,
            "legal_representatives": legal_representatives_data,
        }

        # Convert the dictionary to a JSON string
        json_data = json.dumps(member_info, cls=CustomJSONEncoder)

        # Return the JSON string
        return json_data

    @staticmethod
    def getFromPostgres(member_id: int, session: Session) -> PostgresMemberRegistration:
        """Retrieve a single Member by its unique id"""
        query = text("""SELECT * FROM registration WHERE "registration_id" = :member_id""")
        result = session.execute(query, {"member_id": member_id})
        data = result.fetchone()
        if data:
            return PostgresMemberRegistration(**data._mapping)
        else:
            raise PersonNotFoundException(member_id)

    @staticmethod
    def getAddressesFromPostgres(
        member_id: int, session: Session
    ) -> list[Address]:  # Return type updated
        query = text("""SELECT * FROM addresses WHERE "registration_id" = :member_id""")
        result = session.execute(query, {"member_id": member_id})
        data = result.fetchall()
        if data:
            return [Address(**address._asdict()) for address in data]
        return []

    @staticmethod
    def getPhonesFromPostgres(member_id: int, session: Session) -> list[Phone]:
        query = text("""SELECT * FROM phones WHERE "registration_id" = :member_id""")
        result = session.execute(query, {"member_id": member_id})
        data = result.fetchall()

        if data:
            # Convert Row object to a dictionary using _mapping for unpacking
            return [Phone(**phone._mapping) for phone in data]

        return []

    @staticmethod
    def updateProfessionAndFacebookOnPostgres(
        member_id: int, profession: str, facebook: str, session: Session
    ):
        query = text(
            """UPDATE registration SET profession = :profession, facebook = :facebook WHERE registration_id = :member_id"""
        )
        session.execute(
            query,
            {"profession": profession, "facebook": facebook, "member_id": member_id},
        )

        return True

    @staticmethod
    def getEmailsFromPostgres(
        member_id: int, session: Session
    ) -> list[Email]:  # Return type updated
        query = text("""SELECT * FROM emails WHERE "registration_id" = :member_id""")
        result = session.execute(query, {"member_id": member_id})
        data = result.fetchall()
        if data:
            return [Email(**email._mapping) for email in data]
        return []

    @staticmethod
    def getLegalRepresentativesFromPostgres(
        member_id: int, session: Session
    ) -> list[LegalRepresentative]:
        query = text("""SELECT * FROM legal_representatives WHERE "registration_id" = :member_id""")
        result = session.execute(query, {"member_id": member_id})
        data = result.mappings().all()  # fetch all rows as dict-like mappings

        if data:
            return [LegalRepresentative(**legal_representative) for legal_representative in data]

        return []

    @staticmethod
    def getMBByEmail(email: str, session: Session) -> int:
        query = text("""SELECT "registration_id" FROM emails WHERE "email_address" = :email""")
        result = session.execute(query, {"email": email})
        data = result.fetchone()
        if data:
            return data[0]
        else:
            raise PersonNotFoundException(email)

    @staticmethod
    def getFromFirebase(member_id: int) -> FirebaseMemberRead:
        """Retrieve a single Member by its unique id"""
        document = firebase_collection.document(str(member_id)).get()

        if document.exists:
            data = document.to_dict()
            data["updated_at"] = data["updated_at"].date()
            return FirebaseMemberRead(**data)
        else:
            raise PersonNotFoundException(member_id)

    @staticmethod
    def getFromFirebaseByEmail(email: str) -> FirebaseMemberRead:
        """Retrieve a single Member by its unique email"""
        documents = firebase_collection.where("email", "==", email).get()
        if len(documents) > 0:
            data = documents[0].to_dict()
            data["updated_at"] = data["updated_at"].date()
            return FirebaseMemberRead(**data)
        else:
            raise PersonNotFoundException(email)
