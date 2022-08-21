from datetime import datetime, timedelta
import pytz
from src.earnings_call.utils import (
	get_earnings,
	get_sp500,
	to_datetime,
	modify_date,
	to_datetime_format
)
from pprint import pprint
from src.earnings_call.telegram import Telegram
from src.earnings_call.earnings import Earnings

# utc=pytz.UTC

# def is_next_earning(earning: dict)-> bool:
# 	return earning["epsestimate"] is not None\
# 		and earning["epsactual"] is None\
# 		and to_datetime(earning["startdatetime"]).replace(tzinfo=utc) > datetime.now().replace(tzinfo=utc)

def get_last_earnings(earnings: list, current_index: int)-> list:
	i = current_index + 1
	max_index = i + 4 if len(earnings) > i + 4 else len(earnings)
	return [ 
		{
			"eps_estimate": earning["epsestimate"],
			"eps_actual": earning["epsactual"],
			"diff": round(earning["epsactual"] - earning["epsestimate"], 2)
		} for earning in earnings[i:max_index] if earning["epsestimate"] is not None and earning["epsactual"] is not None
	]

def main():
	universe = Earnings.get_sp500()
	earnings_list = []
	for ticker in universe:
		print(ticker)
		earnings = Earnings.get_earnings(ticker)
		for i, earning in enumerate(earnings):
			if Earnings.is_next_earning(earning):
				earnings_list.append({
					"company": earning["companyshortname"],
					"symbol": earning["ticker"],
					"datetime": earning["startdatetime"],
					"eps_estimate": earning["epsestimate"],
					"last_4": get_last_earnings(earnings, i)
				})
				break

	calendar_list = sorted(
		earnings_list, 
		key=lambda earning: to_datetime(earning["datetime"]),
		reverse=False,
	)

	Telegram.broadcast_message("Earnings call:\n")
	print(earnings_list[0])

	for e in earnings_list:
		message = ""
		if to_datetime(e["datetime"]).replace(tzinfo=utc) < datetime.now().replace(tzinfo=utc) + timedelta(days=2):
			res = Telegram.send_earnings_report(
				e,
				Telegram.broadcast_message,
				Telegram.date_to_string,
			)
			print(res)

if __name__ == "__main__":
	main()