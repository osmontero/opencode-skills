# Choosing a Fine-Tuning Technique

Contents: [Before tuning](#before-you-tune-anything) · [Stage selection](#which-training-stage) ·
[Preference methods](#preference-optimization-methods) · [RL methods](#reinforcement-learning-methods) ·
[Parameter budget](#which-parameter-budget) · [Ordering](#stage-ordering) · [Decision table](#decision-table)

Two independent choices are usually collapsed into one and shouldn't be:

1. **Which training stage** — continued pretraining, SFT, preference optimization, RL. This is decided
   by *what kind of signal you have*.
2. **Which parameter budget** — full fine-tuning, LoRA, QLoRA. This is decided by *how much the weights
   need to move* and what hardware you have.

You pick one from each. "Should I use LoRA or DPO?" is a malformed question.

## Before you tune anything

Fine-tuning is the expensive answer. Rule these out first, in order:

| Try first | When it is actually the right answer |
|---|---|
| **Prompt engineering** | The model can already do it and just needs to be told how. Nearly always worth one honest attempt. |
| **Few-shot exemplars** | The behavior is demonstrable in 3–10 examples and latency/context budget allows it. |
| **RAG** | The gap is *knowledge* — facts, documents, current data. This is the big one. |
| **Structured decoding / grammars** | The gap is output format validity. A grammar guarantees what training only encourages. |
| **A bigger or different base model** | The gap is raw capability. Tuning a too-small model to do something it fundamentally can't is a long road to a bad result. |

**The knowledge/behavior split is the highest-leverage distinction in this whole document.** Models
mostly acquire facts during pretraining; fine-tuning teaches them to *use* what they have. Gekhman et
al. showed fine-tuning examples that introduce genuinely new facts are learned much more slowly than
ones consistent with existing knowledge — and as they are finally learned, they linearly increase the
model's tendency to hallucinate. Teaching facts by fine-tuning does not just fail to work; it damages
factuality generally. Facts go in RAG. Fine-tuning gets format, tone, task procedure, tool use, and
domain reasoning style.

The legitimate exception is *making retrieved knowledge usable*: fine-tuning on document-grounded QA so
the model handles your domain's vocabulary, question shapes, and citation format — with the facts still
supplied at inference by retrieval.

## Which training stage

### Continued pretraining (CPT / domain-adaptive pretraining)

Raw unlabeled domain text, next-token objective, no instruction format.

**Use when** you need the model to absorb a genuinely unfamiliar domain — an unusual language, a
specialized notation, a proprietary codebase's idioms — and you have on the order of 10⁸+ tokens of it.

**Do not use** for a few hundred documents; you will damage the model without teaching it much. And note
LoRA is a poor fit here specifically: this is the regime where it most underperforms full fine-tuning,
because the weight changes required are genuinely high-rank.

Follow CPT with SFT. Raw CPT degrades instruction following, so a model that has only been continued-pretrained
is not ready to use.

### Supervised fine-tuning (SFT / instruction tuning)

Prompt→response pairs. The default, and the right answer for most requests.

**Use when** you can write down the correct output for a given input. Format conversion, house style,
classification, extraction, tool-call syntax, domain Q&A phrasing, reasoning-trace imitation.

**Signal required:** one good answer per prompt.

### Preference optimization (DPO and relatives)

Pairs of responses labeled better/worse.

**Use when** you cannot write the single correct output but you can reliably say which of two outputs is
better. Typical cases: tone and helpfulness calibration, reducing a specific failure mode (hedging,
over-refusal, verbosity), and squeezing out residual errors after SFT.

**Signal required:** comparisons. This is the reason to reach for it — if you have gold answers, SFT is
simpler and usually enough.

Preference data has failure modes SFT does not. Pairs where chosen and rejected are effectively
identical contribute noise and should be dropped. Rejected responses drawn from one source collapse
into one failure mode; sample them across genuinely different failure types — wrong tool, missing
constraint, poor grounding, unnecessary steps. And "human wrote it, so it's chosen" is invalid unless
verified; a high-temperature model sample is not automatically worse.

Preference runs use learning rates 1–2 orders of magnitude below SFT (`~5e-6`).

### Reinforcement learning (PPO, GRPO, RLVR)

A reward signal, computed per rollout.

**Use when** correctness is *verifiable programmatically* — unit tests pass, the math answer checks, the
JSON validates, the agent completed the task — and the space of good answers is too large to enumerate
as SFT targets. This is where reasoning capability is genuinely built rather than imitated.

**Cost:** substantially more compute, more moving parts, and far more ways to fail (reward hacking,
collapse) than SFT or DPO. Do not start here. Get SFT working, measure, and escalate only if the
verifiable-reward structure is real.

### Distillation

Not a separate stage — a way of *sourcing* SFT or preference data from a stronger teacher model. Covered
in `synthetic-generation.md`, including the licensing constraints, which are the binding issue more often
than the technical ones.

## Preference optimization methods

If you have concluded you need preference training:

| Method | Needs | Pick it when |
|---|---|---|
| **DPO** | Paired chosen/rejected + a frozen reference model | Default. Well-understood, widely supported. |
| **ORPO** | Paired data, *no* reference model, runs from the base model | You want to collapse SFT and preference into one stage and save memory. |
| **KTO** | Unpaired binary labels (good / bad) | Your feedback is thumbs-up/down on single responses — far easier to collect than pairs. |
| **SimPO** | Paired data, no reference model | Memory-constrained; length-normalized reward reduces verbosity drift. |
| **IPO** | Paired data | DPO is overfitting your preference set. |

Start with DPO unless your data shape says otherwise — KTO's unpaired signal in particular is often the
data you actually have.

## Which parameter budget

| Budget | Trainable | Choose when |
|---|---|---|
| **Full fine-tuning** | All weights | Continued pretraining; large datasets; you need high-rank change and have the hardware. Forgets the most. |
| **LoRA** | Low-rank adapters on chosen layers | Default for SFT and preference tuning. Forgets less than full FT and less than weight decay or dropout as regularizers. |
| **QLoRA** | LoRA over a 4-bit frozen base | Same as LoRA but VRAM-bound. NF4 recovers most of the quality; budget a small loss. |
| **Prompt / prefix tuning** | A handful of virtual tokens | Very cheap multi-task serving; weaker than LoRA on most tasks. Rarely the right pick now. |
| **Model merging** | Nothing — combines existing adapters | You already have working adapters and want their union without another training run. |

See `lora-configuration.md` for the hyperparameters once you have chosen.

## Stage ordering

When more than one stage applies, the order is fixed by what each assumes about the model it receives:

```
[continued pretraining] → SFT → [preference optimization] → [RL]
```

Each stage assumes the previous one has happened. Preference tuning a model that has not been SFT'd on
your task teaches preferences about behavior it does not yet have. Bracketed stages are optional — most
projects are SFT alone, and that is a fine place to stop.

Every additional stage is another chance to degrade what the last one achieved, so measure the full eval
suite between stages, not just at the end.

## Decision table

| What you have / want | Technique |
|---|---|
| "The model doesn't know our internal facts" | RAG. Not fine-tuning. |
| "It knows the facts but answers in the wrong shape" | SFT |
| "We have 40 real examples of the output we want" | SFT (LoRA), synthetic expansion from those seeds |
| "We have thumbs-up/down logs from production" | KTO, or DPO if you can pair them |
| "It's too verbose / hedges too much / over-refuses" | DPO or SimPO after SFT |
| "Correctness is checkable by a script" | SFT first; RL (GRPO/RLVR) if SFT plateaus |
| "We need it to speak a rare language or notation" | Continued pretraining (full FT), then SFT |
| "We need a small model to imitate a big one" | Distillation into SFT — check the teacher's terms |
| "We have several working adapters" | Merging (TIES/DARE) before another training run |
| "It must always emit valid JSON" | Structured decoding, plus SFT for content quality |
