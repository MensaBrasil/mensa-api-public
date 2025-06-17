# type: ignore
# pylint: disable-all
# ruff: noqa

"""APP
FastAPI app definition, initialization and definition of routes
"""

# # Installed # #
import json
import secrets
import string
from datetime import datetime

from decouple import config
from fastapi import (
    Depends,
    FastAPI,
    Form,
    Header,
    HTTPException,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pydantic import ValidationError, BaseModel
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN

from .auth import verify_firebase_token
from .dbs import get_session
from .endpoints import data_router, whatsapp_router
from .exceptions import *
from .middlewares import request_handler


# # Package # #
from .models import *
from .repositories import MemberRepository
from .settings import api_settings as settings
from .static import download_cert
from .utils import create_certificate
from .settings import DataRouteSettings

SECRET_KEY = config("GOOGLE_API_KEY", "notoken")

app = FastAPI(title=settings.title, docs_url="/documentation$@vtW6qodxYLQ", redoc_url=None)
app.middleware("http")(request_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://carteirinhas.mensa.org.br",
        "https://app.flutterflow.io",
    ],  # List of origins permitted to make requests
    allow_credentials=True,  # Allow cookies to be included in requests
    allow_methods=["*"],  # List of allowed HTTP methods
    allow_headers=["*"],  # List of allowed HTTP headers
)

app.include_router(data_router)
app.include_router(whatsapp_router)


def verify_secret_key(x_api_key: str = Header(...)):
    if x_api_key != SECRET_KEY:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return x_api_key


def generate_password(length=9):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for i in range(length))


# Replace with your service account key JSON file path
SERVICE_ACCOUNT_KEY_PATH = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/admin.directory.user"]


