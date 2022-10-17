# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /src

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY src/main.py main.py
COPY src/bot_state.py bot_state.py
COPY src/chat_handler.py chat_handler.py
COPY src/custom_codecs.py custom_codecs.py
COPY src/format.py format.py
COPY src/storage.py storage.py
COPY src/telegram_client.py telegram_client.py
COPY src/utils.py utils.py
COPY src/scripts/populate_db.py scripts/populate_db.py
COPY src/scripts/scrap_opentrivia.py scripts/scrap_opentrivia.py

CMD ["python", "main.py"]