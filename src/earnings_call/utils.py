from datetime import datetime, timedelta
from pathlib import Path
import yahoo_fin.stock_info as si
from yahoofinancials import YahooFinancials
import json

CWD = Path(__file__).parent.resolve()

def cache_factory(file_prefix):
	def cache(func):
		def wrapper(*args, **kwargs):
			file_sufix = "_".join(args)

			Path(f"{CWD}/../../cache").mkdir(parents=True, exist_ok=True)
			cache_file_path = Path(f"{CWD}/../../cache/{file_prefix}_{file_sufix}.json")
			if cache_file_path.is_file():
				with open(cache_file_path, "r") as file:
					# print(f"getting from cache {cache_file_path}")
					return json.loads(file.read())

			result = func(*args, **kwargs)

			with open(cache_file_path, "w") as file:
				file.write(json.dumps(result, indent=4, ensure_ascii=False))

			# print("getting from web")
			return result
		return wrapper
	return cache

def to_datetime(value: str)-> datetime:
	return datetime.fromisoformat(value[:-1] + "+00:00")

def to_format(value: datetime)-> str:
	return value.strftime("%Y-%m-%d")

def modify_date(date: str, modify: int)-> datetime:
	return to_datetime(date) + timedelta(days=modify)

@cache_factory("prices")
def get_prices(ticker: str, earnings_date: str)-> list:
	yf = YahooFinancials(ticker)
	start_date = to_format(modify_date(earnings_date, -30))
	end_date = to_format(modify_date(earnings_date, 2))
	prices = yf.get_historical_price_data(
		start_date,
		end_date,
		"daily",
	)
	return list(prices.values())[0]["prices"]

@cache_factory("earnings")
def get_earnings(ticker: str)-> list:
	return si.get_earnings_history(ticker)

def get_start_end_prices(ticker: str, earnings_date: str)-> tuple[float, float]:
	prices = get_prices(ticker, earnings_date)
	
	return (
		get_avr_price(prices[0]["low"], prices[0]["high"]), 
		get_avr_price(prices[-1]["low"], prices[-1]["high"]),
	)

def get_avr_price(start_price: float, end_price: float)-> float:
	"""Get average price between 2 prices"""
	return round(start_price + end_price / 2, 2)

def get_ticker_data(ticker: str)-> list:
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
	tickers = get_sp500()
	print(tickers)