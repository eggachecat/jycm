"""Declarative, serializable business comparison policies for JYCM."""

from copy import deepcopy

from jycm.helper import make_ignore_order_func
from jycm.operator import (
    ExpectChangeOperator,
    ExpectExistOperator,
    FloatInRangeOperator,
    IgnoreOperator,
    ListItemFieldMatchOperator,
    NumericToleranceOperator,
    StringNormalizeOperator,
)


class BusinessPolicyError(ValueError):
    """Raised when a business comparison policy is invalid."""


_OPERATION_ALIASES = {
    "ignore": "ignore",
    "unordered": "unordered",
    "ignore_order": "unordered",
    "operator:list:ignoreOrder": "unordered",
    "match_by": "match_by",
    "operator:list:matchWithField": "match_by",
    "numeric_tolerance": "numeric_tolerance",
    "operator:number:tolerance": "numeric_tolerance",
    "string_normalize": "string_normalize",
    "operator:string:normalize": "string_normalize",
    "expect_change": "expect_change",
    "operator:expectChange": "expect_change",
    "expect_exist": "expect_exist",
    "operator:expectExist": "expect_exist",
    "range": "range",
    "operator:floatInRange": "range",
}


class BusinessDiffPolicy:
    """Compile JSON-friendly business rules into JYCM operators.

    Rules are evaluated by path and can ignore volatile values, treat selected
    lists as unordered, match list records by a business key, compare numbers
    with tolerances, normalize strings, and express expectations.
    """

    VERSION = 1

    def __init__(self, policy=None):
        if policy is None:
            policy = {"version": self.VERSION, "rules": []}
        if isinstance(policy, list):
            policy = {"version": self.VERSION, "rules": policy}
        if not isinstance(policy, dict):
            raise BusinessPolicyError("policy must be an object or a list of rules")

        version = policy.get("version", self.VERSION)
        if version != self.VERSION:
            raise BusinessPolicyError(
                "unsupported policy version: {}".format(version)
            )
        rules = policy.get("rules", [])
        if not isinstance(rules, list):
            raise BusinessPolicyError("policy.rules must be a list")

        self.name = policy.get("name")
        self.rules = [self._normalize_rule(rule, index)
                      for index, rule in enumerate(rules)]

    @classmethod
    def from_dict(cls, policy):
        return cls(policy)

    def _normalize_rule(self, rule, index):
        if not isinstance(rule, dict):
            raise BusinessPolicyError("rule {} must be an object".format(index))
        operation = rule.get("operation")
        if operation not in _OPERATION_ALIASES:
            raise BusinessPolicyError(
                "rule {} has unsupported operation: {}".format(index, operation)
            )
        path = rule.get("path", rule.get("value"))
        if not isinstance(path, str) or not path:
            raise BusinessPolicyError(
                "rule {} requires a non-empty path regex".format(index)
            )
        options = rule.get("options", rule.get("parameter", {}))
        if options is None:
            options = {}
        if not isinstance(options, dict):
            raise BusinessPolicyError("rule {} options must be an object".format(index))

        normalized = {
            "name": rule.get("name") or "rule-{}".format(index + 1),
            "path": path,
            "operation": _OPERATION_ALIASES[operation],
            "options": deepcopy(options),
        }
        if normalized["operation"] == "match_by":
            field = options.get("field")
            if not isinstance(field, str) or not field:
                raise BusinessPolicyError(
                    "match_by rule {} requires options.field".format(index)
                )
        return normalized

    def compile(self):
        operators = []
        unordered_paths = []
        for rule in self.rules:
            operation = rule["operation"]
            path = rule["path"]
            options = rule["options"]
            name = rule["name"]

            if operation == "unordered":
                unordered_paths.append(path)
            elif operation == "ignore":
                operators.append(IgnoreOperator(path, rule_name=name))
            elif operation == "match_by":
                operators.append(ListItemFieldMatchOperator(
                    path, options["field"], rule_name=name
                ))
            elif operation == "numeric_tolerance":
                operators.append(NumericToleranceOperator(
                    path,
                    absolute_tolerance=options.get("absolute", 0),
                    relative_tolerance=options.get("relative", 0),
                    rule_name=name,
                ))
            elif operation == "string_normalize":
                operators.append(StringNormalizeOperator(
                    path,
                    trim=options.get("trim", True),
                    lowercase=options.get("lowercase", False),
                    collapse_whitespace=options.get(
                        "collapse_whitespace", False
                    ),
                    rule_name=name,
                ))
            elif operation == "expect_change":
                operators.append(ExpectChangeOperator(path, rule_name=name))
            elif operation == "expect_exist":
                operators.append(ExpectExistOperator(path, rule_name=name))
            elif operation == "range":
                if "start" not in options or "end" not in options:
                    raise BusinessPolicyError(
                        "range rule {} requires options.start and options.end".format(name)
                    )
                operators.append(FloatInRangeOperator(
                    path,
                    options["start"],
                    options["end"],
                    rule_name=name,
                ))

        return {
            "custom_operators": operators,
            "ignore_order_func": make_ignore_order_func(unordered_paths),
        }

    def build(self, left, right, **differ_options):
        from jycm.jycm import YouchamaJsonDiffer

        compiled = self.compile()
        compiled.update(differ_options)
        differ = YouchamaJsonDiffer(left, right, **compiled)
        differ.business_policy = self.to_dict()
        return differ

    def compare(self, left, right, include_diff=True, **differ_options):
        return self.build(left, right, **differ_options).explain(
            include_diff=include_diff
        )

    def to_dict(self):
        result = {
            "version": self.VERSION,
            "rules": deepcopy(self.rules),
        }
        if self.name is not None:
            result["name"] = self.name
        return result
