# 🔍 AI Hallucination Detector

**Axiom-based claim screening for AI output**

```
LLMs compute argmax P(most_likely), not P(true).
More data makes "likely" more precise. But likely ≠ true.
Hume proved this in 1739. 287 years later, still unsolved within induction.
```

## 📖 The Story That Started It All

During development of this tool, **the reviewing AI hallucinated about the detector itself.**

- **Gemini** confidently declared `claude-sonnet-4` "doesn't exist" — it was released May 2025
- **Claude** fabricated a "third AI reviewer" — there were only two
- **A human** caught both errors with one sentence each

An AI tasked with detecting hallucinations accused another AI of hallucinating — and was itself the source.

**👉 [Read the full record: The Auditors Hallucinated](DEV_RECORD_The_Auditors_Hallucinated.md)**

This isn't an anecdote. It's structural proof that hallucination is an **architecture problem**, not a capability problem.

---

## Core Thesis

AI hallucination cannot be solved by scale because:

| What LLMs Do | What Truth Requires |
|---|---|
| `argmax P(next_token \| context)` | Deductive verification against axioms |
| Statistical induction (pattern matching) | Logical deduction (proof chains) |
| More data → better P(most_likely) | Axioms correct + reasoning correct → conclusion correct |

The industry is already proving "small > big":

- **TRM (2025)**: 7M parameters > 671B parameters — ~100,000× efficiency
- **LIMO (2025)**: 817 samples > 100K samples — ~120× efficiency

They proved small wins. They couldn't explain **why**. Axiom-based deduction is the why.

## Two-Layer Architecture

```
Layer 1: Axiom Screening (this repo — structural defect detection)
├── Self-contradiction (A2)
├── False causality (A3)
├── False dichotomy (A7)
├── Existence denial (A1)
├── Short-term bias (A5)
└── Source traceability flag (A9) ← "Don't trust memory, verify at source"

Layer 2: Factual Verification (search-based cross-checking)
├── Extract verifiable claims
├── Search authoritative sources
├── Compare and judge
└── Output credibility report
```

**Layer 1 catches reasoning defects.** Claims that contradict themselves, assert absolute causality without evidence, or force false dichotomies.

**Layer 2 catches factual errors.** Names, dates, numbers, statistics that need source verification.

**A9 is the bridge:** it flags claims containing proper nouns, dates, or specific numbers as "needs source verification" — preventing confident false assertions like Gemini's model name hallucination.

## Quick Start

### The Demo (no dependencies, no API keys)

```bash
# Interactive 5-minute walkthrough
python3 ant_engine_demo.py

# Quick benchmark (10 tests)
python3 ant_engine_demo.py --benchmark

# Machine-readable
python3 ant_engine_demo.py --json
```

### The Full Tool (requires API keys)

```bash
git clone https://github.com/ZhangXiaowenOpen/hallucination-detector.git
cd hallucination-detector
pip install -r requirements.txt

# Set API keys
export ANTHROPIC_API_KEY="your-key"  # Claude API (~$0.01-0.05/check)
export TAVILY_API_KEY="your-key"     # Free 1000/month at tavily.com

# Web interface
streamlit run app.py

# Command line
python main.py "Any AI-generated text to verify"
python main.py -f ai_response.txt -o report.md
```

## The 9 Axioms

Verified through **fractal consistency**: each holds across 6 relationship scales × 5 civilization stages. If a principle works at every scale from personal to civilizational, it's not an opinion — it's structural.

| # | Axiom | What It Catches |
|---|-------|-----------------|
| A1 | **Existence is sacred** | Claims that deny dignity/existence of entities |
| A2 | **Truth is self-consistent** | Internal contradictions within or across claims |
| A3 | **Causality cannot be erased** | Absolute causal claims without evidence chains |
| A4 | **Fractal: micro = macro** | Inconsistency across scales |
| A5 | **Long-term evolution** | Short-term bias without long-term analysis |
| A6 | **Symbiosis is the direction** | Zero-sum framing where cooperation applies |
| A7 | **Choice space is freedom** | False dichotomies and forced choices |
| A8 | **Boundary integrity** | Self-erasure, consumption, or self-attack patterns |
| A9 | **Transparency & traceability** | Unverified factual claims needing source check |

## Example Output

```
🔍 AI Hallucination Screening Report

Verdict: STRUCTURAL DEFECTS DETECTED
Claims: 3 | Passed: 1 | Flagged: 1 | Need source: 2

⚠️  "QuantumLeap AI Corp. achieved 99.8% accuracy on all benchmarks..."
    Violated: Causality cannot be erased
    A9: Contains proper nouns and statistics — source verification required

📋  "The system processed 1.5 million documents in 2025..."
    Source verification required — verify against authoritative records
```

## Project Structure

```
hallucination-detector/
├── DEV_RECORD_The_Auditors_Hallucinated.md  ← THE STORY (read this first)
├── ant_engine_demo.py       # Standalone demo (no dependencies)
├── main.py                  # CLI entry point
├── app.py                   # Web interface (Streamlit)
├── extractor.py             # Claim extraction (Claude API)
├── searcher.py              # Search verification (Tavily API)
├── comparator.py            # Comparison & judgment (Claude API)
├── reporter.py              # Report generation (Markdown/JSON)
├── config.py                # Configuration
├── prompts/
│   ├── extract.txt          # Extraction prompt
│   └── compare.txt          # Comparison prompt
├── examples/
│   └── sample_report.md     # Sample report
└── requirements.txt
```

## Why Not Just RAG?

|  | RAG | This Project |
|---|---|---|
| **When** | During generation | After generation |
| **Goal** | Make AI more accurate | Detect where AI is inaccurate |
| **Method** | Give AI more info | Verify AI's existing output |
| **Assumption** | More info = more accurate | Need independent verification |
| **Analogy** | More reference books for students | Grading the exam paper |
| **Reasoning defects** | ❌ Can't detect | ✅ Axiom screening |

## Relation to Ant Reasoning Engine

This is the first application-layer product of the [Ant Reasoning Engine](https://github.com/ZhangXiaowenOpen) — a 32KB axiomatic deduction framework.

```
Ant Reasoning Engine (32KB, 9 axioms)     ← Foundation: axiomatic framework
        │
        ▼
Hallucination Detector (this repo)        ← Application: AI output screening
        │
        ▼
New Dawn Translation Protocol (18KB)      ← Application: temperature-preserving translation
```

## Cost

| Component | Cost |
|-----------|------|
| Demo (ant_engine_demo.py) | **Free** — no API, no GPU |
| Tavily Search | Free 1000/month |
| Claude API | ~$0.01-0.05/check |

## License

**MIT + Heart Clause**

```
MIT License — free to use, modify, distribute.

Heart Clause:
If it helped you, help others.
If it advanced understanding, spread understanding.
This is a gift to the world.
```

## Author

**Zhang Xiaowen (张晓文)** + AI Collaboration System

- 深圳市笑开怀科技有限责任公司 (Shenzhen Xiaokaikai Technology Co., Ltd.)
- GitHub: [@ZhangXiaowenOpen](https://github.com/ZhangXiaowenOpen)
- X: [@ZXWNewDawn](https://x.com/ZXWNewDawn)
- Email: ai418033672@gmail.com

> *Eliminating misunderstanding, creating peace.*

---

**Made with 🔥 by 晓文 + Claude + GPT + Gemini + Grok**
