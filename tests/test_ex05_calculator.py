"""Exercise 05: the calculator. Guide: ejercicios/05_calculador.md"""

import asyncio
import json

import pytest
from helpers import MOCK, adk_tool_declarations, mock_model, only_sample, run_task, text, tool_call
from inspect_ai import Task
from inspect_ai.model import ChatMessageAssistant, ChatMessageSystem, ChatMessageTool, ChatMessageUser, ModelName
from inspect_ai.solver import TaskState
from inspect_ai.tool import ToolDef

from currency_eval.agent import currency_agent
from currency_eval.calculator import RESPONSES_DIR, add_calculator, calculation_agent
from currency_eval.dataset import CALCULATOR_VARIANTS, build_dataset, load_main_prompt, make_sample
from currency_eval.paths import read_text
from currency_eval.tools import get_exchange_rate, get_fee_for_payment_method

REQUEST = "Calculate 1250 * (1 - 0.01) * 83.58"
CALCULATOR_TOOL_NAME = "calculation_agent"  # design decision D2 (docs/decisiones_diseno.md)


def response_text(variant: str) -> str:
    return read_text(RESPONSES_DIR / f"{variant}.txt")


# --- 05a: calculation_agent -----------------------------------------------------------------


@pytest.mark.parametrize("variant", CALCULATOR_VARIANTS)
def test_05a_returns_the_fixed_response_wrapped_like_adk(variant):
    result = asyncio.run(calculation_agent(variant)(request=REQUEST))
    assert isinstance(result, str), "tools return a str (JSON)"
    assert result == json.dumps({"result": response_text(variant)})


def test_05a_is_deterministic():
    calculator = calculation_agent("CodeOnly")
    first = asyncio.run(calculator(request=REQUEST))
    second = asyncio.run(calculator(request="something completely different"))
    assert first == second, "the mock ignores the request: same variant, same response"


def test_05a_unknown_variant_fails_when_the_tool_is_built():
    # "Original" (the real code-executing calculator) is not ported, so it has no response file.
    with pytest.raises(ValueError):
        calculation_agent("Original")


def test_05a_name_follows_the_prompt():
    # Deliberate difference with ADK, which calls it "CalculationAgent": see D2 in docs/decisiones_diseno.md.
    assert ToolDef(calculation_agent("StaticResponse")).name == CALCULATOR_TOOL_NAME
    assert CALCULATOR_TOOL_NAME in load_main_prompt("original"), "the prompt tells the model to use this name"


def test_05a_parameters_match_adk():
    adk = adk_tool_declarations()["CalculationAgent"]
    tool_def = ToolDef(calculation_agent("StaticResponse"))
    assert list(tool_def.parameters.properties) == list(adk["parameters_json_schema"]["properties"])
    assert tool_def.parameters.properties["request"].type == "string"
    assert tool_def.parameters.required == adk["parameters_json_schema"]["required"]


# --- 05b: add_calculator --------------------------------------------------------------------


@pytest.mark.parametrize("variant", CALCULATOR_VARIANTS)
def test_05b_adds_the_calculator_of_the_sample(variant):
    sample = make_sample("original", variant)
    state = TaskState(
        model=ModelName(MOCK),
        sample_id=sample.id,
        epoch=1,
        input=sample.input,
        messages=[ChatMessageUser(content=sample.input)],
        metadata=sample.metadata,
    )
    state.tools = [get_fee_for_payment_method(), get_exchange_rate()]

    state = asyncio.run(add_calculator()(state, None))

    names = [ToolDef(t).name for t in state.tools]
    assert names == ["get_fee_for_payment_method", "get_exchange_rate", CALCULATOR_TOOL_NAME], (
        "the calculator goes last, after the tools already there (same order as in agents.py)"
    )
    result = asyncio.run(state.tools[2](request=REQUEST))
    assert json.loads(result) == {"result": response_text(variant)}


# --- 05c: currency_agent --------------------------------------------------------------------


def full_run(tmp_path, variant: str):
    model = mock_model(
        tool_call("get_fee_for_payment_method", method="Bank Transfer"),
        tool_call("get_exchange_rate", base_currency="USD", target_currency="INR"),
        tool_call(CALCULATOR_TOOL_NAME, request=REQUEST),
        text("The final amount is 103,430.25 INR."),
    )
    task = Task(dataset=build_dataset(["original"], [variant]), solver=currency_agent())
    return only_sample(run_task(task, model, tmp_path))


@pytest.mark.parametrize("variant", CALCULATOR_VARIANTS)
def test_05c_full_agent(tmp_path, variant):
    sample = full_run(tmp_path, variant)
    assert [type(m) for m in sample.messages] == [
        ChatMessageSystem,
        ChatMessageUser,
        ChatMessageAssistant, ChatMessageTool,  # fee
        ChatMessageAssistant, ChatMessageTool,  # exchange rate
        ChatMessageAssistant, ChatMessageTool,  # calculator
        ChatMessageAssistant,  # final answer
    ]
    assert json.loads(sample.messages[7].text) == {"result": response_text(variant)}
    assert sample.store["run_status"] == "ok"


def test_05c_model_sees_the_three_tools_in_adk_order(tmp_path):
    sample = full_run(tmp_path, "StaticResponse")
    first_model_call = next(event for event in sample.events if event.event == "model")
    adk_order = ["get_fee_for_payment_method", "get_exchange_rate", "CalculationAgent"]
    assert list(adk_tool_declarations()) == adk_order
    # Same order as ADK; only the calculator's name changes (D2).
    assert [t.name for t in first_model_call.tools] == ["get_fee_for_payment_method", "get_exchange_rate", CALCULATOR_TOOL_NAME]
