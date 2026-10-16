---
name: feature-development
description: Upstream workflow for new feature development. Use when Codex is asked to add, build, implement, or extend product functionality and should first determine whether the task is truly new feature development, ask the user to confirm that classification, decide whether module splitting is needed without over-engineering simple features, then hand off to the coding skill for Chinese analysis, approval, and implementation.
---

# Feature Development

Use this skill before `coding` when a request may be new feature development.

## Required Contract

- First analyze whether the request is new feature development, bug fix, refactor, configuration change, test-only work, or documentation work.
- Before using this skill's full workflow, ask the user to confirm whether the task should be treated as new feature development.
- Do not assume every new feature needs splitting.
- Do not put a growing feature's full UI, state, data access, validation, business logic, and side effects into one page or one component.
- Do not over-split simple features. Splitting must reduce real complexity, isolate responsibility, improve testing, or match existing project architecture.
- After the user confirms this is feature development, continue into the `coding` skill workflow: produce the Chinese analysis report, clarify ambiguity, and wait for user approval before code changes.

## Workflow

1. Read `references/feature-splitting.md`.
2. Classify the task and explain the classification briefly.
3. Ask the user: "我判断这个任务可能属于新功能开发，是否按新功能开发流程处理？"
4. If the user says no, use the more appropriate workflow, normally `coding` for ordinary code changes.
5. If the user says yes, analyze feature scope, module boundaries, split necessity, and candidate structure.
6. Include the feature-development analysis as an upstream section in the Chinese Markdown report required by `coding`.
7. Present multiple structure options when the boundary is not obvious, then wait for user selection or approval.

## Handoff to Coding

When this skill applies, the downstream `coding` analysis report must include:

- Feature classification and user confirmation.
- Whether splitting is needed.
- Why splitting is or is not needed.
- Proposed module boundaries.
- Files likely to be created or modified.
- Risks of under-splitting and over-splitting.