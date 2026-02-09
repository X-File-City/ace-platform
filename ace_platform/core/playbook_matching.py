"""Semantic playbook matching utilities.

Provides shared helpers for:
- Building a semantic text representation of a playbook
- Generating embeddings (OpenAI with local fallback)
- Scoring playbook relevance for a task description
"""

from __future__ import annotations

import hashlib
import logging
import math
import re
from datetime import UTC, datetime
from typing import Any

import openai

from ace_platform.config import Settings, get_settings
from ace_platform.db.models import Playbook

logger = logging.getLogger(__name__)

LOCAL_EMBEDDING_MODEL = "local-hash-v1"
LOCAL_EMBEDDING_DIMENSIONS = 256

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def build_playbook_match_text(
    *,
    name: str,
    description: str | None,
    content: str | None,
    max_chars: int,
) -> str:
    """Build canonical text used for semantic matching."""
    pieces = [
        f"Name: {name.strip()}",
        f"Description: {(description or '').strip()}",
        f"Content:\n{(content or '').strip()}",
    ]
    text = "\n\n".join(pieces).strip()
    if len(text) > max_chars:
        return text[:max_chars]
    return text


def _normalize_token(token: str) -> str:
    """Lightweight token normalization for better lexical matching."""
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 4 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 3 and token.endswith(("ed", "es")):
        return token[:-2]
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    return token


def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase alphanumeric terms."""
    return [_normalize_token(tok) for tok in _TOKEN_PATTERN.findall(text.lower())]


def _normalize_vector(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0:
        return vector
    return [x / norm for x in vector]


def generate_local_embedding(
    text: str, dimensions: int = LOCAL_EMBEDDING_DIMENSIONS
) -> list[float]:
    """Create deterministic local embedding using hashed token buckets."""
    vector = [0.0] * dimensions
    tokens = _tokenize(text)

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "big") % dimensions
        vector[idx] += 1.0

        # Add simple character tri-grams to capture morphology/context.
        if len(token) >= 3:
            for i in range(len(token) - 2):
                trigram = token[i : i + 3]
                tri_digest = hashlib.sha256(trigram.encode("utf-8")).digest()
                tri_idx = int.from_bytes(tri_digest[:4], "big") % dimensions
                vector[tri_idx] += 0.15

    return _normalize_vector(vector)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity for same-dimension vectors."""
    if not a or not b:
        return 0.0
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    score = dot / (norm_a * norm_b)
    return max(0.0, min(1.0, score))


def keyword_overlap_score(task_description: str, playbook_text: str) -> float:
    """Compute overlap score between task tokens and playbook tokens."""
    task_tokens = set(_tokenize(task_description))
    playbook_tokens = set(_tokenize(playbook_text))

    if not task_tokens or not playbook_tokens:
        return 0.0

    overlap = len(task_tokens & playbook_tokens)
    return overlap / len(task_tokens)


def parse_embedding(raw_embedding: Any) -> list[float] | None:
    """Parse an arbitrary DB value into a float vector, if possible."""
    if not isinstance(raw_embedding, list) or not raw_embedding:
        return None

    parsed: list[float] = []
    for value in raw_embedding:
        try:
            parsed.append(float(value))
        except (TypeError, ValueError):
            return None
    return parsed


async def generate_embedding(
    text: str,
    *,
    settings: Settings | None = None,
) -> tuple[list[float], str]:
    """Generate embedding using OpenAI when available, else local fallback."""
    settings = settings or get_settings()
    model = settings.playbook_embedding_model

    if settings.openai_api_key:
        client: openai.AsyncOpenAI | None = None
        try:
            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.embeddings.create(model=model, input=text)
            embedding = list(response.data[0].embedding)
            if embedding:
                return embedding, model
        except Exception:
            logger.warning("Falling back to local playbook embeddings", exc_info=True)
        finally:
            if client is not None:
                close = getattr(client, "close", None)
                if close is not None:
                    await close()

    return generate_local_embedding(text), LOCAL_EMBEDDING_MODEL


def generate_embedding_sync(
    text: str,
    *,
    settings: Settings | None = None,
) -> tuple[list[float], str]:
    """Synchronous variant of embedding generation for worker code."""
    settings = settings or get_settings()
    model = settings.playbook_embedding_model

    if settings.openai_api_key:
        client: openai.OpenAI | None = None
        try:
            client = openai.OpenAI(api_key=settings.openai_api_key)
            response = client.embeddings.create(model=model, input=text)
            embedding = list(response.data[0].embedding)
            if embedding:
                return embedding, model
        except Exception:
            logger.warning("Falling back to local playbook embeddings", exc_info=True)
        finally:
            if client is not None:
                close = getattr(client, "close", None)
                if close is not None:
                    close()

    return generate_local_embedding(text), LOCAL_EMBEDDING_MODEL


async def refresh_playbook_embedding(
    playbook: Playbook,
    *,
    content: str | None,
    settings: Settings | None = None,
) -> None:
    """Update a playbook's stored embedding fields."""
    settings = settings or get_settings()
    text = build_playbook_match_text(
        name=playbook.name,
        description=playbook.description,
        content=content,
        max_chars=settings.playbook_embedding_max_chars,
    )
    embedding, model = await generate_embedding(text, settings=settings)
    playbook.semantic_embedding = embedding
    playbook.semantic_embedding_model = model
    playbook.semantic_embedding_updated_at = datetime.now(UTC)


def refresh_playbook_embedding_sync(
    playbook: Playbook,
    *,
    content: str | None,
    settings: Settings | None = None,
) -> None:
    """Synchronous variant for worker code paths."""
    settings = settings or get_settings()
    text = build_playbook_match_text(
        name=playbook.name,
        description=playbook.description,
        content=content,
        max_chars=settings.playbook_embedding_max_chars,
    )
    embedding, model = generate_embedding_sync(text, settings=settings)
    playbook.semantic_embedding = embedding
    playbook.semantic_embedding_model = model
    playbook.semantic_embedding_updated_at = datetime.now(UTC)


def score_playbook_match(
    *,
    task_description: str,
    playbook_text: str,
    task_embedding: list[float],
    task_embedding_model: str,
    playbook_embedding: list[float] | None,
    playbook_embedding_model: str | None,
    local_task_embedding: list[float] | None = None,
) -> tuple[float, str]:
    """Score playbook relevance with semantic + lexical signal.

    Returns:
        Tuple of (score, method)
    """
    keyword_score = keyword_overlap_score(task_description, playbook_text)

    if (
        playbook_embedding
        and playbook_embedding_model
        and playbook_embedding_model == task_embedding_model
        and len(playbook_embedding) == len(task_embedding)
    ):
        semantic_score = cosine_similarity(task_embedding, playbook_embedding)
        score = (semantic_score * 0.85) + (keyword_score * 0.15)
        return max(0.0, min(1.0, score)), "semantic+keyword"

    if local_task_embedding is None:
        local_task_embedding = generate_local_embedding(task_description)
    local_playbook_embedding = generate_local_embedding(playbook_text)
    local_semantic_score = cosine_similarity(local_task_embedding, local_playbook_embedding)
    score = (local_semantic_score * 0.7) + (keyword_score * 0.3)
    return max(0.0, min(1.0, score)), "local-semantic+keyword"
