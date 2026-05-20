from backend.agent_controller import agent_controller


class DummyAdapter:
    def __init__(self, model):
        pass

    def generate(self, prompt):
        raise RuntimeError("model unavailable")


def test_agent_controller_returns_fallback_when_llm_fails(monkeypatch):
    monkeypatch.setattr("backend.agent_controller.GeminiAdapter", DummyAdapter)
    monkeypatch.setattr("backend.mcp_context.get_context", lambda user_input: "sample knowledge")

    user = {"todayXP": 2, "email": "user@example.com"}
    result = agent_controller("I feel anxious", user, model=None)

    assert "trouble contacting the AI service" in result["response"]
    assert result["xp_gained"] == 2
    assert result["mode"] == "calm_support"
