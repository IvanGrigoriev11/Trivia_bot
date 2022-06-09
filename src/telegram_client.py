from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

import jsons
import requests

from utils import transform_keywords


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
class User:
    id: int


@dataclass
class CallbackQuery:
    """A class used to represent the special data from keyboard.

    Attributes
    ----------
    from_ : User
        unique user's identifier

    data : str
        unique information sent by the user after clicking any button
    """

    from_: User
    data: str


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
        An increasing update identifier. Each subsequent updates will have larger update_id
    message : Optional[Message]
        An attribute represents a message from user
    callback_query : Optional[CallbackQuery]
        An attribute represents a data from keyboard
    """

    update_id: int
    message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None

    @property
    def chat_id(self) -> int:
        assert (
            len([x for x in (self.message, self.callback_query) if x is not None]) == 1
        )

        if self.message is not None:
            return self.message.chat.id
        if self.callback_query is not None:
            return self.callback_query.from_.id

        assert False, "Unreachable"


@dataclass
class GetUpdatesResponse:
    """Http response from Telegram for receiving updates."""

    result: List[Update]


@dataclass
class SendMessageResponseResult:
    message_id: int


@dataclass
class SendMessageResponse:
    """Http response from Telegram for receiving message id.

    Attributes
    ----------
    result : SendMessageResponseResult
        response result with a unique message identifier
    """

    result: SendMessageResponseResult


@dataclass
class InlineKeyboardButton:
    """A class contains special data about button."""

    text: str
    callback_data: str


@dataclass
class InlineKeyboardMarkup:
    """This class represents a keyboard that appears right next to the message it belongs to."""

    inline_keyboard: List[List[InlineKeyboardButton]]


@dataclass
class SendMessagePayload:
    """Bot request to send a message to a chat."""

    chat_id: int
    text: str
    reply_markup: Optional[InlineKeyboardMarkup] = None


@dataclass
class MessageEdit:
    """Bot request to edit a necessary message."""

    chat_id: int
    message_id: int
    text: str


class TelegramClient(ABC):
    """An interface for communicating with Telegram backend."""

    @abstractmethod
    def get_updates(self, offset: int = 0) -> List[Update]:
        """Gets updates from the telegram with `update_id` bigger than `offset`."""

    @abstractmethod
    def send_message(self, payload: SendMessagePayload) -> int:
        """Sends message with a given `payload` to Telegram and returns the id of this message."""

    @abstractmethod
    def edit_message_text(self, payload: MessageEdit) -> None:
        """Edits the text of the selected message."""

    def send_text(
        self,
        chat_id: int,
        text: str,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> int:
        """Forms the right construction of the message."""

        return self.send_message(SendMessagePayload(chat_id, text, reply_markup))


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
        response = jsons.loads(
            data, cls=GetUpdatesResponse, key_transformer=transform_keywords
        )
        return response.result

    def send_message(self, payload: SendMessagePayload) -> int:
        data = jsons.dump(payload, strip_nulls=True)
        r = requests.post(
            f"https://api.telegram.org/bot{self._token}/sendMessage", json=data
        )
        assert r.status_code == 200, f"Expected status code 200 but got {r.status_code}"
        message_id = jsons.loads(r.text, cls=SendMessageResponse).result.message_id
        return message_id

    def edit_message_text(self, payload: MessageEdit) -> None:
        data = jsons.dump(payload, strip_nulls=True)
        r = requests.post(
            f"https://api.telegram.org/bot{self._token}/editMessageText", json=data
        )
        assert r.status_code == 200, f"Expected status code 200 but got {r.status_code}"
