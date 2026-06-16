# UnityBench — by **14Dimension Enterprise**

**A two-track evaluation for Unity 6 / C# coding models: domain *knowledge* + real-world *bug review*.**

Generalist code models are strong — but how well do they actually handle **Unity 6**, and can they find **real bugs in real game code** without crying wolf? There was no good public answer. This benchmark is one.

Built by [14Dimension Enterprise](https://github.com/leegod) from a shipping Unity TRPG — bugs and fixes reconstructed from real version-control history.

---

## Tracks

**1. Knowledge** (`data/knowledge/`, ~146 items) — Unity 6 lifecycle/API Q&A + short "write this MonoBehaviour" compile tasks. Tests whether a model actually knows *current* Unity 6 (post-cutoff API, common pitfalls).

**2. Review** (`data/review/`, 24 buggy + 22 clean) — real Unity **gameplay** methods, each in two states: the **pre-fix (buggy)** version and the **post-fix (clean)** version, reconstructed from version-control history. Tests two things at once:
- **Recall** — does it flag the *real* bug? (on `bugs.jsonl`)
- **Specificity** — does it stay quiet on already-fixed/clean code, instead of crying wolf? (on `clean.jsonl`)

---

## 🏆 Leaderboard — Review track

Bug detection on real Unity gameplay code (24 bugs / 22 clean). **Recall** = real bugs flagged. **Quiet** = clean methods left alone (no false alarm). **Balance** = harmonic mean.

| Model | Recall | Quiet (specificity) | Balance |
|---|---|---|---|
| **Qwen3-Coder + project-context (RAG)** | 67% | **82%** | **73** |
| Qwen3-Coder (open, no context) | 92% | 23% | 36 |
| Gemini 2.5 Pro | 67% | 18% | 29 |
| Claude Sonnet 4.5 | 46% | 18% | 26 |
| GPT-5.5 | 100% | 9% | 17 |

**What jumps out:**
1. **Every frontier model over-flags on real game code** — high recall, low specificity. On long, messy gameplay methods, "find bugs" makes them flag *something* almost every time.
2. **Project-context (RAG) is the single biggest lever** — injecting the project's conventions/APIs nearly **4×'d the balance** (36 → 73) of the same base model, by teaching it what's *normal* for this codebase.
3. **Binary recall/specificity is necessary but not sufficient** — see Methodology.

---

## Methodology — why binary metrics lie (and what to do)

A naive `precision/recall` on a "clean" control set is misleading here, for two reasons we measured directly:
- The "clean" (post-fix) methods are **not pristine** — strong models legitimately find *residual* issues in them.
- A "find bugs" prompt makes **every** capable model surface *something*, so raw specificity collapses for all of them.

So beyond the binary, we ran an **LLM-as-judge precision pass**: each flag is classified as **real / nitpick / false-positive**. This surfaces what F1 hides — e.g. a small fine-tuned reviewer can post a high *recall* while its flags are **almost entirely false positives**, whereas a frontier model's flags are mostly **real**. *Measure the flags, not just the binary.* The takeaway is baked into `run_review.py`'s output reminder; the leaderboard above reports the binary metrics.

---

## Run it

```bash
export OPENROUTER_API_KEY=sk-...

# score any model on the review track (recall + specificity + balance)
python eval/run_review.py --model openai/gpt-5.5

# inject your project's conventions (RAG-style) — the lever that tops the leaderboard
python eval/run_review.py --model qwen/qwen3-coder --context your_conventions.txt
```

`--context` takes a plain-text file of your project's conventions/APIs (e.g. "HP changes go
through `HealingService.Heal`; check the bool return of `AddItem`; …"). Reproduce the
leaderboard's top row by giving the model what's *normal* for your codebase.

---

## Data notes / scope

- Review code is **real Unity gameplay logic** (rewards, combat, map/node systems), reconstructed pre-/post-fix from version control. **Proprietary in-game AI and console-platform code are excluded.**
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
