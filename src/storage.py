import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cache
from typing import Dict, List, Optional

from psycopg import Cursor
from psycopg_pool import ConnectionPool


@dataclass
class Question:
    """Question model.

    text: the question text
    answers: List of answers for the question
    correct_answer: the number of right answer 0-based
    """

    text: str
    answers: List[str]
    correct_answer: int


@dataclass
class PostgresQuestionRecord:
    """Intermediate question piece representation. Questions are stored in Postgres in 2
    table: questions and answers. Each record in questions will have one or more corresponding
    entries in the answers table. Example:

    questions:
    | id | text                          |
    | 25 | what is the color of the sky? |

    answers:
    | id | question id | text |
    | 2  | 25          | red  |
    | 3  | 25          | blue |

    This class is an augmented `answers` table record. Question id and text is added to it from the
    `questions` table.

    id: question id
    question: text of the question
    answer: text of an answer
    is_correct: whether the answer is correct
    """

    id: int
    question: str
    answer: str
    is_correct: bool


class Storage(ABC):
    """An interface for accessing and updating the game data (questions, chat states etc.)."""

    @abstractmethod
    def get_questions(self, question_count: int) -> List[Question]:
        """Gets `question_count` questions. Questions may be selected at random.
        Calling the method multiple time may result in a different set of questions."""

    @abstractmethod
    def get_chat_handler(self, chat_id: int) -> Optional[str]:
        """Read the serialized chat_handler from the DB for a specific chat_id.
        Returns None if chat handler for `chat_id` is not found.
        """

    @abstractmethod
    def set_chat_handler(self, chat_id: int, chat_handler: str):
        """Save serialized chat_handler to the DB or internal memory."""


class PostgresStorage(Storage):
    """Data storage over a PostgreSQL database."""

    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def get_questions(self, question_count: int) -> List[Question]:
        # pylint: disable = not-context-manager
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, question, text, is_correct FROM questions
                    INNER JOIN answers ON questions.id = answers.question_id
                    WHERE id IN (
                        SELECT id FROM questions
                        ORDER BY random()
                        LIMIT (%s)
                    )
                    ORDER BY id, text;
                    """,
                    (question_count,),
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

    def get_chat_handler(self, chat_id: int) -> Optional[str]:
        """Read the serialized chat_handler from the DB for a particular chat_id."""

        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                self._ensure_chat_handler_table(cur)
                cur.execute(
                    """
                    SELECT chat_handler FROM handlers
                    WHERE chat_id = (%s);
                    """,
                    (chat_id,),
                )
                json_chat_handler = cur.fetchone()
                if json_chat_handler:
                    return json_chat_handler[0]

                return None

    def set_chat_handler(self, chat_id: int, chat_handler: str):

        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                self._ensure_chat_handler_table(cur)
                cur.execute(
                    """
                    INSERT INTO handlers(chat_id, chat_handler)
                    VALUES(%s, %s)
                    ON CONFLICT(chat_id) DO UPDATE
                    SET chat_handler = excluded.chat_handler;
                    """,
                    (
                        chat_id,
                        chat_handler,
                    ),
                )

    @cache
    def _ensure_chat_handler_table(self):
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS handlers (
                        chat_id integer PRIMARY KEY,
                        chat_handler text
                        )
                    """
                )


class InMemoryStorage(Storage):
    """Storage that holds data in-memory."""

    def __init__(self, questions: List[Question]):
        self._questions = questions
        self._chat_handlers: Dict[int, str] = {}

    def get_questions(self, question_count: int) -> List[Question]:
        return self._questions[:question_count]

    def get_chat_handler(self, chat_id: int) -> Optional[str]:
        return self._chat_handlers[chat_id]

    def set_chat_handler(self, chat_id: int, chat_handler: str):
        self._chat_handlers[chat_id] = chat_handler
