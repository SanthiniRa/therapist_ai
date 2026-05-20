import json
import logging
from typing import Any, Dict

from pydantic import BaseModel, Field, ValidationError
from backend.mcp_context import build_mcp_context
from backend.prompt_builder import build_prompt
from backend.mode_strategies import get_mode_instruction
from backend.llm_adapter import GeminiAdapter
from backend.tool import TOOLS, maybe_call_tool, execute_tool, validate_tool_args

logger = logging.getLogger(__name__)


class MCPContext(BaseModel):
    mode: str
    knowledge: str = ""
    xp: int = 0
    user_email: str = ""
    history: str = ""
    profile: Dict[str, Any] = Field(default_factory=dict)
    session: Dict[str, Any] = Field(default_factory=dict)
    mode_instruction: str = ""


class ToolInvocation(BaseModel):
    tool: str
    args: Dict[str, Any] = Field(default_factory=dict)


def parse_tool_invocation(text: str):
    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    try:
        invocation = ToolInvocation(**payload)
        validate_tool_args(invocation.tool, invocation.args)
        return invocation
    except (ValidationError, ValueError):
        return None


def build_tool_instructions():
    tool_names = [name for name in sorted(TOOLS) if name != "maybe_call_tool"]
    tool_list = "\n".join([f"- {name}" for name in tool_names])

    return f"""
Available tools:
{tool_list}

If a tool is needed, respond ONLY with valid JSON of this form:
{{
  "tool": "tool_name",
  "args": {{
    "param": "value"
  }}
}}
Do not provide any additional text outside the JSON when calling a tool.
If no tool is needed, respond in plain conversational text.
"""


def create_final_prompt(user_input: str, tool_name: str, tool_output):
    output_text = tool_output
    if isinstance(tool_output, list):
        output_text = "\n".join(str(item) for item in tool_output)

    return f"""
You have executed the tool {tool_name}.
Tool result:
{output_text}

User: {user_input}

Respond empathetically and helpfully based on the tool result.
"""


def agent_controller(user_input, user, model, history=None, session=None, profile=None, user_id=None):

    # ✅ STEP 1: MCP Context
    context = build_mcp_context(user_input, user, history=history)
    context["profile"] = profile or {}
    context["session"] = session or {}

    # ✅ STEP 2: Add strategy instruction
    context["mode_instruction"] = get_mode_instruction(context["mode"])

    # ✅ STEP 3: Build prompt
    base_prompt = build_prompt(context, user_input)
    prompt = f"""
You are a compassionate AI therapist assistant.
{build_tool_instructions()}
{base_prompt}
"""

    # ✅ STEP 4: LLM call
    llm = GeminiAdapter(model)
    xp_gained = user.get("todayXP", 0) if isinstance(user, dict) else 0

    try:
        response = llm.generate(prompt).strip()
    except Exception as exc:
        logger.warning("LLM call failed: %s", exc)
        return {
            "response": "I'm having trouble contacting the AI service right now. Please try again in a moment.",
            "xp_gained": xp_gained,
            "mode": context["mode"],
        }

    logger.debug("MCP prompt sent. response length=%d", len(response))

    invocation = parse_tool_invocation(response)
    tool_output = None

    if invocation is not None:
        logger.info("Tool invocation parsed: %s", invocation.dict())
        if user_id is not None:
            try:
                tool_output = execute_tool(user_id, invocation.tool, invocation.args)
            except Exception as exc:
                logger.warning("Tool execution failed, falling back to normal response: %s", exc)
                tool_output = None
        else:
            logger.warning("Tool invocation received but no user_id available; skipping execution.")
            tool_output = None
    else:
        tool_output = maybe_call_tool(context["mode"])
        if tool_output is not None:
            logger.info("Auto-invoked tool for mode '%s'", context["mode"])

    if tool_output:
        logger.debug("Tool output received: %s", tool_output)
        tool_name = invocation.tool if invocation else context["mode"]
        final_prompt = create_final_prompt(user_input, tool_name, tool_output)
        response = llm.generate(final_prompt).strip()

    xp_gained = user.get("todayXP", 0) if isinstance(user, dict) else 0

    return {
        "response": response,
        "xp_gained": xp_gained,
        "mode": context["mode"]
    }