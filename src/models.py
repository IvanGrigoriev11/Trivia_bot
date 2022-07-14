from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple
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
        user = os.environ["TRIVIA_POSTGRES_USER"]
        password = os.environ["TRIVIA_POSTGRES_PASSWD"]
        # pylint: disable = not-context-manager
        with psycopg.connect(
                host="localhost", dbname="postgres", user=user, password=password, port=5432
        ) as conn:
            questions = []
            with conn.cursor() as cur:
                for value in random_value_list:
                    cur.execute(
                        "SELECT id, question, text, is_correct FROM questions\n"
                        "INNER JOIN answers ON questions.id = answers.question_id\n"
                        "WHERE question_id = {}\n"
                        "ORDER BY text ASC;".format(value)
                        )
                    for record in cur:
                        questions.append(record)
            return _format_to_question_model(random_value_list, questions)


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


def _format_to_question_model(list_of_ids: List[int], questions: List[Tuple]) -> List[Question]:
    element = 0
    temp = 0
    text = ''
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
