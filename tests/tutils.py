from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional

from bot_state import BotStateFactory
from chat_handler import ChatHandler
from question_storage import InMemoryStorage
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


class StateKind(Enum):
    GREETING_STATE = "GreetingState"
    IDLE_STATE = "IdleState"
    GAME_STATE = "GameState"


@dataclass(frozen=True)
class MessageContent:
    kind: MessageKind
    text_message: str
    reply_markup: Optional[InlineKeyboardMarkup] = None


@dataclass
class StateContent:
    desired_state: StateKind
    conversation: List[MessageContent]


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


def greeting(conversation: List[MessageContent]) -> StateContent:
    return StateContent(StateKind.GREETING_STATE, conversation)


def idle(conversation: List[MessageContent]) -> StateContent:
    return StateContent(StateKind.IDLE_STATE, conversation)


def game(conversation: List[MessageContent]) -> StateContent:
    return StateContent(StateKind.GAME_STATE, conversation)


def check_state(state_content: StateContent):
    client = FakeTelegramClient()
    storage = InMemoryStorage()
    chat_id = 111
    state_factory = BotStateFactory(client, storage)
    if state_content.desired_state == StateKind.GREETING_STATE:
        state = state_factory.make_greeting_state()
    elif state_content.desired_state == StateKind.IDLE_STATE:
        state = state_factory.make_idle_state()
    else:
        state = state_factory.make_game_state()

    chat_handler = ChatHandler.create(state, chat_id)
    check_conversation(
        chat_id, state_content.conversation, client, chat_handler.process
    )


def check_conversation(
    chat_id: int,
    conversation: List[MessageContent],
    client: FakeTelegramClient,
    handle: Callable[[Update], None],
):
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
            handle(
                Update(
                    update_id,
                    Message(Chat(chat_id), msg.text_message),
                    callback_query=None,
                )
            )
