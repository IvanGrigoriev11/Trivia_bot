from format import (
    CHECK_MARK,
    CROSS_MARK,
    RED_CIRCLE_MARK,
    make_answered_question_message,
    make_keyboard,
)
from storage import Question
from telegram_client import InlineKeyboardButton, InlineKeyboardMarkup


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
    expected_answer = "\n".join(
        [
            "1.What is the color of sky?",
            f"{RED_CIRCLE_MARK}orange",
            f"{CHECK_MARK}blue",
            f"{CROSS_MARK}green",
        ]
    )

    user_answer = 2
    formed_answer = make_answered_question_message(
        user_answer,
        Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
    )

    assert expected_answer == formed_answer
