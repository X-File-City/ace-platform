"""Unit tests for transient API-key auth database failures."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import DBAPIError

from ace_platform.core.api_keys import API_KEY_PREFIX, authenticate_api_key_async, hash_api_key
from ace_platform.db.models import ApiKey, User


class _ScalarResult:
    def __init__(self, item):
        self._item = item

    def scalar_one_or_none(self):
        return self._item


def _build_user() -> User:
    return User(
        id=uuid4(),
        email="test@example.com",
        hashed_password="hashed",
        is_active=True,
    )


def _build_api_key(user_id) -> tuple[str, ApiKey]:
    full_key = f"{API_KEY_PREFIX}1234567890abcdefghijklmnopqrstuv"
    return full_key, ApiKey(
        id=uuid4(),
        user_id=user_id,
        name="Test Key",
        key_prefix=full_key[:8],
        hashed_key=hash_api_key(full_key),
        scopes=["outcomes:write"],
        last_used_at=None,
        revoked_at=None,
    )


class TestAuthenticateApiKeyResilience:
    async def test_recovers_from_disconnect_during_last_used_flush(self):
        """A dropped connection on last_used_at update should not fail auth."""
        user = _build_user()
        full_key, initial_key = _build_api_key(user.id)
        _, refreshed_key = _build_api_key(user.id)

        db = MagicMock()
        db.execute = AsyncMock(
            side_effect=[_ScalarResult(initial_key), _ScalarResult(refreshed_key)]
        )
        db.flush = AsyncMock(
            side_effect=DBAPIError(
                statement="UPDATE api_keys SET last_used_at = :last_used_at",
                params={},
                orig=Exception("connection was closed in the middle of operation"),
                connection_invalidated=True,
            )
        )
        db.rollback = AsyncMock()
        db.get = AsyncMock(return_value=user)

        key_record, authenticated_user = await authenticate_api_key_async(db, full_key)

        assert key_record is refreshed_key
        assert authenticated_user is user
        assert db.execute.await_count == 2
        db.rollback.assert_awaited_once()
        db.get.assert_awaited_once_with(User, refreshed_key.user_id)

    async def test_reraises_non_disconnect_db_errors(self):
        """Unexpected DB failures during flush should still propagate."""
        user = _build_user()
        full_key, key = _build_api_key(user.id)

        db = MagicMock()
        db.execute = AsyncMock(return_value=_ScalarResult(key))
        db.flush = AsyncMock(
            side_effect=DBAPIError(
                statement="UPDATE api_keys SET last_used_at = :last_used_at",
                params={},
                orig=Exception("duplicate key value violates unique constraint"),
            )
        )
        db.rollback = AsyncMock()
        db.get = AsyncMock(return_value=user)

        with pytest.raises(DBAPIError, match="duplicate key value"):
            await authenticate_api_key_async(db, full_key)

        db.rollback.assert_not_awaited()
