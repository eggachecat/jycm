from jycm.helper import make_ignore_order_func
from jycm.jycm import YouchamaJsonDiffer
from jycm.operator import ListItemFieldMatchOperator


def test_only_primitive():
    left = {
        "a": 1,
        "b": 2,
        "d": "12345",
        "f": False,
        "e": [
            {"x": 1, "y": 1},
            {"x": 2, "y": 2},
            {"x": 3, "y": 3},
            {"x": 4, "y": 4},
        ]
    }

    right = {
        "a": 1,
        "b": 3,
        "c": 4,
        "f": True,
        "e": [
            {"x": 0, "y": 1},
            {"x": 2, "y": 2},
            {"x": 3, "y": 3},
            {"x": 5, "y": 5},
        ]
    }

    ycm = YouchamaJsonDiffer(left, right)
    ycm.diff()

    expected = {
        'dict:add': [
            {'left': '__NON_EXIST__',
             'left_path': '',
             'right': 4,
             'right_path': 'c'}
        ],
        'dict:remove': [
            {'left': '12345',
             'left_path': 'd',
             'right': '__NON_EXIST__',
             'right_path': ''}
        ],
        'list:add': [
            {'left': '__NON_EXIST__',
             'left_path': '',
             'right': {'x': 5, 'y': 5},
             'right_path': 'e->[3]'}
        ],
        'list:remove': [
            {'left': {'x': 4, 'y': 4},
             'left_path': 'e->[3]',
             'right': '__NON_EXIST__',
             'right_path': ''}
        ],
        'value_changes': [
            {'left': 2,
             'left_path': 'b',
             'new': 3,
             'old': 2,
             'right': 3,
             'right_path': 'b'},
            {'left': 1,
             'left_path': 'e->[0]->x',
             'new': 0,
             'old': 1,
             'right': 0,
             'right_path': 'e->[0]->x'},
            {'left': False,
             'left_path': 'f',
             'new': True,
             'old': False,
             'right': True,
             'right_path': 'f'}
        ]
    }
    assert ycm.to_dict(no_pairs=True) == expected


def test_with_list_1():
    left = {
        "v": [1, 2, 3]
    }

    right = {
        "v": [1, 2, 3]
    }

    ycm = YouchamaJsonDiffer(left, right)
    ycm.diff()
    expected = {}
    assert ycm.to_dict(no_pairs=True) == expected


def test_with_list_2():
    left = {
        "v": [{"a": 1, "b": 2, "c": 3}, {"c": 1, "d": 2, "e": 3}, {"f": 1, "g": 2, "h": 3}, {"x": 1, "y": 2}]
    }

    right = {
        "v": [{"a": 1, "b": 2, "c": 8}, {"c": 1, "d": 12, "e": 3}, {"f": 11, "g": 2, "h": 3}, {"z": 1}, 2]
    }

    ycm = YouchamaJsonDiffer(left, right)
    ycm.diff()

    expected = {
        'list:add': [
            {'left': '__NON_EXIST__', 'right': {'z': 1}, 'left_path': '', 'right_path': 'v->[3]'},
            {'left': '__NON_EXIST__', 'right': 2, 'left_path': '', 'right_path': 'v->[4]'}
        ],
        'list:remove': [
            {'left': {'x': 1, 'y': 2}, 'right': '__NON_EXIST__', 'left_path': 'v->[3]', 'right_path': ''}
        ],
        'value_changes': [
            {'left': 3, 'right': 8, 'left_path': 'v->[0]->c', 'right_path': 'v->[0]->c', 'old': 3, 'new': 8},
            {'left': 2, 'right': 12, 'left_path': 'v->[1]->d', 'right_path': 'v->[1]->d', 'old': 2,
             'new': 12},
            {'left': 1, 'right': 11, 'left_path': 'v->[2]->f', 'right_path': 'v->[2]->f', 'old': 1,
             'new': 11}
        ]
    }

    assert ycm.to_dict(no_pairs=True) == expected


