import json

from bot_state import BotStateFactory, GameState, GreetingState, IdleState
from chat_handler import ChatHandler
from question_storage import InMemoryStorage, Question

QUESTIONS = [
    Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
    Question("2.How much is 2 + 5?", ["4", "10", "7", "8"], 2),
    Question("3.What date is Christmas?", ["Dec 24", "Apr 15", "Jan 1", "Dec 25"], 3),
]


class ChatHandlerEncoder(json.JSONEncoder):
    """JSON encoder for ChatHandler class.
    Return JSON dict from ChatHandler object."""

    def default(self, o):
        if isinstance(o, ChatHandler):
            return {
                "__chat_handler__": True,
                "chat_id": o.chat_id,
                "state": ChatHandlerEncoder.default(self, o.state),
            }

        if isinstance(o, GreetingState):
            return {
                "state_name": f"{type(o)}",
                "client": f"{type(o.client)}",
                "state_factory": ChatHandlerEncoder.default(self, o.state_factory),
            }
        if isinstance(o, IdleState):
            return {
                "state_name": f"{type(o)}",
                "client": f"{type(o.client)}",
                "state_factory": ChatHandlerEncoder.default(self, o.state_factory),
            }
        if isinstance(o, GameState):
            return {
                "state_name": f"{type(o)}",
                "questions": o.questions,
                "game_parameters": o.game_params,
                "client": f"{type(o.client)}",
                "state_factory": ChatHandlerEncoder.default(self, o.state_factory),
            }

        if isinstance(o, BotStateFactory):
            return {
                "factory_name": f"{type(o)}",
                "storage": f"{type(o.storage)}",
            }

        raise TypeError


def decode_chat_handler(dct: dict):
    """Return ChatHandler object from JSON dict."""

    if "__chat_handler__" in dct:
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
            questions = dct["state"]["questions"]
            state = GameState(client, questions, BotStateFactory(client, storage))

        return ChatHandler.create(state, chat_id)
    return dct


class ChatHandlerDecoder(json.JSONDecoder):
    """JSON decoder for ChatHandler class."""

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(
            self, object_hook=decode_chat_handler, *args, **kwargs
        )
