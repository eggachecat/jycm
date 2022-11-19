import json
import os
import tempfile
import time

import click

from jycm.helper import dump_html_output, make_ignore_order_func, open_url
from jycm.jycm import YouchamaJsonDiffer
from jycm.operator import get_operator


def diff_two_json_with_rules(left, right, rules, debug=False, fast_mode=False):
    operators = []
    ignore_order_path_regex_list = []
    for rule in rules:
        operation = rule["operation"]
        path_regex = rule["value"]
        parameter = rule.get("parameter", {})

        if parameter is None:
            parameter = {}

        if operation == "operator:list:ignoreOrder":
            ignore_order_path_regex_list.append(
                path_regex
            )
            continue

        operator_class = get_operator(operation)
        operators.append(operator_class(path_regex, **parameter))
    ycm = YouchamaJsonDiffer(
        left, right,
        ignore_order_func=make_ignore_order_func(ignore_order_path_regex_list),
        custom_operators=operators,
        debug=debug,
        fast_mode=fast_mode
    )
    same = ycm.diff()

    return same, ycm.to_dict()


def load_json(raw):
    try:
        return json.loads(raw)
    except Exception as e:
        try:
            return json.loads(raw.replace("\'", "\""))
        except Exception as e:
            raise ValueError(f"Not a valid json: `{raw}`")


def run(left, right, rules, output, show, left_title='Left', right_title='Right'):
    left = load_json(left)
    right = load_json(right)
    rules = load_json(rules)

    same, result = diff_two_json_with_rules(left, right, rules)

    if output is not None:
        index_url = dump_html_output(
            left, right, result, output, left_title=left_title, right_title=right_title)
        if show:
            open_url(index_url)

    print(result)
    return 'No-Diff' if same else "Has-diff"


def get_json_input(key):
    while True:
        val = input(f"{key} >>>")
        try:
            json.loads(val)
            return val
        except json.decoder.JSONDecodeError:
            print(f"Not a valid json: {val}")
            continue
        except Exception as e:
            raise (e)


def interactive_main(output):
    if output is None:
        output = tempfile.mkdtemp()

    while True:
        try:
            left = get_json_input("Left Json")
            right = get_json_input("Right Json")
            rules = get_json_input("Rules")
            run(left, right, rules, os.path.join(output, f"jycm-{int(time.time())}"), True)
        except Exception as e:
            print("Exception", e)
            pass


def load_file(file_path):
    with open(file_path) as fp:
        return fp.read()


def get_file_name(file_path):
    return os.path.basename(file_path)


@click.command()
@click.option('--interactive', is_flag=True, show_default=True, help='Enter interactive mode')
@click.option('--left', default='{}', help='Left Json')
@click.option('--right', default='{}', help='Right Json')
@click.option('--left_file', default=None,
              help='Left Json file path, if both left and this are given, jycm will use the file')
@click.option('--right_file', default=None,
              help='Right Json file path, if both right and this are given, jycm will use the file')
@click.option('--left_title', default=None, help='Left Title; By default will be the file name')
@click.option('--right_title', default=None, help='Right Title; By default will be the file name')
@click.option('--rules', default='[]', help='Rules')
@click.option('--rules_file', default=None,
              help='Rules Json file path, if both Json and this are given, jycm will use the file')
@click.option('--output', default=None, help='The folder where the results will be dumped.')
@click.option('--show', is_flag=True, show_default=True, help='Whether or not open the browser to visualize result.')
def main(interactive, left, right, left_file, right_file, left_title, right_title, rules, rules_file, output, show):
    if left_file is not None:
        left = load_file(left_file)
        left_title = get_file_name(left_file)

    if right_file is not None:
        right = load_file(right_file)
        right_title = get_file_name(right_file)

    if rules_file is not None:
        rules = load_file(rules_file)

    if interactive:
        return interactive_main(output)

    if output is None:
        output = os.path.join(tempfile.mkdtemp(), f"jycm-{int(time.time())}")

    if left_title is None:
        left_title = 'Left'

    if right_title is None:
        right_title = 'Right'

    return run(left, right, rules, output, show, left_title=left_title, right_title=right_title)


if __name__ == '__main__':
    main()
