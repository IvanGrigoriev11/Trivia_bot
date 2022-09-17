from test_greeting_state import make_conv_conf
from tutils import QUESTIONS, bot_edit, bot_msg, check_conversation, user

from format import make_answered_question_message, make_keyboard, make_text_question


def test_entire_game():
    check_conversation(
        make_conv_conf(),
        [
            user("Yo"),
            bot_msg(
                "Hello. I am Trivia Bot. If you want to play the game,\n"
                "please type /startGame"
            ),
            user("/startGame"),
            bot_msg("Starting game!"),
            bot_msg(make_text_question(QUESTIONS[0]), make_keyboard(QUESTIONS[0])),
            user("2"),
            bot_edit(make_answered_question_message(1, QUESTIONS[0])),
            bot_msg(make_text_question(QUESTIONS[1]), make_keyboard(QUESTIONS[1])),
            user("2"),
            bot_edit(make_answered_question_message(1, QUESTIONS[1])),
            bot_msg(make_text_question(QUESTIONS[2]), make_keyboard(QUESTIONS[2])),
            user("2"),
            bot_edit(make_answered_question_message(1, QUESTIONS[2])),
            bot_msg(
                "You got 1 points out of 3.\n"
                "If you want to try again, type /startGame to start a new game."
            ),
            user("/startGame"),
            bot_msg("Starting game!"),
        ],
    )
