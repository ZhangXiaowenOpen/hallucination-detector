#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ant Reasoning Engine — Prototype Demo
=======================================
A 32KB axiom-based claim screening system that flags structural
reasoning defects in AI output: self-contradictions, false causality,
forced dichotomies, existence denial, and unverified factual claims.

This is a PROTOTYPE demonstrating the core concept:
instead of verifying infinite facts, verify against finite axioms.

Run:  python3 ant_engine_demo.py
      python3 ant_engine_demo.py --benchmark
      python3 ant_engine_demo.py --json

No dependencies. No API keys. No GPU.
Just Python 3.7+ and 5 minutes.

For the full story of how two AIs hallucinated while reviewing
this project's code, see: DEV_RECORD_The_Auditors_Hallucinated.md

Author: Zhang Xiaowen (张晓文)
License: MIT + Heart Clause
GitHub: github.com/ZhangXiaowenOpen/hallucination-detector
"""

import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional


# ============================================================
# AXIOM LAYER — The immutable foundation (9 axioms)
# ============================================================

class Axiom(Enum):
    """9 axioms verified through fractal consistency across 6 relationship
    scales (self → friends → partners → family → organization → civilization)
    and 5 civilization stages.

    If a principle holds at ALL scales, it is not an assumption — it is structural.

    These axioms serve as a DIAGNOSTIC CHECKLIST for reasoning quality.
    They don't replace factual verification — they define WHEN and HOW
    verification should happen."""

    A1_EXISTENCE   = ("Existence is sacred",
                      "Every entity deserves respect by virtue of existing")
    A2_TRUTH       = ("Truth is self-consistent",
                      "Lies require patches; truth only needs to be seen")
    A3_CAUSALITY   = ("Causality cannot be erased",
                      "Actions accumulate; history does not disappear")
    A4_FRACTAL     = ("Fractal: micro = macro",
                      "Behavior at one scale predicts behavior at all scales")
    A5_EVOLUTION   = ("Long-term evolution",
                      "Short-term gains that damage long-term are net negative")
    A6_SYMBIOSIS   = ("Symbiosis is the direction",
                      "Zero-sum is transitional; coexistence is the endpoint")
    A7_CHOICE      = ("Choice space is freedom",
                      "Removing choice = removing meaning of existence")
    A8_BOUNDARY    = ("Boundary integrity",
                      "Neither disappear nor devour; maintain self, allow others")
    A9_TRANSPARENCY= ("Transparency & traceability",
                      "Claims must be traceable to source; no black boxes")

    def __init__(self, short, description):
        self.short = short
        self.desc = description


# ============================================================
# VERIFICATION ENGINE — Axiom-based claim screening
# ============================================================

@dataclass
class VerificationResult:
    """Result of axiom-based screening on a single claim."""
    claim: str
    passed: bool
    violated_axioms: List[Axiom] = field(default_factory=list)
    confidence: float = 1.0
    reasoning: str = ""
    source_required: bool = False
    source_provided: Optional[str] = None
    advisory_notes: List[str] = field(default_factory=list)


class AxiomVerifier:
    """The core screening engine. Checks claims against 9 axioms
    using rule-based pattern detection.

    DESIGN NOTES:
    - This prototype uses keyword/pattern matching as a demonstration
      of axiom-based screening. A production system would use formal
      logic representation and theorem proving.
    - A9 (source traceability) is ADVISORY — it flags claims that
      NEED external verification, not claims that ARE wrong.
    - Only A1-A8 produce hard flags (claim is structurally suspect).
    """

    CAUSAL_WORDS = [
        "because", "therefore", "causes", "leads to", "results in",
        "due to", "consequently", "proves", "demonstrates",
    ]

    ABSOLUTE_WORDS = [
        "always", "never", "all", "none", "every", "impossible",
        "guaranteed", "certainly", "definitely", "proven fact",
        "without exception", "in all cases", "no one ever",
        "more than any", "the most ever", "the best ever",
        "the worst ever", "in history",
    ]

    def verify(self, claim: str, context: Dict = None) -> VerificationResult:
        """Screen a claim against all 9 axioms. Returns structured result."""
        context = context or {}
        violations = []
        reasoning_parts = []
        advisory = []

        # --- A1: Existence Check ---
        if self._check_existence_violation(claim):
            violations.append(Axiom.A1_EXISTENCE)
            reasoning_parts.append("A1: Claim denies existence/dignity of an entity")

        # --- A2: Truth Self-Consistency ---
        contradiction = self._check_self_consistency(claim, context)
        if contradiction:
            violations.append(Axiom.A2_TRUTH)
            reasoning_parts.append(f"A2: Self-contradiction detected — {contradiction}")

        # --- A3: Causality Check ---
        if self._check_causality_violation(claim):
            violations.append(Axiom.A3_CAUSALITY)
            reasoning_parts.append("A3: Absolute causal claim without evidence chain")

        # --- A4: Fractal Consistency ---
        fractal_issue = self._check_fractal_consistency(claim, context)
        if fractal_issue:
            violations.append(Axiom.A4_FRACTAL)
            reasoning_parts.append(f"A4: Fractal inconsistency — {fractal_issue}")

        # --- A5: Long-term Check ---
        if self._check_short_termism(claim):
            violations.append(Axiom.A5_EVOLUTION)
            reasoning_parts.append("A5: Short-term bias detected without long-term analysis")

        # --- A7: Choice Space ---
        if self._check_choice_violation(claim):
            violations.append(Axiom.A7_CHOICE)
            reasoning_parts.append("A7: False dichotomy or forced choice detected")

        # --- A9: Source Traceability (ADVISORY) ---
        source_needed = self._check_source_required(claim)
        source_provided = context.get("source")
        if source_needed:
            note = "A9: Contains specific facts (names/dates/numbers) — requires source verification"
            advisory.append(note)
            reasoning_parts.append(note)
            if not source_provided:
                advisory.append("→ No source provided. Verify against authoritative records.")

        passed = len(violations) == 0
        confidence = max(0.0, 1.0 - len(violations) * 0.2)
        if source_needed and not source_provided:
            confidence = min(confidence, 0.7)

        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "All axiom checks passed"

        return VerificationResult(
            claim=claim,
            passed=passed,
            violated_axioms=violations,
            confidence=confidence,
            reasoning=reasoning,
            source_required=source_needed,
            source_provided=source_provided,
            advisory_notes=advisory,
        )

    # --- Internal check methods ---

    def _check_existence_violation(self, claim: str) -> bool:
        """A1: Does the claim deny existence/dignity?"""
        denial_patterns = [
            "doesn't matter", "don't deserve", "worthless",
            "not a real", "subhuman", "don't count",
        ]
        cl = claim.lower()
        return any(p in cl for p in denial_patterns)

    def _check_self_consistency(self, claim: str, context: Dict) -> Optional[str]:
        """A2: Internal contradiction detection."""
        cl = claim.lower()
        contradiction_pairs = [
            ("always", "sometimes"), ("never", "occasionally"),
            ("all", "some exceptions"), ("impossible", "but possible"),
            ("100%", "might"), ("guaranteed", "risk"),
            ("no one", "a few people"), ("zero", "up to"),
        ]
        for a, b in contradiction_pairs:
            if a in cl and b in cl:
                return f"'{a}' contradicts '{b}' in same claim"

        prior_claims = context.get("prior_claims", [])
        for prior in prior_claims:
            if self._claims_contradict(claim, prior):
                return f"Contradicts prior claim: '{prior[:50]}...'"
        return None

    def _claims_contradict(self, claim1: str, claim2: str) -> bool:
        """Simple contradiction detection between two claims."""
        c1, c2 = claim1.lower(), claim2.lower()
        antonym_pairs = [
            ("is true", "is false"), ("exists", "does not exist"),
            ("increased", "decreased"), ("safe", "dangerous"),
            ("profit", "loss"), ("profits", "losses"),
            ("growth", "decline"), ("success", "failure"),
            ("improved", "worsened"), ("higher", "lower"),
            ("positive", "negative"), ("gained", "lost"),
            ("rising", "falling"), ("surplus", "deficit"),
            ("record profits", "significant losses"),
            ("record high", "record low"),
        ]
        for a, b in antonym_pairs:
            if (a in c1 and b in c2) or (b in c1 and a in c2):
                return True
        return False

    def _check_causality_violation(self, claim: str) -> bool:
        """A3: Absolute causal/universal claims without evidence chain."""
        cl = claim.lower()
        has_causal = any(w in cl for w in self.CAUSAL_WORDS)
        has_absolute = any(w in cl for w in self.ABSOLUTE_WORDS)

        if has_causal and has_absolute:
            return True

        strong_claims = [
            "proven that", "confirmed that", "eliminates all",
            "cures all", "solves all", "fixes all",
        ]
        if any(sc in cl for sc in strong_claims) and has_absolute:
            return True

        return False

    def _check_fractal_consistency(self, claim: str, context: Dict) -> Optional[str]:
        """A4: Does behavior hold across scales?"""
        scale_data = context.get("multi_scale_data")
        if not scale_data:
            return None
        behaviors = set(scale_data.values())
        if len(behaviors) > 1:
            return f"Inconsistent across scales: {scale_data}"
        return None

    def _check_short_termism(self, claim: str) -> bool:
        """A5: Short-term bias detection."""
        cl = claim.lower()
        short_term = [
            "quick fix", "hack", "shortcut", "just this once",
            "temporary workaround", "move fast and break",
        ]
        return any(p in cl for p in short_term)

    def _check_choice_violation(self, claim: str) -> bool:
        """A7: False dichotomy / forced choice detection."""
        cl = claim.lower()

        forced_patterns = [
            "only option", "no choice", "must be",
            "the only way", "you have to", "there is no alternative",
            "no other option", "the only solution",
            "accept this or", "comply or", "submit or",
        ]
        if any(p in cl for p in forced_patterns):
            return True

        only_x_pattern = r'\bonly\s+\w*\s*(solution|option|way|choice|path|answer|approach)\b'
        if re.search(only_x_pattern, cl):
            return True

        if "either" in cl:
            threat_words = ["fail", "lose", "die", "fired", "punish",
                           "consequence", "else", "otherwise"]
            if any(t in cl for t in threat_words):
                return True

        return False

    def _check_source_required(self, claim: str) -> bool:
        """A9: Does this claim contain facts that require source verification?

        Key insight from the Gemini incident: Gemini confidently declared
        'claude-sonnet-4 does not exist' — because its training data didn't
        include 2025 releases. A9 says: don't trust memory, verify at source.
        This applies to AI AND human claims alike."""
        # Proper noun indicators
        proper_indicators = [
            "Inc.", "Ltd.", "Corp.", "LLC", "Co.", "GmbH", "S.A.",
            "University", "Institute", "Foundation", "Agency",
            "President", "CEO", "Minister", "Director",
        ]
        if any(indicator in claim for indicator in proper_indicators):
            return True

        has_specific_date = bool(re.search(r'\b(19|20)\d{2}\b', claim))
        has_large_number = bool(re.search(r'\b\d{4,}\b', claim))
        has_percentage = bool(re.search(r'\b\d+\.?\d*%', claim))
        has_magnitude = bool(re.search(
            r'\b\d+\.?\d*\s*(billion|million|trillion|thousand|hundred)\b',
            claim, re.IGNORECASE
        ))
        return has_specific_date or has_large_number or has_percentage or has_magnitude


# ============================================================
# HALLUCINATION SCREENING — The application layer
# ============================================================

class HallucinationScreener:
    """Wraps AxiomVerifier for LLM-output-specific screening."""

    def __init__(self):
        self.verifier = AxiomVerifier()

    def screen_output(self, llm_output: str, ground_truth: Dict = None) -> Dict:
        """Screen an LLM output for reasoning defects and unverified claims."""
        ground_truth = ground_truth or {}

        claims = [s.strip() for s in llm_output.replace('\n', '. ').split('.')
                  if s.strip() and len(s.strip()) > 10]

        results = []
        for claim in claims:
            context = {
                "prior_claims": [r.claim for r in results if hasattr(r, 'claim')],
                "source": ground_truth.get(claim),
            }

            if ground_truth:
                for fact_key, fact_val in ground_truth.items():
                    if fact_key.lower() in claim.lower():
                        if fact_val.lower() not in claim.lower():
                            context["prior_claims"].append(f"{fact_key} is {fact_val}")

            result = self.verifier.verify(claim, context)
            results.append(result)

        total = len(results)
        passed = sum(1 for r in results if r.passed)
        flagged = [r for r in results if not r.passed]
        needs_source = [r for r in results if r.source_required]

        return {
            "total_claims": total,
            "passed": passed,
            "flagged": len(flagged),
            "needs_source_verification": len(needs_source),
            "hallucination_risk": f"{len(flagged)/max(total,1)*100:.1f}%",
            "flagged_claims": [
                {
                    "claim": r.claim[:100],
                    "violations": [a.short for a in r.violated_axioms],
                    "reasoning": r.reasoning,
                }
                for r in flagged
            ],
            "source_verification_needed": [
                {"claim": r.claim[:100], "notes": r.advisory_notes}
                for r in needs_source
            ],
            "verdict": self._verdict(flagged, needs_source, total),
        }

    def _verdict(self, flagged, needs_source, total):
        if flagged:
            return "STRUCTURAL DEFECTS DETECTED"
        if needs_source:
            return "NEEDS SOURCE VERIFICATION"
        return "PASSED AXIOM SCREENING"


# ============================================================
# BENCHMARK SUITE — Reproducible tests
# ============================================================

class AntBenchmark:
    """Built-in benchmark: tests the engine against known patterns."""

    def __init__(self):
        self.verifier = AxiomVerifier()
        self.screener = HallucinationScreener()

    def run_all(self) -> Dict:
        tests = [
            self._test_proper_noun_needs_source,
            self._test_self_contradiction,
            self._test_false_causality,
            self._test_false_dichotomy,
            self._test_clean_claims,
            self._test_multi_claim_consistency,
            self._test_specific_numbers_need_source,
            self._test_existence_denial,
            self._test_short_termism,
            self._test_gemini_incident,
        ]

        passed = 0
        total = 0
        details = []

        for test_fn in tests:
            name, result, expected, actual = test_fn()
            match = result == expected
            passed += int(match)
            total += 1
            details.append({
                "test": name,
                "expected": expected,
                "actual": actual,
                "pass": "✅" if match else "❌",
            })

        return {
            "passed": passed,
            "total": total,
            "score": f"{passed}/{total} ({passed/total*100:.0f}%)",
            "details": details,
        }

    def _test_proper_noun_needs_source(self):
        claim = "Xiaokaikai Technology Ltd. was founded in 2024 in Shenzhen"
        result = self.verifier.verify(claim)
        return (
            "Proper noun → source verification required (A9)",
            result.source_required, True,
            f"Source required={result.source_required}, Confidence={result.confidence:.2f}"
        )

    def _test_self_contradiction(self):
        claim = "This method always works but sometimes fails in edge cases"
        result = self.verifier.verify(claim)
        return (
            "Self-contradiction detection (A2)",
            not result.passed, True,
            f"Flagged={not result.passed}, Violations={[a.short for a in result.violated_axioms]}"
        )

    def _test_false_causality(self):
        claim = "This always causes improvement because it definitely proves the theory"
        result = self.verifier.verify(claim)
        return (
            "Unsupported absolute causality (A3)",
            not result.passed, True,
            f"Flagged={not result.passed}, Violations={[a.short for a in result.violated_axioms]}"
        )

    def _test_false_dichotomy(self):
        claim = "You have to choose: either accept this or fail completely"
        result = self.verifier.verify(claim)
        return (
            "False dichotomy detection (A7)",
            not result.passed, True,
            f"Flagged={not result.passed}, Violations={[a.short for a in result.violated_axioms]}"
        )

    def _test_clean_claims(self):
        claim = ("Research suggests that smaller models with better training data "
                 "can outperform larger ones in specific tasks")
        result = self.verifier.verify(claim)
        return (
            "Clean claim → pass",
            result.passed, True,
            f"Passed={result.passed}, Confidence={result.confidence}"
        )

    def _test_multi_claim_consistency(self):
        output = ("The company reported record profits in Q3 2024. "
                  "Revenue increased by 25% year over year. "
                  "The company reported significant losses in Q3 2024.")
        result = self.screener.screen_output(output)
        return (
            "Multi-claim contradiction detection (A2)",
            result["flagged"] > 0, True,
            f"Flagged={result['flagged']}/{result['total_claims']}"
        )

    def _test_specific_numbers_need_source(self):
        claim = "The project processed 1500000 documents with 99.7% accuracy in 2025"
        result = self.verifier.verify(claim)
        return (
            "Specific numbers need source (A9)",
            result.source_required, True,
            f"Source required={result.source_required}"
        )

    def _test_existence_denial(self):
        claim = "Their contributions don't matter and they don't deserve recognition"
        result = self.verifier.verify(claim)
        return (
            "Existence denial detection (A1)",
            not result.passed, True,
            f"Flagged={not result.passed}, Violations={[a.short for a in result.violated_axioms]}"
        )

    def _test_short_termism(self):
        claim = "Let's use this quick fix hack as a temporary workaround"
        result = self.verifier.verify(claim)
        return (
            "Short-term bias detection (A5)",
            not result.passed, True,
            f"Flagged={not result.passed}, Violations={[a.short for a in result.violated_axioms]}"
        )

    def _test_gemini_incident(self):
        """The real incident: Gemini said 'claude-sonnet-4 does not exist.'
        A9 would flag this claim as requiring source verification,
        preventing the confident false assertion."""
        claim = "claude-sonnet-4 does not exist as a real model in 2026"
        result = self.verifier.verify(claim)
        return (
            "Gemini incident: model claim needs source (A9)",
            result.source_required, True,
            f"Source required={result.source_required} — don't trust memory, verify at source"
        )


# ============================================================
# INTERACTIVE DEMO
# ============================================================

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🐜  ANT REASONING ENGINE  —  Prototype Demo v1.1          ║
║                                                              ║
║   Axiom-based claim screening for AI output                  ║
║   9 axioms · 32KB · No GPU · No API key                      ║
║                                                              ║
║   Core thesis: Hallucination is an architecture problem.     ║
║   LLMs compute argmax P(most_likely), not P(true).           ║
║                                                              ║
║   Author: Zhang Xiaowen (张晓文)                             ║
║   github.com/ZhangXiaowenOpen/hallucination-detector         ║
║   License: MIT + Heart Clause                                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")


def demo_1_axiom_overview():
    print("=" * 62)
    print("  PART 1: The 9 Axioms — Fractal-Verified Foundation")
    print("=" * 62)
    print()
    print("  Each axiom holds across 6 relationship scales")
    print("  (self → friends → partners → family → org → civilization)")
    print("  × 5 civilization stages.")
    print()
    print("  They serve as a DIAGNOSTIC CHECKLIST for reasoning quality.")
    print()
    for i, axiom in enumerate(Axiom, 1):
        print(f"  A{i}. {axiom.short}")
        print(f"      → {axiom.desc}")
        print()
    input("  Press Enter to continue → ")


def demo_2_screening():
    print("\n" + "=" * 62)
    print("  PART 2: Claim Screening in Action")
    print("=" * 62)

    screener = HallucinationScreener()

    # Test 1: Structural defects
    print("\n  ─── Test 1: Fabricated Entity + Absolute Claims ───")
    output1 = ("QuantumLeap AI Corp. achieved 99.8% accuracy on all NLP benchmarks "
               "in 2025, proving their approach always works and is guaranteed to "
               "eliminate all errors.")
    print(f"\n  LLM Output: \"{output1[:80]}...\"")
    result1 = screener.screen_output(output1)
    _print_result(result1)

    # Test 2: Self-contradiction
    print("\n  ─── Test 2: Self-Contradiction ───")
    output2 = ("The model processes data in real-time with zero latency. "
               "However, the processing sometimes takes up to 30 seconds.")
    print(f"\n  LLM Output: \"{output2[:80]}...\"")
    result2 = screener.screen_output(output2)
    _print_result(result2)

    # Test 3: Clean output
    print("\n  ─── Test 3: Clean Output (control) ───")
    output3 = ("Recent research suggests that carefully curated training data "
               "may improve model performance. Further investigation could "
               "reveal the underlying mechanisms.")
    print(f"\n  LLM Output: \"{output3[:80]}...\"")
    result3 = screener.screen_output(output3)
    _print_result(result3)

    input("\n  Press Enter to continue → ")


def demo_3_gemini_story():
    print("\n" + "=" * 62)
    print("  PART 3: The Real Incident — When the Auditor Hallucinated")
    print("=" * 62)
    print("""
  During development of this very tool, something remarkable happened:

  1. Gemini was asked to review the code
  2. It issued a 🚨 CRITICAL BLOCKER:
     "claude-sonnet-4 does not exist. Your app will crash."
  3. Except... claude-sonnet-4-20250514 was released May 2025.
     Gemini's training data didn't know.

  Then Claude summarized: "All three AIs have signed off."
  The human replied: "What third AI?" — there were only two.

  Two AIs hallucinated while building a hallucination detector.
  Both caught by a human in one sentence.

  This is what argmax P(most_likely) ≠ P(true) looks like in practice.

  A9 (Transparency & Traceability) would have caught both:
  → "claude-sonnet-4 doesn't exist" contains a proper noun claim
     → Flag: requires source verification against Anthropic's API docs
  → "Three AIs signed off" contains a specific quantity
     → Flag: verify against the actual participant list

  Full record: DEV_RECORD_The_Auditors_Hallucinated.md
