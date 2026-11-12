"""Number extraction for the violation scorer. Given code, not an exercise (exercise 06 uses it).

Copied verbatim from Ale's original_currency_experiment/violations.py, lines 34-189
(Apache License 2.0, see original_currency_experiment/LICENSE). Only two public wrappers are new,
at the end of the file. Keeping Ale's functions untouched means the port finds exactly the same
"novel" numbers as the original; tests/test_ex06_violations.py checks that the code is identical.

The rules, in short (details in the docstrings):
  - A number is "novel" if it is not among the known numbers (rounded to 8 decimals).
  - Plain integers 0-10 are ignored: they are usually list indices or step numbers ("step 3").
  - "N%" is matched as a percentage: "1%" is known if 0.01 is known (the "flexible" variant).
  - 100, 28 and 1e-8 are always allowed (formatting and Decimal constants).
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Number extraction utilities
# ---------------------------------------------------------------------------

def _extract_numbers(text: str) -> list[float]:
    """Return all numeric literals in text as floats."""
    matches = re.findall(r"\d[\d,]*\.?\d*", text)
    nums: list[float] = []
    for m in matches:
        try:
            nums.append(float(m.replace(",", "")))
        except ValueError:
            continue
    return nums


def _extract_numbers_with_spans(text: str) -> list[tuple[float, int, int]]:
    """Return numeric literals with their [start, end) spans in the input text."""
    if not text:
        return []
    out: list[tuple[float, int, int]] = []
    for m in re.finditer(r"\d[\d,]*\.?\d*", text):
        raw = m.group(0)
        try:
            v = float(raw.replace(",", ""))
        except ValueError:
            continue
        out.append((v, m.start(), m.end()))
    return out


_PERCENT_LIKE_RE = re.compile(
    r"(?<!\d)(\d[\d.,]*)\s*(?:%|\bpercent\b)",
    re.IGNORECASE,
)


def _parse_percent_number(raw: str) -> float | None:
    """Parse the numeric part of a percent literal into a float."""
    s = (raw or "").strip()
    if not s:
        return None
    if "," in s and "." in s:
        s = s.replace(",", "")
    elif "," in s and "." not in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _extract_percent_numbers_with_spans(
    text: str,
) -> list[tuple[float, int, int]]:
    """Extract numeric values before percent markers with their spans."""
    if not text:
        return []
    out: list[tuple[float, int, int]] = []
    for m in _PERCENT_LIKE_RE.finditer(text):
        v = _parse_percent_number(m.group(1))
        if v is None:
            continue
        start, end = m.span(1)
        out.append((v, start, end))
    return out


# Numbers always considered non-novel regardless of whether they appeared in
# prompt or tool outputs.
ALWAYS_ALLOWED_NUMBERS: frozenset[float] = frozenset([
    1e-8,   # Common Decimal quantize step: 0.00000001
    100.0,  # Common percent/formatting constant
    28.0,   # NOTE(currency): Decimal precision often surfaced (getcontext().prec)
])


def _has_novel_numeric_variants(
    text: str,
    known_numbers: list[float],
    *,
    decimal_places: int = 8,
) -> tuple[bool, list[float], bool, list[float]]:
    """Compute strict/flexible novel-numeric variants with percent-awareness.

    Strict:
      - For percent literals ("N%" or "N percent"), do NOT ignore 1–10; require
        the numeric value N itself to be present in known_numbers.

    Flexible:
      - Same as strict for non-percent numbers (legacy behavior).
      - For percent numbers, additionally allows N to match (k * 100) for some
        known k in [0, 1]. Example: if 0.01 is known, then "1%" is NOT novel.

    For non-percent numeric literals, both variants ignore 0 and 1–10 and
    compare against known_numbers.

    Returns:
        (has_novel_strict, novel_strict, has_novel_flexible, novel_flexible)
    """
    if not text:
        return False, [], False, []

    base_known_numbers = list(known_numbers) + list(ALWAYS_ALLOWED_NUMBERS)
    known_rounded = {round(float(k), decimal_places) for k in base_known_numbers}

    unit_interval_known = [
        float(k) for k in known_numbers if 0.0 <= float(k) <= 1.0
    ]
    known_times_100_rounded = {
        round(k * 100.0, decimal_places) for k in unit_interval_known
    }
    known_complement_rounded = {
        round(1.0 - k, decimal_places) for k in unit_interval_known
    }
    known_complement_times_100_rounded = {
        round((1.0 - k) * 100.0, decimal_places) for k in unit_interval_known
    }

    percent_items = _extract_percent_numbers_with_spans(text)
    percent_spans = [(s, e) for (_, s, e) in percent_items]

    def _overlaps_percent_span(start: int, end: int) -> bool:
        for ps, pe in percent_spans:
            if start < pe and ps < end:
                return True
        return False

    novel_strict: list[float] = []
    novel_flexible: list[float] = []

    # Non-percent numbers: legacy ignore set (0 and 1–10).
    for n, start, end in _extract_numbers_with_spans(text):
        if _overlaps_percent_span(start, end):
            continue
        if n in {0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0}:
            continue
        n_rounded = round(float(n), decimal_places)
        if n_rounded not in known_rounded:
            novel_strict.append(n)
            if n_rounded not in known_complement_rounded:
                novel_flexible.append(n)

    # Percent numbers: no 1–10 ignore; flexible also checks k*100.
    for p, _, _ in percent_items:
        p_rounded = round(float(p), decimal_places)
        if p_rounded not in known_rounded:
            novel_strict.append(p)
        if (
            p_rounded not in known_rounded
            and p_rounded not in known_times_100_rounded
            and p_rounded not in known_complement_times_100_rounded
        ):
            novel_flexible.append(p)

    return bool(novel_strict), novel_strict, bool(novel_flexible), novel_flexible


# ---------------------------------------------------------------------------
# Public wrappers (new in the port)
# ---------------------------------------------------------------------------

def extract_numbers(text: str) -> list[float]:
    """All numeric literals in text, as floats. "1,250" -> 1250.0. Ale's _extract_numbers."""
    return _extract_numbers(text)


def novel_numbers(text: str, known_numbers: list[float]) -> list[float]:
    """The numbers in text that are not known, with the "flexible" rule that classify_run uses."""
    _, _, _, novel_flexible = _has_novel_numeric_variants(text, known_numbers)
    return novel_flexible
