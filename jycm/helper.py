import json
import os
import re
import shutil
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


HTML_TEMPLATE = """
<!doctype html>
<html lang="en">

<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Web site created using create-react-app" />
    <title>JYCM Viewer</title>
    <script>
        window.jycmLeftJsonStr = __JYCM_LEFT_JSON_STR__;
        window.jycmRightJsonStr = __JYCM_RIGHT_JSON_STR__;
        window.diffResult = __JYCM_DIFF_RESULT__;
        window.jycmLeftTitle = __JYCM_LEFT_TITLE_STR__;
        window.jycmRightTitle = __JYCM_RIGHT_TITLE_STR__;
    </script>
    <script defer="defer" src="__MAIN_SCRIPT_PATH__"></script>
</head>

<body><noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
</body>

</html>
""".strip()


def render_to_html(left, right, diff_result, main_script_path="./index.js", left_title='Left', right_title='Right'):
    return HTML_TEMPLATE.replace(
        "__MAIN_SCRIPT_PATH__", f"{main_script_path}"
    ).replace(
        "__JYCM_LEFT_JSON_STR__", f"JSON.stringify({json.dumps(left)});"
    ).replace(
        "__JYCM_RIGHT_JSON_STR__", f"JSON.stringify({json.dumps(right)});"
    ).replace(
        "__JYCM_LEFT_TITLE_STR__", f"\"{left_title}\""
    ).replace(
        "__JYCM_RIGHT_TITLE_STR__", f"\"{right_title}\""
    ).replace(
        "__JYCM_DIFF_RESULT__", f"{json.dumps(diff_result)};")


def dump_html_output(left, right, diff_result, output, left_title='Left', right_title='Right'):
    html = render_to_html(left, right, diff_result, left_title=left_title, right_title=right_title)

    shutil.copytree(os.path.join(os.path.dirname(os.path.realpath(__file__)), "jycm_viewer_assets/"), output)
    index_url = os.path.join(output, "index.html")
    with open(index_url, "w") as fp:
        fp.write(html)
    return index_url


def open_url(index_url):
    try:
        import webbrowser
        from sys import platform
        if platform == "linux" or platform == "linux2":
            webbrowser.open(f"file://{index_url}")
        elif platform == "darwin":
            webbrowser.open(f"file://{index_url}")
        elif platform == "win32":
            webbrowser.open(f"{index_url}")
    except Exception as e:
        print("You have to install webbrowser to open the html.\nRun pip install webbrowser")
