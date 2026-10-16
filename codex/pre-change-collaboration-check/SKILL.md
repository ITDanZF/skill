---
name: pre-change-collaboration-check
description: Before modifying existing code in a Git repository, scan the planned files or line ranges for overlapping working-tree changes and relevant contributor history, then report possible affected contributors and each person's latest relevant change time. Use for code-editing tasks in shared repositories; do not use for new standalone files with no repository history or for read-only review tasks.
---

# Pre-change collaboration check

Run this check before the first edit, not after implementation has begun.

## Establish the scan scope

Infer the smallest credible change surface from the request and read-only code inspection. Prefer exact line ranges for localized edits. Use whole files when the change is structural or the affected lines are not yet known. Include directly coupled files only when imports, call sites, schemas, generated interfaces, or tests make them part of the planned change.

Do not edit files while establishing this scope. If implementation later expands to another existing file or line range, scan the added scope before editing it.

## Run the scan

Resolve `scripts/scan_collaboration.py` relative to this `SKILL.md`, then run it from any available Python 3 interpreter. Pass the repository root and at least one target:

```text
python <skill-dir>/scripts/scan_collaboration.py --repo <repo-root> --path src/module.py --line-range src/other.py:40:95
```

- Use `--path` once per whole-file target.
- Use `--line-range PATH:START:END` once per localized target. Paths may be absolute or repository-relative.
- Add `--self-email` or `--self-name` when the acting user's Git identity is missing or differs from the repository configuration.
- Use `--format json` only when machine-readable output is useful.

The helper is read-only. It examines the local working tree, local `HEAD`, path history, and line blame. It does not fetch remote refs.

## Report before editing

Share a concise pre-change report in the user's language before making modifications. Include:

- the repository, local `HEAD`, scan time, and exact paths or ranges scanned;
- any staged, unstaged, or untracked overlap in the target scope;
- each possible affected contributor's Git name/email, latest relevant authored time, short commit, and the file or range connecting them to the planned change;
- a confidence distinction: line-blame evidence is localized, while whole-file history is broader;
- the limitation that Git history cannot prove ownership, employment, or who is editing in real time. Uncommitted changes cannot be attributed reliably from local Git alone.

Exclude the configured acting user from the possible-other-contributors table. If no usable acting identity exists, say that self-filtering was unavailable and present all relevant authors as candidates.

Historical overlap alone does not block an authorized edit. When existing uncommitted changes touch the planned scope, inspect the diff and preserve it. If the intended edit would overwrite or ambiguously conflict with that work, pause and ask the user how to proceed. Otherwise, continue after the report.
