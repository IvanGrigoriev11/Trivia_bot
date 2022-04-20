from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

import marshmallow
import marshmallow_dataclass as mdc
import requests


@dataclass
class Chat:
    """A class used to represent a Telegram Chat.

    Attribute
    ---------
    id : int
        chat id
    """

    id: int


@dataclass
class Message:
    """A class used to represent a Telegram Message.

    Attributes
    ----------
    chat : Chat
        chat the message came from
    text : str
        text of the message
    """

    chat: Chat
    text: str


@dataclass
class Update:
    """A class used to represent Telegram updates that a bot can receive.

    Attributes
    ----------
    update_id : int
        An increasing update identifier. Each subsequent updates will have larger update_id.
    """

    update_id: int
    message: Message


@dataclass
class GetUpdatesResponse:
    """Http response from Telegram for recieving updates."""

    result: List[Update]


@dataclass
class SendMessagePayload:
    """Bot request to send a message to a chat."""

    chat_id: int
    text: str


class BaseSchema(marshmallow.Schema):
    class Meta:
        unknown = marshmallow.EXCLUDE


GetUpdatesResponseSchema = mdc.class_schema(
    GetUpdatesResponse, base_schema=BaseSchema
)()
SendMessagePayloadSchema = mdc.class_schema(SendMessagePayload)()


class TelegramClient(ABC):
    """An interface for communicating with Telegram backend."""

    @abstractmethod
    def get_updates(self, offset: int = 0) -> List[Update]:
        """Gets updates from the telegram with `update_id` bigger than `offset`."""
        pass

    @abstractmethod
    def send_message(self, payload: SendMessagePayload) -> None:
        """Sends message with a given `payload` to Telegram."""
        pass

    def send_text(self, chat_id: int, text: str) -> None:
        self.send_message(SendMessagePayload(chat_id, text))


class LiveTelegramClient(TelegramClient):
    """An implementation of the `TelegramClient` for communicating with an actual backend."""

    def __init__(self, token: str) -> None:
        """
        token -- Telegram bot token.
        """
        self._token = token

    def get_updates(self, offset: int = 0) -> List[Update]:
        data = requests.get(
            f"https://api.telegram.org/bot{self._token}/getUpdates?offset={offset}"
        ).text
        response: GetUpdatesResponse = GetUpdatesResponseSchema.loads(data)
        print(response.result)
        return response.result

    def send_message(self, payload: SendMessagePayload) -> None:
        # TODO: handle Telegram errors.
        data = SendMessagePayloadSchema.dump(payload)
        print(data)
        r = requests.post(
            f"https://api.telegram.org/bot{self._token}/sendMessage", data=data
        )
        assert r.status_code == 200, f"Expected status code 200 but got {r.status_code}"
