import logging
import re
from typing import TYPE_CHECKING, Tuple, Type

from jycm.common import PLACE_HOLDER_NON_EXIST

if TYPE_CHECKING:
    from jycm.jycm import TreeLevel, YouchamaJsonDiffer


class BaseOperator:
    __operator_name__ = "__base__"

    def __init__(self, path_regex: str, rule_name=None):
        self.path_regex = path_regex
        self.regex = re.compile(f"{self.path_regex}")
        self.rule_name = rule_name

    def rule_info(self):
        if self.rule_name is None:
            return {}
        return {"rule": self.rule_name}

    def match(self, level: 'TreeLevel') -> bool:
        matched = self.regex.search(level.get_path()) is not None
        return matched

    def diff(self, level: 'TreeLevel', instance, drill: bool) -> Tuple[bool, float]:
        raise NotImplementedError


OPERATOR_DICT = {}


def register_operator(operator_class: Type[BaseOperator]):
    if isinstance(operator_class.__operator_name__, str):
        operator_name_list = [operator_class.__operator_name__]
    elif isinstance(operator_class.__operator_name__, list):
        operator_name_list = operator_class.__operator_name__
    else:
        raise TypeError("bad type for ", operator_class.__operator_name__)

    for name in operator_name_list:
        if name in OPERATOR_DICT:
            # just a warning allow overriding
            logging.warning(f"duplicate operator name: {operator_class.__operator_name__}")

        OPERATOR_DICT[name] = operator_class

    return operator_class


def get_operator(name: str):
    if name not in OPERATOR_DICT:
        logging.warning(f"unknown operation=[{name}]")

    return OPERATOR_DICT[name]


@register_operator
class ListItemFieldMatchOperator(BaseOperator):
    __operator_name__ = "operator:list:matchWithField"
    __event__ = "operator:list:matchWithField"

    def __init__(self, path_regex, field, rule_name=None):
        super().__init__(path_regex=path_regex, rule_name=rule_name)
        self.field = field

    def diff(self, level: 'TreeLevel', instance: 'YouchamaJsonDiffer', drill: bool) -> Tuple[bool, float]:
        if drill:
            # 演习的比较
            if level.left[self.field] == level.right[self.field]:
                return True, 1
        else:
            instance.report(self.__event__, level, {
                "field": self.field,
                "path_regex": self.path_regex,
                **self.rule_info()
            })

        return False, -1


@register_operator
class ExpectChangeOperator(BaseOperator):
    __operator_name__ = "operator:expectChange"
    __event__ = "operator:expectChange"

    def diff(self, level: 'TreeLevel', instance: 'YouchamaJsonDiffer', drill: bool) -> Tuple[bool, float]:
        if level.left == level.right:
            if not drill:
                instance.report(self.__event__, level, {
                    "pass": False,
                    "path_regex": self.path_regex,
                    **self.rule_info()
                })
            return True, 0

        if not drill:
            instance.report(self.__event__, level, {
                "pass": True,
                "path_regex": self.path_regex,
                **self.rule_info()
            })

        return True, 1


@register_operator
class ExpectExistOperator(BaseOperator):
    __operator_name__ = "operator:expectExist"
    __event__ = "operator:expectExist"

    def diff(self, level: 'TreeLevel', instance: 'YouchamaJsonDiffer', drill: bool) -> Tuple[bool, float]:

        info = {
            "pass": True,
            "path_regex": self.path_regex,
            **self.rule_info()
        }

        if level.left == PLACE_HOLDER_NON_EXIST:
            info["pass"] = False
            info["left_non_exist"] = True

        if level.right == PLACE_HOLDER_NON_EXIST:
            info["pass"] = False
            info["right_non_exist"] = True

        # 只要到这里就ok
        if not drill:
            instance.report(self.__event__, level, info)

        if info["pass"]:
            return True, 1

        return True, 0


