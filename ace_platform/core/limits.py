"""Usage limits based on subscription tier.

This module defines subscription tiers and their usage limits,
and provides functions to check if users are within their limits.

Tiers (for billing):
- starter: Entry-level paid tier ($9/month)
- pro: Professional tier ($29/month)
- ultra: High-volume tier ($79/month)
- enterprise: Custom/unlimited usage (post-launch)

Note: FREE tier kept for internal use (testing, grace periods) but not
exposed as a subscription option.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ace_platform.core.metering import get_user_usage_summary


class SubscriptionTier(str, Enum):
    """Subscription tier levels.

    FREE is kept for internal use but not exposed as a billing option.
    """

    FREE = "free"  # Internal use only
    STARTER = "starter"
    PRO = "pro"
    ULTRA = "ultra"
    ENTERPRISE = "enterprise"


@dataclass(frozen=True)
class TierLimits:
    """Usage limits for a subscription tier.

    Primary limit is monthly_evolution_runs which controls how many
    playbook evolutions a user can trigger per month.
    """

    # Monthly limits
    monthly_evolution_runs: int | None  # None = unlimited

    # Per-account limits
    max_playbooks: int | None

    # Feature flags
    can_use_premium_models: bool
    can_export_data: bool
    priority_support: bool


# Define limits for each tier based on BILLING_DECISIONS.md
TIER_LIMITS: dict[SubscriptionTier, TierLimits] = {
    SubscriptionTier.FREE: TierLimits(
        monthly_evolution_runs=10,  # Very limited for internal/testing use
        max_playbooks=1,
        can_use_premium_models=False,
        can_export_data=False,
        priority_support=False,
    ),
    SubscriptionTier.STARTER: TierLimits(
        monthly_evolution_runs=100,
        max_playbooks=5,
        can_use_premium_models=True,
        can_export_data=True,
        priority_support=False,
    ),
    SubscriptionTier.PRO: TierLimits(
        monthly_evolution_runs=500,
        max_playbooks=20,
        can_use_premium_models=True,
        can_export_data=True,
        priority_support=True,
    ),
    SubscriptionTier.ULTRA: TierLimits(
        monthly_evolution_runs=2_000,
        max_playbooks=100,
        can_use_premium_models=True,
        can_export_data=True,
        priority_support=True,
    ),
    SubscriptionTier.ENTERPRISE: TierLimits(
        monthly_evolution_runs=None,  # Unlimited
        max_playbooks=None,
        can_use_premium_models=True,
        can_export_data=True,
        priority_support=True,
    ),
}


@dataclass
class UsageStatus:
    """Current usage status for a user."""

    tier: SubscriptionTier
    limits: TierLimits

    # Current usage (this billing period)
    current_evolution_runs: int

    # Remaining quota (None if unlimited)
    remaining_evolution_runs: int | None

    # Status flags
    is_within_limits: bool
    limit_exceeded: str | None  # Which limit was exceeded, if any


def get_tier_limits(tier: SubscriptionTier) -> TierLimits:
    """Get limits for a subscription tier.

    Args:
        tier: The subscription tier.

    Returns:
        TierLimits for the tier.
    """
    return TIER_LIMITS[tier]


def get_billing_period_start() -> datetime:
    """Get the start of the current billing period.

    Returns the first day of the current month at midnight UTC.

    Returns:
        Start datetime of billing period.
    """
    now = datetime.now(UTC)
    return datetime(now.year, now.month, 1, tzinfo=UTC)


async def get_user_usage_status(
    db: AsyncSession,
    user_id: UUID,
    tier: SubscriptionTier = SubscriptionTier.FREE,
) -> UsageStatus:
    """Get current usage status for a user.

    Args:
        db: Database session.
        user_id: User ID to check.
        tier: User's subscription tier.

    Returns:
        UsageStatus with current usage and remaining quota.
    """
    limits = get_tier_limits(tier)
    period_start = get_billing_period_start()
    now = datetime.now(UTC)

    # Get current usage - total_requests represents evolution runs
    summary = await get_user_usage_summary(db, user_id, period_start, now)

    # Calculate remaining quota
    remaining_evolution_runs = None

    if limits.monthly_evolution_runs is not None:
        remaining_evolution_runs = max(0, limits.monthly_evolution_runs - summary.total_requests)

    # Check if within limits
    limit_exceeded = None
    is_within_limits = True

    if (
        limits.monthly_evolution_runs is not None
        and summary.total_requests >= limits.monthly_evolution_runs
    ):
        is_within_limits = False
        limit_exceeded = "monthly_evolution_runs"

    return UsageStatus(
        tier=tier,
        limits=limits,
        current_evolution_runs=summary.total_requests,
        remaining_evolution_runs=remaining_evolution_runs,
        is_within_limits=is_within_limits,
        limit_exceeded=limit_exceeded,
    )


async def check_can_evolve(
    db: AsyncSession,
    user_id: UUID,
    tier: SubscriptionTier = SubscriptionTier.FREE,
) -> tuple[bool, str | None]:
    """Check if a user can trigger an evolution.

    Args:
        db: Database session.
        user_id: User ID to check.
        tier: User's subscription tier.

    Returns:
        Tuple of (can_proceed, error_message).
        If can_proceed is False, error_message contains the reason.
    """
    status = await get_user_usage_status(db, user_id, tier)

    if not status.is_within_limits:
        return (
            False,
            f"Evolution limit reached ({status.limits.monthly_evolution_runs}/month). "
            "Upgrade your plan for more evolutions.",
        )

    return True, None


def can_use_model(tier: SubscriptionTier, model: str) -> bool:
    """Check if a tier can use a specific model.

    Premium models require paid tiers.

    Args:
        tier: User's subscription tier.
        model: Model name to check.

    Returns:
        True if the tier can use the model.
    """
    limits = get_tier_limits(tier)

    # Free tier can only use mini/cheap models
    if not limits.can_use_premium_models:
        premium_prefixes = ("o1", "gpt-4-turbo", "gpt-4-0")
        if any(model.startswith(prefix) for prefix in premium_prefixes):
            return False

    return True


def can_create_playbook(tier: SubscriptionTier, current_playbook_count: int) -> bool:
    """Check if a user can create another playbook.

    Args:
        tier: User's subscription tier.
        current_playbook_count: Number of playbooks user currently has.

    Returns:
        True if user can create another playbook.
    """
    limits = get_tier_limits(tier)

    if limits.max_playbooks is None:
        return True

    return current_playbook_count < limits.max_playbooks
