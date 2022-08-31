import json
from json import JSONDecodeError

from bot_state import BotStateFactory, GameState, GreetingState, IdleState, ProtoGameState
from chat_handler import ChatHandler, ProtoChatHandler
from question_storage import Question
from telegram_client import TelegramClient


class ChatHandlerEncoder(json.JSONEncoder):
    """JSON encoder for ChatHandler class.
    Return JSON dict from ChatHandler object."""

    def default(self, o):
        if isinstance(o, ChatHandler):
            return {
                "__chat_handler__": True,
                "chat_handler": json.dumps(o.chat_handler_params, cls=ChatHandlerEncoder),
            }
        if isinstance(o, ProtoChatHandler):
            return {
                "chat_id": json.dumps(o.chat_id, cls=ChatHandlerEncoder),
                "__state__": json.dumps(o.state, cls=ChatHandlerEncoder),
            }

        if isinstance(o, GreetingState):
            return {
                "state_name": "GreetingState",
            }
        if isinstance(o, IdleState):
            return {
                "state_name": "IdleState",
            }
        if isinstance(o, GameState):
            return {
                "state_name": "GameState",
                "game_parameters": json.dumps(o.game_params, cls=ChatHandlerEncoder),
            }
        if isinstance(o, ProtoGameState):
            return {
                "questions": json.dumps(o.questions, cls=ChatHandlerEncoder),
                "current_question": o.current_question,
                "score": o.score,
                "last_question_message_id": o.last_question_msg_id,
            }
        if isinstance(o, Question):
            return {
                "text": o.text,
                "answers": o.answers,
                "correct_answer": o.correct_answer,
            }
        raise TypeError(
            f"{o} type object is not subscriptable."
        )


class ChatHandlerDecoder(json.JSONDecoder):
    """JSON decoder for ChatHandler class."""

    def __init__(self, client: TelegramClient, state_factory: BotStateFactory):
        super().__init__()
        self.client = client
        self.state_factory = state_factory

    def decode_chat_handler(self, obj) -> dict:
        """Return ChatHandler object from JSON dict."""
        try:
            if isinstance(obj, list):
                data = [self.decode_chat_handler(el) for el in obj]
            elif isinstance(obj, dict):
                data = obj
            else:
                data = json.loads(obj)

            if isinstance(data, dict):
                for k, v in data.items():
                    data[k] = self.decode_chat_handler(v)
        except (JSONDecodeError, TypeError, AttributeError):
            return obj
        return data

    def form_chat_handler(self, ch) -> ChatHandler:
        data = self.decode_chat_handler(ch)
        chat_id = data["chat_handler"]["chat_id"]
        state_name = data["chat_handler"]["__state__"]["state_name"]
        if state_name == "GreetingState":
            state = GreetingState(self.client, self.state_factory)
        elif state_name == "IdleState":
            state = IdleState(self.client, self.state_factory)
        elif state_name == "GameState":
            game_params = data["chat_handler"]["__state__"]["game_parameters"]

            questions = []
            for question in game_params["questions"]:
                text = question["text"]
                answers = question["answers"]
                correct_answer = question["correct_answer"]
                questions.append(Question(text, answers, correct_answer))

            cur_question = game_params["current_question"]
            score = game_params["score"]
            last_question_msg_id = game_params["last_question_message_id"]
            state = GameState(
                self.client, self.state_factory, ProtoGameState(questions, cur_question, score, last_question_msg_id)
            )
        else:
            raise TypeError("Unknown value of 'state_name' key")

        return ChatHandler.create(state, chat_id)
