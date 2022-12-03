import pytest
from test_greeting_state import make_conv_conf
from tutils import QUESTIONS, bot_edit, bot_msg, check_conversation, user

import format as fmt


@pytest.mark.asyncio
async def test_entire_game():
    await check_conversation(
        await make_conv_conf(),
        [
            user("Yo"),
            bot_msg(
                "Hello. I am Trivia Bot. If you want to play the game,\n"
                "please type /startGame"
            ),
            user("/startGame"),
            bot_msg("Starting game!"),
            bot_msg(fmt.make_question(QUESTIONS[0]), fmt.make_keyboard(QUESTIONS[0])),
            user("b"),
            bot_edit(fmt.make_answered_question(1, QUESTIONS[0])),
            bot_msg(fmt.make_question(QUESTIONS[1]), fmt.make_keyboard(QUESTIONS[1])),
            user("b"),
            bot_edit(fmt.make_answered_question(1, QUESTIONS[1])),
            bot_msg(fmt.make_question(QUESTIONS[2]), fmt.make_keyboard(QUESTIONS[2])),
            user("b"),
            bot_edit(fmt.make_answered_question(1, QUESTIONS[2])),
            bot_msg(
                "You got 1 points out of 3.\n"
                "If you want to try again, type /startGame to start a new game."
            ),
            user("/startGame"),
            bot_msg("Starting game!"),
        ],
    )
