from models import Question
from telegram_client import InlineKeyboardButton, InlineKeyboardMarkup, TelegramClient

CHECK_MARK = "\u2705"
CROSS_MARK = "\u274C"
RED_CIRCLE_MARK = "\u2B55"


def make_keyboard(question: Question) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(answer, f"{i}")
        for i, answer in enumerate(question.answers)
    ]
    return InlineKeyboardMarkup([buttons])


def make_question_message(client: TelegramClient, chat_id: int, question: Question) -> int:
    """
    Builds the original form of question and directs it to the "send_message" interface,
    returns the id of the last sent message with question to the user.
    """

    return client.send_text(
        chat_id,
        f"{question.text}",
        make_keyboard(question),
    )


def make_answered_question_message(
    user_answer: int,
    questions: Question
) -> str:
    """
    Edits the text of last sent question depends on user's answer.
    Returns edited form after adding some unicode symbols to the text of answers.
    """

    for elements, key in enumerate(questions.answers):
        if elements not in (questions.correct_answer, user_answer):
            questions.answers[elements] = f"{RED_CIRCLE_MARK}"+f"{key}"

    if user_answer != questions.correct_answer:
        questions.answers[user_answer] = f"{CROSS_MARK}"+f"{questions.answers[user_answer]}"

    questions.answers[questions.correct_answer] = f"{CHECK_MARK}" + f"{questions.answers[questions.correct_answer]}"
    edit_answers = f"{questions.text}" + "\n" + "\n".join(questions.answers)
    return edit_answers
