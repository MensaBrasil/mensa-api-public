"""Thread handler for managing threads and messages."""

import logging
from datetime import datetime

from fastapi import HTTPException

from .openai_service import openai_client
from .wpp_client_helpers import get_member_info_by_phone_number


class ThreadService:
    """Service for managing threads and messages."""

    threads_by_phone: dict[str, str] = {}
    message_counts: dict[str, dict[str, int]] = {}
    thread_timestamps: dict[str, list[datetime]] = {}

    @staticmethod
    def check_message_length(message: str):
        """Ensure the message does not exceed 150 characters."""
        if len(message) > 150:
            raise ValueError(
                "O limite máximo de 150 caracteres por mensagem foi ultrapassado. Por favor, digite uma mensagem mais curta."
            )

    @staticmethod
    def check_thread_creation_limit(phone_number: str):
        """Ensure a user does not start more than 5 threads per day."""
        today = datetime.now().date()
        timestamps = ThreadService.thread_timestamps.get(phone_number, [])
        threads_today = [ts for ts in timestamps if ts.date() == today]
        if len(threads_today) >= 5:
            raise ValueError(
                "O limite máximo de sessões por dia foi ultrapassado. Por favor, tente novamente amanhã."
            )

    @staticmethod
    def record_message(phone_number: str, thread_id: str, message: str):
        """Record a message after checking the message length."""
        ThreadService.check_message_length(message)
        if phone_number not in ThreadService.message_counts:
            ThreadService.message_counts[phone_number] = {}
        if thread_id not in ThreadService.message_counts[phone_number]:
            ThreadService.message_counts[phone_number][thread_id] = 0
        ThreadService.message_counts[phone_number][thread_id] += 1

    @staticmethod
    async def get_or_create_thread(phone_number: str, session) -> str:
        """
        Retrieve an existing thread if it hasn't reached 15 messages;
        otherwise, create a new thread if within the daily limit.
        """

        logging.info(
            "[CHATBOT-MENSA] Retrieving or creating thread for phone number: %s", phone_number
        )
        existing_thread_id = ThreadService.threads_by_phone.get(phone_number)
        if existing_thread_id:
            count = ThreadService.message_counts.get(phone_number, {}).get(existing_thread_id, 0)
            if count < 15:
                return existing_thread_id
            try:
                ThreadService.check_thread_creation_limit(phone_number)
            except ValueError as e:
                raise HTTPException(status_code=429, detail=str(e)) from e

        thread = await openai_client.beta.threads.create()
        thread_id = thread.id
        ThreadService.threads_by_phone[phone_number] = thread_id
        if phone_number not in ThreadService.thread_timestamps:
            ThreadService.thread_timestamps[phone_number] = []
        ThreadService.thread_timestamps[phone_number].append(datetime.now())
        if phone_number not in ThreadService.message_counts:
            ThreadService.message_counts[phone_number] = {}
        ThreadService.message_counts[phone_number][thread_id] = 0

        user_details = await get_member_info_by_phone_number(phone_number, session)

        if user_details:
            system_message = (
                f"Dados do usuário:\n"
                f"- Nome: {user_details.name}\n"
                f"- MB / Nº Registro: {user_details.registration_id}\n"
                f"- Data de Nascimento: {user_details.birth_date}\n"
                f"- Email Mensa: {user_details.email_mensa}\n"
                f"- Data de Expiração da Anuidade: {user_details.expiration_date}\n\n"
                "Todas as respostas devem levar em conta esse contexto. "
                "Sempre consulte os documentos de apoio para elaborar suas respostas. "
                "Se não encontrar informações, responda que não há informações em nossos materiais internos."
                "Nunca mencione a fonte dos documentos."
            )
        else:
            system_message = (
                "Usuário não encontrado. Continuando sem contexto do usuário. "
                "Sempre consulte os documentos de apoio para elaborar suas respostas. "
                "Se não encontrar informações, responda que não há informações em nossos materiais internos."
                "Nunca mencione a fonte dos documentos. "
            )

        await openai_client.beta.threads.messages.create(
            thread_id=thread_id,
            role="assistant",
            content=system_message,
        )
        return thread_id
