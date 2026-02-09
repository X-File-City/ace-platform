"""Unit tests for semantic playbook matching helpers."""

from __future__ import annotations

from uuid import uuid4

import pytest

from ace_platform.config import Settings
from ace_platform.core.playbook_matching import (
    LOCAL_EMBEDDING_MODEL,
    build_playbook_match_text,
    cosine_similarity,
    generate_embedding,
    generate_local_embedding,
    keyword_overlap_score,
    parse_embedding,
    refresh_playbook_embedding,
    refresh_playbook_embedding_sync,
    score_playbook_match,
)
from ace_platform.db.models import Playbook, PlaybookSource, PlaybookStatus


def _test_playbook(
    name: str = "Deploy App", description: str | None = "Deployment checklist"
) -> Playbook:
    return Playbook(
        user_id=uuid4(),
        name=name,
        description=description,
        status=PlaybookStatus.ACTIVE,
        source=PlaybookSource.USER_CREATED,
    )


def test_build_playbook_match_text_truncates() -> None:
    text = build_playbook_match_text(
        name="Playbook A",
        description="desc",
        content="x" * 100,
        max_chars=40,
    )
    assert len(text) == 40
    assert text.startswith("Name: Playbook A")


def test_generate_local_embedding_is_deterministic() -> None:
    a = generate_local_embedding("deploy app to production")
    b = generate_local_embedding("deploy app to production")
    assert a == b
    assert len(a) > 0


def test_cosine_similarity_returns_expected_bounds() -> None:
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_keyword_overlap_score() -> None:
    score = keyword_overlap_score("deploy web app", "playbook for deploy app process")
    assert score > 0.0


def test_parse_embedding_rejects_invalid_vectors() -> None:
    assert parse_embedding(None) is None
    assert parse_embedding("not-a-list") is None
    assert parse_embedding([1, "x"]) is None


def test_score_playbook_match_prefers_semantic_when_models_align() -> None:
    score, method = score_playbook_match(
        task_description="deploy application to production",
        playbook_text="deployment production application runbook",
        task_embedding=[1.0, 0.0],
        task_embedding_model="test-model",
        playbook_embedding=[1.0, 0.0],
        playbook_embedding_model="test-model",
    )
    assert method == "semantic+keyword"
    assert score >= 0.85


def test_score_playbook_match_falls_back_to_local_when_models_differ() -> None:
    score, method = score_playbook_match(
        task_description="debug flaky tests",
        playbook_text="test debugging and flaky test strategy",
        task_embedding=[1.0, 0.0],
        task_embedding_model="model-a",
        playbook_embedding=[1.0, 0.0],
        playbook_embedding_model="model-b",
    )
    assert method == "local-semantic+keyword"
    assert score > 0.0


@pytest.mark.asyncio
async def test_generate_embedding_falls_back_to_local_without_openai_key() -> None:
    settings = Settings(openai_api_key="")
    embedding, model = await generate_embedding("match this task", settings=settings)
    assert model == LOCAL_EMBEDDING_MODEL
    assert len(embedding) > 0


@pytest.mark.asyncio
async def test_refresh_playbook_embedding_sets_fields_async() -> None:
    playbook = _test_playbook()
    settings = Settings(openai_api_key="")

    await refresh_playbook_embedding(
        playbook,
        content="deployment instructions and rollback plan",
        settings=settings,
    )

    assert playbook.semantic_embedding is not None
    assert playbook.semantic_embedding_model == LOCAL_EMBEDDING_MODEL
    assert playbook.semantic_embedding_updated_at is not None


def test_refresh_playbook_embedding_sets_fields_sync() -> None:
    playbook = _test_playbook()
    settings = Settings(openai_api_key="")

    refresh_playbook_embedding_sync(
        playbook,
        content="incident response and debugging checklist",
        settings=settings,
    )

    assert playbook.semantic_embedding is not None
    assert playbook.semantic_embedding_model == LOCAL_EMBEDDING_MODEL
    assert playbook.semantic_embedding_updated_at is not None
