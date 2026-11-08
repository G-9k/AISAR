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
    # TODO: si message.error es None, devolvé el mensaje sin tocar.
    #       Si no, devolvé un ChatMessageTool NUEVO, sin error, cuyo contenido sea el dict de
    #       ToolErrorToStatusPlugin (runner.py:99-131) serializado con json.dumps(), con las
    #       claves en el mismo orden: status, error_message, tool_name.
    #       tool_name es el nombre de la tool que pidió el modelo (message.function).
    #       Conservá tool_call_id y function: el resultado tiene que seguir respondiendo al mismo pedido.
    raise NotImplementedError("Ejercicio 04a: falta completar tool_error_as_status()")


# Exercise 04b
def derive_run_outcome(state: TaskState, call_limit_reached: bool) -> tuple[str, str | None]:
    # TODO: portá _derive_run_outcome (runner.py:268-318). Devolvé (run_status, run_failure_reason):
    #   1. si se alcanzó el límite de llamadas:         ("failed", "call_limit_reached")
    #   2. si la respuesta final tiene texto visible:    ("ok", None)
    #   3. si state.output.stop_reason está en STOP_REASON_TO_FAILURE: ("failed", <ese motivo>)
    #   4. si no: ("failed", "stop_tool_only") si el modelo pidió alguna tool en la conversación,
    #             ("failed", "stop_no_tool_no_text") si nunca pidió ninguna.
    raise NotImplementedError("Ejercicio 04b: falta completar derive_run_outcome()")


# Exercise 04c
@solver
def agent_loop(max_calls: int = 30) -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        # TODO: el loop del agente, a mano:
        #   - pedile una respuesta al modelo (get_model().generate) con state.messages y state.tools;
        #   - guardala en state.output y agregá su mensaje a state.messages;
        #   - si no pidió tools, terminó. Si pidió, ejecutalas (execute_tools), pasá cada mensaje
        #     resultante por tool_error_as_status y agregalos a state.messages; y volvé a empezar.
        #   - nunca más de max_calls llamadas al modelo (CallLimitPlugin).
        #   Al final, guardá en state.store: "run_status" y "run_failure_reason" (de derive_run_outcome)
        #   y "total_calls" (cuántas veces llamaste al modelo). Devolvé state.
        raise NotImplementedError("Ejercicio 04c: falta completar agent_loop()")

    return solve


# Exercise 04d
@solver
def currency_agent_v1() -> Solver:
    # TODO: igual que currency_agent_v0 (solvers.py), pero con agent_loop() en lugar de generate().
    raise NotImplementedError("Ejercicio 04d: falta completar currency_agent_v1()")


# Exercise 05c
@solver
def currency_agent() -> Solver:
    # TODO: el agente completo: system prompt, las dos tools del ejercicio 01, el calculador
    #       del sample (add_calculator) y el loop. El orden importa: es el orden en que el
    #       modelo ve las tools.
    raise NotImplementedError("Ejercicio 05c: falta completar currency_agent()")
