"""This module contains the tool calls (functions) for the WhatsApp chatbot."""

import json
import logging
from enum import StrEnum

from openai.types.beta.threads.run import Run
from openai.types.beta.threads.run_submit_tool_outputs_params import ToolOutput

from people_api.services.whatsapp_service.chatbot.openai_service import openai_client

from .wpp_client_helpers import (
    create_email_request,
    get_member_addresses_request,
    recover_email_password_request,
    update_address_request,
)


class FunctionCall(StrEnum):
    """Enum for function calls used in the WhatsApp chatbot."""

    CREATE_EMAIL = "create_email"
    RECOVER_EMAIL_PASSWORD = "recover_email_password"
    GET_MEMBER_ADDRESSES = "get_member_addresses"
    UPDATE_ADDRESS = "update_member_address"


class ToolCallService:
    """
    This class handles the tool calls for the WhatsApp chatbot.
    """

    @staticmethod
    async def handle_tool_calls(run: Run, registration_id: int) -> Run:
        """
        Handle the tool call response from the assistant.
        This function will be called when the assistant requires action.
        """

        call_responses: dict = {}

        if (
            run.required_action is not None
            and getattr(run.required_action, "submit_tool_outputs", None) is not None
        ):
            tool_calls = run.required_action.submit_tool_outputs.tool_calls

            for tool_call in tool_calls:
                if tool_call.function.name == FunctionCall.CREATE_EMAIL:
                    logging.info(
                        f"Tool call detected: {tool_call.function.name} with arguments: {tool_call.function.arguments}"
                    )
                    call_responses[f"{tool_call.id}"] = create_email_request(
                        registration_id=registration_id
                    )
                if tool_call.function.name == FunctionCall.RECOVER_EMAIL_PASSWORD:
                    logging.info(
                        f"Tool call detected: {tool_call.function.name} with arguments: {tool_call.function.arguments}"
                    )
                    call_responses[f"{tool_call.id}"] = recover_email_password_request(
                        registration_id=registration_id
                    )
                if tool_call.function.name == FunctionCall.GET_MEMBER_ADDRESSES:
                    logging.info(
                        f"Tool call detected: {tool_call.function.name} with arguments: {tool_call.function.arguments}"
                    )
                    call_responses[f"{tool_call.id}"] = get_member_addresses_request(
                        registration_id=registration_id
                    )
                if tool_call.function.name == FunctionCall.UPDATE_ADDRESS:
                    logging.info(
                        f"Tool call detected: {tool_call.function.name} with arguments: {tool_call.function.arguments}"
                    )
                    args = json.loads(tool_call.function.arguments)
                    address_id = args.get("address_id")
                    updated_address = args.get("updated_address", {})
                    call_responses[f"{tool_call.id}"] = update_address_request(
                        registration_id=registration_id,
                        address=updated_address,
                        address_id=address_id,
                    )

            tool_outputs = [
                ToolOutput(
                    tool_call_id=str(tool_call_id),
                    output=json.dumps(output),
                )
                for tool_call_id, output in call_responses.items()
            ]

            logging.info("Submitting tool outputs to assistant: %s", tool_outputs)
            run = await openai_client.beta.threads.runs.submit_tool_outputs(
                thread_id=run.thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs,
            )

        return run
