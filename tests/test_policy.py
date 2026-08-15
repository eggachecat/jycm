import pytest

from jycm import BusinessDiffPolicy, BusinessPolicyError
from jycm.jycm import YouchamaJsonDiffer


def make_order_policy():
    return BusinessDiffPolicy({
        "version": 1,
        "name": "order-api-contract",
        "rules": [
            {
                "name": "orders-have-no-display-order",
                "path": "^orders$",
                "operation": "unordered",
            },
            {
                "name": "orders-match-by-id",
                "path": r"^orders->\[\d+\]$",
                "operation": "match_by",
                "options": {"field": "id"},
            },
            {
                "name": "currency-rounding",
                "path": r"^orders->\[\d+\]->amount$",
                "operation": "numeric_tolerance",
                "options": {"absolute": 0.5, "relative": 0.001},
            },
            {
                "name": "customer-name-formatting",
                "path": r"^orders->\[\d+\]->customer$",
                "operation": "string_normalize",
                "options": {
                    "trim": True,
                    "lowercase": True,
                    "collapse_whitespace": True,
                },
            },
            {
                "name": "volatile-timestamp",
                "path": "^generated_at$",
                "operation": "ignore",
            },
        ],
    })


def test_declarative_policy_compiles_business_semantics_and_explains():
    left = {
        "generated_at": "2026-01-01T00:00:00Z",
        "orders": [
            {"id": "A", "amount": 100.0, "customer": " Acme   Corp "},
            {"id": "B", "amount": 50.0, "customer": "Beta"},
        ],
    }
    right = {
        "generated_at": "2026-01-02T00:00:00Z",
        "orders": [
            {"id": "B", "amount": 50.02, "customer": " beta "},
            {"id": "A", "amount": 100.4, "customer": "acme corp"},
        ],
    }

    differ = make_order_policy().build(left, right)
    explanation = differ.explain()

    assert explanation["equal"] is True
    assert explanation["summary"]["change_count"] == 0
    assert explanation["summary"]["rule_violation_count"] == 0
    assert explanation["summary"]["rule_evaluation_count"] >= 5
    assert explanation["summary"]["policy"]["name"] == "order-api-contract"
    assert "operator:number:tolerance" in explanation["diff"]
    assert "operator:string:normalize" in explanation["diff"]
    assert all(
        record["rule"] == "currency-rounding"
        for record in explanation["diff"]["operator:number:tolerance"]
    )


def test_policy_violation_is_machine_readable_and_affects_equality():
    policy = make_order_policy()
    left = {"orders": [{"id": "A", "amount": 100, "customer": "Acme"}]}
    right = {"orders": [{"id": "A", "amount": 103, "customer": "Acme"}]}

    explanation = policy.compare(left, right, include_diff=False)

    assert explanation["equal"] is False
    assert explanation["summary"]["rule_violation_count"] == 1
    assert explanation["summary"]["affected_paths"] == ["orders->[0]->amount"]
    assert explanation["violations"][0]["rule"] == "currency-rounding"
    assert explanation["violations"][0]["delta"] == 3
    assert "diff" not in explanation


def test_policy_and_json_patch_share_the_same_list_semantics():
    policy = make_order_policy()
    left = {"orders": [{"id": "A", "amount": 100, "customer": "Acme"}]}

    within_tolerance = policy.build(
        left,
        {"orders": [{"id": "A", "amount": 100.2, "customer": " acme "}]},
    )
    assert within_tolerance.diff() is True
    assert within_tolerance.to_json_patch() == []

    outside_tolerance = policy.build(
        left,
        {"orders": [{"id": "A", "amount": 103, "customer": "Acme"}]},
    )
    assert outside_tolerance.diff() is False
    assert outside_tolerance.to_json_patch() == [
        {"op": "replace", "path": "/orders/0/amount", "value": 103}
    ]


def test_differ_from_policy_accepts_legacy_rule_shape():
    differ = YouchamaJsonDiffer.from_policy(
        {"tags": ["a", "b"], "trace": 1},
        {"tags": ["b", "a"], "trace": 2},
        [
            {"operation": "operator:list:ignoreOrder", "value": "^tags$"},
            {"operation": "ignore", "value": "^trace$"},
        ],
    )

    assert differ.diff() is True
    assert differ.business_policy["version"] == 1


@pytest.mark.parametrize("policy, message", [
    ({"version": 2, "rules": []}, "unsupported policy version"),
    ({"rules": {}}, "policy.rules must be a list"),
    ({"rules": ["bad"]}, "must be an object"),
    ({"rules": [{"path": "^x$", "operation": "unknown"}]},
     "unsupported operation"),
    ({"rules": [{"operation": "ignore"}]}, "requires a non-empty path"),
    ({"rules": [{"path": "^x$", "operation": "match_by"}]},
     "requires options.field"),
])
def test_policy_validation_is_actionable(policy, message):
    with pytest.raises(BusinessPolicyError, match=message):
        BusinessDiffPolicy(policy)


def test_negative_numeric_tolerance_is_rejected():
    policy = BusinessDiffPolicy({
        "rules": [{
            "path": "^amount$",
            "operation": "numeric_tolerance",
            "options": {"absolute": -1},
        }]
    })
    with pytest.raises(ValueError, match="non-negative"):
        policy.compile()
