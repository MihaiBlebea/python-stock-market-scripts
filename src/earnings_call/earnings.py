from typing import Callable
from abc import ABC, abstractmethod
import pytz
import yahoo_fin.stock_info as si
from datetime import datetime

utc=pytz.UTC


class Earnings:

	@abstractmethod
	def get_sp500():
		return list(si.tickers_sp500())

	@abstractmethod
	def to_datetime(value: str)-> datetime:
		return datetime.fromisoformat(value[:-1] + "+00:00")

	@abstractmethod
	def is_next_earning(earning: dict)-> bool:
		return earning["epsestimate"] is not None\
			and earning["epsactual"] is None\
			and Earnings.to_datetime(earning["startdatetime"]).replace(tzinfo=utc) > datetime.now().replace(tzinfo=utc)

	@abstractmethod
	def get_earnings(symbol: str)-> dict:
		return si.get_earnings_history(symbol.upper())