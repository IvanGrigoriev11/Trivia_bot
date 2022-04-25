from typing import List, Tuple

from tutils import FakeTelegramClient, check_conversation

from chat_handler import ChatHandler


def check_chat(conversation: List[Tuple[bool, str]]):
    client = FakeTelegramClient()
    chat_id = 123
    chat_handler = ChatHandler.make_default(client, chat_id)
    check_conversation(chat_id, conversation, client, chat_handler.process)


def test_entire_game():
    check_chat(
     [
         (False, "/startGame"),
         (True, "Starting game!"),
         (True, "1.What is the color of sky?\n['orange', 'blue', 'green']"),
         (False, "2"),
         (True, "You are wrong"),
         (True, "2.How much is 2 + 5?\n['4', '10', '7', '8']"),
         (False, "2"),
         (True, "You are right"),
         (
             True,
             "3.What date is Christmas?\n['Dec 24', 'Apr 15', 'Jan 1', 'Dec 25']",
         ),
         (False, "3"),
         (True, "You are right"),
         (
             True,
             "You got 2 points out of 3.\nIf you want to try again, type"
             + " /startGame to start a new game.",
         ),
         (False, "/startGame"),
         (True, "Starting game!"),
     ]
    )
