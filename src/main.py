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


@dataclass
class ServerConfig:
    """All the necessary settings to start the server."""

    server: bool
    url: str
    host: str
    port: int
    cert_path: Optional[str] = None
    key_path: Optional[str] = None


@dataclass
class Bot:
    """The bot itself. It handles updates and manages TriviaGame."""

    client: LiveTelegramClient
    state_factory: BotStateFactory
    storage: Storage
    server_config: ServerConfig

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


def run_server_mode(bot: Bot):
    """Launch bot in a server mode."""

    app = FastAPI()

    @app.post("/handleUpdate")
    def handle_update(request: Request):
        payload = asyncio.run(request.json())
        update = jsons.load(payload, cls=Update, key_transformer=transform_keywords)
        bot.handle_update(update)

    cf = bot.server_config
    conf = Config(
        app=app,
        host=cf.host,
        port=cf.port,
        debug=True,
        ssl_keyfile=cf.key_path,
        ssl_certfile=cf.cert_path,
    )

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


def config_storage(
    client: LiveTelegramClient, inmemory: bool, server_conf: ServerConfig
):
    """Assembles the necessary parameters for storage configuration."""

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
        run_bot(
            Bot(
                client, BotStateFactory(client, game_storage), game_storage, server_conf
            )
        )
    else:
        user = os.environ["POSTGRES_DB_USER"]
        password = os.environ["POSTGRES_DB_PASSWD"]
        db_host = os.environ["POSTGRES_DB_HOST"]
        db_name = os.environ["POSTGRES_DB_NAME"]
        conninfo = f"postgresql://{user}:{password}@{db_host}:{5432}/{db_name}"
        with ConnectionPool(conninfo) as pool:
            game_storage = PostgresStorage(pool)
            run_bot(
                Bot(
                    client,
                    BotStateFactory(client, game_storage),
                    PostgresStorage(pool),
                    server_conf,
                )
            )


def run_bot(bot: Bot):
    """Сontrols in which mode the bot is launched."""

    if bot.server_config.server:
        if (bot.server_config.cert_path is None) or (
            bot.server_config.key_path is None
        ):
            raise Exception(
                "Blank information about certificate or key location."
                "Please, enter the required information."
            )
        bot.client.set_webhook(bot.server_config.url, bot.server_config.cert_path)
        run_server_mode(bot)
    else:
        bot.client.delete_webhook()
        run_client_mode(bot)


def main(
    server: bool = typer.Option(
        False, help="Turn on the bot's `server mode`. Otherwise `client mode` is used."
    ),
    url: str = typer.Option(" ", help="the URL param of the server"),
    inmemory: bool = typer.Option(
        False,
        help="Turn on `InMemory` mode to debug without connection to the database.",
    ),
    host: str = typer.Option("localhost", help="server host"),
    port: int = typer.Option(8000, help="server port"),
    cert_path: str = typer.Option(None, help="the certificate path"),
    key_path: str = typer.Option(None, help="the key path"),
):  # pylint: disable=too-many-arguments
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    client = LiveTelegramClient(token)
    config_storage(
        client, inmemory, ServerConfig(server, url, host, port, cert_path, key_path)
    )


if __name__ == "__main__":
    typer.run(main)
