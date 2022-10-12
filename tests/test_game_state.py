from typing import Optional

from tutils import (
    QUESTIONS,
    ConvConfig,
    FakeTelegramClient,
    bot_edit,
    bot_msg,
    check_conversation,
    user,
)

import format as fmt
from bot_state import BotStateFactory, GameState, ProtoGameState
from chat_handler import ChatHandler
from storage import InMemoryStorage
from telegram_client import CallbackQuery, MessageEdit, SendMessagePayload, Update, User


def make_conv_conf(game_params: Optional[ProtoGameState] = None):
    client = FakeTelegramClient()
    storage = InMemoryStorage(QUESTIONS)
    state_factory = BotStateFactory(client, storage)
    chat_id = 111

    if game_params is None:
        handler = ChatHandler.create(state_factory.make_game_state(), chat_id)
    else:
        handler = ChatHandler(
            GameState(client, state_factory, game_params, True), chat_id
        )
    return ConvConfig(handler, client, chat_id)


def test_game_till_end():
    check_conversation(
        make_conv_conf(),
        [
            bot_msg(fmt.make_question(QUESTIONS[0]), fmt.make_keyboard(QUESTIONS[0])),
            user("b"),
            bot_edit(fmt.make_answered_question(1, QUESTIONS[0])),
            bot_msg(fmt.make_question(QUESTIONS[1]), fmt.make_keyboard(QUESTIONS[1])),
            user("D"),
            bot_edit(fmt.make_answered_question(3, QUESTIONS[1])),
            bot_msg(fmt.make_question(QUESTIONS[2]), fmt.make_keyboard(QUESTIONS[2])),
            user("d"),
            bot_edit(fmt.make_answered_question(3, QUESTIONS[2])),
            bot_msg(
                "You got 2 points out of 3.\n"
                "If you want to try again, type /startGame to start a new game."
            ),
        ],
    )


def test_gibberish_reply():
    check_conversation(
        make_conv_conf(),
        [
            bot_msg(fmt.make_question(QUESTIONS[0]), fmt.make_keyboard(QUESTIONS[0])),
            user("first"),
            bot_msg(fmt.make_answers_help_message(QUESTIONS[0].answers)),
            user("second"),
            bot_msg(fmt.make_answers_help_message(QUESTIONS[0].answers)),
            user("c"),
            bot_edit(fmt.make_answered_question(2, QUESTIONS[0])),
            bot_msg(fmt.make_question(QUESTIONS[1]), fmt.make_keyboard(QUESTIONS[1])),
        ],
    )


def test_enter_inappropriate_number():
    check_conversation(
        make_conv_conf(),
        [
            bot_msg(fmt.make_question(QUESTIONS[0]), fmt.make_keyboard(QUESTIONS[0])),
            user("-1"),
            bot_msg(fmt.make_answers_help_message(QUESTIONS[0].answers)),
            user("4"),
            bot_msg(fmt.make_answers_help_message(QUESTIONS[0].answers)),
            user("a"),
            bot_edit(fmt.make_answered_question(0, QUESTIONS[0])),
            bot_msg(fmt.make_question(QUESTIONS[1]), fmt.make_keyboard(QUESTIONS[1])),
        ],
    )


def test_typing_unsuitable_letter_as_answer():
    check_conversation(
        make_conv_conf(),
        [
            bot_msg(fmt.make_question(QUESTIONS[0]), fmt.make_keyboard(QUESTIONS[0])),
            user("D"),
            bot_msg(fmt.make_answers_help_message(QUESTIONS[0].answers)),
            user("fff"),
            bot_msg(fmt.make_answers_help_message(QUESTIONS[0].answers)),
            user("a"),
            bot_edit(fmt.make_answered_question(0, QUESTIONS[0])),
            bot_msg(fmt.make_question(QUESTIONS[1]), fmt.make_keyboard(QUESTIONS[1])),
        ],
    )


def check_callback_query(button: str):
    client = FakeTelegramClient()

    state = BotStateFactory(client, InMemoryStorage(QUESTIONS)).make_game_state()
    chat_id = 111
    state.on_enter(chat_id)
    state.process(Update(123, None, CallbackQuery(User(111), f"{button}")))
    expected = [
        SendMessagePayload(
            111, fmt.make_question(QUESTIONS[0]), fmt.make_keyboard(QUESTIONS[0])
        ),
        MessageEdit(
            111,
            0,
            f"1.What is the color of sky?\n"
            f"{fmt.RED_CIRCLE_MARK}orange\n{fmt.CHECK_MARK}blue\n{fmt.CROSS_MARK}green",
        ),
        SendMessagePayload(
            111, fmt.make_question(QUESTIONS[1]), fmt.make_keyboard(QUESTIONS[1])
        ),
    ]
    assert client.sent_messages == expected


def test_callback_query():
    check_callback_query("c")


def test_game_score_for_deserialized_state():
    cur_score = 1
    prev_message_id = 0
    check_conversation(
        make_conv_conf(ProtoGameState(QUESTIONS, 2, cur_score, prev_message_id)),
        [
            user("d"),  # correct answer for question 2 (0-based)
            bot_edit(fmt.make_answered_question(3, QUESTIONS[2])),
            bot_msg(
                "You got 2 points out of 3.\n"
                "If you want to try again, type /startGame to start a new game."
            ),
        ],
    )
