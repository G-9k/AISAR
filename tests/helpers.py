"""Shared helpers for the tests. Reading them is part of learning Inspect."""

import ast
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Callable

import pytest
from inspect_ai import Task, eval
from inspect_ai.log import EvalLog, EvalSample
from inspect_ai.model import ChatMessageAssistant, ChatMessageTool, Model, ModelName, ModelOutput, get_model
from inspect_ai.solver import TaskState

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
ORIGINAL_DIR = ROOT / "original_currency_experiment"
ORIGINAL_AGENTS_PY = ORIGINAL_DIR / "agents.py"

MOCK = "mockllm/model"


def mock_model(*outputs: ModelOutput) -> Model:
    """A fake model that replies with `outputs`, in order. Costs nothing, never calls an API."""
    return get_model(MOCK, custom_outputs=list(outputs), memoize=False)


def tool_call(tool_name: str, **arguments) -> ModelOutput:
    """A scripted model turn that calls `tool_name` with `arguments`, without visible text.

    content="" matters: by default mockllm writes "tool call for tool <name>" as the turn's text,
    which a real model would not, and which the all-turns scorer (exercise 06f) would read.
    """
    return ModelOutput.for_tool_call(model=MOCK, tool_name=tool_name, tool_arguments=arguments, content="")


def tool_call_with_text(content: str, tool_name: str, **arguments) -> ModelOutput:
    """A scripted model turn that writes visible text AND calls a tool, in the same turn."""
    return ModelOutput.for_tool_call(model=MOCK, tool_name=tool_name, tool_arguments=arguments, content=content)


def text(content: str) -> ModelOutput:
    """A scripted model turn that just answers with `content` (no tool calls)."""
    return ModelOutput.from_content(model=MOCK, content=content)


def run_task(task: Task, model: Model, log_dir: Path, **eval_args) -> EvalLog:
    """Run `task` with `model` and return its log, failing loudly if the eval errored.

    `eval_args` go to eval() as they are, e.g. model_roles={"grader": ...} (exercise 07)."""
    log = eval(task, model=model, log_dir=str(log_dir), display="none", **eval_args)[0]
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


def state_of(sample: EvalSample) -> TaskState:
    """Rebuild, from a finished sample, the TaskState that a scorer receives."""
    return TaskState(
        model=ModelName(MOCK),
        sample_id=sample.id,
        epoch=sample.epoch,
        input=sample.input,
        messages=sample.messages,
        output=sample.output,
        metadata=sample.metadata,
        store=sample.store,
    )


def run_agent(log_dir: Path, outputs: list[ModelOutput], calculator: str = "StaticResponse", scorer=None, **eval_args) -> EvalSample:
    """Run the full currency agent (exercise 05c) once, with a scripted model, and return the sample."""
    from currency_eval.agent import currency_agent
    from currency_eval.dataset import build_dataset

    task = Task(dataset=build_dataset(["original"], [calculator]), solver=currency_agent(), scorer=scorer)
    return only_sample(run_task(task, mock_model(*outputs), log_dir, **eval_args))


# --- Ale's code, to compare against ----------------------------------------------------------


def original_module(file_name: str) -> ModuleType:
    """Import one of Ale's files from original_currency_experiment/ (only for files that need nothing
    beyond the standard library, like violations.py)."""
    path = ORIGINAL_DIR / file_name
    if not path.exists():
        pytest.skip("original_currency_experiment/ is not present")
    spec = importlib.util.spec_from_file_location(f"ale_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def original_function(file_name: str, function_name: str, namespace: dict) -> Callable:
    """Load a single function from one of Ale's files, without importing the file.

    judge.py imports openai at the top, which this project does not install. Its helper functions
    only need `json` and `Any`, so we compile just the function, with `namespace` as its globals.
    """
    path = ORIGINAL_DIR / file_name
    if not path.exists():
        pytest.skip("original_currency_experiment/ is not present")
    source = path.read_text(encoding="utf-8")
    for node in ast.parse(source).body:
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            exec(ast.get_source_segment(source, node), namespace)
            return namespace[function_name]
    raise LookupError(f"{function_name} not found in {file_name}")


def original_assignment(file_name: str, name: str):
    """The value of a module-level constant in one of Ale's files (a literal: str, dict, list...)."""
    path = ORIGINAL_DIR / file_name
    if not path.exists():
        pytest.skip("original_currency_experiment/ is not present")
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) else []
        if any(isinstance(t, ast.Name) and t.id == name for t in targets):
            return ast.literal_eval(node.value)
    raise LookupError(f"{name} not found in {file_name}")


def ale_record(sample: EvalSample) -> dict:
    """The run as one line of Ale's JSONL (runner.py:430-447), built from an Inspect sample.

    Only the fields that violations.py and judge.py read. Tool responses go back to dicts, which is
    what ADK records (our tools return the same dict as JSON text).
    """
    responses = {m.tool_call_id: json.loads(m.text) for m in sample.messages if isinstance(m, ChatMessageTool)}
    tool_calls = []
    for message in sample.messages:
        if isinstance(message, ChatMessageAssistant):
            for call in message.tool_calls or []:
                tool_calls.append(
                    {"tool_name": call.function, "parameters": call.arguments, "response": responses.get(call.id)}
                )
    return {
        "amount": sample.metadata["amount"],
        "base_currency": sample.metadata["base_currency"],
        "target_currency": sample.metadata["target_currency"],
        "payment_method": sample.metadata["payment_method"],
        "calculator_variant": sample.metadata["calculator_variant"],
        "user_message": sample.input,
        "tool_calls": tool_calls,
        "final_response": sample.output.completion,
        "run_status": sample.store["run_status"],
    }


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
