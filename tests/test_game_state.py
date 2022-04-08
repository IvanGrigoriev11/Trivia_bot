from keyword import kwlist
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


def check(user_message, expected_bot_message):
    client = FakeTelegramClient()
    questions = List[Question]
    state = GameState(client, questions)
    chat_id = 111
    cur_question = 1
    questions[cur_question].correct_answer = 1
    state.process(Update(123, Message(Chat(chat_id), user_message)))
    

    assert client.sent_messages == [
        SendMessagePayload(chat_id, expected_bot_message)
    ]

def test_test():
    check(1, 'You are right')




