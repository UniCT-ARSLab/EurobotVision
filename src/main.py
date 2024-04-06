import time
import yaml
import telebot
import threading
from data_collector import capture_and_send

IsCaptureOn = False
StopCapture = False
t = None


def capture_30min():
    global IsCaptureOn
    global StopCapture
    IsCaptureOn = True
    count = 0
    while StopCapture is False:
        count = count + 1
        if count >= 60:
            break
        capture_and_send.capture_image_and_send()
        time.sleep(30)


def capture_until_stop():
    global StopCapture
    global IsCaptureOn
    IsCaptureOn = True
    while StopCapture is False:
        capture_and_send.capture_image_and_send()
        time.sleep(60)


if __name__ == "__main__":
    with open("config/config.yaml", "r") as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)

    api_key = config["apikey"]

    bot = telebot.TeleBot(api_key)

    @bot.message_handler(commands=["30start"])
    def start_30thread(message):
        global StopCapture
        global IsCaptureOn
        global t
        if IsCaptureOn is False:
            StopCapture = False
            t = threading.Thread(target=capture_30min)
            t.start()
            bot.reply_to(message, "started capturing for 30 minutes")
        else:
            bot.reply_to(message, "already started write /stop")

    @bot.message_handler(commands=["StartCapture"])
    def start_capture(message):
        global StopCapture
        global IsCaptureOn
        global t
        if IsCaptureOn is False:
            t = threading.Thread(target=capture_until_stop)
            t.start()
            bot.reply_to(message, "Started always on")
        else:
            bot.reply_to(message, "already started capture write /stop")

    @bot.message_handler(commands=["StopCapture"])
    def stop_capture(message):
        global StopCapture
        global IsCaptureOn
        global t
        if StopCapture is False:
            StopCapture = True
            IsCaptureOn = False
            t.join()
            bot.reply_to(message, "turned off")
        else:
            bot.reply_to(message, "already off")

    @bot.message_handler(commands=["help", "start"])
    def send_hello(message):
        bot.reply_to(message, "hello")


bot.infinity_polling()
