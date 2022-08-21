from src.earnings_call.ticker import Ticker
from src.earnings_call.telegram import Telegram
from src.earnings_call.earnings import Earnings


def main():
	earnings_list = Earnings.get_earnings_list(
		Earnings.get_sp500(),
		Earnings.get_last_earnings,
		Earnings.get_earnings,
		Earnings.is_next_earning,
	)
	Earnings.sort_earnings_list(earnings_list)

	Telegram.broadcast_message("Earnings call:\n")
	print(earnings_list[0])

	for e in earnings_list:
		if Earnings.is_earning_call_near(e):
			res = Telegram.send_earnings_report(
				e,
				Ticker.get_ticker_news(e["symbol"]),
				Telegram.broadcast_message,
				Telegram.date_to_string,
			)
			print(res)

if __name__ == "__main__":
	main()