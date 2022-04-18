from bot_state import BotState, IdleState
from telegram_client import Update, TelegramClient


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
    def chat_handler(client: TelegramClient, chat_id: int):
        state = IdleState(client)
        state.on_enter(chat_id)
        return ChatHandler(state, chat_id)
