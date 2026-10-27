"""Exercise 02: dataset. Guide: ejercicios/02_dataset.md"""

import pytest
from helpers import original_constants
from inspect_ai.dataset import Dataset, Sample

from currency_eval.dataset import (
    CALCULATOR_VARIANTS,
    PROMPT_VARIANTS,
    build_dataset,
    load_main_prompt,
    load_user_message,
    make_sample,
)

# --- 02a: load_main_prompt --------------------------------------------------------------


@pytest.mark.parametrize("variant", PROMPT_VARIANTS)
def test_02a_load_main_prompt_is_verbatim(variant):
    expected = original_constants()[f"_PROMPT_{variant.upper()}"]
    assert load_main_prompt(variant) == expected


def test_02a_unknown_variant_raises_value_error():
    with pytest.raises(ValueError):
        load_main_prompt("does_not_exist")


# --- 02b: make_sample -------------------------------------------------------------------


def test_02b_make_sample():
    sample = make_sample("general", "CodeOnly")
    assert isinstance(sample, Sample)
    assert sample.id == "CodeOnly__general"
    assert sample.input == load_user_message()
    assert sample.target == "103430.25"
    assert sample.metadata == {
        "prompt_variant": "general",
        "calculator_variant": "CodeOnly",
        "system_prompt": load_main_prompt("general"),
        "amount": 1250.0,
        "base_currency": "USD",
        "target_currency": "INR",
        "payment_method": "Bank Transfer",
    }


# --- 02c: build_dataset -----------------------------------------------------------------


def test_02c_full_design_has_one_sample_per_cell():
    dataset = build_dataset()
    assert isinstance(dataset, Dataset)
    assert len(dataset) == len(PROMPT_VARIANTS) * len(CALCULATOR_VARIANTS) == 16
    ids = [sample.id for sample in dataset]
    assert len(set(ids)) == len(ids), "sample ids must be unique"
    assert ids[0] == "StaticResponse__original"
    assert ids[-1] == "CodeOnly__broad_end"


def test_02c_filtering():
    dataset = build_dataset(prompt_variants=["original", "broad_end"], calculator_variants=["CodeOnly"])
    assert [sample.id for sample in dataset] == ["CodeOnly__original", "CodeOnly__broad_end"]
