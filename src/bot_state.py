from abc import ABC, abstractmethod
from typing import List

from format import make_answered_question_message, make_keyboard
from models import Context, PostgresMemory, Question
from telegram_client import MessageEdit, TelegramClient, Update
from utils import parse_int


class BotStateException(Exception):
    pass


class InvalidCallbackDataException(BotStateException):
    def __init__(self, data: str):
        super().__init__()
        self.data = data


class BotState(ABC):
    """A class responsible for handling a single chat operation."""

    def __init__(self):
        self._on_enter_called = False

    def on_enter(self, chat_id: int) -> None:
        assert not self._on_enter_called
        self._on_enter_called = True
        self._do_on_enter(chat_id)

    def process(self, update: Update) -> "BotState":
        assert self._on_enter_called
        return self._do_process(update)

    @abstractmethod
    def _do_on_enter(self, chat_id: int) -> None:
        """A callback when this bot state becomes active. Can be used to
        e.g. proactively send a message to the chat."""

    @abstractmethod
    def _do_process(self, update: Update) -> "BotState":
        """A callback for handling an update."""


class IdleState(BotState):
    """A state when there is no active game in place."""

    def __init__(self, client: TelegramClient):
        super().__init__()
        self._client = client

    def _do_on_enter(self, chat_id: int) -> None:
        pass

    def _do_process(self, update: Update) -> "BotState":
        if update.message is not None:
            text = update.message.text.lower()
            chat_id = update.message.chat.id

            if text == "/startgame":
                self._client.send_text(chat_id, "Starting game!")
                return GameState(self._client, Context(PostgresMemory()).execute())

            self._client.send_text(chat_id, "Type /startGame to start a new game.")
        return self


class GameState(BotState):
    """A state responsible for handling the game itself. Assumes the game has already started."""

    def __init__(self, client: TelegramClient, questions: List[Question]):
        """
        questions -- questions for this particular game.
        """
        super().__init__()
        self._client = client
        self._questions = questions
        self._cur_question = 0
        self._score = 0
        self._last_question_msg_id = 0

    def _do_on_enter(self, chat_id: int) -> None:
        self._last_question_msg_id = self._client.send_text(
            chat_id, self._questions[0].text, make_keyboard(self._questions[0])
        )

    def _do_process(self, update: Update) -> "BotState":
        chat_id = update.chat_id
        if update.message is not None:
            answer = parse_int(update.message.text)
            if answer is None:
                self._client.send_text(
                    chat_id, "Please, type the number of your supposed answer"
                )
                return self
            answer -= 1
        elif update.callback_query is not None:
            answer = parse_int(update.callback_query.data)
            if answer is None:
                raise InvalidCallbackDataException(update.callback_query.data)
        else:
            return self
        return self._handle_answer(chat_id, answer)

    def _handle_answer(self, chat_id: int, answer: int):
        cur_question = self._questions[self._cur_question]
        if answer < 0 or answer >= len(cur_question.answers):
            self._client.send_text(
                chat_id, f"Type the number from 1 to {len(cur_question.answers)}"
            )
            return self

        if answer == self._questions[self._cur_question].correct_answer:
            self._score += 1

        self._client.edit_message_text(
            MessageEdit(
                chat_id,
                self._last_question_msg_id,
                make_answered_question_message(
                    answer, self._questions[self._cur_question]
                ),
            ),
        )
        self._cur_question += 1

        if self._cur_question != len(self._questions):
            self._last_question_msg_id = self._client.send_text(
                chat_id,
                self._questions[self._cur_question].text,
                make_keyboard(self._questions[self._cur_question]),
            )
            return self

        self._client.send_text(
            chat_id,
            f"You got {self._score} points out of {self._cur_question}."
            + "\n"
            + "If you want to try again, type /startGame to start a new game.",
        )
        return IdleState(self._client)
