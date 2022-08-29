from typing import List
import pandas as pd
from pipeline import (Transformer, artefact_factory)
from datetime import datetime


class MainTransformer(Transformer):

	def to_fmt_date(self, ts: int)-> str:
		return datetime.fromtimestamp(ts / 1e3).strftime("%Y-%m-%d %H:%M")

	@artefact_factory("./artefacts", "earnings", True)
	def transform(self, earnings: List[dict])-> pd.DataFrame:
		data = []
		for e in earnings:
			data += [
				e["symbol"],
				e["info"]["shortName"],
				self.to_fmt_date(e["Earnings Date"])
			]

		return pd.DataFrame(data=data, columns=[
			"ticker", 
			"company", 
			"datetime"
		])