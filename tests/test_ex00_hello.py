"""Exercise 00: your first Inspect eval. Guide: ejercicios/00_primera_eval.md"""

from inspect_ai import Task
from inspect_ai.log import read_eval_log

from currency_eval.ex00_hello import (
    EXPECTED_FINAL_AMOUNT,
    USER_MESSAGE,
    accuracy_of,
    final_answer,
    hello_currency,
    run_with_mock,
)

GOOD_ANSWER = "After the 1% fee you get 103430.25 INR."
BAD_ANSWER = "You get about 104,475 INR."


def test_00a_task_structure():
    task = hello_currency()
    assert isinstance(task, Task)
    samples = list(task.dataset)
    assert len(samples) == 1
    assert samples[0].input == USER_MESSAGE
    assert samples[0].target == EXPECTED_FINAL_AMOUNT


def test_00b_run_with_mock_returns_a_successful_log(tmp_path):
    log = run_with_mock(GOOD_ANSWER, log_dir=str(tmp_path))
    assert log.status == "success"
    assert log.eval.model == "mockllm/model"
    # The log was also written to disk, and can be read back.
    assert read_eval_log(log.location).status == "success"


def test_00c_final_answer(tmp_path):
    log = run_with_mock(GOOD_ANSWER, log_dir=str(tmp_path))
    assert final_answer(log) == GOOD_ANSWER


def test_00d_accuracy(tmp_path):
    assert accuracy_of(run_with_mock(GOOD_ANSWER, log_dir=str(tmp_path))) == 1.0
    assert accuracy_of(run_with_mock(BAD_ANSWER, log_dir=str(tmp_path))) == 0.0
