Embed a semantic JSON diff viewer in React
==========================================

Compute a JYCM diff in Python or JavaScript, then pass the input documents and
structured result to ``JYCMViewer``. The React component renders the result;
it does not define the comparison rules.

These examples target the current source branch. Install it from a checkout
with ``python -m pip install -e .``; verify installed package capabilities before
using the same APIs with a registry release.

Behavior and limits: react-json-diff-viewer
-------------------------------------------

Install ``react-jycm-viewer``, ``react-monaco-editor``, and ``monaco-editor``.
Configure Monaco for your bundler and give the parent an explicit height.
Keep pair metadata when reordered records need synchronized navigation.

See the `complete React quick start
<https://github.com/eggachecat/react-jycm-viewer#quick-start>`_ for a TSX example
and the `playground source
<https://github.com/eggachecat/jycm-json-diff-viewer>`_ for an integrated app.
Confirm that your installed viewer exports ``JYCMViewer`` before copying
source-branch examples. The standalone ``JYCMPatchViewer`` renders RFC 6902
operations and is a separate component.

Related resources: react-json-diff-viewer
-----------------------------------------

* :doc:`../ecosystem`
* `Online playground <https://eggachecat.github.io/jycm-json-diff-viewer/>`_
* `JavaScript implementation <https://github.com/eggachecat/jycm-js>`_
