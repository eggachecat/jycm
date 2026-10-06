Compare JSON arrays of objects by ID
====================================

Combine ``unordered`` at the array path with ``match_by`` at its element paths
to pair records by identity and inspect changes within each matched record.

These examples target the current source branch. Install it from a checkout
with ``python -m pip install -e .``; verify installed package capabilities before
using the same APIs with a registry release.

Runnable example: compare-json-arrays-by-id
-------------------------------------------

.. code-block:: python

    from jycm import BusinessDiffPolicy

    before = {"users": [{"id": 1, "role": "viewer"}, {"id": 2, "role": "editor"}]}
    after = {"users": [{"id": 2, "role": "admin"}, {"id": 1, "role": "viewer"}]}
    policy = BusinessDiffPolicy({"version": 1, "rules": [
        {"path": "^users$", "operation": "unordered"},
        {"path": r"^users->\[\d+\]$", "operation": "match_by",
         "options": {"field": "id"}}
    ]})
    result = policy.compare(before, after)
    assert result["equal"] is False
    assert len(result["diff"]["value_changes"]) == 1
    assert result["diff"]["value_changes"][0]["new"] == "admin"

Behavior and limits: compare-json-arrays-by-id
----------------------------------------------

Use a stable, unique key. Matching by ID does not make differing child fields
equal. Validate missing or duplicate IDs in your application before comparing.
Policy paths use JYCM syntax (``users->[0]->role``), while JSON Patch uses
JSON Pointer syntax (``/users/0/role``).

Related resources: compare-json-arrays-by-id
--------------------------------------------

* :doc:`../ecosystem`
* `Online playground <https://eggachecat.github.io/jycm-json-diff-viewer/>`_
* `JavaScript implementation <https://github.com/eggachecat/jycm-js>`_
