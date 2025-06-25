# mypy: ignore-errors

"""Service for managing members email addresses."""

from datetime import date
from enum import StrEnum

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from people_api.database.models.pending_registration import PendingRegistrationData
from people_api.schemas import UserToken
from people_api.settings import get_whatsapp_groups_settings

from ..database.models.models import EmailInput, Emails, Registration
from ..services.workspace_service import WorkspaceService


class EmailService:
    """Service for managing members email addresses."""

    @staticmethod
    def add_email(mb: int, email: EmailInput, token_data: UserToken, session: Session):
        """Add email to member."""
        reg_stmt = Registration.select_stmt_by_email(token_data.email)
        member_data = session.exec(reg_stmt).first()
        if not member_data or member_data.registration_id != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")
        if email.email_type in ("main", "alternative"):
            stmt = Emails.get_emails_for_member(mb)
            existing_emails = session.exec(stmt).all()
            for e in existing_emails:
                if e.email_type == email.email_type:
                    raise HTTPException(
                        status_code=400,
                        detail="User already has email of type " + email.email_type,
                    )
        insert_stmt = Emails.insert_stmt_for_email(mb, email)
        session.exec(insert_stmt)
        return {"message": "Email added successfully"}

    @staticmethod
    def update_email(
        mb: int,
        email_id: int,
        updated_email: EmailInput,
        token_data: UserToken,
        session: Session,
    ):
        """Update email for member."""
        reg_stmt = Registration.select_stmt_by_email(token_data.email)
        member_data = session.exec(reg_stmt).first()
        if not member_data or member_data.registration_id != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if updated_email.email_type == "mensa":
            raise HTTPException(status_code=400, detail="Email type cannot be mensa")

        update_stmt = Emails.update_stmt_for_email(mb, email_id, updated_email)
        result = session.exec(update_stmt)
        if result.rowcount is None or result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Email not found")
        return {"message": "Email updated successfully"}

    @staticmethod
    def delete_email(mb: int, email_id: int, token_data: UserToken, session: Session):
        """Delete email from member."""
        reg_stmt = Registration.select_stmt_by_email(token_data.email)
        member_data = session.exec(reg_stmt).first()

        if not member_data or member_data.registration_id != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")

        stmt = Emails.get_emails_for_member(mb)
        existing_emails = session.exec(stmt).all()

        for e in existing_emails:
            if e.email_id == email_id and e.email_type == "mensa":
                raise HTTPException(status_code=400, detail="Cannot delete email of type mensa")

        delete_stmt = Emails.delete_stmt_for_email(mb, email_id)
        result = session.exec(delete_stmt)

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Email not found")

        return {"message": "Email deleted successfully"}

    @staticmethod
    async def request_email_creation(registration_id: int, session: AsyncSession):
        """Request email creation for a member."""

        return await WorkspaceService.create_mensa_email(
            registration_id=registration_id, session=session
        )

    @staticmethod
    async def request_password_reset(email: str, registration_id: int, session: AsyncSession):
        """Request password reset for a member."""
        try:
            if not email or not email.endswith("@mensa.org.br"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email must be a Mensa email",
                )

            db_emails = (await session.exec(Emails.get_emails_for_member(registration_id))).all()
            for e in db_emails:
                if e.email_address and e.email_address.endswith("@mensa.org.br"):
                    email = str(e.email_address)
                    break
            else:
                email = None

            if not email:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No matching Mensa email found for this member",
                )
        except Exception as e:
            raise HTTPException(
                status_code=getattr(e, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
                detail=getattr(
                    e,
                    "detail",
                    {
                        "message": "Failed to fetch member information",
                        "error": str(e),
                    },
                ),
            ) from e

        return await WorkspaceService.reset_email_password(
            registration_id=registration_id,
            mensa_email=email,
            session=session,
        )


class AdultMembersReginalGroupsEnum(StrEnum):
    """Regional WhatsApp groups for Mensa Brazil members."""

    SAO_PAULO_CITY = get_whatsapp_groups_settings().sao_paulo_city_adult_members_group
    SAO_PAULO_STATE = get_whatsapp_groups_settings().sao_paulo_state_adult_members_group
    SOUTHEAST = get_whatsapp_groups_settings().southeast_adult_members_group
    SOUTH = get_whatsapp_groups_settings().south_adult_members_group
    CENTER_WEST_NORTH = get_whatsapp_groups_settings().center_west_north_adult_members_group
    NORTHEAST = get_whatsapp_groups_settings().northeast_adult_members_group


class LegalRepsRegionalGroupsEnum(StrEnum):
    """Regional WhatsApp groups for legal reps of underage Mensa Brazil members."""

    SAO_PAULO_CITY = get_whatsapp_groups_settings().sao_paulo_city_legal_reps_group
    SAO_PAULO_STATE = get_whatsapp_groups_settings().sao_paulo_state_legal_reps_group
    SOUTHEAST = get_whatsapp_groups_settings().southeast_legal_reps_group
    SOUTH = get_whatsapp_groups_settings().south_legal_reps_group
    CENTER_WEST_NORTH = get_whatsapp_groups_settings().center_west_north_legal_reps_group
    NORTHEAST = get_whatsapp_groups_settings().northeast_legal_reps_group


def get_regional_group_string_by_region(
    city: str,
    state: str,
    is_legal_rep: bool = False,
) -> str:
    """
    Get the WhatsApp group link for a given region.
    """
    if not state:
        return ""

    state = state.upper()
    group_enum = LegalRepsRegionalGroupsEnum if is_legal_rep else AdultMembersReginalGroupsEnum

    if is_legal_rep:
        link_template = """Fique atento também ao nosso grupo de <strong>COMUNICADOS</strong> aos responsáveis pelos jovens brilhantes, nele compartilhamos eventos da associação e informações importantes: <a href={0}>{0}</a>"""
    else:
        link_template = """
    <p>Para saber notícias e convites oficiais da associação, você também pode entrar no grupo de avisos do WhatsApp através deste link:<br>
        <a href={0}>{0}</a></p>
    """

    if city and "SAO PAULO" in city.upper().replace("Ã", "A").replace("Á", "A").replace(
        "À", "A"
    ).replace("Â", "A").replace("Ä", "A"):
        return link_template.format(group_enum.SAO_PAULO_CITY)

    if state == "SP":
        return link_template.format(group_enum.SAO_PAULO_STATE)

    region_mapping = {
        "SOUTHEAST": ["RJ", "MG", "ES"],
        "SOUTH": ["PR", "SC", "RS"],
        "CENTER_WEST_NORTH": ["DF", "GO", "MT", "MS", "TO", "AM", "AC", "RO", "RR", "PA", "AP"],
        "NORTHEAST": ["BA", "PE", "CE", "MA", "PI", "RN", "PB", "SE", "AL"],
    }

    for region, states in region_mapping.items():
        if state in states:
            group_link = getattr(group_enum, region)
            return link_template.format(group_link)

    return ""


class EmailTemplates:
    """Service to load and render email templates for new members."""

    TEMPLATES = {
        "BOAS VINDAS JB (DE 2 À 9 ANOS)": """
<html>
<head>
  <meta charset="UTF-8">
  <title>Seja bem-vindo(a) à Mensa Brasil!</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #ecf0f1; margin:0; padding:20px;">
  <div style="max-width:600px; margin:0 auto; background-color:#ffffff; padding:20px; border-radius:8px;">
    <h1 style="color: #2c3e50; text-align: center; margin-top:0;">Seja bem-vindo(a) à Mensa Brasil!</h1>
    <h2 style="color: #3498db; margin-bottom:20px;">{FULL_NAME}</h2>
    <p style="color:#333333; line-height:1.5;">É uma honra recebê-lo(a) como associado(a) da Mensa. Pessoas com QI no top 2% são raras e foi um desafio encontrá-lo(a). Agora, podemos nos orgulhar de fazer parte da mesma família.</p>
    <p style="color:#333333; line-height:1.5;">Seu número de cadastro é <strong>{REGISTRATION_ID}</strong> e você faz parte de um seleto grupo de mais de 4.000 mensans no Brasil e de mais de 100.000 mensans em todo o mundo. Ao compartilhar sua inteligência com os demais membros, você traz sua individualidade e paixão à nossa organização. Entre nossos membros, há uma diversidade de pessoas geniais. A partir de agora, você conhecerá um amplo grupo de pessoas interessadas em diversos temas, desde paleontologia até futurologia, de hieróglifos a literatura, de triathlon a genealogia. Esperamos que você contribua com seu valor único e reconheça o valor igualmente singular dos demais membros.</p>
    <p style="color:#333333; line-height:1.5;">Quanto mais você se envolver, maior será o aproveitamento de sua condição de membro. Algo genuinamente especial ocorre quando temos a oportunidade de criar vínculos de afeto e amizade. Nesses momentos, percebemos o valor de sermos diferentes e, ainda assim, tão próximos. Sentimos que esses vínculos nos tornam mais que amigos: somos uma família.</p>
    <p style="color:#333333; line-height:1.5;">Por ter <strong>{AGE} anos</strong>, você integrou o nosso programa Jovens Brilhantes e já pode efetuar seu cadastro no site da Mensa Internacional: <a href="https://www.mensa.org" style="color:#3498db;">www.mensa.org</a> &gt; Member &gt; Create New Account. A aprovação de sua conta pode levar até uma semana.</p>
    <div style="border-left:4px solid #3498db; background-color:#ecf6fc; padding:15px; margin:20px 0; border-radius:4px;">
      <p style="margin:0; color:#333333;">Seu e-mail institucional é <strong>{EMAIL_INSTITUCIONAL}</strong> e sua senha temporária é <strong>{TEMP_PASSWORD}</strong>. Você pode acessar sua caixa de entrada pelo Gmail.</p>
    </div>
    <p style="color:#333333; line-height:1.5;">Sua carteirinha digital pode ser acessada pelo aplicativo Mensa Brasil, mediante login com seu e-mail institucional.</p>
    <div style="border-left:4px solid #e74c3c; background-color:#fdecea; padding:15px; margin:20px 0; border-radius:4px;">
      <p style="margin:0; color:#333333;"><strong>Observe que, caso você entre em algum grupo com um número de telefone não cadastrado, será removido automaticamente. Utilize o telefone informado no cadastro.</strong></p>
    </div>
    <div style="border-left:4px solid #3498db; background-color:#ecf6fc; padding:15px; margin:20px 0; border-radius:4px;">
      <p style="margin:0; color:#333333;"><strong>Também dispomos de uma comunidade no WhatsApp exclusiva para interação entre jovens brilhantes, com diversos grupos de interesses específicos. Caso o jovem brilhante não possua celular próprio, poderá utilizar o aparelho de seu responsável. Entretanto, solicitamos que os responsáveis não participem da comunidade, pois a atividade é destinada exclusivamente às crianças. Agradecemos a colaboração. Link para a comunidade Jovens Brilhantes: <a href="{MJB_GROUP_LINK}" style="color:#3498db;">{MJB_GROUP_LINK}</a></strong></p>
    </div>
    <p style="color:#333333; margin-bottom:0;">Atenciosamente,</p>
    <p style="color:#2c3e50; margin-top:5px;"><strong>Secretaria - Associação Mensa Brasil</strong><br>
    <a href="https://www.mensa.org.br" style="color:#3498db;">www.mensa.org.br</a></p>
  </div>
</body>
</html>
""",
        "BOAS VINDAS RESPJB (DE 2 À 9 ANOS)": """
<html>
<head>
  <meta charset="UTF-8">
  <title>Bem-vindo(a) à Mensa Brasil!</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #ecf0f1; margin:0; padding:20px;">
  <div style="max-width:600px; margin:0 auto; background-color:#ffffff; padding:20px; border-radius:8px;">
    <h2 style="color:#2c3e50; margin-top:0;">Prezado(a) responsável, <span style="color:#3498db;">{GUARDIAN_NAME}</span></h2>
    <p style="color:#333333; line-height:1.5;">A Associação Mensa Brasil tem o grande prazer de dar as boas-vindas aos nossos Jovens Brilhantes. É com orgulho que recebemos seu(sua) filho(a) em nossa comunidade.</p>
    <p style="color:#333333; line-height:1.5;">Saiba que, quanto mais você se envolver com seu(sua) filho(a), mais ele(a) aproveitará as oportunidades oferecidas pela Mensa.</p>
    <p style="text-align:center; font-weight:bold; color:#333333; background-color:#ecf6fc; padding:15px; margin:20px 0; border-radius:4px;">Contamos com o apoio de todos vocês, pais e responsáveis, nesta nova jornada ao lado daqueles que mais amam!</p>
    <div style="border-left:4px solid #3498db; background-color:#ecf6fc; padding:15px; margin:20px 0; border-radius:4px;">
      <p style="margin:0; color:#333333;"><strong>Convite para a comunidade Jovens Brilhantes:</strong><br>
      <a href="{RJB_GROUP_LINK}" style="color:#3498db;">{RJB_GROUP_LINK}</a></p>
    </div>
    {GRUPO_REGIONAL}
    <div style="border-left:4px solid #e74c3c; background-color:#fdecea; padding:15px; margin:20px 0; border-radius:4px;">
      <p style="margin:0; color:#333333;"><strong>Observe que, caso você entre em algum grupo com um número de telefone não cadastrado, será removido automaticamente. Utilize o telefone informado no cadastro.</strong></p>
    </div>
    <div style="border-left:4px solid #27ae60; background-color:#eafaf1; padding:15px; margin:20px 0; border-radius:4px;">
      <p style="margin:0; color:#333333;">Além das comunidades mencionadas, convidamos você a participar do nosso <strong>Grupo de Primeiros Contatos</strong>. Nele, você poderá se apresentar e conhecer voluntários dispostos a ajudar e esclarecer dúvidas. É um espaço ideal para iniciar a jornada na Mensa e conectar-se com outras famílias.<br>
      Link para o grupo: <a href="{RJB_FIRST_CONTACT}" style="color:#3498db;">{RJB_FIRST_CONTACT}</a></p>
    </div>
    <p style="color:#333333; line-height:1.5;">Ficamos à disposição para eventuais dúvidas.</p>
    <p style="color:#333333; margin-bottom:0;">Atenciosamente,</p>
    <p style="color:#2c3e50; margin-top:5px;"><strong>Secretaria - Associação Mensa Brasil</strong><br>
    <a href="https://www.mensa.org.br" style="color:#3498db;">www.mensa.org.br</a></p>
  </div>
</body>
</html>
""",
        "BOAS VINDAS JB (DE 10 À 17 ANOS)": """
<html>
<head>
  <meta charset="UTF-8">
  <title>Seja bem-vindo(a) à Mensa Brasil!</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #ecf0f1; margin:0; padding:20px;">
  <div style="max-width:600px; margin:0 auto; background-color:#ffffff; padding:20px; border-radius:8px;">
    <h1 style="color: #2c3e50; text-align: center; margin-top:0;">Seja bem-vindo(a) à Mensa Brasil!</h1>
    <h2 style="color: #3498db; margin-bottom:20px;">{FULL_NAME}</h2>
    <p style="color:#333333; line-height:1.5;">É uma honra recebê-lo(a) como associado(a) da Mensa. Pessoas com QI no top 2% são raras e foi um desafio encontrá-lo(a). Agora, podemos nos orgulhar de fazer parte da mesma família.</p>
    <p style="color:#333333; line-height:1.5;">Seu número de cadastro é <strong>{REGISTRATION_ID}</strong> e você faz parte de um seleto grupo de mais de 4.000 mensans no Brasil e de mais de 100.000 mensans em todo o mundo. Ao compartilhar sua inteligência com os demais membros, você traz sua individualidade e paixão à nossa organização. Entre nossos membros, há uma diversidade de pessoas geniais. A partir de agora, você conhecerá um amplo grupo de pessoas interessadas em diversos temas, desde paleontologia até futurologia, de hieróglifos a literatura, de triathlon a genealogia. Esperamos que você contribua com seu valor único e reconheça o valor igualmente singular dos demais membros.</p>
    <p style="color:#333333; line-height:1.5;">Quanto mais você se envolver, maior será o aproveitamento de sua condição de membro. Algo genuinamente especial ocorre quando temos a oportunidade de criar vínculos de afeto e amizade. Nesses momentos, percebemos o valor de sermos diferentes e, ainda assim, tão próximos. Sentimos que esses vínculos nos tornam mais que amigos: somos uma família.</p>
    <p style="color:#333333; line-height:1.5;">Por ter <strong>{AGE} anos</strong>, você integrou o nosso programa Jovens Brilhantes e já pode efetuar seu cadastro no site da Mensa Internacional: <a href="https://www.mensa.org" style="color:#3498db;">www.mensa.org</a> &gt; Member &gt; Create New Account. A aprovação de sua conta pode levar até uma semana.</p>
    <div style="border-left:4px solid #3498db; background-color:#ecf6fc; padding:15px; margin:20px 0; border-radius:4px;">
      <p style="margin:0; color:#333333;">Seu e-mail institucional é <strong>{EMAIL_INSTITUCIONAL}</strong> e sua senha temporária é <strong>{TEMP_PASSWORD}</strong>. Você pode acessar sua caixa de entrada pelo Gmail.</p>
    </div>
    <p style="color:#333333; line-height:1.5;">Sua carteirinha digital pode ser acessada pelo aplicativo Mensa Brasil, mediante login com seu e-mail institucional.</p>
    <div style="border-left:4px solid #e74c3c; background-color:#fdecea; padding:15px; margin:20px 0; border-radius:4px;">
      <p style="margin:0; color:#333333;"><strong>Observe que, caso você entre em algum grupo com um número de telefone não cadastrado, será removido automaticamente. Utilize o telefone informado no cadastro.</strong></p>
    </div>
    <div style="border-left:4px solid #3498db; background-color:#ecf6fc; padding:15px; margin:20px 0; border-radius:4px;">
      <p style="margin:0; color:#333333;"><strong>Também dispomos de uma comunidade no WhatsApp exclusiva para interação entre jovens brilhantes, com diversos grupos de interesses específicos. Caso o jovem brilhante não possua celular próprio, poderá utilizar o aparelho de seu responsável. Entretanto, solicitamos que os responsáveis não participem da comunidade, pois a atividade é destinada exclusivamente às crianças. Agradecemos a colaboração. Link para a comunidade Jovens Brilhantes: <a href="{JB_GROUP_LINK}" style="color:#3498db;">{JB_GROUP_LINK}</a></strong></p>
    </div>
    <p style="color:#333333; margin-bottom:0;">Ficamos à disposição para eventuais dúvidas.</p>
    <p style="color:#2c3e50; margin-top:5px;"><strong>Secretaria - Associação Mensa Brasil</strong><br>
    <a href="https://www.mensa.org.br" style="color:#3498db;">www.mensa.org.br</a></p>
  </div>
</body>
</html>
""",
        "BOAS VINDAS RESPJB (DE 10 À 17 ANOS)": """
<html>
<head>
  <meta charset="UTF-8">
  <title>Bem-vindo(a) à Mensa Brasil!</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #ecf0f1; margin:0; padding:20px;">
  <div style="max-width:600px; margin:0 auto; background-color:#ffffff; padding:20px; border-radius:8px;">
    <h2 style="color:#2c3e50; margin-top:0;">Prezado(a) responsável, <span style="color:#3498db;">{GUARDIAN_NAME}</span></h2>
    <p style="color:#333333; line-height:1.5;">A Associação Mensa Brasil tem o grande prazer de dar as boas-vindas aos nossos Jovens Brilhantes. É com orgulho que recebemos seu(sua) filho(a) em nossa comunidade.</p>
    <p style="color:#333333; line-height:1.5;">Saiba que, quanto mais você se envolver com seu(sua) filho(a), mais ele(a) aproveitará as oportunidades oferecidas pela Mensa.</p>
    <p style="text-align:center; font-weight:bold; color:#333333; background-color:#ecf6fc; padding:15px; margin:20px 0; border-radius:4px;">Contamos com o apoio de todos vocês, pais e responsáveis, nesta nova jornada ao lado daqueles que mais amam!</p>
    <div style="border-left:4px solid #3498db; background-color:#ecf6fc; padding:15px; margin:20px 0; border-radius:4px;">
      <p style="margin:0; color:#333333;"><strong>Convite para a comunidade Jovens Brilhantes:</strong><br>
      <a href="{RJB_GROUP_LINK}" style="color:#3498db;">{RJB_GROUP_LINK}</a></p>
    </div>
    {GRUPO_REGIONAL}
    <div style="border-left:4px solid #e74c3c; background-color:#fdecea; padding:15px; margin:20px 0; border-radius:4px;">
      <p style="margin:0; color:#333333;"><strong>Observe que, caso você entre em algum grupo com um número de telefone não cadastrado, será removido automaticamente. Utilize o telefone informado no cadastro.</strong></p>
    </div>
    <div style="border-left:4px solid #27ae60; background-color:#eafaf1; padding:15px; margin:20px 0; border-radius:4px;">
      <p style="margin:0; color:#333333;">Além das comunidades mencionadas, convidamos você a participar do nosso <strong>Grupo de Primeiros Contatos</strong>. Nele, você poderá se apresentar e conhecer voluntários dispostos a ajudar e esclarecer dúvidas. É um espaço ideal para iniciar a jornada na Mensa e conectar-se com outras famílias.<br>
      Link para o grupo: <a href="{RJB_FIRST_CONTACT}" style="color:#3498db;">{RJB_FIRST_CONTACT}</a></p>
    </div>
    <p style="color:#333333; line-height:1.5;">Ficamos à disposição para eventuais dúvidas.</p>
    <p style="color:#333333; margin-bottom:0;">Atenciosamente,</p>
    <p style="color:#2c3e50; margin-top:5px;"><strong>Secretaria - Associação Mensa Brasil</strong><br>
    <a href="https://www.mensa.org.br" style="color:#3498db;">www.mensa.org.br</a></p>
  </div>
</body>
</html>
""",
        "BOAS VINDAS MB": """
<html>
<head>
  <meta charset="UTF-8">
  <title>Seja bem-vindo(a) à Mensa Brasil!</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #ecf0f1; margin:0; padding:20px;">
  <div style="max-width:600px; margin:0 auto; background-color:#ffffff; padding:20px; border-radius:8px;">
    <h1 style="color: #2c3e50; text-align: center; margin-top:0;">Seja bem-vindo(a) à Mensa Brasil!</h1>
    <h2 style="color: #3498db; margin-bottom:20px;">{FULL_NAME}</h2>
    <p style="color:#333333; line-height:1.5;">É com grande satisfação que recebemos você como membro da Mensa Brasil.</p>
    <p style="color:#333333; line-height:1.5;">Seu comprovante de registro foi confirmado e seu número de associado é <strong>{REGISTRATION_ID}</strong>.</p>
    <div style="border-left:4px solid #3498db; background-color:#ecf6fc; padding:15px; margin:20px 0; border-radius:4px;">
      <p style="margin:0; color:#333333;">Seu e-mail institucional é <strong>{EMAIL_INSTITUCIONAL}</strong> e sua senha temporária é <strong>{TEMP_PASSWORD}</strong>. Você pode acessar sua caixa de entrada pelo Gmail.</p>
    </div>
    <p style="color:#333333; line-height:1.5;">Sua carteirinha digital está disponível em nosso aplicativo Mensa Brasil. O manual de uso e os links para download podem ser acessados em:<br>
    <a href="https://mensa.org.br/manual-carteirinhas/" style="color:#3498db;">https://mensa.org.br/manual-carteirinhas/</a></p>
    <div style="border-left:4px solid #3498db; background-color:#ecf6fc; padding:15px; margin:20px 0; border-radius:4px;">
      <p style="margin:0; color:#333333;">Caso tenha interesse em participar dos fóruns de discussão com outros associados, junte-se ao nosso grupo oficial no Facebook:<br>
      <a href="https://www.facebook.com/groups/associacaomensabrasil/" style="color:#3498db;">https://www.facebook.com/groups/associacaomensabrasil/</a></p>
    </div>
    <p style="color:#333333; line-height:1.5;">Recomendamos também que você crie seu cadastro no site da Mensa Internacional (<a href="https://www.mensa.org" style="color:#3498db;">www.mensa.org</a> &gt; Members &gt; Create New Account) para aproveitar todos os benefícios de membro em todo o mundo. A aprovação do seu cadastro internacional é feita pela nossa equipe e pode levar até uma semana.</p>
    <div style="border-left:4px solid #27ae60; background-color:#eafaf1; padding:15px; margin:20px 0; border-radius:4px;">
      <h3 style="margin-top:0; color:#2c3e50;">Comunidades e Grupos</h3>
      <ul style="color:#333333; line-height:1.5;">
        <li>Para acessar grupos de interesse da Mensa, acesse o link:<br>
        <a href="{MB_GROUP_LINK}" style="color:#3498db;">{MB_GROUP_LINK}</a></li>
        <li>{GRUPO_REGIONAL}</li><br>
      </ul>
    </div>
    <div style="border-left:4px solid #e74c3c; background-color:#fdecea; padding:15px; margin:20px 0; border-radius:4px;">
      <p style="margin:0; color:#333333;"><strong>Observe que, caso você entre em algum grupo com um número de telefone não cadastrado, será removido automaticamente. Utilize o telefone informado no cadastro.</strong></p>
    </div>
    <div style="border-left:4px solid #3498db; background-color:#ecf6fc; padding:15px; margin:20px 0; border-radius:4px;">
      <p style="margin:0; color:#333333;">Além das comunidades mencionadas, convidamos você a participar do nosso <strong>Grupo de Primeiros Contatos</strong>. Nele, você poderá se apresentar e conhecer voluntários dispostos a ajudar e esclarecer dúvidas. É um espaço ideal para conectar-se com outros associados.<br>
      Link para o grupo: <a href="{MB_FIRST_CONTACT}" style="color:#3498db;">{MB_FIRST_CONTACT}</a></p>
    </div>
    <p style="color:#333333; line-height:1.5;">Encorajamos você a ler nosso manual do associado:<br>
    <a href="https://drive.google.com/drive/folders/1b-hwQScTLyTXKF44bU0_7MQ1FbIQ69SY" style="color:#3498db;">https://drive.google.com/drive/folders/1b-hwQScTLyTXKF44bU0_7MQ1FbIQ69SY</a></p>
    <p style="color:#333333; line-height:1.5;">Junte-se à nossa nova rede social em:<br>
    <a href="https://lab.mensa.org.br" style="color:#3498db;">https://lab.mensa.org.br</a> (utilize seu e-mail institucional).</p>
    <p style="color:#333333; line-height:1.5;">Qualquer dúvida, estamos à disposição.</p>
    <p style="color:#333333; margin-bottom:0;">Atenciosamente,</p>
    <p style="color:#2c3e50; margin-top:5px;"><strong>Secretaria - Associação Mensa Brasil</strong><br>
    <a href="https://www.mensa.org.br" style="color:#3498db;">www.mensa.org.br</a></p>
  </div>
</body>
</html>
""",
    }

    @classmethod
    def render_welcome_emails_from_pending(
        cls,
        pending_data: PendingRegistrationData,
        registration_id: int,
        mensa_email: str,
        temp_email_password: str,
    ) -> list[dict]:
        """
        Render welcome emails for new members and for their legal representatives if applicable.
        Args:
            pending_data (PendingRegistrationData): The data of the pending registration.
            registration_id (int): The registration ID of the new member.
            mensa_email (str): The Mensa email address for the new member.
            temp_email_password (str): The temporary password for the Mensa email.
        Returns:
            list of tuples: (recipient_email, subject, body)
        """
        today = date.today()
        age = (
            today.year
            - pending_data.birth_date.year
            - (
                (today.month, today.day)
                < (pending_data.birth_date.month, pending_data.birth_date.day)
            )
        )

        emails = []

        if age < 10:
            member_template_key = "BOAS VINDAS JB (DE 2 À 9 ANOS)"
        elif 10 <= age < 18:
            member_template_key = "BOAS VINDAS JB (DE 10 À 17 ANOS)"
        else:
            member_template_key = "BOAS VINDAS MB"

        subject_member = "Seja bem-vindo à Mensa Brasil!"

        template_vars = {
            "FULL_NAME": pending_data.full_name,
            "REGISTRATION_ID": registration_id,
            "AGE": age,
            "EMAIL_INSTITUCIONAL": mensa_email,
            "EMAIL_ADDRESS": mensa_email,
            "TEMP_PASSWORD": temp_email_password,
            "GRUPO_REGIONAL": get_regional_group_string_by_region(
                city=pending_data.address.city,
                state=pending_data.address.state,
            ),
            "MJB_GROUP_LINK": get_whatsapp_groups_settings().wpp_mjb_group_link,
            "JB_GROUP_LINK": get_whatsapp_groups_settings().wpp_jb_group_link,
            "MB_GROUP_LINK": get_whatsapp_groups_settings().wpp_mb_group_link,
            "MB_FIRST_CONTACT": get_whatsapp_groups_settings().wpp_mb_first_contact,
        }

        member_body = cls.TEMPLATES[member_template_key].format(**template_vars)
        emails.append(
            {
                "recipient_email": pending_data.email,
                "subject": subject_member,
                "body": member_body,
            }
        )

        if age < 18 and pending_data.legal_representatives:
            if age < 10:
                guardian_template_key = "BOAS VINDAS RESPJB (DE 2 À 9 ANOS)"
            else:
                guardian_template_key = "BOAS VINDAS RESPJB (DE 10 À 17 ANOS)"

            subject_guardian = "Bem-vindo(a) à Mensa Brasil!"

            for rep in pending_data.legal_representatives:
                guardian_vars = {
                    "GUARDIAN_NAME": rep.name,
                    "GRUPO_REGIONAL": get_regional_group_string_by_region(
                        city=pending_data.address.city,
                        state=pending_data.address.state,
                        is_legal_rep=True,
                    ),
                    "RJB_GROUP_LINK": get_whatsapp_groups_settings().wpp_rjb_group_link,
                    "RJB_FIRST_CONTACT": get_whatsapp_groups_settings().wpp_rjb_first_contact,
                }
                guardian_body = cls.TEMPLATES[guardian_template_key].format(**guardian_vars)
                emails.append(
                    {
                        "recipient_email": rep.email,
                        "subject": subject_guardian,
                        "body": guardian_body,
                    }
                )

        return emails

    @classmethod
    def render_pending_payment_email(
        cls,
        full_name: str,
        complete_payment_url: str,
        admission_type: str,
    ) -> str:
        """Render the email content for pending payments, with customized admission messages."""

        greeting = f"<p style='text-align: center; font-size: 1.2em;'>Prezado(a) {full_name},</p>"

        if admission_type == "test":
            admission_message = (
                "<p>É com satisfação que informamos que seu teste de admissão foi avaliado e que seu desempenho atingiu o percentil mínimo exigido para integrar a Mensa, de acordo com nossos critérios de avaliação.</p>"
                "<p>Esperamos que decida juntar-se a nós e que contribua para construirmos, juntos, uma sociedade ainda mais interessante e forte.</p>"
                "<p>Você poderá consultar o percentil atingido ao acessar seu cadastro de candidato em nosso site.</p>"
            )

        elif admission_type == "report":
            admission_message = (
                "<p>É com satisfação que informamos que seu laudo foi analisado por nossa NSP (Psicóloga Supervisora Nacional) e que seu desempenho atingiu o percentil mínimo exigido para integrar a Mensa, de acordo com nossos critérios de avaliação.</p>"
                "<p>Esperamos que decida juntar-se a nós e que contribua para construirmos, juntos, uma sociedade ainda mais interessante e forte.</p>"
            )

        else:
            raise ValueError("admission_type must be either 'test' or 'report'")

        return f"""
            <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Pagamento Pendente</title>
                </head>
                <body style="font-family: Arial, sans-serif; background-color: #ecf0f1; margin:0; padding:20px;">
                    <div style="max-width:600px; margin:0 auto; background-color:#ffffff; padding:20px; border-radius:8px;">
                        {greeting}
                        {admission_message}
                        <p style="color:#333333; line-height:1.5; margin-top:20px;">Para concluir seu processo de admissão, efetue o pagamento da anuidade por meio do botão abaixo:</p>
                        <p style="text-align:center; margin:20px 0;">
                        <a href="{complete_payment_url}" style="background-color: #3498db; color: #ffffff; padding:12px 20px; text-decoration:none; border-radius:4px; display:inline-block;">Realizar Pagamento</a>
                        </p>
                        <p style="color:#333333; line-height:1.5;">Se o botão acima não funcionar, copie e cole o seguinte link em seu navegador:</p>
                        <p style="word-break:break-word; margin:0;"><a href="{complete_payment_url}" style="color:#3498db;">{complete_payment_url}</a></p>
                        <p style="color:#333333; line-height:1.5; margin-top:20px;">Estamos ansiosos para recebê-lo(a) oficialmente em nossa comunidade de pessoas com alto potencial intelectual.</p>
                        <p style="color:#333333; margin-bottom:0; margin-top:20px;">Atenciosamente,</p>
                        <p style="color:#2c3e50; margin-top:5px;"><strong>Secretaria - Associação Mensa Brasil</strong><br>
                        <a href="https://www.mensa.org.br" style="color:#3498db;">www.mensa.org.br</a></p>
                    </div>
                </body>
            </html>
        """
