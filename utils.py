import logging

import requests
import telegram
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from settings import Settings


class TelegramLogsHandler(logging.Handler):
    """Custom telegram handler for logging."""
    def __init__(self, token: str, chat_id: str) -> None:
        super().__init__()
        self.token = token
        self.chat_id = chat_id

    def emit(self, record: logging.LogRecord) -> None:
        tg_bot = telegram.Bot(token=self.token)
        tg_bot.send_message(chat_id=self.chat_id, text=self.format(record))


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
