from models import Question
from telegram_client import InlineKeyboardButton, InlineKeyboardMarkup


def form_buttons(questions: Question) -> InlineKeyboardMarkup:
    text_of_button = questions.answers
    default_list = []
    for i in range(len(questions.answers)):
        button = InlineKeyboardButton(f'{text_of_button[i]}', 'None')
        default_list.append(button)

    inline_keyboard = InlineKeyboardMarkup([default_list])
    return inline_keyboard
