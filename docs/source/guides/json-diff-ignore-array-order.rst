Compare JSON while ignoring array order
=======================================

Use an ``unordered`` policy rule at selected paths when collection order has
no business meaning. Order elsewhere is still significant.

These examples target the current source branch. Install it from a checkout
with ``python -m pip install -e .``; verify installed package capabilities before
using the same APIs with a registry release.

Runnable example: json-diff-ignore-array-order
----------------------------------------------

.. code-block:: python

    from jycm import BusinessDiffPolicy
    before = {"tags": ["red", "blue"], "status": "pending"}
    after = {"tags": ["blue", "red"], "status": "paid"}
    policy = BusinessDiffPolicy({"version": 1, "rules": [
        {"path": "^tags$", "operation": "unordered"}
    ]})
    assert policy.compare(before, after)["equal"] is False
    assert policy.build(before, after).to_json_patch() == [
        {"op": "replace", "path": "/status", "value": "paid"}
    ]

Behavior and limits: json-diff-ignore-array-order
-------------------------------------------------

Select exact paths with anchored regular expressions. Do not ignore order in
rankings, event sequences, or other arrays where position is meaningful.
Unordered comparison does not mean duplicate elements can be discarded.

Related resources: json-diff-ignore-array-order
-----------------------------------------------

* :doc:`../ecosystem`
* `Online playground <https://eggachecat.github.io/jycm-json-diff-viewer/>`_
* `JavaScript implementation <https://github.com/eggachecat/jycm-js>`_
