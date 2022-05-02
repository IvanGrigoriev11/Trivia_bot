from typing import List, Tuple, Optional

from tutils import FakeTelegramClient, check_conversation
from form_buttons import form_buttons
from telegram_client import InlineKeyboardMarkup
from chat_handler import ChatHandler


def check_chat(conversation: List[Tuple[bool, str, Optional[InlineKeyboardMarkup]]]):
    client = FakeTelegramClient()
    chat_id = 123
    chat_handler = ChatHandler.make_default(client, chat_id)
    check_conversation(chat_id, conversation, client, chat_handler.process)


def test_entire_game():
    check_chat(
     [
         (False, "/startGame", None),
         (True, "Starting game!", None),
         (True, "1.What is the color of sky?\n['orange', 'blue', 'green']", None),
         (False, "2", None),
         (True, "You are wrong", None),
         (True, "2.How much is 2 + 5?\n['4', '10', '7', '8']", None),
         (False, "2", None),
         (True, "You are right", None),
         (
             True,
             "3.What date is Christmas?\n['Dec 24', 'Apr 15', 'Jan 1', 'Dec 25']", None
         ),
         (False, "3", None),
         (True, "You are right", None),
         (
             True,
             "You got 2 points out of 3.\nIf you want to try again, type"
             + " /startGame to start a new game.", None
         ),
         (False, "/startGame", None),
         (True, "Starting game!", None),
     ]
    )

