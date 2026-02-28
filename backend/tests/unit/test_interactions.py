"""Unit tests for interaction filtering logic and edge cases."""

import pytest
from app.models.interaction import InteractionLog, InteractionLogCreate
from app.routers.interactions import _filter_by_item_id


def _make_log(id: int, learner_id: int, item_id: int, kind: str = "attempt") -> InteractionLog:
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind=kind)


def test_filter_returns_all_when_item_id_is_none() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, None)
    assert result == interactions


def test_filter_returns_empty_for_empty_input() -> None:
    result = _filter_by_item_id([], 1)
    assert result == []


def test_filter_returns_interaction_with_matching_ids() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 1

def test_filter_excludes_interaction_with_different_learner_id() -> None:
    """Test that when filtering by item_id, interactions with that item_id are included
    even when learner_id is different from item_id."""
    # Create interactions where item_id and learner_id are different
    interactions = [
        _make_log(1, 2, 1),  # item_id=1, learner_id=2 (different values)
        _make_log(2, 1, 1),  # item_id=1, learner_id=1
        _make_log(3, 3, 2),  # item_id=2, learner_id=3
        ]
    
    # Filter by item_id=1
    result = _filter_by_item_id(interactions, 1)
    
    # Verify both interactions with item_id=1 are returned
    assert len(result) == 2
    assert {log.id for log in result} == {1, 2}
    
    # Verify the interaction with different item_id/learner_id values is included
    interaction_with_different_ids = next(log for log in result if log.id == 1)
    assert interaction_with_different_ids.item_id == 1
    assert interaction_with_different_ids.learner_id == 2
    
    # Verify all returned interactions have item_id=1
    for log in result:
        assert log.item_id == 1


def test_filter_with_zero_item_id_returns_empty() -> None:
    """Test boundary case: filtering by item_id=0 returns empty list
    when no interactions have that ID."""
    interactions = [
        _make_log(1, 1, 1),
        _make_log(2, 2, 2),
    ]
    result = _filter_by_item_id(interactions, 0)
    assert result == []


def test_filter_with_all_matching_item_id_returns_all() -> None:
    """Test edge case: when all interactions share the same item_id,
    filtering by that ID returns all of them."""
    interactions = [
        _make_log(1, 1, 5),
        _make_log(2, 2, 5),
        _make_log(3, 3, 5),
    ]
    result = _filter_by_item_id(interactions, 5)
    assert len(result) == 3
    assert all(log.item_id == 5 for log in result)


def test_interaction_log_create_with_empty_kind_is_allowed() -> None:
    """Test boundary case: InteractionLogCreate allows empty string for kind.
    Validation of meaningful kind values would be done at business logic level."""
    log_create = InteractionLogCreate(learner_id=1, item_id=1, kind="")
    assert log_create.kind == ""


def test_interaction_log_create_with_very_long_kind_is_allowed() -> None:
    """Test boundary case: InteractionLogCreate accepts very long kind strings.
    Database column length limits would be enforced at DB level."""
    long_kind = "x" * 500
    log_create = InteractionLogCreate(learner_id=1, item_id=1, kind=long_kind)
    assert log_create.kind == long_kind
    assert len(log_create.kind) == 500


# def test_interaction_log_create_with_special_characters_in_kind() -> None:
#     """Test edge case: InteractionLogCreate accepts special characters in kind field."""
#     special_kind = "click@2024#test$value"
#     log_create = InteractionLogCreate(learner_id=1, item_id=1, kind=special_kind)
#     assert log_create.kind == special_kind