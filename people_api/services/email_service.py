# mypy: ignore-errors

"""Service for managing members email addresses."""

from datetime import date
from enum import StrEnum

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from people_api.database.models.pending_registration import PendingRegistrationData
from people_api.schemas import UserToken

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

    SAO_PAULO_CITY = "https://chat.whatsapp.com/Jir03Oo0E8m1GnzXhcIh0o"
    SAO_PAULO_STATE = "https://chat.whatsapp.com/GUHNMiUXuHuAtLs6jtcI8L"
    SOUTHEAST = "https://chat.whatsapp.com/F3MzLhwft221gM2e82czio"
    SOUTH = "https://chat.whatsapp.com/DUWxEniPVobE1wqaTYWl10"
    CENTER_WEST_NORTH = "https://chat.whatsapp.com/IWt7FD1A7qBCfxUwxFwHuQ"
    NORTHEAST = "https://chat.whatsapp.com/BdoH0WM1WkY8pqqxd3GaAB"


class LegalRepsRegionalGroupsEnum(StrEnum):
    """Regional WhatsApp groups for legal reps of underage Mensa Brazil members."""

    SAO_PAULO_CITY = "https://chat.whatsapp.com/GJ3U8NnB1CKBQjZMJCJg2O"
    SAO_PAULO_STATE = "https://chat.whatsapp.com/GttEefRh2THJNrXbLrJMAM"
    SOUTHEAST = "https://chat.whatsapp.com/Hp8dvuZd5CVCx5w51xRmUK"
    SOUTH = "https://chat.whatsapp.com/EqV6LwBz5nDKSUNpFJsoB7"
    CENTER_WEST_NORTH = "https://chat.whatsapp.com/Gi5twi4EGT456iDp09rAPW"
    NORTHEAST = "https://chat.whatsapp.com/KshsYYKYl4q1Bud7uAmFY6"


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
    <li>Para saber notícias e convites oficiais da associação, você também pode entrar no grupo de avisos do WhatsApp através deste link:<br>
        <a href={0}>{0}</a></li>
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
<body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
    <h1 style="color: #2c3e50; text-align: center;">SEJA BEM-VINDO À MENSA BRASIL!!!</h1>
    <h2 style="color: #3498db;">{FULL_NAME}</h2>
    <p>É uma honra recebê-lo(a) como novo(a) associado(a) da Mensa. Pessoas com um QI top 2% são raras. Foi um desafio encontrá-lo(a) e agora podemos nos orgulhar de fazer parte da mesma família.</p>
    <p>Seu número de cadastro é <strong>{REGISTRATION_ID}</strong> e você é agora um dos mais de 2000 mensans de todo o Brasil é um dos mais de 100 mil mensans de todo o mundo. Quando você compartilha sua inteligência com os demais membros, traz um pouco da sua individualidade e da sua paixão à nossa organização. Dentre nossos membros temos uma diversidade de pessoas geniais. Você conhecerá a partir de agora um grande grupo de pessoas interessadas em tantos temas, desde palcontologia até futurologia, de hieróglifos a literatura, de Triathlon a genealogia. Esperamos que você traga seu valor único a esta organização e que se depare com o valor igualmente único que os demais membros trazem para cá.</p>
    <p>Falando em valor, saiba que quanto mais você se envolver mais aproveitará a sua condição de membro. Algo genuinamente especial ocorre quando damos a sorte de encontrar membros com os quais criamos ligações de afeto e amizade. E é nesses momentos que enxergamos o valor de sermos tão diferentes e ainda assim tão próximos. Sentimos que tais ligações nos fazem sentir mais que amigos. Somos uma família.</p>
    <p>Como você tem <strong>{AGE} anos</strong>, entrará no nosso programa Jovens Brilhantes e já pode se registrar no site da Mensa Internacional: <a href="https://www.mensa.org">www.mensa.org</a> > member > create new account. A aprovação da sua conta lá pode levar até uma semana.</p>
    <div style="background-color: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; margin: 20px 0;">
        <p>Seu e-mail institucional é <strong>"{EMAIL_INSTITUCIONAL}"</strong> e sua senha temporária é: <strong>"{TEMP_PASSWORD}"</strong>. Você pode acessar sua caixa de entrada pelo Gmail.</p>
    </div>
    <p>Sua carteirinha digital pode ser baixada pelo nosso app (<strong>"MENSA BRASIL"</strong>), através de login com seu e-mail institucional.</p>
    <p style="background-color: #ffe6e6; padding: 10px; border-left: 4px solid #e74c3c;"><strong>Note que, caso você entre com um telefone não cadastrado nos grupos, será removido automaticamente. Use o telefone fornecido no cadastro.</strong></p>
    <p style="background-color: #e8f4fd; padding: 10px; border-left: 4px solid #3498db;"><strong>Também temos uma comunidade no WhatsApp exclusiva para interação entre jovens brilhantes, com diversos grupos de interesses específicos. Lembrando que se o JB, não tiver celular, vai poder interagir com o celular do pai/mãe. Porém, pedimos aos pais que não participem da comunidade, pois está é uma atividade somente para as crianças, agradecemos a colaboração. Link comunidade jovens brilhantes: <a href="https://chat.whatsapp.com/Ce7ELjd0EqqJO0r6ZBYm1d">https://chat.whatsapp.com/Ce7ELjd0EqqJO0r6ZBYm1d</a></strong></p>
    <p>Me coloco à disposição para eventuais dúvidas.</p>
    <p>Atenciosamente,</p>
    <p style="color: #2c3e50;">
        <strong>Marili Silva Oliveira Cruz</strong><br>
        Secretaria - Associação Mensa Brasil<br>
        <a href="https://www.mensa.org.br">www.mensa.org.br</a>
    </p>
