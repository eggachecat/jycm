Compare JSON numbers with a tolerance
=====================================

A ``numeric_tolerance`` rule treats small numeric differences as equivalent.
Choose the tolerance from your domain, then test both accepted and rejected
values.

These examples target the current source branch. Install it from a checkout
with ``python -m pip install -e .``; verify installed package capabilities before
using the same APIs with a registry release.

Runnable example: json-comparison-numeric-tolerance
---------------------------------------------------

.. code-block:: python

    from jycm import BusinessDiffPolicy
    policy = BusinessDiffPolicy({"version": 1, "rules": [
        {"name": "rounding", "path": "^amount$", "operation": "numeric_tolerance",
         "options": {"absolute": 0.02}}
    ]})
    before = {"amount": 10}
    assert policy.compare(before, {"amount": 10.01})["equal"] is True
    assert policy.build(before, {"amount": 10.01}).to_json_patch() == []
    rejected = policy.compare(before, {"amount": 10.5})
    assert rejected["equal"] is False
    assert rejected["violations"][0]["rule"] == "rounding"

Behavior and limits: json-comparison-numeric-tolerance
------------------------------------------------------

An accepted value remains unchanged in the semantic patch. Floating-point
representation matters near thresholds; test boundaries with your actual data.
Use precise monetary representations where your contract requires them.
Relative tolerances are also supported; consult the operator implementation
and test near zero before adopting them.

Related resources: json-comparison-numeric-tolerance
----------------------------------------------------

* :doc:`../ecosystem`
* `Online playground <https://eggachecat.github.io/jycm-json-diff-viewer/>`_
* `JavaScript implementation <https://github.com/eggachecat/jycm-js>`_
