"""Shared helpers for the tests. Reading them is part of learning Inspect."""

import ast
import json
from pathlib import Path

import pytest
from inspect_ai import Task, eval
from inspect_ai.log import EvalLog, EvalSample
from inspect_ai.model import Model, ModelOutput, get_model

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
ORIGINAL_AGENTS_PY = ROOT / "original_currency_experiment" / "agents.py"

MOCK = "mockllm/model"


def mock_model(*outputs: ModelOutput) -> Model:
    """A fake model that replies with `outputs`, in order. Costs nothing, never calls an API."""
    return get_model(MOCK, custom_outputs=list(outputs), memoize=False)


def tool_call(tool_name: str, **arguments) -> ModelOutput:
    """A scripted model turn that calls `tool_name` with `arguments`."""
    return ModelOutput.for_tool_call(model=MOCK, tool_name=tool_name, tool_arguments=arguments)


def text(content: str) -> ModelOutput:
    """A scripted model turn that just answers with `content` (no tool calls)."""
    return ModelOutput.from_content(model=MOCK, content=content)


def run_task(task: Task, model: Model, log_dir: Path) -> EvalLog:
    """Run `task` with `model` and return its log, failing loudly if the eval errored."""
    log = eval(task, model=model, log_dir=str(log_dir), display="none")[0]
    if log.status != "success":
        raise AssertionError(f"Eval failed: {log.error.message if log.error else log.status}")
    return log


def only_sample(log: EvalLog) -> EvalSample:
    assert log.samples is not None and len(log.samples) == 1
    return log.samples[0]


def adk_tool_declarations() -> dict[str, dict]:
    """What Google ADK sends to Gemini for each tool of Ale's agent, keyed by tool name."""
    data = json.loads((FIXTURES / "adk_tool_declarations.json").read_text(encoding="utf-8"))
    return {decl["name"]: decl for decl in data["tools"]}


def original_constants() -> dict[str, str]:
    """String constants of original_currency_experiment/agents.py, read without importing ADK."""
    if not ORIGINAL_AGENTS_PY.exists():
        pytest.skip("original_currency_experiment/ is not present")
    tree = ast.parse(ORIGINAL_AGENTS_PY.read_text(encoding="utf-8"))
    constants = {}
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            constants[node.targets[0].id] = node.value.value
    return constants