</body>
</html>
""",
        "BOAS VINDAS RESPJB (DE 2 À 9 ANOS)": """
<html>
<body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
    <h2 style="color: #2c3e50;">Caro responsável, <span style="color: #3498db;">{GUARDIAN_NAME}</span></h2>
    <p>A Associação Mensa Brasil tem o grande prazer em receber como novos membros os nossos queridos Jovens Brilhantes e agora podemos nos orgulhar de ter o seu filho(a) fazendo parte da família MENSA BRASIL.</p>
    <p>Saibam que quanto mais você se envolver junto ao seu filho mais ele aproveitará a condição de membro.</p>
    <p style="text-align: center; font-weight: bold; background-color: #f8f9fa; padding: 15px; margin: 20px 0;">CONTAMOS COM O APOIO DE TODOS VOCÊS, PAIS E RESPONSÁVEIS, NESTA NOVA JORNADA JUNTO COM AQUELES QUE VOCÊS MAIS AMAM!</p>
    <div style="background-color: #e8f4fd; padding: 15px; margin: 20px 0; border-radius: 5px;">
        <p><strong>Convite para Comunidade dos Jovens Brilhantes:</strong><br>
        <a href="https://chat.whatsapp.com/G8Nzpw5qCuJ9dwOG97hVXE">https://chat.whatsapp.com/G8Nzpw5qCuJ9dwOG97hVXE</a></p>
    </div>
    {GRUPO_REGIONAL}
    <p style="background-color: #ffe6e6; padding: 10px; border-left: 4px solid #e74c3c;">Note que, caso você entre com um telefone não cadastrado nos grupos, será removido automaticamente. Use o telefone fornecido no cadastro.</p>
    <div style="background-color: #f1f8e9; padding: 15px; border-left: 4px solid #7cb342; margin: 20px 0;">
        <p>Além dos grupos e interações descritos, gostaríamos de convidá-lo(a) a participar do nosso <strong>Grupo de Primeiros Contatos</strong>. Nele, você terá a oportunidade de se apresentar e conhecer voluntários que estão dispostos a ajudar e esclarecer qualquer dúvida. É um ótimo espaço para iniciar sua jornada na Mensa e se conectar com outros responsáveis.</p>
        <p>Segue o link para o grupo: <a href="https://chat.whatsapp.com/ICaS4rQSiFbJRzoADPBpQ8">https://chat.whatsapp.com/ICaS4rQSiFbJRzoADPBpQ8</a></p>
    </div>
    <p>Me coloco à disposição para eventuais dúvidas.</p>
    <p>Atenciosamente,</p>
    <p style="color: #2c3e50;">
        <strong>Marili Silva Oliveira Cruz</strong><br>
        Secretaria - Associação Mensa Brasil<br>
        <a href="https://www.mensa.org.br">www.mensa.org.br</a>
    </p>
</body>
</html>
""",
        "BOAS VINDAS JB (DE 10 À 17 ANOS)": """
