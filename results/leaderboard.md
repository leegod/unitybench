# UnityReviewBench — Leaderboard

Bug detection on real-world Unity gameplay code (24 bugs / 22 clean methods).
Recall = % of real bugs flagged. Quiet = % of clean methods left alone (no false alarm). Balance = harmonic mean.

| Model | Recall | Quiet (specificity) | Balance |
|---|---|---|---|
| Qwen3-Coder + project-context | 16/24 (67%) | 18/22 (82%) | **73** |
| Qwen3-Coder (open) | 22/24 (92%) | 5/22 (23%) | **36** |
| Gemini 2.5 Pro | 16/24 (67%) | 4/22 (18%) | **29** |
| Claude Sonnet 4.5 | 11/24 (46%) | 4/22 (18%) | **26** |
| GPT-5.5 | 24/24 (100%) | 2/22 (9%) | **17** |

> Note: binary recall/specificity is *necessary but not sufficient*. See README — a judge-based
> precision pass reveals that high recall often hides false-positive flags. Project-context (RAG)
> dramatically improves specificity on this set.