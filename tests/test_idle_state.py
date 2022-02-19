from bot_state import IdleState
from telegram_client import TelegramClient, Update, SendMessagePayload, Message, Chat
from typing import List


class FakeTelegramClient(TelegramClient):
    def __init__(self):
        self.sent_messages: List[SendMessagePayload] = []

    def get_updates(self, offset: int = 0) -> List[Update]:
        raise NotImplementedError()

    def send_message(self, payload: SendMessagePayload) -> None:
        self.sent_messages.append(payload)


def check(user_message: str, expected_bot_message: str):
    client = FakeTelegramClient()
    state = IdleState(client)
    chat_id = 111
    state.process(Update(123, Message(Chat(chat_id), user_message)))

    assert client.sent_messages == [
        SendMessagePayload(chat_id, expected_bot_message)
    ]


def test_process_starting_game():
    check('/startGame', 'Starting game!')


def test_process_other_message():
    check('other message', 'Type /startGame to start a new game.')
