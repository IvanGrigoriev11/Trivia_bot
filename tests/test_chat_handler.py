from typing import List, Tuple

from test_game_state import FakeTelegramClient

from bot_state import BotState, GameState, IdleState
from chat_handler import ChatHandler
from models import Question
from telegram_client import Chat, Message, SendMessagePayload, Update


def communication_process(
    bot_state: BotState, bot: bool, bot_message: str, user_message: str
):
    # client = FakeTelegramClient()
    if bot:
        check(bot_state, bot_message, user_message)
    else:
        check(bot_state, user_message, bot_message)


def check(bot_state: BotState, text: str, expected_reply: str):
    client = FakeTelegramClient()
    if bot_state == IdleState:
        state = bot_state(client)
    else:
        questions = [Question("question 3", ["a", "b", "c"], 2)]
        state = bot_state(client, questions)
    chat_id = 111
    state.on_enter(chat_id)
    # state.process(SendMessagePayload(chat_id, text))
    state.process(Update(123, Message(Chat(chat_id), text)))

    assert client.sent_messages == [
        SendMessagePayload(chat_id, text) for text in expected_reply
    ]


def test_for_idle_state():
    communication_process(
        IdleState,
        False,
        [
            "Starting game!",
        ],
        "/startGame",
    )


def test_for_game_state():
    communication_process(
        GameState,
        False,
        [
            "question 3\n['a', 'b', 'c']",
            "You are right",
            "You got 1 points out of 1.\nIf you want to try again, type"
            + " /startGame to start a new game.",
        ],
        "2",
    )


def _test_chat(dialogue: List[Tuple[bool, str]]):
    client = FakeTelegramClient()
    chat_id = 123
    chat_handler = ChatHandler.default_for_chat(client, chat_id)
    last_bot_msg_checked = 0
    for is_bot, message in dialogue:
        if is_bot:
            assert client.sent_messages[last_bot_msg_checked] == SendMessagePayload(
                chat_id, message
            )
            last_bot_msg_checked += 1
        else:
            chat_handler.process(Update(1, Message(Chat(chat_id), message)))


def test_chat_handler():
    _test_chat(
        [
            (False, "/startgame"),
            (True, "Starting game!"),
            (True, "1.What is the color of sky?\n['orange', 'blue', 'green']"),
            (False, "1"),
            (True, "You are right"),
        ]
    )
