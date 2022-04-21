from typing import List, Tuple

from tutils import FakeTelegramClient

from chat_handler import ChatHandler
from telegram_client import Chat, Message, SendMessagePayload, Update


def check_chat(conversation: List[Tuple[bool, str]]):
    client = FakeTelegramClient()
    chat_id = 123
    chat_handler = ChatHandler.make_default(client, chat_id)
    last_message_from_bot = 0
    update_id = 345
    for bot, message in conversation:
        if bot:
            assert client.sent_messages[last_message_from_bot] == SendMessagePayload(
                chat_id, message
            )
            last_message_from_bot += 1
        else:
            chat_handler.process(Update(update_id, Message(Chat(chat_id), message)))


def test_entire_game():
    check_chat(
        [
            (False, "/startGame"),
            (True, "Starting game!"),
            (True, "1.What is the color of sky?\n['orange', 'blue', 'green']"),
            (False, "1"),
            (True, "You are right"),
            (True, "2.How much is 2 + 5?\n['4', '10', '7', '8']"),
            (False, "1"),
            (True, "You are wrong"),
            (
                True,
                "3.What date is Christmas?\n['Dec 24', 'Apr 15', 'Jan 1', 'Dec 25']",
            ),
            (False, "1"),
            (True, "You are wrong"),
            (
                True,
                "You got 1 points out of 3.\nIf you want to try again, type /startGame to start a new game.",
            ),
            (False, "/startGame"),
            (True, "Starting game!"),
        ]
    )
