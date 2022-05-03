from format import make_keyboard
from models import Question
from telegram_client import InlineKeyboardButton, InlineKeyboardMarkup


def test_keyboard():
    expected_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="orange", callback_data="None"),
                InlineKeyboardButton(text="blue", callback_data="None"),
                InlineKeyboardButton(text="green", callback_data="None"),
            ]
        ]
    )
    question = [
        Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
    ]
    formed_keyboard = make_keyboard(question[0])

    assert expected_keyboard == formed_keyboard
