import itertools
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from psycopg_pool import ConnectionPool
from psycopg.types.json import Jsonb


@dataclass
class Question:
    text: str
    answers: List[str]
    correct_answer: int


class Storage(ABC):
    """An interface for accessing questions."""

    @abstractmethod
    def get_records(self, count_records: int):
        """Get records from a database.
        This method is true for both QuestionStorage and HandlerStorage.
        The number of records is limited by 'record_count' parameter."""


@dataclass
class PostgresQuestionRecord:
    id: int
    question: str
    answer: str
    is_correct: bool


class PostgresQuestionStorage(Storage):
    """Questions storage over a PostgreSQL database."""

    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def get_records(self, count_records: int) -> List[Question]:
        """Get questions from PostgreSQL database.
        Calling the method multiple time will result in a different set of questions."""

        # pylint: disable = not-context-manager
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT id, question, text, is_correct FROM questions
                    INNER JOIN answers ON questions.id = answers.question_id
                    WHERE id IN (
                        SELECT id FROM questions
                        ORDER BY random()
                        LIMIT {count_records}
                    )
                    ORDER BY id, text;
                """
                )
                questions = [PostgresQuestionRecord(*r) for r in cur]
        game_questions = []
        for _, group_ in itertools.groupby(questions, lambda q: q.id):
            group: List[PostgresQuestionRecord] = list(group_)
            text = group[0].question
            answers = [x.answer for x in group]
            correct_answer = [y.is_correct for y in group].index(True)
            game_questions.append(Question(text, answers, correct_answer))

        return game_questions


class InMemoryStorage(Storage):
    """Storage that holds data in-memory."""

    def __init__(self, questions: List[Question]):
        self._questions = questions

    def get_records(self, count_records: int) -> List[Question]:
        """Get questions from inner memory."""

        return self._questions[:count_records]


class HandlerStorage(Storage):
    """Handlers storage over a PostgreSQL database."""

    def __init__(self, pool: ConnectionPool, chat_id: int):
        self._pool = pool
        self._chat_id = chat_id

    def get_records(self, count_records: int):
        """Read the serialized chat_handler from the DB for a particular chat_id."""

        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT string FROM handlers
                    WHERE string->'chat_handler'->>'chat_id' = '{self._chat_id}'
                    ORDER BY id DESC
                    LIMIT '{count_records}';
                    """
                )
                json_chat_handler = json.dumps(cur.fetchone()[0])
                return json_chat_handler

    def store(self, json_chat_handler: str):
        """Save the serialized chat_handler to DB."""

        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO handlers(string)
                    VALUES ('{json_chat_handler}');
                    """
                )
