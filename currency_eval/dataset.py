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
    # TODO: leé data/prompts/main/<variant>.txt con read_text() y devolvé su contenido.
    #       Si el archivo no existe, lanzá ValueError con un mensaje que nombre la variante.
    raise NotImplementedError("Ejercicio 02a: falta completar load_main_prompt()")


# Exercise 02b
def make_sample(prompt_variant: str, calculator_variant: str) -> Sample:
    # TODO: devolvé un Sample con:
    #   id:       "<calculator_variant>__<prompt_variant>"   (ej. "CodeOnly__general")
    #   input:    el mensaje de usuario (load_user_message())
    #   target:   EXPECTED_FINAL_AMOUNT como string
    #   metadata: prompt_variant, calculator_variant, system_prompt (el texto del prompt)
    #             y todas las claves de SCENARIO
    raise NotImplementedError("Ejercicio 02b: falta completar make_sample()")


# Exercise 02c
def build_dataset(
    prompt_variants: list[str] | None = None,
    calculator_variants: list[str] | None = None,
) -> MemoryDataset:
    # TODO: si un argumento es None, usá la lista completa (PROMPT_VARIANTS / CALCULATOR_VARIANTS).
    #       Armá un Sample por cada combinación (calculador x prompt, en ese orden; mirá
    #       itertools.product) y devolvé MemoryDataset(samples, name="currency_conversion").
    raise NotImplementedError("Ejercicio 02c: falta completar build_dataset()")
