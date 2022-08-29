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
		pass
