from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional

from telegram_client import (
    Chat,
    InlineKeyboardMarkup,
    Message,
    MessageEdit,
    SendMessagePayload,
    TelegramClient,
    Update,
)


class FakeTelegramClient(TelegramClient):
    def __init__(self):
        self.sent_messages: List[SendMessagePayload | MessageEdit] = []

    def get_updates(self, offset: int = 0) -> List[Update]:
        raise NotImplementedError()

    def send_message(self, payload: SendMessagePayload) -> int:
        self.sent_messages.append(payload)
        return 0

    def edit_message_text(self, payload: MessageEdit) -> None:
        self.sent_messages.append(payload)


class MessageKind(Enum):
    USER = "user_mode"
    BOT_MSG = "bot_msg"
    BOT_EDIT = "bot_edit"


@dataclass(frozen=True)
class MessageContent:
    mode: MessageKind
    text_message: str
    reply_markup: Optional[InlineKeyboardMarkup] = None


def bot_edit(
    text_message: str, reply_markup: Optional[InlineKeyboardMarkup] = None
) -> MessageContent:
    return MessageContent(MessageKind.BOT_EDIT, text_message, reply_markup)


def bot_msg(
    text_message: str, reply_markup: Optional[InlineKeyboardMarkup] = None
) -> MessageContent:
    return MessageContent(MessageKind.BOT_MSG, text_message, reply_markup)


def user(text_message: str) -> MessageContent:
    return MessageContent(MessageKind.USER, text_message)


def check_conversation(
    chat_id: int,
    conversation: List[MessageContent],
    client: FakeTelegramClient,
    handle: Callable[[Update], None],
):
    last_message_from_bot = 0
    update_id = 111
    for msg in conversation:
        if msg.mode == "bot_msg":
            assert client.sent_messages[last_message_from_bot] == SendMessagePayload(
                chat_id, msg.text_message, msg.reply_markup
            )
            last_message_from_bot += 1
        elif msg.mode == "bot_edit":
            assert client.sent_messages[last_message_from_bot] == MessageEdit(
                chat_id, 0, msg.text_message
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