def test_with_list_3():
    left = {
        "v": [9, 1, 2, 3, 7]
    }
    right = {
        "v": [0, 1, 3, 4]
    }
    ycm = YouchamaJsonDiffer(left, right)
    ycm.diff()
    expected = {
        'list:add': [
            {'left': '__NON_EXIST__',
             'left_path': '',
             'right': 0,
             'right_path': 'v->[0]'},
            {'left': '__NON_EXIST__',
             'left_path': '',
             'right': 4,
             'right_path': 'v->[3]'}
        ],
        'list:remove': [
            {'left': 9,
             'left_path': 'v->[0]',
             'right': '__NON_EXIST__',
             'right_path': ''},
            {'left': 2,
             'left_path': 'v->[2]',
             'right': '__NON_EXIST__',
             'right_path': ''},
            {'left': 7,
             'left_path': 'v->[4]',
             'right': '__NON_EXIST__',
             'right_path': ''}
        ]
    }
    assert ycm.to_dict(no_pairs=True) == expected


def test_with_list_4():
    left = {
        "v": [
            {"id": 1, "label": "label:1"},
            {"id": 2, "label": "label:2"},
            {"id": 3, "label": "label:3"}
        ]
    }
    right = {
        "v": [
            {"id": 1, "label": "label:1"},
            {"id": 4, "label": "label:4"},
            {"id": 2, "label": "label:22222"},
            {"id": 3, "label": "label:3"}
        ]
    }

    ycm = YouchamaJsonDiffer(left, right, custom_operators=[
        ListItemFieldMatchOperator("^v->\\[\\d+\\]$", "id")
    ])
    ycm.diff()

    expected = {
        'list:add': [
            {'left': '__NON_EXIST__',
             'left_path': '',
             'right': {'id': 4, 'label': 'label:4'},
             'right_path': 'v->[1]'}
        ],
        'operator:list:matchWithField': [
            {'field': 'id',
             'left': {'id': 1, 'label': 'label:1'},
             'left_path': 'v->[0]',
             'path_regex': '^v->\\[\\d+\\]$',
             'right': {'id': 1, 'label': 'label:1'},
             'right_path': 'v->[0]'},
            {'field': 'id',
             'left': {'id': 2, 'label': 'label:2'},
             'left_path': 'v->[1]',
             'path_regex': '^v->\\[\\d+\\]$',
             'right': {'id': 2, 'label': 'label:22222'},
             'right_path': 'v->[2]'},
            {'field': 'id',
             'left': {'id': 3, 'label': 'label:3'},
             'left_path': 'v->[2]',
             'path_regex': '^v->\\[\\d+\\]$',
             'right': {'id': 3, 'label': 'label:3'},
             'right_path': 'v->[3]'}
        ],
        'value_changes': [
            {'left': 'label:2',
             'left_path': 'v->[1]->label',
             'new': 'label:22222',
             'old': 'label:2',
             'right': 'label:22222',
             'right_path': 'v->[2]->label'}
        ]
    }
    assert ycm.to_dict(no_pairs=True) == expected


def test_with_list_without_order():
    left = {
        "ignore_order": [1, 2, 3],
        "not_ignore_order": [1, 2, 3]
    }

    right = {
        "ignore_order": [3, 2, 1],
        "not_ignore_order": [3, 2, 1]
    }

    ycm = YouchamaJsonDiffer(left, right, ignore_order_func=make_ignore_order_func([
        "^ignore_order$"
    ]))
    ycm.diff()
    expected = {
        'list:add': [
            {'left': '__NON_EXIST__',
             'left_path': '',
             'right': 2,
             'right_path': 'not_ignore_order->[1]'},
            {'left': '__NON_EXIST__',
             'left_path': '',
             'right': 1,
             'right_path': 'not_ignore_order->[2]'}
        ],
        'list:remove': [
            {'left': 1,
             'left_path': 'not_ignore_order->[0]',
             'right': '__NON_EXIST__',
             'right_path': ''},
            {'left': 2,
             'left_path': 'not_ignore_order->[1]',
             'right': '__NON_EXIST__',
             'right_path': ''}
        ]
    }
    assert ycm.to_dict(no_pairs=True) == expected