<html>
<body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
    <h1 style="color: #2c3e50; text-align: center;">SEJA BEM-VINDO À MENSA BRASIL!!!</h1>
    <h2 style="color: #3498db;">{FULL_NAME}</h2>
    <p>É uma honra recebê-lo(a) como novo(a) associado(a) da Mensa. Pessoas com um QI top 2% são raras. Foi um desafio encontrá-lo(a) e agora podemos nos orgulhar de fazer parte da mesma família.</p>
    <p>Seu número de cadastro é <strong>{REGISTRATION_ID}</strong> e você é agora um dos mais de 2000 mensans de todo o Brasil é um dos mais de 100 mil mensans de todo o mundo. Quando você compartilha sua inteligência com os demais membros, traz um pouco da sua individualidade e da sua paixão à nossa organização. Dentre nossos membros temos uma diversidade de pessoas geniais. Você conhecerá a partir de agora um grande grupo de pessoas interessadas em tantos temas, desde palcontologia até futurologia, de hieróglifos a literatura, de Triathlon a genealogia. Esperamos que você traga seu valor único a esta organização e que se depare com o valor igualmente único que os demais membros trazem para cá.</p>
    <p>Falando em valor, saiba que quanto mais você se envolver mais aproveitará a sua condição de membro. Algo genuinamente especial ocorre quando damos a sorte de encontrar membros com os quais criamos ligações de afeto e amizade. E é nesses momentos que enxergamos o valor de sermos tão diferentes e ainda assim tão próximos. Sentimos que tais ligações nos fazem sentir mais que amigos. Somos uma família.</p>
    <p>Como você tem <strong>{AGE} anos</strong>, entrará no nosso programa Jovens Brilhantes e já pode se registrar no site da Mensa Internacional: <a href="https://www.mensa.org">www.mensa.org</a> > member > create new account. A aprovação da sua conta lá pode levar até uma semana.</p>
    <div style="background-color: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; margin: 20px 0;">
        <p>Seu e-mail institucional é <strong>"{EMAIL_INSTITUCIONAL}"</strong> e sua senha temporária é: <strong>"{TEMP_PASSWORD}"</strong>. Você pode acessar sua caixa de entrada pelo Gmail.</p>
    </div>
    <p>Sua carteirinha digital pode ser baixada pelo nosso app (<strong>"MENSA BRASIL"</strong>), através de login com seu e-mail institucional.</p>
    <p style="background-color: #ffe6e6; padding: 10px; border-left: 4px solid #e74c3c;"><strong>Note que, caso você entre com um telefone não cadastrado nos grupos, será removido automaticamente. Use o telefone fornecido no cadastro.</strong></p>
    <p style="background-color: #e8f4fd; padding: 10px; border-left: 4px solid #3498db;"><strong>Também temos uma comunidade no WhatsApp exclusiva para interação entre jovens brilhantes, com diversos grupos de interesses específicos. Lembrando que se o JB, não tiver celular, vai poder interagir com o celular do pai/mãe. Porém, pedimos aos pais que não participem da comunidade, pois está é uma atividade somente para as crianças, agradecemos a colaboração. Link comunidade jovens brilhantes: <a href="https://chat.whatsapp.com/LRNITWVAy4Y2RAgJJ4tgbx">https://chat.whatsapp.com/LRNITWVAy4Y2RAgJJ4tgbx</a></strong></p>
    <p>Me coloco à disposição para eventuais dúvidas.</p>
    <p>Atenciosamente,</p>
    <p style="color: #2c3e50;">
        <strong>Marili Silva Oliveira Cruz</strong><br>
        Secretaria - Associação Mensa Brasil<br>
        <a href="https://www.mensa.org.br">www.mensa.org.br</a>
    </p>
</body>
</html>
""",
        "BOAS VINDAS RESPJB (DE 10 À 17 ANOS)": """
