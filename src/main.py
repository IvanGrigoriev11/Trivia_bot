import json
import os

from fastapi import FastAPI, Depends
from psycopg_pool import ConnectionPool

import telegram_client
from bot_state import BotStateFactory
from chat_handler import ChatHandler
from custom_codecs import ChatHandlerDecoder, ChatHandlerEncoder
from storage import PostgresStorage
from telegram_client import LiveTelegramClient
import typer


app = FastAPI(dependencies=[Depends(LiveTelegramClient.set_webhook)])


def main(
    server: bool = typer.Option(False, help="Turn on the bot's `server mode`. Otherwise `client mode` is used."),
    url: str = typer.Option(" ", help="the URL param of the server"),
):
    user = os.environ["POSTGRES_DB_USER"]
    password = os.environ["POSTGRES_DB_PASSWD"]
    host = 'localhost'
    dbname = os.environ["POSTGRES_DB_NAME"]
    conninfo = f"postgresql://{user}:{password}@{host}:{5432}/{dbname}"

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    client = LiveTelegramClient(token)
    with ConnectionPool(conninfo) as pool:
        storage = PostgresStorage(pool)
        state_factory = BotStateFactory(client, storage)
        # chat_id -> handler
        offset = 0
        while True:
            if server is True:
                updates = client.set_webhook(url)
            else:
                client.delete_webhook(url)
                updates = client.get_updates(offset)
            for update in updates:
                offset = update.update_id + 1
                chat_id = update.chat_id
                chat_handler_snapshot = storage.get_chat_handler(chat_id)
                if chat_handler_snapshot is None:
                    chat_handler = ChatHandler.create(
                        state_factory.make_greeting_state(), chat_id
                    )
                else:
                    chat_handler = ChatHandlerDecoder(client, state_factory).decode(
                        json.loads(chat_handler_snapshot)
                    )
                chat_handler.process(update)
                storage.set_chat_handler(
                    chat_id, json.dumps(chat_handler, cls=ChatHandlerEncoder)
                )


if __name__ == "__main__":
    main()
