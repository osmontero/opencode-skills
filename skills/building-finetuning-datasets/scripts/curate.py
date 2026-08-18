#!/usr/bin/env python3
"""Curate a raw generated JSONL into a training set: dedup, decontaminate, report coverage.

Reference pipeline, standard-library only (no numpy/faiss) so it runs anywhere. The
near-duplicate and decontamination checks here are n-gram based — good enough to catch
what synthetic pipelines actually overproduce. For semantic dedup at scale, swap in
sentence embeddings + a vector index; the interfaces below are where that plugs in.

Steps, in order:
  1. Drop malformed rows (no messages / empty turns).
  2. Exact dedup on the normalized instruction.
  3. Near-duplicate dedup: MinHash-free Jaccard over instruction word-shingles.
  4. Decontaminate: drop any train row sharing a long n-gram with an eval file.
  5. Report coverage per taxonomy cell, and flag cells under target.

Usage:
  python curate.py --in data/raw.jsonl --out data/train.jsonl \
      --eval eval/task.jsonl --min-per-cell 5 --jaccard 0.8 --ngram 13
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

WORD = re.compile(r"\w+")


def norm(text: str) -> str:
    return " ".join(WORD.findall(text.lower()))


def instruction_of(row: dict) -> str:
    for m in row.get("messages", []):
        if m.get("role") == "user":
            return m.get("content", "")
    return ""


def shingles(text: str, k: int = 5) -> set[str]:
    toks = norm(text).split()
    if len(toks) < k:
        return {" ".join(toks)} if toks else set()
    return {" ".join(toks[i:i + k]) for i in range(len(toks) - k + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return inter / (len(a) + len(b) - inter)


def ngrams(text: str, n: int) -> set[str]:
    toks = norm(text).split()
    return {" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1)} if len(toks) >= n else set()


def valid(row: dict) -> bool:
    msgs = row.get("messages")
    if not msgs or len(msgs) < 2:
        return False
    if msgs[0].get("role") != "user" or msgs[-1].get("role") != "assistant":
        return False
    return all((m.get("content") or "").strip() or m.get("tool_calls") for m in msgs)


def curate(args) -> None:
    rows = [json.loads(l) for l in Path(args.in_path).read_text().splitlines() if l.strip()]
    start = len(rows)

    rows = [r for r in rows if valid(r)]
    dropped_malformed = start - len(rows)

    # exact dedup on the instruction
    seen: set[str] = set()
    exact: list[dict] = []
    for r in rows:
        key = norm(instruction_of(r))
        if key in seen:
            continue
        seen.add(key)
        exact.append(r)
    dropped_exact = len(rows) - len(exact)

    # near-duplicate dedup (greedy: keep first, drop later rows too similar to a kept one)
    kept: list[dict] = []
    kept_shingles: list[set[str]] = []
    for r in exact:
        sh = shingles(instruction_of(r))
        if any(jaccard(sh, ks) >= args.jaccard for ks in kept_shingles):
            continue
        kept.append(r)
        kept_shingles.append(sh)
    dropped_near = len(exact) - len(kept)

    # decontamination against eval files
    eval_ngrams: set[str] = set()
    for ev in args.eval or []:
        for line in Path(ev).read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                text = " ".join(m.get("content", "") for m in r.get("messages", []))
                eval_ngrams |= ngrams(text, args.ngram)
    clean: list[dict] = []
    for r in kept:
        text = " ".join(m.get("content", "") for m in r.get("messages", []))
        if ngrams(text, args.ngram) & eval_ngrams:
            continue
        clean.append(r)
    dropped_contam = len(kept) - len(clean)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out).open("w") as fh:
        for r in clean:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # coverage report per taxonomy cell
    cells = Counter(r.get("metadata", {}).get("cell_key", "?") for r in clean)
    labels = {r["metadata"]["cell_key"]: r["metadata"].get("cell", {})
              for r in clean if r.get("metadata", {}).get("cell_key")}

    print(f"in {start} | malformed -{dropped_malformed} | exact-dup -{dropped_exact} | "
          f"near-dup -{dropped_near} | contaminated -{dropped_contam} | out {len(clean)}")
    print(f"wrote {args.out}\ncoverage ({len(cells)} cells):")
    under = 0
    for key, count in sorted(cells.items(), key=lambda kv: kv[1]):
        flag = ""
        if count < args.min_per_cell:
            flag = f"  << under target ({args.min_per_cell})"
            under += 1
        print(f"  {count:4d}  {labels.get(key, key)}{flag}")
    if under:
        print(f"\n{under} cell(s) below target — regenerate INTO those cells "
              f"(add/raise their n in the taxonomy) rather than generating more at random.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--in", dest="in_path", default="data/raw.jsonl")
    p.add_argument("--out", default="data/train.jsonl")
    p.add_argument("--eval", action="append", help="eval JSONL to decontaminate against (repeatable)")
    p.add_argument("--jaccard", type=float, default=0.8, help="near-dup threshold on instruction shingles")
    p.add_argument("--ngram", type=int, default=13, help="shared n-gram length that counts as contamination")
    p.add_argument("--min-per-cell", type=int, default=5)
    curate(p.parse_args())


if __name__ == "__main__":
    main()
