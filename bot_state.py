from abc import ABC, abstractclassmethod
from models import Question
from telegram_client import TelegramClient, Update
from typing import List


class BotState(ABC):
    """A class used to as State interface"""

    @abstractclassmethod
    def on_enter(self, chat_id: int) -> None: pass

    @abstractclassmethod
    def process(self, update: Update) -> 'BotState': pass



class IdleState(BotState):
    """A child class used to represent TelegramBot's state in idle time
    
    Attributes
    ----------
    client : TelegramClient
        Used to determine which client is chatting with bot
    text : str 
        A formatted string used to receive the text from Client 
    chat_id : int 
        A variable used to receive Client's Telegram chat ID 

    Methods
    -------
    on_enter(chat_id: int)
        The method does nothing

    process (update: Update)
        The method receives last updates from Client and run the game    
    """

    def __init__(self, client: TelegramClient):
        self._client = client

    def on_enter(self, chat_id: int) -> None:
        pass

    def process(self, update: Update) -> 'BotState':
        """The method receives last updates from Client and run the game

        Parameteres
        -----------
        text : str 
            A formatted string used to receive the text from Client 
        chat_id : int 
            A variable used to receive Client's Telegram chat ID 
        """

        text = update.message.text.lower()
        chat_id = update.message.chat.id

        if text == '/startgame':
            self._client.send_text(chat_id, 'Starting game!')
            return GameState(self._client, Question.make_some())
        
        self._client.send_text(chat_id, 'Type /startGame to start a new game.')
        return self


class GameState(BotState):
    """A child class used to represent TelegramBot state in game time

    Attributes
    ----------
    client : TelegramClient
        Used to determine which client is chatting with bot
    questions: List 
        A list with a question

    Methods
    -------
    on_enter(chat_id: int)
        The method toggles bot states

    process (update: Update)
        The method receives last updates from Client
    """

    def __init__(self, client: TelegramClient, questions: List[Question]):
        self._client = client
        self._questions = questions
        self.cur_question = 0
        self.score = 0

    def on_enter(self, chat_id: int) -> None:
        """
        """

        # TODO: send the first question to the chat
        self._send_question(chat_id, self._questions[0])

    def process(self, update: Update) -> 'BotState':
        """

        Parameters
        ----------
        update: Update
            A variable used to receive last updates, especially client's chat ID
        """

        chat_id = update.message.chat.id

        # use try/except to handle int conversion error
        if int(update.message.text) == self._questions[self.cur_question].correct_answer:    
            self._client.send_text(chat_id, f'You are right')
            self.score += 1 
        else:
            self._client.send_text(chat_id, f'You are wrong')
        
        self.cur_question += 1 
        
        if self.cur_question != len(self._questions):
            self._send_question(chat_id, self._questions[self.cur_question])
        else:    
            self._client.send_text(chat_id, f'You got {self.score} points out of {self.cur_question}.' + '\n' +
            'If you want to try again, type /startGame to start a new game.')
            return IdleState(self._client)
        
        return self

    def _send_question(self, chat_id: int, question: Question):
        self._client.send_text(chat_id, f'{question.text}' + '\n' + f'{question.answers}')
