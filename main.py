from dataclasses import dataclass
from pydoc import cli
import marshmallow_dataclass as mdc
from typing import List
import requests
import marshmallow
import os

@dataclass
class Chat:
    id: int


@dataclass
class Message:
    chat: Chat
    text: str


@dataclass
class Update:
    update_id: int
    message: Message


@dataclass
class GetUpdatesResponse:
    result: List[Update]

@dataclass
class SendMessagePayload:
    chat_id: int
    text: str


class BaseSchema(marshmallow.Schema):
    class Meta:
        unknown = marshmallow.EXCLUDE


GetUpdatesResponseSchema = mdc.class_schema(GetUpdatesResponse, base_schema=BaseSchema)()
SendMessagePayloadSchema = mdc.class_schema(SendMessagePayload)()


class TelegramClient:
    def __init__(self, token: str) -> None:
        self._token = token

    def get_updates(self, offset: int = 0) -> List[Update]:
        data = requests.get(f'https://api.telegram.org/bot{self._token}/getUpdates').text
        response: GetUpdatesResponse = GetUpdatesResponseSchema.loads(data)
        return response.result

    def send_message(self, payload: SendMessagePayload) -> None:
        data = SendMessagePayloadSchema.dump(payload)
        r = requests.post(f'https://api.telegram.org/bot{self._token}/sendMessage', data=data)
        assert r.status_code == 200, f'Expected status code 200 but got {r.status_code}'


def main():
    #token = '5253161404:AAHesFGZ4_01ZaD1sjw7BM06Ghw5CTLaWFc'
    token = os.environ['TELEGRAM_BOT_TOKEN']
    client = TelegramClient(token)
    updates = client.get_updates()
    for update in updates:
        client.send_message(SendMessagePayload(
            update.message.chat.id,
            update.message.text
        ))


if __name__ == '__main__':
    main()