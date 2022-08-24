import json

from tutils import QUESTIONS, FakeTelegramClient

from bot_state import BotStateFactory
from chat_handler import ChatHandler
from custom_encoder import ChatHandlerDecoder, ChatHandlerEncoder
from question_storage import InMemoryStorage


def test_chat_handler_encoder():
    client = FakeTelegramClient()
    chat_id = 111
    state_factory = BotStateFactory(client, storage=InMemoryStorage(QUESTIONS))
    state = state_factory.make_idle_state()
    initial_chat_handler = ChatHandler.create(state, chat_id)

    ch = json.dumps(initial_chat_handler, cls=ChatHandlerEncoder)
    json_chat_handler = json.loads(ch, cls=ChatHandlerDecoder)

    wrong_state = state_factory.make_greeting_state()
    wrong_chat_handler = ChatHandler.create(wrong_state, chat_id)

    assert (
        initial_chat_handler == json_chat_handler
        and wrong_chat_handler != json_chat_handler
    )
