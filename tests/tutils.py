from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from bot_state import BotStateFactory
from chat_handler import ChatHandler
from question_storage import InMemoryStorage, Question
from telegram_client import (
    Chat,
    InlineKeyboardMarkup,
    Message,
    MessageEdit,
    SendMessagePayload,
    TelegramClient,
    Update,
)

QUESTIONS = [
    Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
    Question("2.How much is 2 + 5?", ["4", "10", "7", "8"], 2),
    Question("3.What date is Christmas?", ["Dec 24", "Apr 15", "Jan 1", "Dec 25"], 3),
]


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


class StateKind(Enum):
    GREETING_STATE = "GreetingState"
    IDLE_STATE = "IdleState"
    GAME_STATE = "GameState"


@dataclass(frozen=True)
class MessageContent:
    kind: MessageKind
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


def make_handler_greet():
    return StateKind.GREETING_STATE


def make_handler_idle():
    return StateKind.IDLE_STATE


def make_handler_game():
    return StateKind.GAME_STATE


def check_conversation(
    desired_state: StateKind,
    conversation: List[MessageContent],
):
    client = FakeTelegramClient()
    storage = InMemoryStorage(QUESTIONS)
    chat_id = 111
    state_factory = BotStateFactory(client, storage)
    if desired_state == StateKind.GREETING_STATE:
        state = state_factory.make_greeting_state()
    elif desired_state == StateKind.IDLE_STATE:
        state = state_factory.make_idle_state()
    else:
        state = state_factory.make_game_state()

    chat_handler = ChatHandler.create(state, chat_id)
    last_message_from_bot = 0
    update_id = 111
    for msg in conversation:
        if msg.kind == MessageKind.BOT_MSG:
            assert client.sent_messages[last_message_from_bot] == SendMessagePayload(
                chat_id, msg.text_message, msg.reply_markup
            )
            last_message_from_bot += 1
        elif msg.kind == MessageKind.BOT_EDIT:
            assert client.sent_messages[last_message_from_bot] == MessageEdit(
                chat_id, 0, msg.text_message
            )
            last_message_from_bot += 1
        else:
            chat_handler.process(
                Update(
                    update_id,
                    Message(Chat(chat_id), msg.text_message),
                    callback_query=None,
                )
            )
