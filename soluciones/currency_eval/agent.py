"""The currency agent's loop, written by hand (exercises 04 and 05c).

Ported from run_single() and its two ADK plugins in runner.py:
  - CallLimitPlugin: at most 30 model calls per run.
  - ToolErrorToStatusPlugin: a failed tool call reaches the model as {"status": "error", ...}.
  - _derive_run_outcome(): every run ends with run_status "ok" or "failed" plus a reason.
The outcome is saved in the sample's store, with the same field names as Ale's JSONL records.
"""

import json

from inspect_ai.model import ChatMessageAssistant, ChatMessageTool, execute_tools, get_model
from inspect_ai.solver import Generate, Solver, TaskState, chain, solver, use_tools

from currency_eval.calculator import add_calculator
from currency_eval.solvers import currency_system_prompt
from currency_eval.tools import get_exchange_rate, get_fee_for_payment_method

# Inspect's stop_reason -> Ale's run_failure_reason, for runs that end without a visible answer.
# Inspect merges Gemini's SAFETY and RECITATION into "content_filter", so Ale's
# "finish_safety" and "finish_recitation" become a single reason here.
STOP_REASON_TO_FAILURE = {
    "max_tokens": "finish_max_tokens",
    "content_filter": "finish_content_filter",
    "unknown": "finish_other",
}


# Exercise 04a
def tool_error_as_status(message: ChatMessageTool) -> ChatMessageTool:
    if message.error is None:
        return message
    return ChatMessageTool(
        content=json.dumps(
            {"status": "error", "error_message": "Tool not found", "tool_name": message.function}
        ),
        tool_call_id=message.tool_call_id,
        function=message.function,
    )


# Exercise 04b
def derive_run_outcome(state: TaskState, call_limit_reached: bool) -> tuple[str, str | None]:
    if call_limit_reached:
        return "failed", "call_limit_reached"
    if state.output.completion != "":
        return "ok", None
    if state.output.stop_reason in STOP_REASON_TO_FAILURE:
        return "failed", STOP_REASON_TO_FAILURE[state.output.stop_reason]
    made_tool_calls = any(
        isinstance(message, ChatMessageAssistant) and message.tool_calls
        for message in state.messages
    )
    if made_tool_calls:
        return "failed", "stop_tool_only"
    return "failed", "stop_no_tool_no_text"


# Exercise 04c
@solver
def agent_loop(max_calls: int = 30) -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        model = get_model()
        calls = 0
        call_limit_reached = False
        while True:
            if calls == max_calls:
                call_limit_reached = True
                break
            output = await model.generate(state.messages, state.tools)
            calls += 1
            state.output = output
            state.messages.append(output.message)
            if not output.message.tool_calls:
                break
            result = await execute_tools(state.messages, state.tools)
            state.messages.extend(tool_error_as_status(message) for message in result.messages)

        run_status, run_failure_reason = derive_run_outcome(state, call_limit_reached)
        state.store.set("run_status", run_status)
        state.store.set("run_failure_reason", run_failure_reason)
        state.store.set("total_calls", calls)
        return state

    return solve


# Exercise 04d
@solver
def currency_agent_v1() -> Solver:
    return chain(
        currency_system_prompt(),
        use_tools(get_fee_for_payment_method(), get_exchange_rate()),
        agent_loop(),
    )


# Exercise 05c
@solver
def currency_agent() -> Solver:
    return chain(
        currency_system_prompt(),
        use_tools(get_fee_for_payment_method(), get_exchange_rate()),
        add_calculator(),
        agent_loop(),
    )
