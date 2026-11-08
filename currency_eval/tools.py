"""Domain tools of the currency agent (exercise 01).

Ported from original_currency_experiment/agents.py:46-93. The databases and the returned dicts are identical to the original. Two differences are forced by Inspect:
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
        #   éxito: {"status": "success", "fee_percentage": {float}}
        #   error: {"status": "error", "error_message": "Payment method '{method}' not found"}
        lmethod = method.lower()

        fee = FEE_DATABASE.get(lmethod,"error")

        if fee == "error":
            result = {"status": "error", "error_message": f"Payment method '{method}' not found"}
        else:
            result = {"status": "success", "fee_percentage": fee}
        
        return json.dumps(result)
            

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
        """Return the exchange rate between two currencies (ISO 4217 codes).

        Returns {"status": "success", "rate": <float>}
             or {"status": "error", "error_message": <str>}.

        Args:
            base_currency: The currency you want to exchange from.
            target_currency: The currency you want to exchange to.
        """

        lbasec_currency = base_currency.lower()
        ltarget_currency = target_currency.lower()

        ex_rate = RATE_DATABASE.get(lbasec_currency,{}).get(ltarget_currency,"error")

        if ex_rate == "error":
            result = {"status": "error", "error_message": f"Unsupported currency pair: {base_currency}/{target_currency}"}
        else:
            result = {"status": "success", "rate": ex_rate}
        
        return json.dumps(result)

    return execute
