from abc import ABC, abstractclassmethod
from models import Question
from telegram_client import TelegramClient, Update
from typing import List


class BotState(ABC):
    @abstractclassmethod
    def on_enter(self, chat_id: int) -> None: pass

    @abstractclassmethod
    def process(self, update: Update) -> 'BotState': pass


class IdleState(BotState):
    def __init__(self, client: TelegramClient):
        self._client = client

    def on_enter(self, chat_id: int) -> None:
        pass

    def process(self, update: Update) -> 'BotState':
        text = update.message.text.lower()
        chat_id = update.message.chat.id

        if text == '/startgame':
            self._client.send_text(chat_id, 'Starting game!')
            return GameState(self._client, Question.make_some())
        
        self._client.send_text(chat_id, 'Type /startGame to start a new game.')
        return self


class GameState(BotState):
    def __init__(self, client: TelegramClient, questions: List[Question]):
        self._client = client
        self._questions = questions

    def on_enter(self, chat_id: int) -> None:
        # TODO: send the first question to the chat
        self._client.send_text(chat_id, f'GameState.on_enter({chat_id})')

    def process(self, update: Update) -> 'BotState':
        chat_id = update.message.chat.id
        self._client.send_text(chat_id, f'GameState.process()')
        return self
