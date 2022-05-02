from tutils import FakeTelegramClient

from bot_state import IdleState
from telegram_client import Chat, Message, SendMessagePayload, Update


def check_idle_state(user_message: str, expected_bot_message: str, callback_query: None):
    client = FakeTelegramClient()
    state = IdleState(client)
    chat_id = 111
    state.on_enter(chat_id)
    state.process(Update(123, Message(Chat(chat_id), user_message), callback_query))
    assert client.sent_messages == [
        SendMessagePayload(chat_id, expected_bot_message, callback_query)]


def test_process_starting_game():
    check_idle_state("/startGame", "Starting game!", None)


def test_process_other_message():
    check_idle_state("other message", "Type /startGame to start a new game.", None)
