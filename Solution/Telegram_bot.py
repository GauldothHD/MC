import json
import requests


class TelegramBot:

    TOKEN = ""
    URL = ""
    CHAT_ID = ""

    def __init__(self):
        self.TOKEN = open('../telegram_token.txt', 'r').read()
        self.URL = "https://api.telegram.org/bot{}/".format(self.TOKEN)
        self.CHAT_ID = self.get_last_chat_id(self.get_updates())

    @staticmethod
    def get_url(url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

    def get_json_from_url(self, url):
        content = self.get_url(url)
        js = json.loads(content)
        return js

    def get_updates(self):
        url = self.URL + "getUpdates"
        js = self.get_json_from_url(url)
        return js

    @staticmethod
    def get_last_chat_id_and_text(updates):
        num_updates = len(updates["result"])
        last_update = num_updates - 1
        text = updates["result"][last_update]["message"]["text"]
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        return text, chat_id

    @staticmethod
    def get_last_chat_id(updates):
        num_updates = len(updates["result"])
        last_update = num_updates - 1
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        return chat_id

    def send_message(self, text):
        url = self.URL + "sendMessage?text={}&chat_id={}".format(text, self.CHAT_ID)
        self.get_url(url)


TB = TelegramBot()
TB.send_message("Bot connection successful.")
