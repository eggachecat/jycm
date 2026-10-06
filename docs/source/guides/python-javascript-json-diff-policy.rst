Share JSON comparison rules between Python and JavaScript
=========================================================

Store declarative comparison rules in a JSON policy document. Python uses
``BusinessDiffPolicy(policy).compare(before, after)``; JavaScript uses
``YouchamaJsonDiffer.fromPolicy(before, after, policy).explain()``.

These examples target the current source branch. Install it from a checkout
with ``python -m pip install -e .``; verify installed package capabilities before
using the same APIs with a registry release.

Behavior and limits: python-javascript-json-diff-policy
-------------------------------------------------------

Policy format version 1 supports ignore, unordered, match-by identity, numeric
tolerance, string normalization, expected change, expected existence, and
range rules. Version the policy alongside shared input/output fixtures.

Use the `cross-language example
<https://github.com/eggachecat/jycm-js/blob/main/docs/shared-policy.md>`_ with
real JSON files and runnable commands in both languages. Treat this as a
shared format, not a blanket guarantee of identical runtime behavior: regex,
Unicode, numeric precision, and unsupported input values can differ.
Use JSON-compatible values and check your fixtures in both runtimes.
Custom Python operators and JavaScript functions are not portable JSON policy
data.

Related resources: python-javascript-json-diff-policy
-----------------------------------------------------

* :doc:`../ecosystem`
* `Online playground <https://eggachecat.github.io/jycm-json-diff-viewer/>`_
* `JavaScript implementation <https://github.com/eggachecat/jycm-js>`_
