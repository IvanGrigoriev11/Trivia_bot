from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Tuple

import psycopg


class QuestionStorage(ABC):
    """An interface for accessing questions."""

    @abstractmethod
    def get_questions(self, question_count: int) -> List["Question"]:
        """Gets `question_count` questions. Questions may be selected at random.
        Calling the method multiple time will result in a different set of questions."""


class PostgresQuestionStorage(QuestionStorage):
    """Questions storage over a PostgreSQL database."""

    def __init__(self, conninfo: str):
        self._conninfo = conninfo
        self._connection: Optional[psycopg.Connection] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close_connection()

    def _get_connection(self) -> psycopg.Connection:
        if self._connection is None or self._connection.closed:
            self._connection = psycopg.connect(self._conninfo)

        return self._connection

    def close_connection(self):
        if self._connection:
            self._connection.close()

    def get_questions(self, question_count: int) -> List["Question"]:
        # pylint: disable = not-context-manager
        with psycopg.connect(self._conninfo) as conn:
            questions = []
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT id FROM questions\n"
                    f"ORDER BY random()\n"
                    f"LIMIT {question_count};"
                )
                psycopg_questions_id = cur.fetchall()
                # transform psycopg list containing questions' id to the most pythonic list
                question_ids = [
                    question_id[0] for question_id in psycopg_questions_id
                ]
                for value in question_ids:
                    cur.execute(
                        f"SELECT id, question, text, is_correct FROM questions\n"
                        f"INNER JOIN answers ON questions.id = answers.question_id\n"
                        f"WHERE id = {value}\n"
                        f"ORDER BY id, text;"
                    )
                    for record in cur:
                        questions.append(record)
            return _format_to_question_model(question_ids, questions)


class InMemoryStorage(QuestionStorage):
    """Storage that holds data in-memory."""

    def get_questions(self, question_count: int) -> List["Question"]:
        return [
            Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
            Question("2.How much is 2 + 5?", ["4", "10", "7", "8"], 2),
            Question(
                "3.What date is Christmas?", ["Dec 24", "Apr 15", "Jan 1", "Dec 25"], 3
            ),
        ]


@dataclass
class Question:
    text: str
    answers: List[str]
    correct_answer: int


def _format_to_question_model(
    list_of_ids: List[int], questions: List[Tuple]
) -> List[Question]:
    """
    Transforms postgres transaction output into a list of `Question`.
    """

    element = 0
    temp = 0
    text = ""
    correct_answer = 0
    answer = []
    list_of_questions = []
    for question in questions:
        if question[0] == list_of_ids[element]:
            text = question[1]
            answer.append(question[2])
            if question[3]:
                correct_answer = temp
            temp += 1
        else:
            list_of_questions.append(Question(text, answer, correct_answer))
            element += 1
            temp = 0
            answer = [question[2]]
            if question[3]:
                correct_answer = temp
            temp += 1

    list_of_questions.append(Question(text, answer, correct_answer))
    return list_of_questions