def test_with_list_without_order_with_matching_field():
    left = {
        "ignore_order": [
            {"id": 1, "label": "label:1"},
            {"id": 2, "label": "label:2"},
            {"id": 3, "label": "label:3"}
        ],
    }

    right = {
        "ignore_order": [
            {"id": 4, "label": "label:4444"},
            {"id": 2, "label": "label:2222"},
            {"id": 1, "label": "label:1111"},
        ]
    }

    ycm = YouchamaJsonDiffer(left, right, ignore_order_func=make_ignore_order_func([
        "^ignore_order$"
    ]), custom_operators=[
        ListItemFieldMatchOperator("^ignore_order->\\[\\d+\\]$", "id")
    ])
    ycm.diff()
    expected = {
        'list:add': [
            {'left': '__NON_EXIST__',
             'left_path': '',
             'right': {'id': 4, 'label': 'label:4444'},
             'right_path': 'ignore_order->[0]'}
        ],
        'list:remove': [
            {'left': {'id': 3, 'label': 'label:3'},
             'left_path': 'ignore_order->[2]',
             'right': '__NON_EXIST__',
             'right_path': ''}
        ],
        'operator:list:matchWithField': [
            {'field': 'id',
             'path_regex': '^ignore_order->\\[\\d+\\]$',
             'left': {'id': 1, 'label': 'label:1'},
             'left_path': 'ignore_order->[0]',
             'right': {'id': 1, 'label': 'label:1111'},
             'right_path': 'ignore_order->[2]'},
            {'field': 'id',
             'path_regex': '^ignore_order->\\[\\d+\\]$',
             'left': {'id': 2, 'label': 'label:2'},
             'left_path': 'ignore_order->[1]',
             'right': {'id': 2, 'label': 'label:2222'},
             'right_path': 'ignore_order->[1]'}
        ],
        'value_changes': [
            {'left': 'label:1',
             'left_path': 'ignore_order->[0]->label',
             'new': 'label:1111',
             'old': 'label:1',
             'right': 'label:1111',
             'right_path': 'ignore_order->[2]->label'},
            {'left': 'label:2',
             'left_path': 'ignore_order->[1]->label',
             'new': 'label:2222',
             'old': 'label:2',
             'right': 'label:2222',
             'right_path': 'ignore_order->[1]->label'}
        ]
    }
    assert ycm.to_dict(no_pairs=True) == expected


def test_matching_with_list():
    left = [
        {
            "id": 2,
            "label": "label:2"
        },
        {
            "id": 1,
            "label": "label:1"
        },
        {
            "id": 5,
            "label": "label:5"
        },
    ]

    right = [
        {
            "id": 9,
            "label": "label:9"
        },
        {
            "id": 1,
            "label": "label:1"
        },
        {
            "id": 5,
            "label": "label:9"
        },
    ]

    ycm = YouchamaJsonDiffer(left, right)

    ycm.diff()

    expected = {'list:add': [
        {'left': '__NON_EXIST__', 'right': {'id': 9, 'label': 'label:9'}, 'left_path': '', 'right_path': '[0]'}],
        'list:remove': [{'left': {'id': 2, 'label': 'label:2'}, 'right': '__NON_EXIST__', 'left_path': '[0]',
                         'right_path': ''}], 'value_changes': [
            {'left': 'label:5', 'right': 'label:9', 'left_path': '[2]->label', 'right_path': '[2]->label',
             'old': 'label:5', 'new': 'label:9'}]}
    assert ycm.to_dict(no_pairs=True) == expected


def test_set_in_set():
    left = {
        "set_in_set": [
            {
                "id": 1,
                "label": "label:1",
                "set": [
                    1,
                    2,
                    3
                ]
            },
            {
                "id": 2,
                "label": "label:2",
                "set": [
                    4,
                    5,
                    6
                ]
            }
        ]
    }

    right = {
        "set_in_set": [
            {
                "id": 2,
                "label": "label:2",
                "set": [
                    6,
                    5,
                    4
                ]
            },
            {
                "id": 1,
                "label": "label:1",
                "set": [
                    3,
                    2,
                    1
                ]
            }
        ]
    }

    ycm = YouchamaJsonDiffer(left, right, ignore_order_func=make_ignore_order_func([
        "^set_in_set$",
        "^set_in_set->\\[\\d+\\]->set$"
    ]))

    ycm.diff()

    expected = {}

    assert ycm.to_dict(no_pairs=True) == expected


