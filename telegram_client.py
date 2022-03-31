import requests
from typing import List
from abc import abstractclassmethod, ABC


from dataclasses import dataclass
import marshmallow_dataclass as mdc
from typing import List
import marshmallow


@dataclass
class Chat:
    """A class used to represent Chat ID
    
    Attribute
    ---------
    id : int
        chat id
    """

    id: int


@dataclass
class Message:
    """A class used to show message

    Attributes
    ----------
    chat : Chat 
        A variable used to represent Chat ID
    text : str
        A formatted string which contains a text message
    """

    chat: Chat
    text: str


@dataclass
class Update:
    """A class used to represent lasd updates from the Chat between Bot and Client

    Attributes
    ----------
    update_id : int
        A variable shown the number of message from the chat 
    message : Message
        A variable contains text of the message and which clients sent it
    """

    update_id: int
    message: Message


@dataclass
class GetUpdatesResponse:
    """A class gets updates from Bot

    Attribute
    ---------
    result : List 
        List of updates
    """

    result: List[Update]


@dataclass
class SendMessagePayload:
    """A class used to send message to client

    Attribute
    ---------
    chat_id : int
        the number of client's ID
    text : str 
        the text of message is sent to client 
    """

    chat_id: int
    text: str


class BaseSchema(marshmallow.Schema):
    class Meta:
        unknown = marshmallow.EXCLUDE


GetUpdatesResponseSchema = mdc.class_schema(GetUpdatesResponse, base_schema=BaseSchema)()
SendMessagePayloadSchema = mdc.class_schema(SendMessagePayload)()


class TelegramClient(ABC):
    """An interface for receiving and sending messages
    
    Methods
    ------
    get_updates(offset)
        The interface used to get list of updates from the chat between Client and Bot
    send_message(payload)
        The interface used to send messages to Client from Bot  
    send_text(chat_id, text)
        The interface used to form text for message    
    """

    @abstractclassmethod
    def get_updates(self, offset: int = 0) -> List[Update]: pass

    @abstractclassmethod
    def send_message(self, payload: SendMessagePayload) -> None: pass

    def send_text(self, chat_id: int, text: str) -> None:
        self.send_message(SendMessagePayload(chat_id, text))


class LiveTelegramClient(TelegramClient):
    """A class for receiving and sending messages

    Attribute
    ---------
    token : str
        a variable to get access to Telegram Bot  

    Methods
    ------
    get_updates(offset)
        The interface used to get list of updates from the chat between Client and Bot
    send_message(payload)
        The interface used to send messages to Client from Bot  
    send_text(chat_id, text)
        The interface used to form text for message 
    """

    def __init__(self, token: str) -> None:
        self._token = token

    def get_updates(self, offset: int = 0) -> List[Update]:


        data = requests.get(f'https://api.telegram.org/bot{self._token}/getUpdates?offset={offset}').text
        response: GetUpdatesResponse = GetUpdatesResponseSchema.loads(data)
        print(response.result)
        return response.result

    def send_message(self, payload: SendMessagePayload) -> None:
        """A method used to form and send message to the client

        Assert
        ------
        If API response is incorrect, to write the current status of the programme 
        """

        data = SendMessagePayloadSchema.dump(payload)
        print(data)
        r = requests.post(f'https://api.telegram.org/bot{self._token}/sendMessage', data=data)
        assert r.status_code == 200, f'Expected status code 200 but got {r.status_code}'
