from typing import List

from tutils import (
    FakeTelegramClient,
    MessageContent,
    bot_edit,
    bot_msg,
    check_conversation,
    user,
)

from chat_handler import ChatHandler
from format import make_answered_question_message, make_keyboard
from question_storage import Question

QUESTIONS = [
    Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
    Question("2.How much is 2 + 5?", ["4", "10", "7", "8"], 2),
    Question("3.What date is Christmas?", ["Dec 24", "Apr 15", "Jan 1", "Dec 25"], 3),
]


def check_chat(conversation: List[MessageContent]):
    client = FakeTelegramClient()
    chat_id = 123
    chat_handler = ChatHandler.make_default(client, chat_id)
    check_conversation(chat_id, conversation, client, chat_handler.process)


def test_entire_game():
    check_chat(
        [
            user("/startGame"),
            bot_edit("Starting game!"),
            bot_msg("1.What is the color of sky?", make_keyboard(QUESTIONS[0])),
            user("1"),
            bot_msg(make_answered_question_message(0, QUESTIONS[0])),
            bot_msg("2.How much is 2 + 5?", make_keyboard(QUESTIONS[1])),
            user("3"),
            bot_edit(make_answered_question_message(2, QUESTIONS[1])),
            bot_msg("3.What date is Christmas?", make_keyboard(QUESTIONS[2])),
            user("4"),
            bot_edit(make_answered_question_message(3, QUESTIONS[2])),
            bot_msg(
                "You got 2 points out of 3.\n"
                "If you want to try again, type /startGame to start a new game."
            ),
            user("/startGame"),
            bot_msg("Starting game!"),
        ]
    )