def test_fuzzy_matching_in_set():
    left = {
        "set": [
            [{"id": 0, "label": 0}],
            [{"id": 1, "label": 1}],
            [{"id": 2, "label": 2}, "c", "d"],
            [{"id": 3, "label": 3}, "e", "f"],
            [{"id": 4, "label": 4}, "g", "h"],
            [{"id": 5, "label": 5}, "i", "j"]
        ]
    }

    right = {
        "set": [
            [{"id": 4, "label": 444}],
            [{"id": 1, "label": 3}, "e", "f"],
            [{"id": 1, "label": 111}],
            [{"id": 5, "label": 5}, "i", "j"],
            [{"id": 2, "label": 2}, "c", "dddd"],
            [{"id": 9, "label": 9}, "z", "k"],

        ]
    }

    ycm = YouchamaJsonDiffer(left, right, ignore_order_func=make_ignore_order_func([
        "^set$",
    ]), debug=False, use_cache=True)

    ycm.diff()

    expected = {
        'list:add': [
            {'left': '__NON_EXIST__', 'right': [{'id': 9, 'label': 9}, 'z', 'k'], 'left_path': '',
             'right_path': 'set->[5]'},
            {'left': '__NON_EXIST__', 'right': 'dddd', 'left_path': '', 'right_path': 'set->[4]->[2]'}
        ],
        'list:remove': [
            {'left': [{'id': 0, 'label': 0}], 'right': '__NON_EXIST__', 'left_path': 'set->[0]', 'right_path': ''},
            {'left': 'd', 'right': '__NON_EXIST__', 'left_path': 'set->[2]->[2]', 'right_path': ''},
            {'left': 'g', 'right': '__NON_EXIST__', 'left_path': 'set->[4]->[1]', 'right_path': ''},
            {'left': 'h', 'right': '__NON_EXIST__', 'left_path': 'set->[4]->[2]', 'right_path': ''}
        ],
        'value_changes': [
            {'left': 1, 'right': 111, 'left_path': 'set->[1]->[0]->label', 'right_path': 'set->[2]->[0]->label',
             'old': 1,
             'new': 111},
            {'left': 3, 'right': 1, 'left_path': 'set->[3]->[0]->id', 'right_path': 'set->[1]->[0]->id', 'old': 3,
             'new': 1},
            {'left': 4, 'right': 444, 'left_path': 'set->[4]->[0]->label', 'right_path': 'set->[0]->[0]->label',
             'old': 4,
             'new': 444}
        ]
    }
    assert ycm.to_dict(no_pairs=True) == expected


def test_fuzzy_matching_in_set_2():
    left = {
        "set": [
            {"id": 0, "label": 0},
            {"id": 1, "label": 1},
            {"id": 2, "label": 2},
            {"id": 3, "label": 3},
            {"id": 4, "label": 4},
            {"id": 5, "label": 5},
        ]
    }

    right = {
        "set": [
            {"id": 4, "label": 444},
            {"id": 3, "label": 3},
            {"id": 1, "label": 111},
            {"id": 5, "label": 5},
            {"id": 2, "label": 2},
            {"id": 9, "label": 9},
            {"id": 10, "label": 10},

        ]
    }

    ycm = YouchamaJsonDiffer(left, right, ignore_order_func=make_ignore_order_func([
        "^set$",
    ]))

    ycm.diff()

    expected = {
        'list:add': [
            {'left': '__NON_EXIST__', 'right': {'id': 9, 'label': 9}, 'left_path': '', 'right_path': 'set->[5]'},
            {'left': '__NON_EXIST__', 'right': {'id': 10, 'label': 10}, 'left_path': '', 'right_path': 'set->[6]'}
        ],
        'list:remove': [
            {'left': {'id': 0, 'label': 0}, 'right': '__NON_EXIST__', 'left_path': 'set->[0]',
             'right_path': ''}
        ], 'value_changes': [
            {'left': 1, 'right': 111, 'left_path': 'set->[1]->label', 'right_path': 'set->[2]->label', 'old': 1,
             'new': 111},
            {'left': 4, 'right': 444, 'left_path': 'set->[4]->label', 'right_path': 'set->[0]->label', 'old': 4,
             'new': 444}
        ]
    }

    assert ycm.to_dict(no_pairs=True) == expected


def test_different_types_list():
    left = {
        "set": [
            ["a", 0, 1],
            ["b", 1, 2]
        ]
    }

    right = {
        "set": [
            ["b", 1, 2],
            ["a", 0, 1]
        ]
    }

    ycm = YouchamaJsonDiffer(left, right, ignore_order_func=make_ignore_order_func([
        "^set$",
    ]))

    ycm.diff()


