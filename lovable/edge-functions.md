# Supabase Edge Functions

Two server-side functions hold the AI calls so the Anthropic key never reaches the browser.
A third (optional) handles document text extraction. Create them via Lovable's Supabase
integration, or `supabase functions new <name>`.

## Secret

```
supabase secrets set ANTHROPIC_API_KEY=sk-ant-...
```

In Lovable: add `ANTHROPIC_API_KEY` as an edge-function secret in the Supabase dashboard.

## 1. `analyze-plan`

- **Input:** `{ client_org_id }` (the function reads that client's documents) OR `{ plan_text }`.
- **Work:** concatenate the client's `document.full_text` (prefix each with
  `=== DOCUMENT: <label> ===`), build the user message with the baseline list, call Anthropic
  with the gap-analysis system prompt and forced structured output (see
  `ai-prompts-and-seed.md` §1).
- **Persist:** replace this client's `plan_section` rows; insert `gap_finding` rows where
  `gap` is set and `severity != 'none'` (`status='ai_suggested'`, `source='ai'`).
- **Model:** `claude-haiku-4-5` default; accept an optional `model` override.

Sketch (Deno):

```ts
import Anthropic from "npm:@anthropic-ai/sdk";
const anthropic = new Anthropic({ apiKey: Deno.env.get("ANTHROPIC_API_KEY")! });

const tools = [{
  name: "report_analysis",
  description: "Return the per-chapter plan assessment.",
  input_schema: { /* the JSON shape in ai-prompts-and-seed.md §1 */ }
}];

const msg = await anthropic.messages.create({
  model: model ?? "claude-haiku-4-5",
  max_tokens: 16000,
  system: GAP_SYSTEM_PROMPT,          // verbatim from §1
  tools, tool_choice: { type: "tool", name: "report_analysis" },
  messages: [{ role: "user", content: userMessage }],
});
const analysis = (msg.content.find(b => b.type === "tool_use") as any).input;
// ...write plan_section + gap_finding via the service-role client
```

## 2. `closing-notes`

- **Input:** `{ run_id }`.
- **Work:** assemble the run context (client, scenario, started/resolved/total, overview,
  impact, summary fields, full timeline, validated gaps — same fields as the prototype's
  `report.context_for_ai`), call Anthropic with the closing-notes system prompt (§2), plain text
  out (~150–250 words).
- **Persist:** save to `run.meta.closing_notes`. The facilitator edits/approves in the UI.

## 3. `extract-text` (optional but recommended)

`pypdf`/`python-docx` don't exist in Lovable. On upload, store the file in Supabase Storage, then
extract text in this function:
- PDF → `unpdf` (`extractText`) or `pdfjs-serverless`.
- DOCX → `mammoth` (`extractRawText`).
- Save the result to `document.full_text`.

v1 fallback if you want to skip this: add a "paste plan text" box and let the facilitator paste
the plan, writing straight to `document.full_text`. The whole AI pipeline runs on text, so
extraction is a convenience, not a blocker.

## Export (Word/JSON)

The prototype built `.docx` with python-docx. In Lovable do it client-side with the `docx` npm
package (mirror the 8 sections: Exec Summary, Debrief, Overview+Impact+Summary, Team, Tasks,
Timeline, Plan-gap punch-list, Confidence vote), and JSON via `JSON.stringify`. Gate both behind
the "Approve report" checkbox (decision B12), exactly as the prototype does.
