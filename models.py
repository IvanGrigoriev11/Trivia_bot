from dataclasses import dataclass
from typing import List


@dataclass
class Question:
    text: str
    answers: List[str]
    correct_answer: int

    @staticmethod
    def make_some() -> List["Question"]:
        return [
            Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
            Question("2.How much is 2 + 5?", ["4", "10", "7", "8"], 2),
            Question(
                "3.What date is Christmas?", ["Dec 24", "Apr 15", "Jan 1", "Dec 25"], 3
            ),
        ]
