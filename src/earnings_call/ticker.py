from __future__ import annotations
from typing import Callable, List
from abc import ABC, abstractmethod
import yfinance as yf

class Ticker(ABC):

	@abstractmethod
	def get_ticker_news(ticker: str)-> List[dict]:
		news = []
		for n in yf.Ticker(ticker.upper()).news:
			news.append({
				"title": n["title"],
				"link": n["link"],
			})

		return news


if __name__ == "__main__":
	from pprint import pprint
	for n in Ticker.get_ticker_news("AAPL"):
		pprint(n)
