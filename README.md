# JYCM

![Build Status](https://github.com/eggachecat/jycm/actions/workflows/on-push.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/jycm.svg)](https://badge.fury.io/py/jycm)
[![Coverage Status](https://coveralls.io/repos/github/eggachecat/jycm/badge.svg?branch=master&kill_cache=1)](https://coveralls.io/github/eggachecat/jycm?branch=master)

A flexible json diff framework for minimalist.

JYCM = Json You-Cha-Ma (「is there a difference」in Chinese)

Also see a [**Javascript Implementation**](https://github.com/eggachecat/jycm-js)

# Live DEMO

See [https://eggachecat.github.io/jycm-json-diff-viewer](https://eggachecat.github.io/jycm-json-diff-viewer) for a live demo.


# Reference
- [deepdiff](https://github.com/seperman/deepdiff)
    - how results are reported in JYCM is learnt from this amazing framework.
    - how TreeLevel is designed in JYCM is learnt from this amazing framework.
    
- [gojsondif](https://github.com/yudai/gojsondiff)
    - Fuzzy matching part of JYCM is learnt from this amazing framework.

# Install
> pip install jycm

## Business Diff Policy

Define domain equality as versioned, serializable data and reuse the same policy
in Python and JavaScript. Rules can ignore volatile fields, compare unordered
collections, pair records by identity, normalize text, apply absolute or
relative numeric tolerances, and assert expected values or changes.

```python
from jycm import BusinessDiffPolicy

policy = BusinessDiffPolicy({
    "version": 1,
    "name": "order-contract",
    "rules": [
        {"name": "items-as-set", "path": "^items$", "operation": "unordered"},
        {
            "name": "match-sku",
            "path": r"^items->\[\d+\]$",
            "operation": "match_by",
            "options": {"field": "sku"},
        },
        {
            "name": "money-rounding",
            "path": r"^items->\[\d+\]->price$",
            "operation": "numeric_tolerance",
            "options": {"absolute": 0.01, "relative": 0.001},
        },
        {"name": "trace-id", "path": "^trace_id$", "operation": "ignore"},
    ],
})

explanation = policy.compare(before, after)
print(explanation["equal"])
print(explanation["summary"])
print(explanation["violations"])

differ = policy.build(before, after)
patch = differ.to_json_patch()  # uses the same business semantics
```

`explain()` returns dashboard-ready counts, affected paths, named rule
violations, matched-pair totals, and the structured diff. Policies also accept
the original `value` / `parameter` rule shape for backward compatibility.

### Agent Skill for Codex and Claude

This repository includes the portable `jycm-business-diff` Agent Skill. It
teaches compatible coding agents to design Policy rules from business examples,
validate fixtures, generate and verify Patch, integrate the React UI, and plan
safe deployment.

```bash
# user-wide Codex installation
python skills/jycm-business-diff/scripts/install_skill.py --client codex

# user-wide Claude Code installation
python skills/jycm-business-diff/scripts/install_skill.py --client claude

# open Agent Skills project installation
python skills/jycm-business-diff/scripts/install_skill.py --client agents --project .
```

The canonical skill follows the open Agent Skills `SKILL.md` format and includes
policy/deployment references plus a deterministic validation and comparison
workflow. Existing installs are never overwritten unless `--force` is passed;
the installer creates a timestamped backup first.

# Renderer
Yes! JYCM has a [rendering tool](https://github.com/eggachecat/react-jycm-viewer) out of the box!

![gif-show](https://media.giphy.com/media/03PbgaFqYCwyhzOUSU/giphy.gif)


# [Document](https://jycm.readthedocs.io/en/latest/index.html)

# Use JYCM with viewer directly from Terminal
## Easy
```bash
python -m jycm --help 
# Usage: python -m jycm [OPTIONS]

# Options:
#   --interactive  Enter interactive mode
#   --left TEXT    Left Json
#   --right TEXT   Right Json
#   --rules TEXT   Rules
#   --output TEXT  The folder where the results will be dumped.
#   --open         Open the browser; This is valid only if you specify the
#                  output parameter.
#   --help         Show this message and exit.
```

### Example
Use
-  mac/linux

```bash
python -m jycm --show \
--left="{\"normal-string\":\"aaaaa\",\"ignore_me-string\":\"aaaaa\",\"normal-list-1\":[{\"val\":1},{\"val\":2},{\"val\":3},{\"val\":4},{\"val\":5}],\"set_in_set\":[{\"id\":1,\"label\":\"label:1\",\"set\":[1,2,3,4,5]},{\"id\":2,\"label\":\"label:2\",\"set\":[4,5,6,7,8]}]}" \
--right="{\"normal-string\":\"bbbbb\",\"ignore_me-string\":\"bbbbb\",\"normal-list-1\":[{\"val\":1},{\"val\":9},{\"val\":3},{\"val\":8},{\"what\":5}],\"set_in_set\":[{\"id\":2,\"label\":\"label:2\",\"set\":[6,5,4,7]},{\"id\":1,\"label\":\"label:1\",\"set\":[3,2,1,4,8,9]}]}" \
--rules="[{\"operation\":\"ignore\",\"value\":\"^ignore_me.*\"},{\"value\":\"^set_in_set$\",\"operation\":\"operator:list:ignoreOrder\"},{\"value\":\"set_in_set->\\\\[\\\\d+\\\\]->set\",\"operation\":\"operator:list:ignoreOrder\"}]" \
--left_title="Left Title" \
--right_title="Right Title"
```

- or on windows:

```python -m jycm --show --left="{'normal-string': 'aaaaa', 'ignore_me-string': 'aaaaa', 'normal-list-1': [{'val': 1}, {'val': 2}, {'val': 3}, {'val': 4}, {'val': 5}], 'set_in_set': [{'id': 1, 'label': 'label:1', 'set': [1, 2, 3, 4, 5]}, {'id': 2, 'label': 'label:2', 'set': [4, 5, 6, 7, 8]}]}" --right="{'normal-string': 'bbbbb', 'ignore_me-string': 'bbbbb', 'normal-list-1': [{'val': 1}, {'val': 9}, {'val': 3}, {'val': 8}, {'what': 5}], 'set_in_set': [{'id': 2, 'label': 'label:2', 'set': [6, 5, 4, 7]}, {'id': 1, 'label': 'label:1', 'set': [3, 2, 1, 4, 8, 9]}]}" --rules="[{'operation': 'ignore', 'value': '^ignore_me.*'}, {'value': '^set_in_set$', 'operation': 'operator:list:ignoreOrder'}, {'value': 'set_in_set->\\[\\d+\\]->set', 'operation': 'operator:list:ignoreOrder'}]"```

- when the json are too large you can pass file path
```bash
python -m jycm --show  --left_file /xxxx/your_left.json --right_file ~/xxxx/your_right.json
```

then you will see a popup like this:
![cli-popup](https://raw.githubusercontent.com/eggachecat/jycm/master/docs/source/images/examples/cli-popup.jpg)


## Interactive
You can play with cli using:
```bash
python -m jycm --interactive
```


# Show cases

Here's some examples showing you what you can do with JYCM.
Only the results without configuration are shown below. (in case you wonder why things are not consistence here)

## Notes
Kindly suggestion from [@TonisPiip](https://github.com/TonisPiip)

- Why you want `no_pairs=True` in `ycm.to_dict(no_pairs=True)`? 
  - `pairs` are for rendering purpose (you can see the usage here at [react-jycm-viewer](https://github.com/eggachecat/react-jycm-viewer/blob/master/src/hooks/useJYCM.tsx#L30)) 
  - usually `pairs` are pretty large json (especially for some *relocation* diff)
  - so if you just want to get the diff you don't need `pairs`

## Default behaviour
Diff two json objects are easy:

Basically you do this:

```python
from jycm.jycm import YouchamaJsonDiffer
left = {} # your json
right = {} # your json

ycm = YouchamaJsonDiffer(left, right)
diff_result = ycm.get_diff() 
"""
ycm.get_diff() 

are the same as

ycm.diff()
ycm.to_dict*(
"""
```



### Code

```python
from jycm.helper import make_ignore_order_func
from jycm.jycm import YouchamaJsonDiffer
from jycm.helper import dump_html_output, open_url
from jycm.jycm import YouchamaJsonDiffer

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

diff_result = ycm.get_diff() # new API

# legacy usage:
# ycm.diff()
# diff_result = ycm.to_dict()

# you can find generated html in the folder
output_dir = "/Users/xxx/jycm-example-1"
# you can directly view it by clicking the index.html file inside the folder
url = dump_html_output(left, right, diff_result, output_dir)

# if you want to open it from python
open_url(url)



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

```

## Generate and apply JSON Patch

JYCM can produce and apply standard [RFC 6902 JSON Patch](https://www.rfc-editor.org/rfc/rfc6902)
operations. The generated patch follows the same business rules as the diff: ignored paths,
order-insensitive arrays, and custom operators that consider a value equivalent are left untouched.

```python
from jycm import apply_json_patch
from jycm.jycm import YouchamaJsonDiffer
from jycm.operator import IgnoreOperator

before = {
    "order": {"status": "pending", "total": 100},
    "generated_at": "2024-01-01T00:00:00Z",
}
after = {
    "order": {"status": "paid", "total": 100},
    "generated_at": "2024-01-02T00:00:00Z",
}

differ = YouchamaJsonDiffer(
    before,
    after,
    custom_operators=[IgnoreOperator("^generated_at$")],
)

# `test` operations make stale writes fail instead of silently overwriting data.
patch = differ.to_json_patch(include_tests=True)
assert patch == [
    {"op": "test", "path": "/order/status", "value": "pending"},
    {"op": "replace", "path": "/order/status", "value": "paid"},
]

updated = apply_json_patch(before, patch)
# Or: updated = differ.apply_patch()
```

`apply_json_patch` supports all RFC 6902 operations: `add`, `remove`, `replace`,
`move`, `copy`, and `test`. It copies the input by default; pass `in_place=True`
only when mutation is intentional.
### Graph
![default_behaviour](https://raw.githubusercontent.com/eggachecat/jycm/master/docs/source/images/examples/default_behaviour.png)

## Ignore Order
### Code
```python
from jycm.helper import make_ignore_order_func
from jycm.jycm import YouchamaJsonDiffer

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

diff_result = ycm.get_diff() # new API

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
# legacy usage:
# ycm.diff()
# diff_result = ycm.to_dict()
assert ycm.diff_result(no_pairs=True) == expected
```
### Graph
![ignore_order](https://raw.githubusercontent.com/eggachecat/jycm/master/docs/source/images/examples/ignore_order.png)



## Diff set-in-set
### Code
```python
from jycm.helper import make_ignore_order_func
from jycm.jycm import YouchamaJsonDiffer

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

```

### Graph 
![set_in_set](https://raw.githubusercontent.com/eggachecat/jycm/master/docs/source/images/examples/set_in_set.png)


## Custom operator

### Define an operator
```python
import math
from jycm.operator import  BaseOperator

class L2DistanceOperator(BaseOperator):
    __operator_name__ = "operator:l2distance"
    __event__ = "operator:l2distance"

    def __init__(self, path_regex, distance_threshold):
        super().__init__(path_regex=path_regex)
        self.distance_threshold = distance_threshold

    def diff(self, level: 'TreeLevel', instance, drill: bool) -> Tuple[bool, float]:
        print("damn")
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
```
### And use it
```python

from jycm.jycm import YouchamaJsonDiffer

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
    L2DistanceOperator(f"distance.*", 3),
])

expected = {
    'operator:l2distance': [
        {'left': {'x': 1, 'y': 1}, 'right': {'x': 2, 'y': 2}, 'left_path': 'distance_ok',
         'right_path': 'distance_ok', 'distance': 1.4142135623730951, 'distance_threshold': 3, 'pass': True},
        {'left': {'x': 5, 'y': 5}, 'right': {'x': 7, 'y': 9}, 'left_path': 'distance_too_far',
         'right_path': 'distance_too_far', 'distance': 4.47213595499958, 'distance_threshold': 3, 'pass': False}
    ]
}
assert {**ycm.to_dict(), "pairs": []} == expected


```

# Philosophy
Since determining two things are equal or not is heavily depend on the context, 
it is not possible to build a json diff tool to meet all requirements.  

JYCM choose another way: making it easy to compare values.

JYCM allows users just need to focus on defining the differing logic or what a distance is between
two values and 
JYCM will take care all the other dirty works such as array-item-matching, 
ignoring-array-order, recursively comparing and calculating similarity.

By the way, JYCM uses algorithms below to match items in array:

|            | exactly matching | fuzzy matching |
|:----------:|:--------:|:--------:|
| **with order** |    LCS  | Edit distance |
| **without order** |   Brute force   |  Kuhn–Munkres  |

Speaking of flexibility, to make a new operator, you just to need to extend a class called **BaseOperator** with such function signature:

```

diff: (level: 'TreeLevel', instance, drill: bool) => [float, boolean]

```

where the first return is a float number between zero and one for describing how similar **level.left** and **level.right** are and the second 
return is used to indicate whether comparing process should stop here.     


# Contribute

## requirements
```bash
pip install -r requirements-dev.txt
```

## Releases

```bash
git checkout master && git pull
bumpversion {patch|minor|major}
git push && git push --tags
```

## run test with cov
```bash
make testcov 
```

## make docs
```bash
make docs
```


