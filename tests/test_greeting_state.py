import pytest
from tutils import (
    QUESTIONS,
    ConvConfig,
    FakeTelegramClient,
    bot_msg,
    check_conversation,
    user,
)

from bot_state import BotStateFactory
from chat_handler import ChatHandler
from storage import InMemoryStorage


async def make_conv_conf():
    client = FakeTelegramClient()
    storage = InMemoryStorage(QUESTIONS)
    state_factory = BotStateFactory(client, storage)
    state = state_factory.make_greeting_state()
    chat_id = 111
    ch = await ChatHandler.create(await state, chat_id)
    return ConvConfig(ch, client, chat_id)


@pytest.mark.asyncio
async def test_greeting_state():
    await check_conversation(
        await make_conv_conf(),
        [
            user("hi"),
            bot_msg(
                "Hello. I am Trivia Bot. If you want to play the game,\n"
                "please type /startGame"
            ),
        ],
    )
