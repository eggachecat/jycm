import pytest

from jycm.helper import make_ignore_order_func
from jycm.jycm import YouchamaJsonDiffer
from jycm.operator import IgnoreOperator, ListItemFieldMatchOperator
from jycm.patch import JsonPatchTestFailed, apply_json_patch


def test_json_patch_round_trip_nested_values_and_lists():
    left = {
        "name": "old",
        "meta": {"removed": True, "keep": 1},
        "items": [1, {"value": 2}, "remove-me"],
    }
    right = {
        "name": "new",
        "meta": {"added": None, "keep": 1},
        "items": [1, {"value": 3}, "added", "tail"],
    }

    differ = YouchamaJsonDiffer(left, right)
    patch = differ.to_json_patch(include_tests=True)

    assert apply_json_patch(left, patch) == right
    assert differ.apply_patch() == right
    assert left["name"] == "old"


def test_json_patch_respects_business_diff_rules():
    left = {"generated_at": "yesterday", "tags": ["a", "b"], "amount": 10}
    right = {"generated_at": "today", "tags": ["b", "a"], "amount": 11}
    differ = YouchamaJsonDiffer(
        left,
        right,
        custom_operators=[IgnoreOperator("^generated_at$")],
        ignore_order_func=make_ignore_order_func(["^tags$"]),
    )

    patch = differ.to_json_patch()

    assert patch == [{"op": "replace", "path": "/amount", "value": 11}]
    assert differ.apply_patch() == {"generated_at": "yesterday", "tags": ["a", "b"], "amount": 11}


def test_matching_operator_keeps_diffing_business_fields():
    left = {"orders": [{"id": 7, "status": "pending"}]}
    right = {"orders": [{"id": 7, "status": "paid"}]}
    differ = YouchamaJsonDiffer(
        left,
        right,
        custom_operators=[ListItemFieldMatchOperator(r"^orders->\[\d+\]$", "id")],
    )

    assert differ.to_json_patch() == [
        {"op": "replace", "path": "/orders/0/status", "value": "paid"}
    ]
    assert differ.apply_patch() == right


def test_apply_json_patch_supports_move_copy_and_escaped_paths():
    document = {"a/b": ["first", "second"], "target": {}}
    patch = [
        {"op": "copy", "from": "/a~1b/0", "path": "/target/copied"},
        {"op": "move", "from": "/a~1b/1", "path": "/a~1b/0"},
    ]

    assert apply_json_patch(document, patch) == {
        "a/b": ["second", "first"],
        "target": {"copied": "first"},
    }


def test_json_patch_test_operation_guards_stale_documents():
    patch = YouchamaJsonDiffer({"version": 1}, {"version": 2}).to_json_patch(include_tests=True)

    with pytest.raises(JsonPatchTestFailed):
        apply_json_patch({"version": 9}, patch)


def test_large_equal_list_does_not_use_recursive_lcs_backtracking():
    values = list(range(1200))

    assert YouchamaJsonDiffer(values, list(values)).diff()
