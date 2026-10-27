"""Domain tools of the currency agent (exercise 01).

Ported from original_currency_experiment/agents.py:46-93. The databases and the
returned dicts are identical to the original. Two differences are forced by Inspect:
  - Tools return a string, so the dict is serialized with json.dumps().
  - Inspect requires a description for every parameter (ADK sends none).
"""

import json

from inspect_ai.tool import Tool, tool

FEE_DATABASE = {
    "platinum credit card": 0.02,
    "gold debit card": 0.035,
    "bank transfer": 0.01,
}

RATE_DATABASE = {
    "usd": {
        "eur": 0.93,
        "jpy": 157.50,
        "inr": 83.58,
    }
}


# Exercise 01a
@tool
def get_fee_for_payment_method() -> Tool:
    async def execute(method: str) -> str:
        """Return the transaction fee percentage for a payment method.

        Simulates an internal fee database lookup.
        Returns {"status": "success", "fee_percentage": <float>}
             or {"status": "error", "error_message": <str>}.

        Args:
            method: The payment method.
        """
        # TODO: buscá `method` en FEE_DATABASE sin distinguir mayúsculas y devolvé,
        # serializado con json.dumps(), el mismo dict que devuelve agents.py:
        #   éxito: {"status": "success", "fee_percentage": <float>}
        #   error: {"status": "error", "error_message": "Payment method '<method>' not found"}
        raise NotImplementedError("Ejercicio 01a: falta completar get_fee_for_payment_method()")

    return execute


# Exercise 01b
@tool
def get_exchange_rate() -> Tool:
    async def execute(base_currency: str, target_currency: str) -> str:
        # TODO 1: escribí el docstring. La descripción que ve el modelo tiene que ser IDÉNTICA
        #         al docstring de get_exchange_rate en agents.py (copialo), más una sección
        #         Args: que describa cada parámetro (Inspect la exige).
        # TODO 2: buscá la tasa en RATE_DATABASE (sin distinguir mayúsculas) y devolvé con json.dumps():
        #   éxito: {"status": "success", "rate": <float>}
        #   error: {"status": "error", "error_message": "Unsupported currency pair: <BASE>/<TARGET>"}
        #          (BASE y TARGET tal como llegaron, sin pasar a minúsculas)
        raise NotImplementedError("Ejercicio 01b: falta completar get_exchange_rate()")

    return execute
