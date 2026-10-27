"""Where the data files live, and how to read them.

This module is given (not an exercise). Both currency_eval/ and soluciones/currency_eval/
use it, so it finds data/ by walking up from this file instead of assuming a fixed depth.
"""

from pathlib import Path


def _find_data_dir() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "data" / "prompts").is_dir():
            return parent / "data"
    raise FileNotFoundError("Could not find data/prompts/ above " + __file__)


DATA_DIR = _find_data_dir()
PROMPTS_DIR = DATA_DIR / "prompts"


def read_text(path: Path) -> str:
    """Read a UTF-8 text file exactly as written (prompts must stay byte-identical)."""
    return path.read_text(encoding="utf-8")
