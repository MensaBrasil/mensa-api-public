"""Handle incoming WhatsApp messages and forward them to the assistant."""

import logging

from ....settings import get_settings
from .openai_service import openai_client
from .tool_calls_handler import ToolCallService


class MessageHandler:
    """Service for handling incoming messages from WhatsApp and sending them to the OpenAI chatbot."""

    @staticmethod
    async def process_message(thread_id: str, message: str, registration_id: int) -> str:
        """Handle incoming WhatsApp messages and forward them to the assistant."""

        logging.info("[CHATBOT-MENSA] Processing message: %s", message)
        try:
            await openai_client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message,
            )

            logging.info("[CHATBOT-MENSA] Message sent to assistant. Waiting for response...")
            run = await openai_client.beta.threads.runs.create_and_poll(
                thread_id=thread_id,
                assistant_id=get_settings().chatgpt_assistant_id,
                tools=[{"type": "file_search"}],
                tool_choice="required",
            )

            logging.info(run.model_dump_json(indent=2))
            logging.info("[CHATBOT-MENSA] Assistant response received. Checking status...")
            while run.status == "requires_action" and run.required_action:
                logging.info("[CHATBOT-MENSA] Tool call detected... Handling tool calls...")
                run = await ToolCallService.handle_tool_calls(run, registration_id)

            if run.status == "completed":
                logging.info("[CHATBOT-MENSA] Assistant response completed.")
                messages_response = await openai_client.beta.threads.messages.list(
                    thread_id=thread_id
                )
                last_message = next(
                    msg for msg in messages_response.data if msg.role == "assistant"
                )
                if hasattr(last_message.content[0], "text") and hasattr(
                    last_message.content[0].text, "value"
                ):
                    last_response = last_message.content[0].text.value

                    return last_response

            logging.error("[CHATBOT-MENSA] No valid response from the assistant.")
            raise ValueError("No valid response from the assistant.")

        except Exception as e:
            logging.error("[CHATBOT-MENSA] Error processing message: %s", e)
            return "Erro ao processar mensagem, tente novamente mais tarde..."
