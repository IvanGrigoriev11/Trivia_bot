from format import make_keyboard
from models import Question
from telegram_client import InlineKeyboardButton, InlineKeyboardMarkup


def test_keyboard():
    expected_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="orange", callback_data="1"),
                InlineKeyboardButton(text="blue", callback_data="2"),
                InlineKeyboardButton(text="green", callback_data="3"),
            ]
        ]
    )

    formed_keyboard = make_keyboard(
        Question("1.What is the color of sky?", ["orange", "blue", "green"], 2),
    )

    assert expected_keyboard == formed_keyboard
