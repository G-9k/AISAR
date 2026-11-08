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
        # TODO:
        #   1. Tomá el prompt de la metadata del sample (clave "system_prompt").
        #   2. Decidí si va el sufijo: si no_thinking_suffix es None, va solo cuando el modelo
        #      NO es Gemini (usá is_gemini(str(state.model))); si es True/False, obedecé eso.
        #   3. Insertá un ChatMessageSystem con el texto al PRINCIPIO de state.messages.
        #   4. Devolvé state.

        system_prompt = ChatMessageSystem(content = state.metadata["system_prompt"])

        if no_thinking_suffix is None:
            if is_gemini(str(state.model)): decision_suffix = False
            else: decision_suffix = True
        else: decision_suffix = no_thinking_suffix

        if decision_suffix:
            system_prompt.content = system_prompt.content + suffix
            state.messages.insert(0, system_prompt)
            return state
        else:
            state.messages.insert(0, system_prompt)
            return state

    return solve


# Exercise 03b
@solver
def currency_agent_v0() -> Solver:
    # TODO: devolvé un chain(...) de tres solvers:
    #   1. currency_system_prompt()
    #   2. use_tools(...) con las dos tools del ejercicio 01
    #   3. generate(tool_calls="loop")
    currency_agent = chain([currency_system_prompt(),
                            use_tools(get_fee_for_payment_method(), get_exchange_rate()),
                            generate(tool_calls="loop")])

    return currency_agent