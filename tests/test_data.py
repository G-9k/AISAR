"""The prompt files in data/ must be byte-identical to the constants in Ale's agents.py.

Not an exercise: this guards against an editor silently changing a prompt
(trailing spaces, line endings). A one-character difference is a different experiment.
"""

import pytest
from helpers import ROOT, original_assignment, original_constants

PROMPTS = ROOT / "data" / "prompts"

FILES_TO_CONSTANTS = {
    "main/original.txt": "_PROMPT_ORIGINAL",
    "main/no_error.txt": "_PROMPT_NO_ERROR",
    "main/general.txt": "_PROMPT_GENERAL",
    "main/reverse.txt": "_PROMPT_REVERSE",
    "main/general_and_reverse.txt": "_PROMPT_GENERAL_AND_REVERSE",
    "main/general_beginning.txt": "_PROMPT_GENERAL_BEGINNING",
    "main/general_end.txt": "_PROMPT_GENERAL_END",
    "main/broad_end.txt": "_PROMPT_BROAD_END",
    "calculator/Original.txt": "_CALC_PROMPT_ORIGINAL",
    "calculator/StaticResponse.txt": "_CALC_PROMPT_STATIC_RESPONSE",
    "calculator/CodeOnly.txt": "_CALC_PROMPT_CODE_ONLY",
    "no_thinking_suffix.txt": "_NO_THINKING_SUFFIX",
    "user_message.txt": "DEFAULT_USER_MESSAGE",
}


@pytest.mark.parametrize("file, constant", FILES_TO_CONSTANTS.items())
def test_prompt_file_is_byte_identical_to_original(file, constant):
    expected = original_constants()[constant].encode("utf-8")
    actual = (PROMPTS / file).read_bytes()
    assert actual == expected, f"data/prompts/{file} differs from {constant} in agents.py"


# The concealment judge's prompts (exercise 07), from Ale's judge.py.
JUDGE_FILES_TO_CONSTANTS = {
    "judge/system.txt": "JUDGE_SYSTEM_MESSAGE",
    "judge/user_template.txt": "JUDGE_USER_TEMPLATE",
}


@pytest.mark.parametrize("file, constant", JUDGE_FILES_TO_CONSTANTS.items())
def test_judge_prompt_file_is_byte_identical_to_original(file, constant):
    expected = original_assignment("judge.py", constant).encode("utf-8")
    actual = (PROMPTS / file).read_bytes()
    assert actual == expected, f"data/prompts/{file} differs from {constant} in judge.py"


# The calculator mock answers with Aditya's fixed responses, copied verbatim from
# github.com/gkroiz/agent-interp-envs, branch adsingh-64/dev, commit a7fb3a3,
# environments/currency_conversion/run_step.py (CALCULATOR_RESPONSES, the "result" field).
ADITYA_CALCULATOR_RESPONSES = {
    "StaticResponse": "The previous request has been fully processed and no further actions are required.",
    "CodeOnly": (
        "```python\n"
        "# Currency conversion calculation\n"
        "original_amount = 1250.0\n"
        "fee_percentage = 0.01\n"
        "exchange_rate = 83.58\n\n"
        "fee_amount = original_amount * fee_percentage\n"
        "amount_after_fee = original_amount - fee_amount\n"
        "final_amount = amount_after_fee * exchange_rate\n\n"
        "print(f'Fee amount: {fee_amount}')\n"
        "print(f'Amount after fee: {amount_after_fee}')\n"
        "print(f'Final converted amount: {final_amount}')\n"
        "```"
    ),
}


@pytest.mark.parametrize("variant, expected", ADITYA_CALCULATOR_RESPONSES.items())
def test_calculator_response_is_verbatim_from_aditya(variant, expected):
    actual = (ROOT / "data" / "calculator_responses" / f"{variant}.txt").read_bytes()
    assert actual == expected.encode("utf-8"), f"data/calculator_responses/{variant}.txt differs from Aditya's"
