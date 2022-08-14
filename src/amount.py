from __future__ import annotations
from currency_converter import CurrencyConverter

class Amount:

	converter = CurrencyConverter()

	def __init__(self, amount: float, currency: str) -> None:
		self.amount = amount
		self.currency = currency

	@staticmethod
	def from_market(market: str, amount: str)-> Amount:
		match market:
			case "XLON":
				amount = amount.replace(",", "")
				if "£" in amount:
					amount = round(float(amount.replace("£", "")) * 100, 2)
					return Amount(amount, "penny")

				if "p" in amount:
					amount = float(amount.replace("p", ""))
					return Amount(amount, "penny")

			case "XNYS":
				if "$" in amount:
					amount = round(float(amount.replace("$", "")) * 100, 2)
					return Amount(amount, "cent")

				if "c" in amount:
					amount = float(amount.replace("c", ""))
					return Amount(amount, "cent")

			case "XTSE":
				if "C$" in amount:
					amount = round(float(amount.replace("C$", "")) * 100, 2)
					return Amount(amount, "canadian cent")

				if "c" in amount:
					amount = float(amount.replace("c", ""))
					return Amount(amount, "canadian cent")
