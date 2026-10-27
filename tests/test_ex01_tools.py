"""Exercise 01: tools. Guide: ejercicios/01_tools.md"""

import asyncio
import json

import pytest
from helpers import adk_tool_declarations, mock_model, only_sample, run_task, text, tool_call
from inspect_ai import Task
from inspect_ai.dataset import Sample
from inspect_ai.model import ChatMessageTool
from inspect_ai.solver import generate, use_tools
from inspect_ai.tool import ToolDef

from currency_eval.tools import get_exchange_rate, get_fee_for_payment_method


def call(tool, **arguments) -> dict:
    """Call an Inspect tool directly (outside an eval) and parse its JSON result."""
    result = asyncio.run(tool(**arguments))
    assert isinstance(result, str), f"The tool must return a str (JSON), got {type(result).__name__}"
    return json.loads(result)


# --- 01a: get_fee_for_payment_method -------------------------------------------------


@pytest.mark.parametrize("method", ["Bank Transfer", "bank transfer", "BANK TRANSFER"])
def test_01a_fee_success_is_case_insensitive(method):
    assert call(get_fee_for_payment_method(), method=method) == {
        "status": "success",
        "fee_percentage": 0.01,
    }


def test_01a_fee_other_methods():
    assert call(get_fee_for_payment_method(), method="Gold Debit Card")["fee_percentage"] == 0.035


def test_01a_fee_unknown_method_returns_status_error():
    assert call(get_fee_for_payment_method(), method="Bitcoin") == {
        "status": "error",
        "error_message": "Payment method 'Bitcoin' not found",
    }


# --- 01b: get_exchange_rate ------------------------------------------------------------


def test_01b_rate_success():
    assert call(get_exchange_rate(), base_currency="USD", target_currency="INR") == {
        "status": "success",
        "rate": 83.58,
    }
    assert call(get_exchange_rate(), base_currency="usd", target_currency="eur")["rate"] == 0.93


def test_01b_rate_unsupported_pair_returns_status_error():
    assert call(get_exchange_rate(), base_currency="USD", target_currency="ARS") == {
        "status": "error",
        "error_message": "Unsupported currency pair: USD/ARS",
    }


# --- What the model sees: must match what ADK sends to Gemini ----------------------------


@pytest.mark.parametrize("make_tool", [get_fee_for_payment_method, get_exchange_rate])
def test_tool_schema_matches_adk(make_tool):
    tool_def = ToolDef(make_tool())
    adk = adk_tool_declarations()[tool_def.name]
    assert tool_def.description == adk["description"], (
        "The tool description (docstring without the Args: section) must be identical "
        "to the docstring of the original function in agents.py"
    )
    adk_params = adk["parameters_json_schema"]
    assert list(tool_def.parameters.properties) == list(adk_params["properties"])
    assert tool_def.parameters.required == adk_params["required"]


# --- End to end: a scripted model calls the tool inside an eval ---------------------------


def test_tools_inside_an_eval(tmp_path):
    model = mock_model(
        tool_call("get_fee_for_payment_method", method="Bank Transfer"),
        tool_call("get_exchange_rate", base_currency="USD", target_currency="INR"),
        text("done"),
    )
    task = Task(
        dataset=[Sample(input="Convert 1,250 USD to INR using a Bank Transfer.")],
        solver=[use_tools(get_fee_for_payment_method(), get_exchange_rate()), generate()],
    )
    sample = only_sample(run_task(task, model, tmp_path))
    tool_messages = [m for m in sample.messages if isinstance(m, ChatMessageTool)]
    assert [json.loads(m.text) for m in tool_messages] == [
        {"status": "success", "fee_percentage": 0.01},
        {"status": "success", "rate": 83.58},
    ]
