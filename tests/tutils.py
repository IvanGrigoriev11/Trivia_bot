from typing import Callable, List, Tuple, Optional

from telegram_client import Chat, Message, SendMessagePayload, TelegramClient, Update, InlineKeyboardMarkup, InlineKeyboardButton


class FakeTelegramClient(TelegramClient):
    def __init__(self):
        self.sent_messages: List[SendMessagePayload] = []

    def get_updates(self, offset: int = 0) -> List[Update]:
        raise NotImplementedError()

    def send_message(self, payload: SendMessagePayload) -> None:
        self.sent_messages.append(payload)


def fake_form_buttons(questions: List[str]) -> InlineKeyboardMarkup:
    default_list = []
    for i in range(len(questions)):
        button = InlineKeyboardButton(f'{questions[i]}', 'None')
        default_list.append(button)
    inline_keyboard = InlineKeyboardMarkup([default_list])
    return inline_keyboard


def check_conversation(
    chat_id: int,
    conversation: List[Tuple[bool, str, List[str]]],
    client: FakeTelegramClient,
    handle: Callable[[Update], None],
):
    last_message_from_bot = 0
    update_id = 111
    for bot, message, list_of_buttons in conversation:
        reply_markup = fake_form_buttons(list_of_buttons)
        if bot:
            assert client.sent_messages[last_message_from_bot] == SendMessagePayload(
                chat_id, message, reply_markup
            )
            last_message_from_bot += 1
        else:
            handle(Update(update_id, Message(Chat(chat_id), message), callback_query=None))
