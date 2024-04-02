import os
import time
import yaml
from threading import Timer

import telegram
from telegram.ext import Updater, CommandHandler


class TelegramBot:
    def __init__(self, api_key):
        self.api_key = api_key
        self.bot = telegram.Bot(api_key)
        self.updater = Updater(token=api_key, use_context=True)

        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", self.start_command))

    def start_command(self, update, context):
        print("Bot started!")
        self.call_function_every_n_seconds()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bot started!")

    def start(self):
        self.updater.start_polling()

    def stop(self):
        self.updater.stop()


if __name__ == "__main__":
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    api_key = config["api_key"]
    bot = TelegramBot(api_key)

    bot.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        bot.stop()