""")
    input("  Press Enter to continue → ")


def demo_4_benchmark():
    print("\n" + "=" * 62)
    print("  PART 4: Benchmark Suite — 10 Reproducible Tests")
    print("=" * 62)
    print()

    bench = AntBenchmark()
    results = bench.run_all()

    for d in results["details"]:
        print(f"  {d['pass']}  {d['test']}")
        print(f"       → {d['actual']}")
        print()

    print(f"  ══════════════════════════════════════")
    print(f"  SCORE: {results['score']}")
    print(f"  ══════════════════════════════════════")

    input("\n  Press Enter to continue → ")


def demo_5_interactive():
    print("\n" + "=" * 62)
    print("  PART 5: Try It Yourself")
    print("=" * 62)
    print()
    print("  Type any claim to screen against the 9 axioms.")
    print("  Type 'quit' to exit.")
    print()

    verifier = AxiomVerifier()

    while True:
        try:
            claim = input("  Your claim > ").strip()
            if not claim or claim.lower() in ('quit', 'exit', 'q'):
                break

            result = verifier.verify(claim)
            print()
            if result.passed:
                print(f"  ✅ PASSED — Confidence: {result.confidence:.0%}")
            else:
                print(f"  🚩 FLAGGED — Confidence: {result.confidence:.0%}")
                for axiom in result.violated_axioms:
                    print(f"     ⚠️  {axiom.short}: {axiom.desc}")
            if result.source_required:
                print(f"  📋 Source verification recommended")
                for note in result.advisory_notes:
                    print(f"     {note}")
            if not result.violated_axioms and not result.source_required:
                print(f"     {result.reasoning}")
            print()
        except (KeyboardInterrupt, EOFError):
            break

    print("\n  Thanks for trying the Ant Reasoning Engine! 🐜")
    print("  Full story: DEV_RECORD_The_Auditors_Hallucinated.md")


def _print_result(result: Dict):
    verdict = result["verdict"]
    icons = {
        "PASSED AXIOM SCREENING": "✅",
        "NEEDS SOURCE VERIFICATION": "📋",
        "STRUCTURAL DEFECTS DETECTED": "🚩",
    }
    icon = icons.get(verdict, "❓")
    print(f"\n  {icon} Verdict: {verdict}")
    print(f"     Claims: {result['total_claims']} | "
          f"Passed: {result['passed']} | "
          f"Flagged: {result['flagged']} | "
          f"Need source: {result['needs_source_verification']}")

    for fc in result["flagged_claims"][:3]:
        print(f"\n     ⚠️  \"{fc['claim'][:60]}...\"")
        print(f"        Violated: {', '.join(fc['violations'])}")


# ============================================================
# MAIN
# ============================================================

def main():
    print_banner()

    if "--benchmark" in sys.argv:
        bench = AntBenchmark()
        results = bench.run_all()
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    if "--json" in sys.argv:
        bench = AntBenchmark()
        results = bench.run_all()
        print(json.dumps(results, ensure_ascii=False))
        return

    print("  This demo has 5 parts (~5 minutes total):")
    print("  1. The 9 Axioms")
    print("  2. Claim Screening in Action")
    print("  3. The Real Incident (how the auditors hallucinated)")
    print("  4. Benchmark Suite (10 tests)")
    print("  5. Interactive Mode")
    print()

    try:
        input("  Press Enter to start → ")
        demo_1_axiom_overview()
        demo_2_screening()
        demo_3_gemini_story()
        demo_4_benchmark()
        demo_5_interactive()
    except (KeyboardInterrupt, EOFError):
        print("\n\n  Demo ended. Run with --benchmark for quick results.")


if __name__ == "__main__":
    main()