<html>
<body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
    <h2 style="color: #2c3e50;">Caro responsável, <span style="color: #3498db;">{GUARDIAN_NAME}</span></h2>
    <p>A Associação Mensa Brasil tem o grande prazer em receber como novos membros os nossos queridos Jovens Brilhantes e agora podemos nos orgulhar de ter o seu filho(a) fazendo parte da família MENSA BRASIL.</p>
    <p>Saibam que quanto mais você se envolver junto ao seu filho mais ele aproveitará a condição de membro.</p>
    <p style="text-align: center; font-weight: bold; background-color: #f8f9fa; padding: 15px; margin: 20px 0;">CONTAMOS COM O APOIO DE TODOS VOCÊS, PAIS E RESPONSÁVEIS, NESTA NOVA JORNADA JUNTO COM AQUELES QUE VOCÊS MAIS AMAM!</p>
    <div style="background-color: #e8f4fd; padding: 15px; margin: 20px 0; border-radius: 5px;">
        <p><strong>Convite para Comunidade dos Jovens Brilhantes:</strong><br>
        <a href="https://chat.whatsapp.com/G8Nzpw5qCuJ9dwOG97hVXE">https://chat.whatsapp.com/G8Nzpw5qCuJ9dwOG97hVXE</a></p>
    </div>
    {GRUPO_REGIONAL}
    <p style="background-color: #ffe6e6; padding: 10px; border-left: 4px solid #e74c3c;">Note que, caso você entre com um telefone não cadastrado nos grupos, será removido automaticamente. Use o telefone fornecido no cadastro.</p>
    <div style="background-color: #f1f8e9; padding: 15px; border-left: 4px solid #7cb342; margin: 20px 0;">
        <p>Além dos grupos e interações descritos, gostaríamos de convidá-lo(a) a participar do nosso <strong>Grupo de Primeiros Contatos</strong>. Nele, você terá a oportunidade de se apresentar e conhecer voluntários que estão dispostos a ajudar e esclarecer qualquer dúvida. É um ótimo espaço para iniciar sua jornada na Mensa e se conectar com outros responsáveis.</p>
        <p>Link para o grupo: <a href="https://chat.whatsapp.com/ICaS4rQSiFbJRzoADPBpQ8">https://chat.whatsapp.com/ICaS4rQSiFbJRzoADPBpQ8</a></p>
    </div>
    <p>Me coloco à disposição para eventuais dúvidas.</p>
    <p>Atenciosamente,</p>
    <p style="color: #2c3e50;">
        <strong>Marili Silva Oliveira Cruz</strong><br>
        Secretaria - Associação Mensa Brasil<br>
        <a href="https://www.mensa.org.br">www.mensa.org.br</a>
    </p>
</body>
</html>
""",
        "BOAS VINDAS MB": """
