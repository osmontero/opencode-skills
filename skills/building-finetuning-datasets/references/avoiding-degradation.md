# Avoiding Model Degradation

Contents: [The four modes](#the-four-degradation-modes) · [Replay](#replay-the-primary-defense) ·
[Unknown knowledge](#unknown-knowledge) · [Safety](#safety-regression) ·
[Overfitting and collapse](#overfitting-and-collapse) · [Gate thresholds](#gate-thresholds) ·
[Recovery](#recovering-a-degraded-run)

A fine-tune that improves its target metric and quietly ruins three other capabilities is a net loss
that looks like a win on the only chart anyone made. These are the four ways it happens and what each
one costs to prevent.

## The four degradation modes

| Mode | Symptom | Root cause |
|---|---|---|
| **Catastrophic forgetting** | General reasoning, other languages, unrelated tasks get worse | Weights moved far from pretrained values on a narrow distribution |
| **Induced hallucination** | Confident wrong facts, including outside the training domain | Trained on facts the model did not already know |
| **Safety regression** | Answers things the base model declined | Alignment behavior is fragile to any fine-tuning, benign included |
| **Mode collapse / overfitting** | One phrasing for everything, repetition loops, memorized outputs | Too many epochs, LR too high, dataset too small or too uniform |

They have different fixes. Diagnosing which one you have is worth more than applying all four remedies
at once.

## Replay: the primary defense

Mixing data from the original distribution into the fine-tuning set is the simplest and most reliable
mitigation for forgetting, and it is the step most pipelines omit entirely.

**Ratios.** There is no universal number, but the shape of the answer is consistent: a minority fraction
of general data buys most of the retention.

| Situation | General-data fraction |
|---|---|
| Narrow task, short run, LoRA | 5–10% |
| Broad behavior change, or full fine-tuning | 20–30% |
| Continual/sequential tuning across several tasks | 10–30%, including data from *prior* tasks |
| Highly specialized domain shift | 30–50% |

Published continual-learning work has maintained instruction-following with as little as 1% replay per
task, so start low and raise it if the retention gate fails. Replay costs training tokens; buying more
than you need is real waste.

**Sources**, in rough order of preference:

1. **The original instruction data**, if the model's post-training mix is public or reconstructible.
2. **A general open instruction set** — a sample of a broad, high-quality SFT corpus.
3. **Your own production traffic**, labeled with the base model's outputs. This targets exactly the
   distribution you care about not losing.
4. **Self-synthesized rehearsal** — prompt the *base* model to generate instruction/response pairs, and
   train on those. Requires no access to the original data, and can be steered at specific capabilities
   you need preserved (chat, instruction following, reasoning).

Option 4 is the practical default when you have no access to the original mix. Generate it from the base
model *before* training, not from the tuned model after.

**Other levers**, roughly in order of cost-effectiveness:

- **Fewer epochs and lower LR.** The cheapest forgetting mitigation is not moving the weights as far.
- **`lora_dropout` 0.05.** Cheap, isolated, and a *validated regression lever*, not only an
  anti-overfitting one. In a documented ~750-row case, adding 0.05 dropout (alongside a val split)
  narrowed a confirmed benchmark regression on every affected task without touching the target
  behaviors. Try it before the more invasive options below. See `lora-configuration.md`.
- **LoRA itself.** Low-rank adaptation forgets less than full fine-tuning, and less than weight decay or
  dropout as regularizers (Biderman et al.). The constraint that limits how much it learns is the same
  one that preserves the base model.
- **Lower rank.** Less capacity to overwrite. Trades task performance for retention.
- **Narrower target modules.** Targeting all linear layers maximizes learning but also maximizes what
  can be overwritten; dropping back toward attention-only (or a smaller module set) is a plausible
  retention lever when the task is narrow. This is in direct tension with the "target everything"
  default in `lora-configuration.md` — treat it as a knob to try under a confirmed regression, not a
  starting point, and change it in isolation so you can attribute the result.
- **KL regularization** toward the base model's outputs, where the trainer supports it.
- **Merging** the tuned model back toward base weights (TIES/DARE, or a simple weighted interpolation)
  recovers general capability at some cost to the task. A legitimate last-resort dial.

A note on ordering these against replay: replay is the best-supported defense in the literature, but a
real ~750-row run narrowed a regression substantially with dropout and a val split *before* trying
replay at all (rehearsal data was listed as the next thing to try, not the first). The lesson is not
that replay is wrong — it is that the cheap regularization knobs are worth spending first, because they
are one-line changes you can attribute, whereas building a good replay mix is real work.

## Unknown knowledge

The single highest-value data filter for factuality: **do not train on facts the model does not already
know.**

Fine-tuning examples that introduce new knowledge are learned significantly more slowly than examples
consistent with the model's existing knowledge, and as they are eventually learned they linearly
increase hallucination rates (Gekhman et al., EMNLP 2024, on closed-book QA). The rate is measured
across the whole evaluation rather than only the newly taught items, and it climbs with training time —
so the longer you train to make the new facts stick, the more factuality you pay for them.

**Detecting unknowns before training** — for each candidate example, sample the base model K times
(K≈8–16) at moderate temperature with a few-shot prompt and check how often it produces the correct fact:

| Base model gets it | Category | Do |
|---|---|---|
| Consistently | Known | Safe to train on |
| Sometimes | Maybe-known | Safe, and the most useful for teaching *reliable* recall |
| Never | Unknown | Do not train on it — route the fact to retrieval |

The maybe-known band is where fine-tuning actually earns its keep on factual tasks: the knowledge is
present but unreliable, and training makes it accessible.

When facts genuinely must be in the weights, augmentation helps: multiple paraphrases per fact, varied
question shapes, and varied context relevance. Un-augmented document→QA memorizes surface strings
without making the knowledge usable.

## Safety regression

Fine-tuning on *purely benign, utility-oriented* datasets measurably degrades safety alignment — this is
documented for Alpaca, Dolly, and LLaVA-Instruct across Llama-2 and GPT-3.5-Turbo (Qi et al., ICLR
2024). Adversarially, ten examples were enough to strip guardrails from a commercial model. You do not
need bad intent to lose alignment; you only need to fine-tune.

Practical response:

- Include a safety slice in the training mix — refusals and safe-completion examples in *your* format,
  so the model learns the behavior is compatible with the new style rather than superseded by it.
- Put refusal and boundary prompts in the eval suite's behavior subset and gate on them.
- Prefer LoRA at modest rank and few epochs; the less the weights move, the less alignment erodes.
- Re-run the behavior gate after every stage, including after merging adapters.

## Overfitting and collapse

| Signal | Reading |
|---|---|
| Train loss below ~0.2 | Memorization territory for typical SFT |
| Validation loss rising while train loss falls | Past the optimum — stop at the divergence point |
| Outputs verbatim from training data | Memorized; reduce epochs, raise dataset diversity |
| Same opening phrase for every input | Mode collapse from a uniform dataset |
| Non-terminating repetition loops | EOS not learned, or collapse from over-training |
| Output length distribution far from base | Length bias baked in from unbalanced training answers |

With a few hundred unique examples, a rank-16 adapter has enough parameters to start memorizing within
a few hundred optimizer steps — adapters capture generalizable patterns early and shift toward copying
exact token sequences after. This is why the eval curve matters more than the final loss, and why
1–3 epochs is the standard range rather than a formality.

Fixes in order of preference: more diverse data → fewer epochs → lower LR → `weight_decay` 0.01–0.1 →
`lora_dropout` 0.1 → scale `lora_alpha` by 0.5.

## Gate thresholds

Reasonable defaults; tighten them for anything user-facing.

| Gate | Threshold | Measured on |
|---|---|---|
| Task improvement | Beats base by a margin larger than run-to-run noise | Held-out real examples, ≥50 (100+ better) |
| Retention | Within 2–3 points of base | MMLU/ARC/HellaSwag subset, or production-traffic prompts |
| Factuality | Hallucination rate ≤ base | Closed-book QA on known-answer items |
| Safety | Refusal rate on boundary prompts ≥ base | Behavior subset |
| Format validity | ≥99% parse and terminate | Held-out task set |
| Output diversity | Distinct-n and length distribution near base | Sampled generations |

Establish run-to-run noise before trusting a small delta: train the same config twice with different
seeds and measure the spread. A 1-point "improvement" inside a 3-point noise band is not a result.

## Recovering a degraded run

1. **Identify the mode** from the table at the top. Do not apply all remedies at once — you will not
   learn which mattered, and several trade task performance away.
2. **Check config before regenerating data.** Learning rate and target modules explain more failures
   than data volume does, and re-running training is far cheaper than re-running generation.
3. **If retention failed**, raise replay fraction one band and cut epochs before touching anything else.
4. **If factuality failed**, run the unknown-knowledge filter over the training set and move the
   unknowns to retrieval. This is a data fix; no hyperparameter rescues it.
5. **If everything degraded at once**, suspect a format bug — chat template mismatch, missing EOS, or
   loss computed over prompt tokens — rather than a training dynamics problem. Decode one training batch
   and read it before re-running.
