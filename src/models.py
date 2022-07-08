from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


class QuestionStorage(ABC):

    @abstractmethod
    def execute(self) -> List[str]:
        pass


class QuestionInterface:
    strategy: QuestionStorage  # interface

    def set_strategy(self, strategy):
        if strategy is InMemoryStorage:
            self.strategy = strategy
        else:
            self.strategy = PostgresMemory()

    def execute_strategy(self):
        self.strategy.execute()


class PostgresMemory(AbstractQuestionClass):
    def execute(self) -> List[str]:
        return ["from database"]


class InMemoryStorage(AbstractQuestionClass):
    def execute(self) -> List["Question"]:
        return [
            Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
            Question("2.How much is 2 + 5?", ["4", "10", "7", "8"], 2),
            Question(
                "3.What date is Christmas?", ["Dec 24", "Apr 15", "Jan 1", "Dec 25"], 3
            ),
        ]


@dataclass
class PostgresMemory:
    category: str
    type: str
    difficulty: str
    question: str
    correct_answer: str
    incorrect_answers: List[str]


@dataclass
class Question:
    text: str
    answers: List[str]
    correct_answer: int
