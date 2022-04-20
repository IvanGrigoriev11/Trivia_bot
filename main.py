from typing import Dict
import os
from telegram_client import LiveTelegramClient
from chat_handler import ChatHandler


def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    client = LiveTelegramClient(token)

    # chat_id -> handler
    chat_handlers: Dict[int, ChatHandler] = {}
    offset = 0

    while True:
        for update in client.get_updates(offset):
            offset = update.update_id + 1
            chat_id = update.message.chat.id
            if chat_id not in chat_handlers:
                chat_handler = ChatHandler.default_for_chat(client, chat_id)
                chat_handlers[chat_id] = chat_handler

            chat_handler = chat_handlers[chat_id]
            chat_handler.process(update)


if __name__ == "__main__":
    main()
