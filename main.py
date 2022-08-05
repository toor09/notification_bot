import time

import requests
import telegram
from requests.exceptions import ConnectionError, ReadTimeout

from settings import Settings
from utils import prepare_script_environment


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
    session, settings = prepare_script_environment(settings=Settings())
    bot = telegram.Bot(token=settings.TG_BOT_TOKEN)
    dvmn_url = f"{settings.DVMN_API_URL}" \
               f"{settings.DVMN_API_URI_REVIEWS_LONG_POLLING}"
    headers = {
        "Authorization": f"Token {settings.DVMN_API_TOKEN}"
    }
    while True:
        try:
            list_reviews_with_long_polling = session.get(
                url=dvmn_url,
                headers=headers,
            )
            list_reviews_with_long_polling.raise_for_status()
            status = list_reviews_with_long_polling.json().get("status")

            if status == "timeout":
                timestamp_to_request = list_reviews_with_long_polling.json(
                ).get("timestamp_to_request")
                params = {
                    "timestamp": timestamp_to_request,
                }
                list_reviews_with_long_polling = session.get(
                    url=dvmn_url,
                    headers=headers,
                    params=params,
                )
                list_reviews_with_long_polling.raise_for_status()

            if status == "found":
                bot.send_message(
                    chat_id=settings.TG_CHAT_ID,
                    text="Преподаватель проверил работу!"
                )
                last_review = get_list_reviews()["results"][0]
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

        except ReadTimeout as err:
            print(f"Ошибка чтения по тайм-ауту: {err}")

        except ConnectionError as err:
            print(f"Ошибка подключения :( {err}")
            time.sleep(settings.TIMEOUT)


if __name__ == "__main__":
    get_list_reviews_with_long_polling()
