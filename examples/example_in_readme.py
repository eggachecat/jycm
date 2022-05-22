from jycm.helper import dump_html_output, open_url
from jycm.jycm import YouchamaJsonDiffer


def run_example_1():
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
    ycm.diff()  # you have to call this
    diff_result = ycm.to_dict()

    # you can find generated html in the folder
    output_dir = "/Users/xxx/jycm-example-1"
    # you can directly view it by clicking the index.html file inside the folder
    url = dump_html_output(left, right, diff_result, output_dir)

    # if you want to open it from python
    open_url(url)


if __name__ == '__main__':
    run_example_1()
