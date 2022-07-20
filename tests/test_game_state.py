from typing import List

from tutils import (
    FakeTelegramClient,
    MessageContent,
    bot_edit,
    bot_msg,
    check_conversation,
    user,
)

from bot_state import BotStateFactory
from format import (
    CHECK_MARK,
    CROSS_MARK,
    RED_CIRCLE_MARK,
    make_answered_question_message,
    make_keyboard,
)
from question_storage import InMemoryStorage, Question
from telegram_client import CallbackQuery, MessageEdit, SendMessagePayload, Update, User

QUESTIONS = [
    Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
    Question("2.How much is 2 + 5?", ["4", "10", "7", "8"], 2),
    Question("3.What date is Christmas?", ["Dec 24", "Apr 15", "Jan 1", "Dec 25"], 3),
]


def check_game_state(conversation: List[MessageContent]):
    client = FakeTelegramClient()
    chat_id = 111
    state = BotStateFactory(client, InMemoryStorage()).make_game_state()
    state.on_enter(chat_id)

    def process(u: Update):
        state.process(u)

    check_conversation(chat_id, conversation, client, process)


def test_game_state():
    check_game_state(
        [
            bot_msg("1.What is the color of sky?", make_keyboard(QUESTIONS[0])),
            user("2"),
            bot_edit(make_answered_question_message(1, QUESTIONS[0])),
            bot_msg("2.How much is 2 + 5?", make_keyboard(QUESTIONS[1])),
            user("2"),
            bot_edit(make_answered_question_message(1, QUESTIONS[1])),
            bot_msg("3.What date is Christmas?", make_keyboard(QUESTIONS[2])),
            user("2"),
            bot_edit(make_answered_question_message(1, QUESTIONS[2])),
            bot_msg(
                "You got 1 points out of 3.\n"
                "If you want to try again, type /startGame to start a new game."
            ),
        ]
    )


def test_gibberish_reply():
    check_game_state(
        [
            bot_msg("1.What is the color of sky?", make_keyboard(QUESTIONS[0])),
            user("first"),
            bot_msg("Please, type the number of your supposed answer"),
            user("second"),
            bot_msg("Please, type the number of your supposed answer"),
            user("3"),
            bot_msg(make_answered_question_message(2, QUESTIONS[0])),
            bot_msg("2.How much is 2 + 5?", make_keyboard(QUESTIONS[1])),
        ]
    )


def test_enter_inappropriate_number():
    check_game_state(
        [
            bot_msg("1.What is the color of sky?", make_keyboard(QUESTIONS[0])),
            user("-1"),
            bot_msg("Type the number from 1 to 3"),
            user("4"),
            bot_msg("Type the number from 1 to 3"),
            user("1"),
            bot_edit(make_answered_question_message(0, QUESTIONS[0])),
            bot_msg("2.How much is 2 + 5?", make_keyboard(QUESTIONS[1])),
        ]
    )


def check_callback_query(button: str):
    client = FakeTelegramClient()

    state = BotStateFactory(client, InMemoryStorage()).make_game_state()
    chat_id = 111
    state.on_enter(chat_id)
    state.process(Update(123, None, CallbackQuery(User(111), f"{button}")))
    assert client.sent_messages == [
        SendMessagePayload(
            111, "1.What is the color of sky?", make_keyboard(QUESTIONS[0])
        ),
        MessageEdit(
            111,
            0,
            f"1.What is the color of sky?\n"
            f"{RED_CIRCLE_MARK}orange\n{CHECK_MARK}blue\n{CROSS_MARK}green",
        ),
        SendMessagePayload(111, "2.How much is 2 + 5?", make_keyboard(QUESTIONS[1])),
    ]


def test_callback_query():
    check_callback_query("2")
