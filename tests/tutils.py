from typing import Callable, List, Tuple, Optional

from form_buttons import form_buttons
from telegram_client import Chat, Message, SendMessagePayload, TelegramClient, Update, InlineKeyboardMarkup,\
    InlineKeyboardButton

from models import Question


class FakeTelegramClient(TelegramClient):
    def __init__(self):
        self.sent_messages: List[SendMessagePayload] = []

    def get_updates(self, offset: int = 0) -> List[Update]:
        raise NotImplementedError()

    def send_message(self, payload: SendMessagePayload) -> None:
        self.sent_messages.append(payload)


def check_conversation(
    chat_id: int,
    conversation: List[Tuple[bool, str, Optional[InlineKeyboardMarkup]]],
    client: FakeTelegramClient,
    handle: Callable[[Update], None],
):
    last_message_from_bot = 0
    update_id = 111
    for bot, message, reply_markup in conversation:
        if bot:
            assert client.sent_messages[last_message_from_bot] == SendMessagePayload(
                chat_id, message, reply_markup
            )
            last_message_from_bot += 1
        else:
            handle(Update(update_id, Message(Chat(chat_id), message), callback_query=None))


def check_keyboard(expected_keyboard: InlineKeyboardMarkup):
    questions = [
        Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
    ]
    formed_keyboard = form_buttons(questions[0])

    assert expected_keyboard == formed_keyboard


def test_keyboard():
    check_keyboard(
        InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text='orange', callback_data='None'),
                    InlineKeyboardButton(text='blue', callback_data='None'),
                    InlineKeyboardButton(text='yellow', callback_data='None')
                ]
            ]
        )
    )
