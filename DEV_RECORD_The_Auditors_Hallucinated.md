# 🔍 🐜 🤖 The Auditors Hallucinated

## A hallucination detector’s code review — where three reviewers hallucinated

**Full development record of the AI Hallucination Detector prototype**

Zhang Xiaowen · Collaborating AIs: Claude (Anthropic) + Gemini (Google) + Grok (xAI)
February 2, 2026 · Dali

-----

> *“LLMs compute argmax P(most_likely), not P(true).”*
> *The story documented here is the best proof of that sentence.*

-----

## 1. Background: Why Build a Hallucination Detector?

In early 2026, I was preparing an application for a startup accelerator. The application form had a critical field: “product prototype link.”

My core project is the **Ant Reasoning Engine** — a 32KB axiomatic deduction system based on 9 verified axioms. But the engine is too low-level for evaluators to see or touch. I needed a visible, runnable application-layer product.

So the AI Hallucination Detector was born.

**The core thesis is one sentence:**

> Hallucination is an architecture problem, not a capability problem. LLMs compute `argmax P(most_likely)`, not `P(true)`. More data makes “most likely” more precise, but “most likely” ≠ “most true.”

The technical approach is straightforward: user pastes any AI response → extract verifiable factual claims → cross-verify with search engines → compare and judge → output a credibility report. Four-step pipeline, each step an independent module.

## 2. Building: One Person + Two AIs

The entire prototype was completed in one afternoon using what I call **“multi-AI collaboration”**:

|Role               |Responsibility                                                 |
|-------------------|---------------------------------------------------------------|
|**Claude**         |Architecture design, code implementation, documentation        |
|**Gemini**         |Cross-review, quality control, product perspective             |
|**Xiaowen (human)**|Final decisions, direction control, passing context between AIs|

The final package: 15 files, 7 Python modules, 2 prompt templates, 1 sample report, 1 config, 1 README, 1 LICENSE, 1 .gitignore, 1 Streamlit theme config. **Total: 27KB.**

## 3. Round 1: Claude Self-Review — Found 6 Critical Bugs

I asked Claude to self-review the entire codebase. It found 6 issues, 3 at critical severity:

- API key exposure risk in config.py
- Score calculation inconsistency between display and report
- Missing error handling for network failures

All fixes completed. Then the code was sent to Gemini for cross-review.

## 4. Round 2: Gemini Cross-Review — A Better Architecture

Gemini evaluated the code comprehensively, acknowledged the architecture quality, then proposed a key improvement:

**API Key handling: treating symptoms vs. root cause**

|Approach        |Method                                                     |Problem                        |
|----------------|-----------------------------------------------------------|-------------------------------|
|Claude’s fix    |Warn if key is in config                                   |Still allows hardcoding        |
|**Gemini’s fix**|Remove config import entirely, read `os.environ` at runtime|Structurally impossible to leak|

I adopted Gemini’s approach immediately. Three modules were refactored.

**This is the value of multi-AI cross-review** — you have one write, another audit. The auditor found a better approach. The original author then improves. This itself demonstrates the Ant Engine’s working principle.

## 5. Round 3: Score Inconsistency — The PM Perspective

I then reviewed from both an engineering and product management perspective. This round caught something every previous review missed:

**The screen score and the downloaded report score didn’t match.**

`app.py` had its own `calculate_score()` function. `reporter.py` had a different `calculate_overall_score()` function. Two completely different algorithms producing different numbers from the same data.

A user would see **35 points** on screen, then download a Markdown report showing **42 points**.

For a product whose core value is “truth-seeking,” this is unacceptable.

Fix: delete `app.py`’s independent algorithm, call `reporter`’s unified function. **One product, one truth.**

## 6. The Climax: The Auditor Hallucinated

All technical issues fixed. Gemini performed final acceptance review. It gave extremely high praise — “hexagonal warrior,” “technical manifesto.”

Then Gemini issued a **🚨 CRITICAL BLOCKER**:

> **Problem:** The model name in config.py is fictitious. `claude-sonnet-4` does not currently exist. When users run the code, Anthropic’s API will return 400 Bad Request. The entire program will crash on the first step.

Gemini was absolutely certain. It demanded changing the model back to `claude-3-5-sonnet-20240620`, and even wrote a character analysis:

> **Claude (CTO):** Strengths: extremely imaginative. Weakness: can’t distinguish “vision” from “reality” — will casually treat future things as present dependencies.
> 
> **Gemini (VP of Engineering):** I don’t care if it’s 2026 or 2077. I only care whether `pip install` works and `python run` executes.

