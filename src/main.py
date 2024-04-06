import yaml
from telebot import TeleBot
from telebot.types import BotCommand, Message
from enum import StrEnum
import multiprocessing
import time


class CaptureStatus(StrEnum):
    NOT_STARTED = "not started"
    THIRTY_MIN = "capturing for the next 30 minutes"
    UNTIL_STOP = "capturing until stopped"


current_status: CaptureStatus = CaptureStatus.NOT_STARTED
capture_process: multiprocessing.Process | None = None


def _peek(message: Message, bot: TeleBot) -> None:
    """
    This function sends the current camera view
    :param message: The message object
    :param bot: The bot object
    """
    raise NotImplementedError("This function is not implemented yet")


def endless_capture() -> None:
    """
    This function captures images for 30 minutes. It captures an image every 30 seconds
    :return:
    """
    global current_status
    while current_status == CaptureStatus.UNTIL_STOP:
        #capture_image_and_send()
        time.sleep(60)


def _endless_capture_job(message: Message, bot: TeleBot) -> None:
    """
    This function starts the capture service until stopped
    :param message: The message object
    :param bot: The bot object
    """
    global current_status, capture_process
    if current_status != CaptureStatus.NOT_STARTED:
        bot.reply_to(message, "Capture service is already running")
        return
    current_status = CaptureStatus.UNTIL_STOP
    capture_process = multiprocessing.Process(target=endless_capture)
    capture_process.start()
    bot.reply_to(message, "Capture service started until stopped")


def capture_30min() -> None:
    """
    This function captures images for 30 minutes. It captures an image every 30 seconds
    :return:
    """
    global current_status
    count = 0
    while current_status == CaptureStatus.THIRTY_MIN:
        count = count + 1
        if count >= 60:
            break
        #capture_image_and_send()
        time.sleep(30)


def _start_30_minutes_job(message: Message, bot: TeleBot) -> None:
    """
    This function starts the capture service for the next 30 minutes
    :param message: The message object
    :param bot: The bot object
    """
    global current_status, capture_process
    if current_status != CaptureStatus.NOT_STARTED:
        bot.reply_to(message, "Capture service is already running")
        return
    current_status = CaptureStatus.THIRTY_MIN
    capture_process = multiprocessing.Process(target=capture_30min)
    capture_process.start()
    bot.reply_to(message, "Capture service started for the next 30 minutes")


def _stop_capture_service(message: Message, bot: TeleBot) -> None:
    """
    This function stops the capture service
    :param message: The message object
    :param bot: The bot object
    """
    global current_status, capture_process
    text: str = "Capture service is not started"
    if current_status != CaptureStatus.NOT_STARTED:
        current_status = CaptureStatus.NOT_STARTED
        text = "Capture service stopped"
        capture_process.terminate()
    bot.reply_to(message, text)


def _get_status(message: Message, bot: TeleBot, ) -> None:
    """
    This function gets the status of the capture
    :param message: The message object
    :param bot: The bot object
    """
    bot.send_message(message.chat.id, f"Capture status is <b>{current_status}</b>")


def _retrieve_api_key() -> str | None:
    """
    This function retrieves the api key from the config file
    :return: The api key if it exists, None otherwise
    """
    try:
        with open("./config/config.yaml", "r") as config_file:
            config = yaml.safe_load(config_file)
        return config["api_key"]
    except OSError:
        return None


def _set_commands(bot: TeleBot) -> None:
    """
    This function sets the commands for the bot
    :param bot: The bot object
    """

    # Delete previous commands
    bot.delete_my_commands()
    # Register new commands
    bot.set_my_commands(
        commands=[
            BotCommand("start", "If not started, start the bot"),
            BotCommand("status", "Display the current status of the capture"),
            BotCommand("stop", "Stop capturing images"),
            BotCommand("30capture", "Start capturing images for the next 30 minutes"),
            BotCommand("endless_capture", "Start capturing images until stopped"),
            BotCommand("peek", "Get the current camera view")
        ],
    )


def _register_handlers(bot: TeleBot) -> None:
    """
    This function registers the handlers for the bot
    :param bot: The bot object
    """
    bot.message_handler(commands=["start"])(lambda message: bot.send_message(message.chat.id, "Hello!"))
    bot.register_message_handler(_get_status, commands=["status"], pass_bot=True)
    bot.register_message_handler(_stop_capture_service, commands=["stop"], pass_bot=True)
    bot.register_message_handler(_start_30_minutes_job, commands=["30start"], pass_bot=True)
    bot.register_message_handler(_endless_capture_job, commands=["endless_capture"], pass_bot=True)
    bot.register_message_handler(_peek, commands=["peek"], pass_bot=True)


def execute_bot() -> None:
    """
    This function executes the bot
    """
    api_key: str | None = _retrieve_api_key()
    if api_key is None:
        print("Error: API key not found")
        return
    bot: TeleBot = TeleBot(api_key, parse_mode="HTML")
    _set_commands(bot)
    _register_handlers(bot)
    bot.infinity_polling()


if __name__ == "__main__":
    execute_bot()
