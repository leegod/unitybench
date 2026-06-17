# UnityBench — by **14Dimension Enterprise**

**A two-track evaluation for Unity 6 / C# coding models: domain *knowledge* + real-world *bug review*.**

Generalist code models are strong — but how well do they actually handle **Unity 6**, and can they find **real bugs in real game code** without crying wolf? There was no good public answer. This benchmark is one.

Built by [14Dimension Enterprise](https://github.com/leegod) from a shipping Unity game — bugs and fixes reconstructed from real version-control history.

---

## Tracks

**1. Knowledge** (`data/knowledge/`, ~146 items) — Unity 6 lifecycle/API Q&A + short "write this MonoBehaviour" compile tasks. Tests whether a model actually knows *current* Unity 6 (post-cutoff API, common pitfalls).

**2. Review** (`data/review/`, 24 buggy + 22 post-fix) — real Unity **gameplay** methods, each in two states: the **pre-fix (buggy)** version and the **post-fix** version, reconstructed from version-control history. We measure **recall** (does it flag the *real* bug?) — and the "post-fix" set turned out to be a **methodology finding**, not a clean specificity control (see the Review-track section below for why).

---

## Review track — a methodology finding, not a leaderboard

We ran seven models on 24 buggy + 22 "post-fix" gameplay methods, expecting to **rank** them by recall (catch the real bug) and specificity (stay quiet on already-fixed code). The raw numbers:

| Model | Recall (real bug flagged) | Flag rate on "post-fix" methods |
|---|---|---|
| GPT-5.5 | 100% | 91% |
| Opus 4.8 | 100% | 100% |
| Qwen3-Coder (open, no context) | 92% | 77% |
| Gemini 2.5 Pro | 67% | 82% |
| Qwen3-Coder **+ project context (RAG)** | 67% | 18% |
| Gemini 3.1 Pro | 62% | 55% |
| Claude Sonnet 4.5 | 46% | 64% |

A naive "balance" (harmonic mean) score would rank GPT-5.5 and Opus 4.8 **last** — they flag almost everything. **That ranking is wrong, and *why* it's wrong is the most useful result in this benchmark.**

We hand-read the flags the thorough frontier models (GPT-5.5, Opus 4.8) raised on the "post-fix" methods, then ran a **convention-aware per-flag judge** (given the project's own conventions, cross-checked by two independent judges) across all models. Their flags are **predominantly real, reasonable review issues** — unchecked return values, missing null guards, non-atomic reward grants that allow duplication, missing idempotency on click handlers, `Resources.Load` returning null, `OnDestroy` firing on scene-unload. These are not hallucinated false positives; they're what a senior reviewer flags. (GPT-5.5 *did* return `CLEAN` on the two methods that truly had no residual issue — it isn't flagging blindly.)

The ground truth is the problem: a "post-fix" method is just the version where **one specific bug** was fixed — not a method with **zero** issues. Real shipping game code always carries residual concerns, so "specificity" here **punishes the most thorough reviewer**, and a balance score built on it is upside-down.

**What this track actually shows:**
1. On long, real game methods, every capable model flags *something* — and for frontier models, that something is usually legitimate.
2. **Binary recall/specificity is the wrong instrument** for "is this a good reviewer." You need a per-flag verdict (real / nitpick / false-positive), not a clean/buggy label — see Methodology.
3. **Project context (RAG) doesn't make a model better at *finding* bugs** — it makes it flag *less* (77% → 18% here on the same base model) by teaching it what's normal for the codebase. Whether that's an improvement depends on whether the suppressed flags were real — usually a mix.

→ Treat this as a **case study in why bug-detection benchmarks are hard**, not a model ranking.

---

## Methodology — why binary metrics mislead here

A clean/buggy label on a control set is the wrong instrument for code review, for two reasons we measured directly:
- The "post-fix" methods are **not pristine** — they're the version where *one* bug was fixed, and strong models legitimately find *other* residual issues in them.
- A "find bugs" prompt makes **every** capable model surface *something*, so raw specificity collapses — and collapses **most** for the **most thorough** model.

The right instrument is a **per-flag verdict** — classify each flag as **real / nitpick / false-positive** — not a clean/buggy match. We did this: a convention-aware judge (given the project's own conventions) scored every flag, cross-checked by two independent judges. The thorough frontier models (GPT-5.5, Opus 4.8) score highest, and their "post-fix" flags are **predominantly real**. But the two judges disagree enough (46–88% agreement across models) that the **absolute precision numbers need human gold labels before they can be ranked** — which is exactly why we publish recall + flag-rate here, not a precision/balance leaderboard. *Measure the flags, not the binary.*

---

## Run it

```bash
export OPENROUTER_API_KEY=sk-...

# score any model on the review track (recall + how often it flags post-fix methods)
python eval/run_review.py --model openai/gpt-5.5

# inject your project's conventions (RAG-style) and watch the flag rate change
python eval/run_review.py --model qwen/qwen3-coder --context your_conventions.txt
```

`--context` takes a plain-text file of your project's conventions/APIs (e.g. "HP changes go
through `HealingService.Heal`; check the bool return of `AddItem`; …"). Giving the model what's
*normal* for your codebase makes it flag **less** — which, as the Review-track finding explains, is
not the same as making it *better*. Inspect the flags, don't trust the binary.

---

## Data notes / scope

- Review code is **real Unity gameplay logic** (rewards, combat, map/node systems), reconstructed pre-/post-fix from version control.  
- 46 review items is a focused, honest set — a *case study + methodology*, not a thousand-item leaderboard. Knowledge track is broader.
- `context_needed: true` marks bugs that require cross-file context (no snippet-only model can fully catch those).

## License & citation

- **Data** (`data/`): CC-BY-4.0 — free to use **with attribution to 14Dimension Enterprise**.
- **Code** (`eval/`): MIT.

```bibtex
@misc{unitybench2026,
  title  = {UnityBench: Unity 6 Knowledge \& Real-World Bug-Review Evaluation},
  author = {14Dimension Enterprise},
  year   = {2026},
  url    = {https://github.com/leegod/unitybench}
}
```

— Built and measured hands-on by **14Dimension Enterprise** while shipping a Unity game.
