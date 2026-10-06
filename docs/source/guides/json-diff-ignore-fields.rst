Compare JSON while ignoring selected fields
===========================================

Use an ``ignore`` rule to exclude volatile fields, such as a trace ID, without
hiding changes in business fields.

These examples target the current source branch. Install it from a checkout
with ``python -m pip install -e .``; verify installed package capabilities before
using the same APIs with a registry release.

Runnable example: json-diff-ignore-fields
-----------------------------------------

.. code-block:: python

    from jycm import BusinessDiffPolicy
    before = {"trace_id": "old", "status": "pending"}
    after = {"trace_id": "new", "status": "paid"}
    policy = BusinessDiffPolicy({"version": 1, "rules": [
        {"path": "^trace_id$", "operation": "ignore"}
    ]})
    assert policy.compare(before, after)["equal"] is False
    assert policy.build(before, after).to_json_patch() == [
        {"op": "replace", "path": "/status", "value": "paid"}
    ]

Behavior and limits: json-diff-ignore-fields
--------------------------------------------

Use narrowly scoped rules. Ignoring a parent can suppress meaningful child
changes. A semantic patch preserves ignored source values; applying it need
not produce a byte-for-byte copy of the target document.

Related resources: json-diff-ignore-fields
------------------------------------------

* :doc:`../ecosystem`
* `Online playground <https://eggachecat.github.io/jycm-json-diff-viewer/>`_
* `JavaScript implementation <https://github.com/eggachecat/jycm-js>`_
