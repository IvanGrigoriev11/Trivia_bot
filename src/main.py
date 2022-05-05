import os
from typing import Dict

from chat_handler import ChatHandler
from telegram_client import LiveTelegramClient


def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    client = LiveTelegramClient(token)

    # chat_id -> handler
    chat_handlers: Dict[int, ChatHandler] = {}
    offset = 0

    while True:
        for update in client.get_updates(offset):
            offset = update.update_id + 1
            if update.message and update.callback_query is None:
                chat_id = update.message.chat.id
            elif update.message is None and update.callback_query:
                chat_id = update.callback_query.from_.id
            else:
                pass

            if chat_id not in chat_handlers:
                chat_handlers[chat_id] = ChatHandler.make_default(client, chat_id)

            chat_handler = chat_handlers[chat_id]
            chat_handler.process(update)


if __name__ == "__main__":
    main()
