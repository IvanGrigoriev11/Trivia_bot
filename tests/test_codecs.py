import json

from tutils import OTHER_QUESTION, QUESTIONS, FakeTelegramClient

from bot_state import BotStateFactory
from chat_handler import ChatHandler
from custom_codecs import ChatHandlerDecoder, ChatHandlerEncoder
from storage import InMemoryStorage


def check_chat_handler_codecs(desired_state: str):
    client = FakeTelegramClient()
    chat_id = 111
    storage = InMemoryStorage(QUESTIONS)
    state_factory = BotStateFactory(client, storage)
    if desired_state == "GreetingState":
        state = state_factory.make_greeting_state()
    elif desired_state == "IdleState":
        state = state_factory.make_idle_state()
    else:
        state = state_factory.make_game_state()
    initial_chat_handler = ChatHandler.create(state, chat_id)
    ch = json.dumps(initial_chat_handler, cls=ChatHandlerEncoder)
    reassembled_chat_handler = json.loads(
        ch, object_hook=ChatHandlerDecoder(client, state_factory).form_chat_handler
    )

    # to verify the correctness of states' equality
    other_storage = InMemoryStorage(OTHER_QUESTION)
    wrong_state_factory = BotStateFactory(client, other_storage)
    wrong_state = wrong_state_factory.make_game_state()
    wrong_chat_handler = ChatHandler.create(wrong_state, chat_id)

    assert initial_chat_handler == reassembled_chat_handler
    assert wrong_chat_handler != reassembled_chat_handler


def test_greeting_state_handler():
    check_chat_handler_codecs("GreetingState")


def test_idle_state_handler():
    check_chat_handler_codecs("IdleState")


def test_game_state_handler():
    check_chat_handler_codecs("GameState")
