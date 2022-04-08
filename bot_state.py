from abc import ABC, abstractclassmethod
from models import Question
from telegram_client import TelegramClient, Update
from typing import List


class BotState(ABC):
    """A class responsible for handling a single chat operation."""

    @abstractclassmethod
    def on_enter(self, chat_id: int) -> None:
        """A callback when this bot state becomes active. Can be used to
        e.g. proactively send a message to the chat."""
        pass

    @abstractclassmethod
    def process(self, update: Update) -> 'BotState':
        """A callback for handling an update."""
        pass


class IdleState(BotState):
    """A state when there is no active game in place."""

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
    """A state responsible for handling the game itself. Assumes the game has already started."""

    def __init__(self, client: TelegramClient, questions: List[Question]):
        """
        questions -- questions for this particular game.
        """
        self._client = client
        self._questions = questions
        self.cur_question = 0
        self.score = 0

    def on_enter(self, chat_id: int) -> None:
        # TODO: send the first question to the chat
        self._send_question(chat_id, self._questions[0])

    def process(self, update: Update) -> 'BotState':
        chat_id = update.message.chat.id

        # TODO: use try/except to handle int conversion error
        try:
            if int(update.message.text) == self._questions[self.cur_question].correct_answer:    
                self._client.send_text(chat_id, f'You are right')
                self.score += 1 
            else:
                self._client.send_text(chat_id, f'You are wrong')
            
            self.cur_question += 1 
        except ValueError: 
            self._client.send_text(chat_id, f'please, type the number of your supposed answer')

        if self.cur_question != len(self._questions):
            self._send_question(chat_id, self._questions[self.cur_question])
            return self

        self._client.send_text(chat_id, f'You got {self.score} points out of {self.cur_question}.' + '\n' +
        'If you want to try again, type /startGame to start a new game.')
        return IdleState(self._client)


    def _send_question(self, chat_id: int, question: Question):
        self._client.send_text(chat_id, f'{question.text}' + '\n' + f'{question.answers}')
