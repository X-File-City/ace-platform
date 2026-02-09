"""Hardened client IP extraction utilities.

Security model:
- Prefer Fly.io's ``Fly-Client-IP`` when available.
- Parse ``X-Forwarded-For`` from right-to-left to avoid spoofed left-most values.
- Only trust forwarded headers from configured trusted proxy CIDRs.
"""

import ipaddress
import logging
from functools import lru_cache

from fastapi import Request

from ace_platform.config import get_settings

logger = logging.getLogger(__name__)

IPNetwork = ipaddress.IPv4Network | ipaddress.IPv6Network


def _parse_ip(value: str | None) -> str | None:
    """Parse and normalize an IP token from headers.

    Returns None for empty/malformed values.
    """
    if not value:
        return None

    token = value.strip().strip("'\"")
    if not token or token.lower() == "unknown":
        return None

    # Support tokens like "for=203.0.113.5" and "for=\"[2001:db8::1]\"".
    if token.lower().startswith("for="):
        token = token[4:].strip().strip("'\"")

    # Strip IPv6 brackets and optional :port.
    if token.startswith("[") and "]" in token:
        token = token[1 : token.index("]")]
    elif token.count(":") == 1:
        host, port = token.rsplit(":", 1)
        if port.isdigit():
            token = host

    # Strip optional IPv6 zone ID suffix.
    if "%" in token:
        token = token.split("%", 1)[0]

    try:
        return str(ipaddress.ip_address(token))
    except ValueError:
        return None


def _parse_x_forwarded_for(header_value: str | None) -> list[str]:
    """Parse X-Forwarded-For into normalized IPs, keeping order."""
    if not header_value:
        return []

    chain: list[str] = []
    for token in header_value.split(","):
        ip = _parse_ip(token)
        if ip:
            chain.append(ip)
    return chain


@lru_cache(maxsize=32)
def _parse_trusted_proxy_networks(raw_cidrs: tuple[str, ...]) -> tuple[IPNetwork, ...]:
    """Parse configured trusted proxy CIDRs."""
    networks: list[IPNetwork] = []
    for raw in raw_cidrs:
        cidr = raw.strip()
        if not cidr:
            continue
        try:
            networks.append(ipaddress.ip_network(cidr, strict=False))
        except ValueError:
            logger.warning("Ignoring invalid trusted proxy CIDR: %s", raw)
    return tuple(networks)


def _is_trusted_proxy(ip: str, trusted_networks: tuple[IPNetwork, ...]) -> bool:
    """Return True when IP falls within configured trusted proxy networks."""
    addr = ipaddress.ip_address(ip)
    return any(addr in network for network in trusted_networks)


def _select_untrusted_from_right(
    chain: list[str],
    trusted_networks: tuple[IPNetwork, ...],
    *,
    skip: set[str] | None = None,
) -> str | None:
    """Pick the first non-trusted IP scanning from right to left."""
    skip = skip or set()
    for ip in reversed(chain):
        if ip in skip:
            continue
        if _is_trusted_proxy(ip, trusted_networks):
            continue
        return ip
    return None


def get_client_ip(request: Request, *, default: str | None = None) -> str | None:
    """Resolve a trustworthy client IP from a request.

    Rules:
    1. If ``Fly-Client-IP`` is present and valid, use Fly-aware parsing.
    2. Otherwise, only trust forwarded headers if direct peer is trusted.
    3. Fall back to direct peer IP.
    """
    settings = get_settings()
    trusted_networks = _parse_trusted_proxy_networks(tuple(settings.trusted_proxy_cidrs))

    remote_ip = _parse_ip(request.client.host if request.client else None)
    fly_client_ip = _parse_ip(request.headers.get("Fly-Client-IP"))
    xff_chain = _parse_x_forwarded_for(request.headers.get("X-Forwarded-For"))

    if fly_client_ip:
        if not xff_chain:
            return fly_client_ip

        # Fly commonly appends its own proxy hop at the right-most XFF position.
        # Drop that extra hop when present; if not present, keep the chain intact.
        fly_adjusted_chain = xff_chain
        if len(xff_chain) > 1 and xff_chain[-1] != fly_client_ip:
            fly_adjusted_chain = xff_chain[:-1]
        selected = _select_untrusted_from_right(
            fly_adjusted_chain,
            trusted_networks,
            skip={remote_ip} if remote_ip else None,
        )
        return selected or fly_client_ip

    if xff_chain and remote_ip and _is_trusted_proxy(remote_ip, trusted_networks):
        selected = _select_untrusted_from_right(
            xff_chain,
            trusted_networks,
            skip={remote_ip},
        )
        if selected:
            return selected

    # Only trust X-Real-IP when immediate peer is trusted.
    real_ip = _parse_ip(request.headers.get("X-Real-IP"))
    if real_ip and remote_ip and _is_trusted_proxy(remote_ip, trusted_networks):
        return real_ip

    return remote_ip or default
