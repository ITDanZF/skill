---
name: coding
description: Tiered engineering workflow for code writing, modification, refactoring, debugging, testing, and review. Use when Codex is asked to touch code and should choose between a lightweight chat-based analysis for simple changes and a full Chinese Markdown analysis report for complex or high-risk changes, enforce confirmed contracts without unapproved fallbacks or excessive defensive programming, clarify ambiguity with explicit chat questions and selectable options, respect user requests to skip the heavy workflow, use stable report-path output with best-effort VS Code opening, and use fast targeted verification instead of always running expensive full builds.
---

# Coding

Use this skill for code tasks that need practical analysis before implementation.

## Required Contract

- Choose the workflow weight based on task complexity and user intent.
- For simple, low-risk changes, give concise Chinese analysis and modification advice directly in the conversation, then wait for user confirmation before editing.
- For complex, broad, risky, architectural, ambiguous, or user-requested analysis tasks, generate a Chinese Markdown analysis report using `scripts/create_analysis_doc.py`.
- Always report the generated Markdown file path in the conversation. Treat the path as the stable preview channel.
- Opening the Markdown in VS Code is best-effort only. If VS Code opening fails, continue by giving the report path and asking whether to retry opening it.
- Any required user confirmation must also be asked in the conversation. A Markdown report can record the question, but it cannot replace a chat confirmation.
- Ask confirmation questions in a Cursor-like format: one clear question with 2-4 concrete options and a short explanation of each option's impact.
- If the user explicitly asks to skip the heavy workflow, skip it unless the request involves destructive actions, security/privacy risk, data loss, production migration, or unclear acceptance criteria.
- Ask the user before recommending or implementing when task boundaries, acceptance criteria, fallback behavior, affected users, data contracts, or risk tolerance are unclear.
- Never add blind fallback behavior. Any fallback, retry, default value, compatibility shim, silent ignore, or graceful degradation must be explicitly justified and approved by the user.
- Treat every user-confirmed or authoritative contract detail—including a field name, nested path, type, status, value source, API behavior, or acceptance rule—as the sole source of truth for the requested change. Do not retain, prepend, append, or invent alternate sources unless the user explicitly approves compatibility behavior.
- When a confirmed value is absent or malformed, expose the contract violation through the module's normal validation or error path. Do not replace it with another field, a derived value, a plausible default, silent coercion, an empty collection, or a swallowed error merely to keep execution looking successful.
- Do not broaden a field-mapping change into adjacent mappings, refactors, compatibility work, tests of unrelated behavior, or policy changes. If another field appears questionable, report it separately and wait for authorization before changing it.
- Prefer reasonable local module conventions. If the existing convention is harmful, inconsistent, or blocks the task, explain the issue and ask the user before departing from it.
- When multiple viable options exist, present them with tradeoffs and let the user choose.

## Confirmed Contracts: Mandatory No-Fallback Rule

This section is mandatory for every code-writing, modification, debugging, refactoring, and review task handled by this skill.

1. Identify which requirements and data-contract details are confirmed by the user, an authoritative schema, or an explicit payload supplied for the task.
2. Implement confirmed details exactly and only within the authorized scope. If the contract says `result.smoke.counts`, read `result.smoke.counts`; do not also read `smokeCounts`, `smoke.count`, or another historical guess.
3. Do not disguise missing or invalid confirmed data with defensive fallback code. Prefer a visible failure, validation result, or existing explicit error path so contract regressions remain diagnosable.
4. If backward compatibility, a default, graceful degradation, retry, alternate source, derived substitute, or silent tolerance may be necessary, stop and obtain the user's explicit approval before adding it.
5. When editing an existing fallback chain for a confirmed field, replace the relevant chain with the confirmed source instead of inserting the source into the chain. Preserve unrelated behavior outside the requested scope.
6. Before finishing, inspect the diff and verify that no unapproved fallback or adjacent change was introduced. State any remaining compatibility consequence plainly.

Safe access syntax such as optional chaining is not itself a fallback, but it must not convert a broken confirmed contract into apparently valid business data. Type conversion is allowed only when required by the confirmed contract or existing interface and must not select an alternate source.

## Workflow Selection

1. Read repository instructions first: `AGENTS.md`, project docs, package scripts, test setup, and nearby implementation patterns.
2. Read `references/coding-workflow.md` before planning or editing code.
3. Classify the task as lightweight or heavy.
4. Use lightweight chat confirmation for simple, localized, low-risk changes.
5. Use the full Markdown report for complex or high-risk changes, or when the user asks for a formal analysis document.
6. When a report is generated, always paste its path in the conversation and state whether VS Code opening succeeded, failed, or was skipped.
7. When confirmation is needed, ask it in the conversation with selectable options, even if the same question is also written in the Markdown report.
8. After user confirmation, implement only the approved change.
9. Verify with the fastest reliable targeted check. Do not run full `npm run build` or equivalent for every change by default, especially in large projects where a full build is slow or expensive. Treat full build as an explicit verification choice that needs a clear reason.

## Lightweight Flow

For simple changes, respond in the conversation with:

- 简要分析
- 修改建议
- 涉及文件
- 风险与验证方式
- 一个明确确认问题和 2-4 个选项

Then wait for the user's confirmation before editing unless the user has already clearly authorized direct implementation.

## Heavy Flow

Use the full report when the task has broad impact, multiple files/modules, architecture decisions, public API/data contract changes, fallback/error policy decisions, unclear requirements, or meaningful risk.

The report must be mirrored by chat questions for any decision that blocks implementation. The report path must always be shown in chat.

## Verification

Prefer quick checks first:

- Typecheck or lint only for touched files when available.
- Run focused unit tests for affected modules.
- Use existing narrow test commands or test filters.
- Inspect diffs and affected call sites.
- For UI changes, use targeted render/smoke checks or screenshots when useful.
- Run full build only when the change touches build config, shared types, routing, bundling, dependency versions, release-critical paths, or when targeted checks cannot provide enough confidence.
- For large frontend projects, avoid using `npm run build` as the routine final check. Prefer a verification budget: touched-file lint/typecheck, focused tests, local render smoke checks, or screenshot checks first; run the full build only after justifying why narrower checks are insufficient or when the user explicitly requests it.

## Resources

- `references/coding-workflow.md`: detailed workflow selection, ambiguity gate, chat option format, report template, approval flow, stable report preview policy, and verification policy.
- `references/standards.md`: personal coding defaults and review criteria.
- `scripts/create_analysis_doc.py`: create a 3-day temporary Chinese Markdown analysis file, print the report path, and best-effort open it with VS Code when needed.
