import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Tuple

import psycopg


class QuestionStorage(ABC):
    """An interface for accessing questions."""

    @abstractmethod
    def get_questions(self, max_num_questions: int) -> List["Question"]:
        """pass"""


class PostgresQuestionStorage(QuestionStorage):
    """Concrete implementation for questions from PostgreSQL database."""

    def __init__(self):
        self.user = os.environ["TRIVIA_POSTGRES_USER"]
        self.password = os.environ["TRIVIA_POSTGRES_PASSWD"]
        self.host = "localhost"
        self.dbname = "postgres"
        self.port = 5432
        self.conninfo = (
            f"postgresql://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.dbname}"
        )

    def get_questions(self, max_num_questions: int) -> List["Question"]:
        # pylint: disable = not-context-manager
        with psycopg.connect(self.conninfo) as conn:
            questions = []
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT id FROM questions\n"
                    f"ORDER BY random()\n"
                    f"LIMIT {max_num_questions};"
                )
                psycopg_questions_id = cur.fetchall()
                # transform psycopg list containing questions' id to the most pythonic list
                random_value_list = [
                    question_id[0] for question_id in psycopg_questions_id
                ]
                for value in random_value_list:
                    cur.execute(
                        f"SELECT id, question, text, is_correct FROM questions\n"
                        f"INNER JOIN answers ON questions.id = answers.question_id\n"
                        f"WHERE id = {value}\n"
                        f"ORDER BY id, text;"
                    )
                    for record in cur:
                        questions.append(record)
            return _format_to_question_model(random_value_list, questions)


class InMemoryStorage(QuestionStorage):
    """Concrete implementation for questions from local memory."""

    def get_questions(self, max_num_questions: int) -> List["Question"]:
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
