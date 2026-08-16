# Integration and deployment

## Agent installation

Run `scripts/install_skill.py` from this skill checkout.

- Codex user scope: `--client codex` installs to `~/.codex/skills`.
- Claude user scope: `--client claude` installs to `~/.claude/skills`.
- Open Agent Skills project scope: `--client agents --project .` installs to
  `.agents/skills`.
- Claude project scope: `--client claude --project .` installs to
  `.claude/skills`.

Use `--force` to back up an existing installation and replace it. Commit
project-scoped skills so the whole team receives the same workflow.

## Service boundary

Accept three explicit inputs: `before`, `after`, and a versioned policy ID or
policy document. Return:

```json
{
  "equal": false,
  "summary": {},
  "violations": [],
  "diff": {},
  "patch": []
}
```

Validate policy documents at configuration-write time and again when loading a
new version. Reject unsupported versions and invalid regexes before comparing
production data.

## CI pattern

1. Store fixtures under source control.
2. Validate the policy.
3. Compare each expected-equivalent and expected-different fixture.
4. Fail on unexpected equality or named rule violations.
5. Save `explanation.json` and Patch as build artifacts when review is needed.
6. Apply Patch to a copy and re-run semantic comparison against the target.

Use `--fail-on-difference` with `scripts/jycm_workflow.py` only for fixtures that
must be semantically equal. For negative fixtures, assert the expected rule name
and affected path in the test framework.

## Deployment choices

- Python service: package `jycm`, cache compiled policies, and create a fresh
  differ for each request.
- Node/browser service: package `jycm`; do not execute user-provided code for
  custom rules. Prefer the declarative Policy operations.
- Review UI: deploy `react-jycm-viewer` with `JYCMViewer`, `showSummary`, and the
  standalone `JYCMPatchViewer`.
- Static demo: avoid embedding secrets or private payloads; comparisons run in
  the browser only when data is safe for the client.

## Operational safeguards

- Limit document size, list cardinality, regex length, and request duration.
- Treat policies as executable configuration requiring ownership and review.
- Log policy name/version and summary, not sensitive full documents by default.
- Use RFC 6902 `test` operations for optimistic concurrency before destructive
  writes.
- Roll back by selecting the previous immutable policy version, not by editing
  historical policy content in place.
