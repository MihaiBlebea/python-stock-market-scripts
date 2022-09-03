from typing import List
import pandas as pd
from pipeline import (Transformer, artefact_factory)
from datetime import datetime


class MainTransformer(Transformer):

	def to_fmt_date(self, ts: int)-> str:
		return datetime.fromtimestamp(ts / 1e3).strftime("%Y-%m-%d %H:%M")

	def if_news_link_exists(self, news: List[dict], index: int)-> str | None:
		return news[index]["link"] if len(news) > index else None

	@artefact_factory("./artefacts", "earnings", True)
	def transform(self, earnings: List[dict])-> pd.DataFrame:
		data = []
		for e in earnings:
			data.append([
				e["symbol"],
				e["info"]["shortName"],
				self.to_fmt_date(e["calendar"]["Earnings Date"]),
				self.if_news_link_exists(e["news"], 0),
				self.if_news_link_exists(e["news"], 1),
				self.if_news_link_exists(e["news"], 2),
				self.if_news_link_exists(e["news"], 3),
			])

		return pd.DataFrame(data=data, columns=[
			"ticker", 
			"company", 
			"datetime",
			"news_link_1",
			"news_link_2",
			"news_link_3",
			"news_link_4"
		])