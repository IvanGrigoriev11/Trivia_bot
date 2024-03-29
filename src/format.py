import string
from typing import List

from storage import Question
from telegram_client import InlineKeyboardButton, InlineKeyboardMarkup

CHECK_MARK = "✅"
CROSS_MARK = "❌"
RED_CIRCLE_MARK = "⭕"


def make_keyboard(question: Question) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(chr(ord("a") + i), f"{chr(ord('a') + i)}")
        for i in range(len(question.answers))
    ]
    return InlineKeyboardMarkup([buttons])


def make_question(question: Question) -> str:
    """
    Creates a text field in the question message
    with the answer options marked with ordered letters.
    """

    answers = []
    for letter, answer in zip(string.ascii_lowercase, question.answers):
        answers.append(letter + ") " + answer)
    return question.text + "\n" + "\n".join(answers)


def make_answered_question(user_answer: int, question: Question) -> str:
    """
    Creates a question message that reflects the user's answer.
    """

    edited_answers = []
    for index, word in enumerate(question.answers):
        if index == question.correct_answer:
            edited_answers.append(
                f"{CHECK_MARK}" + f"{question.answers[question.correct_answer]}"
            )
        elif index != question.correct_answer and index == user_answer:
            edited_answers.append(f"{CROSS_MARK}" + f"{question.answers[user_answer]}")
        else:
            edited_answers.append(f"{RED_CIRCLE_MARK}" + f"{word}")

    message = f"{question.text}" + "\n" + "\n".join(edited_answers)
    return message


def make_answers_help_message(answers: List[str]) -> str:
    """Reports the wrong form of the answer."""

    return (
        f"Please type a letter indicating your answer. "
        f"Valid options are {', '.join(string.ascii_lowercase[:len(answers)])}."
    )
