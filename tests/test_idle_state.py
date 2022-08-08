from tutils import (
    bot_msg,
    check_conversation,
    make_handler_greet,
    make_handler_idle,
    user,
)


def test_process_starting_game():
    check_conversation(
        make_handler_idle(),
        [
            user("/startGame"),
            bot_msg("Starting game!"),
        ],
    )


def test_process_other_message():
    check_conversation(
        make_handler_idle(),
        [
            user("other message"),
            bot_msg("Type /startGame to start a new game."),
        ],
    )


def test_greeting_state():
    check_conversation(
        make_handler_greet(),
        [
            user("hi"),
            bot_msg(
                "Hello. I am Trivia Bot. If you want to play the game,\n"
                "please type /startGame"
            ),
        ],
    )
