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
    return Task(
        dataset=[Sample(input=USER_MESSAGE, target=EXPECTED_FINAL_AMOUNT)],
        solver=generate(),
        scorer=includes(),
    )


# Exercise 00b
def run_with_mock(answer: str, log_dir: str) -> EvalLog:
    model = get_model(
        "mockllm/model",
        custom_outputs=[ModelOutput.from_content(model="mockllm/model", content=answer)],
    )
    logs = eval(hello_currency(), model=model, log_dir=log_dir, display="none")
    return logs[0]


# Exercise 00c
def final_answer(log: EvalLog) -> str:
    return log.samples[0].output.completion


# Exercise 00d
def accuracy_of(log: EvalLog) -> float:
    return log.results.scores[0].metrics["accuracy"].value
