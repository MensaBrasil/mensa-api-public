"""Service for updating WhatsApp-related data for members and their representatives."""

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from people_api.services.twilio_service import TwilioService

from ....database.models.whatsapp import ReceivedWhatsappMessage
from .message_handler import MessageHandler
from .thread_handler import ThreadService

# from .tool_calls_handler import ToolCallService


class WhatsappChatBot:
    """Service for handling incoming messages from WhatsApp and sending them to the OpenAI chatbot."""

    error_notifications: dict[str, str] = {}

    @staticmethod
    async def chatbot_message(
        message: ReceivedWhatsappMessage, session: AsyncSession, registration_id: int
    ) -> str:
        """Handle incoming WhatsApp messages and forward them to the assistant."""

        message_text = message.Body
        phone_number = message.WaId

        try:
            if message_text.strip() == "!reset":
                thread_key = str(phone_number)
                if thread_key in ThreadService.threads_by_phone:
                    del ThreadService.threads_by_phone[thread_key]
                await TwilioService().send_whatsapp_message(
                    to_=phone_number, message="Thread reset successfully!"
                )
                return "Thread reset successfully!"
        except Exception as e:
            print(f"Error processing reset command: {e}")
            await TwilioService().send_whatsapp_message(
                to_=phone_number,
                message="Erro ao processar o comando de reset. Por favor, tente novamente.",
            )
            return "Error reseting thread."

        try:
            thread_id = await ThreadService.get_or_create_thread(
                phone_number=phone_number, session=session
            )
            ThreadService.record_message(str(phone_number), thread_id, message_text)
            if str(phone_number) in WhatsappChatBot.error_notifications:
                del WhatsappChatBot.error_notifications[str(phone_number)]
        except ValueError as e:
            error_msg = str(e)
            if str(phone_number) not in WhatsappChatBot.error_notifications:
                WhatsappChatBot.error_notifications[str(phone_number)] = error_msg
                await TwilioService().send_whatsapp_message(
                    to_=phone_number,
                    message="Algo deu errado ao processar sua mensagem. Por favor, tente novamente mais tarde.",
                )
            return error_msg
        except HTTPException as e:
            error_msg = e.detail
            if str(phone_number) not in WhatsappChatBot.error_notifications:
                WhatsappChatBot.error_notifications[str(phone_number)] = error_msg
                await TwilioService().send_whatsapp_message(
                    to_=phone_number,
                    message="Algo deu errado ao processar sua mensagem. Por favor, tente novamente mais tarde.",
                )
            return error_msg

        try:
            assistant_response = await MessageHandler.process_message(
                thread_id=thread_id,
                message=message_text,
                registration_id=registration_id,
            )

            await TwilioService().send_whatsapp_message(
                to_=phone_number,
                message=assistant_response,
            )
        except Exception as e:
            error_msg = str(e)
            if str(phone_number) not in WhatsappChatBot.error_notifications:
                WhatsappChatBot.error_notifications[str(phone_number)] = error_msg
                await TwilioService().send_whatsapp_message(
                    to_=phone_number,
                    message="Erro ao processar mensagem, tente novamente mais tarde...",
                )
            return error_msg

        return assistant_response
