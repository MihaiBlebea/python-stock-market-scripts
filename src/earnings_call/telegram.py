from dotenv import dotenv_values
import requests

config = dotenv_values(".env")

def broadcast_message(message: str):
	bot_token = config["TELEGRAM_BOT_TOKEN"]
	chat_id = config["TELEGRAM_CHAT_ID"]
	data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
	url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
	r = requests.post(url, data=data)
	
	if r.status_code != 200:
		return None

	return r.json()

if __name__ == "__main__":
	broadcast_message("Hello how are you?")