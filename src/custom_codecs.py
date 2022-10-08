import json

import jsons

from bot_state import (
    BotState,
    BotStateFactory,
    GameState,
    GreetingState,
    IdleState,
    ProtoGameState,
)
from chat_handler import ChatHandler
from telegram_client import TelegramClient


class ChatHandlerEncoder(json.JSONEncoder):
    """JSON encoder for ChatHandler class.
    Return JSON dict from ChatHandler object."""

    def default(self, o):
        def encode_state(state: BotState):
            if isinstance(state, GreetingState):
                return {
                    "state_name": "GreetingState",
                    "is_on_enter_called": state.is_on_enter_called,
                }

            if isinstance(state, IdleState):
                return {
                    "state_name": "IdleState",
                    "is_on_enter_called": state.is_on_enter_called,
                }

            if isinstance(state, GameState):
                return {
                    "state_name": "GameState",
                    "is_on_enter_called": state.is_on_enter_called,
                    "game_params": jsons.dump(state.game_params),
                }

            raise TypeError(f"Unsupported state: {type(state)}")

        if isinstance(o, ChatHandler):
            return {
                "chat_id": o.chat_id,
                "state": encode_state(o.state),
            }

        raise TypeError(f"Can only encode ChatHandler. But got {type(o)}")


class ChatHandlerDecoder:
    """JSON decoder for ChatHandler class.
    Return ChatHandler object from JSON dict."""

    def __init__(self, client: TelegramClient, state_factory: BotStateFactory):
        self.client = client
        self.state_factory = state_factory

    def decode(self, dct) -> ChatHandler:
        """Reassemble ChatHandler object from primitive data types."""

        chat_id = dct["chat_id"]
        proto_state = dct["state"]
        state_name = proto_state["state_name"]
        is_on_enter_called = proto_state["is_on_enter_called"]

        if state_name == "GreetingState":
            state = GreetingState(self.client, self.state_factory, is_on_enter_called)
        elif state_name == "IdleState":
            state = IdleState(self.client, self.state_factory, is_on_enter_called)
        elif state_name == "GameState":
            state = GameState(
                self.client,
                self.state_factory,
                jsons.load(proto_state["game_params"], cls=ProtoGameState),
                is_on_enter_called,
            )
        else:
            raise TypeError(f"Can't deserialize state. Unknown name: {state_name}")

        return ChatHandler(state, chat_id)
