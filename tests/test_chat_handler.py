from typing import List, Optional, Tuple

from tutils import check_conversation, FakeTelegramClient
from form_buttons import form_buttons
from models import Question
from telegram_client import InlineKeyboardButton, InlineKeyboardMarkup
from chat_handler import ChatHandler

QUESTIONS = [
        Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
        Question("2.How much is 2 + 5?", ["4", "10", "7", "8"], 2),
        Question(
            "3.What date is Christmas?", ["Dec 24", "Apr 15", "Jan 1", "Dec 25"], 3
        ),
]


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
         (
             True, "1.What is the color of sky?\n['orange', 'blue', 'green']",
             form_buttons(QUESTIONS[0])
         ),
         (False, "2", None),
         (True, "You are wrong", None),
         (
             True, "2.How much is 2 + 5?\n['4', '10', '7', '8']",
             form_buttons(QUESTIONS[1])
         ),
         (False, "2", None),
         (True, "You are right", None),
         (
             True,
             "3.What date is Christmas?\n['Dec 24', 'Apr 15', 'Jan 1', 'Dec 25']",
             form_buttons(QUESTIONS[2])
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


def check_keyboard(expected_keyboard: InlineKeyboardMarkup):
    questions = [
        Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
    ]
    formed_keyboard = form_buttons(questions[0])

    assert expected_keyboard == formed_keyboard


def test_keyboard():
    check_keyboard(
        InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text='orange', callback_data='None'),
                    InlineKeyboardButton(text='blue', callback_data='None'),
                    InlineKeyboardButton(text='green', callback_data='None')
                ]
            ]
        )
    )
