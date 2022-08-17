from typing import List
from datetime import datetime, timedelta
from pathlib import Path
import yahoo_fin.stock_info as si
import json
import requests

CWD = Path(__file__).parent.resolve()

def cache_factory(file_prefix):
	def cache(func):
		def wrapper(*args, **kwargs):
			file_sufix = "_".join([str(argv) for argv in args])

			Path(f"{CWD}/../../cache").mkdir(parents=True, exist_ok=True)
			cache_file_path = Path(f"{CWD}/../../cache/{file_prefix}_{file_sufix}.json")
			if cache_file_path.is_file():
				with open(cache_file_path, "r") as file:
					return json.loads(file.read())

			result = func(*args, **kwargs)

			with open(cache_file_path, "w") as file:
				file.write(json.dumps(result, indent=4, ensure_ascii=False))

			return result
		return wrapper
	return cache

def to_datetime(value: str)-> datetime:
	return datetime.fromisoformat(value[:-1] + "+00:00")

def to_format(value: datetime)-> str:
	return value.strftime("%Y-%m-%d")

def to_datetime_format(value: datetime)-> str:
	return value.strftime("%Y-%m-%d %H:%M")

def modify_date(date: str, modify: int)-> datetime:
	return to_datetime(date) + timedelta(days=modify)

@cache_factory("prices")
def fetch_prices(symbol: str, start_date: str, end_date: str) -> List[dict]:
	start_date = to_datetime(start_date).timestamp
	end_date = to_datetime(end_date).timestamp
	url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&period1={start_date}&period2={end_date}"

	res = requests.get(
		url, 
		headers={"User-agent": "Mozilla/5.0"}
	)
	
	if res.status_code != 200:
		raise Exception(f"response to request is not status 200, instead {res.status_code}")

	body = res.json()

	timestamps = body["chart"]["result"][0]["timestamp"]
	quote = body["chart"]["result"][0]["indicators"]["quote"][0]

	results = []
	for i, t in enumerate(timestamps):
		results.append({
			"open": quote["open"][i],
			"close": quote["close"][i],
			"high": quote["high"][i],
			"low": quote["low"][i],
			"volume": quote["volume"][i],
			"timestamp": t
		})

	return results

@cache_factory("earnings")
def get_earnings(ticker: str)-> list:
	return si.get_earnings_history(ticker.upper())

def get_start_end_prices(ticker: str, earnings_date: str)-> tuple[float, float]:
	prices: List[Quote] = fetch_prices(
		ticker.upper(), 
		earnings_date, 
		earnings_date,
	)

	return (prices[0]["open"], prices[0]["close"],)

def get_ticker_data(ticker: str)-> list:
	ticker = ticker.upper()
	earnings = get_earnings(ticker)

	data = []
	for h in earnings[-8:]:
		actual = h["epsactual"]
		estimate = h["epsestimate"]
		surprise = h["epssurprisepct"]

		if actual is None or estimate is None or surprise is None:
			continue

		diff = actual - estimate
		if diff > 0:
			surprise_direction = 1
		elif diff < 0:
			surprise_direction = -1
		else:
			surprise_direction = 0

		date = h["startdatetime"]

		(start_price, end_price) = get_start_end_prices(ticker, date)
		price_diff = round(end_price - start_price, 2)

		if price_diff > 0:
			price_direction = 1
		elif price_diff < 0:
			price_direction = -1
		else:
			price_direction = 0

		data.append([
			ticker,
			date,
			actual,
			estimate,
			diff,
			surprise,
			surprise_direction,
			price_diff,
			price_direction
		])

	return data

def calc_percentage(x: int | float, y: int | float)-> float:
	"""What percent of X is Y?"""
	return round(y / x * 100, 2)

def get_sp500()-> list:
	return list(si.tickers_sp500())

if __name__ == "__main__":
	# tickers = get_sp500()
	# print(tickers)
	fetch_prices("aapl", 1660744578, 1660744578)