import os

from click.testing import CliRunner

from jycm.__main__ import main


def get_abs_file_path(file_name):
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        file_name
    )


def test_main_1():
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            '--left',
            "{\"normal-string\":\"aaaaa\",\"ignore_me-string\":\"aaaaa\",\"normal-list-1\":[{\"val\":1},{\"val\":2},{\"val\":3},{\"val\":4},{\"val\":5}],\"set_in_set\":[{\"id\":1,\"label\":\"label:1\",\"set\":[1,2,3,4,5]},{\"id\":2,\"label\":\"label:2\",\"set\":[4,5,6,7,8]}]}",
            '--right',
            "{\"normal-string\":\"bbbbb\",\"ignore_me-string\":\"bbbbb\",\"normal-list-1\":[{\"val\":1},{\"val\":9},{\"val\":3},{\"val\":8},{\"what\":5}],\"set_in_set\":[{\"id\":2,\"label\":\"label:2\",\"set\":[6,5,4,7]},{\"id\":1,\"label\":\"label:1\",\"set\":[3,2,1,4,8,9]}]}",
            '--rules',
            "[{\"operation\":\"ignore\",\"value\":\"^ignore_me.*\"},{\"value\":\"^set_in_set$\",\"operation\":\"operator:list:ignoreOrder\"},{\"value\":\"set_in_set->\\\\[\\\\d+\\\\]->set\",\"operation\":\"operator:list:ignoreOrder\"}]"
        ]
    )
    assert result.output.strip() == "{'ignore': [{'left': 'aaaaa', 'right': 'bbbbb', 'left_path': 'ignore_me-string', 'right_path': 'ignore_me-string', 'path_regex': '^ignore_me.*', 'pass': True}], 'just4vis:pairs': [{'left': {'id': 1, 'label': 'label:1', 'set': [1, 2, 3, 4, 5]}, 'right': {'id': 1, 'label': 'label:1', 'set': [3, 2, 1, 4, 8, 9]}, 'left_path': 'set_in_set->[0]', 'right_path': 'set_in_set->[1]'}, {'left': 1, 'right': 1, 'left_path': 'set_in_set->[0]->id', 'right_path': 'set_in_set->[1]->id'}, {'left': 'label:1', 'right': 'label:1', 'left_path': 'set_in_set->[0]->label', 'right_path': 'set_in_set->[1]->label'}, {'left': [1, 2, 3, 4, 5], 'right': [3, 2, 1, 4, 8, 9], 'left_path': 'set_in_set->[0]->set', 'right_path': 'set_in_set->[1]->set'}, {'left': 1, 'right': 1, 'left_path': 'set_in_set->[0]->set->[0]', 'right_path': 'set_in_set->[1]->set->[2]'}, {'left': 2, 'right': 2, 'left_path': 'set_in_set->[0]->set->[1]', 'right_path': 'set_in_set->[1]->set->[1]'}, {'left': 3, 'right': 3, 'left_path': 'set_in_set->[0]->set->[2]', 'right_path': 'set_in_set->[1]->set->[0]'}, {'left': 4, 'right': 4, 'left_path': 'set_in_set->[0]->set->[3]', 'right_path': 'set_in_set->[1]->set->[3]'}, {'left': {'id': 2, 'label': 'label:2', 'set': [4, 5, 6, 7, 8]}, 'right': {'id': 2, 'label': 'label:2', 'set': [6, 5, 4, 7]}, 'left_path': 'set_in_set->[1]', 'right_path': 'set_in_set->[0]'}, {'left': 2, 'right': 2, 'left_path': 'set_in_set->[1]->id', 'right_path': 'set_in_set->[0]->id'}, {'left': 'label:2', 'right': 'label:2', 'left_path': 'set_in_set->[1]->label', 'right_path': 'set_in_set->[0]->label'}, {'left': [4, 5, 6, 7, 8], 'right': [6, 5, 4, 7], 'left_path': 'set_in_set->[1]->set', 'right_path': 'set_in_set->[0]->set'}, {'left': 4, 'right': 4, 'left_path': 'set_in_set->[1]->set->[0]', 'right_path': 'set_in_set->[0]->set->[2]'}, {'left': 5, 'right': 5, 'left_path': 'set_in_set->[1]->set->[1]', 'right_path': 'set_in_set->[0]->set->[1]'}, {'left': 6, 'right': 6, 'left_path': 'set_in_set->[1]->set->[2]', 'right_path': 'set_in_set->[0]->set->[0]'}, {'left': 7, 'right': 7, 'left_path': 'set_in_set->[1]->set->[3]', 'right_path': 'set_in_set->[0]->set->[3]'}], 'list:add': [{'left': '__NON_EXIST__', 'right': {'val': 9}, 'left_path': '', 'right_path': 'normal-list-1->[1]'}, {'left': '__NON_EXIST__', 'right': {'val': 8}, 'left_path': '', 'right_path': 'normal-list-1->[3]'}, {'left': '__NON_EXIST__', 'right': {'what': 5}, 'left_path': '', 'right_path': 'normal-list-1->[4]'}, {'left': '__NON_EXIST__', 'right': 8, 'left_path': '', 'right_path': 'set_in_set->[1]->set->[4]'}, {'left': '__NON_EXIST__', 'right': 9, 'left_path': '', 'right_path': 'set_in_set->[1]->set->[5]'}], 'list:remove': [{'left': {'val': 2}, 'right': '__NON_EXIST__', 'left_path': 'normal-list-1->[1]', 'right_path': ''}, {'left': {'val': 4}, 'right': '__NON_EXIST__', 'left_path': 'normal-list-1->[3]', 'right_path': ''}, {'left': {'val': 5}, 'right': '__NON_EXIST__', 'left_path': 'normal-list-1->[4]', 'right_path': ''}, {'left': 5, 'right': '__NON_EXIST__', 'left_path': 'set_in_set->[0]->set->[4]', 'right_path': ''}, {'left': 8, 'right': '__NON_EXIST__', 'left_path': 'set_in_set->[1]->set->[4]', 'right_path': ''}], 'value_changes': [{'left': 'aaaaa', 'right': 'bbbbb', 'left_path': 'normal-string', 'right_path': 'normal-string', 'old': 'aaaaa', 'new': 'bbbbb'}]}"


