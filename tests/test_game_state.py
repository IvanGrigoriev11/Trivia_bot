from typing import List

from utils import FakeTelegramClient

from bot_state import GameState
from models import Question
from telegram_client import Chat, Message, SendMessagePayload, TelegramClient, Update


def check_game_state(
    last_question: bool, user_message: str, expected_messages: List[str]
):
    client = FakeTelegramClient()
    if not last_question:
        questions = [
            Question("question 1", ["a", "b", "c"], 0),
            Question("question 2", ["a", "b", "c"], 1),
        ]
    else:
        questions = [Question("question 3", ["a", "b", "c"], 2)]
    state = GameState(client, questions)
    chat_id = 111
    state.on_enter(chat_id)
    state.process(Update(123, Message(Chat(chat_id), user_message)))

    expected_payloads = [
        SendMessagePayload(chat_id, text) for text in expected_messages
    ]

    assert client.sent_messages == expected_payloads


def test_end_game_score_1_of_1():
    check_game_state(
        True,
        "2",
        [
            "question 3\n['a', 'b', 'c']",
            "You are right",
            "You got 1 points out of 1.\nIf you want to try again,"
            + " type /startGame to start a new game.",
        ],
    )


def test_end_game_score_0_of_1():
    check_game_state(
        True,
        "1",
        [
            "question 3\n['a', 'b', 'c']",
            "You are wrong",
            "You got 0 points out of 1.\nIf you want to try again,"
            + " type /startGame to start a new game.",
        ],
    )


def test_right_asnwer():
    check_game_state(
        False,
        "0",
        ["question 1\n['a', 'b', 'c']", "You are right", "question 2\n['a', 'b', 'c']"],
    )


def test_wrong_answer():
    check_game_state(
        False,
        "1",
        ["question 1\n['a', 'b', 'c']", "You are wrong", "question 2\n['a', 'b', 'c']"],
    )


def test_others_from_client():
    check_game_state(
        False,
        "others",
        [
            "question 1\n['a', 'b', 'c']",
            "please, type the number of your supposed answer",
            "question 1\n['a', 'b', 'c']",
        ],
    )