<html>
<body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
    <h1 style="color: #2c3e50; text-align: center;">SEJA BEM-VINDO À MENSA BRASIL</h1>
    <h2 style="color: #3498db;">{FULL_NAME}</h2>
    <p>Seja bem-vindo(a) à Mensa Brasil! Estamos muito contentes em ter você no nosso grupo!</p>
    <p>Seu comprovante foi recebido e seu número de cadastro é <strong>{REGISTRATION_ID}</strong>.</p>
    <div style="background-color: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; margin: 20px 0;">
        <p>Seu e-mail institucional é <strong>"{EMAIL_INSTITUCIONAL}"</strong> e sua senha temporária é: <strong>"{TEMP_PASSWORD}"</strong>. Você pode acessar sua caixa de entrada através do Gmail.</p>
    </div>
    <p>Sua carteirinha digital pode ser baixada pelo nosso app, através de login com seu e-mail institucional. O manual de uso do app e os links de download podem ser acessados em:<br>
    <a href="https://mensa.org.br/manual-carteirinhas/">https://mensa.org.br/manual-carteirinhas/</a></p>
    <div style="background-color: #e8f4fd; padding: 15px; margin: 20px 0; border-radius: 5px;">
        <p>Caso tenha interesse em participar dos fóruns de discussão com os demais membros, segue nosso grupo oficial no Facebook:<br>
        <a href="https://www.facebook.com/groups/associacaomensabrasil/">https://www.facebook.com/groups/associacaomensabrasil/</a></p>
    </div>
    <p>Sugerimos também que crie o seu cadastro no site da Mensa Internacional (<a href="https://www.mensa.org">www.mensa.org</a> > members > create new account) para que possa aproveitar todos os benefícios de membro pelo mundo inteiro. A aprovação do seu cadastro na Mensa Internacional é feita por nós e pode levar até uma semana.</p>
    <div style="background-color: #f1f8e9; padding: 15px; border-left: 4px solid #7cb342; margin: 20px 0;">
        <h3 style="margin-top: 0;">Comunidades e Grupos</h3>
        <ul>
            <li>Para acessar a comunidade dos grupos de interesse da Mensa, comece pelo link:<br>
            <a href="https://chat.whatsapp.com/FreTAvDcMJ7IXZ8sSFlJR8">https://chat.whatsapp.com/FreTAvDcMJ7IXZ8sSFlJR8</a></li>
            <li>Temos um grupo de WhatsApp que agrega os participantes da sua região. Para entrar, acesse:<br>
            <a href="https://chat.whatsapp.com/BYTRtDQ814X0uAllO78xlw">https://chat.whatsapp.com/BYTRtDQ814X0uAllO78xlw</a></li>
            {GRUPO_REGIONAL}
        </ul>
    </div>
    <p style="background-color: #ffe6e6; padding: 10px; border-left: 4px solid #e74c3c;">Note que, caso você entre com um telefone não cadastrado nos grupos, será removido automaticamente. Use o telefone fornecido no cadastro.</p>
    <div style="background-color: #e8f4fd; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0;">
        <p>Além dos grupos e interações descritos, gostaríamos de convidá-lo(a) a participar do nosso <strong>Grupo de Primeiros Contatos</strong>. Nele, você terá a oportunidade de se apresentar e conhecer voluntários que estão dispostos a ajudar e esclarecer qualquer dúvida. É um ótimo espaço para iniciar sua jornada na Mensa e se conectar com outros membros.</p>
        <p>Link para o grupo: <a href="https://chat.whatsapp.com/BgHJfBC80wZ29f7E3j0he6">https://chat.whatsapp.com/BgHJfBC80wZ29f7E3j0he6</a></p>
    </div>
    <p>Encorajamos você a ler o nosso manual do associado:<br>
    <a href="https://drive.google.com/drive/folders/1b-hwQScTLyTXKF44bU0_7MQ1FbIQ69SY">https://drive.google.com/drive/folders/1b-hwQScTLyTXKF44bU0_7MQ1FbIQ69SY</a></p>
    <p>Junte-se a nossa nova rede social em:<br>
    <a href="https://lab.mensa.org.br">https://lab.mensa.org.br</a> (utilize seu e-mail institucional).</p>
    <p>Qualquer dúvida, me coloco à disposição!</p>
    <p>Atenciosamente,</p>
    <p style="color: #2c3e50;">
        <strong>Marili Silva Oliveira Cruz</strong><br>
        Secretaria - Associação Mensa Brasil<br>
        <a href="https://www.mensa.org.br">www.mensa.org.br</a>
    </p>
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

        greeting = f"<p style='text-align: center; font-size: 1.2em;'>Olá {full_name},</p>"

        if admission_type == "test":
            admission_message = (
                "<p>Temos a satisfação de informar que o seu teste de admissão foi corrigido e seu desempenho "
                "atingiu o percentil necessário para fazer parte da Mensa, segundo nosso instrumento de avaliação.</p>"
                "<p>Esperamos que você se decida por juntar-se a nós e contribua para construirmos juntos uma sociedade ainda mais interessante e forte.</p>"
                "<p>Você poderá consultar o percentil atingido acessando seu cadastro de candidato em nosso website.</p>"
            )

        elif admission_type == "report":
            admission_message = (
                "<p>Temos a satisfação de informar que o seu laudo foi analisado por nossa NSP (Psicóloga Supervisora Nacional) e seu desempenho "
                "atingiu o percentil necessário para fazer parte da Mensa, segundo nossos critérios de avaliação.</p>"
                "<p>Esperamos que você se decida por juntar-se a nós e contribua para construirmos juntos uma sociedade ainda mais interessante e forte.</p>"
            )

        else:
            raise ValueError("admission_type must be either 'test' or 'report'")

        return f"""
            <div style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto; text-align: justify;">
                {greeting}

                {admission_message}

                <p>Para concluir seu processo de admissão, basta realizar o pagamento da sua associação utilizando o botão abaixo:</p>

                <p style="text-align: center;">
                    <a href="{complete_payment_url}" style="background-color: #0066cc; color: white; padding: 12px 20px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        Realizar Pagamento
                    </a>
                </p>

                <p>Se o botão acima não funcionar, copie e cole o seguinte link em seu navegador:</p>
                <p style="word-break: break-word;"><a href="{complete_payment_url}">{complete_payment_url}</a></p>

                <p>Estamos ansiosos para recebê-lo(a) oficialmente em nossa comunidade de pessoas com alto potencial intelectual.</p>

                <p>Atenciosamente,</p>
                <p style="color: #2c3e50;">
                    <strong>Marili Silva Oliveira Cruz</strong><br>
                    Secretaria - Associação Mensa Brasil<br>
                    <a href="https://www.mensa.org.br">www.mensa.org.br</a>
                </p>
            </div>
        """
