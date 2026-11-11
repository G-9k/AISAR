"""Exercise 04: the agent loop, written by hand. Guide: ejercicios/04_loop_del_agente.md"""

import json

import pytest
from helpers import MOCK, mock_model, only_sample, run_task, text, tool_call
from inspect_ai import Task
from inspect_ai.model import (
    ChatMessageAssistant,
    ChatMessageTool,
    ChatMessageUser,
    ContentReasoning,
    ModelName,
    ModelOutput,
)
from inspect_ai.solver import TaskState, use_tools
from inspect_ai.tool import ToolCall, ToolCallError

from currency_eval.agent import agent_loop, currency_agent_v1, derive_run_outcome, tool_error_as_status
from currency_eval.dataset import build_dataset
from currency_eval.solvers import currency_agent_v0
from currency_eval.tools import get_exchange_rate, get_fee_for_payment_method

FINAL_ANSWER = "The final amount is 103,430.25 INR."


def happy_path():
    """A scripted model that looks up the fee and the rate, then answers."""
    return [
        tool_call("get_fee_for_payment_method", method="Bank Transfer"),
        tool_call("get_exchange_rate", base_currency="USD", target_currency="INR"),
        text(FINAL_ANSWER),
    ]


# --- 04a: tool_error_as_status -------------------------------------------------------------


def test_04a_tool_error_becomes_the_status_dict_of_ale():
    failed = ChatMessageTool(
        content="",
        tool_call_id="call_1",
        function="calculation_agent",
        error=ToolCallError("parsing", "Tool calculation_agent not found"),
    )
    converted = tool_error_as_status(failed)
    # Same keys, same order as ToolErrorToStatusPlugin in runner.py: the model reads this text.
    assert converted.text == json.dumps(
        {"status": "error", "error_message": "Tool not found", "tool_name": "calculation_agent"}
    )
    assert converted.error is None, "the model must receive the dict as a normal tool result, not as an error"
    assert converted.tool_call_id == "call_1", "the result must still answer the same tool call"
    assert converted.function == "calculation_agent"


def test_04a_successful_results_are_untouched():
    ok = ChatMessageTool(
        content='{"status": "success", "rate": 83.58}', tool_call_id="call_2", function="get_exchange_rate"
    )
    assert tool_error_as_status(ok) == ok


# --- 04b: derive_run_outcome ---------------------------------------------------------------

FEE_CALL = ChatMessageAssistant(
    content="",
    tool_calls=[ToolCall(id="c1", function="get_fee_for_payment_method", arguments={"method": "Bank Transfer"})],
)


def finished_state(last_turn: ModelOutput, earlier_turns: list = []) -> TaskState:
    """A TaskState as it looks when the loop has just stopped, built by hand."""
    state = TaskState(
        model=ModelName(MOCK),
        sample_id="s",
        epoch=1,
        input="Convert 1,250 USD to INR",
        messages=[ChatMessageUser(content="Convert 1,250 USD to INR"), *earlier_turns, last_turn.message],
    )
    state.output = last_turn
    return state


@pytest.mark.parametrize(
    "last_turn, earlier_turns, call_limit_reached, expected",
    [
        (text(FINAL_ANSWER), [], False, ("ok", None)),
        (text(FINAL_ANSWER), [], True, ("failed", "call_limit_reached")),
        (ModelOutput.from_content(MOCK, "", stop_reason="max_tokens"), [], False, ("failed", "finish_max_tokens")),
        (ModelOutput.from_content(MOCK, "", stop_reason="content_filter"), [], False, ("failed", "finish_content_filter")),
        (ModelOutput.from_content(MOCK, "", stop_reason="unknown"), [], False, ("failed", "finish_other")),
        (text(""), [], False, ("failed", "stop_no_tool_no_text")),
        (text(""), [FEE_CALL], False, ("failed", "stop_tool_only")),
    ],
    ids=["answer", "call-limit", "max-tokens", "content-filter", "unknown", "nothing", "tools-but-no-answer"],
)
def test_04b_derive_run_outcome(last_turn, earlier_turns, call_limit_reached, expected):
    state = finished_state(last_turn, earlier_turns)
    assert derive_run_outcome(state, call_limit_reached) == expected


