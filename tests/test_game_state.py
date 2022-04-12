from bot_state import GameState
from telegram_client import TelegramClient, Update, SendMessagePayload, Message, Chat
from typing import List
from models import Question


class FakeTelegramClient(TelegramClient):
    def __init__(self):
        self.sent_messages: List[SendMessagePayload] = []

    def get_updates(self, offset: int = 0) -> List[Update]:
        raise NotImplementedError()

    def send_message(self, payload: SendMessagePayload) -> None:
        self.sent_messages.append(payload)


def check(user_message: str, expected_messages: List[str]):
    client = FakeTelegramClient()
    questions = [
        Question("question 1", ["a", "b", "c"], 0),
        Question("question 2", ["a", "b", "c"], 1)
    ]
    state = GameState(client, questions)
    chat_id = 111
    state.on_enter(chat_id)
    state.process(Update(123, Message(Chat(chat_id), user_message)))

    expected_payloads = [SendMessagePayload(chat_id, text) for text in expected_messages]

    assert client.sent_messages == expected_payloads


def test_right_asnwer():
    check("0", [
        "question 1\n['a', 'b', 'c']",
        "You are right",
        "question 2\n['a', 'b', 'c']"
    ])


def test_wrong_answer():
    check("1", [
        "question 1\n['a', 'b', 'c']",
        "You are wrong",
        "question 2\n['a', 'b', 'c']"
    ])


def test_others_from_client():
    check("others", [
        "question 1\n['a', 'b', 'c']",
        "please, type the number of your supposed answer",
        "question 1\n['a', 'b', 'c']"
    ])
