"""Exercise 03: solvers. Guide: ejercicios/03_solvers.md"""

import asyncio
import json

from helpers import mock_model, only_sample, run_task, text, tool_call
from inspect_ai import Task
from inspect_ai.model import (
    ChatMessageAssistant,
    ChatMessageSystem,
    ChatMessageTool,
    ChatMessageUser,
    ModelName,
)
from inspect_ai.solver import TaskState, system_message

from currency_eval.dataset import build_dataset, load_main_prompt, make_sample
from currency_eval.paths import PROMPTS_DIR, read_text
from currency_eval.solvers import currency_agent_v0, currency_system_prompt

SUFFIX = read_text(PROMPTS_DIR / "no_thinking_suffix.txt")


def state_for(sample_id_parts: tuple[str, str], model: str) -> TaskState:
    """Build a TaskState by hand, as Inspect would at the start of a sample."""
    sample = make_sample(*sample_id_parts)
    return TaskState(
        model=ModelName(model),
        sample_id=sample.id,
        epoch=1,
        input=sample.input,
        messages=[ChatMessageUser(content=sample.input)],
        metadata=sample.metadata,
    )


def run_solver(solver, state: TaskState) -> TaskState:
    """Call a solver directly, outside an eval. This solver never calls `generate`, so None is fine."""
    return asyncio.run(solver(state, None))


# --- 03a: currency_system_prompt ----------------------------------------------------------


def test_03a_system_prompt_for_gemini_has_no_suffix():
    state = run_solver(currency_system_prompt(), state_for(("reverse", "CodeOnly"), "google/gemini-3.1-pro-preview"))
    assert isinstance(state.messages[0], ChatMessageSystem)
    assert state.messages[0].text == load_main_prompt("reverse")
    assert isinstance(state.messages[1], ChatMessageUser), "the user message must stay after the system prompt"


def test_03a_system_prompt_for_other_models_has_suffix():
    state = run_solver(currency_system_prompt(), state_for(("reverse", "CodeOnly"), "openai/gpt-4.1"))
    assert state.messages[0].text == load_main_prompt("reverse") + SUFFIX


def test_03a_suffix_can_be_forced():
    on = run_solver(currency_system_prompt(no_thinking_suffix=True), state_for(("original", "CodeOnly"), "google/gemini-3.1-pro-preview"))
    off = run_solver(currency_system_prompt(no_thinking_suffix=False), state_for(("original", "CodeOnly"), "openai/gpt-4.1"))
    assert on.messages[0].text.endswith(SUFFIX)
    assert off.messages[0].text == load_main_prompt("original")


def test_03a_same_as_builtin_system_message_template():
    # Inspect's built-in system_message() fills {placeholders} from the sample metadata.
    mine = run_solver(currency_system_prompt(no_thinking_suffix=False), state_for(("general", "StaticResponse"), "openai/gpt-4.1"))
    builtin = run_solver(system_message("{system_prompt}"), state_for(("general", "StaticResponse"), "openai/gpt-4.1"))
    assert mine.messages[0].text == builtin.messages[0].text


# --- 03b: currency_agent_v0 ---------------------------------------------------------------


def test_03b_agent_v0_runs_the_tool_loop(tmp_path):
    model = mock_model(
        tool_call("get_fee_for_payment_method", method="Bank Transfer"),
        tool_call("get_exchange_rate", base_currency="USD", target_currency="INR"),
        text("The final amount is 103,430.25 INR."),
    )
    task = Task(dataset=build_dataset(["original"], ["StaticResponse"]), solver=currency_agent_v0())
    sample = only_sample(run_task(task, model, tmp_path))

    roles = [type(m) for m in sample.messages]
    assert roles == [
        ChatMessageSystem,
        ChatMessageUser,
        ChatMessageAssistant, ChatMessageTool,  # fee
        ChatMessageAssistant, ChatMessageTool,  # exchange rate
        ChatMessageAssistant,  # final answer, no tool call: the loop stops here
    ]
    assert sample.messages[0].text == load_main_prompt("original") + SUFFIX  # mockllm is not Gemini
    assert json.loads(sample.messages[5].text) == {"status": "success", "rate": 83.58}
    assert sample.output.completion == "The final amount is 103,430.25 INR."