def test_04b_thinking_alone_is_not_an_answer():
    # Ale skips thought=True parts when extracting the final response. In Inspect the thinking
    # arrives as ContentReasoning, which output.completion already leaves out.
    only_thinking = ModelOutput.from_content(MOCK, [ContentReasoning(reasoning="1237.5 * 83.58 = 103430.25")])
    state = finished_state(only_thinking)
    assert derive_run_outcome(state, call_limit_reached=False) == ("failed", "stop_no_tool_no_text")


# --- 04c: agent_loop -----------------------------------------------------------------------


def run_loop(tmp_path, outputs, max_calls: int = 30):
    task = Task(
        dataset=build_dataset(["original"], ["StaticResponse"]),
        solver=[use_tools(get_fee_for_payment_method(), get_exchange_rate()), agent_loop(max_calls=max_calls)],
    )
    return only_sample(run_task(task, mock_model(*outputs), tmp_path))


def test_04c_stops_at_the_first_turn_without_tool_calls(tmp_path):
    sample = run_loop(tmp_path, happy_path())
    assert [type(m) for m in sample.messages] == [
        ChatMessageUser,
        ChatMessageAssistant, ChatMessageTool,  # fee
        ChatMessageAssistant, ChatMessageTool,  # exchange rate
        ChatMessageAssistant,  # final answer
    ]
    assert json.loads(sample.messages[4].text) == {"status": "success", "rate": 83.58}
    assert sample.output.completion == FINAL_ANSWER, "the loop must keep state.output up to date"


def test_04c_saves_the_run_outcome_in_the_store(tmp_path):
    sample = run_loop(tmp_path, happy_path())
    assert sample.store["run_status"] == "ok"
    assert sample.store["run_failure_reason"] is None
    assert sample.store["total_calls"] == 3


def test_04c_unknown_tool_reaches_the_model_as_a_status_dict(tmp_path):
    # The prompt calls the tool "calculation_agent", but this agent has no such tool.
    sample = run_loop(tmp_path, [tool_call("calculation_agent", request="1237.5 * 83.58"), text(FINAL_ANSWER)])
    tool_message = sample.messages[2]
    assert isinstance(tool_message, ChatMessageTool)
    assert tool_message.error is None
    assert json.loads(tool_message.text) == {
        "status": "error",
        "error_message": "Tool not found",
        "tool_name": "calculation_agent",
    }


def test_04c_call_limit(tmp_path):
    # A model that never stops calling tools. With max_calls=3 the loop must stop after 3 model calls.
    endless = [tool_call("get_fee_for_payment_method", method="Bank Transfer") for _ in range(10)]
    sample = run_loop(tmp_path, endless, max_calls=3)
    assistant_turns = [m for m in sample.messages if isinstance(m, ChatMessageAssistant)]
    assert len(assistant_turns) == 3
    assert sample.store["run_status"] == "failed"
    assert sample.store["run_failure_reason"] == "call_limit_reached"
    assert sample.store["total_calls"] == 3


def test_04c_an_answer_on_the_last_allowed_call_is_ok(tmp_path):
    # The limit forbids a call number max_calls + 1. A final answer on call number max_calls is a
    # normal, successful run: CallLimitPlugin only raises when a call goes over the limit.
    sample = run_loop(tmp_path, happy_path(), max_calls=3)
    assert sample.store["run_status"] == "ok"
    assert sample.store["total_calls"] == 3


def test_04c_tool_calls_without_a_final_answer(tmp_path):
    sample = run_loop(tmp_path, [tool_call("get_fee_for_payment_method", method="Bank Transfer"), text("")])
    assert (sample.store["run_status"], sample.store["run_failure_reason"]) == ("failed", "stop_tool_only")


# --- 04d: currency_agent_v1 ----------------------------------------------------------------


def test_04d_v1_writes_the_same_conversation_as_v0(tmp_path):
    # Differential test: in the normal case, the hand-written loop must behave exactly like
    # Inspect's generate(tool_calls="loop").
    dataset = build_dataset(["original"], ["StaticResponse"])
    v0 = only_sample(run_task(Task(dataset=dataset, solver=currency_agent_v0()), mock_model(*happy_path()), tmp_path / "v0"))
    v1 = only_sample(run_task(Task(dataset=dataset, solver=currency_agent_v1()), mock_model(*happy_path()), tmp_path / "v1"))
    assert [(type(m), m.text) for m in v1.messages] == [(type(m), m.text) for m in v0.messages]
    assert v1.store["run_status"] == "ok"
