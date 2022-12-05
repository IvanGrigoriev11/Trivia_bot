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
    state = await state_factory.make_idle_state()
    chat_id = 111
    ch = await ChatHandler.create(state, chat_id)
    return ConvConfig(ch, client, chat_id)


@pytest.mark.asyncio
async def test_process_starting_game():
    await check_conversation(
        await make_conv_conf(),
        [
            user("/startGame"),
            bot_msg("Starting game!"),
        ],
    )


@pytest.mark.asyncio
async def test_process_other_message():
    await check_conversation(
        await make_conv_conf(),
        [
            user("other message"),
            bot_msg("Type /startGame to start a new game."),
        ],
    )
