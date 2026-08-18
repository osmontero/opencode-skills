#!/usr/bin/env python3
"""Taxonomy-driven synthetic SFT data generation against an OpenAI-compatible endpoint.

This is a REFERENCE pipeline, not a framework. Adapt the taxonomy, the prompts, and
`build_messages()` to your task, then run it. It exists so you write the generation LOOP
by hand once instead of emitting examples one at a time — generation is a script's job.

What it gives you that hand-emission does not:
  - Deterministic coverage: it generates into named taxonomy cells, N per cell.
  - Resume: re-running skips cells already at target (keyed by a stable content hash),
    so a crash or a rate-limit costs nothing.
  - Provenance: every row records the generator model, the cell, and a seed, written to
    the output alongside the example.

Endpoint: any OpenAI-compatible /v1/chat/completions (vLLM, together, openai, ...).
Configure with OPENAI_BASE_URL and OPENAI_API_KEY, or the flags below.

Usage:
  python generate.py --taxonomy taxonomy.json --out data/raw.jsonl --per-cell 8 \
      --model my-model --base-url http://localhost:8000/v1

The taxonomy file is a JSON list of cells; each cell is a dict of axis->value plus an
optional "n" override. See `example_taxonomy()` for the shape and edit it for your task.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# ---- adapt these three to your task -----------------------------------------

SYSTEM_PROMPT = "You are a careful assistant that produces training examples."

def build_messages(cell: dict, seed: int) -> list[dict]:
    """Return the chat messages sent to the generator for one example.

    `cell` is one taxonomy cell (e.g. {"topic": "billing", "difficulty": "hard"}).
    Vary the request by cell so the dataset covers the cross-product, and by `seed`
    so repeated draws on the same cell differ. Diversity comes from THIS function,
    not from temperature.
    """
    axes = ", ".join(f"{k}={v}" for k, v in cell.items() if k != "n")
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content":
            f"Generate one realistic instruction-and-response training example for a "
            f"model, matching these attributes: {axes}. Variation #{seed}. "
            f"Return strict JSON: {{\"instruction\": ..., \"response\": ...}}. "
            f"No preamble, no code fences."},
    ]

def parse_example(raw: str, cell: dict) -> dict | None:
    """Turn the generator's raw text into a messages-format row, or None to reject."""
    try:
        obj = json.loads(raw)
        instr, resp = obj["instruction"].strip(), obj["response"].strip()
    except (json.JSONDecodeError, KeyError, AttributeError):
        return None
    if not instr or not resp:
        return None
    return {
        "messages": [
            {"role": "user", "content": instr},
            {"role": "assistant", "content": resp},
        ],
    }

# ---- example taxonomy (replace with your own axes) --------------------------

def example_taxonomy() -> list[dict]:
    topics = ["billing", "login", "data-export", "permissions"]
    difficulties = ["easy", "hard"]
    return [{"topic": t, "difficulty": d} for t in topics for d in difficulties]

# ---- endpoint ---------------------------------------------------------------

def chat(base_url: str, api_key: str, model: str, messages: list[dict],
         temperature: float, max_tokens: int, retries: int = 4) -> str | None:
    """One OpenAI-compatible chat call, with backoff. Returns content or None."""
    body = json.dumps({
        "model": model, "messages": messages,
        "temperature": temperature, "max_tokens": max_tokens,
        # vLLM thinking models: disabling thinking here is much faster for data gen.
        "chat_template_kwargs": {"enable_thinking": False},
    }).encode()
    url = base_url.rstrip("/") + "/chat/completions"
    for attempt in range(retries):
        req = urllib.request.Request(url, data=body, method="POST", headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        })
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.load(r)
            return data["choices"][0]["message"]["content"]
        except (urllib.error.URLError, KeyError, TimeoutError) as exc:
            wait = 2 ** attempt
            print(f"  call failed ({exc}); retry in {wait}s", file=sys.stderr)
            time.sleep(wait)
    return None

# ---- resume-aware generation loop -------------------------------------------

def cell_key(cell: dict) -> str:
    return hashlib.sha1(json.dumps(cell, sort_keys=True).encode()).hexdigest()[:12]

def load_counts(out_path: Path) -> dict[str, int]:
    """Count already-written rows per cell so a re-run resumes instead of duplicating."""
    counts: dict[str, int] = {}
    if not out_path.exists():
        return counts
    for line in out_path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        k = row.get("metadata", {}).get("cell_key")
        if k:
            counts[k] = counts.get(k, 0) + 1
    return counts

def generate(args) -> None:
    taxonomy = (json.loads(Path(args.taxonomy).read_text())
                if args.taxonomy else example_taxonomy())
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = load_counts(out_path)
    total_target = sum(cell.get("n", args.per_cell) for cell in taxonomy)
    print(f"{len(taxonomy)} cells, target {total_target} rows, "
          f"{sum(done.values())} already present")

    with out_path.open("a") as fh:
        for cell in taxonomy:
            key = cell_key(cell)
            target = cell.get("n", args.per_cell)
            have = done.get(key, 0)
            for seed in range(have, target):
                raw = chat(args.base_url, args.api_key, args.model,
                           build_messages(cell, seed), args.temperature, args.max_tokens)
                if raw is None:
                    print(f"  [{key}] seed {seed}: no response, skipping", file=sys.stderr)
                    continue
                row = parse_example(raw, cell)
                if row is None:
                    print(f"  [{key}] seed {seed}: rejected (bad shape)", file=sys.stderr)
                    continue
                row["metadata"] = {"cell": {k: v for k, v in cell.items() if k != "n"},
                                   "cell_key": key, "seed": seed, "generator": args.model}
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()
            print(f"  [{key}] {cell}: {target} rows")
    print(f"done -> {out_path}")

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--taxonomy", help="JSON list of cells; omit to use the built-in example")
    p.add_argument("--out", default="data/raw.jsonl")
    p.add_argument("--per-cell", type=int, default=8, help="rows per cell unless the cell sets n")
    p.add_argument("--model", default=os.environ.get("GEN_MODEL", "gpt-4o-mini"))
    p.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL", "http://localhost:8000/v1"))
    p.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", "EMPTY"))
    p.add_argument("--temperature", type=float, default=0.9)
    p.add_argument("--max-tokens", type=int, default=1024)
    generate(p.parse_args())

if __name__ == "__main__":
    main()
