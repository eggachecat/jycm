import math
from typing import Tuple

from jycm.jycm import TreeLevel, YouchamaJsonDiffer
from jycm.operator import BaseOperator, ExpectChangeOperator, ExpectExistOperator, FloatInRangeOperator


def test_operator_expect_change():
    left = {
        "expect_change_pos": 1,
        "expect_change_neg": 1,
    }

    right = {
        "expect_change_pos": 11111,
        "expect_change_neg": 1,
    }

    ycm = YouchamaJsonDiffer(left, right, custom_operators=[
        ExpectChangeOperator("^expect_change_pos"),
        ExpectChangeOperator("^expect_change_neg")
    ])
    ycm.diff()

    expected = {
        'operator:expectChange': [
            {'left': 1,
             'left_path': 'expect_change_neg',
             'pass': False,
             'path_regex': '^expect_change_neg',
             'right': 1,
             'right_path': 'expect_change_neg'},
            {'left': 1,
             'left_path': 'expect_change_pos',
             'pass': True,
             'path_regex': '^expect_change_pos',
             'right': 11111,
             'right_path': 'expect_change_pos'}],
    }
    assert ycm.to_dict(no_pairs=True) == expected


def test_operator_expect_exist():
    left = {
        "expect_exist_pos": 1,
        "expect_exist_neg": 999,
        "key:removed": "23456",
        "key:changed": "abc"
    }

    right = {
        "expect_exist_pos": "",
        "key:changed": "xyz",
        "key:added": "ooooooo"
    }

    ycm = YouchamaJsonDiffer(left, right, custom_operators=[
        ExpectExistOperator("expect_exist_pos"),
        ExpectExistOperator("expect_exist_neg")
    ])
    ycm.diff()
    expected = {
        'dict:add': [
            {'left': '__NON_EXIST__',
             'left_path': '',
             'right': 'ooooooo',
             'right_path': 'key:added'}
        ],
        'dict:remove': [
            {'left': '23456',
             'left_path': 'key:removed',
             'right': '__NON_EXIST__',
             'right_path': ''}
        ],
        'operator:expectExist': [
            {'left': 999,
             'left_path': 'expect_exist_neg',
             'pass': False,
             'path_regex': 'expect_exist_neg',
             'right': '__NON_EXIST__',
             'right_non_exist': True,
             'right_path': ''},
            {'left': 1,
             'left_path': 'expect_exist_pos',
             'pass': True,
             'path_regex': 'expect_exist_pos',
             'right': '',
             'right_path': 'expect_exist_pos'}
        ],
        'value_changes': [
            {'left': 'abc',
             'left_path': 'key:changed',
             'new': 'xyz',
             'old': 'abc',
             'right': 'xyz',
             'right_path': 'key:changed'}
        ]
    }
    assert ycm.to_dict(no_pairs=True) == expected


def test_operator_float_in_range():
    left = {
        "float_in_range_pos": 1,
        "float_in_range_neg": 2333,
    }

    right = {
        "float_in_range_pos": 1.5,
        "float_in_range_neg": 4567,
    }

    ycm = YouchamaJsonDiffer(left, right, custom_operators=[
        FloatInRangeOperator("float_in_range_pos", 0, 2),
        FloatInRangeOperator("float_in_range_neg", 0, 2),
    ])
    ycm.diff()

    expected = {
        'operator:floatInRange': [
            {'interval_end': 2,
             'interval_start': 0,
             'left': 2333,
             'left_invalid': True,
             'left_path': 'float_in_range_neg',
             'pass': False,
             'path_regex': 'float_in_range_neg',
             'right': 4567,
             'right_invalid': True,
             'right_path': 'float_in_range_neg'},
            {'interval_end': 2,
             'interval_start': 0,
             'left': 1,
             'left_path': 'float_in_range_pos',
             'pass': True,
             'path_regex': 'float_in_range_pos',
             'right': 1.5,
             'right_path': 'float_in_range_pos'}
        ]
    }
    assert ycm.to_dict(no_pairs=True) == expected


def test_operator_custom():
    class L2DistanceOperator(BaseOperator):
        __operator_name__ = "operator:l2distance"
        __event__ = "operator:l2distance"

        def __init__(self, path_regex, distance_threshold):
            super().__init__(path_regex=path_regex)
            self.distance_threshold = distance_threshold

        def diff(self, level: 'TreeLevel', instance, drill: bool) -> Tuple[bool, float]:
            distance = math.sqrt(
                (level.left["x"] - level.right["x"]) ** 2 + (level.left["y"] - level.right["y"]) ** 2
            )
            info = {
                "distance": distance,
                "distance_threshold": self.distance_threshold,
                "pass": distance < self.distance_threshold
            }

            if not drill:
                instance.report(self.__event__, level, info)
            return True, 1 if info["pass"] else 0

    left = {
        "distance_ok": {
            "x": 1,
            "y": 1
        },
        "distance_too_far": {
            "x": 5,
            "y": 5
        },
    }

    right = {
        "distance_ok": {
            "x": 2,
            "y": 2
        },
        "distance_too_far": {
            "x": 7,
            "y": 9
        },
    }

    ycm = YouchamaJsonDiffer(left, right, custom_operators=[
        L2DistanceOperator("distance.*", 3),
    ])

    ycm.diff()

    expected = {
        'operator:l2distance': [
            {'left': {'x': 1, 'y': 1}, 'right': {'x': 2, 'y': 2}, 'left_path': 'distance_ok',
             'right_path': 'distance_ok',
             'distance': 1.4142135623730951, 'distance_threshold': 3, 'pass': True},
            {'left': {'x': 5, 'y': 5}, 'right': {'x': 7, 'y': 9}, 'left_path': 'distance_too_far',
             'right_path': 'distance_too_far', 'distance': 4.47213595499958, 'distance_threshold': 3, 'pass': False}
        ]
    }
    assert ycm.to_dict(no_pairs=True) == expected
