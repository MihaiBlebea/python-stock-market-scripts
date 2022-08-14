from __future__ import annotations
from dataclasses import dataclass
import requests
from pathlib import Path
import json
from enum import Enum

from src.amount import Amount

from pprint import pprint


CWD = Path(__file__).parent.resolve()


class Currency(Enum):
	USD = "$"
	GBP = "£"
	EUR = "€"

	def is_dollar(self)-> bool:
		return self.name == "USD"

	def is_pound(self)-> bool:
		return self.name == "GBP"

	def is_euro(self)-> bool:
		return self.name == "EUR"


@dataclass(frozen=True)
class Dividend:

	amount: float

	currency: str

	flag: str

	direction: str

	market: str

	name: str

	prev: float

	share_price: float

	ticker: str

	ex_date: str

	@staticmethod
	def from_response(data: dict)-> Dividend:
		price = float(data["price"][1:].replace(",", ""))
		currency = Currency(data["price"][0])
		
		amount = data["amnt"]

		print(amount)
		d = Dividend(
			amount,
			currency.value,
			data["flag"],
			"up",
			data["mic"],
			data["name"],
			data["prev"],
			price,
			data["ticker"],
			data["xdd"],
		)

		return d


class Scraper:

	base_url = "https://www.dividendmax.com/dividends/declared.json?region="

	regions = [1, 6]

	def fetch_all_regions(self)-> dict:
		res = []
		for r in self.regions:
			data = self.fetch_region(r)
			for d in data:
				div = Dividend.from_response(d)
				pprint(div)

			res += data

		with open(f"{CWD}/../cache.json", "w") as file:
			file.write(json.dumps(res, indent=4, ensure_ascii=False))


	def fetch_region(self, region: int):
		r = requests.get(self.base_url + str(region))
		if r.status_code != 200:
			raise Exception("response status code is not 200")

		payload = r.json()

		return payload

if __name__ == "__main__":
	# s = Scraper()
	# s.fetch_all_regions()
	pprint(Amount.from_market("XTSE", "C$20.08").__dict__)

