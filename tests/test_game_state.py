from typing import List, Tuple, Optional

from form_buttons import form_buttons
from test_chat_handler import QUESTIONS
from tutils import FakeTelegramClient, check_conversation

from bot_state import GameState
from models import Question
from telegram_client import Update, InlineKeyboardMarkup


def check_game_state(conversation: List[Tuple[bool, str, Optional[InlineKeyboardMarkup]]]):
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
            (True, "1.What is the color of sky?\n['orange', 'blue', 'green']", form_buttons(QUESTIONS[0])),
            (False, "1", None),
            (True, "You are right", None),
            (True, "2.How much is 2 + 5?\n['4', '10', '7', '8']", form_buttons(QUESTIONS[1])),
            (False, "1", None),
            (True, "You are wrong", None),
            (
                True,
                "3.What date is Christmas?\n['Dec 24', 'Apr 15', 'Jan 1', 'Dec 25']", form_buttons(QUESTIONS[2])
            ),
            (False, "1", None),
            (True, "You are wrong", None),
            (
                True,
                "You got 1 points out of 3.\nIf you want to try again, type"
                + " /startGame to start a new game.", None
            ),
        ]
    )


def test_gibberish_reply():
    check_game_state(
        [
            (True, "1.What is the color of sky?\n['orange', 'blue', 'green']", form_buttons(QUESTIONS[0])),
            (False, "first", None),
            (True, "Please, type the number of your supposed answer", None),
            (False, "second", None),
            (True, "Please, type the number of your supposed answer", None),
            (False, "1", None),
            (True, "You are right", None),
        ]
    )


def test_enter_inappropriate_number():
    check_game_state(
        [
            (True, "1.What is the color of sky?\n['orange', 'blue', 'green']", form_buttons(QUESTIONS[0])),
            (False, "-1", None),
            (True, "Type the number from 0 to 2", None),
            (False, "3", None),
            (True, "Type the number from 0 to 2", None),
            (False, "2", None),
            (True, "You are wrong", None),
            (True, "2.How much is 2 + 5?\n['4', '10', '7', '8']", form_buttons(QUESTIONS[1])),
        ]
    )
