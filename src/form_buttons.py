from telegram_client import SendMessagePayload
from models import Question
from telegram_client import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict


def form_buttons() -> InlineKeyboardMarkup:
    button1 = InlineKeyboardButton('orange', '0')
    button2 = InlineKeyboardButton('blue', '1')
    button3 = InlineKeyboardButton('green', '2')
    inline_keyboard = InlineKeyboardMarkup([[button1, button2, button3]])
    return inline_keyboard

