from typing import List, Optional, Tuple

from tutils import FakeTelegramClient, bot, check_conversation, user, ConversationConstructor

from chat_handler import ChatHandler
from format import make_keyboard
from models import Question
from telegram_client import InlineKeyboardMarkup

QUESTIONS = [
    Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
    Question("2.How much is 2 + 5?", ["4", "10", "7", "8"], 2),
    Question("3.What date is Christmas?", ["Dec 24", "Apr 15", "Jan 1", "Dec 25"], 3),
]


def check_chat(conversation: List[ConversationConstructor]):
    client = FakeTelegramClient()
    chat_id = 123
    chat_handler = ChatHandler.make_default(client, chat_id)
    check_conversation(chat_id, conversation, client, chat_handler.process)


def test_entire_game():
    check_chat(
        [
            user("/startGame"),
            bot("Starting game!"),
            bot(
                "1.What is the color of sky?\n['orange', 'blue', 'green']",
                make_keyboard(QUESTIONS[0]),
            ),
            user("0"),
            bot("You are wrong"),
            bot(
                "2.How much is 2 + 5?\n['4', '10', '7', '8']",
                make_keyboard(QUESTIONS[1]),
            ),
            user("2"),
            bot("You are right"),
            bot(
                "3.What date is Christmas?\n['Dec 24', 'Apr 15', 'Jan 1', 'Dec 25']",
                make_keyboard(QUESTIONS[2]),
            ),
            user("3"),
            bot("You are right"),
            bot(
                "You got 2 points out of 3.\nIf you want to try again, type"
                + " /startGame to start a new game."
            ),
            user("/startGame"),
            bot("Starting game!"),
        ]
    )
