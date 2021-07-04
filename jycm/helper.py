import re
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from jycm.jycm import TreeLevel


def make_ignore_order_func(ignore_order_path_regex_list):
    ignore_order_matcher_list = [re.compile(p) for p in ignore_order_path_regex_list]

    def ignore_order_func(level: 'TreeLevel', drill: bool):
        for matcher in ignore_order_matcher_list:
            if re.search(matcher, level.get_path()) is not None:
                return True
        return False

    return ignore_order_func


def make_json_path_key(path_list: List[str]):
    return "->".join([f"[{v}]" if isinstance(v, int) else v for v in path_list])
