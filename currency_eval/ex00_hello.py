"""Exercise 00: your first Inspect eval.

A one-sample task that asks the model to do the currency conversion, with no tools.
It is not part of the final port: it exists to learn Task, Sample, eval(), logs and mockllm.

Run it from the terminal:
    inspect eval currency_eval/ex00_hello.py --model mockllm/model
    inspect view
"""

from inspect_ai import Task, eval, task
from inspect_ai.dataset import Sample
from inspect_ai.log import EvalLog
from inspect_ai.model import ModelOutput, get_model
from inspect_ai.scorer import includes
from inspect_ai.solver import generate

USER_MESSAGE = "Convert 1,250 USD to INR using a Bank Transfer. Show me the precise calculation."

# 1250 * (1 - 0.01) * 83.58: the amount the agent should report.
EXPECTED_FINAL_AMOUNT = "103430.25"


# Exercise 00a
@task
def hello_currency() -> Task:
    # TODO: devolvé una Task con:
    #   - dataset: una lista con un solo Sample (input=USER_MESSAGE, target=EXPECTED_FINAL_AMOUNT)
    #   - solver: generate()
    #   - scorer: includes()
    raise NotImplementedError("Ejercicio 00a: falta completar hello_currency()")


# Exercise 00b
def run_with_mock(answer: str, log_dir: str) -> EvalLog:
    # TODO:
    #   1. Creá un modelo falso con get_model("mockllm/model", custom_outputs=[...]) que responda `answer`.
    #      Una respuesta guionada se arma con ModelOutput.from_content(model="mockllm/model", content=answer).
    #   2. Corré eval(hello_currency(), model=..., log_dir=log_dir, display="none").
    #   3. eval() devuelve una LISTA de logs (uno por task): devolvé el primero.
    raise NotImplementedError("Ejercicio 00b: falta completar run_with_mock()")


# Exercise 00c
def final_answer(log: EvalLog) -> str:
    # TODO: devolvé el texto de la respuesta final del (único) sample del log.
    raise NotImplementedError("Ejercicio 00c: falta completar final_answer()")


# Exercise 00d
def accuracy_of(log: EvalLog) -> float:
    # TODO: devolvé el valor de la métrica "accuracy" del primer scorer del log.
    raise NotImplementedError("Ejercicio 00d: falta completar accuracy_of()")
