"""RFC 6902 JSON Patch generation and application for JYCM."""

from copy import deepcopy


class JsonPatchError(ValueError):
    """Raised when a JSON Patch operation is invalid or cannot be applied."""


class JsonPatchTestFailed(JsonPatchError):
    """Raised when an RFC 6902 ``test`` operation does not match."""


def _escape(token):
    return str(token).replace("~", "~0").replace("/", "~1")


def _tokens(path):
    if path == "":
        return []
    if not isinstance(path, str) or not path.startswith("/"):
        raise JsonPatchError("JSON Pointer paths must be empty or start with '/'")
    return [token.replace("~1", "/").replace("~0", "~") for token in path[1:].split("/")]


def _join(path, token):
    return path + "/" + _escape(token)


def _index(token, length, allow_end=False):
    if token == "-" and allow_end:
        return length
    try:
        index = int(token)
    except (TypeError, ValueError):
        raise JsonPatchError("Invalid array index: {!r}".format(token))
    upper = length if allow_end else length - 1
    if index < 0 or index > upper:
        raise JsonPatchError("Array index out of bounds: {}".format(index))
    return index


def _resolve(document, path):
    value = document
    for token in _tokens(path):
        if isinstance(value, list):
            value = value[_index(token, len(value))]
        elif isinstance(value, dict):
            if token not in value:
                raise JsonPatchError("Path does not exist: {}".format(path))
            value = value[token]
        else:
            raise JsonPatchError("Cannot traverse path: {}".format(path))
    return value


def _parent(document, path):
    tokens = _tokens(path)
    if not tokens:
        return None, None
    parent = document
    for token in tokens[:-1]:
        if isinstance(parent, list):
            parent = parent[_index(token, len(parent))]
        elif isinstance(parent, dict) and token in parent:
            parent = parent[token]
        else:
            raise JsonPatchError("Parent path does not exist: {}".format(path))
    return parent, tokens[-1]


def _add(document, path, value):
    if path == "":
        return value
    parent, token = _parent(document, path)
    if isinstance(parent, list):
        parent.insert(_index(token, len(parent), allow_end=True), value)
    elif isinstance(parent, dict):
        parent[token] = value
    else:
        raise JsonPatchError("Add target is not a container: {}".format(path))
    return document


def _remove(document, path):
    if path == "":
        raise JsonPatchError("Removing the document root is not supported")
    parent, token = _parent(document, path)
    if isinstance(parent, list):
        del parent[_index(token, len(parent))]
    elif isinstance(parent, dict) and token in parent:
        del parent[token]
    else:
        raise JsonPatchError("Remove path does not exist: {}".format(path))
    return document


def apply_json_patch(document, patch, in_place=False):
    """Apply RFC 6902 operations and return the patched document.

    All six standard operations are supported: ``add``, ``remove``,
    ``replace``, ``move``, ``copy`` and ``test``. Input is copied by default.
    """
    result = document if in_place else deepcopy(document)
    for operation in patch:
        if not isinstance(operation, dict) or "op" not in operation or "path" not in operation:
            raise JsonPatchError("Each patch operation requires 'op' and 'path'")
        op = operation["op"]
        path = operation["path"]

        if op == "test":
            if "value" not in operation or _resolve(result, path) != operation["value"]:
                raise JsonPatchTestFailed("Test failed at path: {}".format(path))
        elif op == "add":
            if "value" not in operation:
                raise JsonPatchError("Add operation requires 'value'")
            result = _add(result, path, deepcopy(operation["value"]))
        elif op == "remove":
            result = _remove(result, path)
        elif op == "replace":
            if "value" not in operation:
                raise JsonPatchError("Replace operation requires 'value'")
            if path != "":
                _resolve(result, path)
                result = _remove(result, path)
            result = _add(result, path, deepcopy(operation["value"]))
        elif op in ("move", "copy"):
            if "from" not in operation:
                raise JsonPatchError("{} operation requires 'from'".format(op.title()))
            value = deepcopy(_resolve(result, operation["from"]))
            if op == "move":
                result = _remove(result, operation["from"])
            result = _add(result, path, value)
        else:
            raise JsonPatchError("Unsupported patch operation: {}".format(op))
    return result


def make_json_patch(left, right, equivalent=None, include_tests=False):
    """Build a deterministic RFC 6902 patch.

    ``equivalent`` may implement business semantics. It receives left/right
    values and their token paths; returning true suppresses changes below that
    node. Lists are updated positionally for linear runtime and deterministic
    patches, while dictionaries are traversed by sorted key.
    """
    operations = []

    def add_test(path, value):
        if include_tests:
            operations.append({"op": "test", "path": path, "value": deepcopy(value)})

    def walk(left_value, right_value, left_path, right_path, pointer):
        if left_value == right_value:
            return
        if equivalent is not None and equivalent(left_value, right_value, left_path, right_path):
            return

        if isinstance(left_value, dict) and isinstance(right_value, dict):
            removed = sorted(set(left_value) - set(right_value), key=str)
            added = sorted(set(right_value) - set(left_value), key=str)
            common = sorted(set(left_value) & set(right_value), key=str)
            for key in removed:
                child_pointer = _join(pointer, key)
                add_test(child_pointer, left_value[key])
                operations.append({"op": "remove", "path": child_pointer})
            for key in common:
                walk(
                    left_value[key], right_value[key],
                    left_path + [key], right_path + [key], _join(pointer, key)
                )
            for key in added:
                operations.append({
                    "op": "add", "path": _join(pointer, key),
                    "value": deepcopy(right_value[key])
                })
            return

        if isinstance(left_value, list) and isinstance(right_value, list):
            shared = min(len(left_value), len(right_value))
            for index in range(shared):
                walk(
                    left_value[index], right_value[index],
                    left_path + [index], right_path + [index], _join(pointer, index)
                )
            for index in range(len(left_value) - 1, shared - 1, -1):
                child_pointer = _join(pointer, index)
                add_test(child_pointer, left_value[index])
                operations.append({"op": "remove", "path": child_pointer})
            for index in range(shared, len(right_value)):
                operations.append({
                    "op": "add", "path": _join(pointer, index),
                    "value": deepcopy(right_value[index])
                })
            return

        add_test(pointer, left_value)
        operations.append({"op": "replace", "path": pointer, "value": deepcopy(right_value)})

    walk(left, right, [], [], "")
    return operations
