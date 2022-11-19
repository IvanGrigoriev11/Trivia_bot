from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import jsons
import requests
from requests.exceptions import ConnectionError
from utils import transform_keywords


@dataclass
class TelegramException(Exception):
    pass


@dataclass
class UnexpectedStatusCodeException(TelegramException):

    status_code: int
    msg: str


@dataclass
class NetworkException(TelegramException):

    msg: str


@dataclass
class UnknownErrorException(TelegramException):

    msg: str


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
    """A class represents a special kind of message
    when a user taps a preconfigured button attached to a message.

    Attributes
    ----------
    from_ : User
        The user who tapped the button.

    data : str
        The information attached to the button when a message with a preconfigured button was sent.
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
    The class contains two optional fields which represent special type of Telegram messages.
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
    result: SendMessageResponseResult


@dataclass
class InlineKeyboardButton:
    """A button of an inline keyboard attachable to a message.

    Attributes
    ----------
    text: str
        text displayed on the button
    callback_data: str
        any string associated with the button that will be sent back to the bot once
        the button is pressed. The maximum size for this field is 64 bytes.
    """

    text: str
    callback_data: str


@dataclass
class InlineKeyboardMarkup:
    """Layout of an inline keyboard that can be attached to messages.
    https://core.telegram.org/bots/api#inlinekeyboardmarkup"""

    inline_keyboard: List[List[InlineKeyboardButton]]


@dataclass
class SendMessagePayload:
    """Bot request to send a message to a chat."""

    chat_id: int
    text: str
    reply_markup: Optional[InlineKeyboardMarkup] = None


@dataclass
class MessageEdit:
    """Bot request to edit a previously sent message."""

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

        return self.send_message(SendMessagePayload(chat_id, text, reply_markup))


class LiveTelegramClient(TelegramClient):
    """An implementation of the `TelegramClient` for communicating with an actual backend."""

    def __init__(self, token: str) -> None:
        """
        token -- Telegram bot token.
        """
        self._token = token

    def get_updates(self, offset: int = 0) -> List[Update]:
        try:
            data = requests.get(
                f"https://api.telegram.org/bot{self._token}/getUpdates?offset={offset}"
            )
            response = jsons.loads(
                data.text, cls=GetUpdatesResponse, key_transformer=transform_keywords
            )
        except ConnectionError:
            raise NetworkException("Failed to establish a new connection.")
        except Exception as exc:
            raise UnknownErrorException(f"{exc}") from exc

        if data.status_code != 200:
            raise UnexpectedStatusCodeException(data.status_code, data.reason)
        return response.result

    def set_webhook(self, url: str, cert_path: Optional[str] = None) -> None:
        try:
            if cert_path is None:
                resp = requests.post(
                    f"https://api.telegram.org/bot{self._token}/setWebhook?url={url}",
                )
            else:
                cert = Path(cert_path)
                with open(cert, encoding="utf-8") as cert:
                    files = {"certificate": cert}
                    resp = requests.post(
                        f"https://api.telegram.org/bot{self._token}/setWebhook?url={url}",
                        files=files,
                    )
        except ConnectionError:
            raise NetworkException("Failed to establish a new connection.")
        except Exception as exc:
            raise UnknownErrorException(f"{exc}") from exc

        if resp.status_code != 200:
            raise UnexpectedStatusCodeException(resp.status_code, resp.reason)

    def delete_webhook(self):
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{self._token}/deleteWebhook"
            )
        except ConnectionError:
            raise NetworkException("Failed to establish a new connection.")
        except Exception as exc:
            raise UnknownErrorException(f"{exc}") from exc

        if resp.status_code != 200:
            raise UnexpectedStatusCodeException(resp.status_code, resp.reason)

    def send_message(self, payload: SendMessagePayload) -> int:
        try:
            data = jsons.dump(payload, strip_nulls=True)
            r = requests.post(
                f"https://api.telegram.org/bot{self._token}/sendMessage", json=data
            )
            message_id = jsons.loads(r.text, cls=SendMessageResponse).result.message_id
        except ConnectionError:
            raise NetworkException("Failed to establish a new connection.")
        except Exception as exc:
            raise UnknownErrorException(f"{exc}") from exc

        if r.status_code != 200:
            raise UnexpectedStatusCodeException(r.status_code, r.reason)
        return message_id

    def edit_message_text(self, payload: MessageEdit) -> None:
        try:
            data = jsons.dump(payload, strip_nulls=True)
            r = requests.post(
                f"https://api.telegram.org/bot{self._token}/editMessageText", json=data
            )
        except ConnectionError:
            raise NetworkException("Failed to establish a new connection.")
        except Exception as exc:
            raise UnknownErrorException(f"{exc}") from exc

        if r.status_code != 200:
            raise UnexpectedStatusCodeException(r.status_code, r.reason)
