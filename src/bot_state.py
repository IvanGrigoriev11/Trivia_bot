from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from format import make_answered_question_message, make_keyboard
from storage import Question, Storage
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

    def __init__(self, _on_enter_called: bool):
        self._on_enter_called = _on_enter_called

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

    def __eq__(self, other):
        # pylint: disable = unidiomatic-typecheck
        if isinstance(other, BotState) and type(self) == type(other):
            return self.is_on_enter_called == other.is_on_enter_called
        return False

    @property
    def is_on_enter_called(self):
        return self._on_enter_called


class IdleState(BotState):
    """A state when there is no active game in place."""

    def __init__(
        self,
        client: TelegramClient,
        state_factory: "BotStateFactory",
        _on_enter_called: bool = False,
    ):
        super().__init__(_on_enter_called)
        self._client = client
        self._state_factory = state_factory

    def _do_on_enter(self, chat_id: int) -> None:
        pass

    def _do_process(self, update: Update) -> "BotState":
        if update.message is not None:
            text = update.message.text.lower()
            chat_id = update.message.chat.id

            if text == "/startgame":
                self._client.send_text(chat_id, "Starting game!")
                return self._state_factory.make_game_state()

            self._client.send_text(chat_id, "Type /startGame to start a new game.")
        return self


@dataclass
class ProtoGameState:
    """A serializable part of the GameState. Used to store and load the state."""

    questions: List[Question]
    current_question: int
    score: int
    last_question_msg_id: int


class GameState(BotState):
    """A state responsible for handling the game itself. Assumes the game has already started."""

    def __init__(
        self,
        client: TelegramClient,
        state_factory: "BotStateFactory",
        game_params: ProtoGameState,
        _on_enter_called: bool = False,
    ):
        """
        questions -- questions for this particular game.
        """
        super().__init__(_on_enter_called)
        self._client = client
        self._state_factory = state_factory
        self._params = game_params

    def __eq__(self, other):
        if isinstance(other, GameState):
            return self._params == other._params and super().__eq__(other)
        return False

    @property
    def game_params(self) -> ProtoGameState:
        return self._params

    def _do_on_enter(self, chat_id: int) -> None:
        self._params.last_question_msg_id = self._client.send_text(
            chat_id,
            self._params.questions[self._params.current_question].text,
            make_keyboard(self._params.questions[self._params.current_question]),
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
        cur_question = self._params.questions[self._params.current_question]
        if answer < 0 or answer >= len(cur_question.answers):
            self._client.send_text(
                chat_id, f"Type the number from 1 to {len(cur_question.answers)}"
            )
            return self

        if (
            answer
            == self._params.questions[self._params.current_question].correct_answer
        ):
            self._params.score += 1

        self._client.edit_message_text(
            MessageEdit(
                chat_id,
                self._params.last_question_msg_id,
                make_answered_question_message(
                    answer, self._params.questions[self._params.current_question]
                ),
            ),
        )
        self._params.current_question += 1

        if self._params.current_question != len(self._params.questions):
            self._params.last_question_msg_id = self._client.send_text(
                chat_id,
                self._params.questions[self._params.current_question].text,
                make_keyboard(self._params.questions[self._params.current_question]),
            )
            return self

        self._client.send_text(
            chat_id,
            f"You got {self._params.score} points out of {self._params.current_question}."
            + "\n"
            + "If you want to try again, type /startGame to start a new game.",
        )
        return self._state_factory.make_idle_state()


class GreetingState(BotState):
    """A state responsible for greeting and introducing new user to the bot."""

    def __init__(
        self,
        client: TelegramClient,
        state_factory: "BotStateFactory",
        _on_enter_called: bool = False,
    ):
        super().__init__(_on_enter_called)
        self._client = client
        self._state_factory = state_factory

    def _do_on_enter(self, chat_id: int) -> None:
        pass

    def _do_process(self, update: Update) -> "BotState":
        self._client.send_text(
            update.chat_id,
            "Hello. I am Trivia Bot. If you want to play the game,\n"
            "please type /startGame",
        )
        return self._state_factory.make_idle_state()


class BotStateFactory:
    """A factory responsible for creating a new bot state."""

    def __init__(self, client: TelegramClient, storage: Storage):
        self._client = client
        self._storage = storage

    def make_game_state(self):
        _question_count = 5
        if self._storage is not None:
            return GameState(
                self._client,
                self,
                ProtoGameState(self._storage.get_questions(_question_count), 0, 0, 0),
            )
        raise TypeError("Storage must be chosen for creating game state")

    def make_idle_state(self):
        return IdleState(self._client, self)

    def make_greeting_state(self):
        return GreetingState(self._client, self)
