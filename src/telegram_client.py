import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Coroutine, List, Optional, Type, TypeVar

import aiohttp
import jsons
import requests

from utils import transform_keywords

T = TypeVar("T")


class TelegramException(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(status_code, message)


class UnexpectedStatusCodeException(TelegramException):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(message, status_code)


class NetworkException(TelegramException):
    def __init__(self, message: str):
        super().__init__(message)


class UnknownErrorException(TelegramException):
    def __init__(self, message: str):
        super().__init__(message)


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
class ChatMember:
    """Сurrent status of the specific chat."""

    status: str


@dataclass
class ChatMemberUpdated:
    """Current membership status."""

    chat: Chat
    new_chat_member: ChatMember


@dataclass
class Update:
    """A class used to represent Telegram updates that a bot can receive.
    The class contains two optional fields which represent special type of Telegram messages.
    """

    update_id: int
    message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None
    my_chat_member: Optional[ChatMemberUpdated] = None
    channel_post: Optional[Message] = None

    @property
    def chat_id(self) -> int:
        assert (
            len(
                [
                    x
                    for x in (self.message, self.callback_query, self.my_chat_member)
                    if x is not None
                ]
            )
            == 1
        )

        if self.message is not None:
            return self.message.chat.id
        if self.callback_query is not None:
            return self.callback_query.from_.id
        if self.my_chat_member is not None:
            return self.my_chat_member.chat.id

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
    async def get_updates(self, offset: int = 0) -> List[Update]:
        """Gets updates from the telegram with `update_id` bigger than `offset`."""

    @abstractmethod
    async def send_message(self, payload: SendMessagePayload) -> int:
        """Sends message with a given `payload` to Telegram and returns the id of this message."""

    @abstractmethod
    async def edit_message_text(self, payload: MessageEdit) -> None:
        """Edits the text of the selected message."""

    async def send_text(
        self,
        chat_id: int,
        text: str,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> int:

        return await self.send_message(SendMessagePayload(chat_id, text, reply_markup))


def filter_updates(
    func: Callable[..., Coroutine[Any, Any, List[Update]]]
) -> Callable[..., Coroutine[Any, Any, List[Update]]]:
    """Filters out updates with valid fields from those with the field 'channel_post'
    if such are skipped by telegram.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs) -> List[Update]:
        result = await func(*args, **kwargs)
        filtered_updates = []
        for update in result:
            if update.channel_post is not None:
                logging.warning(
                    "The message is not processable due to invalid format: %s",
                    update.channel_post,
                )
            else:
                filtered_updates.append(update)
        return filtered_updates

    return wrapper


class LiveTelegramClient(TelegramClient):
    """An implementation of the `TelegramClient` for communicating with an actual backend."""

    def __init__(self, token: str) -> None:
        """
        token -- Telegram bot token.
        """
        self._token = token

    @staticmethod
    def _request(
        method: str,
        url: str,
        cls: Optional[Type[T]] = None,
        files: Optional[dict] = None,
        json: Optional[Any] = None,
    ) -> Optional[T]:
        try:
            response = requests.request(method, url, files=files, json=json)
            if cls is not None:
                return jsons.load(
                    response.json(), cls=cls, key_transformer=transform_keywords
                )
        except ConnectionError as exc:
            raise NetworkException("Failed to establish a new connection.") from exc
        except Exception as exc:
            raise UnknownErrorException("Telegram request failed") from exc

        if response.status_code != 200:
            raise UnexpectedStatusCodeException(response.status_code, response.reason)
        return None

    def set_webhook(self, url: str, cert_path: Optional[str] = None) -> None:
        fields = "allowed_updates=['message','callback_query','my_chat_member']"
        if cert_path is None:
            self._request(
                "post",
                f"https://api.telegram.org/bot{self._token}/setWebhook?url={url}&{fields}",
            )
        else:
            cert = Path(cert_path)
            with open(cert, encoding="utf-8") as cert:
                files = {"certificate": cert}
                self._request(
                    "post",
                    f"https://api.telegram.org/bot{self._token}/setWebhook?url={url}&{fields}",
                    files=files,
                )

    def delete_webhook(self):
        self._request(
            "post", f"https://api.telegram.org/bot{self._token}/deleteWebhook"
        )

    @staticmethod
    async def _async_request(
        method: str,
        url: str,
        cls: Optional[Type[T]] = None,
        json: Optional[Any] = None,
    ) -> Optional[T]:
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.request(method, url, json=json)
                if cls is not None:
                    return jsons.load(
                        await response.json(),
                        cls=cls,
                        key_transformer=transform_keywords,
                    )
        except ConnectionError as exc:
            raise NetworkException("Failed to establish a new connection.") from exc
        except Exception as exc:
            raise UnknownErrorException("Telegram request failed") from exc

        if response.status != 200:
            raise UnexpectedStatusCodeException(response.status, response.reason)
        return None

    @filter_updates
    async def get_updates(self, offset: int = 0) -> List[Update]:
        fields = "allowed_updates=['message','callback_query','my_chat_member']"
        response = await self._async_request(
            "get",
            f"https://api.telegram.org/bot{self._token}/getUpdates?offset={offset}&{fields}",
            cls=GetUpdatesResponse,
        )
        if response is None:
            raise UnknownErrorException("Failed to get updates")
        return response.result

    async def send_message(self, payload: SendMessagePayload) -> int:
        data = jsons.dump(payload, strip_nulls=True)
        response = await self._async_request(
            "post",
            f"https://api.telegram.org/bot{self._token}/sendMessage",
            cls=SendMessageResponse,
            json=data,
        )
        if response is None:
            raise UnknownErrorException("Failed to get a response")
        return response.result.message_id

    async def edit_message_text(self, payload: MessageEdit) -> None:
        data = jsons.dump(payload, strip_nulls=True)
        await self._async_request(
            "post",
            f"https://api.telegram.org/bot{self._token}/editMessageText",
            json=data,
        )
