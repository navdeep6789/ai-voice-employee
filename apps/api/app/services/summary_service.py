from typing import Optional, Dict, Any, List
from app.models import Lead, Conversation, Booking
from app.schemas.conversation import ConversationSummary


class ConversationSummaryService:
    """
    Derives structured conversation summary from stored database state.
    Prevents hallucinating customer details by using verified system-of-record data.
    """

    @staticmethod
    def generate_summary(
        conversation: Conversation,
        lead: Optional[Lead] = None,
        booking: Optional[Booking] = None
    ) -> ConversationSummary:
        req_list: List[str] = []
        if lead and lead.requirements:
            req_list = [r.strip() for r in lead.requirements.split(",") if r.strip()]

        next_action = "Awaiting discovery follow-up"
        if booking:
            next_action = f"Technical Discovery Call scheduled for {booking.confirmed_start.strftime('%A, %b %d at %I:%M %p')}"
        elif lead and lead.lead_status == "QUALIFIED":
            next_action = "Reach out for solution demo & discovery scheduling"
        elif lead and lead.lead_status == "HANDOFF":
            next_action = "Human solutions engineer handoff in progress"

        return ConversationSummary(
            customer_name=lead.name if lead and lead.name else None,
            company=lead.company if lead and lead.company else None,
            email=lead.email if lead and lead.email else None,
            intent=lead.intent if lead and lead.intent else None,
            use_case=lead.use_case if lead and lead.use_case else None,
            requirements=req_list,
            timeline=lead.timeline if lead and lead.timeline else None,
            budget_range=lead.budget_range if lead and lead.budget_range else None,
            qualification_score=lead.qualification_score if lead else 0,
            lead_status=lead.lead_status if lead else "NEW",
            next_action=next_action,
        )
