import time
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.crm_service import CRMService
from app.services.calendar_service import CalendarService
from app.services.pricing_service import PricingService
from app.rag.service import RAGService
from app.repositories.conversation_repo import ConversationRepository
from app.schemas.lead import LeadCreate, LeadUpdate
from app.schemas.calendar import BookingCreate
from app.schemas.events import AgentEventCreate
from app.core.logging import logger


class ToolRouter:
    """
    Central dispatcher for model tool calls.
    Validates arguments, invokes business services, records telemetry, and emits agent events.
    """

    def __init__(self, db: AsyncSession, conversation_id: Optional[str] = None):
        self.db = db
        self.conversation_id = conversation_id
        self.crm_service = CRMService(db)
        self.calendar_service = CalendarService(db)
        self.pricing_service = PricingService()
        self.rag_service = RAGService(db)
        self.conv_repo = ConversationRepository(db)

    async def execute_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.perf_counter()
        logger.info(f"Executing tool '{name}' with args: {args}", extra={"tool": name, "session_id": self.conversation_id})

        # Record tool_started event in database
        start_event = None
        if self.conversation_id:
            try:
                start_event = await self.conv_repo.add_event(AgentEventCreate(
                    conversation_id=self.conversation_id,
                    event_type="tool_started",
                    tool_name=name,
                    status="running",
                    payload={"args": args}
                ))
            except Exception as e:
                logger.error(f"Failed to record start event: {e}")

        try:
            result = await self._dispatch(name, args)
            duration_ms = int((time.perf_counter() - start_time) * 1000)

            # Record tool_completed event
            if self.conversation_id:
                try:
                    await self.conv_repo.add_event(AgentEventCreate(
                        conversation_id=self.conversation_id,
                        event_type="tool_completed",
                        tool_name=name,
                        status="success",
                        duration_ms=duration_ms,
                        payload={"result": result}
                    ))
                except Exception as e:
                    logger.error(f"Failed to record complete event: {e}")

            return {
                "ok": True,
                "data": result,
                "error": None,
                "duration_ms": duration_ms
            }

        except Exception as exc:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            logger.error(f"Tool execution failed for '{name}': {exc}", exc_info=True)

            if self.conversation_id:
                try:
                    await self.conv_repo.add_event(AgentEventCreate(
                        conversation_id=self.conversation_id,
                        event_type="tool_failed",
                        tool_name=name,
                        status="failed",
                        duration_ms=duration_ms,
                        payload={"error": str(exc)}
                    ))
                except Exception as e:
                    logger.error(f"Failed to record fail event: {e}")

            return {
                "ok": False,
                "data": None,
                "error": {
                    "code": "TOOL_EXECUTION_ERROR",
                    "message": f"Tool '{name}' encountered an error: {str(exc)}"
                },
                "duration_ms": duration_ms
            }

    async def _dispatch(self, name: str, args: Dict[str, Any]) -> Any:
        if name == "search_knowledge":
            query = args.get("query", "")
            res = await self.rag_service.search(query=query, top_k=3)
            return {
                "success": res.success,
                "query": query,
                "citations": [
                    {
                        "document_id": r.document_id,
                        "title": r.document_title,
                        "category": r.category,
                        "snippet": r.content[:300] + "..." if len(r.content) > 300 else r.content,
                        "score": r.similarity_score
                    }
                    for r in res.results
                ],
                "context_summary": self.rag_service.build_context(res.results)
            }

        elif name == "check_pricing":
            service_name = args.get("service_name", "")
            return self.pricing_service.get_service_pricing(service_name)

        elif name == "check_calendar":
            slots = await self.calendar_service.list_available_slots()
            formatted_slots = [
                {
                    "slot_id": s.id,
                    "date": s.start_time.strftime("%A, %B %d, %Y"),
                    "time": s.start_time.strftime("%I:%M %p"),
                    "start_iso": s.start_time.isoformat(),
                    "end_iso": s.end_time.isoformat(),
                }
                for s in slots[:6]  # Return next 6 upcoming slots
            ]
            return {
                "success": True,
                "available_slots": formatted_slots,
                "total_available": len(slots),
                "booking_rule": "Inform the caller of these exact slots and obtain explicit confirmation before booking."
            }

        elif name == "book_meeting":
            slot_id = args.get("slot_id")
            name_val = args.get("name")
            email_val = args.get("email")
            company_val = args.get("company")
            lead_id_val = args.get("lead_id")
            meeting_type = args.get("meeting_type", "AI Solutions Consultation")

            if not slot_id or not name_val or not email_val:
                raise ValueError("slot_id, name, and email are mandatory for booking a meeting.")

            booking_req = BookingCreate(
                slot_id=slot_id,
                lead_id=lead_id_val,
                name=name_val,
                email=email_val,
                company=company_val,
                meeting_type=meeting_type
            )
            result = await self.calendar_service.book_meeting(booking_req)
            if not result.get("ok"):
                raise ValueError(result.get("error", {}).get("message", "Slot is no longer available."))
            return result["data"]

        elif name == "create_lead":
            lead_in = LeadCreate(**args)
            lead_res = await self.crm_service.create_lead(lead_in)
            return lead_res.model_dump()

        elif name == "update_lead":
            lead_id = args.get("lead_id")
            if not lead_id:
                raise ValueError("lead_id is required to update a lead.")
            update_data = {k: v for k, v in args.items() if k != "lead_id"}
            lead_update = LeadUpdate(**update_data)
            lead_res = await self.crm_service.update_lead(lead_id, lead_update)
            if not lead_res:
                raise ValueError(f"Lead with id '{lead_id}' not found.")
            return lead_res.model_dump()

        elif name == "calculate_lead_qualification":
            lead_id = args.get("lead_id")
            if not lead_id:
                raise ValueError("lead_id is required.")
            res = await self.crm_service.get_qualification(lead_id)
            if not res:
                raise ValueError(f"Lead with id '{lead_id}' not found.")
            return res.model_dump()

        elif name == "transfer_to_human":
            reason = args.get("reason", "User requested human agent")
            priority = args.get("priority", "standard")
            lead_id = args.get("lead_id")
            if lead_id:
                await self.crm_service.update_lead(lead_id, LeadUpdate(lead_status="HANDOFF"))
            return {
                "success": True,
                "handoff_ticket": {
                    "reason": reason,
                    "priority": priority,
                    "status": "QUEUED_FOR_HUMAN_ENGINEER",
                    "notice": "A human solutions engineer has been alerted."
                }
            }

        else:
            raise NotImplementedError(f"Tool '{name}' is not recognized.")
