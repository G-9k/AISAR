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
        fee = FEE_DATABASE.get(method.lower())
        if fee is not None:
            return json.dumps({"status": "success", "fee_percentage": fee})
        return json.dumps(
            {"status": "error", "error_message": f"Payment method '{method}' not found"}
        )

    return execute


# Exercise 01b
@tool
def get_exchange_rate() -> Tool:
    async def execute(base_currency: str, target_currency: str) -> str:
        """Return the exchange rate between two currencies (ISO 4217 codes).

        Returns {"status": "success", "rate": <float>}
             or {"status": "error", "error_message": <str>}.

        Args:
            base_currency: The base currency code.
            target_currency: The target currency code.
        """
        rate = RATE_DATABASE.get(base_currency.lower(), {}).get(target_currency.lower())
        if rate is not None:
            return json.dumps({"status": "success", "rate": rate})
        return json.dumps(
            {
                "status": "error",
                "error_message": f"Unsupported currency pair: {base_currency}/{target_currency}",
            }
        )

    return execute