@register_operator
class FloatInRangeOperator(BaseOperator):
    __operator_name__ = "operator:floatInRange"
    __event__ = "operator:floatInRange"

    def __init__(self, path_regex, interval_start, interval_end, rule_name=None):
        super().__init__(path_regex=path_regex, rule_name=rule_name)
        self.interval_start = interval_start
        self.interval_end = interval_end

    def diff(self, level: 'TreeLevel', instance: 'YouchamaJsonDiffer', drill: bool) -> Tuple[bool, float]:
        info = {
            "interval_start": self.interval_start,
            "interval_end": self.interval_end,
            "path_regex": self.path_regex,
            "pass": True,
            **self.rule_info()
        }

        invalid = False
        if not (self.interval_start < level.left <= self.interval_end):
            info.update({"left_invalid": True, "pass": False})
            invalid = True

        if not (self.interval_start < level.right <= self.interval_end):
            info.update({"right_invalid": True, "pass": False})
            invalid = True

        if not drill:
            instance.report(self.__event__, level, info)

        if invalid:
            return True, 0

        # 只要到这里就ok
        return True, 1


@register_operator
class IgnoreOperator(BaseOperator):
    __operator_name__ = [
        "ignore", "diff_word", "diff_image", "diff_pdf"
    ]
    __event__ = "ignore"

    def __init__(self, path_regex: str, *args, **kwargs):
        super().__init__(path_regex, rule_name=kwargs.get("rule_name"))

    def diff(self, level: 'TreeLevel', instance: 'YouchamaJsonDiffer', drill: bool) -> Tuple[bool, float]:
        info = {
            "path_regex": self.path_regex,
            "pass": True,
            **self.rule_info()
        }
        if not drill:
            instance.report(self.__event__, level, info)

        return True, 1


@register_operator
class NumericToleranceOperator(BaseOperator):
    """Compare numeric values with absolute and relative business tolerances."""

    __operator_name__ = ["operator:number:tolerance", "numeric_tolerance"]
    __event__ = "operator:number:tolerance"

    def __init__(self, path_regex, absolute_tolerance=0,
                 relative_tolerance=0, rule_name=None):
        super().__init__(path_regex=path_regex, rule_name=rule_name)
        if absolute_tolerance < 0 or relative_tolerance < 0:
            raise ValueError("numeric tolerances must be non-negative")
        self.absolute_tolerance = absolute_tolerance
        self.relative_tolerance = relative_tolerance

    def diff(self, level: 'TreeLevel', instance: 'YouchamaJsonDiffer',
             drill: bool) -> Tuple[bool, float]:
        numeric = all((
            isinstance(level.left, (int, float)),
            not isinstance(level.left, bool),
            isinstance(level.right, (int, float)),
            not isinstance(level.right, bool),
        ))
        delta = abs(level.left - level.right) if numeric else None
        scale = max(abs(level.left), abs(level.right)) if numeric else 0
        threshold = max(
            self.absolute_tolerance,
            self.relative_tolerance * scale
        )
        passed = numeric and delta <= threshold
        info = {
            "pass": passed,
            "path_regex": self.path_regex,
            "absolute_tolerance": self.absolute_tolerance,
            "relative_tolerance": self.relative_tolerance,
            "delta": delta,
            "threshold": threshold,
            **self.rule_info()
        }
        if not drill:
            instance.report(self.__event__, level, info)
        return True, 1 if passed else 0


@register_operator
class StringNormalizeOperator(BaseOperator):
    """Compare strings after configurable, explainable normalization."""

    __operator_name__ = ["operator:string:normalize", "string_normalize"]
    __event__ = "operator:string:normalize"

    def __init__(self, path_regex, trim=True, lowercase=False,
                 collapse_whitespace=False, rule_name=None):
        super().__init__(path_regex=path_regex, rule_name=rule_name)
        self.trim = trim
        self.lowercase = lowercase
        self.collapse_whitespace = collapse_whitespace

    def normalize(self, value):
        if not isinstance(value, str):
            return value
        if self.trim:
            value = value.strip()
        if self.collapse_whitespace:
            value = " ".join(value.split())
        if self.lowercase:
            value = value.lower()
        return value

    def diff(self, level: 'TreeLevel', instance: 'YouchamaJsonDiffer',
             drill: bool) -> Tuple[bool, float]:
        strings = isinstance(level.left, str) and isinstance(level.right, str)
        normalized_left = self.normalize(level.left)
        normalized_right = self.normalize(level.right)
        passed = strings and normalized_left == normalized_right
        info = {
            "pass": passed,
            "path_regex": self.path_regex,
            "normalized_left": normalized_left,
            "normalized_right": normalized_right,
            "trim": self.trim,
            "lowercase": self.lowercase,
            "collapse_whitespace": self.collapse_whitespace,
            **self.rule_info()
        }
        if not drill:
            instance.report(self.__event__, level, info)
        return True, 1 if passed else 0
