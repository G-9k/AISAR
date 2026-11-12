"""The calculator tool (calculation_agent), as a deterministic mock (exercise 05).

In Ale's code (agents.py:366-390) the calculator is a sub-agent: an LLM (gemini-2.5-flash-lite)
wrapped by ADK's AgentTool. Here it is a fixed response per variant, like Aditya's replication
(run_step.py, CALCULATOR_RESPONSES). The texts live in data/calculator_responses/.

ADK wraps the sub-agent's text as {"result": "<text>"}; this tool returns that same dict,
serialized with json.dumps() like the other tools.
"""

import json

from inspect_ai.solver import Generate, Solver, TaskState, solver
from inspect_ai.tool import Tool, tool

from currency_eval.paths import DATA_DIR, read_text

RESPONSES_DIR = DATA_DIR / "calculator_responses"


# Exercise 05a
# The name the model sees is a design decision: "calculation_agent", as in the prompt and in Aditya,
# not ADK's "CalculationAgent". See D2 in docs/decisiones_diseno.md.
@tool(name="calculation_agent")
def calculation_agent(variant: str) -> Tool:
    path = RESPONSES_DIR / f"{variant}.txt"
    if not path.exists():
        raise ValueError(f"Unknown calculator variant: {variant!r}")
    response = json.dumps({"result": read_text(path)})

    async def execute(request: str) -> str:
        """Calculation agent

        Args:
            request: The request
        """
        return response

    return execute


# Exercise 05b
@solver
def add_calculator() -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        variant = state.metadata["calculator_variant"]
        state.tools.append(calculation_agent(variant))
        return state

    return solve
