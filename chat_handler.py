from bot_state import BotState
from telegram_client import Update


class ChatHandler:
    def __init__(self, initial_state: BotState, chat_id: int) -> None:
        self._state = initial_state
        self._chat_id = chat_id

    def process(self, update: Update) -> None:
        new_state = self._state.process(update)
        if new_state != self._state:
            new_state.on_enter(self._chat_id)

        self._state = new_state
