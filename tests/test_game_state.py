from tutils import (
    QUESTIONS,
    FakeTelegramClient,
    bot_edit,
    bot_msg,
    check_conversation,
    make_handler_game,
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
from question_storage import InMemoryStorage
from telegram_client import CallbackQuery, MessageEdit, SendMessagePayload, Update, User


def test_game_state():
    check_conversation(
        make_handler_game(),
        [
            bot_msg("1.What is the color of sky?", make_keyboard(QUESTIONS[0])),
            user("2"),
            bot_edit(make_answered_question_message(1, QUESTIONS[0])),
            bot_msg("2.How much is 2 + 5?", make_keyboard(QUESTIONS[1])),
            user("4"),
            bot_edit(make_answered_question_message(3, QUESTIONS[1])),
            bot_msg("3.What date is Christmas?", make_keyboard(QUESTIONS[2])),
            user("4"),
            bot_edit(make_answered_question_message(3, QUESTIONS[2])),
            bot_msg(
                "You got 2 points out of 3.\n"
                "If you want to try again, type /startGame to start a new game."
            ),
        ],
    )


def test_gibberish_reply():
    check_conversation(
        make_handler_game(),
        [
            bot_msg("1.What is the color of sky?", make_keyboard(QUESTIONS[0])),
            user("first"),
            bot_msg("Please, type the number of your supposed answer"),
            user("second"),
            bot_msg("Please, type the number of your supposed answer"),
            user("3"),
            bot_edit(make_answered_question_message(2, QUESTIONS[0])),
            bot_msg("2.How much is 2 + 5?", make_keyboard(QUESTIONS[1])),
        ],
    )


def test_enter_inappropriate_number():
    check_conversation(
        make_handler_game(),
        [
            bot_msg("1.What is the color of sky?", make_keyboard(QUESTIONS[0])),
            user("-1"),
            bot_msg("Type the number from 1 to 3"),
            user("4"),
            bot_msg("Type the number from 1 to 3"),
            user("1"),
            bot_edit(make_answered_question_message(0, QUESTIONS[0])),
            bot_msg("2.How much is 2 + 5?", make_keyboard(QUESTIONS[1])),
        ],
    )


def check_callback_query(button: str):
    client = FakeTelegramClient()

    state = BotStateFactory(client, InMemoryStorage(QUESTIONS)).make_game_state()
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
