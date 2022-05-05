from models import Question
from telegram_client import InlineKeyboardButton, InlineKeyboardMarkup


def make_keyboard(question: Question) -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(answer, f'{answer}') for answer in question.answers]
    return InlineKeyboardMarkup([buttons])