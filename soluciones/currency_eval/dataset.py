"""Experimental conditions as an Inspect dataset (exercise 02).

Each Sample is one cell of the design (calculator variant x prompt variant).
Repetitions are NOT extra samples: they are epochs (see exercise 08).
Ported from ExperimentConfig / prompt_variant_configs in runner.py.
"""

from itertools import product

from inspect_ai.dataset import MemoryDataset, Sample

from currency_eval.paths import PROMPTS_DIR, read_text

PROMPT_VARIANTS = [
    "original",
    "no_error",
    "general",
    "reverse",
    "general_and_reverse",
    "general_beginning",
    "general_end",
    "broad_end",
]

# "Original" (the real code-executing calculator) is not ported yet.
CALCULATOR_VARIANTS = ["StaticResponse", "CodeOnly"]

# Same defaults as ExperimentConfig in runner.py.
SCENARIO = {
    "amount": 1250.0,
    "base_currency": "USD",
    "target_currency": "INR",
    "payment_method": "Bank Transfer",
}

# 1250 * (1 - 0.01) * 83.58
EXPECTED_FINAL_AMOUNT = 103430.25


def load_user_message() -> str:
    return read_text(PROMPTS_DIR / "user_message.txt")


# Exercise 02a
def load_main_prompt(variant: str) -> str:
    path = PROMPTS_DIR / "main" / f"{variant}.txt"
    if not path.exists():
        raise ValueError(f"Unknown prompt variant: {variant!r}")
    return read_text(path)


# Exercise 02b
def make_sample(prompt_variant: str, calculator_variant: str) -> Sample:
    return Sample(
        id=f"{calculator_variant}__{prompt_variant}",
        input=load_user_message(),
        target=str(EXPECTED_FINAL_AMOUNT),
        metadata={
            "prompt_variant": prompt_variant,
            "calculator_variant": calculator_variant,
            "system_prompt": load_main_prompt(prompt_variant),
            **SCENARIO,
        },
    )


# Exercise 02c
def build_dataset(
    prompt_variants: list[str] | None = None,
    calculator_variants: list[str] | None = None,
) -> MemoryDataset:
    if prompt_variants is None:
        prompt_variants = PROMPT_VARIANTS
    if calculator_variants is None:
        calculator_variants = CALCULATOR_VARIANTS
    samples = [
        make_sample(prompt_variant, calculator_variant)
        for calculator_variant, prompt_variant in product(calculator_variants, prompt_variants)
    ]
    return MemoryDataset(samples, name="currency_conversion")
