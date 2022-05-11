from typing import List

from test_chat_handler import QUESTIONS
from tutils import FakeTelegramClient, MessageContent, bot, check_conversation, user

from bot_state import GameState
from format import make_keyboard
from models import Question
from telegram_client import CallbackQuery, SendMessagePayload, Update, User


def check_game_state(conversation: List[MessageContent]):
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
                "1.What is the color of sky?",
                make_keyboard(QUESTIONS[0]),
            ),
            user("2"),
            bot("You are right"),
            bot(
                "2.How much is 2 + 5?",
                make_keyboard(QUESTIONS[1]),
            ),
            user("2"),
            bot("You are wrong"),
            bot(
                "3.What date is Christmas?",
                make_keyboard(QUESTIONS[2]),
            ),
            user("2"),
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
                "1.What is the color of sky?",
                make_keyboard(QUESTIONS[0]),
            ),
            user("first"),
            bot("Please, type the number of your supposed answer"),
            bot(
                "1.What is the color of sky?",
                make_keyboard(QUESTIONS[0]),
            ),
            user("second"),
            bot("Please, type the number of your supposed answer"),
            bot(
                "1.What is the color of sky?",
                make_keyboard(QUESTIONS[0]),
            ),
            user("2"),
            bot("You are right"),
        ]
    )


def test_enter_inappropriate_number():
    check_game_state(
        [
            bot(
                "1.What is the color of sky?",
                make_keyboard(QUESTIONS[0]),
            ),
            user("-1"),
            bot("Type the number from 1 to 3"),
            bot(
                "1.What is the color of sky?",
                make_keyboard(QUESTIONS[0]),
            ),
            user("4"),
            bot("Type the number from 1 to 3"),
            bot(
                "1.What is the color of sky?",
                make_keyboard(QUESTIONS[0]),
            ),
            user("3"),
            bot("You are wrong"),
            bot(
                "2.How much is 2 + 5?",
                make_keyboard(QUESTIONS[1]),
            ),
        ]
    )


def check_callback_query(button: str, expected_answer: str):
    client = FakeTelegramClient()
    state = GameState(client, QUESTIONS)
    chat_id = 111
    state.on_enter(chat_id)
    state.process(Update(123, None, CallbackQuery(User(111), f"{button}")))
    assert client.sent_messages == [
        (
            SendMessagePayload(
                111, "1.What is the color of sky?", make_keyboard(QUESTIONS[0])
            )
        ),
        (SendMessagePayload(111, f"{expected_answer}")),
        (SendMessagePayload(111, "2.How much is 2 + 5?", make_keyboard(QUESTIONS[1]))),
    ]


def test_positive_callback_query():
    check_callback_query("2", "You are right")


def test_negative_callback_query():
    check_callback_query("1", "You are wrong")