def create_google_workspace_user(primary_email, given_name, family_name, secondary_email=None):
    # Generate a random password
    password = generate_password()

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_KEY_PATH, scopes=SCOPES
    )
    service = build("admin", "directory_v1", credentials=creds)

    user = {
        "primaryEmail": primary_email,
        "name": {
            "givenName": given_name,
            "familyName": "\u200e",
        },
        "password": password,
        "changePasswordAtNextLogin": True,
    }

    if secondary_email:
        user["emails"] = [{"address": secondary_email, "type": "work"}]

    try:
        response = service.users().insert(body=user).execute()
        return response, password  # Return the response and the generated password
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# set user pronouns
@app.patch("/pronouns", description="Set pronouns for member", tags=["member"])
async def _set_pronouns(
    pronouns: PronounsCreate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    # should only accept Ele/dele, Ela/dela, Elu/delu
    if (
        pronouns.pronouns != "Ele/dele"
        and pronouns.pronouns != "Ela/dela"
        and pronouns.pronouns != "Elu/delu"
        and pronouns.pronouns != "Nenhuma das opções"
    ):
        raise HTTPException(
            status_code=400,
            detail="Pronouns must be Ele/dele, Ela/dela or Elu/delu or Nenhuma das opções",
        )
    MemberRepository.setPronounsOnPostgres(MB, pronouns.pronouns, session)
    return {"message": "Pronouns set successfully"}


@app.get("/get_member_groups", description="Get member groups", tags=["member"])
async def _get_member_groups(
    token_data=Depends(verify_firebase_token), session: Session = Depends(get_session)
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    member_groups = MemberRepository.getMemberGroupsFromPostgres(MB, session)
    return member_groups


@app.post("/request_join_group", tags=["member"], description="Request to join a group")
async def _request_join_group(
    join_request: GroupJoinRequest,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    registration_id = MemberRepository.getMBByEmail(token_data["email"], session)
    phones = MemberRepository.getAllMemberAndLegalRepPhonesFromPostgres(registration_id, session)

    # Raise an HTTPException if no phones are associated with the user
    if not phones:
        raise HTTPException(
            status_code=400, detail="Não há número de telefone registrado para o usuário."
        )

    # for each phone, add a request
    for phone in phones:
        # check if a request exists for the phone
        if (
            MemberRepository.getGroupRequestId(phone["phone"], join_request.group_id, session)
            == None
        ):
            # check if phone is not an empty string and has more than 6 characters
            if phone["phone"] == "" or len(phone["phone"]) < 6:
                print("error: Phone is not valid")
            else:
                created_at = datetime.now()
                last_attempt = None
                fulfilled = False

                # Add request to join group in the database
                MemberRepository.addGroupRequest(
                    registration_id,
                    phone["phone"],
                    join_request.group_id,
                    created_at,
                    last_attempt,
                    fulfilled,
                    session,
                )
    return {"message": "Request to join group sent successfully"}


# every user must have cpf, birth_date. if it doesnt have one of these, return the list of the missing fields
@app.get(
    "/missing_fields",
    description="Get missing fields from member",
    tags=["missing_fields"],
)
async def _get_missing_fields(
    token_data=Depends(verify_firebase_token), session: Session = Depends(get_session)
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    missing_fields = MemberRepository.getMissingFieldsFromPostgres(MB, session)
    return missing_fields


# set the missing fields of a member
@app.post(
    "/missing_fields",
    description="Set missing fields from member",
    tags=["missing_fields"],
)
async def _set_missing_fields(
    missing_fields: MissingFieldsCreate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    # check if user really has those fields missing, if not, deny
    missing_fields_list = MemberRepository.getMissingFieldsFromPostgres(MB, session)
    # set only fields that are missing
    if missing_fields.cpf != None:
        if "cpf" in missing_fields_list:
            print("cpf")
            MemberRepository.setCPFOnPostgres(MB, missing_fields.cpf, session)
    if missing_fields.birth_date != None:
        if "birth_date" in missing_fields_list:
            print("birth_date")
            MemberRepository.setBirthDateOnPostgres(MB, missing_fields.birth_date, session)
    return {"message": "Missing fields set successfully"}


# update Profession and Facebook url in Postgres
@app.put(
    "/update_fb_profession/{mb}",
    description="Update profession and facebook url for member",
    tags=["member"],
)
async def update_fb_profession(
    mb: int,
    updated_member: MemberProfessionFacebookUpdate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    # Get firebase user data of user token_data['uid']
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # Call the update method to modify the member
    profession = updated_member.profession
    facebook = updated_member.facebook
    success = MemberRepository.updateProfessionAndFacebookOnPostgres(
        mb, profession, facebook, session
    )
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")

    return {"message": "Member updated successfully"}


# crud for member email, phone, address, legal representative
@app.post("/address/{mb}", description="Add address to member", tags=["address"])
async def _add_address(
    mb: int,
    address: AddressCreate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # user can just have one address
    member_data = MemberRepository.getAddressesFromPostgres(mb, session)
    if len(member_data) > 0:
        raise HTTPException(status_code=400, detail="User already has an address")

    MemberRepository.addAddressToPostgres(mb, address, session)
    return {"message": "Address added successfully"}


@app.post("/phone/{mb}", description="Add phone to member", tags=["phone"])
async def _add_phone(
    mb: int,
    phone: PhoneCreate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # user can just have one phone
    member_data = MemberRepository.getPhonesFromPostgres(mb, session)
    if len(member_data) > 0:
        raise HTTPException(status_code=400, detail="User already has a phone")
    MemberRepository.addPhoneToPostgres(mb, phone, session)
    return {"message": "Phone added successfully"}


@app.post("/email/{mb}", description="Add email to member", tags=["email"])
async def _add_email(
    mb: int,
    email: EmailCreate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
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


@app.post(
    "/legal_representative/{mb}",
    description="Add legal representative to member",
    tags=["legal_representative"],
)
async def _add_legal_representative(
    mb: int,
    legal_representative: LegalRepresentativeCreate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # user must be under 18 to add legal representative
    member_data = MemberRepository.getFromPostgres(mb, session)
    if member_data.birth_date == None:
        raise HTTPException(
            status_code=400,
            detail="User must have birth date to add legal representative",
        )
    birth_date = member_data.birth_date
    current_date = datetime.now().date()
    age = (
        current_date.year
        - birth_date.year
        - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
    )

    if age > 18:
        raise HTTPException(
            status_code=400, detail="User must be under 18 to add legal representative"
        )
    # user can only have two legal representatives
    member_data = MemberRepository.getLegalRepresentativesFromPostgres(mb, session)
    if len(member_data) > 1:
        raise HTTPException(status_code=400, detail="User already has two legal representatives")
    MemberRepository.addLegalRepresentativeToPostgres(mb, legal_representative, session)
    return {"message": "Legal representative added successfully"}


class LegalRepresentativeRequest(BaseModel):
    token: str
    mb: str
    birth_date: str
    cpf: str
    legal_representative: LegalRepresentativeCreate


@app.post(
    "/legal_representative_twilio",
    description="Add legal representative to member using API key authentication",
    tags=["legal_representative"],
)
async def add_legal_representative_api_key(
    request: LegalRepresentativeRequest,
    session: Session = Depends(get_session),
):
    if request.token != DataRouteSettings.whatsapp_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    request.mb = int(request.mb)
    member_data = MemberRepository.getFromPostgres(request.mb, session)

    try:
        request.birth_date = datetime.strptime(request.birth_date, "%d/%m/%Y").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid birth date format. Use dd/mm/YYYY.")

    # check birth matches
    if member_data.birth_date != request.birth_date:
        raise HTTPException(status_code=400, detail="Birth date does not match")

    if member_data.cpf != request.cpf:
        raise HTTPException(status_code=400, detail="CPF does not match")

    legal_representative = request.legal_representative

    member_data = MemberRepository.getFromPostgres(request.mb, session)
    if member_data.birth_date is None:
        raise HTTPException(
            status_code=400,
            detail="User must have birth date to add legal representative",
        )

    birth_date = member_data.birth_date
    current_date = datetime.now().date()
    age = (
        current_date.year
        - birth_date.year
        - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
    )

    MemberRepository.addLegalRepresentativeToPostgres(request.mb, legal_representative, session)
    return {"message": "Legal representative added successfully"}


@app.delete(
    "/address/{mb}/{address_id}",
    description="Delete address from member",
    tags=["address"],
)
async def delete_address(
    mb: int,
    address_id: int,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Call the delete method to remove the address
    success = MemberRepository.deleteAddressFromPostgres(mb, address_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Address not found")

    return {"message": "Address deleted successfully"}


@app.delete("/phone/{mb}/{phone_id}", description="Delete phone from member", tags=["phone"])
async def delete_phone(
    mb: int,
    phone_id: int,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Call the delete method to remove the phone
    success = MemberRepository.deletePhoneFromPostgres(mb, phone_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Phone not found")

    return {"message": "Phone deleted successfully"}


@app.delete("/email/{mb}/{email_id}", description="Delete email from member", tags=["email"])
async def delete_email(
    mb: int,
    email_id: int,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
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


@app.delete(
    "/legal_representative/{mb}/{legal_rep_id}",
    description="Delete legal representative from member",
    tags=["legal_representative"],
)
async def delete_legal_representative(
    mb: int,
    legal_rep_id: int,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Call the delete method to remove the legal representative
    success = MemberRepository.deleteLegalRepresentativeFromPostgres(mb, legal_rep_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Legal representative not found")

    return {"message": "Legal representative deleted successfully"}


@app.put(
    "/address/{mb}/{address_id}",
    description="Update address for member",
    tags=["address"],
)
async def update_address(
    mb: int,
    address_id: int,
    updated_address: AddressUpdate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Call the update method to modify the address
    success = MemberRepository.updateAddressInPostgres(mb, address_id, updated_address, session)
    if not success:
        raise HTTPException(status_code=404, detail="Address not found")

    return {"message": "Address updated successfully"}


@app.put("/phone/{mb}/{phone_id}", description="Update phone for member", tags=["phone"])
async def update_phone(
    mb: int,
    phone_id: int,
    updated_phone: PhoneUpdate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Call the update method to modify the phone
    success = MemberRepository.updatePhoneInPostgres(mb, phone_id, updated_phone, session)
    if not success:
        raise HTTPException(status_code=404, detail="Phone not found")

    return {"message": "Phone updated successfully"}


@app.put("/email/{mb}/{email_id}", description="Update email for member", tags=["email"])
async def update_email(
    mb: int,
    email_id: int,
    updated_email: EmailUpdate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
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


@app.put(
    "/legal_representative/{mb}/{legal_rep_id}",
    description="Update legal representative for member",
    tags=["legal_representative"],
)
async def update_legal_representative(
    mb: int,
    legal_rep_id: int,
    updated_legal_rep: LegalRepresentativeUpdate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Call the update method to modify the legal representative
    success = MemberRepository.updateLegalRepresentativeInPostgres(
        mb, legal_rep_id, updated_legal_rep, session
    )
    if not success:
        raise HTTPException(status_code=404, detail="Legal representative not found")

    return {"message": "Legal representative updated successfully"}


@app.get(
    "/get_member/{mb}",
    response_model=PostgresMemberRead,
    description="Get a single member by its unique ID",
    responses=get_exception_responses(PersonNotFoundException),
    tags=["member"],
)
# , token: string = Depends(verify_firebase_token)
async def _get_member(
    mb: int, token_data=Depends(verify_firebase_token), session: Session = Depends(get_session)
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)

    member_data = MemberRepository.getAllMemberDataFromPostgres(MB, session)

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

    return validated_data


@app.post(
    "/create_user/",
    include_in_schema=True,
    description="Create a new user in Google Workspace",
)
async def _create_user(
    primary_email: str = Form(...),
    given_name: str = Form(...),
    family_name: str = Form(...),
    secondary_email: str = Form(None),
    api_key: str = Depends(verify_secret_key),
):
    try:
        user_data, password = create_google_workspace_user(
            primary_email, given_name, family_name, secondary_email
        )  # Capture the returned password
        return {
            "message": "User created successfully",
            "user_data": {"email": user_data["primaryEmail"], "password": password},
        }
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "User creation failed", "error": e.detail},
        )


@app.get("/download_certificate.png", description="Gerar certificado", tags=["certificado"])
async def _get_certificado(MB: int, key: str):  # Note que eu mudei o tipo de MB para int
    # check if key matches CertificateKey in the database
    member = MemberRepository.getFromFirebase(MB)
    if member.CertificateToken != key:
        return {"error": "Chave inválida"}
    cert = create_certificate(member.display_name, MB, member.expiration_date)
    return StreamingResponse(
        cert,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=certificate.png"},
    )


@app.get(
    "/certificado",
    response_class=HTMLResponse,
    description="Gerar botão certificado",
    tags=["certificado"],
)
async def _show_download_button(MB: int, key: str):
    return download_cert(MB, key)
