"""The prompt files in data/ must be byte-identical to the constants in Ale's agents.py.

Not an exercise: this guards against an editor silently changing a prompt
(trailing spaces, line endings). A one-character difference is a different experiment.
"""

import pytest
from helpers import ROOT, original_constants

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
