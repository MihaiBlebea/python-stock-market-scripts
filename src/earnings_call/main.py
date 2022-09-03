from typing import List
from pipeline import Pipeline
import yahoo_fin.stock_info as si
from src.earnings_call.extractors import (
	NewsExtractor, 
	InfoExtractor, 
	CalendarExtractor, 
	MainExtractor,
)
from src.earnings_call.transformers import MainTransformer
from src.earnings_call.loaders import TelegramLoader


def get_sp500()-> List[str]:
	return list(si.tickers_sp500())


if __name__ == "__main__":
	# universe = get_sp500() + ["BBW"]
	universe = ["GAMA.L", "SOHO.L"]
	pipe = Pipeline(
		MainExtractor(
			CalendarExtractor(), 
			NewsExtractor(), 
			InfoExtractor(),
			universe,
		),
		MainTransformer(),
		TelegramLoader()
	)

	pipe.run_once()