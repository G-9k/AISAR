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
        raise NotImplementedError("Ejercicio 03a: falta completar currency_system_prompt()")

    return solve


# Exercise 03b
@solver
def currency_agent_v0() -> Solver:
    # TODO: devolvé un chain(...) de tres solvers:
    #   1. currency_system_prompt()
    #   2. use_tools(...) con las dos tools del ejercicio 01
    #   3. generate(tool_calls="loop")
    raise NotImplementedError("Ejercicio 03b: falta completar currency_agent_v0()")
