# Product and business analysis

## Evidence order

Use the most direct evidence available, normally in this order:

1. `docs/07-product/` for product inventories, known questions, menus, permissions, and product terminology.
2. Routes and menu configuration for discoverability, navigation, and access boundaries.
3. Views and components for user actions, display conditions, validation, feedback, and local state changes.
4. Stores, constants, and dictionaries for shared states and business labels.
5. API wrappers and `docs/04-api/` for the frontend contract and response handling. An API document does not prove live backend behavior.

## Product framing

Describe findings through these concepts when relevant:

- User and role: who can see or perform the action.
- Scenario and entry: where the user starts and what must already be true.
- Workflow: user action, system feedback, state transition, and completion outcome.
- Business rule: visibility, eligibility, permissions, ordering, limits, and mutual exclusion.
- Exception: validation failure, API failure, missing data, timeout, unavailable device, or permission denial.
- Impact: affected roles, pages, workflows, data, and compatibility expectations.
- Acceptance: observable behavior for normal, boundary, permission, and failure cases.

Do not lead with files or implementation. Use code only to support a product statement.

## Confidence language

- Use direct language for behavior explicitly enforced in the repository.
- Use “从当前前端实现推断” for conclusions supported indirectly by several artifacts.
- Use “当前前端仓库无法确认” for backend rules, database state, deployment configuration, requirement intent, and live environment behavior.

Do not use a separately maintained ownership knowledge base. Infer frontend maintenance activity only from the current repository's scoped Git history and label it accordingly.
