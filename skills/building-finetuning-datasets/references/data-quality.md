# Dataset Quality and Format Reference

Contents: [Building the eval set](#build-the-eval-set-first) · [Sizing](#how-much-data) ·
[Dedup](#deduplication) · [Decontamination](#decontamination) · [Balance](#balance-and-coverage) ·
[Format](#format-and-templating) · [Splits](#splits-and-leakage) · [Dataset card](#dataset-card)

## Build the eval set first

The eval set is not a downstream artifact of the dataset — it is the specification the dataset is built
against. Writing it first forces you to state what "better" means before you have a stake in the answer,
and it is the only defense against a pipeline that optimizes toward whatever the generator happens to
produce.

Hold out **real** examples, never synthetic ones, and reserve them before any generation runs. 50
examples is a floor for detecting a meaningful difference; 100+ is better. For style and format tasks
where there is no single correct output, the eval set is a rubric plus reference outputs, not an exact-match
key — score with an LLM judge validated against your own scoring of a subset.

Your eval suite needs three parts, and skipping the second and third is how models silently regress:

1. **Task set** — held-out real examples of the thing you are teaching.
2. **Retention set** — general-capability probes the model could already do. Reuse a standard benchmark
   subset (MMLU, ARC, HellaSwag) or, better, prompts drawn from your own production traffic.
3. **Behavior set** — refusals, safety, tone, and any invariant the base model had that you need kept.

Measure all three on the *base* model before training. A fine-tune with no base-model measurement has no
denominator, and "it looks good" is not a result. For behavior-set items like refusals, measure a *rate*,
not a single shot: refusal behavior is stochastic in the temperature/seed region (Larsen et al., 2025;
APST, 2026 — models with comparable single-shot scores have substantially different failure rates under
repeated sampling), so sample 3–5 completions per boundary prompt and report "2/3 refused" rather than
pass/fail.

## How much data

Volume is the wrong first question; the answer depends on what you are teaching.

| Goal | Typical range | Notes |
|---|---|---|
| Format / structure conversion | 100–1,000 | Highly regular tasks saturate early |
| Style, tone, voice | 500–2,000 | Needs diversity of content, not volume |
| Classification / extraction | 50–500 per class | Balance matters more than total |
| General instruction following | 1,000–10,000 | LIMA reached competitive results at 1,000 curated |
| Reasoning behavior distillation | 800–10,000 traces | s1 used 1k, LIMO 817 — verification matters more than count |
| Broad domain capability | 10,000+ | At this point consider whether continued pretraining fits better |

Gains flatten fast. Applied studies commonly see steady improvement to a few hundred examples and
little beyond it. When a run underperforms, the reflex to double the data is usually wrong — check
diversity, label quality, and LR first.

## Deduplication

Run all three levels; each catches what the others miss.

1. **Exact** — hash the normalized text. Catches pipeline bugs that emit the same example repeatedly.
2. **Near-duplicate** — MinHash/LSH over character or word n-grams, Jaccard threshold ~0.7–0.8.
   Catches templated restatements.
3. **Semantic** — embed and drop examples whose nearest-neighbor cosine distance falls below a
   threshold. This is the only level that catches "same question, different words," which is what
   synthetic pipelines overproduce.

Deduplicate on the *instruction*, not the full example. Two different valid answers to one question is
useful signal; two phrasings of one question with one answer is redundancy that biases the model.

## Decontamination

Check the training set against every eval set you intend to report, including public benchmarks if you
will cite them. N-gram overlap (e.g. any shared 13-gram) is the cheap standard check; embedding
similarity catches paraphrase; LLM-based checking outperforms both but costs more. Run at least the
first two.

Contamination via the generator is the subtle case: if you generated data with a model that memorized a
benchmark, benchmark items can appear in your training set without ever being copied from it.

## Balance and coverage

- **Length.** Check the token-length distribution of outputs. If training answers are uniformly long,
  the model learns "always be long" — a real and frequently-shipped regression.
- **Class/topic.** Count examples per taxonomy cell. Empty cells are capability gaps; overweight cells
  become the model's default.
- **Negatives and refusals.** A dataset made only of successful cases teaches the model to always
  succeed, including when it should decline, ask a question, or report that the input is malformed.
  Include those cases deliberately.
- **Difficulty.** A dataset of only easy examples produces a model that fails on hard ones; a dataset of
  only hard ones trains poorly.
- **Share needed to override a base prior.** When a behavior fights something the base model was
  aligned *against* — a safety refusal you have authorization to override, a strong default it resists —
  it needs a minimum fraction of the training mix, well above what a merely-new behavior needs. A
  documented case found one such behavior fixed at ~33% of the mix but *regressing* at ~18%: too small a
  share and the base prior wins, and the fine-tune ends up worse than untouched. If a target behavior is
  not taking, raising its share of the mix is a lever before raising the total count.

## Format and templating

Use the messages schema and let the tokenizer apply the model's own chat template:

```jsonl
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

Three format bugs account for most "the fine-tune produced garbage" reports:

- **Template mismatch.** Training with a hand-written prompt string and serving with the model's chat
  template (or vice versa) means the model never sees the format it was trained on. Call
  `tokenizer.apply_chat_template` on both sides and diff the resulting token IDs on one example.
- **Missing or masked EOS.** If the sequence's end token is absent, or masked out of the labels, the
  model never learns to stop and will generate until it hits the length limit. Verify the EOS the chat
  template uses is the one the tokenizer emits — for Qwen-style templates it is `<|im_end|>`, not
  `</s>`.
- **Loss on prompt tokens.** Without masking (prompt labels set to `-100`), the model spends capacity
  learning to predict user turns. The flag differs by format — `assistant_only_loss` for `messages`
  data, `completion_only_loss` for prompt/completion data — and the wrong one is a silent no-op.
  Confirm by decoding one batch's unmasked label positions; they should be exactly the assistant text.

For multi-turn conversations, supervise every assistant turn, not just the last. For tool-use
trajectories, supervise assistant turns and tool-call emissions but not the tool results, which are
environment input the model does not generate.

## Splits and leakage

Split before any augmentation, deduplication across split boundaries, or generation. If one real
document produced ten synthetic examples, all ten belong in the same split — otherwise a paraphrase of a
training item lands in the test set and the score is fiction. Group by source document, then split.

80/10/10 train/validation/test is a reasonable default. Lock the test set; look at it once, at the end.
Use validation for the eval curve during training.

## Dataset card

Ship a `README.md` or `card.md` alongside the data recording: source of the seeds, generator model and
version, generation prompts, filters applied and their thresholds, dedup method, final counts per
taxonomy cell, split policy, and the license/terms under which the data may be used. Every one of these
is cheap to record now and impossible to reconstruct in three months.