def test_set_in_set_2():
    left = {
        "set_in_set": [
            {
                "id": 1,
                "label": "label:1",
                "set": [
                    1,
                    5,
                    3
                ]
            },
            {
                "id": 2,
                "label": "label:2",
                "set": [
                    4,
                    5,
                    6
                ]
            }
        ]
    }

    right = {
        "set_in_set": [
            {
                "id": 2,
                "label": "label:2",
                "set": [
                    6,
                    5,
                    4
                ]
            },
            {
                "id": 1,
                "label": "label:1111",
                "set": [
                    3,
                    2,
                    1
                ]
            }
        ]
    }

    ycm = YouchamaJsonDiffer(left, right, ignore_order_func=make_ignore_order_func([
        f"^set_in_set$",
        f"^set_in_set->\\[\\d+\\]->set$"
    ]))

    ycm.diff()

    expected = {
        'list:add': [
            {'left': '__NON_EXIST__', 'right': 2, 'left_path': '', 'right_path': 'set_in_set->[1]->set->[1]'}
        ],
        'list:remove': [
            {'left': 5, 'right': '__NON_EXIST__', 'left_path': 'set_in_set->[0]->set->[1]', 'right_path': ''}
        ],
        'value_changes': [
            {'left': 'label:1', 'right': 'label:1111', 'left_path': 'set_in_set->[0]->label',
             'right_path': 'set_in_set->[1]->label', 'old': 'label:1', 'new': 'label:1111'}
        ]
    }

    assert ycm.to_dict(no_pairs=True) == expected


def test_compare_list_with_order_fast():
    left = {
        "list": [
            {"a": [1, 1, 1], "b": "111111", "c": {"c-1": 1, "c-2": 1}},
            {"a": [2, 2, 2], "b": "222222", "c": {"c-1": 2, "c-2": 2}},
            {"a": [3, 3, 3], "b": "333333", "c": {"c-1": 3, "c-2": 3}},
        ]
    }

    right = {
        "list": [
            {"a": [0, 0, 0], "b": "111111", "c": {"c-1": 0, "c-2": 0}},
            {"a": [1, 1, 1], "b": "111111", "c": {"c-1": 1, "c-2": 1}},
            {"a": [3, 3, 3], "b": "444444", "c": {"c-1": 3, "c-2": 3}},
            {"a": [4, 4, 4], "b": "444444", "c": {"c-1": 4, "c-2": 4}},
        ]
    }

    ycm = YouchamaJsonDiffer(left, right, fast_mode=True)
    ycm.diff()

    expected = {
        'list:add': [
            {'left': '__NON_EXIST__', 'right': {'a': [4, 4, 4], 'b': '444444', 'c': {'c-1': 4, 'c-2': 4}},
             'left_path': '',
             'right_path': 'list->[3]'}
        ],
        'value_changes': [
            {'left': 1, 'right': 0, 'left_path': 'list->[0]->a->[0]', 'right_path': 'list->[0]->a->[0]', 'old': 1,
             'new': 0},
            {'left': 1, 'right': 0, 'left_path': 'list->[0]->a->[1]', 'right_path': 'list->[0]->a->[1]', 'old': 1,
             'new': 0},
            {'left': 1, 'right': 0, 'left_path': 'list->[0]->a->[2]', 'right_path': 'list->[0]->a->[2]', 'old': 1,
             'new': 0},
            {'left': 1, 'right': 0, 'left_path': 'list->[0]->c->c-1', 'right_path': 'list->[0]->c->c-1', 'old': 1,
             'new': 0},
            {'left': 1, 'right': 0, 'left_path': 'list->[0]->c->c-2', 'right_path': 'list->[0]->c->c-2', 'old': 1,
             'new': 0},
            {'left': 2, 'right': 1, 'left_path': 'list->[1]->a->[0]', 'right_path': 'list->[1]->a->[0]', 'old': 2,
             'new': 1},
            {'left': 2, 'right': 1, 'left_path': 'list->[1]->a->[1]', 'right_path': 'list->[1]->a->[1]', 'old': 2,
             'new': 1},
            {'left': 2, 'right': 1, 'left_path': 'list->[1]->a->[2]', 'right_path': 'list->[1]->a->[2]', 'old': 2,
             'new': 1},
            {'left': '222222', 'right': '111111', 'left_path': 'list->[1]->b', 'right_path': 'list->[1]->b',
             'old': '222222', 'new': '111111'},
            {'left': 2, 'right': 1, 'left_path': 'list->[1]->c->c-1', 'right_path': 'list->[1]->c->c-1', 'old': 2,
             'new': 1},
            {'left': 2, 'right': 1, 'left_path': 'list->[1]->c->c-2', 'right_path': 'list->[1]->c->c-2', 'old': 2,
             'new': 1}, {'left': '333333', 'right': '444444', 'left_path': 'list->[2]->b', 'right_path': 'list->[2]->b',
                         'old': '333333', 'new': '444444'}
        ]
    }

    assert expected == ycm.to_dict(no_pairs=True)
