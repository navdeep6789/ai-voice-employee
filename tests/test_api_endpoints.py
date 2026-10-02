import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_fastapi_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Health check
        res = await ac.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "Voice Employee" in data["service"]

        # 2. Public config
        res_cfg = await ac.get("/api/config")
        assert res_cfg.status_code == 200
        cfg = res_cfg.json()
        assert cfg["demo_mode"] is True
        assert len(cfg["services"]) >= 5
        # Verify API key is NOT exposed
        assert "GEMINI_API_KEY" not in cfg
        assert "gemini_api_key" not in cfg

        # 3. Calendar slots
        res_cal = await ac.get("/api/calendar/slots")
        assert res_cal.status_code == 200
        slots = res_cal.json()
        assert len(slots) > 0

        # 4. Leads listing
        res_leads = await ac.get("/api/leads")
        assert res_leads.status_code == 200
        leads = res_leads.json()
        assert len(leads) >= 2

        # 5. Knowledge search
        res_rag = await ac.get("/api/knowledge/search?query=voice+agents")
        assert res_rag.status_code == 200
        rag_data = res_rag.json()
        assert rag_data["success"] is True
        assert len(rag_data["results"]) > 0

        # 6. Chat endpoint text fallback
        res_chat = await ac.post("/api/chat", json={
            "session_id": "test-session-chat-1",
            "message": "Hello, what services do you provide?"
        })
        assert res_chat.status_code == 200
        chat_data = res_chat.json()
        assert "reply" in chat_data
        assert len(chat_data["reply"]) > 10
