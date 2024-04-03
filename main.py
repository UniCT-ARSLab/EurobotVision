import os
import time
import yaml
import telebot
import threading
from DataCollector import capture_and_send
from DataCollector import gdrive


def capture_30min():
    IsCaptureOn = True
    count = 0
    while StopCapture is False:
        count = count + 1
        if count >= 60:
            break
        capture_and_send.capture_image_and_send()
        time.sleep(30)


def capture_until_stop(message):
    bot.reply_to(message, "Started capture")
    while StopCapture is False:
        capture_and_send.capture_image_and_send()
        time.sleep(60)


if __name__ == "__main__":
    IsCaptureOn = False
    StopCapture = False
    with open("./Config/config.yaml", "r") as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)

    api_key = config["apikey"]

    bot = telebot.TeleBot(api_key)

    @bot.message_handler(commands=["30start"])
    def start_30thread(message):
        if IsCaptureOn is False:
            StopCapture = False
            bot.reply_to(message, "started capturing for 30 minutes")
            t = threading.Thread(target=capture_30min)
            t.start()
        else:
            bot.reply_to(message, "already started write /stop")

    @bot.message_handler(commands=["StartCapture"])
    def start_capture(message):
        if IsCaptureOn is False:
            t1 = threading.Thread(target=capture_until_stop, args=(message))
            t1.start()
        else:
            bot.reply_to(message, "already started capture write /stop")

    @bot.message_handler(commands=["StopCapture"])
    def stop_capture(message):
        if StopCapture is False:
            StopCapture = True
            IsCaptureOn = False
            t.stop()
            t1.stop()
            bot.reply_to(message, "turned off")
        else:
            bot.reply_to(message, "already off")

    @bot.message_handler(commands=["help", "start"])
    def send_hello(message):
        bot.reply_to(message, "hello")


bot.infinity_polling()
