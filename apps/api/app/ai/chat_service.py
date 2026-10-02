import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import logger
from app.tools.definitions import TOOL_DECLARATIONS
from app.tools.router import ToolRouter
from app.repositories.conversation_repo import ConversationRepository
from app.schemas.events import AgentEventResponse

settings = get_settings()

PROMPT_FILE = Path(__file__).resolve().parent / "prompts" / "voice_employee.md"


def get_system_instruction() -> str:
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text(encoding="utf-8")
    return "You are Voice AI Assistant, a helpful voice solutions assistant for our engineering team."


class TextAgentService:
    """
    Orchestrates text-based conversational sessions with Gemini API and ToolRouter.
    Ensures complete tool parity with the real-time voice mode.
    """

    def __init__(self, db: AsyncSession, conversation_id: str):
        self.db = db
        self.conversation_id = conversation_id
        self.tool_router = ToolRouter(db, conversation_id=conversation_id)
        self.conv_repo = ConversationRepository(db)
        self.api_key = settings.GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    async def send_message(self, user_text: str, session_id: str, lead_id: Optional[str] = None) -> Dict[str, Any]:
        # 1. Record incoming user message in conversation history
        conv = await self.conv_repo.get_or_create(session_id, lead_id)
        await self.conv_repo.add_message(conv.id, "user", user_text)

        if not self.client or not self.api_key or self.api_key.startswith("your_"):
            # Clean fallback simulation for demo when API key is not yet configured
            simulated_reply = (
                "Hi! I'm your AI Voice Assistant. I can answer questions about our voice agents, "
                "enterprise RAG systems, explain our demo pricing, or book a consultation meeting. "
                "What kind of AI capability are you looking to build?"
            )
            await self.conv_repo.add_message(conv.id, "assistant", simulated_reply)
            return {
                "reply": simulated_reply,
                "session_id": session_id,
                "lead_id": lead_id,
                "events": [],
                "customer_context": None,
                "booking_confirmed": None,
            }

        # Format past messages for context
        history_msgs = []
        for m in conv.messages[-10:]:
            role = "user" if m.speaker == "user" else "model"
            history_msgs.append(types.Content(role=role, parts=[types.Part.from_text(text=m.text)]))

        # Convert tool declarations to types.Tool
        tools = [types.Tool(function_declarations=[
            types.FunctionDeclaration(
                name=decl["name"],
                description=decl["description"],
                parameters=decl.get("parameters")
            ) for decl in TOOL_DECLARATIONS
        ])]

        system_instruction = get_system_instruction()
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=tools,
            temperature=0.3,
            max_output_tokens=600,
        )

        turns = 0
        max_turns = settings.MAX_TOOL_CALLS_PER_TURN
        booking_confirmed = None
        assistant_reply = ""

        # Main agent tool loop
        while turns < max_turns:
            turns += 1
            response = await self.client.aio.models.generate_content(
                model=settings.GEMINI_TEXT_MODEL,
                contents=history_msgs,
                config=config,
            )

            # Check if model wants to call functions
            function_calls = response.function_calls
            if not function_calls:
                assistant_reply = response.text or ""
                break

            # Execute tool calls
            for call in function_calls:
                tool_name = call.name
                tool_args = dict(call.args) if call.args else {}

                tool_res = await self.tool_router.execute_tool(tool_name, tool_args)
                if tool_name == "book_meeting" and tool_res.get("ok"):
                    booking_confirmed = tool_res.get("data")

                # Add model call and tool response to history
                history_msgs.append(response.candidates[0].content)
                history_msgs.append(types.Content(
                    role="user",
                    parts=[types.Part.from_function_response(
                        name=tool_name,
                        response={"result": tool_res}
                    )]
                ))

        if not assistant_reply and turns >= max_turns:
            assistant_reply = "I processed your request using our internal tools. How else can I assist with your AI requirements?"

        # Persist assistant reply
        await self.conv_repo.add_message(conv.id, "assistant", assistant_reply)

        # Fetch recent events for UI stream
        events = await self.conv_repo.get_events(conv.id, limit=20)
        event_responses = [AgentEventResponse.model_validate(e) for e in events]

        return {
            "reply": assistant_reply,
            "session_id": session_id,
            "lead_id": lead_id,
            "events": event_responses,
            "customer_context": None,
            "booking_confirmed": booking_confirmed,
        }
