import asyncio
import json
import os
from dataclasses import dataclass
from typing import Optional

import jsons
import typer
from fastapi import FastAPI, Request
from psycopg_pool import ConnectionPool
from uvicorn import Config, Server

from bot_state import BotStateFactory
from chat_handler import ChatHandler
from custom_codecs import ChatHandlerDecoder, ChatHandlerEncoder
from storage import InMemoryStorage, PostgresStorage, Question, Storage
from telegram_client import LiveTelegramClient, Update
from utils import transform_keywords

run = typer.Typer()


@dataclass
class ServerConfig:
    url: str
    host: str
    port: int
    cert_path: Optional[str]
    key_path: Optional[str]


@dataclass
class Bot:
    """The bot itself. It handles updates and manages TriviaGame."""

    client: LiveTelegramClient
    state_factory: BotStateFactory
    storage: Storage

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

    def run_client_mode(self):
        self.client.delete_webhook()
        offset = 0
        while True:
            for update in self.client.get_updates(offset):
                offset = update.update_id + 1
                self.handle_update(update)

    def run_server_mode(self, conf: ServerConfig):
        self.client.set_webhook(conf.url, conf.cert_path)

        app = FastAPI()

        @app.post("/handleUpdate")
        def handle_update(request: Request):
            payload = asyncio.run(request.json())
            update = jsons.load(payload, cls=Update, key_transformer=transform_keywords)
            self.handle_update(update)

        uvicorn_conf = Config(
            app=app,
            host=conf.host,
            port=conf.port,
            debug=True,
            ssl_keyfile=conf.key_path,
            ssl_certfile=conf.cert_path,
        )
        server = Server(uvicorn_conf)
        server.run()


def config_storage(inmemory: bool, server_conf: Optional[ServerConfig] = None):
    """Assembles the necessary parameters for storage configuration."""

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    client = LiveTelegramClient(token)

    def run_bot(storage: Storage):
        bot = Bot(client, BotStateFactory(client, storage), storage)
        if server_conf:
            bot.run_server_mode(server_conf)
        else:
            bot.run_client_mode()

    if inmemory:
        game_storage = InMemoryStorage(
            [
                Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
                Question("2.How much is 2 + 5?", ["4", "10", "7", "8"], 2),
                Question(
                    "3.What date is Christmas?",
                    ["Dec 24", "Apr 15", "Jan 1", "Dec 25"],
                    3,
                ),
            ]
        )
        run_bot(game_storage)
    else:
        user = os.environ["POSTGRES_DB_USER"]
        password = os.environ["POSTGRES_DB_PASSWD"]
        db_host = os.environ["POSTGRES_DB_HOST"]
        db_name = os.environ["POSTGRES_DB_NAME"]
        conninfo = f"postgresql://{user}:{password}@{db_host}:{5432}/{db_name}"
        with ConnectionPool(conninfo) as pool:
            game_storage = PostgresStorage(pool)
            run_bot(game_storage)


@run.command()
def conf_client(
    inmemory: bool = typer.Option(
        False,
        help="Turn on `InMemory` mode to debug without connection to the database.",
    )
):
    """Configures parameters for client mode."""

    config_storage(inmemory)


@run.command()
def conf_server(
    url: str = typer.Argument(..., help="the URL param of the server"),
    host: str = typer.Argument(..., help="server host"),
    port: int = typer.Argument(..., help="server port"),
    cert_path: Optional[str] = typer.Option(None, help="the certificate path"),
    key_path: Optional[str] = typer.Option(None, help="the key path"),
    inmemory: bool = typer.Option(
        False,
        help="Turn on `InMemory` mode to debug without connection to the database.",
    ),
):  # pylint: disable=too-many-arguments
    """Configures parameters for server mode."""

    config_storage(inmemory, ServerConfig(url, host, port, cert_path, key_path))


if __name__ == "__main__":
    run()
