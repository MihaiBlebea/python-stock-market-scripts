from __future__ import annotations
from typing import Callable, List
from abc import ABC, abstractmethod
import pytz
import yahoo_fin.stock_info as si
from datetime import datetime, timedelta

utc=pytz.UTC

LastEarnings = Callable[[List[dict]], List[dict]]

EarningsGetter = Callable[[str], dict]

IsNextEarning = Callable[[dict], bool]


class Earnings(ABC):

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

	@abstractmethod
	def get_last_earnings(earnings: List[dict], current_index: int)-> List[dict]:
		i = current_index + 1
		max_index = i + 4 if len(earnings) > i + 4 else len(earnings)
		return [ 
			{
				"eps_estimate": earning["epsestimate"],
				"eps_actual": earning["epsactual"],
				"diff": round(earning["epsactual"] - earning["epsestimate"], 2)
			} for earning in earnings[i:max_index] if earning["epsestimate"] is not None and earning["epsactual"] is not None
		]

	@abstractmethod
	def is_earning_call_near(earnings: dict):
		return Earnings.to_datetime(earnings["datetime"]).replace(tzinfo=utc)\
			< datetime.now().replace(tzinfo=utc) + timedelta(days=2)

	@abstractmethod
	def sort_earnings_list(earnings_list: List[dict]):
		sorted(
			earnings_list, 
			key=lambda earning: Earnings.to_datetime(earning["datetime"]),
			reverse=False,
		)

	@abstractmethod
	def get_earnings_list(
		universe: List[str], 
		last_earnings: LastEarnings, 
		earning_getter: EarningsGetter, 
		is_next_earning: IsNextEarning)-> List[dict]:

		earnings_list = []
		for ticker in universe:
			earnings = earning_getter(ticker)
			for i, earning in enumerate(earnings):
				if is_next_earning(earning):
					earnings_list.append({
						"company": earning["companyshortname"],
						"symbol": earning["ticker"],
						"datetime": earning["startdatetime"],
						"eps_estimate": earning["epsestimate"],
						"last_4": last_earnings(earnings, i)
					})
					break

		return earnings_list