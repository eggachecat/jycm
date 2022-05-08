import json
import os
import tempfile
import time

import click

from jycm.helper import dump_html_output, make_ignore_order_func
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


def run(left, right, rules, output, show):
    left = load_json(left)
    right = load_json(right)
    rules = load_json(rules)

    same, result = diff_two_json_with_rules(left, right, rules)

    if output is not None:
        index_url = dump_html_output(left, right, result, output)
        if show:
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

    print("No diff" if same else "Has diff!")


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
            raise(e)


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


@click.command()
@click.option('--interactive', is_flag=True, show_default=True, help='Enter interactive mode')
@click.option('--left', default='{}', help='Left Json')
@click.option('--right', default='{}', help='Right Json')
@click.option('--rules', default='[]', help='Rules')
@click.option('--output', default=None, help='The folder where the results will be dumped.')
@click.option('--show', is_flag=True, show_default=True, help='Whether or not open the browser to visualize result.')
def main(interactive, left, right, rules, output, show):
    print(interactive, left, right, rules, output, show)
    if interactive:
        return interactive_main(output)

    if output is None:
        output = os.path.join(tempfile.mkdtemp(), f"jycm-{int(time.time())}")

    return run(left, right, rules, output, show)


if __name__ == '__main__':
    main()
