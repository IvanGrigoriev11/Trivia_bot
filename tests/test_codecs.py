import json
from typing import Callable

from tutils import QUESTIONS, FakeTelegramClient

from bot_state import BotState, BotStateFactory
from chat_handler import ChatHandler
from custom_codecs import ChatHandlerDecoder, ChatHandlerEncoder
from storage import InMemoryStorage


def check_chat_handler_codecs(make_state: Callable[[BotStateFactory], BotState]):
    client = FakeTelegramClient()
    chat_id = 111
    storage = InMemoryStorage(QUESTIONS)
    state_factory = BotStateFactory(client, storage)
    initial_chat_handler = ChatHandler.create(make_state(state_factory), chat_id)
    ch = json.dumps(initial_chat_handler, cls=ChatHandlerEncoder)
    reassembled_chat_handler = ChatHandlerDecoder(client, state_factory).decode(
        json.loads(ch)
    )
    assert initial_chat_handler == reassembled_chat_handler


def test_greeting_state_handler():
    check_chat_handler_codecs(lambda factory: factory.make_greeting_state())


def test_idle_state_handler():
    check_chat_handler_codecs(lambda factory: factory.make_idle_state())


def test_right_game_state_handler():
    check_chat_handler_codecs(lambda factory: factory.make_game_state())
