import logging
import re
from typing import TYPE_CHECKING, Tuple, Type

from jycm.common import PLACE_HOLDER_NON_EXIST

if TYPE_CHECKING:
    from jycm.jycm import TreeLevel, YouchamaJsonDiffer


class BaseOperator:
    __operator_name__ = "__base__"

    def __init__(self, path_regex: str):
        self.path_regex = path_regex
        self.regex = re.compile(f"{self.path_regex}")

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
            raise KeyError(f"duplicate operator name: {operator_class.__operator_name__}")

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

    def __init__(self, path_regex, field):
        super().__init__(path_regex=path_regex)
        self.field = field

    def diff(self, level: 'TreeLevel', instance: 'YouchamaJsonDiffer', drill: bool) -> Tuple[bool, float]:
        if drill:
            # 演习的比较
            if level.left[self.field] == level.right[self.field]:
                return True, 1
        else:
            instance.report(self.__event__, level, {"field": self.field, "path_regex": self.path_regex})

        return False, -1


@register_operator
class ExpectChangeOperator(BaseOperator):
    __operator_name__ = "operator:expectChange"
    __event__ = "operator:expectChange"

    def diff(self, level: 'TreeLevel', instance: 'YouchamaJsonDiffer', drill: bool) -> Tuple[bool, float]:
        if level.left == level.right:
            if not drill:
                instance.report(self.__event__, level, {"pass": False, "path_regex": self.path_regex})
            return True, 0

        if not drill:
            instance.report(self.__event__, level, {"pass": True, "path_regex": self.path_regex})

        return True, 1


@register_operator
class ExpectExistOperator(BaseOperator):
    __operator_name__ = "operator:expectExist"
    __event__ = "operator:expectExist"

    def diff(self, level: 'TreeLevel', instance: 'YouchamaJsonDiffer', drill: bool) -> Tuple[bool, float]:

        info = {
            "pass": True,
            "path_regex": self.path_regex
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

    def __init__(self, path_regex, interval_start, interval_end):
        super().__init__(path_regex=path_regex)
        self.interval_start = interval_start
        self.interval_end = interval_end

    def diff(self, level: 'TreeLevel', instance: 'YouchamaJsonDiffer', drill: bool) -> Tuple[bool, float]:
        info = {
            "interval_start": self.interval_start,
            "interval_end": self.interval_end,
            "path_regex": self.path_regex,
            "pass": True
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
        super().__init__(path_regex)

    def diff(self, level: 'TreeLevel', instance: 'YouchamaJsonDiffer', drill: bool) -> Tuple[bool, float]:
        info = {
            "path_regex": self.path_regex,
            "pass": True
        }
        if not drill:
            instance.report(self.__event__, level, info)

        return True, 1
