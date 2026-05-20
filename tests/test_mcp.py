import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
from backend.mcp_context import build_mcp_context
from backend.agent_controller import agent_controller, ToolInvocation, parse_tool_invocation
from backend.tool import execute_tool


def test_build_mcp_context_returns_expected_keys(monkeypatch):
    def fake_get_context(user_input):
        return "sample knowledge"

    monkeypatch.setattr("backend.mcp_context.get_context", fake_get_context)

    user_input = "I feel anxious today"
    user = {"todayXP": 5, "history": ["hello"]}

    context = build_mcp_context(user_input, user)

    assert context["mode"] == "calm_support"
    assert context["knowledge"] == "sample knowledge"
    assert context["xp"] == 5


def test_agent_controller_returns_response_and_mode(monkeypatch):
    def fake_get_context(user_input):
        return "sample knowledge"

    class FakeModel:
        def generate_content(self, prompt):
            class Response:
                text = "Hello from LLM"
            return Response()

    monkeypatch.setattr("backend.mcp_context.get_context", fake_get_context)

    user_input = "I feel anxious today"
    user = {"todayXP": 3, "history": []}
    model = FakeModel()

    output = agent_controller(user_input, user, model)

    assert output["mode"] == "calm_support"
    assert output["response"].startswith("Hello from LLM")
    assert output["xp_gained"] == 3


def test_parse_tool_invocation_valid_json():
    invocation = parse_tool_invocation('{"tool": "cbt_reframe", "args": {"thought": "I worry"}}')

    assert invocation is not None
    assert invocation.tool == "cbt_reframe"
    assert invocation.args["thought"] == "I worry"


def test_parse_tool_invocation_with_code_fence():
    invocation = parse_tool_invocation('```json\n{"tool": "cbt_reframe", "args": {"thought": "I worry"}}\n```')

    assert invocation is not None
    assert invocation.tool == "cbt_reframe"
    assert invocation.args["thought"] == "I worry"


def test_execute_tool_validates_arguments():
    result = execute_tool("user@example.com", "cbt_reframe", {"thought": "I worry"})

    assert result["original_thought"] == "I worry"

    with pytest.raises(ValueError):
        execute_tool("user@example.com", "track_mood", {})
