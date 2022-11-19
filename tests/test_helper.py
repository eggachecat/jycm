from jycm.helper import render_to_html
from jycm.jycm import YouchamaJsonDiffer

expected_html_code = """<!doctype html>
<html lang="en">

<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Web site created using create-react-app" />
    <title>JYCM Viewer</title>
    <script>
        window.jycmLeftJsonStr = JSON.stringify({"a": 1, "b": 2, "d": "12345", "f": false, "e": [{"x": 1, "y": 1}, {"x": 2, "y": 2}, {"x": 3, "y": 3}, {"x": 4, "y": 4}]});;
        window.jycmRightJsonStr = JSON.stringify({"a": 1, "b": 3, "c": 4, "f": true, "e": [{"x": 0, "y": 1}, {"x": 2, "y": 2}, {"x": 3, "y": 3}, {"x": 5, "y": 5}]});;
        window.diffResult = {"dict:add": [{"left": "__NON_EXIST__", "right": 4, "left_path": "", "right_path": "c"}], "dict:remove": [{"left": "12345", "right": "__NON_EXIST__", "left_path": "d", "right_path": ""}], "just4vis:pairs": [{"left": "__NON_EXIST__", "right": 4, "left_path": "", "right_path": "c"}, {"left": "12345", "right": "__NON_EXIST__", "left_path": "d", "right_path": ""}], "list:add": [{"left": "__NON_EXIST__", "right": {"x": 5, "y": 5}, "left_path": "", "right_path": "e->[3]"}], "list:remove": [{"left": {"x": 4, "y": 4}, "right": "__NON_EXIST__", "left_path": "e->[3]", "right_path": ""}], "value_changes": [{"left": 2, "right": 3, "left_path": "b", "right_path": "b", "old": 2, "new": 3}, {"left": 1, "right": 0, "left_path": "e->[0]->x", "right_path": "e->[0]->x", "old": 1, "new": 0}, {"left": false, "right": true, "left_path": "f", "right_path": "f", "old": false, "new": true}]};;
        window.jycmLeftTitle = "Left";
        window.jycmRightTitle = "Right";
    </script>
    <script defer="defer" src="./index.js"></script>
</head>

<body><noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
</body>

</html>"""


def test_html_dump():
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

    assert expected_html_code == render_to_html(left, right, ycm.to_dict())
