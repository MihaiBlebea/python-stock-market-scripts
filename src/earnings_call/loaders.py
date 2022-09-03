import pandas as pd
from pipeline import Loader
from dotenv import dotenv_values
import requests as re


config = dotenv_values(".env")


class TelegramLoader(Loader):

	def _broadcast_message(self, message: str):
		bot_token = config["TELEGRAM_BOT_TOKEN"]
		chat_id = config["TELEGRAM_CHAT_ID"]
		data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
		url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
		r = re.post(url, data=data)
		
		if r.status_code != 200:
			raise Exception("Error while making the request")

		return r.json()

	def load(self, data: pd.DataFrame)-> None:
		self._broadcast_message("Company earnings call in next 7 days:")
		for i, row in data.iterrows():
			ticker = row["ticker"]
			company = row["company"]
			datetime = row["datetime"]
			self._broadcast_message(f"{company} ({ticker}) on {datetime}")

			news = [
				n for n in [
					row["news_link_1"],
					row["news_link_2"],
					row["news_link_3"],
					row["news_link_4"]
				] if n is not None
			]
			
			self._broadcast_message(f"In the news:")
			for link in news:
				self._broadcast_message(link)
		
