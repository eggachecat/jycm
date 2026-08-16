---
name: jycm-business-diff
description: Design, implement, validate, explain, and deploy business-aware JSON comparisons with JYCM in Python or JavaScript. Use when an agent must write semantic diff rules, ignore volatile fields, match array records by identity, compare unordered collections, add numeric tolerances or string normalization, generate RFC 6902 JSON Patch, integrate the React viewer, build regression fixtures, or deploy a business diff service.
---

# JYCM Business Diff

Build a versioned Business Diff Policy from concrete domain examples, prove it
against fixtures, and expose both human-review and machine-actionable outputs.

## Workflow

1. Inspect the repository language, package manager, existing JYCM version, and
   current diff fixtures. Do not replace an established integration blindly.
2. Collect at least one equivalent pair and one meaningful-difference pair.
   Infer rules only from explicit business meaning; flag uncertain semantics.
3. Author a version 1 policy. Read [references/policy-schema.md](references/policy-schema.md)
   for operation definitions, path patterns, and design constraints.
4. Validate and normalize the policy:

   ```bash
   python scripts/jycm_workflow.py validate policy.json
   ```

5. Compare representative documents and generate an executable patch:

   ```bash
   python scripts/jycm_workflow.py compare before.json after.json policy.json \
     --explain-out explanation.json --patch-out change.patch.json --include-tests
   ```

6. Review `summary`, named `violations`, `affected_paths`, and every patch
   operation. Add regression tests for pass, fail, missing-field, reordered-list,
   wrong-type, and tolerance-boundary cases.
7. Integrate the appropriate API and UI. Keep policy files independent of
   runtime code so Python and JavaScript services can share them.
8. Read [references/deployment.md](references/deployment.md) when adding CI,
   HTTP services, containers, viewer deployment, or agent installation.

## Policy design rules

- Apply `unordered` to the list container and `match_by` to its item path.
- Treat identity matching as pairing only. Child rules determine equality.
- Never apply numeric tolerance to IDs, counts requiring exactness, permission
  levels, or security decisions without an explicit domain requirement.
- Name every production rule with business language, not implementation jargon.
- Prefer narrow anchored path regexes. Test that a rule does not match siblings.
- Keep absolute and relative tolerance intentional and cover exact boundaries.
- Use `ignore` only for fields proven irrelevant. Do not hide unknown changes.
- Preserve `explain()` results in CI or audit flows; do not reduce the result to
  a single boolean when violations must be reviewable.
- Generate Patch from the same configured differ. Never derive Patch from a
  separate raw structural diff.
- Remember that a semantic Patch may intentionally leave ignored or reordered
  values unchanged. Verify the patched result semantically, not by raw equality.

## Runtime patterns

Python:

```python
import json
from jycm import BusinessDiffPolicy

policy = BusinessDiffPolicy(json.load(open("policy.json")))
differ = policy.build(before, after)
explanation = differ.explain()
patch = differ.to_json_patch(include_tests=True)
```

JavaScript/TypeScript:

```ts
import { YouchamaJsonDiffer } from "jycm";
import policy from "./policy.json";

const differ = YouchamaJsonDiffer.fromPolicy(before, after, policy);
const explanation = differ.explain();
const patch = differ.toJsonPatch(true);
```

React:

```tsx
<JYCMViewer left={before} right={after} diffResult={explanation.diff} showSummary />
<JYCMPatchViewer patch={patch} onNavigate={focusJsonPointer} />
```

## Completion checks

- Validate the policy successfully.
- Prove equivalent and violating fixtures behave as intended.
- Apply the generated patch without mutating the source document.
- Confirm the patched result is semantically equivalent to the target.
- Run repository lint, type, test, and production-build commands.
- Document policy ownership, versioning, rollback, and deployment behavior.
- Report any rules based on assumptions rather than approved domain semantics.

## Installation helper

From a checkout of this repository, install this skill without manually copying
files:

```bash
python skills/jycm-business-diff/scripts/install_skill.py --client codex
python skills/jycm-business-diff/scripts/install_skill.py --client claude
python skills/jycm-business-diff/scripts/install_skill.py --client agents --project .
```

Existing installations are backed up only when `--force` is supplied.
