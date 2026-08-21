# LoRA Configuration Reference

Contents: [Method choice](#choosing-the-method) · [Core hyperparameters](#core-hyperparameters) ·
[Training schedule](#training-schedule) · [Variants](#lora-variants) · [Worked configs](#worked-configs) ·
[Symptom table](#symptom-to-knob) · [Merging and serving](#merging-and-serving)

The single most useful fact about LoRA tuning: **target modules and learning rate dominate; rank
matters less than people assume.** Biderman et al. found performance is affected mostly by the choice
of target modules and to a smaller extent by rank, and that LoRA is unusually sensitive to learning
rate. Sweep those two before touching anything else.

## Choosing the method

| Situation | Method |
|---|---|
| Style, format, tone, task behavior; ≤ a few 10k examples | LoRA |
| Same, but VRAM-constrained (single 24GB card, 7B–14B model) | QLoRA (NF4) |
| Genuinely new domain, large corpus, continued pretraining | Full fine-tuning — LoRA underperforms here |
| Need maximum retention of base capability | LoRA, deliberately — it forgets less than full FT |

LoRA is not merely a cheaper full fine-tune. It learns less *and* forgets less. Biderman et al. showed
full fine-tuning learns weight perturbations with rank 10–100× greater than typical LoRA configs, which
is why LoRA lags on continued pretraining but can match full FT on instruction tuning at high rank. The
same constraint that limits it acts as a regularizer: it preserves base-model behavior and output
diversity better than weight decay or dropout do.

QLoRA's quality cost is small but not zero. NF4 with double quantization recovers 16-bit LoRA MMLU
performance in the original QLoRA work; FP4 lags by roughly a point. Independent applied comparisons
land a few points below LoRA on some extraction tasks. Treat 4-bit as a deliberate VRAM-for-fidelity
trade, not a default.

## Core hyperparameters

### rank (`r`)

| Rank | Use for |
|---|---|
| 4–8 | Classification, narrow style transfer, tiny datasets |
| 16–32 | Default working range for instruction/format/tone tuning |
| 64–128 | Complex reasoning, code generation, large diverse datasets |
| 256+ | Instruction tuning where you want to close the gap to full FT and have the VRAM — but only if *learning* is the bottleneck; at high rank LoRA forgets nearly as much as full FT (Biderman et al.), so never raise rank to "fix" retention benchmarks |

Start at 16 or 32. Raise rank only after target modules and LR are settled — and re-tune LR when you do,
since the optimal LR shifts with rank.

### `lora_alpha`

Set `alpha = 2r` as the default, or `alpha = r` for a more conservative update. The ratio `alpha/r` is
the effective scale on the adapter's contribution; keep it at 1 or 2. The `2r` rule is the one Biderman
et al. recommend and it is what most modern recipes use.

Halving alpha (to `0.5r`) is a legitimate emergency brake for an overfitting run, because it scales down
the whole adapter contribution without retraining.

### `target_modules`

Target every linear layer, not just attention:

```
["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
```

Attention-only LoRA is the most common cause of "LoRA didn't work for me." MLP blocks (`gate/up/down`)
carry higher-rank updates than attention does and matter disproportionately for continual learning.
Targeting MLP or all-modules beats attention-only consistently.

Module names are architecture-specific — the list above is Llama/Qwen/Mistral-style. Print the model's
named modules rather than assuming.

### `lora_dropout`

The common advice is 0 for short runs, and the common justification — that dropout only matters once
train loss says you are overfitting — is too narrow. Dropout is also a lever against *capability
regression*, which shows up on benchmarks rather than on the loss curve.

A documented case: an otherwise-identical pair of runs on a ~750-row dataset where the only changes were
`lora_dropout 0.0 → 0.05` and `val_set_size 0.0 → 0.05`. The second run narrowed a confirmed
general-capability regression on every affected benchmark — multilingual grade-school math went from
-15.6pp to -8.9pp against the reference model, MMLU-Pro and GPQA each closed 2–3pp — while fully
preserving the task behaviors the fine-tune was for. It was a real lever, though not a complete fix.
Read the mechanism carefully: Biderman et al. measured that dropout does **not** reduce forgetting
(full FT + dropout 0.05/0.1 forgets exactly as much as no dropout), so this win is *overfitting control*
on a small templated set — consistent with a sawtooth train-loss pattern — and it is confounded, since
the val split also removed ~5% of rows from training. Keep it as a cheap first step, and do not keep
tuning it; the levers with a direct path to the benchmark gap are lower LR and general replay data.

Practical reading: start at 0, but if the retention gate fails, **0.05 is a cheap first thing to try**,
and it is an isolated one-knob change you can attribute. Do not wait for train loss to tell you.

### `val_set_size` / eval split

Non-zero, always. Runs configured with no validation split produce no `eval_loss` curve at all, which
means overfitting and regression are both invisible until you benchmark the finished model. In the case
above, the first run with a 5% val split was also the first one where the team could see eval loss
falling over training rather than guessing — on a small dataset that curve is noisy, but an unmeasured
curve tells you nothing at any dataset size.

### `bias`

`"none"`. Training biases adds parameters and complicates merging for no measured benefit in the common
case.

## Training schedule

| Knob | Value | Note |
|---|---|---|
| Learning rate (SFT, *learning-bound*) | `2e-4` start; range `5e-5`–`5e-4` | LoRA tolerates far higher LR than full FT (Biderman et al.) — that is the answer when the model has *not* learned the task. |
| Learning rate (SFT, *retention-bound*) | `1e-5`–`5e-5` | When the behavior is already learned but benchmarks regressed, the binding constraint is forgetting: Lin et al. (2025) show 1e-6 largely eliminates general-capability degradation at comparable domain performance, while 2e-5 (the "learning-bound" default) is the degrading end. This is the first knob to try against a retention gate failure. |
| Learning rate (DPO/GRPO) | `5e-6` | Preference optimization needs 1–2 orders of magnitude less. |
| Epochs | 1–3 | Past 3 the returns are diminishing and overfitting risk climbs sharply. |
| Scheduler | `cosine` (or `linear`) | Cosine is the common default. |
| Warmup | 3–10% of total steps | |
| Effective batch size | 8–32 | `per_device_batch × grad_accum × world_size`. Small datasets prefer the low end. |
| Weight decay | 0.01–0.1 | |
| Precision | bf16 | fp16 overflows more often on these LRs. |
| Gradient checkpointing | on | Trades ~20–30% speed for large VRAM savings. |

**Learning rate is the highest-variance knob.** If a run produces a model that is either unchanged or
lobotomized, LR is the first suspect, before rank, before data volume.

### Sequence length and packing

Set `max_seq_length` from the actual token-length distribution of your data, not from the model's
maximum. Compute the p95 length and round up; anything longer is padding you pay for on every step.

Packing concatenates short examples to fill the context and removes padding waste, but naively packed
sequences let attention flow across unrelated examples — cross-contamination that measurably hurts
reasoning tasks. Only enable packing when the trainer applies per-example attention masking
(TRL's `SFTConfig(packing=True)` and Axolotl's multipack do; a hand-rolled concat does not).

**Packing is a throughput optimization, and on a small dataset there is no throughput problem to
solve.** A few hundred to a couple thousand examples train in minutes either way, so the padding you
save is worth nothing and the contamination risk — higher for multi-turn and tool-call data, where one
example is already many messages — is pure downside. Real agentic-tuning setups routinely run
`sample_packing: false` for exactly this reason. Turn packing on only when the dataset is large enough
that step time actually hurts.

## LoRA variants

Vanilla LoRA with a well-tuned LR is a strong baseline and recent work argues it is usually sufficient.
Reach for a variant only with a measured reason:

| Variant | What it changes | Worth it when |
|---|---|---|
| **rsLoRA** | Scales by `alpha/√r` instead of `alpha/r` | Using high rank (64+); stabilizes what would otherwise need LR retuning |
| **DoRA** | Decouples update magnitude from direction | Chasing the last points of downstream accuracy and can afford ~5–10% more VRAM and slower steps; merge before serving |
| **LoRA+** | Different LR for the `A` and `B` matrices | Cheap to try — no extra memory, sometimes converges faster |
| **PiSSA** | Initializes adapters from principal singular components of `W` | Fixed compute budget and convergence speed is the binding constraint |
| **LoftQ** | Quantization-aware init | QLoRA runs where 4-bit init error is measurably hurting |

Gains from these are inconsistent across models and tasks. Do not stack them speculatively — each one
adds a confound to the one experiment that matters, which is whether your data works.

## Worked configs

A starting point for format/tone/task tuning of a 7B–14B instruct model on a single 24GB card. Adjust
after the first run, one knob at a time.

```python
# QLoRA SFT with TRL + PEFT. Assumes a `messages`-format dataset.
from peft import LoraConfig
from transformers import BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer
import torch

quant = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",          # NF4, not FP4 — FP4 costs ~1 point
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
)

peft_config = LoraConfig(
    r=32,
    lora_alpha=64,                       # alpha = 2r
    lora_dropout=0.0,                    # raise only if overfitting is confirmed
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],   # all linear layers
)

args = SFTConfig(
    learning_rate=2e-4,
    num_train_epochs=2,
    lr_scheduler_type="cosine",
    warmup_ratio=0.05,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,       # effective batch 16
    weight_decay=0.01,
    bf16=True,
    gradient_checkpointing=True,
    max_length=2048,                     # set from your p95 token length
    packing=True,                        # TRL masks across packed examples
    assistant_only_loss=True,            # messages format: loss on assistant turns only
    eos_token="<|im_end|>",              # must match the chat template, not the raw tokenizer default
    eval_strategy="steps",
    eval_steps=50,                       # you need this curve to catch overfitting
    save_strategy="steps",
    save_steps=50,
    load_best_model_at_end=True,
)
```

Three settings there are not cosmetic.

**The loss-masking flag depends on your dataset format, and picking the wrong one silently trains on
everything.** In current TRL they are not interchangeable:

| Dataset format | Flag | Notes |
|---|---|---|
| Conversational (`messages`) | `assistant_only_loss=True` | Requires the chat template to mark generation spans with `{% generation %}`; TRL auto-patches known families such as Qwen3. Verify for anything else. |
| Prompt-completion (`prompt`/`completion`) | `completion_only_loss=True` | Already the default for this format. |

Masking the prompt makes the model learn to *produce* answers rather than to predict user turns it will
never generate — typically worth 5–15% on instruction-following benchmarks.

**`eos_token` must match the chat template**, not the tokenizer's default. Qwen-style templates end
turns with `<|im_end|>`; leaving the default `</s>` means the model never learns to stop.

**`eval_steps` with a real validation split** is the only way you will see the divergence that signals
overfitting. A run with no eval curve is a run you cannot diagnose.

TRL's argument names move between versions — `max_seq_length` became `max_length`, and the masking flags
were split as above. Check the installed version's `SFTConfig` signature rather than trusting a config
copied from a blog post.

## Symptom to knob

| Symptom | Most likely cause | Fix |
|---|---|---|
| Output barely changed from base | LR too low, rank too low, or attention-only targets | Raise LR toward `3e-4`; add MLP modules; then raise rank |
| Train loss < 0.2, outputs memorized | Overfitting | Cut to 1 epoch, lower LR, `weight_decay` 0.01–0.1, `lora_dropout` 0.1, or scale alpha by 0.5 |
| Val loss rising while train loss falls | Overfitting | Stop at the divergence point; use `load_best_model_at_end` |
| Model repeats phrases, never stops | EOS not learned, or mode collapse | Verify the chat template's EOS is present and unmasked in labels; reduce epochs |
| Correct content, wrong wrapper/format | Chat template mismatch between train and inference | Use `tokenizer.apply_chat_template` on both sides |
| Gained the task, lost general ability | Capability regression (often LR-side) | See `avoiding-degradation.md` — **lower LR first** (to 1e-5–5e-5), then add a general replay mix, then fewer epochs; dropout/val are cheap overfitting control, not the forgetting fix |
| Confidently wrong new facts | Taught unknown knowledge | See `avoiding-degradation.md` — this is a data problem, not a config problem |
| Loss spikes to NaN | fp16 with high LR | Switch to bf16; lower LR |

## Merging and serving

Adapters can be served dynamically (one base model, many adapters — vLLM and LoRAX support this) or
merged into the base weights for a single artifact. Merge when you want no inference overhead; DoRA in
particular should be merged because its runtime cost is higher than plain LoRA's.

Combining several adapters into one model is a different operation from serving them separately.
Linear averaging (model soup) is the naive baseline; TIES trims redundant parameters, resolves sign
conflicts, then averages the agreeing ones; DARE randomly drops and rescales to cut interference and is
usually applied as a preprocessing step before TIES. Both generally beat plain weight averaging.
Expect some per-task loss relative to the individual adapters — measure it rather than assuming it is
free.

Merging a QLoRA adapter into a 4-bit base and then dequantizing loses precision. Merge into the
full-precision base weights instead, then quantize the merged model if you need to.
