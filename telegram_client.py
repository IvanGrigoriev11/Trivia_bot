import requests
from typing import List
from abc import abstractclassmethod, ABC


from dataclasses import dataclass
import marshmallow_dataclass as mdc
from typing import List
import marshmallow


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


class TelegramClient(ABC):
    @abstractclassmethod
    def get_updates(self, offset: int = 0) -> List[Update]: pass

    @abstractclassmethod
    def send_message(self, payload: SendMessagePayload) -> None: pass

    def send_text(self, chat_id: int, text: str) -> None:
        self.send_message(SendMessagePayload(chat_id, text))


class LiveTelegramClient(TelegramClient):
    def __init__(self, token: str) -> None:
        self._token = token

    def get_updates(self, offset: int = 0) -> List[Update]:
        data = requests.get(f'https://api.telegram.org/bot{self._token}/getUpdates?offset={offset}').text
        response: GetUpdatesResponse = GetUpdatesResponseSchema.loads(data)
        print(response.result)
        return response.result

    def send_message(self, payload: SendMessagePayload) -> None:
        
        data = SendMessagePayloadSchema.dump(payload)
        print(data)
        r = requests.post(f'https://api.telegram.org/bot{self._token}/sendMessage', data=data)
        assert r.status_code == 200, f'Expected status code 200 but got {r.status_code}'
