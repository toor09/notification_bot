import logging
import textwrap

import requests
import telegram
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from settings import Settings


class TelegramLogsHandler(logging.Handler):
    """Custom telegram handler for logging."""
    def __init__(self, tg_bot: telegram.Bot, chat_id: str) -> None:
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record: logging.LogRecord) -> None:
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def correct_textwrap_dedent(multiline_message: str) -> str:
    """Correct textwrap dedent."""
    message = "\n".join(
        [
            textwrap.dedent(line_message)
            for line_message in multiline_message.split("\n")
        ]
    )
    return message


def get_session(
        settings: Settings
) -> requests.Session:
    """Get new request session with retry strategy."""

    retry_strategy = Retry(
        total=settings.RETRY_COUNT,
        status_forcelist=settings.STATUS_FORCE_LIST,
        allowed_methods=settings.ALLOWED_METHODS
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
