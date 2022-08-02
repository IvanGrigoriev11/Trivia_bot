from tutils import FakeTelegramClient

from bot_state import BotStateFactory, GameState, GreetingState, IdleState
from question_storage import InMemoryStorage


def check_creating(desired_state: str):
    storage = InMemoryStorage()
    client = FakeTelegramClient()
    state_factory = BotStateFactory(client, storage)

    if desired_state == "GreetingState":
        state = state_factory.make_greeting_state()
        assert isinstance(state, GreetingState)
    elif desired_state == "IdleState":
        state = state_factory.make_idle_state()
        assert isinstance(state, IdleState)
    else:
        state = state_factory.make_game_state()
        assert isinstance(state, GameState)


def test_create_greeting_state():
    check_creating("GreetingState")


def test_create_idle_state():
    check_creating("IdleState")


def test_create_game_state():
    check_creating("GameState")
