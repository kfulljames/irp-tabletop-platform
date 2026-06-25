"""Anthropic-powered AI gap analysis (decisions Q8, Q26, B15).

Suggest-only: the model proposes how each baseline chapter is covered and where the
plan is missing/stale. A human (facilitator) reviews and accepts in the UI. Runs on the
Anthropic API (no training on customer data) — the answer to the "don't use public
ChatGPT" concern in 04-REFERENCE-NOTES.
"""
import os
from typing import List, Optional, Literal

import anthropic
from pydantic import BaseModel, Field

from .baseline import BASELINE_CHAPTERS, baseline_for_prompt

MODEL = "claude-opus-4-8"

Severity = Literal["none", "low", "medium", "high"]


class ChapterAssessment(BaseModel):
    chapter_key: str = Field(description="The baseline chapter key being assessed.")
    present: bool = Field(description="Whether the plan meaningfully covers this chapter.")
    coverage_summary: str = Field(description="1-2 sentences on how the plan covers it.")
    original_excerpt: str = Field(
        description="A short quote from the client's plan for this chapter, or empty string if absent."
    )
    gap: Optional[str] = Field(
        default=None,
        description="What is missing, weak, or out of date — or null if the chapter is solid.",
    )
    recommended_change: Optional[str] = Field(
        default=None, description="Concrete recommended change to close the gap, or null."
    )
    severity: Severity = Field(description="Severity of the gap; 'none' if no gap.")


class PlanAnalysis(BaseModel):
    assessments: List[ChapterAssessment]
    overall_notes: str = Field(description="Brief overall read of the plan's readiness.")


SYSTEM = (
    "You are an incident-response readiness analyst. You compare a client's incident "
    "response / business continuity plan against a best-practice baseline and identify "
    "gaps. Be specific and practical. Flag missing chapters, stale details (e.g. a former "
    "insurer or PR firm still listed, no ransom negotiator, no out-of-band contact path), "
    "and vague responsibilities. You only propose findings; a human facilitator approves them."
)


def _client(api_key: Optional[str] = None) -> anthropic.Anthropic:
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("No ANTHROPIC_API_KEY set. Add it in the sidebar or environment.")
    return anthropic.Anthropic(api_key=key)


def analyze_plan(plan_text: str, api_key: Optional[str] = None) -> PlanAnalysis:
    """Map the plan onto the baseline and return per-chapter assessments + gaps."""
    client = _client(api_key)
    # Guard against extremely long plans blowing the request; the IRP/BCP samples fit easily.
    plan_text = plan_text[:120_000]

    prompt = (
        "Best-practice baseline chapters (key | title: what good looks like):\n"
        f"{baseline_for_prompt()}\n\n"
        "Assess the client's plan below against EVERY baseline chapter. For each chapter "
        "return an assessment using the exact chapter_key. If a chapter is absent, set "
        "present=false, severity appropriately, and give a recommended_change.\n\n"
        "=== CLIENT PLAN START ===\n"
        f"{plan_text}\n"
        "=== CLIENT PLAN END ==="
    )

    response = client.messages.parse(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        output_format=PlanAnalysis,
    )
    result = response.parsed_output
    if result is None:
        raise RuntimeError("The model did not return a structured result. Try again.")
    return result


def analysis_to_db_rows(analysis: PlanAnalysis):
    """Split a PlanAnalysis into plan_section rows and gap_finding rows for storage."""
    valid_keys = {k for k, _, _ in BASELINE_CHAPTERS}
    titles = {k: t for k, t, _ in BASELINE_CHAPTERS}

    sections, gaps = [], []
    for a in analysis.assessments:
        if a.chapter_key not in valid_keys:
            continue
        sections.append({
            "baseline_key": a.chapter_key,
            "title": titles[a.chapter_key],
            "original_text": a.original_excerpt or "",
        })
        if a.gap and a.severity != "none":
            gaps.append({
                "baseline_key": a.chapter_key,
                "title": f"{titles[a.chapter_key]}: {a.gap[:80]}",
                "description": a.gap,
                "recommended_change": a.recommended_change or "",
                "severity": a.severity,
            })
    return sections, gaps
