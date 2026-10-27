"""pytest configuration.

`pytest` tests YOUR code in currency_eval/.
`pytest --soluciones` tests the reference solutions in soluciones/currency_eval/ instead.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def pytest_addoption(parser):
    parser.addoption(
        "--soluciones",
        action="store_true",
        help="Run the tests against soluciones/currency_eval instead of currency_eval.",
    )


def pytest_configure(config):
    if config.getoption("--soluciones"):
        # Put soluciones/ first on the import path, so `import currency_eval` finds the solutions.
        sys.path.insert(0, str(ROOT / "soluciones"))


def pytest_report_header(config):
    import currency_eval

    return f"currency_eval loaded from: {Path(currency_eval.__file__).parent}"
