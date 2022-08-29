from typing import List
import pandas as pd
from pipeline import (
	Pipeline, 
	Extractor, 
	Transformer, 
	Loader, 
	cache_factory,
	artefact_factory
)
import yahoo_fin.stock_info as si
from dotenv import dotenv_values
import requests as re
from time import sleep


config = dotenv_values(".env")

def get_sp500()-> List[str]:
	return list(si.tickers_sp500())


class EarningExtractor(Extractor):

	def __init__(self, tickers: List[str])-> None:
		self.tickers = tickers

	# @cache_factory("./cache", "earnings", 10 * 60 * 60)
	def extract(self)-> List[dict]:
		res = []
		for ticker in self.tickers:
			try:
				res += self.extract_one(ticker)
			except Exception as e:
				print(e)
				sleep(10)

		return res

	@cache_factory("./cache", "earnings", 24 * 60 * 60)
	def extract_one(self, ticker: str)-> List[dict]:
		print(ticker)
		return si.get_earnings_history(ticker.upper())


class EarningTransformer(Transformer):

	def last_4_earning_results(self, earnings: List[dict], symbol: str)-> List[float]:
		res = []
		for earning in earnings:
			if earning["ticker"] == symbol and earning["startdatetimetype"] == "TAS":
				res.append(round(earning["epsactual"] - earning["epsestimate"], 2))
				if len(res) == 4:
					return res

	@artefact_factory("./artefacts", "earnings")
	def transform(self, earnings: List[dict])-> pd.DataFrame:
		data = []
		for earning in earnings:
			if earning["startdatetimetype"] == "AMC":
				if earning["epsactual"] is None or earning["epsestimate"] is None:
					continue

				last_earnings = self.last_4_earning_results(earnings, earning["ticker"])
				data.append(
					[
						earning["ticker"], 
						earning["companyshortname"],
						earning["epsestimate"],
						earning["startdatetime"],
						last_earnings[0] if len(last_earnings) > 0 else None,
						last_earnings[1] if len(last_earnings) > 1 else None,
						last_earnings[2] if len(last_earnings) > 2 else None,
						last_earnings[3] if len(last_earnings) > 3 else None,
					]
				)

		return pd.DataFrame(data=data, columns=[
			"ticker", 
			"company", 
			"eps_est",
			"earning_datetime",
			"earning_1",
			"earning_2",
			"earning_3",
			"earning_4",
		])

class TelegramLoader(Loader):

	def _broadcast_message(self, message: str):
		bot_token = config["TELEGRAM_BOT_TOKEN"]
		chat_id = config["TELEGRAM_CHAT_ID"]
		data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
		url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
		r = re.post(url, data=data)
		
		if r.status_code != 200:
			raise Exception("Error while making the request")

		return r.json()

	def load(self, data: pd.DataFrame)-> None:
		for i, row in data.iterrows():
			ticker = row["ticker"]
			datetime = row["earning_datetime"]
			eps_estimate = row["eps_est"]

			self._broadcast_message(
				f"{ticker} will have next earning call on {datetime} with EPS estimate of {eps_estimate}"
			)

			last_earnings = ", ".join(
				[str(row["earning_1"]), str(row["earning_2"]), str(row["earning_3"]), str(row["earning_4"])]
			)
			self._broadcast_message(
				f"{ticker} last earnings: " + last_earnings
			)

if __name__ == "__main__":
	pipe = Pipeline(
		EarningExtractor(get_sp500()),
		EarningTransformer(),
		TelegramLoader()
	)

	pipe.run_once()