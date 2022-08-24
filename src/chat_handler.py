from bot_state import BotState, GameState, GreetingState, IdleState
from telegram_client import Update


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
    def state(self):
        return self._state

    @property
    def chat_id(self):
        return self._chat_id

    def __eq__(self, other):
        if self._chat_id == other.chat_id:
            if isinstance(self._state, GreetingState):
                return isinstance(other.state, GreetingState)
            if isinstance(self._state, IdleState):
                return isinstance(other.state, IdleState)
            if isinstance(self._state, GameState):
                return isinstance(other.state, GameState)
        return False