def test_main_2():
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            '--left_file',
            get_abs_file_path("./assets/left_file.json"),
            '--right_file',
            get_abs_file_path("./assets/right_file.json"),
            '--rules_file',
            get_abs_file_path("./assets/rules_file.json"),
        ]
    )
    assert result.output.strip() == "{'ignore': [{'left': 'aaaaa', 'right': 'bbbbb', 'left_path': 'ignore_me-string', 'right_path': 'ignore_me-string', 'path_regex': '^ignore_me.*', 'pass': True}], 'just4vis:pairs': [{'left': {'id': 1, 'label': 'label:1', 'set': [1, 2, 3, 4, 5]}, 'right': {'id': 1, 'label': 'label:1', 'set': [3, 2, 1, 4, 8, 9]}, 'left_path': 'set_in_set->[0]', 'right_path': 'set_in_set->[1]'}, {'left': 1, 'right': 1, 'left_path': 'set_in_set->[0]->id', 'right_path': 'set_in_set->[1]->id'}, {'left': 'label:1', 'right': 'label:1', 'left_path': 'set_in_set->[0]->label', 'right_path': 'set_in_set->[1]->label'}, {'left': [1, 2, 3, 4, 5], 'right': [3, 2, 1, 4, 8, 9], 'left_path': 'set_in_set->[0]->set', 'right_path': 'set_in_set->[1]->set'}, {'left': 3, 'right': 3, 'left_path': 'set_in_set->[0]->set->[2]', 'right_path': 'set_in_set->[1]->set->[0]'}, {'left': 4, 'right': 4, 'left_path': 'set_in_set->[0]->set->[3]', 'right_path': 'set_in_set->[1]->set->[3]'}, {'left': {'id': 2, 'label': 'label:2', 'set': [4, 5, 6, 7, 8]}, 'right': {'id': 2, 'label': 'label:2', 'set': [6, 5, 4, 7]}, 'left_path': 'set_in_set->[1]', 'right_path': 'set_in_set->[0]'}, {'left': 2, 'right': 2, 'left_path': 'set_in_set->[1]->id', 'right_path': 'set_in_set->[0]->id'}, {'left': 'label:2', 'right': 'label:2', 'left_path': 'set_in_set->[1]->label', 'right_path': 'set_in_set->[0]->label'}, {'left': [4, 5, 6, 7, 8], 'right': [6, 5, 4, 7], 'left_path': 'set_in_set->[1]->set', 'right_path': 'set_in_set->[0]->set'}, {'left': 6, 'right': 6, 'left_path': 'set_in_set->[1]->set->[2]', 'right_path': 'set_in_set->[0]->set->[0]'}, {'left': 7, 'right': 7, 'left_path': 'set_in_set->[1]->set->[3]', 'right_path': 'set_in_set->[0]->set->[3]'}], 'list:add': [{'left': '__NON_EXIST__', 'right': {'val': 9}, 'left_path': '', 'right_path': 'normal-list-1->[1]'}, {'left': '__NON_EXIST__', 'right': {'val': 8}, 'left_path': '', 'right_path': 'normal-list-1->[3]'}, {'left': '__NON_EXIST__', 'right': {'what': 5}, 'left_path': '', 'right_path': 'normal-list-1->[4]'}, {'left': '__NON_EXIST__', 'right': 2, 'left_path': '', 'right_path': 'set_in_set->[1]->set->[1]'}, {'left': '__NON_EXIST__', 'right': 1, 'left_path': '', 'right_path': 'set_in_set->[1]->set->[2]'}, {'left': '__NON_EXIST__', 'right': 8, 'left_path': '', 'right_path': 'set_in_set->[1]->set->[4]'}, {'left': '__NON_EXIST__', 'right': 9, 'left_path': '', 'right_path': 'set_in_set->[1]->set->[5]'}, {'left': '__NON_EXIST__', 'right': 5, 'left_path': '', 'right_path': 'set_in_set->[0]->set->[1]'}, {'left': '__NON_EXIST__', 'right': 4, 'left_path': '', 'right_path': 'set_in_set->[0]->set->[2]'}], 'list:remove': [{'left': {'val': 2}, 'right': '__NON_EXIST__', 'left_path': 'normal-list-1->[1]', 'right_path': ''}, {'left': {'val': 4}, 'right': '__NON_EXIST__', 'left_path': 'normal-list-1->[3]', 'right_path': ''}, {'left': {'val': 5}, 'right': '__NON_EXIST__', 'left_path': 'normal-list-1->[4]', 'right_path': ''}, {'left': 1, 'right': '__NON_EXIST__', 'left_path': 'set_in_set->[0]->set->[0]', 'right_path': ''}, {'left': 2, 'right': '__NON_EXIST__', 'left_path': 'set_in_set->[0]->set->[1]', 'right_path': ''}, {'left': 5, 'right': '__NON_EXIST__', 'left_path': 'set_in_set->[0]->set->[4]', 'right_path': ''}, {'left': 4, 'right': '__NON_EXIST__', 'left_path': 'set_in_set->[1]->set->[0]', 'right_path': ''}, {'left': 5, 'right': '__NON_EXIST__', 'left_path': 'set_in_set->[1]->set->[1]', 'right_path': ''}, {'left': 8, 'right': '__NON_EXIST__', 'left_path': 'set_in_set->[1]->set->[4]', 'right_path': ''}], 'value_changes': [{'left': 'aaaaa', 'right': 'bbbbb', 'left_path': 'normal-string', 'right_path': 'normal-string', 'old': 'aaaaa', 'new': 'bbbbb'}]}"
