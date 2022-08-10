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
from question_storage import InMemoryStorage


def make_conv_conf():
    client = FakeTelegramClient()
    storage = InMemoryStorage(QUESTIONS)
    state_factory = BotStateFactory(client, storage)
    state = state_factory.make_greeting_state()
    chat_id = 111
    return ConvConfig(ChatHandler.create(state, chat_id), client, chat_id)


def test_greeting_state():
    check_conversation(
        make_conv_conf(),
        [
            user("hi"),
            bot_msg(
                "Hello. I am Trivia Bot. If you want to play the game,\n"
                "please type /startGame"
            ),
        ],
    )
