from typing import List
from pipeline import Extractor, cache_factory
import yfinance as yf
import json
import time


ONE_DAY = 24 * 60 * 60
ONE_YEAR = ONE_DAY * 365


class InfoExtractor(Extractor):

	@cache_factory("./cache/info", "info", ONE_YEAR)
	def extract(self, ticker: str)-> dict:
		return yf.Ticker(ticker).info

class NewsExtractor(Extractor):

	@cache_factory("./cache/news", "news", ONE_DAY)
	def extract(self, ticker: str)-> dict:
		return [
			{
				"title": n["title"],
				"link": n["link"]
			} 
			for n in yf.Ticker(ticker).news
		]


class CalendarExtractor(Extractor):

	def get_now(self)-> int:
		return int(time.time()) * 1000

	def get_after_7_days(self)-> int:
		return self.get_now() + ONE_DAY * 7 * 1000

	def _flatten(self, nested_list: List[List[dict]])-> List[dict]:
		return [item for sublist in nested_list for item in sublist]

	@cache_factory("./cache/calendars", "calendar", ONE_DAY)
	def extract_one(self, ticker: str)-> dict:
		print(f"extracting {ticker}")

		calendar = list(json.loads(
			yf.Ticker(ticker).calendar.to_json()
		).values())

		return [
			dict(event, **{"symbol": ticker})
			for event in calendar
		]

	def extract(self, tickers: List[str])-> dict:
		if isinstance(tickers, list) is False:
			raise Exception("invalid type not list")

		calendar = self._flatten(
			[self.extract_one(t) for t in tickers]
		)
		
		now = self.get_now() 
		one_week = self.get_after_7_days()

		return list(filter(lambda cal: now < cal["Earnings Date"] < one_week , calendar))


class MainExtractor(Extractor):

	def __init__(
		self,
		calendar: CalendarExtractor,
		news: NewsExtractor,
		info: InfoExtractor,
		tickers: List[str])-> None:

		self.news = news
		self.calendar = calendar
		self.info = info
		self.tickers = tickers

	def extract(self)-> List[dict]:
		calendars = self.calendar.extract(self.tickers)

		return [
			{
				"symbol": calendar["symbol"],
				"info": self.info.extract(calendar["symbol"]),
				"calendar": calendar,
				"news": self.news.extract(calendar["symbol"])
			}
			for calendar in calendars
		]


if __name__ == "__main__":
	from pprint import pprint
	s = MainExtractor(
		CalendarExtractor(), 
		NewsExtractor(), 
		InfoExtractor(),
		["BBW"],
	)
	pprint(s.extract())
