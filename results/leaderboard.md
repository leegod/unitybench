# Review track — a methodology finding, not a leaderboard

We ran five models on 24 buggy + 22 "post-fix" Unity gameplay methods, expecting to rank them by
recall and specificity. We are **not** publishing a balance ranking — here's why.

| Model | Recall (real bug flagged) | Flag rate on "post-fix" methods |
|---|---|---|
| GPT-5.5 | 100% | 91% |
| Qwen3-Coder (open, no context) | 92% | 77% |
| Gemini 2.5 Pro | 67% | 82% |
| Claude Sonnet 4.5 | 46% | 82% |
| Qwen3-Coder + project context (RAG) | 67% | 18% |

A naive harmonic-mean "balance" would rank GPT-5.5 last. **That is wrong.** We hand-read every flag
GPT-5.5 raised on the "post-fix" methods: they are overwhelmingly **real, reasonable review issues**
(unchecked return values, missing null guards, non-atomic reward grants, missing idempotency,
`Resources.Load` null, `OnDestroy` on scene-unload) — not false positives. GPT-5.5 even returned
`CLEAN` on the two methods with no residual issue, so it isn't flagging blindly.

The ground truth is the problem: a "post-fix" method is just the version where *one* bug was fixed,
not a method with *zero* issues — real shipping game code always has residual concerns. So
"specificity" punishes the most thorough reviewer, and a balance score built on it is upside-down.

**Takeaway:** binary recall/specificity is the wrong instrument for code-review quality. The right
one is a per-flag verdict (real / nitpick / false-positive); see the repo README for the full
methodology. Treat this track as a case study in why bug-detection benchmarks are hard.
