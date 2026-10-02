import asyncio
import json
from typing import Optional, Callable, Dict, Any, Awaitable
from google import genai
from google.genai import types
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import logger
from app.tools.definitions import TOOL_DECLARATIONS
from app.tools.router import ToolRouter
from app.ai.chat_service import get_system_instruction

settings = get_settings()


class GeminiLiveSession:
    """
    Manages a live bidirectional streaming audio session between
    a client WebSocket and the Google Gemini Live API.
    """

    def __init__(
        self,
        db: AsyncSession,
        conversation_id: str,
        on_audio_chunk: Callable[[bytes], Awaitable[None]],
        on_text_event: Callable[[str, str], Awaitable[None]],
        on_activity_event: Callable[[Dict[str, Any]], Awaitable[None]],
    ):
        self.db = db
        self.conversation_id = conversation_id
        self.on_audio_chunk = on_audio_chunk
        self.on_text_event = on_text_event
        self.on_activity_event = on_activity_event
        self.tool_router = ToolRouter(db, conversation_id=conversation_id)

        self.api_key = settings.GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.live_session = None
        self._is_running = False
        self._receive_task: Optional[asyncio.Task] = None

    async def start(self):
        """Initializes and connects the live session."""
        if not self.client or not self.api_key or self.api_key.startswith("your_"):
            logger.warning("Gemini Live session initialized without active API key.")
            await self.on_text_event("assistant", "Connected in demo mode. (Configure GEMINI_API_KEY for live voice model)")
            return

        # Prepare tools declaration
        tools = [types.Tool(function_declarations=[
            types.FunctionDeclaration(
                name=decl["name"],
                description=decl["description"],
                parameters=decl.get("parameters")
            ) for decl in TOOL_DECLARATIONS
        ])]

        system_instruction = get_system_instruction()
        config = types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            system_instruction=types.Content(parts=[types.Part.from_text(text=system_instruction)]),
            tools=tools,
        )

        try:
            logger.info("Connecting to Gemini Live API WebSocket...")
            self.live_session = await self.client.aio.live.connect(
                model=settings.GEMINI_LIVE_MODEL,
                config=config,
            ).__aenter__()

            self._is_running = True
            self._receive_task = asyncio.create_task(self._listen_loop())
            logger.info("Gemini Live API connection established.")
        except Exception as e:
            logger.error(f"Failed to connect to Gemini Live: {e}", exc_info=True)
            self._is_running = False
            raise

    async def send_audio(self, pcm_bytes: bytes):
        """Forwards incoming PCM 16kHz mono audio chunk from browser to Gemini Live."""
        if not self.live_session or not self._is_running:
            return

        try:
            blob = types.Blob(data=pcm_bytes, mime_type="audio/pcm;rate=16000")
            await self.live_session.send_realtime_input(media_chunks=[blob])
        except Exception as e:
            logger.error(f"Error sending audio chunk to Gemini Live: {e}")

    async def _listen_loop(self):
        """Continuously receives streaming events, audio, and tool calls from Gemini Live."""
        try:
            async for response in self.live_session.receive():
                if not self._is_running:
                    break

                # 1. Handle Tool Calls
                if response.tool_call:
                    for call in response.tool_call.function_calls:
                        tool_name = call.name
                        tool_args = dict(call.args) if call.args else {}
                        logger.info(f"Gemini Live requested tool call: {tool_name}")

                        await self.on_activity_event({
                            "type": "tool_started",
                            "tool": tool_name,
                            "args": tool_args
                        })

                        # Execute tool via ToolRouter
                        tool_res = await self.tool_router.execute_tool(tool_name, tool_args)

                        await self.on_activity_event({
                            "type": "tool_completed",
                            "tool": tool_name,
                            "result": tool_res
                        })

                        # Return tool response to Gemini Live
                        function_responses = [
                            types.FunctionResponse(
                                name=call.name,
                                id=call.id,
                                response={"result": tool_res}
                            )
                        ]
                        await self.live_session.send_tool_response(function_responses=function_responses)

                # 2. Handle Server Content (Spoken Audio & Text Transcripts)
                if response.server_content:
                    model_turn = response.server_content.model_turn
                    if model_turn:
                        for part in model_turn.parts:
                            # Forward PCM audio frame to client
                            if part.inline_data and part.inline_data.data:
                                await self.on_audio_chunk(part.inline_data.data)

                            # Forward text transcript snippet if provided
                            if part.text:
                                await self.on_text_event("assistant", part.text)

                    # Interruption detection
                    if response.server_content.interrupted:
                        logger.info("Gemini Live interrupted by user speech.")
                        await self.on_activity_event({"type": "interrupted"})

        except asyncio.CancelledError:
            logger.info("Gemini Live listen loop cancelled.")
        except Exception as e:
            logger.error(f"Exception in Gemini Live receive loop: {e}", exc_info=True)
            await self.on_activity_event({
                "type": "error",
                "message": f"Gemini Live session error: {str(e)}"
            })
        finally:
            self._is_running = False

    async def close(self):
        """Gracefully closes the Live API session and cancels listeners."""
        self._is_running = False
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass

        if self.live_session:
            try:
                await self.live_session.__aexit__(None, None, None)
            except Exception as e:
                logger.error(f"Error during Gemini Live session cleanup: {e}")
            finally:
                self.live_session = None
        logger.info("Gemini Live session closed.")
