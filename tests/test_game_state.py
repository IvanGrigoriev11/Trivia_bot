from typing import List, Optional, Tuple

from test_chat_handler import QUESTIONS
from tutils import (
    ConversationConstructor,
    FakeTelegramClient,
    bot,
    check_conversation,
    user,
)

from bot_state import GameState
from format import make_keyboard
from models import Question
from telegram_client import InlineKeyboardMarkup, Update


def check_game_state(conversation: List[ConversationConstructor]):
    client = FakeTelegramClient()
    chat_id = 111
    state = GameState(client, Question.make_some())
    state.on_enter(chat_id)

    def process(u: Update):
        state.process(u)

    check_conversation(chat_id, conversation, client, process)


def test_game_state():
    check_game_state(
        [
            bot(
                "1.What is the color of sky?\n['orange', 'blue', 'green']",
                make_keyboard(QUESTIONS[0]),
            ),
            user("1"),
            bot("You are right"),
            bot(
                "2.How much is 2 + 5?\n['4', '10', '7', '8']",
                make_keyboard(QUESTIONS[1]),
            ),
            user("1"),
            bot("You are wrong"),
            bot(
                "3.What date is Christmas?\n['Dec 24', 'Apr 15', 'Jan 1', 'Dec 25']",
                make_keyboard(QUESTIONS[2]),
            ),
            user("1"),
            bot("You are wrong"),
            bot(
                "You got 1 points out of 3.\nIf you want to try again, type"
                + " /startGame to start a new game."
            ),
        ]
    )


def test_gibberish_reply():
    check_game_state(
        [
            bot(
                "1.What is the color of sky?\n['orange', 'blue', 'green']",
                make_keyboard(QUESTIONS[0]),
            ),
            user("first"),
            bot("Please, type the number of your supposed answer"),
            user("second"),
            bot("Please, type the number of your supposed answer"),
            user("1"),
            bot("You are right"),
        ]
    )


def test_enter_inappropriate_number():
    check_game_state(
        [
            bot(
                "1.What is the color of sky?\n['orange', 'blue', 'green']",
                make_keyboard(QUESTIONS[0]),
            ),
            user("-1"),
            bot("Type the number from 0 to 2"),
            user("3"),
            bot("Type the number from 0 to 2"),
            user("2"),
            bot("You are wrong"),
            bot(
                "2.How much is 2 + 5?\n['4', '10', '7', '8']",
                make_keyboard(QUESTIONS[1]),
            ),
        ]
    )
