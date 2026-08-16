# Business Diff Policy v1

## Shape

```json
{
  "version": 1,
  "name": "order-contract",
  "rules": [
    {
      "name": "money-rounding",
      "path": "^items->\\[\\d+\\]->price$",
      "operation": "numeric_tolerance",
      "options": { "absolute": 0.01, "relative": 0.001 }
    }
  ]
}
```

Paths use JYCM path keys: object fields are separated by `->` and array indexes
look like `[0]`. Rules use regular expressions, so escape brackets in JSON.

## Operations

| Operation | Target | Options | Meaning |
| --- | --- | --- | --- |
| `ignore` | any path | none | Treat the entire matched subtree as equivalent. |
| `unordered` | list container | none | Match list members without positional ordering. |
| `match_by` | list item | `field` | Pair object items whose identity field is equal. |
| `numeric_tolerance` | number | `absolute`, `relative` | Pass when delta is within the larger configured threshold. |
| `string_normalize` | string | `trim`, `lowercase`, `collapse_whitespace` | Compare normalized strings. |
| `expect_change` | any matched value | none | Pass only when left and right differ. |
| `expect_exist` | any matched path | none | Pass only when both sides exist. |
| `range` | number | `start`, `end` | Require both values in `(start, end]`. |

Legacy operation names plus `value` and `parameter` fields remain accepted, but
new policies should use the canonical shape above.

## Common patterns

Unordered records matched by SKU:

```json
[
  { "name": "items-are-a-set", "path": "^items$", "operation": "unordered" },
  {
    "name": "match-item-sku",
    "path": "^items->\\[\\d+\\]$",
    "operation": "match_by",
    "options": { "field": "sku" }
  }
]
```

Volatile metadata plus normalized labels:

```json
[
  { "name": "generated-trace", "path": "^metadata->trace_id$", "operation": "ignore" },
  {
    "name": "canonical-label",
    "path": "^items->\\[\\d+\\]->label$",
    "operation": "string_normalize",
    "options": { "trim": true, "lowercase": true, "collapse_whitespace": true }
  }
]
```

## Review checklist

- Does each path match only the intended business field?
- Can duplicate identity values occur? If yes, define the expected behavior.
- Are missing values distinct from `null`, empty strings, zero, and false?
- Is tolerance symmetric and correct at zero and for negative values?
- Should ignored values also be excluded from generated Patch?
- Does a passing expectation mean the entire document may be considered equal?
- Are policy changes reviewed and versioned like application code?
