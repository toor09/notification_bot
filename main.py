import logging
import logging.config
import sys
import time

import telegram
from requests.exceptions import ConnectionError, ReadTimeout

from settings import Settings
from utils import get_session


def get_lesson_reviews() -> None:
    """Get lesson reviews with long polling from dvmn API."""
    settings = Settings()
    session = get_session(settings=settings)
    bot = telegram.Bot(token=settings.TG_BOT_TOKEN)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
        },
        "handlers": {
            "default": {
                "level": settings.LOGGING_LEVEL,
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": sys.stderr,
            },
            "rotating_to_file": {
                "level": settings.LOGGING_LEVEL,
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "standard",
                "filename": "notification_bot.log",
                "maxBytes": 10000,
                "backupCount": 10,
            },
            "telegram_bot": {
                "class": "utils.TelegramLogsHandler",
                "tg_bot": bot,
                "chat_id": settings.TG_CHAT_ID,
                "level": settings.LOGGING_LEVEL,
                "formatter": "standard",
            }
        },
        "loggers": {
            "get_lesson_reviews": {
                "handlers": ["default", "rotating_to_file", "telegram_bot"],
                "level": settings.LOGGING_LEVEL,
                "propagate": True
            }
        }
    }
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger("get_lesson_reviews")

    dvmn_url = f"{settings.DVMN_API_URL}" \
               f"{settings.DVMN_API_URI_REVIEWS_LONG_POLLING}"
    headers = {
        "Authorization": f"Token {settings.DVMN_API_TOKEN}"
    }
    params = None
    logger.debug("Бот уведомлений стартовал...")
    while True:
        try:
            lesson_reviews = session.get(
                url=dvmn_url,
                headers=headers,
                params=params,
                timeout=settings.READ_TIMEOUT,
            )
            lesson_reviews.raise_for_status()
            message = f"{lesson_reviews.request.url=} " \
                      f"{lesson_reviews.status_code=}"
            logger.debug(msg=message)
        except ReadTimeout:
            message = "Тайм-аут по чтению..."
            logger.error(msg=message)
            continue

        except ConnectionError as err:
            message = f"Ошибка подключения :( {err}"
            logger.error(msg=message, exc_info=True)
            time.sleep(settings.TIMEOUT)
            continue

        lesson_reviews = lesson_reviews.json()
        logger.debug(msg=f"{lesson_reviews=}")

        status = lesson_reviews["status"]  # type: ignore

        message = f"{status=}. {params=}"

        if status == "timeout":
            timestamp_to_request = lesson_reviews[
                "timestamp_to_request"
            ]  # type: ignore
            params = {
                "timestamp": timestamp_to_request,
            }

            logger.debug(msg=message)

        if status == "found":
            timestamp_to_request = lesson_reviews[
                "last_attempt_timestamp"
            ]   # type: ignore
            params = {
                "timestamp": timestamp_to_request,
            }
            logger.debug(msg=message)

            last_review = lesson_reviews["new_attempts"][0]  # type: ignore
            negative_result = "К сожалению, в работе нашлись ошибки!"
            positive_result = "Преподавателю все понравилось, можно " \
                              "приступать к следующему уроку!"
            review_result_message = negative_result \
                if last_review["is_negative"] \
                else positive_result
            message = f"У Вас проверили работу " \
                      f"«{last_review['lesson_title']}». " \
                      f"{review_result_message}{last_review['lesson_url']}"
            logger.debug(msg=message)
            try:
                bot.send_message(
                    chat_id=settings.TG_CHAT_ID,
                    text=message
                )
                logger.debug(
                    msg=f"Было отправлено сообщение в чат: `{message}`"
                )
            except telegram.error.NetworkError as err:
                message = f"Что-то пошло не так :( {err}"
                logger.error(msg=message, exc_info=True)


if __name__ == "__main__":
    get_lesson_reviews()
