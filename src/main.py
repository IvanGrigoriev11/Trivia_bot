import asyncio
import json
import logging
import os
from dataclasses import dataclass
from typing import Optional

import jsons
import typer
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from psycopg_pool import AsyncConnectionPool
from uvicorn import Config, Server

from bot_state import BotStateFactory
from chat_handler import ChatHandler
from custom_codecs import ChatHandlerDecoder, ChatHandlerEncoder
from storage import InMemoryStorage, PostgresStorage, Question, Storage
from telegram_client import (
    LiveTelegramClient,
    NetworkException,
    TelegramException,
    UnexpectedStatusCodeException,
    UnknownErrorException,
    Update,
)
from utils import transform_keywords


@dataclass
class ServerConfig:
    """Necessary parameters to configure the server."""

    url: str
    host: str
    port: int
    cert_path: Optional[str] = None
    key_path: Optional[str] = None


@dataclass
class Bot:
    """The bot itself. It handles updates and manages TriviaGame."""

    telegram_client: LiveTelegramClient
    state_factory: BotStateFactory
    storage: Storage

    async def handle_update(self, update: Update):
        chat_id = update.chat_id

        if update.my_chat_member is None:
            chat_handler_snapshot = await self.storage.get_chat_handler(chat_id)
            if chat_handler_snapshot is None:
                chat_handler = await ChatHandler.create(
                    await self.state_factory.make_greeting_state(), chat_id
                )
            else:
                chat_handler = ChatHandlerDecoder(
                    self.telegram_client, self.state_factory
                ).decode(json.loads(chat_handler_snapshot))
            await chat_handler.process(update)
            await self.storage.set_chat_handler(
                chat_id, json.dumps(chat_handler, cls=ChatHandlerEncoder)
            )
        elif update.my_chat_member.new_chat_member.status == "member":
            logging.warning("The bot was unblocked by user: %s", chat_id)
        elif update.my_chat_member.new_chat_member.status == "kicked":
            logging.warning("The bot was blocked by user: %s", chat_id)
            await self.storage.del_chat_handler(chat_id)

    async def run_client_mode(self):
        self.telegram_client.delete_webhook()
        offset = 0
        while True:
            try:
                result = await self.telegram_client.get_updates(offset)
            except TelegramException as e:
                logging.error(e)
                continue

            for update in result:
                try:
                    await self.handle_update(update)
                except Exception as e:
                    logging.error(e)
                finally:
                    offset = update.update_id + 1

    async def run_server_mode(self, conf: ServerConfig):
        self.telegram_client.set_webhook(conf.url, conf.cert_path)
        app = FastAPI()

        @app.post("/handleUpdate")
        async def handle_update(request: Request):
            def _filter_payload(payload):
                if "channel_post" in payload:
                    logging.warning(
                        "The message is not processable due to invalid format: %s",
                        payload,
                    )
                    return None

                return payload

            filtered_payload = _filter_payload(await request.json())

            try:
                update = jsons.load(
                    filtered_payload, cls=Update, key_transformer=transform_keywords
                )
            except jsons.DeserializationError as e:
                raise UnknownErrorException(
                    "Failed to deserialize Telegram request"
                ) from e
            await self.handle_update(update)

        @app.exception_handler(TelegramException)
        async def telegram_exception_handler(_request: Request, exc: TelegramException):
            logging.error(exc)
            if isinstance(exc, UnexpectedStatusCodeException):
                if 400 <= exc.status_code <= 500:
                    return PlainTextResponse(
                        status_code=500, content="Internal server error"
                    )

                if 500 < exc.status_code:
                    return PlainTextResponse(status_code=502, content="Bad gateway")

                return PlainTextResponse(
                    status_code=500, content="Internal server error"
                )

            if isinstance(exc, NetworkException):
                return PlainTextResponse(
                    status_code=500, content="Internal server error"
                )

            return PlainTextResponse(status_code=500, content="Internal server error")

        uvicorn_conf = Config(
            app=app,
            host=conf.host,
            port=conf.port,
            debug=True,
            ssl_keyfile=conf.key_path,
            ssl_certfile=conf.cert_path,
        )
        await Server(uvicorn_conf).serve()


async def launch_bot(inmemory: bool, server_conf: Optional[ServerConfig] = None):
    """Launches of a specific mode depends on the assembled storage configuration.
    The storage configuration build process, in turn,
    depends on the presence of a server configuration parameter."""

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    telegram_client = LiveTelegramClient(token)

    async def run_bot(storage: Storage):
        bot = Bot(telegram_client, BotStateFactory(telegram_client, storage), storage)
        if server_conf:
            await bot.run_server_mode(server_conf)
        else:
            await bot.run_client_mode()

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
        await run_bot(game_storage)
    else:
        user = os.environ["POSTGRES_DB_USER"]
        password = os.environ["POSTGRES_DB_PASSWD"]
        db_host = os.environ["POSTGRES_DB_HOST"]
        db_name = os.environ["POSTGRES_DB_NAME"]
        conninfo = f"postgresql://{user}:{password}@{db_host}:{5432}/{db_name}"
        async with AsyncConnectionPool(conninfo) as pool:
            game_storage = PostgresStorage(pool)
            await run_bot(game_storage)


run = typer.Typer()


@run.command()
def client(
    inmemory: bool = typer.Option(
        False,
        help="Turn on `InMemory` mode to debug without connection to the database.",
    )
):
    """Configures parameters for client mode."""

    asyncio.run(launch_bot(inmemory))


@run.command()
def server(
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

    asyncio.run(
        launch_bot(inmemory, ServerConfig(url, host, port, cert_path, key_path))
    )


if __name__ == "__main__":
    run()
