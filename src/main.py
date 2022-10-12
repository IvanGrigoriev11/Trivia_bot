import json
import os

from psycopg_pool import ConnectionPool

from bot_state import BotStateFactory
from chat_handler import ChatHandler
from custom_codecs import ChatHandlerDecoder, ChatHandlerEncoder
from storage import PostgresStorage
from telegram_client import LiveTelegramClient


def main():
    user = os.environ["POSTGRES_AWSDB_USER"]
    password = os.environ["POSTGRES_AWSDB_PASSWD"]
    host = os.environ["POSTGRES_AWSDB_HOST"]
    dbname = os.environ["POSTGRES_AWSDB_NAME"]
    conninfo = f"postgresql://{user}:{password}@{host}:{5432}/{dbname}"

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    client = LiveTelegramClient(token)
    with ConnectionPool(conninfo) as pool:
        storage = PostgresStorage(pool)
        state_factory = BotStateFactory(client, storage)
        # chat_id -> handler
        offset = 0
        while True:
            for update in client.get_updates(offset):
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
