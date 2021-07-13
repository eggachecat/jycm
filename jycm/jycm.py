from typing import Callable, Dict, List, Tuple, Union

from jycm.common import EVENT_PAIR, PLACE_HOLDER_NON_EXIST, EVENT_LIST_REMOVE, EVENT_LIST_ADD, EVENT_DICT_REMOVE, \
    EVENT_DICT_ADD
from jycm.helper import make_json_path_key
from jycm.km_matcher import KMMatcher
from jycm.operator import BaseOperator


class TreeLevel:
    """The base data structure for diffing.

    Args:
        left: left value
        right: right value
        left_path: left json path
        right_path: right json path
        up: the parent TreeLevel
        diff: a simple way to inject custom operators ; default None
    """

    def __init__(self, left, right, left_path: List, right_path: List, up: Union['TreeLevel', None],
                 diff: Union[Callable[['TreeLevel', bool], Tuple[bool, float]], None] = None):
        """Init method for TreeLevel

        """
        self.left = left
        self.right = right

        self.left_path: List = left_path
        self.right_path: List = right_path

        self.up: TreeLevel = up

        if diff is not None:
            self.diff = lambda _drill: diff(self, _drill)
        else:
            self.diff = None

    def get_type(self) -> type:
        """Get the type of this level

        Returns:
            Return the type of this level.
            If left and right are of different type, then a exception will be threw.
        """
        if type(self.left) != type(self.right):
            raise DifferentTypeException

        return type(self.left)

    def to_dict(self):
        """Convert TreeLevel to dict

        Returns:
            A dict contains all info about this level.
        """
        return {
            "left": self.left,
            "right": self.right,
            "left_path": self.left_path,
            "right_path": self.right_path
        }

    def get_path(self):
        """Get the path of this level

        Returns:
            The left path of this level (matching will be concerned on left mainly)

        """
        if self.left != PLACE_HOLDER_NON_EXIST:
            return make_json_path_key(self.left_path)
        return make_json_path_key(self.right_path)

    def get_key(self):
        """ Get the key of this level

        Returns:
            The unique key for this level
        """
        return f"{make_json_path_key(self.left_path)}/{make_json_path_key(self.right_path)}"

    def __repr__(self):
        return f"{self.to_dict()}"


class DifferentTypeException(Exception):
    """The exception that will be threw when left and right are of different types

    This maybe improved as a feature.

    """
    pass


class DiffLevelException(Exception):
    """The exception that will be threw from _diff function.

    """
    pass


class Record:
    """To record the info made from operators and differ.

    Args:
        event: a unique string to describe the info
        level: where the info and event are described for
        info:  the additional info attached to the event
    """

    def __init__(self, event: str, level: TreeLevel, info: Dict):
        self.event = event
        self.level = level
        self.info = info

    def to_dict(self):
        """Convert to dict

        Returns:
            A dict
        """
        return {
            **self.level.to_dict(),
            "left_path": make_json_path_key(self.level.left_path),
            "right_path": make_json_path_key(self.level.right_path),
            **self.info
        }


def gather_serial_pair(target_index, indices, list_, container):
    """Match parts between LCS index

    Args:
        target_index: LCS index that being collected before
        indices: all candidates index
        list_: list of values
        container: reference of collector

    Returns:

    """
    while len(indices) > 0:
        _index = indices.pop(0)

        if _index < target_index:
            container.append(list_[_index])
            continue

        if _index == target_index:
            break

        indices.insert(0, _index)
        break


class ListItemPair:
    """Pair of array items

    """

    def __init__(self, value: TreeLevel, left_index, right_index):
        self.level: TreeLevel = value
        self.left_index = left_index
        self.right_index = right_index

    def __repr__(self):
        return f"<left_index=[{self.left_index}],right_index=[{self.right_index}],level=[{self.level}]>"


