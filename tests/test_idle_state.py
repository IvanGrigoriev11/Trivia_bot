from tutils import bot_msg, check_state, greeting, idle, user


def test_process_starting_game():
    check_state(
        idle(
            [
                user("/startGame"),
                bot_msg("Starting game!"),
            ]
        )
    )


def test_process_other_message():
    check_state(
        idle(
            [
                user("other message"),
                bot_msg("Type /startGame to start a new game."),
            ]
        )
    )


def test_greeting_state():
    check_state(
        greeting(
            [
                user("hi"),
                bot_msg(
                    "Hello. I am Trivia Bot. If you want to play the game,\n"
                    "please type /startGame"
                ),
            ]
        )
    )
