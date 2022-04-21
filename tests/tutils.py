from typing import Callable, List, Tuple

from telegram_client import Chat, Message, SendMessagePayload, TelegramClient, Update


class FakeTelegramClient(TelegramClient):
    def __init__(self):
        self.sent_messages: List[SendMessagePayload] = []

    def get_updates(self, offset: int = 0) -> List[Update]:
        raise NotImplementedError()

    def send_message(self, payload: SendMessagePayload) -> None:
        self.sent_messages.append(payload)


def check_conversation(
    chat_id: int,
    conversation: List[Tuple[bool, str]],
    client: FakeTelegramClient,
    handle: Callable[[Update], None],
):
    last_message_from_bot = 0
    update_id = 111
    for bot, message in conversation:
        if bot:
            assert client.sent_messages[last_message_from_bot] == SendMessagePayload(
                chat_id, message
            )
            last_message_from_bot += 1
        else:
            handle(Update(update_id, Message(Chat(chat_id), message)))
