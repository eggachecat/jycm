JYCM: JSON diff with business rules
================================================================================

JYCM compares nested JSON with explicit rules for what a change means.
Use it for API regression tests, configuration review, or reconciliation where
array order and generated fields can create noisy structural differences.

Choose an engine or viewer
--------------------------

* `Python engine and CLI <https://github.com/eggachecat/jycm>`_: compute diffs,
  explain policy outcomes, and generate JSON Patch.
* `JavaScript / TypeScript engine <https://github.com/eggachecat/jycm-js>`_:
  use the npm package named ``jycm`` in Node.js or a browser.
* `React viewer <https://github.com/eggachecat/react-jycm-viewer>`_: embed
  synchronized visual diffs or a standalone JSON Patch component.
* `Online playground <https://eggachecat.github.io/jycm-json-diff-viewer/>`_:
  try examples and inspect rules, events, and patches.

When to choose JYCM
-------------------

Choose JYCM when equality depends on selected paths, record identity, numeric
tolerances, or custom operators, and you also need explainable diff output.
For a simple text change review, a text diff may be sufficient. A semantic
patch intentionally preserves source values declared equivalent by a rule;
it is not necessarily an exact reconstruction of the target JSON.

Installation and compatibility
------------------------------

The guides describe the current source branch. Start with :doc:`installation`.
To run source-branch examples, check out this repository and run
``python -m pip install -e .``. Check installed package exports before using new
APIs with a registry release. Pin versions and validate shared fixtures before
using a policy across Python and JavaScript.

Algorithm reference
-------------------

`An adaptable JSON Diff Framework <https://arxiv.org/abs/2305.05865>`_ describes
the project's comparison approach. It is not a benchmark of current releases.
See :doc:`design` for the implementation's design documentation.

Task guides
-----------

.. toctree::
   :maxdepth: 1

   guides/json-diff-ignore-array-order
   guides/compare-json-arrays-by-id
   guides/json-diff-ignore-fields
   guides/json-comparison-numeric-tolerance
   guides/react-json-diff-viewer
   guides/python-javascript-json-diff-policy
