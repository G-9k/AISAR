"""Solvers for the currency agent (exercise 03).

currency_system_prompt() reproduces how build_currency_agent() in agents.py picks the
instruction: the sample's prompt variant, plus a "be methodical" suffix for non-Gemini models.
currency_agent_v0() is a first, simplified agent (no calculator yet; that is exercise 05).
"""

from inspect_ai.model import ChatMessageSystem
from inspect_ai.solver import Generate, Solver, TaskState, chain, generate, solver, use_tools

from currency_eval.paths import PROMPTS_DIR, read_text
from currency_eval.tools import get_exchange_rate, get_fee_for_payment_method


def is_gemini(model_name: str) -> bool:
    """Same rule as agents.py: any model whose name contains 'gemini'."""
    return "gemini" in model_name.lower()


# Exercise 03a
@solver
def currency_system_prompt(no_thinking_suffix: bool | None = None) -> Solver:
    suffix = read_text(PROMPTS_DIR / "no_thinking_suffix.txt")

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        prompt = state.metadata["system_prompt"]
        if no_thinking_suffix is None:
            add_suffix = not is_gemini(str(state.model))
        else:
            add_suffix = no_thinking_suffix
        if add_suffix:
            prompt = prompt + suffix
        state.messages.insert(0, ChatMessageSystem(content=prompt))
        return state

    return solve


# Exercise 03b
@solver
def currency_agent_v0() -> Solver:
    return chain(
        currency_system_prompt(),
        use_tools(get_fee_for_payment_method(), get_exchange_rate()),
        generate(tool_calls="loop"),
    )
