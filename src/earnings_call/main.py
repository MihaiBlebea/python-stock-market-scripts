from pandas import DataFrame
from time import sleep
# import numpy as np
# from sklearn.linear_model import LinearRegression
from src.earnings_call.utils import (
	get_ticker_data,
	calc_percentage,
	get_sp500,
	CWD
)


def main():
	# tickers = ["F", "FB", "COLA", "TSLA", "AAPL"]
	tickers = get_sp500()
	
	data = []
	for ticker in tickers:
		try:
			data += get_ticker_data(ticker)
		except:
			print(f"Skipping {ticker}")
			continue

		sleep(2)

	columns = [
		"symbol", 
		"date", 
		"eps_actual", 
		"eps_estimate", 
		"diff", 
		"surprise", 
		"surprise_direction", 
		"price_diff",
		"price_direction"
	]
	df = DataFrame(data=data, columns=columns)

	# df.to_excel(f"{CWD}/../../output.xlsx")

	inputs = list(df.loc[:, "surprise_direction"])
	results = list(df.loc[:, "price_direction"])

	match = 0
	total = 0
	for i, input in enumerate(inputs):
		if input == 0:
			continue

		if input == results[i]:
			match += 1

		total += 1

	print(f"total {total}, match {match}")
	print(f"match {calc_percentage(total, match) }%")


if __name__ == "__main__":
	main()