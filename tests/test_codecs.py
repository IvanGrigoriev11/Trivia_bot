import json
from typing import Callable

import pytest
from tutils import QUESTIONS, FakeTelegramClient

from bot_state import BotState, BotStateFactory
from chat_handler import ChatHandler
from custom_codecs import ChatHandlerDecoder, ChatHandlerEncoder
from storage import InMemoryStorage


async def check_chat_handler_codecs(make_state: Callable[[BotStateFactory], BotState]):
    client = FakeTelegramClient()
    chat_id = 111
    storage = InMemoryStorage(QUESTIONS)
    state_factory = BotStateFactory(client, storage)
    initial_chat_handler = await ChatHandler.create(make_state(state_factory), chat_id)
    ch = json.dumps(initial_chat_handler, cls=ChatHandlerEncoder)
    reassembled_chat_handler = ChatHandlerDecoder(client, state_factory).decode(
        json.loads(ch)
    )
    assert initial_chat_handler == reassembled_chat_handler


@pytest.mark.asyncio
async def test_greeting_state_handler():
    await check_chat_handler_codecs(lambda factory: factory.make_greeting_state())


@pytest.mark.asyncio
async def test_idle_state_handler():
    await check_chat_handler_codecs(lambda factory: factory.make_idle_state())


@pytest.mark.asyncio
async def test_right_game_state_handler():
    await check_chat_handler_codecs(lambda factory: factory.make_game_state())
