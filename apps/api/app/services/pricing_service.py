from typing import Dict, Any, List, Optional
from app.core.constants import DEMO_SERVICES


class PricingService:
    """
    Returns verified, structured pricing information exclusively from the approved catalog.
    Guarantees the AI never invents or hallucinates prices.
    """

    @staticmethod
    def get_service_pricing(service_name_or_query: str) -> Dict[str, Any]:
        query_norm = service_name_or_query.lower().strip()
        matched = []

        for s in DEMO_SERVICES:
            # Match on name, category, or service_id
            if (
                query_norm in s["name"].lower()
                or query_norm in s["service_id"].lower()
                or query_norm in s["category"].lower()
                or any(query_norm in cap.lower() for cap in s["capabilities"])
            ):
                matched.append(s)

        # Fallback to all services if query is general like "services" or "pricing"
        if not matched and any(term in query_norm for term in ["all", "pricing", "catalog", "services", "cost"]):
            matched = DEMO_SERVICES

        if not matched:
            return {
                "success": False,
                "service": service_name_or_query,
                "message": f"No exact matching service found in demo catalog for '{service_name_or_query}'. Available services include: "
                           + ", ".join(s["name"] for s in DEMO_SERVICES),
                "pricing": None,
                "is_demo": True,
            }

        primary = matched[0]
        return {
            "success": True,
            "service_id": primary["service_id"],
            "service_name": primary["name"],
            "category": primary["category"],
            "starting_price": primary["starting_price"],
            "pricing_notes": primary["pricing_notes"],
            "delivery_range": primary["delivery_range"],
            "capabilities": primary["capabilities"],
            "is_demo": True,
            "demo_disclaimer": "DEMO PRICING: Provided for interactive demonstration purposes only.",
        }

    @staticmethod
    def list_all_services() -> List[Dict[str, Any]]:
        return DEMO_SERVICES
