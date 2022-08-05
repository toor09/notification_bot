# Чат-бот для уведомлений проверки работ на Devman

## Установка чат-бота для уведомлений

- Скачайте код.
- Установите актуальную версию poetry в `UNIX`-подобных дистрибутивах с помощью команды:
```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
```
или в `Windows Powershell`:
```
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -
```
- Добавьте к переменной окружения `$PATH` команду poetry:
```
source $HOME/.poetry/bin
```
- Установите виртуальное окружение в директории с проектом командой:
```
poetry config virtualenvs.in-project true
```
- Установите все зависимости (для установки без dev зависимостей можно добавить аргумент `--no-dev`):
```
poetry install
```
- Активируйте виртуальное окружение командой: 
```
source .venv/bin/activate
```

## Настройка переменных окружения

- Cоздайте файл `.env` в директории проекта, на основе файла `.env.example` командой 
(при необходимости скорректируйте значения переменных окружения):
```
cp .env.example .env
```
<details>
  <summary>Переменные окружения</summary>
  <pre>
    DVMN_API_TOKEN=
    DVMN_API_URL=https://dvmn.org
    DVMN_API_URI_REVIEWS=/api/user_reviews/
    DVMN_API_URI_REVIEWS_LONG_POLLING=/api/long_polling/
    TIMEOUT=90
    RETRY_COUNT=5
    STATUS_FORCE_LIST=429,500,502,503,504
    ALLOWED_METHODS=HEAD,GET,OPTIONS
  </pre>
</details>

## Запуск линтеров

```
isort . && flake8 . && mypy .
```

## Цели проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [Devman](https://dvmn.org).
