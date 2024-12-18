"""REPOSITORIES
Methods to interact with the database
"""

# # Package # #
import json
from datetime import date, datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

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
    def getCanParticipate(mb: int, session: Session):
        query = text(
            """
            select
                gl.group_id,
                gl.group_name
            from
                group_list gl
            left join (
                select
                    group_id,
                    registration_id,
                    entry_date,
                    exit_date,
                    row_number() over (partition by group_id
                order by
                    exit_date desc nulls first) as rn
                from
                    member_groups
                where
                    registration_id = :mb
                                    ) mg on
                gl.group_id = mg.group_id
                and mg.rn = 1
            inner join registration r on
                r.registration_id = :mb
            where
                (r.birth_date <= CURRENT_DATE - interval '18 year'
                    and gl.group_name not like '%%JB%%'
                    and gl.group_name not like '%%OrgMB%%')
                or (r.birth_date > CURRENT_DATE - interval '18 year'
                    and gl.group_name like '%%JB%%'
                    and gl.group_name not like '%%OrgMB%%'
                    and gl.group_name not like 'Avisos Mensa JB%%')
            order by
                case
                    when mg.entry_date is not null
                    and mg.exit_date is null then 1
                    when mg.entry_date is not null
                    and mg.exit_date is not null then 2
                    else 3
                end,
                mg.exit_date desc,
                gl.group_name
            """
        )
        result = session.execute(query, {"mb": mb})
        data = result.fetchall()
        if data:
            column_names = [column for column in result.keys()]
            return [{k: v for k, v in zip(column_names, row)} for row in data]
        return []

    @staticmethod
    def getParticipateIn(mb: int, session: Session):
        query = text(
            """
            select
                gl.group_name,
                mg.entry_date
            from
                member_groups mg
            inner join
                group_list gl on
                mg.group_id = gl.group_id
            where
                mg.registration_id = :mb
                and mg.status = 'Active'
            """
        )
        result = session.execute(query, {"mb": mb})
        data = result.fetchall()
        if data:
            column_names = [column for column in result.keys()]
            return [{k: v for k, v in zip(column_names, row)} for row in data]
        return []

    @staticmethod
    def getPendingRequests(mb: int, session: Session):
        query = text(
            """
            select
                gl.group_name,
                max(gr.last_attempt) as last_attempt,
                max(gr.no_of_attempts) as no_of_attempts
            from
                group_requests gr
            inner join
                group_list gl
            on
                gr.group_id = gl.group_id
            where
                gr.registration_id = :mb
                and gr.fulfilled = false
                and gr.no_of_attempts < 3
            group by
                gr.group_id,
                gl.group_name
            order by last_attempt desc nulls last
            """
        )
        result = session.execute(query, {"mb": mb})
        data = result.fetchall()
        if data:
            column_names = [column for column in result.keys()]
            return [{k: v for k, v in zip(column_names, row)} for row in data]
        return []

    @staticmethod
    def getFailedRequests(mb: int, session: Session):
        query = text(
            """
            select
                gl.group_name,
                max(gr.last_attempt) as last_attempt
            from
                group_requests gr
            inner join
                group_list gl
            on
                gr.group_id = gl.group_id
            where
                gr.registration_id = :mb
                and gr.fulfilled = false
                and gr.no_of_attempts >= 3
            group by
                gr.group_id,
                gl.group_name
            order by
                last_attempt desc nulls last
            """
        )
        result = session.execute(query, {"mb": mb})
        data = result.fetchall()
        if data:
            column_names = [column for column in result.keys()]
            return [{k: v for k, v in zip(column_names, row)} for row in data]
        return []

    @staticmethod
    def idMemberOfGroup(phone_number: int, group_id: str, session: Session) -> bool:
        query = text("""
                SELECT EXISTS(
                    SELECT 1 FROM member_groups WHERE phone_number = :phone_number AND group_id = :group_id
                )
            """)
        result = session.execute(query, {"phone_number": phone_number, "group_id": group_id})
        return result.fetchone()[0]

    @staticmethod
    def getUnfullfilledGroupRequests(mb: int, session: Session) -> list:
        """Retrieve a list of unfulfilled group requests for a member"""
        query = text("""
                SELECT group_id
                FROM group_requests
                WHERE fulfilled = false
                AND registration_id = :mb
                AND no_of_attempts < 3
            """)
        result = session.execute(query, {"mb": mb})
        data = result.scalars().all()
        if data:
            return result
        return None

    @staticmethod
    def getFailedGroupRequests(mb: int, session: Session) -> list:
        """Retrieve a list of failed group requests for a member"""
        query = text("""
                SELECT group_id
                FROM group_requests
                WHERE fulfilled = false
                AND registration_id = :mb
                AND no_of_attempts >= 3
            """)
        result = session.execute(query, {"mb": mb})
        data = result.scalars().all()
        if data:
            return data
        return None

    @staticmethod
    def updateFailedGroupRequests(mb: int, session: Session):
        query = text("""
                UPDATE group_requests
                SET no_of_attempts = 0
                WHERE registration_id = :mb
                AND fulfilled = false
                AND group_id IN (
                    SELECT group_id
                    FROM group_requests
                    WHERE fulfilled = false
                    AND registration_id = :mb
                    AND no_of_attempts >= 3
                )
            """)
        session.execute(query, {"mb": mb})
        return True

    @staticmethod
    def addGroupRequest(
        registration_id: int,
        group_id: str,
        created_at: datetime,
        last_attempt: datetime,
        fulfilled: bool,
        session: Session,
    ):
        query = text("""
                INSERT INTO group_requests (registration_id, group_id, created_at, last_attempt, fulfilled)
                VALUES (:registration_id, :group_id, :created_at, :last_attempt, :fulfilled) RETURNING id
            """)
        result = session.execute(
            query,
            {
                "registration_id": registration_id,
                "group_id": group_id,
                "created_at": created_at,
                "last_attempt": last_attempt,
                "fulfilled": fulfilled,
            },
        )
        request_id = result.fetchone()[0]
        return request_id

    @staticmethod
    def getAllMemberAndLegalRepPhonesFromPostgres(mb: int, session: Session) -> list:
        query = text("""SELECT
                phone_number AS phone  -- Alias the column as 'phone'
            FROM
                phones
            WHERE
                registration_id = :mb
            UNION ALL
            SELECT
                phone AS phone  -- Alias the column as 'phone'
            FROM
                legal_representatives
            WHERE
                registration_id = :mb
            UNION ALL
            SELECT
                alternative_phone AS phone  -- Alias the column as 'phone'
            FROM
                legal_representatives
            WHERE
                registration_id = :mb
                AND alternative_phone IS NOT NULL;
                    """)
        result = session.execute(query, {"mb": mb})
        data = result.fetchall()
        if data:
            column_names = [column for column in result.keys()]
            return [dict(zip(column_names, row)) for row in data]
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
