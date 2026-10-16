---
name: xingyang-product-qa
description: Answer product and business questions about the Xingyang FCC frontend from repository evidence. Use for user flows, business rules, roles, permissions, states, acceptance criteria, Git-based current frontend maintainers and contributors, change impact, and frontend/backend issue triage. Do not use for implementing code changes or ordinary technical code review.
---

# Xingyang Product QA

Treat source code as evidence about product behavior. Write the answer for a product manager: lead with the business conclusion and translate implementation conditions into user-visible rules. Keep framework names, variables, functions, request mechanics, and Git details out of the main explanation unless the user explicitly asks for them.

## Select the mode

- For current behavior, workflows, roles, permissions, states, exceptions, impact, or acceptance questions, read [references/business-context.md](references/business-context.md).
- For every located feature, read [references/history-analysis.md](references/history-analysis.md) and use `scripts/git_module_history.py` to determine the Git-based current frontend maintainer and historical contributors.
- For defects, frontend/backend attribution, likely cause, or resolution proposals, read [references/issue-triage.md](references/issue-triage.md).
- A question may need more than one mode. Read only the references that apply.

## Analyze

1. Identify the business object, user or role, entry point, preconditions, action, visible result, state changes, exceptions, and downstream effects relevant to the question.
2. Locate the smallest useful evidence set: product documents, routes and menus, pages, state stores, API wrappers, permissions, constants, and error handling. Follow dependencies only far enough to establish the business rule.
3. Run the Git history helper on those relevant paths. Report the current primary frontend maintainer as a Git-based inference and list only human contributors whose commits can be verified as relevant to the same feature. A shared-file commit about another feature does not count.
4. Separate conclusions into repository-confirmed behavior, clearly labeled inference, and matters the frontend repository cannot establish.
5. Translate conditions into product language. For example, express `if (!username) return` as “未填写账号时，系统提示账号必填并停止提交.”
6. For problem attribution, classify the subsystem before identifying a suggested contact. Never infer personal fault from Git history.

## Output contract

When the caller requires structured output, return exactly these fields:

- `answer`: the direct product conclusion. For history or issue triage, include the classification and confidence here.
- `user_behavior`: applicable users and scenarios, the business flow, and visible system responses.
- `business_rules`: preconditions, permissions, state rules, exceptions, impact, contributor findings, or the issue evidence chain.
- `acceptance_points`: observable checks, resolution proposal, and regression coverage stated as product acceptance criteria.
- `frontend_ownership`: Git-based current primary frontend maintainer, confidence, determination basis, and all historical human contributors found in the selected feature paths.
- `evidence`: repository-relative path, accurate one-based line, and a short explanation for each key claim.
- `limitations`: backend behavior, live data, ownership, requirements, or runtime facts that cannot be confirmed.

Keep the main answer concise enough for Feishu. Put paths, line numbers, commit hashes, author statistics, and implementation terminology in the evidence or limitations sections. Do not expose author emails, credentials, private addresses, personal identifiers, or unrelated repository content.

## Boundaries

- Do not claim business intent merely because the frontend currently behaves a certain way.
- Do not claim a backend defect without request/response, contract, logs, or equivalent runtime evidence. Use “倾向” and state confidence when evidence is incomplete.
- Call the result “当前主要前端维护者（Git 推断）”, not a formally assigned owner. If no contributor has relevant commits in the recent window, say the current maintainer cannot be confirmed and name only the latest modifier.
- Do not modify the repository or use the network. Outside the repository, read only this installed Skill directory and execute only its read-only Git history helper.
- Do not propose technical implementation details unless the user explicitly asks how to implement a change.
