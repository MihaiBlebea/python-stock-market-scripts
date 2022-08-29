class EarningExtractor(Extractor):

	def __init__(self, tickers: List[str])-> None:
		self.tickers = tickers

	# @cache_factory("./cache", "earnings", 10 * 60 * 60)
	def extract(self)-> List[dict]:
		res = []
		for ticker in self.tickers:
			try:
				res += self.extract_one(ticker)
			except Exception as e:
				print(e)
				sleep(10)

		return res

	@cache_factory("./cache", "earnings", 24 * 60 * 60)
	def extract_one(self, ticker: str)-> List[dict]:
		print(ticker)
		return si.get_earnings_history(ticker.upper())
