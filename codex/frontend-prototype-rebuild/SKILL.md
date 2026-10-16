---
name: frontend-prototype-rebuild
description: Frontend prototype screenshot to static page implementation workflow. Use when the user provides or references a page image, screenshot, mockup, or prototype and explicitly asks Codex to generate, recreate, restore, convert, or implement the related frontend page. Focus on extracting layout, visible elements, implied interactions, local theme alignment, efficient production-style code, and CSS-first rendering without unnecessary JavaScript.
---

# Frontend Prototype Rebuild

## Activation

Use this skill only when both are true:

- The user provides or clearly references a page image, screenshot, mockup, or prototype.
- The user explicitly asks to generate, recreate, convert, implement, or restore the related frontend page.

If the user only asks to review or describe the image, do not implement code unless asked.

## Workflow

1. Inspect the prototype image first.
   - Identify the page type, viewport, main layout regions, alignment grid, spacing rhythm, typography scale, density, and visual hierarchy.
   - Extract visible elements: navigation, forms, buttons, tables, cards, lists, tabs, filters, media, empty states, status indicators, and icons.
   - Infer likely interactions only from visible affordances, such as hoverable actions, selected tabs, dropdowns, toggles, filters, modals, pagination, or input states.
   - Treat ambiguous content as static display unless the user asks for functional behavior.

2. Inspect the local frontend project before coding.
   - Identify framework, routing, component conventions, styling method, theme tokens, CSS variables, Tailwind config, design system, icon library, and existing page patterns.
   - Prefer existing components, spacing scales, typography utilities, color tokens, and layout primitives.
   - Match the closest existing page or component pattern when it does not conflict with the prototype.

3. Plan the implementation surface.
   - Choose the smallest file/component structure that fits the project conventions.
   - Keep static prototype data local and obvious unless the project has an established fixture or mock-data pattern.
   - Do not introduce new state management, component libraries, CSS frameworks, or global theme changes for a static page recreation.

4. Implement the page.
   - Recreate the layout and visual structure with semantic HTML and project-native components.
   - Use CSS for layout, sizing, spacing, responsive behavior, hover/focus states, transitions, layering, and simple visual states.
   - Use JavaScript only for behavior that genuinely requires state or event handling.
   - Keep code efficient, readable, and production-style: clear component boundaries, minimal duplication, no one-off abstractions that make the page harder to scan.

5. Verify the result visually.
   - Run the relevant local dev server or static preview when needed.
   - Compare the rendered page against the prototype at the target viewport and at least one responsive breakpoint when applicable.
   - Fix obvious mismatches in spacing, hierarchy, color, sizing, and overflow before finishing.

## Theme And Color Rules

Use the local project theme as the source of truth:

- Prefer project tokens, CSS variables, Tailwind theme values, design-system props, and existing component variants.
- If the project has a matching semantic token, use it even if the screenshot color is slightly different.
- If the project has no suitable token, use the screenshot color directly and keep it local to the recreated page/component.
- Do not modify global theme files just to match one screenshot unless the user explicitly asks.
- Preserve brand consistency over pixel-perfect color copying when local theme intent is clear.

## Layout And Element Extraction

Capture these details before writing code:

- Page shell: header, sidebar, footer, content width, scroll regions, sticky areas.
- Grid: columns, rows, gutters, card/table/list rhythm, breakpoint behavior.
- Typography: heading/body/caption scale, weight, line height, truncation.
- Controls: button sizes, input heights, selected/disabled/loading states, icons, badges.
- Content fidelity: labels, visible copy, numbers, dates, avatars, image placeholders, and empty states.
- Layering: shadows, borders, dividers, overlays, popovers, and z-index relationships.

Do not overuse absolute positioning. Prefer flex, grid, intrinsic sizing, aspect-ratio, min/max constraints, and container-based responsive rules. Use absolute positioning only for overlays, badges, decorative anchors, or screenshot-specific layering that cannot be expressed cleanly otherwise.

## Interaction Guidance

For static page recreation, implement interactions only to the level implied by the request:

- Always include accessible hover, focus, active, selected, disabled, and loading visuals when the prototype implies them.
- Implement simple open/close, tab switching, selection, or filtering only when the user asks for interactive behavior or the prototype clearly depends on it.
- Prefer CSS selectors and native HTML behavior for simple interactions where practical.
- Avoid JavaScript used only to patch layout, spacing, truncation, colors, or responsive behavior. Solve those with CSS.

## Code Quality Rules

Follow large-codebase frontend practice:

- Keep components cohesive and named by domain or visible role, not by vague visual fragments.
- Avoid splitting the page into many tiny components unless there are real independent responsibilities.
- Keep static sample data typed when the project uses TypeScript.
- Use existing icon libraries instead of hand-coded SVGs when available.
- Add alt text, labels, keyboard focus styles, and semantic structure where appropriate.
- Avoid hardcoded magic numbers when the project has spacing, sizing, or color tokens.
- Do not add dependencies for effects that CSS or existing utilities can handle.

## Completion Checklist

Before final response, confirm:

- The image was inspected for layout, elements, theme, and implied interactions.
- Existing project theme and frontend conventions were checked.
- Colors prefer local tokens, with screenshot colors used only for missing tokens.
- CSS handles visual layout and states wherever possible.
- The rendered page was previewed or the reason it could not be previewed is stated.
