# Development history analysis

Git history answers who changed code, not who owns the product requirement or caused a defect. Run this analysis for every located feature, using only the files that implement that feature.

## Workflow

1. Locate the routes, pages, components, stores, API wrappers, constants, and product documents that belong to the feature.
2. Use the smallest relevant path set. Avoid repository-wide author rankings when the question concerns one module.
3. Inspect recent history and the last relevant commit. Use `git show` when a commit subject alone cannot establish what changed.
4. Separate these concepts in the answer:
   - Historical contributors: people with relevant commits in the selected paths.
   - Recently active contributors: people with relevant commits during the selected time window.
   - Last modifier: author of the latest relevant non-merge commit.
   - Current primary frontend maintainer: a Git-based inference from recent, repeated, relevant changes.
   - Suggested technical contact: a cautious suggestion based on the same evidence.
5. State the selected paths and time window so the conclusion can be reviewed.

## Current maintainer decision

- Use a 180-day recent window unless the repository history gives a clear reason to use another period.
- Prefer the contributor with the strongest combination of recent relevant commits, latest relevant modification, and repeated work across the selected feature paths.
- Inspect commit subjects or diffs when needed to exclude formatting, bulk refactors, merges, generated changes, and incidental edits.
- For shared routes, stores, API wrappers, and common components, inspect the relevant commit diff or changed symbols. Do not count a person when their commit touched the shared file only for another feature.
- If two or more contributors are similarly active, list them together rather than forcing one person.
- If nobody has a relevant commit in the recent window, write “无法从 Git 确认当前负责人” and identify only the latest historical modifier.
- List every human contributor with at least one verified feature-relevant commit. The helper output is a candidate set; exclude contributors whose selected-path commits only concern unrelated code in shared files.
- Include the relevant date and abbreviated commit when they help support the determination. Never expose author emails.

## Read-only helper

Use the helper after locating the relevant feature paths:

```powershell
python C:\Users\Administrator\.codex-feishu-product\skills\xingyang-product-qa\scripts\git_module_history.py --repo . --path src/views/login --path src/api/user.js --since-days 180 --limit 50
```

The helper groups aliases only when Git records have the same normalized email internally. It never emits email addresses. Review the returned commits before turning statistics into a suggested contact.

You may also use read-only commands such as `git log`, `git show`, and `git blame` scoped to the relevant paths. Do not change branches, restore files, fetch, pull, or write Git metadata.

## Interpretation rules

- Commit count is evidence of participation, not ownership, expertise, availability, or fault.
- Prefer a recent contributor with several meaningful commits over a person whose only change was formatting, generated files, dependency updates, merges, or bulk refactoring.
- Exclude obvious automated authors. Disclose that automated commits were excluded when this affects the count.
- Treat different names as aliases only when Git metadata gives a strong identity match. Otherwise keep them separate and note that author identities may be inconsistent.
- Display names only. Never display author emails.
- If evidence is thin or several people are similarly active, present multiple suggested contacts and explain the basis instead of naming one owner.
- Write “当前主要前端维护者（Git 推断）” and include confidence. This is a practical maintenance inference, not proof of formal assignment.

## Product-manager wording

Lead with the module and business change, then give the people and dates. A useful answer distinguishes:

- 最近一次相关修改的日期、变更主题和影响范围；
- 历史参与者与近期开发表现；
- 当前主要前端维护者（Git 推断）、可信度及判定依据；
- 全部历史参与开发者及各自最近一次相关修改。

Put commit hashes, author counts, selected paths, and other Git mechanics in `evidence` or `limitations`.
