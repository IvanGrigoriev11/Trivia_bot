from typing import Callable, List, Optional, Tuple
from dataclasses import dataclass

from telegram_client import (
    Chat,
    InlineKeyboardMarkup,
    Message,
    SendMessagePayload,
    TelegramClient,
    Update,
)


class FakeTelegramClient(TelegramClient):
    def __init__(self):
        self.sent_messages: List[SendMessagePayload] = []

    def get_updates(self, offset: int = 0) -> List[Update]:
        raise NotImplementedError()

    def send_message(self, payload: SendMessagePayload) -> None:
        self.sent_messages.append(payload)

@dataclass
class Container:
    is_bot: bool
    text_message: str
    reply_markup: Optional[InlineKeyboardMarkup] = None


@dataclass
class ConversationConstructor:
    container: List[Container]


def bot(
    text_message: str, reply_markup: Optional[InlineKeyboardMarkup] = None
) -> ConversationConstructor:
    return ConversationConstructor([True, text_message, reply_markup])


def user(
    text_message: str, reply_markup: Optional[InlineKeyboardMarkup] = None
) -> ConversationConstructor:
    return ConversationConstructor([True, text_message, reply_markup])


def check_conversation(
    chat_id: int,
    conversation: List[ConversationConstructor],
    client: FakeTelegramClient,
    handle: Callable[[Update], None],
):
    last_message_from_bot = 0
    update_id = 111
    for telegram_bot, message, reply_markup in conversation:
        if telegram_bot:
            assert client.sent_messages[last_message_from_bot] == SendMessagePayload(
                chat_id, message, reply_markup
            )
            last_message_from_bot += 1
        else:
            handle(
                Update(update_id, Message(Chat(chat_id), message), callback_query=None)
            )
