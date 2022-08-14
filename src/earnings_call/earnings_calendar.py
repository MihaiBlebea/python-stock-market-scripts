from datetime import datetime
import pytz
from src.earnings_call.utils import (
	get_earnings,
	get_sp500,
	to_datetime,
)
from pprint import pprint

utc=pytz.UTC

def is_next_earning(earning: dict)-> bool:
	return earning["epsestimate"] is not None\
		and earning["epsactual"] is None\
		and to_datetime(earning["startdatetime"]).replace(tzinfo=utc) > datetime.now().replace(tzinfo=utc)


def main():
	universe = get_sp500()
	earnings_list = []
	for ticker in universe:
		earnings = get_earnings(ticker)
		for earning in earnings:
			if is_next_earning(earning):
				earnings_list.append({
					"company": earning["companyshortname"],
					"symbol": earning["ticker"],
					"datetime": earning["startdatetime"],
					"eps_estimate": earning["epsestimate"],
				})
				break

	calendar_list = sorted(
		earnings_list, 
		key=lambda earning: to_datetime(earning["datetime"]),
		reverse=True,
	)

	pprint(calendar_list)


if __name__ == "__main__":
	main()