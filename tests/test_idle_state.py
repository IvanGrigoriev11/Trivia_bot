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


def make_conv_conf():
    client = FakeTelegramClient()
    storage = InMemoryStorage(QUESTIONS)
    state_factory = BotStateFactory(client, storage)
    state = state_factory.make_idle_state()
    chat_id = 111
    return ConvConfig(ChatHandler.create(state, chat_id), client, chat_id)


def test_process_starting_game():
    check_conversation(
        make_conv_conf(),
        [
            user("/startGame"),
            bot_msg("Starting game!"),
        ],
    )


def test_process_other_message():
    check_conversation(
        make_conv_conf(),
        [
            user("other message"),
            bot_msg("Type /startGame to start a new game."),
        ],
    )
