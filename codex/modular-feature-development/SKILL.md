---
name: modular-feature-development
description: Project-aware modular feature development workflow. Use when Codex is asked to add, implement, build, or extend a new feature that should live as a coherent module with well-sized files/components, project-aligned data flow, minimal integration changes, clarified API assumptions, and strict data access without excessive fallback defaults.
---

# Modular Feature Development

## Core Rule

Build the feature as one coherent module that fits the existing project. First understand the repository's architecture, naming, state/data patterns, routing, API conventions, test style, and module boundaries. Then design the smallest feature-specific structure that can be maintained without becoming either a single large file or a scattered collection of tiny files.

If the `coding` skill is also active or applicable, follow it for the general engineering workflow. This skill adds stricter guidance for feature-module structure, component boundaries, data flow, and API assumptions.

## Workflow

1. Inspect the existing project before proposing implementation.
   - Identify framework, language, routing, state management, API clients, generated types, validation style, tests, and nearby feature modules.
   - Prefer local patterns over generic architecture advice.
   - Locate the nearest comparable feature and use it as the main precedent unless it is clearly legacy or inconsistent.

2. Clarify unclear requirements before finalizing the solution.
   - Ask when API contracts, required fields, permissions, navigation entry points, error behavior, persistence rules, or cross-module ownership are unclear.
   - Offer a concrete choice when helpful: "provide API docs" or "use temporary mock data behind a narrow adapter".
   - Do not invent backend contracts as final behavior. If mock data is used, isolate it so replacing it with real API data is a small change.

3. Establish the module shape before editing broadly.
   - Define the feature module's root folder and public entry points.
   - Keep cross-module imports narrow and intentional.
   - Avoid new global state, new service layers, or new architectural systems unless the project already uses that pattern or the feature cannot work otherwise.

4. Implement with minimal integration change.
   - Add only the route, registry entry, provider wiring, API call, store slice, or export needed to connect the module.
   - Reuse existing API clients, state stores, validation helpers, hooks/composables, UI primitives, and error handling conventions.
   - Keep feature-specific behavior inside the feature module unless shared usage already exists.

5. Verify with focused tests or checks appropriate to the project.
   - Prefer targeted tests for the new module and any touched integration boundary.
   - Run the narrowest reliable build, typecheck, lint, or test command available.

## Module And File Boundaries

Use cohesion and change reasons as the main split criteria, following common large-codebase practice:

- Split by responsibility that changes independently: view/container, UI subcomponent, data adapter, domain transform, validation, constants/types, tests.
- Keep files large enough to be meaningful. Avoid extracting one-off wrappers, single-use markup fragments, or tiny helpers unless they clarify a real boundary.
- Keep files small enough to review. When a file mixes fetching, transformation, layout, form state, and rendering, split it.
- Prefer a compact module. As a default target, aim for roughly 4-8 production files for a normal feature module. Exceed that only when the feature has genuinely separate screens, forms, data adapters, or complex domain logic.
- Do not create broad folders like `components/`, `utils/`, or `hooks/` just to hold one trivial file. Create folders when there are multiple related files or the project already uses that structure.
- Make the module's external surface small: one route/screen export, one registration object, or one index file only when the repo convention supports it.

## Component Splitting

Use component extraction when it improves ownership, testing, or readability:

- Extract reusable UI only after a second use case exists or the abstraction is clearly a domain concept.
- Extract complex sections when they have independent state, validation, loading behavior, or a distinct domain role.
- Keep parent components responsible for orchestration and child components responsible for display or local interaction.
- Avoid prop drilling across many levels by following the existing project pattern: colocated hooks/composables, context/provider, store, route loader, query cache, or explicit props.
- Do not split purely by visual tags such as header/body/footer unless the resulting components carry meaningful behavior or the project convention requires it.

## Data Flow

When data crosses module boundaries, integrate into the existing flow instead of creating a parallel system:

- Follow the current source of truth: route loader, query library, store, service client, server action, controller, repository, or backend endpoint.
- Keep transformations close to the boundary where raw data enters the feature.
- Reuse existing types and schemas. If they are missing, define narrow feature-local types that mirror the actual contract and are easy to replace with generated/shared types later.
- Avoid duplicating canonical state in the feature module. Derive view state from existing state when possible.
- Add cross-module exports only when another module truly needs them. Do not expose internals speculatively.

## Strict Data Access

Do not hide contract problems with excessive fallbacks:

- Read required fields strictly. Avoid chains like `value || fallback || ""` for required backend data.
- Use defaults only for genuine optional UI concerns, such as an omitted filter label, empty list state, or optional display text.
- If a required field may be absent, surface the mismatch through the project's normal error, validation, or loading/error state instead of silently rendering misleading data.
- Do not normalize unknown backend shapes by guessing. Ask for API docs or mark the mock/assumption explicitly in code comments only where unavoidable.
- Prefer precise null/undefined checks over broad truthiness checks when `0`, `false`, or empty strings are valid values.

## Before Finalizing A Plan

Make sure the plan answers:

- Where does the feature module live, and what existing module does it mirror?
- What files will be created, and why is each split justified?
- Which existing data/API/state path will be reused?
- Which unclear API or product points were clarified, mocked temporarily, or explicitly left as assumptions?
- What strict data assumptions could fail if backend data is wrong?
- What targeted verification will be run?

