"""This module contains the tool calls (functions) for the WhatsApp chatbot."""

import json
import logging
from enum import StrEnum

from openai.types.beta.threads.run import Run
from openai.types.beta.threads.run_submit_tool_outputs_params import ToolOutput

from people_api.services.whatsapp_service.chatbot.openai_service import openai_client

from .wpp_client_helpers import (
    add_member_legal_reps,
    create_email_request,
    delete_member_legal_reps,
    get_all_whatsapp_groups,
    get_member_addresses_request,
    get_member_legal_reps,
    get_pending_whatsapp_group_join_requests,
    recover_email_password_request,
    request_whatsapp_group_join,
    update_address_request,
    update_member_legal_reps,
)


class FunctionCall(StrEnum):
    """Enum for function calls used in the WhatsApp chatbot."""

    CREATE_EMAIL = "create_email"
    RECOVER_EMAIL_PASSWORD = "recover_email_password"
    GET_MEMBER_ADDRESSES = "get_member_addresses"
    UPDATE_ADDRESS = "update_member_address"
    GET_MEMBER_LEGAL_REPS = "get_member_legal_representatives"
    ADD_MEMBER_LEGAL_REPS = "add_member_legal_representatives"
    UPDATE_MEMBER_LEGAL_REPS = "update_member_legal_representatives"
    DELETE_MEMBER_LEGAL_REPS = "delete_member_legal_representatives"
    GET_ALL_WHATSAPP_GROUPS = "get_all_whatsapp_groups"
    REQUEST_WHATSAPP_GROUP_JOIN = "request_whatsapp_group_join"
    GET_PENDING_WHATSAPP_GROUP_JOIN_REQUESTS = "get_pending_whatsapp_group_join_requests"


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
                        "[CHATBOT-MENSA] Tool call detected: %s with arguments: %s",
                        tool_call.function.name,
                        tool_call.function.arguments,
                    )
                    call_responses[f"{tool_call.id}"] = await create_email_request(
                        registration_id=registration_id
                    )
                if tool_call.function.name == FunctionCall.RECOVER_EMAIL_PASSWORD:
                    logging.info(
                        "[CHATBOT-MENSA] Tool call detected: %s with arguments: %s",
                        tool_call.function.name,
                        tool_call.function.arguments,
                    )
                    call_responses[f"{tool_call.id}"] = await recover_email_password_request(
                        registration_id=registration_id
                    )
                if tool_call.function.name == FunctionCall.GET_MEMBER_ADDRESSES:
                    logging.info(
                        "[CHATBOT-MENSA] Tool call detected: %s with arguments: %s",
                        tool_call.function.name,
                        tool_call.function.arguments,
                    )
                    call_responses[f"{tool_call.id}"] = await get_member_addresses_request(
                        registration_id=registration_id
                    )
                if tool_call.function.name == FunctionCall.UPDATE_ADDRESS:
                    logging.info(
                        "[CHATBOT-MENSA] Tool call detected: %s with arguments: %s",
                        tool_call.function.name,
                        tool_call.function.arguments,
                    )
                    args = json.loads(tool_call.function.arguments)
                    address_id = args.get("address_id")
                    updated_address = args.get("updated_address", {})
                    call_responses[f"{tool_call.id}"] = await update_address_request(
                        registration_id=registration_id,
                        address=updated_address,
                        address_id=address_id,
                    )
                if tool_call.function.name == FunctionCall.GET_MEMBER_LEGAL_REPS:
                    logging.info(
                        "[CHATBOT-MENSA] Tool call detected: %s with arguments: %s",
                        tool_call.function.name,
                        tool_call.function.arguments,
                    )
                    call_responses[f"{tool_call.id}"] = await get_member_legal_reps(
                        registration_id=registration_id
                    )
                if tool_call.function.name == FunctionCall.ADD_MEMBER_LEGAL_REPS:
                    logging.info(
                        "[CHATBOT-MENSA] Tool call detected: %s with arguments: %s",
                        tool_call.function.name,
                        tool_call.function.arguments,
                    )
                    args = json.loads(tool_call.function.arguments)
                    legal_representative = args.get("legal_representative", {})
                    call_responses[f"{tool_call.id}"] = await add_member_legal_reps(
                        registration_id=registration_id,
                        legal_representative=legal_representative,
                    )
                if tool_call.function.name == FunctionCall.UPDATE_MEMBER_LEGAL_REPS:
                    logging.info(
                        "[CHATBOT-MENSA] Tool call detected: %s with arguments: %s",
                        tool_call.function.name,
                        tool_call.function.arguments,
                    )
                    args = json.loads(tool_call.function.arguments)
                    legal_representative_id = args.get("legal_representative_id")
                    legal_representative = args.get("legal_representative", {})
                    call_responses[f"{tool_call.id}"] = await update_member_legal_reps(
                        registration_id=registration_id,
                        legal_representative_id=legal_representative_id,
                        legal_representative=legal_representative,
                    )
                if tool_call.function.name == FunctionCall.DELETE_MEMBER_LEGAL_REPS:
                    logging.info(
                        "[CHATBOT-MENSA] Tool call detected: %s with arguments: %s",
                        tool_call.function.name,
                        tool_call.function.arguments,
                    )
                    args = json.loads(tool_call.function.arguments)
                    legal_representative_id = args.get("legal_representative_id")
                    call_responses[f"{tool_call.id}"] = await delete_member_legal_reps(
                        registration_id=registration_id,
                        legal_representative_id=legal_representative_id,
                    )
                if tool_call.function.name == FunctionCall.GET_ALL_WHATSAPP_GROUPS:
                    logging.info(
                        "[CHATBOT-MENSA] Tool call detected: %s with arguments: %s",
                        tool_call.function.name,
                        tool_call.function.arguments,
                    )
                    call_responses[f"{tool_call.id}"] = await get_all_whatsapp_groups(
                        registration_id=registration_id
                    )
                if tool_call.function.name == FunctionCall.REQUEST_WHATSAPP_GROUP_JOIN:
                    logging.info(
                        "[CHATBOT-MENSA] Tool call detected: %s with arguments: %s",
                        tool_call.function.name,
                        tool_call.function.arguments,
                    )
                    args = json.loads(tool_call.function.arguments)
                    group_id = args.get("group_id")
                    call_responses[f"{tool_call.id}"] = await request_whatsapp_group_join(
                        registration_id=registration_id,
                        group_id=group_id,
                    )
                if tool_call.function.name == FunctionCall.GET_PENDING_WHATSAPP_GROUP_JOIN_REQUESTS:
                    logging.info(
                        "[CHATBOT-MENSA] Tool call detected: %s with arguments: %s",
                        tool_call.function.name,
                        tool_call.function.arguments,
                    )
                    call_responses[
                        f"{tool_call.id}"
                    ] = await get_pending_whatsapp_group_join_requests(
                        registration_id=registration_id
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

        return run
