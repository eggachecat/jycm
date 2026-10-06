# JYCM discovery and adoption experiment

This is the rollout checklist for the ecosystem documentation changes. It
records candidate search intents, not researched keyword volume or a promise
of ranking or AI recommendations.

## Publish in dependency order

1. Merge the Python and JavaScript documentation PRs together so cross-links
   resolve on the default branches. Build Read the Docs and verify the six
   guide URLs from the live documentation index.
2. Merge the React README changes. Registry descriptions change only after a
   package release; validate published exports before announcing new APIs.
3. Merge the playground changes, build and deploy through its existing Pages
   workflow, and confirm the Pages build is successful. Inspect returned HTML
   for the static guide section and canonical URL.
4. Verify the documentation and playground in Google Search Console using an
   account that controls the properties. Inspect key URLs and request indexing
   where appropriate. GitHub repository pages are outside that site's property.

## Initial search intents

| Intent | Source guide |
| --- | --- |
| json diff ignore array order | `docs/source/guides/json-diff-ignore-array-order.rst` |
| compare json arrays by id | `docs/source/guides/compare-json-arrays-by-id.rst` |
| json diff ignore fields | `docs/source/guides/json-diff-ignore-fields.rst` |
| json comparison numeric tolerance | `docs/source/guides/json-comparison-numeric-tolerance.rst` |
| react json diff viewer | `docs/source/guides/react-json-diff-viewer.rst` |
| python javascript json diff same rules | `docs/source/guides/python-javascript-json-diff-policy.rst` |

Use Search Console query data after publication to prioritize expansion.
Avoid generating many near-identical pages for unverified keyword variants.

## Four-week measurement

Record a baseline before deployment, then compare weekly. Leave unavailable
metrics blank rather than treating missing access as zero.

| Metric | Evidence | Interpretation |
| --- | --- | --- |
| Non-brand impressions and clicks | Search Console, page/query exports | Discovery for problems rather than the JYCM name |
| Guide and playground visits | Available aggregate site analytics | Interest; account for bots and internal traffic |
| Successful playground comparisons | Instrumentation if available | Actual use; currently requires separate implementation |
| Outbound repository clicks | Instrumentation if available | Intent to integrate; not proof of adoption |
| GitHub stars, forks, referring sites | Repository Insights and public counts | Supporting indicators, not the primary goal |
| Reported integrations and issues | Public issues/discussions or volunteered reports | Evidence of adoption and friction |
| AI mentions, citations, correct descriptions | Fixed prompt set and saved responses | Exploratory visibility, not causal attribution |

Test each of the six intents as a question without mentioning JYCM. Record the
AI provider/model, date, language, whether web search was enabled, full answer,
cited URLs, and feature-description errors. Repeat under the same conditions;
answers vary and a single mention is not a stable rank. Keep results separate
for search-grounded answers and answers generated without retrieval.

## Content distribution

Start with one useful tutorial on ignoring order and pairing by ID. Include
real input/output and a runnable fixture. Adapt it for an English developer
article and a Chinese technical post. Share only in communities where the
subject and self-promotion rules fit. Social posts, community submissions,
benchmark claims, and third-party outreach are not automatically published by
this documentation change.

A future comparison article must pin versions, publish the fixture and
commands, distinguish text/structural/semantic comparison, and report both
strengths and limitations. Do not claim speed or superiority without results.

## References

- [Google: AI features and your website](https://developers.google.com/search/docs/appearance/ai-features)
- [Google Search Essentials](https://developers.google.com/search/docs/essentials)
- [JYCM algorithm paper](https://arxiv.org/abs/2305.05865)