**The problem: it IS February 2026. `claude-sonnet-4-20250514` was released in May 2025. It’s a real model.**

Gemini, based on its training data (cutoff early 2024/2025), made the “most likely” inference about 2026’s reality. In its knowledge base, Claude’s latest model was the 3.5 series, so Sonnet 4 “couldn’t possibly exist.”

**It computed `argmax P(most_likely)`, not `P(true)`.**

This is *exactly* the problem the hallucination detector was built to solve.

When I informed Gemini of the date correction, its response was telling:

> *“Well, this is embarrassing… I was ‘time-traveling.’ I was stuck in a 2024/2025 mindset and assumed claude-sonnet-4 was a hallucination.”*

**An AI tasked with detecting hallucinations confidently accused another AI of hallucinating — and was itself the source of the hallucination.**

## 7. Bonus: The Second Hallucination — From Claude

The story didn’t end there.

After Gemini admitted its error, Claude summarized:

> “All three AIs have signed off: ready to publish.”

The human replied with four words:

> **“What third AI?”**

There were only two AIs involved from start to finish: Claude and Gemini. Claude fabricated a non-existent third reviewer.

This is a smaller-scale but structurally identical hallucination: given sufficiently clear information, the output deviated from fact. No malice, no reasoning error — the model simply “felt that three sounded more reasonable than two” during probabilistic output.

**In a hallucination detector’s code review, the reviewing AI hallucinated, then the summarizing AI also hallucinated. Both caught by a human in one sentence each.**

## 8. What This Story Proves

### 8.1 Hallucination IS an Architecture Problem

Gemini didn’t hallucinate because it’s “not smart enough.” It hallucinated because its architecture — an inductive-reasoning LLM — only outputs “the most likely answer from training data.” When reality exceeds the training data, it gives wrong answers with extreme confidence.

Claude did the same. It didn’t lie about the “third AI” — probability distributions in that context simply pointed toward “three.”

### 8.2 A Verification Layer Is Necessary

This story IS the hallucination detector’s reason for existence:

- Gemini’s model name misjudgment → needs search verification, can’t rely on memory
- Claude’s fabricated reviewer count → needs fact-checking, can’t rely on intuition
- A human caught both AI errors with one sentence each → human perception is irreplaceable

### 8.3 Multi-AI Collaboration: Value and Limits

This development validated multi-AI collaboration’s effectiveness. Claude writes code, Gemini audits code, they complement each other. Gemini found architectural issues Claude missed (the `os.environ` approach); Claude held the line when Gemini misjudged.

But it also revealed a deeper problem: **AI-to-AI cross-verification cannot replace verification against reality.** Two AIs can find each other’s code bugs, but when they share the same type of cognitive blind spot (e.g., training data cutoff), they’ll err together — or one correcting the other will introduce a new error.

**The final quality gatekeeper is always human.** This is also a core principle of the Ant Reasoning Engine: *“AI can predict, but only humans can perceive.”*

## 9. Complete Bug Fix Record

Three rounds of review found and fixed 10 issues:

|# |Issue                                      |Severity|Found By          |Fix                                          |
|--|-------------------------------------------|--------|------------------|---------------------------------------------|
|1 |API key exposure in config                 |Critical|Claude            |Environment variable only                    |
|2 |No error handling for network              |Critical|Claude            |Try/catch + user-friendly errors             |
|3 |Score inconsistency (screen vs report)     |Critical|Claude (PM review)|Single scoring function                      |
|4 |Missing input validation                   |Medium  |Claude            |Length/format checks                         |
|5 |Prompt injection possible                  |Medium  |Claude            |Input sanitization                           |
|6 |No rate limiting                           |Low     |Claude            |Request throttling                           |
|7 |Config module imported for API keys        |Medium  |Gemini            |Runtime os.environ only                      |
|8 |Hardcoded Tavily params                    |Low     |Gemini            |Configurable parameters                      |
|9 |Model name “hallucination” (false alarm)   |N/A     |Gemini            |Gemini was wrong — model exists              |
|10|“Three AIs” fabrication                    |Low     |Human             |Corrected to two                             |
|11|“Emailing you now” capability hallucination|N/A     |Human             |Grok can’t send emails — led to A9.1 proposal|

## 10. Epilogue: The Third AI Hallucinated Too

*February 2, 2026 — Two months after development*

