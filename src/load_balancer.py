from typing import Protocol

import aioredis


class LockService(Protocol):
    """Load balancer interface based on Redis."""

    async def acquire_lock(self, chat_id: int) -> None:
        """Set the lock on operations with a specific chat.
        If the key 'chat_id' exists in the DB, the lock is acquired on the chat.
        If the key doesn't exist in the DB, the lock doesn't exist on this chat as well.
        """

    async def release_lock(self, chat_id: int) -> None:
        """Delete lock on operations with a particular chat."""

    async def check_existing_lock(self, chat_id: int) -> bool:
        """Check if the lock is still existing."""


# TO DO: think more about the names of child classes


class Op(LockService):
    """Implementation for operating with multiple machine setup."""

    def __init__(self):
        # TO DO: do not forget to write to right address

        self._pool = aioredis.ConnectionPool.from_url(
            "redis://localhost/", max_connections=10
        )

    async def acquire_lock(self, chat_id: int) -> None:

        async with aioredis.Redis(connection_pool=self._pool) as conn:
            # TO DO: discuss which expiration time is more preferable for holding the key and add it
            await conn.execute_command("SET", chat_id, 1, "NX")

    async def release_lock(self, chat_id: int) -> None:

        async with aioredis.Redis(connection_pool=self._pool) as conn:
            await conn.execute_command("del", chat_id)

    async def check_existing_lock(self, chat_id: int) -> bool:

        async with aioredis.Redis(connection_pool=self._pool) as conn:
            if await conn.execute_command("get", chat_id):
                return True
            return False


class NoOp(LockService):
    """Implementation for operating with only one machine in setup."""

    def __init__(self):
        self._pool = aioredis.ConnectionPool.from_url(
            "redis://localhost/", max_connections=10
        )

    async def acquire_lock(self, chat_id: int) -> None:

        async with aioredis.Redis(connection_pool=self._pool) as conn:
            # TO DO: discuss which expiration time is more preferable for holding the key and add it
            await conn.execute_command("SET", chat_id, 1, "NX")

    async def release_lock(self, chat_id: int) -> None:
        pass

    async def check_existing_lock(self, chat_id: int) -> bool:

        async with aioredis.Redis(connection_pool=self._pool) as conn:
            if await conn.execute_command("get", chat_id):
                return True
            return False
