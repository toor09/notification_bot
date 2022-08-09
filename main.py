import time

import requests
import telegram
from requests.exceptions import ConnectionError

from settings import Settings
from utils import get_session


def get_list_reviews() -> dict:
    """Get list reviews from dvmn API."""
    settings = Settings()
    dvmn_url = f"{settings.DVMN_API_URL}{settings.DVMN_API_URI_REVIEWS}"
    headers = {
        "Authorization": f"Token {settings.DVMN_API_TOKEN}"
    }
    list_reviews = requests.get(url=dvmn_url, headers=headers)
    list_reviews.raise_for_status()
    return list_reviews.json()


def get_list_reviews_with_long_polling() -> None:
    """Get list reviews with long polling from dvmn API."""
    settings = Settings()
    session = get_session(settings=settings)
    bot = telegram.Bot(token=settings.TG_BOT_TOKEN)
    dvmn_url = f"{settings.DVMN_API_URL}" \
               f"{settings.DVMN_API_URI_REVIEWS_LONG_POLLING}"
    headers = {
        "Authorization": f"Token {settings.DVMN_API_TOKEN}"
    }
    while True:
        try:
            list_reviews = session.get(
                url=dvmn_url,
                headers=headers,
                timeout=settings.READ_TIMEOUT,
            )
            list_reviews.raise_for_status()
            list_reviews = list_reviews.json()
            status = list_reviews["status"]  # type: ignore
            timestamp_to_request = list_reviews[
                "timestamp_to_request"
            ]  # type: ignore
            params = {
                "timestamp": timestamp_to_request,
            }
            if status == "timeout":
                session.get(
                    url=dvmn_url,
                    headers=headers,
                    params=params,
                    timeout=settings.READ_TIMEOUT,
                )
            if status == "found":
                session.get(
                    url=dvmn_url,
                    headers=headers,
                    params=params,
                    timeout=settings.READ_TIMEOUT,
                )
                last_review = list_reviews["new_attempts"][0]  # type: ignore
                negative_result = "К сожалению, в работе нашлись ошибки!"
                positive_result = """Преподавателю все понравилось, можно
                                приступать к следующему уроку!
                """
                review_result_message = negative_result \
                    if last_review["is_negative"] \
                    else positive_result
                message = f"""У Вас проверили работу
                        «{last_review["lesson_title"]}».
                        {review_result_message}
                        {last_review["lesson_url"]}
                """
                bot.send_message(
                    chat_id=settings.TG_CHAT_ID,
                    text=message
                )

        except telegram.error.NetworkError as err:
            print(f"Что-то пошло не так :( {err}")

        except ConnectionError as err:
            print(f"Ошибка подключения :( {err}")
            time.sleep(settings.TIMEOUT)


if __name__ == "__main__":
    get_list_reviews_with_long_polling()
