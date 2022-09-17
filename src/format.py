from question_storage import Question
from telegram_client import InlineKeyboardButton, InlineKeyboardMarkup

CHECK_MARK = "✅"
CROSS_MARK = "❌"
RED_CIRCLE_MARK = "⭕"


def make_keyboard(question: Question) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(chr(97 + i), f"{i}") for i in range(len(question.answers))
    ]
    return InlineKeyboardMarkup([buttons])


def make_text_question(question: Question) -> str:
    """
    Create a text field in the question message with the answer options marked with ordered letters.
    """

    new_formatted_answers = []
    for index, word in enumerate(question.answers):
        new_formatted_answers.append(f"{chr(index + 97)})" + " " + word)
    return question.text + "\n" + "\n".join(new_formatted_answers)


def make_answered_question_message(user_answer: int, question: Question) -> str:
    """
    Create a question message that reflects the user's answer.
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
