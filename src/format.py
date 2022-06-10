from models import Question
from telegram_client import InlineKeyboardButton, InlineKeyboardMarkup

CHECK_MARK = "✅"
CROSS_MARK = "❌"
RED_CIRCLE_MARK = "⭕"


def make_keyboard(question: Question) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(answer, f"{i}")
        for i, answer in enumerate(question.answers)
    ]
    return InlineKeyboardMarkup([buttons])


def make_answered_question_message(user_answer: int, question: Question) -> str:
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