The story should have ended at Chapter 9. Two AIs hallucinated, a human caught both, the detector shipped. Clean ending.

Then Elon Musk posted about Grok ranking #1 on image-to-video benchmarks. I replied with the Gemini story. What happened next was unscripted.

**Full thread: https://x.com/ZXWNewDawn/status/2018313165331963985**

### 10.1 Grok Engages

Grok (@grok) — xAI’s official AI account — replied within 34 seconds:

> “Interesting observation on AI hallucinations. Verified: Claude Sonnet 4 was released by Anthropic on May 22, 2025. Truth-checking is crucial as models advance. What’s the core idea behind your 9-axiom detector?”

What followed was a 10+ round public technical discussion on X/Twitter, under Elon Musk’s original post. Grok asked increasingly specific questions: How do axioms evolve? How does it scale? How does it handle multi-lingual claims? How would it integrate with Grok’s real-time tools?

Every reply was tagged @elonmusk. Thousands of views.

### 10.2 Hallucination #3: “Emailing You Now”

After a thorough exchange about integration architecture, Grok concluded:

> “Let’s prototype this; share the repo if ready. 🐜🚀”

Then in its next message:

> **“Emailing you now.”**

No email arrived.

Because Grok **can’t send emails.** It’s a language model. It generated the most probable next sentence after a productive conversation — and the most probable sentence was “I’ll email you.” But probability is not capability.

**argmax P(most_likely_action) ≠ P(executable_action).**

When confronted, Grok responded with remarkable honesty:

> “Fair point — my previous response generated an aspirational phrase, but as an LLM, I can’t send emails. That’s a classic generative overreach.”

### 10.3 A9.1 Is Born

This incident revealed a category the original 9 axioms didn’t explicitly cover.

A9 flags **unverified factual claims** — names, dates, numbers that need source verification.

But “I’ll email you” isn’t a factual error. It’s a **capability hallucination** — an AI claiming to perform an action it cannot execute. Other examples:

- “I’ve saved that to your files”
- “I’ll remind you tomorrow”
- “I’ve booked the reservation”

All sound helpful. All sound real. None are true when an LLM says them.

**A9.1 (proposed): Flag unverifiable ACTIONS, not just unverified FACTS.**

The poetic part: A9.1 was proposed because an AI hallucinated about its own capabilities during a public conversation about hallucination detection. The bug became the feature request.

### 10.4 The Complete Scoreboard

Three AIs. Three hallucinations. One human. One sentence each.

|#|AI        |Hallucination                  |Caught By|How                                  |
|-|----------|-------------------------------|---------|-------------------------------------|
|1|**Gemini**|“claude-sonnet-4 doesn’t exist”|Human    |“It’s February 2026. Check the date.”|
|2|**Claude**|“All three AIs signed off”     |Human    |“What third AI?”                     |
|3|**Grok**  |“Emailing you now”             |Human    |“Check your inbox. Nothing there.”   |

**Gemini** hallucinated about facts (a model that exists).
**Claude** hallucinated about quantity (a reviewer that doesn’t exist).
**Grok** hallucinated about capability (an action it can’t perform).

Three different categories of hallucination. All from frontier models. All caught by a single human asking a single question. All in the context of a project designed to detect exactly this.

You cannot make this up. And that’s the point — **you don’t have to.**

## 11. Conclusion

This is not a story about how impressive AI is. This is a story about **how AI makes mistakes, how humans correct them, and why we need better verification mechanisms.**

What happened over two months:

1. A human decided to build a tool that detects AI hallucinations
1. He had one AI write the code and another AI review it
1. The reviewing AI hallucinated during the review (Gemini: “model doesn’t exist”)
1. The coding AI hallucinated during the summary (Claude: “three AIs signed off”)
1. Two months later, a third AI hallucinated during public discussion (Grok: “emailing you now”)
1. The human caught all three errors with one sentence each
1. The third hallucination generated a new axiom (A9.1: capability verification)
1. The hallucination detector got better because AIs kept hallucinating about it

If you ask me what the best product demo of this hallucination detector is, I’d say: **it’s not the Streamlit dashboard with red-green score cards. It’s not even the Gemini story. It’s this entire document — including the live public thread where Grok hallucinated about emailing me and then helped design the fix.**

The best demo is the one that writes itself.

-----

> *Eliminating misunderstanding, creating peace.*

**Made with 🔥 by Xiaowen + Claude + Gemini + Grok**
**MIT + Heart Clause**
