import os
from typing import Dict

from psycopg_pool import ConnectionPool

from bot_state import BotStateFactory
from chat_handler import ChatHandler
from custom_codecs import ChatHandlerDecoder, ChatHandlerEncoder
from storage import PostgresQuestionStorage, HandlerStorage
import json
from telegram_client import LiveTelegramClient


def main():
    user = os.environ["TRIVIA_POSTGRES_USER"]
    password = os.environ["TRIVIA_POSTGRES_PASSWD"]
    host = "localhost"
    dbname = "postgres"
    port = 5432
    conninfo = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    client = LiveTelegramClient(token)
    with ConnectionPool(conninfo) as pool:
        state_factory = BotStateFactory(client, storage=PostgresQuestionStorage(pool))
        # chat_id -> handler
        offset = 0
        while True:
            for update in client.get_updates(offset):
                offset = update.update_id + 1
                chat_id = update.chat_id
                handler_storage = HandlerStorage(pool, chat_id)
                chat_handler_snapshot = handler_storage.get_records(1)
                if chat_handler_snapshot is None:
                    chat_handler = ChatHandler.create(
                        state_factory.make_greeting_state(), chat_id
                    )
                else:
                    chat_handler = json.loads(
                        chat_handler_snapshot, object_hook=ChatHandlerDecoder(client, state_factory).form_chat_handler
                        )
                chat_handler.process(update)
                handler_storage.store(json.dumps(chat_handler, cls=ChatHandlerEncoder))


if __name__ == "__main__":
    main()