class YouchamaJsonDiffer:
    """
        Args:
            left: a dict value.
            right: a dict value.
            custom_operators: List of operators extend from BaseOperator.
            ignore_order_func: the func that decides whether the current array should be ignored order or not.
                (level: TreeLevel, drill: boolean) => bool
            debug: set True then some debug info will be collected. default False.
            fast_mode: whether or not using LCS. default True
    """

    def __init__(self, left, right, custom_operators: Union[List[BaseOperator], None] = None,
                 ignore_order_func: Union[Callable[[TreeLevel, bool], bool], None] = None, debug=False,
                 fast_mode=False, use_cache=True):
        self.left = left
        self.right = right

        if custom_operators is None:
            custom_operators = []
        self.custom_operators: List[BaseOperator] = custom_operators

        self.records: Dict[str, List[Record]] = {
            EVENT_PAIR: []
        }

        self.cache = {}
        self.key_ctr = {}

        self.use_cache = use_cache
        self.fast_mode = fast_mode
        self.debug = debug

        self.lcs_table_cache = {}

        if ignore_order_func is None:
            def __ignore_order_func(__level: TreeLevel, __drill: bool):
                return False

            ignore_order_func = __ignore_order_func

        self.ignore_order_func: Callable[[TreeLevel, bool], bool] = ignore_order_func

    def report_pair(self, level: TreeLevel):
        """Report pair of json path

        In order to save space, only the level whose left and right path are different will be reported

        Args:
            level: TreeLevel

        """
        if make_json_path_key(level.left_path) != make_json_path_key(level.right_path):
            self.records[EVENT_PAIR].append(Record(
                event=EVENT_PAIR, level=level, info={}
            ))

    def report(self, event: str, level: TreeLevel, info: Union[Dict, None] = None):
        """Report any useful info

        Args:
            event: a unique string to describe the info
            level: where the info and event are described for
            info:  the additional info attached to the event
        """
        if event not in self.records:
            self.records[event] = []
        self.records[event].append(Record(
            event=event, level=level, info=info if info is not None else {}
        ))

    def to_dict(self, no_pairs=False) -> dict:
        """Convert this to a dict

        Normally to_dict is enough to collect all the info.

        Args:
            no_pairs: boolean to decide whether to report pairs of json path

        Returns:
            a dict
        """
        total_dict = {}
        events = list(self.records.keys())
        events.sort()
        for event in events:
            records = self.records[event]
            total_dict[event] = [r.to_dict() for r in records]

        if no_pairs and EVENT_PAIR in total_dict:
            del total_dict[EVENT_PAIR]

        return total_dict

    def _generate_lcs_pair_list(self, level: TreeLevel, left_size: int, right_size: int, dp_table):
        """Inner function to find the longest common subsequence of string `X[0…m-1]` and `Y[0…n-1]`

        """
        # return an empty string if the end of either sequence is reached
        if left_size == 0 or right_size == 0:
            return []

        # if the last character of `X` and `Y` matches
        # if left[left_size - 1] == right[right_size - 1]:
        if self.diff_level(TreeLevel(
            left=level.left[left_size - 1],
            right=level.right[right_size - 1],
            left_path=[*level.left_path, left_size - 1],
            right_path=[*level.right_path, right_size - 1],
            up=level
        ), drill=True) == 1:
            # append current character (`X[m-1]` or `Y[n-1]`) to LCS of
            # substring `X[0…m-2]` and `Y[0…n-2]`
            return self._generate_lcs_pair_list(level, left_size - 1, right_size - 1, dp_table) + [
                ListItemPair(value=TreeLevel(
                    left=level.left[left_size - 1],
                    right=level.right[right_size - 1],
                    left_path=[*level.left_path, left_size - 1],
                    right_path=[*level.right_path, right_size - 1],
                    up=level
                ), left_index=left_size - 1, right_index=right_size - 1)
            ]

        # otherwise, if the last character of `X` and `Y` are different

        # if a top cell of the current cell has more value than the left
        # cell, then drop the current character of string `X` and find LCS
        # of substring `X[0…m-2]`, `Y[0…n-1]`

        if dp_table[left_size - 1][right_size] > dp_table[left_size][right_size - 1]:
            return self._generate_lcs_pair_list(level, left_size - 1, right_size, dp_table)
        else:
            # if a left cell of the current cell has more value than the top
            # cell, then drop the current character of string `Y` and find LCS
            # of substring `X[0…m-1]`, `Y[0…n-2]`
            return self._generate_lcs_pair_list(level, left_size, right_size - 1, dp_table)

    def _build_up_lcs_table(self, level: TreeLevel, left_size, right_size, dp_table):
        """Inner function

        To fill the lookup table by finding the length of LCS of substring `X[0…m-1]` and `Y[0…n-1]`

        """
        # fill the lookup table in a bottom-up manner
        for i in range(1, left_size + 1):
            for j in range(1, right_size + 1):
                if self.diff_level(TreeLevel(
                    left=level.left[i - 1],
                    right=level.right[j - 1],
                    left_path=[*level.left_path, i - 1],
                    right_path=[*level.right_path, j - 1],
                    up=level
                ), drill=True) == 1:
                    dp_table[i][j] = dp_table[i - 1][j - 1] + 1
                else:
                    dp_table[i][j] = max(dp_table[i - 1][j], dp_table[i][j - 1])

    def generate_lcs_pair_list(self, level: TreeLevel) -> List[ListItemPair]:
        """Generate all ListItemPair

        Use LCS algorithm to match arrays with taking order into consideration

        Args:
            level: a tree level

        Returns:
            List of pairs
        """

        left_size, right_size = len(level.left), len(level.right)
        dp_table = [[0 for x in range(right_size + 1)] for y in range(left_size + 1)]

        # fill lookup table
        self._build_up_lcs_table(level, left_size, right_size, dp_table)

        # find the longest common sequence
        return self._generate_lcs_pair_list(level, left_size, right_size, dp_table)

    def _list_with_order_partial_matching(
        self, left_list: List[TreeLevel], right_list: List[TreeLevel]
    ) -> Tuple[List[TreeLevel], List[TreeLevel], List[TreeLevel]]:

        size_x = 1 + len(left_list)
        size_y = 1 + len(right_list)
        distance_table = [
            [0 for _ in range(size_y)]
            for _ in range(size_x)
        ]

        for x in reversed(range(size_x - 1)):
            for y in reversed(range(size_y - 1)):
                prev_x_score = distance_table[x + 1][y]
                prev_y_score = distance_table[x][y + 1]
                _level = TreeLevel(
                    left=left_list[x].left,
                    right=right_list[y].right,
                    left_path=left_list[x].left_path,
                    right_path=right_list[y].right_path,
                    up=None
                )
                score = self.diff_level(_level, True) + distance_table[x + 1][y + 1]

                distance_table[x][y] = max([prev_x_score, prev_y_score, score])
        removed, add, delta = [*left_list], [*right_list], []

        x, y = 0, 0

        while x + y < size_x + size_y - 2:
            curr = distance_table[x][y]
            prev_x_score = 0 if x + 1 >= size_x else distance_table[x + 1][y]
            prev_y_score = 0 if y + 1 >= size_y else distance_table[x][y + 1]

            if curr == prev_x_score and x + 1 < size_x:
                # by removing
                x += 1
                continue

            if curr == prev_y_score and y + 1 < size_y:
                # by adding
                y += 1
                continue

            removed.remove(left_list[x])
            add.remove(right_list[y])
            delta.append(TreeLevel(
                left=left_list[x].left,
                right=right_list[y].right,
                left_path=left_list[x].left_path,
                right_path=right_list[y].right_path,
                up=None
            ))

            # by updating at last
            x += 1
            y += 1

        return removed, add, delta

    def _compare_list_with_order(self, level: TreeLevel, drill=False) -> float:

        lcs_pair_list = self.generate_lcs_pair_list(level)

        left_indices, right_indices = list(range(len(level.left))), list(range(len(level.right)))

        left_data: List[TreeLevel] = [
            TreeLevel(left=level.left[i], left_path=[*level.left_path, i],
                      right=PLACE_HOLDER_NON_EXIST, right_path=[], up=None) for i in left_indices]

        right_data: List[TreeLevel] = [
            TreeLevel(left=PLACE_HOLDER_NON_EXIST, left_path=[],
                      right=level.right[i], right_path=[*level.right_path, i], up=None) for i in right_indices]

        serial_pair_list: List[Tuple[
            List[TreeLevel],
            List[TreeLevel]
        ]] = []

        total_score = 0
        for lcs_pair in lcs_pair_list:
            _serial_pair_left, _serial_pair_right = [], []

            # can be different without drill
            score = self.diff_level(lcs_pair.level, drill)
            total_score += score

            if not drill:
                self.report_pair(level)

            # fuzzy matching
            gather_serial_pair(lcs_pair.left_index, left_indices, left_data, _serial_pair_left)
            gather_serial_pair(lcs_pair.right_index, right_indices, right_data, _serial_pair_right)

            serial_pair_list.append((_serial_pair_left, _serial_pair_right))

        serial_pair_list.append((
            [TreeLevel(left=level.left[i], left_path=[*level.left_path, i],
                       right=PLACE_HOLDER_NON_EXIST, right_path=[], up=None) for i in left_indices],
            [TreeLevel(left=PLACE_HOLDER_NON_EXIST, left_path=[],
                       right=level.right[i], right_path=[*level.right_path, i], up=None) for i in right_indices],
        ))

        # fuzzy matching
        for left_serial, right_serial in serial_pair_list:
            removed, add, delta = self._list_with_order_partial_matching(left_serial, right_serial)

            if not drill:
                for tl in removed:
                    self.report(EVENT_LIST_REMOVE, tl)

                for tl in add:
                    self.report(EVENT_LIST_ADD, tl)

            for tl in delta:
                # 这样子取报告
                score = self.diff_level(tl, drill)
                total_score += score

                if not drill:
                    self.report_pair(tl)

        return total_score / max([len(level.left), len(level.right)])

    def _compare_list_with_order_fast(self, level: TreeLevel, drill=False) -> float:
        # index -> index的比较即可
        # 多出部分即超出
        len_left = len(level.left)
        len_right = len(level.right)

        min_len = min([len_left, len_right])
        max_len = max([len(level.left), len(level.right)])

        total_score = 0
        for i in range(min_len):
            _score = self.diff_level(
                TreeLevel(
                    left=level.left[i],
                    right=level.right[i],
                    left_path=[*level.left_path, i],
                    right_path=[*level.right_path, i],
                    up=level
                ),
                drill=drill
            )

            total_score += _score

        if not drill:
            # 这些就是新增的
            for i in range(min_len, len_left):
                self.report(EVENT_LIST_REMOVE, TreeLevel(
                    left=level.left[i],
                    right=PLACE_HOLDER_NON_EXIST,
                    left_path=[*level.left_path, i],
                    right_path=[],
                    up=level
                ))

            # 这些就是删除的
            for i in range(min_len, len_right):
                self.report(EVENT_LIST_ADD, TreeLevel(
                    left=PLACE_HOLDER_NON_EXIST,
                    right=level.right[i],
                    left_path=[],
                    right_path=[*level.right_path, i],
                    up=level
                ))

        return total_score / max_len

    def compare_list_with_order(self, level: TreeLevel, drill=False) -> float:
        """Compare two arrays with order

        Args:
            level: the tree level to be diffed
            drill: whether this diff is in drill mode.

        Returns:
            A score between 0~1 to describe how similar level.left and level.right are
        """

        max_len = max([len(level.left), len(level.right)])

        if self.debug:
            print(f"compare_list_with_order>>> {level}")

        if max_len == 0:
            return 1

        if self.fast_mode:
            score = self._compare_list_with_order_fast(level, drill)
        else:
            # than use similarity to match the others
            score = self._compare_list_with_order(level, drill)
        if self.debug:
            print(f"list score = {score} for {level}")

        return score

    def _list_without_order_partial_matching(
        self, left_list: List[TreeLevel], right_list: List[TreeLevel]
    ) -> Tuple[List[TreeLevel], List[TreeLevel], List[TreeLevel]]:
        """Use KM algorithm to match pairs

        First construct a table
                 r1  r2  r3  r4
            l1  [2., 3., 0., 3.]
            l2  [0., 4., 4., 0.]
            l3  [5., 6., 0., 0.]

        Then matching

        Args:
            left_list:
            right_list:

        Returns:

        """
        removed, add, delta = [*left_list], [*right_list], []

        size_left = len(left_list)
        size_right = len(right_list)

        if size_left == 0 or size_right == 0:
            return removed, add, delta

        distance_table = [
            [0.0 for _ in range(size_right)]
            for _ in range(size_left)
        ]

        for li in range(size_left):
            for ri in range(size_right):
                level = TreeLevel(
                    left=left_list[li].left,
                    right=right_list[ri].right,
                    left_path=[*left_list[li].left_path],
                    right_path=[*right_list[ri].right_path],
                    up=None
                )
                score = self.diff_level(level, drill=True)
                if self.debug:
                    print(f"distance_table[{ri}][{li}]", ri, li, score, level)

                distance_table[li][ri] = score

        if self.debug:
            print("distance_table>>>", distance_table)

        matcher = KMMatcher(distance_table)
        _, pairs = matcher.solve(verbose=False)

        if self.debug:
            print("pairs>>>", pairs)

        for li, ri in pairs:
            if distance_table[li][ri] != 0:
                removed.remove(left_list[li])
                add.remove(right_list[ri])
                delta.append(TreeLevel(
                    left=left_list[li].left,
                    right=right_list[ri].right,
                    left_path=left_list[li].left_path,
                    right_path=right_list[ri].right_path,
                    up=None
                ))

        return removed, add, delta

    def _compare_list_without_order_post(self, pair_list: List[ListItemPair], level: TreeLevel):
        matched_left_index = []
        matched_right_index = []
        for pair in pair_list:
            # still can be different under not drill
            self.diff_level(pair.level, False)
            self.report_pair(pair.level)
            matched_left_index.append(pair.left_index)
            matched_right_index.append(pair.right_index)

        partial_left = [
            TreeLevel(left=level.left[i], left_path=[*level.left_path, i],
                      right=PLACE_HOLDER_NON_EXIST, right_path=[], up=None)
            for i in range(len(level.left)) if i not in matched_left_index]
        partial_right = [
            TreeLevel(left=PLACE_HOLDER_NON_EXIST, left_path=[],
                      right=level.right[i], right_path=[*level.right_path, i], up=None)
            for i in range(len(level.right)) if i not in matched_right_index]

        removed, add, delta = self._list_without_order_partial_matching(partial_left, partial_right)
        for tl in removed:
            self.report(EVENT_LIST_REMOVE, tl)

        for tl in add:
            self.report(EVENT_LIST_ADD, tl)

        for tl in delta:
            # 这样子取报告
            self.diff_level(tl, False)
            self.report_pair(tl)

    def compare_list_without_order(self, level: TreeLevel, drill=False) -> float:

        pair_list = []
        matched_right = {}
        matched_left = {}
        for li in range(len(level.left)):
            for ri in range(len(level.right)):
                if ri in matched_right:
                    continue
                new_level = TreeLevel(
                    left=level.left[li],
                    right=level.right[ri],
                    left_path=[*level.left_path, li],
                    right_path=[*level.right_path, ri],
                    up=level
                )
                if self.diff_level(new_level, True) == 1:
                    pair_list.append(ListItemPair(value=new_level, left_index=li, right_index=ri))
                    matched_right[ri] = True
                    matched_left[li] = True
                    break

        if not drill:
            # only in the report phase
            self._compare_list_without_order_post(pair_list, level)

        if max([len(level.left), len(level.right)]) == 0:
            return 1
        return len(pair_list) / max([len(level.left), len(level.right)])

    def compare_list(self, level: TreeLevel, drill=False) -> float:
        if self.ignore_order_func(level, drill):
            return self.compare_list_without_order(level, drill)
        return self.compare_list_with_order(level, drill)

    def compare_dict(self, level: TreeLevel, drill=False) -> float:
        """Compare Dict

        Args:
            level: the tree level to be diffed
            drill: whether this diff is in drill mode.

        Returns:
            A score between 0~1 to describe how similar **level.left** and **level.right** are.
            The score will be average score for all scores for all keys.
        """
        score = 0
        all_keys = list(set(list(level.left.keys()) + list(level.right.keys())))
        all_keys.sort()

        if self.debug:
            print(f"[compare_dict>>>] {level}")

        ref = self

        def __dict_remove_diff(_level: 'TreeLevel', _drill: bool):
            if not _drill:
                ref.report(EVENT_DICT_REMOVE, TreeLevel(
                    left=_level.left,
                    right=PLACE_HOLDER_NON_EXIST,
                    left_path=[*_level.left_path],
                    right_path=[],
                    up=level
                ))
            return True, 0

        def __dict_add_diff(_level: 'TreeLevel', _drill: bool):
            if not _drill:
                ref.report(EVENT_DICT_ADD, TreeLevel(
                    left=PLACE_HOLDER_NON_EXIST,
                    right=_level.right,
                    left_path=[],
                    right_path=[*_level.right_path],
                    up=level
                ))
            return True, 0

        for k in all_keys:
            if k in level.right and k in level.left:
                _score = self.diff_level(TreeLevel(
                    left=level.left[k],
                    right=level.right[k],
                    left_path=[*level.left_path, k],
                    right_path=[*level.right_path, k],
                    up=level
                ), drill=drill)

                if self.debug:
                    print(f"[_score = {_score}] for [key={k}] {level}")

                score += _score

                if not drill:
                    self.report_pair(level)
                continue

            if k in level.left:
                _score = self.diff_level(TreeLevel(
                    left=level.left[k],
                    right=PLACE_HOLDER_NON_EXIST,
                    left_path=[*level.left_path, k],
                    right_path=[],
                    up=level,
                    diff=__dict_remove_diff
                ), drill=drill)
                score += _score
                continue

            if k in level.right:
                _score = self.diff_level(TreeLevel(
                    left=PLACE_HOLDER_NON_EXIST,
                    right=level.right[k],
                    left_path=[],
                    right_path=[*level.right_path, k],
                    up=level,
                    diff=__dict_add_diff
                ), drill=drill)
                score += _score
                continue

        if len(all_keys) == 0:
            return 1
        return score / len(all_keys)

    def compare_primitive(self, level: TreeLevel, drill=False) -> float:
        """Compare primitive values

        Args:
            level: the tree level to be diffed
            drill: whether this diff is in drill mode.

        Returns:
            A score between 0~1 to describe how similar **level.left** and **level.right** are.
        """
        if not drill:
            self.report_pair(level)

        if level.left != level.right:
            # 非演习
            if not drill:
                self.report("value_changes", level, {
                    "old": level.left,
                    "new": level.right
                })
            return 0
        return 1

    def use_custom_operators(self, level: TreeLevel, drill=False) -> Tuple[bool, float]:
        """Compare with custom operators

        Args:
            level: the tree level to be diffed
            drill: whether this diff is in drill mode.

        Returns:
            A boolean to determine whether diff should be early stopped.
            A score between 0~1 to describe how similar **level.left** and **level.right** are.

        """
        for operator in self.custom_operators:
            if operator.match(level):
                skip, score = operator.diff(level, self, drill)
                if skip:
                    return skip, score

        return False, -1

    def _diff_level(self, level: TreeLevel, drill: bool) -> float:
        """Base diff function

        Args:
            level: the tree level to be diffed
            drill: whether this diff is in drill mode.

        Returns:
            A score between 0~1 to describe how similar **level.left** and **level.right** are.

        """

        try:
            skip, score = self.use_custom_operators(level, drill)

            if skip:
                return score

            if level.diff is not None:
                skip, score = level.diff(drill)
                if skip:
                    return score

            try:
                level_type = level.get_type()
            except DifferentTypeException:
                return 0

            if level_type == list:
                return self.compare_list(level, drill)

            if level_type == dict:
                return self.compare_dict(level, drill)

            return self.compare_primitive(level, drill)
        except DiffLevelException as e:
            raise e
        except Exception as e:
            raise DiffLevelException(f"Error {e} [drill={drill}] when compare [{level}]")

    def diff_level(self, level: TreeLevel, drill: bool) -> float:
        """Diff level function\

        It is a wrapper of _diff_level with cache mechanism.

        Args:
            level: the tree level to be diffed
            drill: whether this diff is in drill mode.

        Returns:
            A score between 0~1 to describe how similar **level.left** and **level.right** are.

        """
        if self.use_cache:
            cache_key = f"[{level.get_key()}]@[{drill}]"

            if cache_key not in self.cache:
                score = self._diff_level(level, drill)
                if self.debug:
                    print(f"save score = {score} for cache_key = {cache_key} with level = {level}")
                self.cache[cache_key] = score
            else:
                if self.debug:
                    print(f"hit cache_key = {cache_key} for level {level}")

            score = self.cache[cache_key]
            if self.debug:
                self.key_ctr[cache_key] = 1 + self.key_ctr.get(cache_key, 0)
                print(f"score = {score} for level: {level}")
            return score

        score = self._diff_level(level, drill)
        if self.debug:
            print(f"score = {score} for level: {level}")
        return score

    def diff(self):
        """Entry function to be called to diff

        """
        root_level = TreeLevel(left=self.left, right=self.right, left_path=[], right_path=[], up=None)
        return self.diff_level(level=root_level, drill=False) == 1
