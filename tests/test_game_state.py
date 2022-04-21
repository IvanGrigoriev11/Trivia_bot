from utils import FakeTelegramClient
from bot_state import GameState
from telegram_client import Update, SendMessagePayload, Message, Chat
from models import Question
from typing import List, Tuple


def check_game_state(conversation: List[Tuple[bool, str]]):
    client = FakeTelegramClient()
    chat_id = 111
    state = GameState(client, Question.make_some())
    state.on_enter(chat_id)
    last_message_from_bot = 0
    update_id = 111
    for bot, message in conversation:
        if bot:
            assert client.sent_messages[last_message_from_bot] == SendMessagePayload(chat_id, message)
            last_message_from_bot += 1
        else:
            state.process(Update(update_id, Message(Chat(chat_id), message)))


def test_game_state():
    check_game_state([
        (True, "1.What is the color of sky?\n['orange', 'blue', 'green']"),
        (False, '1'),
        (True, 'You are right'),
        (True, "2.How much is 2 + 5?\n['4', '10', '7', '8']"),
        (False, '1'),
        (True, 'You are wrong'),
        (True, "3.What date is Christmas?\n['Dec 24', 'Apr 15', 'Jan 1', 'Dec 25']"),
        (False, '1'),
        (True, 'You are wrong'),
        (True, 'You got 1 points out of 3.\nIf you want to try again, type /startGame to start a new game.')
    ])


def test_right_answer():
    check_game_state([
        (True, "1.What is the color of sky?\n['orange', 'blue', 'green']"),
        (False, '1'),
        (True, 'You are right')
    ])


def test_wrong_answer():
    check_game_state([
        (True, "1.What is the color of sky?\n['orange', 'blue', 'green']"),
        (False, '2'),
        (True, 'You are wrong')
    ])


def test_gibberish_reply():
    check_game_state([
        (True, "1.What is the color of sky?\n['orange', 'blue', 'green']"),
        (False, 'first'),
        (True, "please, type the number of your supposed answer"),
        (False, 'second'),
        (True, "please, type the number of your supposed answer"),
        (False, '1'),
        (True, "You are right")
    ])


def test_enter_inappropriate_number():
    check_game_state([
        (True, "1.What is the color of sky?\n['orange', 'blue', 'green']"),
        (False, '-1'),
        (True, "Type the number from 0 to 2"),
        (False, '3'),
        (True, "Type the number from 0 to 2"),
        (False, '2'),
        (True, 'You are wrong'),
        (True, "2.How much is 2 + 5?\n['4', '10', '7', '8']"),
    ])
