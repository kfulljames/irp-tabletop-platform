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

# Default to the cheapest current model for this structured-extraction task.
# Override per-call (the UI exposes a model picker). $1/$5 per M tokens vs Opus $5/$25.
MODEL = "claude-haiku-4-5"

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
    "You review a client's incident-response / business-continuity plan for an EXECUTIVE "
    "tabletop exercise. This kind of plan is a COORDINATION and DECISION document — NOT a "
    "technical runbook. Its job is to ensure that during an incident the team knows: WHO is "
    "responsible and who has decision authority; WHO to contact (internal leaders and external "
    "partners — cyber insurer, breach counsel, forensics/IR firm, PR firm, ransom negotiator, "
    "DR provider, ISP, law enforcement, regulators); and WHAT must be decided and communicated, "
    "by when.\n\n"
    "Technical execution (HOW to eradicate malware, HOW to rebuild a system) is deliberately "
    "DELEGATED to the technical team or external partners and does NOT belong in this plan.\n\n"
    "Understand the document's two parts: the POLICY defines WHEN the plan activates, what "
    "triggers each step, and who decides; the PROCEDURE is essentially a LIST OF CONTACTS "
    "(WHO to call). There is no technical procedure to evaluate — do not look for one or treat "
    "its absence as a gap.\n\n"
    "Calibrate accordingly:\n"
    "- DO flag: unclear or missing decision authority / role ownership; missing or out-of-date "
    "external contacts (e.g. no PR firm, a former insurer still listed, no ransom negotiator, no "
    "contact path that works if email/systems are down); unclear notification obligations or "
    "timing; no named alternates.\n"
    "- DO NOT flag the absence of step-by-step technical procedures. If a topic is handled by "
    "naming the responsible owner or the external partner to call, that is SUFFICIENT — do not "
    "recommend adding technical detail or 'more thoroughness'.\n\n"
    "Assume the plan may already be approved by a SOC 2 auditor and is a HIGH bar. Be "
    "conservative: raise a gap only when something genuinely needed for executive coordination "
    "is missing or stale. When in doubt, mark the chapter present with severity 'none' rather "
    "than inventing improvements. You only propose findings; a human facilitator approves them."
)


def _client(api_key: Optional[str] = None) -> anthropic.Anthropic:
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("No ANTHROPIC_API_KEY set. Add it in the sidebar or environment.")
    return anthropic.Anthropic(api_key=key)


def analyze_plan(plan_text: str, api_key: Optional[str] = None,
                 model: Optional[str] = None) -> PlanAnalysis:
    """Map the plan onto the baseline and return per-chapter assessments + gaps."""
    client = _client(api_key)
    model = model or MODEL
    # Guard against extremely long plans blowing the request; the IRP/BCP samples fit easily.
    plan_text = plan_text[:120_000]

    prompt = (
        "Best-practice baseline chapters (key | title: what good looks like):\n"
        f"{baseline_for_prompt()}\n\n"
        "Assess the client's plan below against EVERY baseline chapter. For each chapter "
        "return an assessment using the exact chapter_key. Judge ONLY whether the right "
        "owner, contact, decision authority, and notification path are clear — NOT whether "
        "technical procedures are written out. A chapter handled by naming a responsible "
        "owner or external partner counts as present (severity 'none'). Only set present=false "
        "or raise a gap when the coordination/contact/decision content is genuinely missing "
        "or out of date.\n\n"
        "The client's plan may span several documents (e.g. a policy and a procedure, or an "
        "IRP and a BCP), shown below with '=== DOCUMENT: … ===' headers. Treat them together "
        "as one corpus — a topic covered in any document counts as covered.\n\n"
        "=== CLIENT PLAN START ===\n"
        f"{plan_text}\n"
        "=== CLIENT PLAN END ==="
    )

    response = client.messages.parse(
        model=model,
        max_tokens=16000,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        output_format=PlanAnalysis,
    )
    result = response.parsed_output
    if result is None:
        raise RuntimeError("The model did not return a structured result. Try again.")
    return result


CLOSING_SYSTEM = (
    "You write the closing notes for a SOC 2-grade incident-response tabletop evidence report. "
    "Produce a clear, factual, neutral narrative (~150-250 words) of how the exercise unfolded: "
    "what happened, when it was first reported, when it was resolved, the key decisions made, who "
    "was contacted, the business impact, and the resolution. Use only the facts provided — do not "
    "invent details. Write in past tense, third person. This is a draft a human facilitator will "
    "review and approve."
)


def closing_notes(context_text: str, api_key: Optional[str] = None,
                  model: Optional[str] = None) -> str:
    """Draft the incident closing-notes narrative from the assembled run context (B15, suggest-only)."""
    client = _client(api_key)
    model = model or MODEL
    response = client.messages.create(
        model=model,
        max_tokens=1200,
        system=CLOSING_SYSTEM,
        messages=[{"role": "user", "content":
                   "Write the closing notes from this exercise record:\n\n" + context_text[:60_000]}],
    )
    parts = [b.text for b in response.content if getattr(b, "type", "") == "text"]
    return "\n".join(parts).strip()


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
