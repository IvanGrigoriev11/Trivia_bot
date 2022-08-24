import json

from tutils import QUESTIONS

from bot_state import BotStateFactory, GameState, GreetingState, IdleState
from chat_handler import ChatHandler
from question_storage import InMemoryStorage
from telegram_client import TelegramClient


class ChatHandlerEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ChatHandler):
            return {
                "chat_handler": True,
                "chat_id": o.chat_id,
                "state": ChatHandlerEncoder.default(self, o.state),
            }

        if isinstance(o, GreetingState):
            return {
                "state_name": f"{type(o)}",
                "client": ChatHandlerEncoder.default(self, o.client),
                "state_factory": ChatHandlerEncoder.default(self, o.state_factory),
            }
        if isinstance(o, IdleState):
            return {
                "state_name": f"{type(o)}",
                "client": ChatHandlerEncoder.default(self, o.client),
                "state_factory": ChatHandlerEncoder.default(self, o.state_factory),
            }
        if isinstance(o, GameState):
            return {
                "state_name": f"{type(o)}",
                "questions": o.questions,
                "game_parameters": o.game_params,
                "client": ChatHandlerEncoder.default(self, o.client),
                "state_factory": ChatHandlerEncoder.default(self, o.state_factory),
            }

        if isinstance(o, TelegramClient):
            return f"{type(o)}"

        if isinstance(o, BotStateFactory):
            return {
                "factory_name": f"{type(o)}",
                "storage": f"{type(o.storage)}",
            }


def chat_handler_deserialization(dct):
    if "chat_handler" in dct:
        chat_id = dct["chat_id"]
        state_name = dct["state"]["state_name"]
        client = dct["state"]["client"]
        if state_name == f"{GreetingState}":
            storage = InMemoryStorage(QUESTIONS)
            state = GreetingState(client, BotStateFactory(client, storage))
        elif state_name == f"{IdleState}":
            storage = InMemoryStorage(QUESTIONS)
            state = IdleState(client, BotStateFactory(client, storage))
        else:
            storage = InMemoryStorage(QUESTIONS)
            questions = dct["questions"]
            state = GameState(client, questions, BotStateFactory(client, storage))

        return ChatHandler.create(state, chat_id)
    return dct


class ChatHandlerDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(
            self, object_hook=chat_handler_deserialization, *args, **kwargs
        )
