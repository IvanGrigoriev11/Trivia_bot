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


class Bot:
    """The bot itself. It handles updates and manages TriviaGame."""

    def __init__(
        self,
        client: TelegramClient,
        state_factory: BotStateFactory,
        storage: PostgresStorage,
    ):
        self.client = client
        self.state_factory = state_factory
        self.storage = storage

    def handle_update(self, update: Update):
        chat_id = update.chat_id
        chat_handler_snapshot = self.storage.get_chat_handler(chat_id)
        if chat_handler_snapshot is None:
            chat_handler = ChatHandler.create(
                self.state_factory.make_greeting_state(), chat_id
            )
        else:
            chat_handler = ChatHandlerDecoder(self.client, self.state_factory).decode(
                json.loads(chat_handler_snapshot)
            )
        chat_handler.process(update)
        self.storage.set_chat_handler(
            chat_id, json.dumps(chat_handler, cls=ChatHandlerEncoder)
        )


def run_server_mode(bot: Bot, host: str, port: int):
    """Launch bot in a server mode."""

    app = FastAPI()

    @app.post("/handleUpdate")
    def handle_update(request: Request):
        payload = asyncio.run(request.json())
        update = jsons.load(payload, cls=Update, key_transformer=transform_keywords)
        bot.handle_update(update)

    conf = Config(app=app, host=host, port=port, debug=True)

    server = Server(conf)
    server.run()


def run_client_mode(bot: Bot):
    """Launch bot in a client mode."""

    offset = 0
    # chat_id -> handler
    while True:
        for update in bot.client.get_updates(offset):
            offset = update.update_id + 1
            bot.handle_update(update)


def main(
    server: bool = typer.Option(
        False, help="Turn on the bot's `server mode`. Otherwise `client mode` is used."
    ),
    url: str = typer.Option(" ", help="the URL param of the server"),
    host: str = typer.Option("localhost", help="server host"),
    port: int = typer.Option(8000, help="server port"),
):
    user = os.environ["POSTGRES_DB_USER"]
    password = os.environ["POSTGRES_DB_PASSWD"]
    db_host = os.environ["POSTGRES_DB_HOST"]
    db_name = os.environ["POSTGRES_DB_NAME"]
    conninfo = f"postgresql://{user}:{password}@{db_host}:{5432}/{db_name}"
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    client = LiveTelegramClient(token)
    with ConnectionPool(conninfo) as pool:
        storage = PostgresStorage(pool)
        state_factory = BotStateFactory(client, storage)
        bot = Bot(client, state_factory, storage)
        if server:
            client.set_webhook(f"{url}/handleUpdate")
            run_server_mode(bot, host, port)
        else:
            client.delete_webhook()
            run_client_mode(bot)


if __name__ == "__main__":
    typer.run(main)
