#!/usr/bin/env python3
"""UnityBench — Review track runner. Scores any model on recall (bugs) + specificity (clean).

  export OPENROUTER_API_KEY=sk-...
  python eval/run_review.py --model openai/gpt-5.5
  python eval/run_review.py --model qwen/qwen3-coder --context conventions.txt   # RAG-style

Add --context with a text file of your project's conventions/APIs to emulate
project-aware review (this is the lever that dominates the leaderboard).
"""
from __future__ import annotations
import argparse, json, os, re, sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYS = ("You are a Unity 6 C# code reviewer. Review the code for real bugs (null/lifecycle, "
       "exploits, logic errors, resource/coroutine leaks). Output each problem as a line starting "
       "'BUG:'. If the code is correct, reply exactly 'CLEAN'.")


def load(name):
    p = os.path.join(HERE, "data", "review", name)
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def verdict(text):
    t = (text or "").strip()
    if re.search(r"(?im)^\s*BUG\s*:", t) or re.search(r"(?im)\bBUG\s*:", t):
        return "BUG"
    return "CLEAN" if t.upper().startswith(("CLEAN", "SAFE")) else "OTHER"


def call(model, key, code, ctx):
    sysp = SYS + (("\n\nProject conventions to apply:\n" + ctx) if ctx else "")
    body = {"model": model, "messages": [{"role": "system", "content": sysp},
                                          {"role": "user", "content": "```csharp\n" + code.strip() + "\n```"}]}
    if re.search(r"(?i)(gpt-5|o[1-9]|gpt-oss)", model):
        body["max_completion_tokens"] = 4000
    else:
        body["temperature"] = 0; body["max_tokens"] = 700
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
                                 data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return (json.load(r)["choices"][0]["message"]["content"] or "").strip()
    except Exception as e:
        return f"(error: {str(e)[:60]})"


def run(model, key, items, code_key, ctx):
    out = [None] * len(items)
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(call, model, key, it["code"], ctx): i for i, it in enumerate(items)}
        for f in futs:
            out[futs[f]] = f.result()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--context", default=None, help="text file of project conventions (RAG-style)")
    a = ap.parse_args()
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        sys.exit("set OPENROUTER_API_KEY")
    ctx = open(a.context, encoding="utf-8").read() if a.context else ""
    bugs, clean = load("bugs.jsonl"), load("clean.jsonl")

    rb = run(a.model, key, bugs, "code", ctx)
    rc = run(a.model, key, clean, "code", ctx)
    rec = sum(verdict(x) == "BUG" for x in rb)
    quiet = sum(verdict(x) == "CLEAN" for x in rc)
    R, S = 100 * rec / len(bugs), 100 * quiet / len(clean)
    bal = 2 * R * S / (R + S) if R + S else 0
    print(f"\nModel: {a.model}" + ("  (+project context)" if ctx else ""))
    print(f"  Recall (bugs flagged):       {rec}/{len(bugs)} = {R:.0f}%")
    print(f"  Quiet  (clean left alone):   {quiet}/{len(clean)} = {S:.0f}%")
    print(f"  Balance (harmonic mean):     {bal:.0f}")
    print("\n  Tip: high recall alone can hide false positives — inspect the flags, don't trust the binary.")


if __name__ == "__main__":
    main()
