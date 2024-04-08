import yaml
from telebot import TeleBot
from telebot.types import BotCommand, Message
from data_collector.camera_utils import get_camera, get_camera_image
from data_collector.gdrive import upload_photo
from enum import StrEnum
import time
from io import BytesIO
from PIL.Image import Image
import threading


class CaptureStatus(StrEnum):
    NOT_STARTED = "not started"
    RUNNING = "running"


current_status: CaptureStatus = CaptureStatus.NOT_STARTED
capture_thread: threading.Thread | None = None
capture_thread_duration: int = -1


def _peek(message: Message, bot: TeleBot) -> None:
    """
    This function sends the current camera view
    :param message: The message object
    :param bot: The bot object
    """
    peek: Image | None = get_camera_image()
    if peek is not None:
        image_bytes = BytesIO()
        image_bytes.name = 'peek.jpeg'
        peek.save(image_bytes, 'JPEG')
        image_bytes.seek(0)
        bot.send_photo(message.chat.id, photo=image_bytes)
    else:
        bot.send_message(message.chat.id, "Unable to capture image",
                         message_thread_id=message.message_thread_id)


def capture_job(duration: int) -> None:
    """
    This function captures images from the camera every 30 seconds. The process will run for the specified duration.
    If duration is 0, the process will run indefinitely
    """
    global current_status, capture_thread_duration
    internal_counter: int = 0
    endless = duration == 0
    duration = duration * 60
    try:
        while current_status != CaptureStatus.NOT_STARTED:
            if internal_counter == 0:
                image: Image | None = get_camera_image()
                upload_photo(image)
                if not endless:
                    duration -= 30
                    if duration <= 0:
                        print("Capture process finished")
                        current_status = CaptureStatus.NOT_STARTED
                        capture_thread_duration = -1
                        break
            # This module should trigger the capture process every 30 seconds
            internal_counter = (internal_counter + 1) % 60
            time.sleep(0.5)

    except KeyboardInterrupt:
        pass


def _start_capture_process(message: Message, bot: TeleBot) -> None:
    """
    This function starts the capture service for the next 30 minutes

    :param message: The message object
    :param bot: The bot object
    """
    global current_status, capture_thread, capture_thread_duration
    command = message.text.split()
    if len(command) == 1 or not command[1].isdigit():
        bot.reply_to(message, "The command must be in the format:\n/capture [duration in minutes]\nIf 0 the process "
                              "will run indefinitely")
        return
    if current_status != CaptureStatus.NOT_STARTED:
        bot.reply_to(message, "Capture service is already running")
        return
    capture_thread_duration = int(command[1])
    current_status = CaptureStatus.RUNNING
    capture_thread = threading.Thread(target=capture_job, args=(capture_thread_duration,))
    capture_thread.start()
    bot.send_message(message.chat.id, "Capture service started",
                     message_thread_id=message.message_thread_id)


def _stop_capture_service(message: Message, bot: TeleBot) -> None:
    """
    This function stops the capture service

    :param message: The message object
    :param bot: The bot object
    """
    global current_status, capture_thread, capture_thread_duration
    text: str = "Capture service is not started"
    if current_status != CaptureStatus.NOT_STARTED:
        current_status = CaptureStatus.NOT_STARTED
        capture_thread_duration = -1
        text = "Capture service stopped"
    bot.send_message(message.chat.id, text, message_thread_id=message.message_thread_id)


def _get_status(message: Message, bot: TeleBot, ) -> None:
    """
    This function gets the status of the capture

    :param message: The message object
    :param bot: The bot object
    """
    if capture_thread_duration == 0:
        duration = " indefinitely"
    elif capture_thread_duration == -1:
        duration = ""
    else:
        duration = f" for {capture_thread_duration} minutes"
    bot.send_message(message.chat.id, f"Capture status is <b>{current_status}{duration}</b>",
                     message_thread_id=message.message_thread_id)


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
            BotCommand("capture",
                       "Start capturing images process. A duration in minutes must be provided, if 0 the process will run indefinitely."),
            BotCommand("peek", "Get the current camera view")
        ],
    )


def _register_handlers(bot: TeleBot) -> None:
    """
    This function registers the handlers for the bot

    :param bot: The bot object
    """
    bot.message_handler(commands=["start"])(lambda message: bot.send_message(message.chat.id, "Hello!",
                                                                             message_thread_id=message.message_thread_id))
    bot.register_message_handler(_get_status, commands=["status"], pass_bot=True)
    bot.register_message_handler(_stop_capture_service, commands=["stop"], pass_bot=True)
    bot.register_message_handler(_start_capture_process, commands=["capture"], pass_bot=True)
    bot.register_message_handler(_peek, commands=["peek"], pass_bot=True)


def execute_bot() -> None:
    """
    This function executes the bot
    """
    print("Looking for API key...")
    api_key: str | None = _retrieve_api_key()
    if api_key is None:
        print("Error: API key not found")
        return
    print("Looking for camera...")
    if not get_camera():
        print("Error: Camera not found")
        return
    print("Starting bot...")
    bot: TeleBot = TeleBot(api_key, parse_mode="HTML")
    print("Setting commands...")
    _set_commands(bot)
    print("Registering handlers...")
    _register_handlers(bot)
    print("Bot started")
    bot.infinity_polling()


if __name__ == "__main__":
    execute_bot()
