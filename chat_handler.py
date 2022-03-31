from bot_state import BotState
from telegram_client import Update


class ChatHandler:
    """A method used to handle chatting with multiple clients

    Attributes
    ----------
    initial_state : BotState
        Initial bot state 
    chat_id : int
        A variable shown client's ID 

    Method
    ------
    process(update: Update)
        A method toggles between previous and future states    
    """

    def __init__(self, initial_state: BotState, chat_id: int) -> None:
        self._state = initial_state
        self._chat_id = chat_id

    def process(self, update: Update) -> None:
        """The method toggles bot states"""

        new_state = self._state.process(update)
        if new_state != self._state:
            new_state.on_enter(self._chat_id)

        self._state = new_state
