import asyncio
import json
import os

import jsons
import typer
from fastapi.applications import FastAPI, Request
from psycopg_pool import ConnectionPool
from uvicorn import Config, Server

from bot_state import BotStateFactory
from chat_handler import ChatHandler
from custom_codecs import ChatHandlerDecoder, ChatHandlerEncoder
from storage import PostgresStorage
from telegram_client import LiveTelegramClient, TelegramClient, Update
from utils import transform_keywords


def run(
    update: Update,
    client: TelegramClient,
    state_factory: BotStateFactory,
    storage: PostgresStorage,
):
    chat_id = update.chat_id
    chat_handler_snapshot = storage.get_chat_handler(chat_id)
    if chat_handler_snapshot is None:
        chat_handler = ChatHandler.create(state_factory.make_greeting_state(), chat_id)
    else:
        chat_handler = ChatHandlerDecoder(client, state_factory).decode(
            json.loads(chat_handler_snapshot)
        )
    chat_handler.process(update)
    storage.set_chat_handler(chat_id, json.dumps(chat_handler, cls=ChatHandlerEncoder))


def run_server_mode(
    client: TelegramClient, state_factory: BotStateFactory, storage: PostgresStorage
):
    app = FastAPI()

    @app.post("/handleUpdate")
    def handle_update(request: Request):
        payload = asyncio.run(request.json())
        update = jsons.load(payload, cls=Update, key_transformer=transform_keywords)
        run(update, client, state_factory, storage)

    conf = Config(app=app, host="localhost", port=8000, debug=True)

    server = Server(conf)
    server.run()


def run_client_mode(
    client: TelegramClient, state_factory: BotStateFactory, storage: PostgresStorage
):
    offset = 0
    # chat_id -> handler
    while True:
        for update in client.get_updates(offset):
            offset = update.update_id + 1
            run(update, client, state_factory, storage)


def main(
    server: bool = typer.Option(
        False, help="Turn on the bot's `server mode`. Otherwise `client mode` is used."
    ),
    url: str = typer.Option(" ", help="the URL param of the server"),
):
    user = os.environ["POSTGRES_DB_USER"]
    password = os.environ["POSTGRES_DB_PASSWD"]
    host = "localhost"
    dbname = os.environ["POSTGRES_DB_NAME"]
    conninfo = f"postgresql://{user}:{password}@{host}:{5432}/{dbname}"
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    client = LiveTelegramClient(token)
    with ConnectionPool(conninfo) as pool:
        storage = PostgresStorage(pool)
        state_factory = BotStateFactory(client, storage)
        if server:
            client.set_webhook(f"{url}/handleUpdate")
            run_server_mode(client, state_factory, storage)
        else:
            client.delete_webhook()
            run_client_mode(client, state_factory, storage)


if __name__ == "__main__":
    typer.run(main)
