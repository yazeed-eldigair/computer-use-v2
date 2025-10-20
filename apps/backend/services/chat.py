import json
import logging
import platform
import uuid
from datetime import datetime
from typing import Any, List, cast

from anthropic import Anthropic
from anthropic.types.beta import (
    BetaContentBlockParam,
    BetaImageBlockParam,
    BetaMessage,
    BetaMessageParam,
    BetaTextBlock,
    BetaTextBlockParam,
    BetaToolResultBlockParam,
    BetaToolUseBlockParam,
)
from fastapi import HTTPException
from models.base import Message
from services.session import SessionService
from services.ws import ws_manager
from utils.database import execute_query

from .tools import TOOL_GROUPS_BY_VERSION, ToolCollection, ToolResult

logger = logging.getLogger(__name__)


class ChatService:
    """Service for interacting with Claude API and managing messages."""

    client: Anthropic

    MAX_ITERATIONS = 10
    ANTHROPIC_MODEL = "claude-3-7-sonnet-20250219"
    MAX_TOKENS = 1024
    SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
    * You are utilising an Ubuntu virtual machine using {platform.machine()} architecture with internet access.
    * You can feel free to install Ubuntu applications with your bash tool. Use curl instead of wget.
    * Note, firefox-esr is what is installed on your system. Use that to open
      Firefox. Firefox should be your default browser.
    * Using bash tool you can start GUI applications, but you need to set export DISPLAY=:1 and use a subshell. For example "(DISPLAY=:1 xterm &)". GUI apps run with bash tool will appear within your desktop environment, but they may take some time to appear.
    * When using your bash tool with commands that are expected to output very large quantities of text, redirect into a tmp file and use str_replace_editor or `grep -n -B <lines before> -A <lines after> <query> <filename>` to confirm output.
    * When viewing a page it can be helpful to zoom out so that you can see everything on the page.  Either that, or make sure you scroll down to see everything before deciding something isn't available.
    * When using your computer function calls, they take a while to run and send
      back to you.  Where possible/feasible, try to chain multiple of these
      calls all into one function calls request.
    * When opening a file in LibreOffice Calc, make sure you close the 'Tip of the Day' dialog if it appears after opening the file.
    * The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
    * You do not need to take any screenshots.
    </SYSTEM_CAPABILITY>

    <IMPORTANT>
    * When using Firefox, if a startup wizard appears, IGNORE IT.  Do not even click "skip this step".  Instead, click on the address bar where it says "Search or enter address", and enter the appropriate search term or URL there.
    </IMPORTANT>"""

    tool_group = TOOL_GROUPS_BY_VERSION["computer_use_20250124"]
    tool_collection = ToolCollection(
        *(ToolCls() for ToolCls in tool_group.tools)
    )
    system = BetaTextBlockParam(
        type="text",
        text=f"{SYSTEM_PROMPT}",
    )

    def __init__(self) -> None:
        """Initialize the Claude service."""
        from config import settings

        if not settings.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is not set"
            )

        self.client = Anthropic(
            api_key=settings.ANTHROPIC_API_KEY, max_retries=4
        )

    async def create_message(
        self,
        session_id: str,
        userMessage: str,
    ) -> Message:
        try:
            # Save user message to database - for user messages, convert to content block array
            user_content = [{"type": "text", "text": userMessage}]
            SessionService.save_message(
                session_id=session_id,
                role="user",
                content=user_content,
                message=userMessage,
            )

            iterations = 0
            while True and iterations < self.MAX_ITERATIONS:
                iterations += 1
                # Get all messages for this session
                messages = SessionService.get_session_messages(session_id)

                # Convert to Anthropic format
                anthropic_messages: list[BetaMessageParam] = [
                    {"role": msg.role, "content": msg.content}
                    for msg in messages
                ]
                raw_response = (
                    self.client.beta.messages.with_raw_response.create(
                        model=self.ANTHROPIC_MODEL,
                        max_tokens=self.MAX_TOKENS,
                        system=self.SYSTEM_PROMPT,
                        tools=self.tool_collection.to_params(),
                        messages=anthropic_messages,
                        betas=["computer-use-2025-01-24"],
                    )
                )

                response = raw_response.parse()
                response_params = self._response_to_params(response)

                # Save assistant response to database
                SessionService.save_message(
                    session_id=session_id,
                    role="assistant",
                    content=response_params,
                )

                tool_result_contents: list[BetaToolResultBlockParam] = []
                for content_block in response_params:
                    await self._handle_output(
                        session_id,
                        content_block,
                    )

                    if content_block["type"] == "tool_use":
                        result = await self.tool_collection.run(
                            name=content_block["name"],
                            tool_input=cast(
                                dict[str, Any], content_block["input"]
                            ),
                        )
                        tool_result_content = self._make_api_tool_result(
                            result, content_block["id"]
                        )
                        await self._handle_output(
                            session_id, tool_result_content
                        )
                        tool_result_contents.append(tool_result_content)

                if not tool_result_contents:
                    break

                # Save tool results as user message
                SessionService.save_message(
                    session_id=session_id,
                    role="user",
                    content=tool_result_contents,
                )

            # Broadcast end of assistant response
            await ws_manager.broadcast_to_session(
                session_id,
                {
                    "type": "assistant_response",
                    "action": "end",
                    "data": None,
                },
            )

            return

        except Exception as e:
            error_msg = f"Unexpected error processing message for session {session_id}: {str(e)}"
            logger.exception(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)

    async def _broadcast_to_session(
        self, msg_id: str, session_id: str, message: str
    ) -> None:
        # Notify via WebSocket
        await ws_manager.broadcast_to_session(
            session_id,
            {
                "type": "assistant_response",
                "action": "message",
                "data": {
                    "id": msg_id,
                    "session_id": session_id,
                    "role": "assistant",
                    "content": message,
                    "created_at": datetime.utcnow().isoformat(),
                },
            },
        )

    async def get_session_messages(self, session_id: str) -> List[Message]:
        """Get all messages for a session in chronological order.

        Args:
            session_id: The ID of the session

        Returns:
            List[Message]: List of messages, empty list if no messages exist
        """
        results = execute_query(
            """
            SELECT id, session_id, role, content, created_at
            FROM messages
            WHERE session_id = ?
            ORDER BY created_at ASC
            """,
            (session_id,),
        )

        messages = []
        for row in results:
            try:
                content = json.loads(row["content"])
                messages.append(
                    Message(
                        id=row["id"],
                        session_id=row["session_id"],
                        role=row["role"],
                        content=content,
                        created_at=row["created_at"],
                    )
                )
            except json.JSONDecodeError:
                logger.error(f"Failed to parse content for message {row['id']}")
                continue

        return messages

    async def _handle_output(
        self,
        session_id: str,
        content: BetaContentBlockParam | ToolResult,
    ) -> None:
        message = self._get_message(content)
        assistant_msg_id = str(uuid.uuid4())
        # Only broadcast if we have a non-empty message
        if message and len(message.strip()) > 0:
            await self._broadcast_to_session(
                assistant_msg_id,
                session_id,
                message,
            )

    def _get_message(
        self,
        content: BetaContentBlockParam | ToolResult,
    ) -> str | None:
        """Extract human-readable message from content block.

        Args:
            content: Content block from Claude or tool result

        Returns:
            str: Human-readable message to display, or None if no message
        """
        if isinstance(content, dict):
            if content["type"] == "text":
                return content["text"]
            elif content["type"] == "thinking":
                thinking_content = content.get("thinking", "")
                return f"[Thinking]\n\n{thinking_content}"
            elif content["type"] == "tool_use":
                return f'Tool Use: {content["name"]}\nInput: {content["input"]}'
        return None

    def _response_to_params(
        self,
        response: BetaMessage,
    ) -> list[BetaContentBlockParam]:
        res: list[BetaContentBlockParam] = []
        for block in response.content:
            if isinstance(block, BetaTextBlock):
                if block.text:
                    res.append(BetaTextBlockParam(type="text", text=block.text))
                elif getattr(block, "type", None) == "thinking":
                    # Handle thinking blocks - include signature field
                    thinking_block = {
                        "type": "thinking",
                        "thinking": getattr(block, "thinking", None),
                    }
                    if hasattr(block, "signature"):
                        thinking_block["signature"] = getattr(
                            block, "signature", None
                        )
                    res.append(cast(BetaContentBlockParam, thinking_block))
            else:
                # Handle tool use blocks normally
                res.append(cast(BetaToolUseBlockParam, block.model_dump()))
        return res

    def _make_api_tool_result(
        self, result: ToolResult, tool_use_id: str
    ) -> BetaToolResultBlockParam:
        """Convert an agent ToolResult to an API ToolResultBlockParam."""
        tool_result_content: (
            list[BetaTextBlockParam | BetaImageBlockParam] | str
        ) = []
        is_error = False
        if result.error:
            is_error = True
            tool_result_content = self._maybe_prepend_system_tool_result(
                result, result.error
            )
        else:
            if result.output:
                tool_result_content.append(
                    {
                        "type": "text",
                        "text": self._maybe_prepend_system_tool_result(
                            result, result.output
                        ),
                    }
                )
            if result.base64_image:
                tool_result_content.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": result.base64_image,
                        },
                    }
                )
        return BetaToolResultBlockParam(
            type="tool_result",
            content=tool_result_content,
            tool_use_id=tool_use_id,
            is_error=is_error,
        )

    def _maybe_prepend_system_tool_result(
        self, result: ToolResult, result_text: str
    ):
        if result.system:
            result_text = f"<system>{result.system}</system>\n{result_text}"
        return result_text


# Global Chat service instance
chat_service = ChatService()
