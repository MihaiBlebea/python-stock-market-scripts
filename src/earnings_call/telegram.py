from ast import Call
from typing import Callable, List
from abc import ABC, abstractmethod
from datetime import datetime
from dotenv import dotenv_values
import requests

config = dotenv_values(".env")

Sender = Callable[[str], dict]

DateFormatter = Callable[[str], str]


class Telegram(ABC):

	@abstractmethod
	def broadcast_message(message: str):
		bot_token = config["TELEGRAM_BOT_TOKEN"]
		chat_id = config["TELEGRAM_CHAT_ID"]
		data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
		url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
		r = requests.post(url, data=data)
		
		if r.status_code != 200:
			raise Exception("Error while making the request")

		return r.json()

	@abstractmethod
	def date_to_string(value: str)-> str:
		dt = datetime.fromisoformat(value[:-1] + "+00:00")
		return dt.strftime("%Y-%m-%d %H:%M")

	@abstractmethod
	def send_earnings_report(
		earning: dict,
		news: List[dict],
		sender: Sender, 
		date_formatter: DateFormatter)-> dict:

		message = f"- {earning['company']} ({earning['symbol']})\n"
		message += f"\t- {date_formatter(earning['datetime'])}\n"
		message += "\t News:"
		for n in news:
			message += f"\t\t- {n['title']} - {n['link']}"
	
		return sender(message)

if __name__ == "__main__":
	print(Telegram.broadcast_message("Hello how are you?"))