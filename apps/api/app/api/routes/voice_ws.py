import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.lead_repo import LeadRepository
from app.services.crm_service import CRMService
from app.services.summary_service import ConversationSummaryService
from app.voice.gemini_live import GeminiLiveSession
from app.core.constants import VoiceState
from app.core.logging import logger

router = APIRouter(tags=["Voice WebSocket"])


@router.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = websocket.query_params.get("session_id", "default-session")
    lead_id = websocket.query_params.get("lead_id")

    logger.info(f"WebSocket client connected with session_id: {session_id}")

    db: AsyncSession = AsyncSessionLocal()
    conv_repo = ConversationRepository(db)
    conv = await conv_repo.get_or_create(session_id, lead_id)

    async def emit_json(payload: dict):
        try:
            await websocket.send_text(json.dumps(payload))
        except Exception:
            pass

    async def on_audio_chunk(pcm_bytes: bytes):
        try:
            # Send binary PCM audio frame directly to client speakers
            await websocket.send_bytes(pcm_bytes)
            await emit_json({"type": "state_changed", "state": VoiceState.SPEAKING.value})
        except Exception as e:
            logger.error(f"Error forwarding audio chunk to client: {e}")

    async def on_text_event(speaker: str, text: str):
        try:
            await conv_repo.add_message(conv.id, speaker, text)
            await emit_json({
                "type": "transcript",
                "speaker": speaker,
                "text": text
            })
        except Exception as e:
            logger.error(f"Error persisting/emitting transcript: {e}")

    async def on_activity_event(event_data: dict):
        try:
            await emit_json({
                "type": "agent_event",
                "event": event_data
            })
            # Check if event was a lead/meeting update and stream fresh customer context
            if event_data.get("type") == "tool_completed" and event_data.get("tool") in ["create_lead", "update_lead", "book_meeting", "calculate_lead_qualification"]:
                if conv.lead_id:
                    crm = CRMService(db)
                    lead = await crm.get_lead(conv.lead_id)
                    qual = await crm.get_qualification(conv.lead_id)
                    if lead:
                        await emit_json({
                            "type": "customer_context_updated",
                            "customer": {
                                "id": lead.id,
                                "name": lead.name,
                                "email": lead.email,
                                "company": lead.company,
                                "role": lead.role,
                                "intent": lead.intent,
                                "use_case": lead.use_case,
                                "requirements": lead.requirements,
                                "timeline": lead.timeline,
                                "budget_range": lead.budget_range,
                                "qualification_score": lead.qualification_score,
                                "lead_status": lead.lead_status,
                                "qualification_details": qual.model_dump() if qual else None
                            }
                        })
        except Exception as e:
            logger.error(f"Error handling activity event: {e}")

    # Initialize Gemini Live Session
    live_session = GeminiLiveSession(
        db=db,
        conversation_id=conv.id,
        on_audio_chunk=on_audio_chunk,
        on_text_event=on_text_event,
        on_activity_event=on_activity_event,
    )

    try:
        await emit_json({"type": "state_changed", "state": VoiceState.CONNECTING.value})
        await live_session.start()
        await emit_json({"type": "state_changed", "state": VoiceState.LISTENING.value})

        # Main client receiving loop
        while True:
            message = await websocket.receive()
            if "bytes" in message and message["bytes"]:
                # Binary audio chunk from microphone
                pcm_data = message["bytes"]
                await live_session.send_audio(pcm_data)

            elif "text" in message and message["text"]:
                try:
                    data = json.loads(message["text"])
                    msg_type = data.get("type")

                    if msg_type == "interrupt":
                        # Client detected speech while assistant was speaking
                        await emit_json({"type": "state_changed", "state": VoiceState.LISTENING.value})

                    elif msg_type == "end":
                        # End conversation and produce summary
                        lead_repo = LeadRepository(db)
                        lead = await lead_repo.get_by_id(conv.lead_id) if conv.lead_id else None
                        summary = ConversationSummaryService.generate_summary(conv, lead)
                        await conv_repo.update_summary(conv.id, summary.model_dump(), status="COMPLETED")
                        await emit_json({
                            "type": "summary",
                            "summary": summary.model_dump()
                        })
                        await emit_json({"type": "state_changed", "state": VoiceState.ENDED.value})
                        break

                except json.JSONDecodeError:
                    pass

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket unexpected error: {e}", exc_info=True)
        await emit_json({"type": "state_changed", "state": VoiceState.ERROR.value, "error": str(e)})
    finally:
        await live_session.close()
        await db.close()
