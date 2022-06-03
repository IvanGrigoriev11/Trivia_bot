from format import make_answered_question_message, make_keyboard
from models import Question
from telegram_client import InlineKeyboardButton, InlineKeyboardMarkup

CHECK_MARK = "\u2705"
CROSS_MARK = "\u274C"
RED_CIRCLE_MARK = "\u2B55"


def test_keyboard():
    expected_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="orange", callback_data="0"),
                InlineKeyboardButton(text="blue", callback_data="1"),
                InlineKeyboardButton(text="green", callback_data="2"),
            ]
        ]
    )

    formed_keyboard = make_keyboard(
        Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
    )

    assert expected_keyboard == formed_keyboard


def test_edit_text_message():
    expected_answer = (
        "1.What is the color of sky?"
        + "\n"
        + f"{RED_CIRCLE_MARK}orange"
        + "\n"
        + f"{CHECK_MARK}blue"
        + "\n"
        + f"{CROSS_MARK}green"
    )

    user_answer = 2
    formed_answer = make_answered_question_message(
        user_answer,
        Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
    )

    assert expected_answer == formed_answer
