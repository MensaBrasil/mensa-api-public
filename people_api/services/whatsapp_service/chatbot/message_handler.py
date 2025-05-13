"""Handle incoming WhatsApp messages and forward them to the assistant."""

import asyncio
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
            runs_response = await openai_client.beta.threads.runs.list(thread_id=thread_id)
            active_runs = [
                r
                for r in runs_response.data
                if r.status not in ("completed", "failed", "cancelled", "expired")
            ]
            if active_runs:
                logging.info(
                    "[CHATBOT-MENSA] Waiting for active runs to complete before adding new message..."
                )
                timeout = 240
                elapsed = 0
                while active_runs and elapsed < timeout:
                    await asyncio.sleep(1)
                    elapsed += 1
                    runs_response = await openai_client.beta.threads.runs.list(thread_id=thread_id)
                    active_runs = [
                        r
                        for r in runs_response.data
                        if r.status not in ("completed", "failed", "cancelled", "expired")
                    ]
                if active_runs:
                    raise TimeoutError("Previous run did not complete in time.")

            await openai_client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message,
            )

            logging.info("[CHATBOT-MENSA] Message sent to assistant. Waiting for response...")
            run = await openai_client.beta.threads.runs.create_and_poll(
                thread_id=thread_id,
                assistant_id=get_settings().chatgpt_assistant_id,
            )

            logging.info(
                "[CHATBOT-MENSA] Assistant response received. Initial status: %s", run.status
            )

            timeout = 240
            elapsed = 0

            while (
                run.status not in ("completed", "failed", "cancelled", "expired")
                and elapsed < timeout
            ):
                if run.status == "queued":
                    logging.info("[CHATBOT-MENSA] Assistant run is queued. Waiting to start...")
                elif run.status == "in_progress":
                    logging.info("[CHATBOT-MENSA] Assistant run is in progress...")
                elif run.status == "requires_action" and run.required_action:
                    logging.info("[CHATBOT-MENSA] Tool call detected... Handling tool calls...")
                    run = await ToolCallService.handle_tool_calls(run, registration_id)
                else:
                    logging.info("[CHATBOT-MENSA] Assistant run status: %s", run.status)

                if run.status not in ("completed", "failed", "cancelled", "expired"):
                    await asyncio.sleep(1)
                    elapsed += 1
                    run = await openai_client.beta.threads.runs.retrieve(
                        thread_id=thread_id, run_id=run.id
                    )

            if run.status == "completed":
                logging.info("[CHATBOT-MENSA] Assistant response completed.")
                messages_response = await openai_client.beta.threads.messages.list(
                    thread_id=thread_id
                )
                assistant_messages = [
                    msg for msg in messages_response.data if msg.role == "assistant"
                ]
                if not assistant_messages:
                    logging.error("[CHATBOT-MENSA] No assistant messages found after completion.")
                    raise ValueError("No valid response from the assistant.")

                assistant_messages.sort(key=lambda msg: msg.created_at)

                latest_timestamp = assistant_messages[-1].created_at
                latest_messages = [
                    msg for msg in assistant_messages if msg.created_at == latest_timestamp
                ]
                responses = []
                for msg in latest_messages:
                    if hasattr(msg.content[0], "text") and hasattr(msg.content[0].text, "value"):
                        responses.append(msg.content[0].text.value)
                return "\n".join(responses)

            if run.status in ("failed", "cancelled", "expired"):
                logging.error("[CHATBOT-MENSA] Assistant run ended with status: %s", run.status)
                raise ValueError(f"Assistant run ended with status: {run.status}")

            logging.error("[CHATBOT-MENSA] Assistant run did not complete in time.")
            raise TimeoutError("Assistant run did not complete in time.")

        except Exception as e:
            logging.error("[CHATBOT-MENSA] Error processing message: %s", e)
            return "Erro ao processar mensagem, tente novamente mais tarde..."
