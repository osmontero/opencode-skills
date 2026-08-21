# Synthetic Data Generation Reference

Contents: [The QDC frame](#quality-diversity-complexity) · [Method catalog](#method-catalog) ·
[Engineering diversity](#engineering-diversity) · [Verification](#verification-and-filtering) ·
[Collapse and drift](#collapse-and-drift) · [Licensing](#licensing-and-terms)

## Quality, diversity, complexity

Three axes govern whether synthetic data helps, and they trade off against each other:

- **Quality** — correctness and low noise relative to the target distribution. Drives *in-distribution*
  performance.
- **Diversity** — coverage and low self-similarity across the sample space. Drives *out-of-distribution*
  generalization.
- **Complexity** — difficulty and compositionality. Helps both, up to a point; data that is too hard
  degrades learning.

The failure mode of naive pipelines is optimizing quality alone. Aggressive quality filtering shrinks
volume *and* collapses diversity, producing a model that scores well on the target benchmark and falls
apart one step outside it. Decide which axis your use case actually needs before you filter: a narrow
format-conversion task genuinely wants quality over diversity; an assistant persona wants both.

Generation is cheap and filtering is destructive, so **generate wide and filter down** rather than
generating exactly the number of examples you want.

## Method catalog

Pick by what you have, not by what is fashionable.

| You have | Method | How it works |
|---|---|---|
| A few dozen real examples | **Seed expansion (Self-Instruct)** | Bootstrap new instructions from a seed pool, sampling a few seeds as few-shot context each round; add accepted outputs back to the pool. Original work turned 175 seeds into 52k pairs. |
| A working dataset that is too easy | **Evolution (Evol-Instruct)** | Iteratively rewrite instructions to be harder along fixed operators: add constraints, deepen reasoning, require domain knowledge, increase input complexity. Produces a difficulty curriculum. |
| An aligned model and nothing else | **Template-free extraction (Magpie)** | Feed only the pre-query chat template prefix; the aligned model autoregressively emits a plausible user query, then answer it in a second pass. Generates instructions with no seed set at all. |
| A need for breadth | **Persona-driven (Persona Hub)** | Condition each generation on a sampled persona so the model's latent perspectives are spread across the dataset. Without a persona seed, an LLM returns variations on a handful of default voices. |
| A document corpus | **Document-grounded QA** | Generate question/answer pairs from chunks, then augment: paraphrase answers, vary retrieved-context relevance, generate multiple valid phrasings per fact. Un-augmented doc→QA memorizes without generalizing. |
| A need for dialogue | **Self-chat / user simulator** | Two roles played by the model, with an explicit persona defining the user turns. Vague user personas produce unrealistically cooperative users. |
| Tools/APIs to teach | **Trajectory synthesis** | Sample tool graphs, generate tasks requiring them, execute against real or simulated tools, log the full trajectory including failures and recovery. Supervise assistant turns only. |
| A stronger reasoning model | **Reasoning distillation** | Sample chain-of-thought traces from the teacher, keep only traces whose final answer verifies. Small curated sets go far — s1 used 1k traces, LIMO 817. |

These compose. A common strong pipeline is persona-conditioned seed expansion → evolution for
difficulty → verification filter → dedup.

## Engineering diversity

Diversity does not emerge from raising temperature. It comes from varying the *conditioning*.

**Build an explicit taxonomy first.** Enumerate the axes your data must cover — task type, topic,
input length, difficulty, tone, edge cases, failure modes — and sample cells from the cross-product
rather than asking for N examples in one call. An unconditioned generation loop rediscovers the same
few modes indefinitely.

**Vary the generator, not just the prompt.** Different models, different system prompts, different
few-shot exemplars per batch. Rotate which seeds appear as exemplars so the pool does not inbreed.

**Measure diversity, do not assume it:**

| Metric | What it catches |
|---|---|
| N-gram diversity score (unique n-grams / total) | Surface-level template repetition |
| Compression ratio (gzip size / raw size) | Global redundancy — a cheap first alarm |
| Mean pairwise embedding cosine distance | Semantic clustering across the whole set |
| Nearest-neighbor distance per example | Individual near-duplicates; also a filter threshold |
| K-means cluster coverage / facility location | Whether taxonomy cells are actually populated |

Heuristic metrics are necessary but not sufficient — n-gram and compression scores miss semantic
monotony. Pair one lexical metric with one embedding metric.

## Verification and filtering

Match the verifier to what "correct" means for the task:

- **Verifiable answers** (math, code, structured extraction): generate K samples, take the majority
  vote, discard the example if the majority disagrees with the reference. Cheap and reliable.
- **Executable outputs**: run it. Unit tests and parsers are stronger verifiers than any judge.
- **Schema-constrained outputs**: validate against the schema before a model ever sees it.
- **Open-ended outputs**: reward model scores, or an LLM judge with an explicit rubric.

**LLM judges need bias controls or they measure the wrong thing.** Position bias (favoring whichever
response came first) requires randomizing order and averaging across both orderings. Verbosity bias
requires a rubric that states how length is treated. Self-preference is real and causal (Panickssery et
al., NeurIPS 2024), but the measured mechanism is *familiarity/perplexity*: judges rate lower-perplexity,
in-distribution text higher regardless of authorship (Wataoka et al., 2024) — so a judge from the same
base family as the generator is biased even when they are technically different models, and a judge
fine-tuned on exactly the content being scored has no incentive to flag "in-distribution but broken"
outputs. Use a different model as judge where you can, cross-judge borderline scores with a second
family, and fix the judge's sampling (temperature 0; re-run any score that flips). For **code**
quality specifically, the validated layer is deterministic: syntax checks, execution, unit tests, and
schema validation are the pass/fail gates; the LLM judge is an advisory ranking on top of them, with an
explicit fault taxonomy (CodeJudge, EMNLP 2024: an 8-type/4-severity rubric with the task spec as
reference gave the biggest measured correlation gain with human judgment). Judge accuracy tracks the
generator's difficulty (JudgeBench, 2024), so expect exactly the hard samples you care about to be the
worst-scored.

Quality-scoring approaches worth knowing: AlpaGasus prompts a strong model to rate each example and
drops those below a threshold; DEITA scores on quality *and* difficulty jointly; IFD (Instruction
Following Difficulty) and Superfiltering use the loss signal of a small model — even GPT-2 — to rank
examples cheaply, which scales to sets too large for judge calls.

The consistent empirical result across LIMA, AlpaGasus, and LIMO is that, **within the same total
budget and for general instruction/style tasks**, a curated few hundred to few thousand examples beat
tens of thousands of unfiltered ones. The result does not extend to overriding a base prior
(safety-refusal removal, strong-default override), where the evidence points the other way: the behavior
needs a minimum count and a minimum share of the mix, and rephrased variants of a few scenarios are the
least-effective data there.

## Collapse and drift

Training on model output recursively degrades the distribution: rare events vanish first (tail
collapse), then the distribution narrows toward the mean. The finding that matters operationally is
about *accumulate versus replace*. Replacing real data with each new synthetic generation collapses;
accumulating — keeping the real data and prior generations alongside the new synthetic data — controls
the error. Keep a real-data anchor in every mix, and never train generation N+1 exclusively on the
output of generation N.

Practical guards:
- Keep a fixed, human-authored holdout that never gets regenerated. It is your drift detector.
- Version the generator model and prompt with the dataset. A generator upgrade is a distribution change.
- Track the diversity metrics above across generations; a falling n-gram score is early collapse.

## Licensing and terms

Whether you may train on another model's outputs is a contract question, not a technical one.

- Open-weight models under permissive licenses (Apache-2.0, MIT): generally fine; check the specific
  license and any acceptable-use addendum.
- Commercial APIs: major providers' terms — OpenAI, Anthropic, Mistral, xAI among them — restrict using
  outputs to train competing models, and some restrict training *any* model on outputs without
  authorization. Read the current terms for the specific provider before building a pipeline on it.
- Some open-weight licenses carry naming or downstream-license obligations for derived models.

Record the generating model, its version, and the applicable terms in the dataset card. This is the
detail that is impossible to reconstruct later and blocks a release when someone finally asks.
