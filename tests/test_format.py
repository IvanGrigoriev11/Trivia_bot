from format import (
    CHECK_MARK,
    CROSS_MARK,
    RED_CIRCLE_MARK,
    make_answered_question_message,
    make_keyboard,
    make_text_question,
)
from question_storage import Question
from telegram_client import InlineKeyboardButton, InlineKeyboardMarkup


def test_keyboard():
    expected_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="a", callback_data="a"),
                InlineKeyboardButton(text="b", callback_data="b"),
                InlineKeyboardButton(text="c", callback_data="c"),
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


def test_question_formatting():
    formed_text = make_text_question(
        Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
    )
    expected_text = "1.What is the color of sky?\na) orange\nb) blue\nc) green"
    assert formed_text == expected_text
