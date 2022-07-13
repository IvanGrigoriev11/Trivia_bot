from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import psycopg
import os
import random


class QuestionStorage(ABC):
    """A strategy interface"""

    @abstractmethod
    def execute(self) -> List["Question"]:
        """pass"""


class PostgresMemory(QuestionStorage):
    """A concrete class"""

    def execute(self) -> List["Question"]:
        max_num_questions = 5
        random_value_list = random.sample(range(0, 4050), max_num_questions)
        print(random_value_list)
        user = os.environ["TRIVIA_POSTGRES_USER"]
        password = os.environ["TRIVIA_POSTGRES_PASSWD"]

        # pylint: disable = not-context-manager
        with psycopg.connect(
                host="localhost", dbname="postgres", user=user, password=password, port=5432
        ) as conn:
            with conn.cursor() as cur:
                for value in random_value_list:
                    cur.execute(
                        "SELECT id, question, text, is_correct FROM questions"
                        "INNER JOIN answers ON questions.id = answers.question_id"
                        "WHERE question_id = {};".format(value)
                        )
                    questions_list = questions_list.append(cur.fetchall())
        return [Question("from database", ["yes", "no"], 1)]


class InMemoryStorage(QuestionStorage):
    """A concrete class"""

    def execute(self) -> List["Question"]:
        return [
            Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
            Question("2.How much is 2 + 5?", ["4", "10", "7", "8"], 2),
            Question(
                "3.What date is Christmas?", ["Dec 24", "Apr 15", "Jan 1", "Dec 25"], 3
            ),
        ]


class Context:
    """This is the object whose behavior will change."""

    question: QuestionStorage

    def __init__(self, question):
        if type(question) is InMemoryStorage:
            self.question = InMemoryStorage()
        else:
            self.question = PostgresMemory()

    def execute(self) -> List["Question"]:
        return self.question.execute()


@dataclass
class Question:
    text: str
    answers: List[str]
    correct_answer: int


"""@dataclass
class Question:
    id: int
    question: str
    text: str
    is_correct: bool"""
