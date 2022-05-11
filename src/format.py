from models import Question
from telegram_client import InlineKeyboardButton, InlineKeyboardMarkup


def make_keyboard(question: Question) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(answer, f"{i + 1}")
        for i, answer in enumerate(question.answers)
    ]
    return InlineKeyboardMarkup([buttons])
