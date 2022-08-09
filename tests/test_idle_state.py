from tutils import (
    QUESTIONS,
    Config,
    FakeTelegramClient,
    bot_msg,
    check_conversation,
    user,
)

from bot_state import BotStateFactory
from chat_handler import ChatHandler
from question_storage import InMemoryStorage


def make_handler_greet():
    client = FakeTelegramClient()
    storage = InMemoryStorage(QUESTIONS)
    state_factory = BotStateFactory(client, storage)
    state = state_factory.make_greeting_state()
    chat_id = 111
    return Config(ChatHandler.create(state, chat_id), client, chat_id)


def make_handler_idle():
    client = FakeTelegramClient()
    storage = InMemoryStorage(QUESTIONS)
    state_factory = BotStateFactory(client, storage)
    state = state_factory.make_idle_state()
    chat_id = 111
    return Config(ChatHandler.create(state, chat_id), client, chat_id)


def test_process_starting_game():
    check_conversation(
        make_handler_idle(),
        [
            user("/startGame"),
            bot_msg("Starting game!"),
        ],
    )


def test_process_other_message():
    check_conversation(
        make_handler_idle(),
        [
            user("other message"),
            bot_msg("Type /startGame to start a new game."),
        ],
    )


def test_greeting_state():
    check_conversation(
        make_handler_greet(),
        [
            user("hi"),
            bot_msg(
                "Hello. I am Trivia Bot. If you want to play the game,\n"
                "please type /startGame"
            ),
        ],
    )
