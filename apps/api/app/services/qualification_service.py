from typing import Dict, Any, List
from app.models import Lead
from app.schemas.lead import LeadQualificationResult
from app.core.constants import LEAD_SCORING_WEIGHTS, LeadStatus


class LeadQualificationService:
    """
    Deterministic, transparent scoring engine for inbound lead qualification.
    Ensures mathematical consistency without model hallucination.
    """

    @staticmethod
    def evaluate(lead: Lead) -> LeadQualificationResult:
        score = 0
        reasons: List[str] = []
        missing_fields: List[str] = []

        # 1. Use Case (+20)
        if lead.use_case and len(lead.use_case.strip()) > 5:
            score += LEAD_SCORING_WEIGHTS["use_case_identified"]
            reasons.append("Clear business use case identified")
        else:
            missing_fields.append("Specific use case / project scope")

        # 2. Timeline (+15)
        if lead.timeline and lead.timeline.strip().lower() not in ["unknown", "none", "not provided"]:
            score += LEAD_SCORING_WEIGHTS["timeline_identified"]
            reasons.append(f"Target timeline established ({lead.timeline})")
        else:
            missing_fields.append("Target project timeline")

        # 3. Budget (+15)
        if lead.budget_range and lead.budget_range.strip().lower() not in ["unknown", "none", "not provided"]:
            score += LEAD_SCORING_WEIGHTS["budget_identified"]
            reasons.append("Budget parameters communicated")
        else:
            missing_fields.append("Budget allocation")

        # 4. Company Name (+10)
        if lead.company and len(lead.company.strip()) > 1:
            score += LEAD_SCORING_WEIGHTS["company_identified"]
            reasons.append(f"Organization identified ({lead.company})")
        else:
            missing_fields.append("Company or organization name")

        # 5. Role / Decision Maker (+10)
        if lead.role and len(lead.role.strip()) > 2:
            score += LEAD_SCORING_WEIGHTS["decision_maker_identified"]
            reasons.append(f"Stakeholder role documented ({lead.role})")
        else:
            missing_fields.append("Stakeholder role / decision-making capacity")

        # 6. Concrete Requirements (+15)
        if lead.requirements and len(lead.requirements.strip()) > 8:
            score += LEAD_SCORING_WEIGHTS["concrete_requirements"]
            reasons.append("Technical requirements and integrations outlined")
        else:
            missing_fields.append("Specific technical requirements")

        # 7. Intent / Meeting (+15)
        if lead.lead_status == LeadStatus.MEETING_BOOKED or (lead.intent and "book" in lead.intent.lower()):
            score += LEAD_SCORING_WEIGHTS["meeting_requested"]
            reasons.append("Consultation meeting scheduled or requested")
        elif lead.intent and len(lead.intent.strip()) > 5:
            score += 10
            reasons.append("Active intent to implement AI solutions")
        else:
            missing_fields.append("Clear implementation intent")

        # Cap score at 100
        score = min(score, 100)

        # Recommended status based on deterministic threshold
        if lead.lead_status == LeadStatus.MEETING_BOOKED:
            recommended_status = LeadStatus.MEETING_BOOKED.value
        elif score >= 65:
            recommended_status = LeadStatus.QUALIFIED.value
        elif score >= 30:
            recommended_status = LeadStatus.QUALIFYING.value
        else:
            recommended_status = LeadStatus.NEW.value

        return LeadQualificationResult(
            lead_id=lead.id,
            qualification_score=score,
            reasons=reasons,
            missing_fields=missing_fields,
            recommended_status=recommended_status,
        )
