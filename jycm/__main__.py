import json
import os
import click
import tempfile
import time

from jycm.helper import make_ignore_order_func, dump_html_output
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
    except:
        try:
            return json.loads(raw.replace("\'", "\""))
        except:
            raise ValueError(f"Not a valid json: `{raw}`")

def run(left, right, rules, output, open):
    left = load_json(left)
    right = load_json(right)
    rules = load_json(rules)

    same, result = diff_two_json_with_rules(left, right, rules)

    if output is not None:
        index_url = dump_html_output(left, right, result, output)
        if open:
            try:
                import webbrowser
                webbrowser.open(index_url)
            except:
                print("You have to install webbrowser to open the html.\nRun pip install webbrowser")

    print("No diff" if same else "Has diff!")
    print(result)

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
@click.option('--open', is_flag=True, show_default=True, help='Open the browser; This is valid only if you specify the output paramter.')
def main(interactive, left, right, rules, output, open):
    print(interactive, left, right, rules, output, open)
    if interactive:
        return interactive_main(output)

    if output is None:
        output = os.path.join(tempfile.mkdtemp(), f"jycm-{int(time.time())}")

    return run(left, right, rules, output, open)


if __name__ == '__main__':
    main()