from audioop import avg
from cgitb import text
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


#@dataclass
#class SendQuestion:
 # number_of_question: int
 # text = '1'
 # Question_2: dict
 # Question_3: dict  


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
        data = requests.get(f'https://api.telegram.org/bot{self._token}/getUpdates?offset={offset}').text
        response: GetUpdatesResponse = GetUpdatesResponseSchema.loads(data)
        print(response.result)
        return response.result

    def send_message(self, payload: SendMessagePayload) -> None:
        
        data = SendMessagePayloadSchema.dump(payload)
        print(data)
        r = requests.post(f'https://api.telegram.org/bot{self._token}/sendMessage', data=data)
        assert r.status_code == 200, f'Expected status code 200 but got {r.status_code}'


def main():
    token = os.environ['TELEGRAM_BOT_TOKEN']
    client = TelegramClient(token)
    correct_answer = 0
    #offset = 0
    updates = client.get_updates()
    
 #while True:
    for update in updates:
      #offset = update.update_id + 1  
      try: 
        #offset = update.update_id + 1
        if update.message.text == '/start':
            number_of_question = 1
            client.send_message(SendMessagePayload(
            update.message.chat.id, 
            'Question 1. London is the capital of ... a) the UK b) the USA c) Germany'
            ))
        elif update.message.text == 'a' or 'b' or 'c':
            if number_of_question == 1:
                if update.message.text == 'a':
                    client.send_message(SendMessagePayload(
                    update.message.chat.id, 
                    'U R right. Question 2. What is the fastest land animal? a) gorilla b) tiger c) cheetah'
                    ))
                    correct_answer = correct_answer + 1
                    number_of_question = 2
                else:
                    client.send_message(SendMessagePayload(
                    update.message.chat.id, 
                    'This is wrong. Question 2. What is the fastest land animal? a) gorilla b) tiger c) cheetah'
                    ))
                    number_of_question = 2   
            elif number_of_question == 2:
                if update.message.text == 'c': 
                    client.send_message(SendMessagePayload(
                    update.message.chat.id, 
                    'U R right. Question 3. How many letters are in the chinese alphabet? a) 20  b) 26 c) 32'
                    ))	
                    correct_answer = correct_answer + 1
                    number_of_question = 3
                else:
                    client.send_message(SendMessagePayload(
                    update.message.chat.id, 
                    'This is wrong. Question 3. How many letters are in the chinese alphabet? a) 20  b) 26 c) 32'
                    ))	
                    number_of_question = 3 
            elif number_of_question == 3: 
                if update.message.text == 'b':
                    correct_answer = str(correct_answer + 1)
                    print(type(correct_answer))
                    client.send_message(SendMessagePayload(
                    update.message.chat.id, 
                    'U R right.Test has been completed. Your score is  ' + correct_answer + '  Please, send /start to play again'
                    ))
                else: 
                    client.send_message(SendMessagePayload(
                    update.message.chat.id, 
                    'This is wrong. Test has been completed. Your score is  ' + correct_answer + '  Please, send /start to play again'
                    ))
        else:
            client.send_message(SendMessagePayload(update.message.chat.id, 'Please, send /start for the beginning of the quiz'))
        
        
      except:
        client.send_message(SendMessagePayload(update.message.chat.id, 'Error'))
        #offset = update.update_id + 1
     

if __name__ == '__main__':
    main()