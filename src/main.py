import os
from typing import Dict

from bot_state import BotStateFactory
from chat_handler import ChatHandler
from question_storage import PostgresQuestionStorage
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
    with PostgresQuestionStorage(conninfo) as storage:
        state_factory = BotStateFactory(client, storage)

        # chat_id -> handler
        chat_handlers: Dict[int, ChatHandler] = {}
        offset = 0

        while True:
            for update in client.get_updates(offset):
                offset = update.update_id + 1
                chat_id = update.chat_id

                if chat_id not in chat_handlers:
                    chat_handlers[chat_id] = ChatHandler.create(
                        state_factory.make_greeting_state(), chat_id
                    )

                chat_handler = chat_handlers[chat_id]
                chat_handler.process(update)


if __name__ == "__main__":
    main()
