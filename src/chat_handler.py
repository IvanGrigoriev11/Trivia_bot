from dataclasses import dataclass

from bot_state import BotState
from telegram_client import Update


@dataclass(frozen=True)
class ProtoChatHandler:
    """A serializable part of the ChatHandler. Used to store and load ChatHandler."""

    state: BotState
    chat_id: int


class ChatHandler:
    """A top-level handler responsible for driving communications within a single chat.
    It works by implementing a state machine over `BotState`s."""

    def __init__(self, initial_state: BotState, chat_id: int) -> None:
        """
        initial_state -- initial state responsible for handling chat updates.
        chat_id -- id of the chat this handler is responsible for.
        """

        self._state = initial_state
        self._chat_id = chat_id

    def process(self, update: Update) -> None:
        """Processes a given `update`."""

        new_state = self._state.process(update)
        if new_state != self._state:
            new_state.on_enter(self._chat_id)

        self._state = new_state

    @staticmethod
    def create(state: BotState, chat_id: int):
        """Method initialize default state for chat handler
        at the very beginning of the game"""

        state.on_enter(chat_id)
        return ChatHandler(state, chat_id)

    @property
    def proto(self):
        return ProtoChatHandler(self._state, self._chat_id)

    def __eq__(self, other):
        if isinstance(other, ChatHandler):
            return self._chat_id == other._chat_id and self._state == other._state

        return False
