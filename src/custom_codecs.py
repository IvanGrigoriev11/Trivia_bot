import json
from json import JSONDecodeError

from bot_state import (
    BotStateFactory,
    GameState,
    GreetingState,
    IdleState,
    ProtoGameState,
)
from chat_handler import ChatHandler, ProtoChatHandler
from storage import Question
from telegram_client import TelegramClient


class ChatHandlerEncoder(json.JSONEncoder):
    """JSON encoder for ChatHandler class.
    Return JSON dict from ChatHandler object."""

    def default(self, o):
        data = {}
        try:
            if isinstance(o, ChatHandler):
                data.update(
                    {
                        "__chat_handler__": True,
                        "chat_handler": self.default(o.chat_handler_params),
                    }
                )
            if isinstance(o, ProtoChatHandler):
                data.update(
                    {
                        "chat_id": json.dumps(o.chat_id, cls=ChatHandlerEncoder),
                        "__state__": self.default(o.state),
                    }
                )
            if isinstance(o, GreetingState):
                data.update(
                    {
                        "state_name": "GreetingState",
                    }
                )
            if isinstance(o, IdleState):
                data.update(
                    {
                        "state_name": "IdleState",
                    }
                )
            if isinstance(o, GameState):
                data.update(
                    {
                        "state_name": "GameState",
                        "game_parameters": self.default(o.game_params),
                    }
                )
            if isinstance(o, ProtoGameState):
                data.update(
                    {
                        "questions": json.dumps(o.questions, cls=ChatHandlerEncoder),
                        "current_question": json.dumps(
                            o.current_question, cls=ChatHandlerEncoder
                        ),
                        "score": json.dumps(o.score, cls=ChatHandlerEncoder),
                        "last_question_message_id": json.dumps(
                            o.last_question_msg_id, cls=ChatHandlerEncoder
                        ),
                    }
                )
            if isinstance(o, Question):
                data.update(
                    {
                        "text": json.dumps(o.text, cls=ChatHandlerEncoder),
                        "answers": json.dumps(o.answers, cls=ChatHandlerEncoder),
                        "correct_answer": json.dumps(
                            o.correct_answer, cls=ChatHandlerEncoder
                        ),
                    }
                )
        except TypeError:
            print(f"{o} type object is not subscriptable.")
        return data


class ChatHandlerDecoder(json.JSONDecoder):
    """JSON decoder for ChatHandler class.
    Return ChatHandler object from JSON dict."""

    def __init__(
        self, client: TelegramClient, state_factory: BotStateFactory, *args, **kwargs
    ):
        json.JSONDecoder.__init__(
            self, object_hook=self.form_chat_handler, *args, **kwargs
        )
        self.client = client
        self.state_factory = state_factory

    def helper(self, obj):
        try:
            if isinstance(obj, list):
                data = [self.helper(el) for el in obj]
            elif isinstance(obj, dict):
                data = obj
            else:
                data = json.loads(obj)

            if isinstance(data, dict):
                for k, v in data.items():
                    data[k] = self.helper(v)
            if isinstance(data, list):
                for i in data:
                    self.helper(i)
        except (JSONDecodeError, TypeError, AttributeError):
            return obj
        return data

    def form_chat_handler(self, dct) -> ChatHandler:
        if "chat_handler" in dct:
            if dct["chat_handler"]["__state__"]["state_name"] == "GreetingState":
                state = GreetingState(self.client, self.state_factory)
            elif dct["chat_handler"]["__state__"]["state_name"] == "IdleState":
                state = IdleState(self.client, self.state_factory)
            elif dct["chat_handler"]["__state__"]["state_name"] == "GameState":
                game_params = self.helper(
                    dct["chat_handler"]["__state__"]["game_parameters"]
                )
                questions = []
                for question in game_params["questions"]:
                    questions.append(
                        Question(
                            question["text"],
                            question["answers"],
                            question["correct_answer"],
                        )
                    )

                state = GameState(
                    self.client,
                    self.state_factory,
                    ProtoGameState(
                        questions,
                        game_params["current_question"],
                        game_params["score"],
                        game_params["last_question_message_id"],
                    ),
                )
            else:
                raise KeyError("Unknown name for 'state_name' key")
            return ChatHandler.create(state, json.loads(dct["chat_handler"]["chat_id"]))
        return dct
