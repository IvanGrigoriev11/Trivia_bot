from tutils import bot_edit, bot_msg, check_state, greeting, user

from format import make_answered_question_message, make_keyboard
from question_storage import Question

QUESTIONS = [
    Question("1.What is the color of sky?", ["orange", "blue", "green"], 1),
    Question("2.How much is 2 + 5?", ["4", "10", "7", "8"], 2),
    Question("3.What date is Christmas?", ["Dec 24", "Apr 15", "Jan 1", "Dec 25"], 3),
]


def test_entire_game():
    check_state(
        greeting(
            [
                user("Yo"),
                bot_msg(
                    "Hello. I am Trivia Bot. If you want to play the game,\n"
                    "please type /startGame"
                ),
                user("/startGame"),
                bot_msg("Starting game!"),
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
                user("/startGame"),
                bot_msg("Starting game!"),
            ]
        )
    )
