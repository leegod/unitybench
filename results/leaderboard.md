# Review track — a methodology finding, not a leaderboard

We ran seven models on 24 buggy + 22 "post-fix" Unity gameplay methods, expecting to rank them by
recall and specificity. We are **not** publishing a balance ranking — here's why.

| Model | Recall (real bug flagged) | Flag rate on "post-fix" methods |
|---|---|---|
| GPT-5.5 | 100% | 91% |
| Opus 4.8 | 100% | 100% |
| Qwen3-Coder (open, no context) | 92% | 77% |
| Gemini 2.5 Pro | 67% | 82% |
| Qwen3-Coder + project context (RAG) | 67% | 18% |
| Gemini 3.1 Pro | 62% | 55% |
| Claude Sonnet 4.5 | 46% | 64% |

A naive harmonic-mean "balance" would rank GPT-5.5 and Opus 4.8 last. **That is wrong.** We hand-read
their flags on the "post-fix" methods, then ran a convention-aware per-flag judge (cross-checked by
two independent judges) across all models: the thorough frontier models' flags are **predominantly
real review issues** (unchecked return values, missing null guards, non-atomic reward grants, missing
idempotency, `Resources.Load` null, `OnDestroy` on scene-unload), not false positives.

The ground truth is the problem: a "post-fix" method is just the version where *one* bug was fixed,
not a method with *zero* issues — real shipping game code always has residual concerns. So
"specificity" punishes the most thorough reviewer, and a balance score built on it is upside-down.

**Takeaway:** binary recall/specificity is the wrong instrument for code-review quality. The right one
is a per-flag verdict (real / nitpick / false-positive) — but two independent judges disagree enough
(46–88% agreement) that absolute precision needs human gold labels before it can be ranked, which is
why only recall + flag-rate are shown. Treat this track as a case study in why bug-detection
benchmarks are hard.
