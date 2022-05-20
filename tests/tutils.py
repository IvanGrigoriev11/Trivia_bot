from dataclasses import dataclass
from typing import Callable, List, Optional

from telegram_client import (
    Chat,
    EditSendMessage,
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

    def edit_message_text(self, payload: EditSendMessage) -> None:
        """write later"""


@dataclass(frozen=True)
class MessageContent:
    is_bot: bool
    text_message: str
    reply_markup: Optional[InlineKeyboardMarkup] = None


def bot(
    text_message: str, reply_markup: Optional[InlineKeyboardMarkup] = None
) -> MessageContent:
    return MessageContent(True, text_message, reply_markup)


def user(text_message: str) -> MessageContent:
    return MessageContent(False, text_message)


def check_conversation(
    chat_id: int,
    conversation: List[MessageContent],
    client: FakeTelegramClient,
    handle: Callable[[Update], None],
):
    last_message_from_bot = 0
    update_id = 111
    for msg in conversation:
        if msg.is_bot:
            assert client.sent_messages[last_message_from_bot] == SendMessagePayload(
                chat_id, msg.text_message, msg.reply_markup
            )
            last_message_from_bot += 1
        else:
            handle(
                Update(
                    update_id,
                    Message(Chat(chat_id), msg.text_message),
                    callback_query=None,
                )
            )
