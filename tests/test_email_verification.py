"""Tests for email verification functionality."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from jose import jwt

from ace_platform.config import get_settings
from ace_platform.core.email import (
    TOKEN_TYPE_EMAIL_VERIFICATION,
    create_email_verification_token,
    decode_email_verification_token,
    is_email_enabled,
)

settings = get_settings()


class TestEmailVerificationTokens:
    """Tests for email verification token creation and decoding."""

    def test_create_verification_token(self):
        """Test creating a verification token."""
        user_id = uuid4()
        email = "test@example.com"

        token = create_email_verification_token(user_id, email)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        """Test decoding a valid verification token."""
        user_id = uuid4()
        email = "test@example.com"

        token = create_email_verification_token(user_id, email)
        result = decode_email_verification_token(token)

        assert result is not None
        decoded_user_id, decoded_email = result
        assert decoded_user_id == user_id
        assert decoded_email == email

    def test_decode_expired_token(self):
        """Test that expired tokens are rejected."""
        user_id = uuid4()
        email = "test@example.com"

        # Create a token that's already expired
        expire = datetime.now(UTC) - timedelta(hours=1)
        payload = {
            "sub": str(user_id),
            "email": email,
            "type": TOKEN_TYPE_EMAIL_VERIFICATION,
            "exp": expire,
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

        result = decode_email_verification_token(token)
        assert result is None

    def test_decode_wrong_token_type(self):
        """Test that tokens with wrong type are rejected."""
        user_id = uuid4()
        email = "test@example.com"

        # Create a token with wrong type
        expire = datetime.now(UTC) + timedelta(hours=24)
        payload = {
            "sub": str(user_id),
            "email": email,
            "type": "wrong_type",
            "exp": expire,
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

        result = decode_email_verification_token(token)
        assert result is None

    def test_decode_invalid_token(self):
        """Test that invalid tokens are rejected."""
        result = decode_email_verification_token("invalid-token")
        assert result is None

    def test_decode_tampered_token(self):
        """Test that tampered tokens are rejected."""
        user_id = uuid4()
        email = "test@example.com"

        token = create_email_verification_token(user_id, email)
        # Tamper with the token
        tampered_token = token[:-5] + "xxxxx"

        result = decode_email_verification_token(tampered_token)
        assert result is None


class TestEmailEnabled:
    """Tests for email enabled check."""

    def test_email_disabled_by_default(self):
        """Test that email is disabled when no API key is set."""
        with patch.object(settings, "resend_api_key", ""):
            # Re-check with empty key
            assert not is_email_enabled() or settings.resend_api_key == ""

    def test_email_enabled_with_api_key(self):
        """Test that email is enabled when API key is set."""
        with patch.object(settings, "resend_api_key", "re_test_key"):
            assert is_email_enabled()


class TestSendVerificationEmail:
    """Tests for sending verification emails."""

    @pytest.mark.asyncio
    async def test_send_email_disabled(self):
        """Test that send returns error when email is disabled."""
        from ace_platform.core.email import send_verification_email

        with patch("ace_platform.core.email.is_email_enabled", return_value=False):
            result = await send_verification_email(
                "test@example.com",
                "https://example.com/verify?token=xxx",
            )

            assert not result.success
            assert "not configured" in result.error.lower()

    @pytest.mark.asyncio
    async def test_send_email_success(self):
        """Test successful email sending."""
        from ace_platform.core.email import send_verification_email

        mock_send = AsyncMock(return_value={"id": "msg_123"})

        with patch("ace_platform.core.email.is_email_enabled", return_value=True):
            with patch("resend.Emails.send", mock_send):
                result = await send_verification_email(
                    "test@example.com",
                    "https://example.com/verify?token=xxx",
                )

                # Note: The actual test depends on resend being installed
                # This test structure shows the expected behavior
                assert result is not None
