import json

from bot_state import BotStateFactory, GameState, GreetingState, IdleState
from chat_handler import ChatHandler
from telegram_client import TelegramClient


class ChatHandlerEncoder(json.JSONEncoder):
    """JSON encoder for ChatHandler class.
    Return JSON dict from ChatHandler object."""

    def default(self, o):
        if isinstance(o, ChatHandler):
            return {
                "__chat_handler__": True,
                "chat_id": o.chat_handler_params.chat_id,
                "state": ChatHandlerEncoder.default(self, o.chat_handler_params.state),
            }

        if isinstance(o, GreetingState):
            return {
                "state_name": f"{type(o)}",
            }
        if isinstance(o, IdleState):
            return {
                "state_name": f"{type(o)}",
            }
        if isinstance(o, GameState):
            return {
                "state_name": f"{type(o)}",
                "questions": o.questions,
                "game_parameters": o.game_params,
            }

        raise TypeError(
            f"{o} type object is not subscriptable."
            f"An object of type ChatHandler is expected to be encoded, not {o}."
        )


class ChatHandlerDecoder(json.JSONDecoder):
    """JSON decoder for ChatHandler class."""

    def __init__(self, client: TelegramClient, state_factory: BotStateFactory):
        super().__init__()
        self.client = client
        self.state_factory = state_factory

    def decode_chat_handler(self, dct: dict):
        """Return ChatHandler object from JSON dict."""

        if "__chat_handler__" in dct:
            chat_id = dct["chat_id"]
            state_name = dct["state"]["state_name"]
            if state_name == f"{GreetingState}":
                state = GreetingState(self.client, self.state_factory)
            elif state_name == f"{IdleState}":
                state = IdleState(self.client, self.state_factory)
            elif state_name == f"{GameState}":
                questions = dct["state"]["questions"]
                game_params = dct["state"]["game_parameters"]
                state = GameState(
                    self.client, questions, self.state_factory, game_params
                )
            else:
                raise TypeError("Unknown value of 'state_name' key")

            return ChatHandler.create(state, chat_id)
        return dct
