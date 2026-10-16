#!/usr/bin/env python3
"""Read-only Git scan for contributor overlap before editing code."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable


class ScanError(RuntimeError):
    pass


def git(repo: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", "-c", "core.quotepath=false", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "unknown Git error"
        raise ScanError(detail)
    return proc.stdout


def repo_root(candidate: str) -> Path:
    base = Path(candidate).expanduser().resolve()
    if base.is_file():
        base = base.parent
    output = git(base, "rev-parse", "--show-toplevel").strip()
    if not output:
        raise ScanError(f"Not a Git repository: {base}")
    return Path(output).resolve()


def relative_target(root: Path, value: str) -> str:
    candidate = Path(value).expanduser()
    absolute = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        relative = absolute.relative_to(root)
    except ValueError as exc:
        raise ScanError(f"Target is outside the repository: {value}") from exc
    text = relative.as_posix()
    if text in ("", "."):
        raise ScanError("Repository root is too broad; provide specific files or directories")
    return text


@dataclass(frozen=True)
class LineRange:
    path: str
    start: int
    end: int

    @property
    def label(self) -> str:
        return f"{self.path}:{self.start}-{self.end}"


def parse_line_range(root: Path, raw: str) -> LineRange:
    try:
        path_text, start_text, end_text = raw.rsplit(":", 2)
        start, end = int(start_text), int(end_text)
    except (ValueError, TypeError) as exc:
        raise ScanError(f"Invalid line range '{raw}'; expected PATH:START:END") from exc
    if start < 1 or end < start:
        raise ScanError(f"Invalid line range '{raw}'; require 1 <= START <= END")
    return LineRange(relative_target(root, path_text), start, end)


def identity_key(name: str, email: str) -> str:
    normalized_email = email.strip().strip("<>").lower()
    return normalized_email or name.strip().lower()


@dataclass
class Contributor:
    name: str
    email: str
    latest_time: str
    latest_epoch: int
    commit: str
    summary: str
    evidence: set[str] = field(default_factory=set)
    confidence: set[str] = field(default_factory=set)

    def update(
        self,
        *,
        name: str,
        email: str,
        changed_at: str,
        changed_epoch: int,
        commit: str,
        summary: str,
        evidence: str,
        confidence: str,
    ) -> None:
        self.evidence.add(evidence)
        self.confidence.add(confidence)
        if changed_epoch > self.latest_epoch:
            self.name = name
            self.email = email
            self.latest_time = changed_at
            self.latest_epoch = changed_epoch
            self.commit = commit
            self.summary = summary


def add_contributor(
    contributors: dict[str, Contributor],
    *,
    name: str,
    email: str,
    changed_at: str,
    changed_epoch: int,
    commit: str,
    summary: str,
    evidence: str,
    confidence: str,
) -> None:
    key = identity_key(name, email)
    if not key:
        return
    if key not in contributors:
        contributors[key] = Contributor(name, email, changed_at, changed_epoch, commit, summary)
    contributors[key].update(
        name=name,
        email=email,
        changed_at=changed_at,
        changed_epoch=changed_epoch,
        commit=commit,
        summary=summary,
        evidence=evidence,
        confidence=confidence,
    )


def path_history(root: Path, path: str, max_commits: int) -> list[dict[str, str]]:
    fmt = "%x1e%H%x1f%an%x1f%ae%x1f%aI%x1f%at%x1f%s"
    args = ["log", "HEAD", f"--format={fmt}"]
    if (root / path).is_file():
        args.append("--follow")
    if max_commits > 0:
        args.append(f"--max-count={max_commits}")
    args.extend(["--", path])
    output = git(root, *args, check=False)
    records: list[dict[str, str]] = []
    for chunk in output.split("\x1e"):
        chunk = chunk.strip("\r\n")
        if not chunk:
            continue
        fields = chunk.split("\x1f", 5)
        if len(fields) == 6:
            records.append(
                dict(zip(("commit", "name", "email", "time", "epoch", "summary"), fields))
            )
    return records


def tz_iso(epoch: str, offset: str) -> str:
    try:
        utc_value = datetime.fromtimestamp(int(epoch), tz=timezone.utc)
        sign = 1 if offset.startswith("+") else -1
        hours, minutes = int(offset[1:3]), int(offset[3:5])
        tz = timezone(sign * timedelta(hours=hours, minutes=minutes))
        return utc_value.astimezone(tz).isoformat()
    except (ValueError, IndexError, OverflowError):
        return epoch


def blame_history(root: Path, line_range: LineRange) -> list[dict[str, str]]:
    output = git(
        root,
        "blame",
        "--line-porcelain",
        "-L",
        f"{line_range.start},{line_range.end}",
        "HEAD",
        "--",
        line_range.path,
        check=False,
    )
    records: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in output.splitlines():
        if line.startswith("\t"):
            if current.get("commit"):
                current["time"] = tz_iso(
                    current.get("author-time", ""), current.get("author-tz", "+0000")
                )
                records.append(current)
            current = {}
            continue
        pieces = line.split()
        if len(pieces) >= 4 and len(pieces[0]) >= 8 and all(
            char in "0123456789abcdef^" for char in pieces[0].lower()
        ):
            current = {"commit": pieces[0].lstrip("^")}
            continue
        if not current:
            continue
        for key in ("author", "author-mail", "author-time", "author-tz", "summary"):
            prefix = key + " "
            if line.startswith(prefix):
                current[key] = line[len(prefix) :]
                break
    return records


def working_tree_status(root: Path, targets: Iterable[str]) -> list[str]:
    args = ["status", "--short", "--untracked-files=all", "--", *targets]
    return [line for line in git(root, *args).splitlines() if line.strip()]


def markdown_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def build_report(args: argparse.Namespace) -> dict[str, object]:
    if args.max_commits < 0:
        raise ScanError("--max-commits must be 0 or greater")
    root = repo_root(args.repo)
    paths = [relative_target(root, item) for item in args.path]
    ranges = [parse_line_range(root, item) for item in args.line_range]
    if not paths and not ranges:
        raise ScanError("Provide at least one --path or --line-range target")

    target_paths = list(dict.fromkeys(paths + [item.path for item in ranges]))
    head = git(root, "rev-parse", "--short=12", "HEAD", check=False).strip() or "unborn"
    branch = git(root, "branch", "--show-current", check=False).strip() or "detached"
    self_name = args.self_name or git(root, "config", "user.name", check=False).strip()
    self_email = args.self_email or git(root, "config", "user.email", check=False).strip()
    self_keys = {identity_key(self_name, self_email)} if (self_name or self_email) else set()
    if self_name:
        self_keys.add(identity_key(self_name, ""))
    if self_email:
        self_keys.add(identity_key("", self_email))

    contributors: dict[str, Contributor] = {}
    for path in paths:
        for item in path_history(root, path, args.max_commits):
            add_contributor(
                contributors,
                name=item["name"],
                email=item["email"],
                changed_at=item["time"],
                changed_epoch=int(item["epoch"]),
                commit=item["commit"],
                summary=item["summary"],
                evidence=path,
                confidence="whole-file history",
            )

    for item_range in ranges:
        for item in blame_history(root, item_range):
            add_contributor(
                contributors,
                name=item.get("author", "Unknown"),
                email=item.get("author-mail", "").strip("<>"),
                changed_at=item.get("time", ""),
                changed_epoch=int(item.get("author-time", "0") or 0),
                commit=item.get("commit", ""),
                summary=item.get("summary", ""),
                evidence=item_range.label,
                confidence="line blame",
            )

    candidates = []
    for key, person in contributors.items():
        if self_keys and (
            key in self_keys
            or identity_key(person.name, "") in self_keys
            or identity_key("", person.email) in self_keys
        ):
            continue
        candidates.append(
            {
                "name": person.name,
                "email": person.email,
                "latest_relevant_change": person.latest_time,
                "latest_relevant_change_epoch": person.latest_epoch,
                "commit": person.commit[:12],
                "summary": person.summary,
                "evidence": sorted(person.evidence),
                "confidence": sorted(person.confidence),
            }
        )
    candidates.sort(key=lambda item: int(item["latest_relevant_change_epoch"]), reverse=True)

    return {
        "repository": str(root),
        "branch": branch,
        "head": head,
        "scanned_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "acting_identity": {"name": self_name or None, "email": self_email or None},
        "self_filtering_available": bool(self_keys),
        "scope": {
            "whole_paths": paths,
            "line_ranges": [item.label for item in ranges],
        },
        "working_tree_overlap": working_tree_status(root, target_paths),
        "possible_affected_contributors": candidates,
        "history_limit_per_path": args.max_commits if args.max_commits > 0 else None,
        "limitations": [
            "Uses local Git state only and does not fetch remote refs.",
            "Git authorship indicates relevant history, not ownership, employment, or live editing.",
            "Local Git cannot reliably attribute uncommitted changes to a person.",
        ],
    }


def render_markdown(report: dict[str, object]) -> str:
    identity = report["acting_identity"]
    assert isinstance(identity, dict)
    scope = report["scope"]
    assert isinstance(scope, dict)
    lines = [
        "# Pre-change collaboration scan",
        "",
        f"- Repository: `{report['repository']}`",
        f"- Local ref: `{report['branch']}` at `{report['head']}`",
        f"- Scanned at: {report['scanned_at']}",
        f"- Acting identity: {identity.get('name') or 'unavailable'} <{identity.get('email') or 'unavailable'}>",
        f"- Whole paths: {', '.join(f'`{item}`' for item in scope['whole_paths']) or 'none'}",
        f"- Line ranges: {', '.join(f'`{item}`' for item in scope['line_ranges']) or 'none'}",
        "",
        "## Existing working-tree overlap",
        "",
    ]
    overlaps = report["working_tree_overlap"]
    assert isinstance(overlaps, list)
    lines.extend([f"- `{item}`" for item in overlaps] if overlaps else ["- None in the scanned paths."])
    lines.extend(["", "## Possible affected contributors", ""])
    candidates = report["possible_affected_contributors"]
    assert isinstance(candidates, list)
    if candidates:
        lines.extend(
            [
                "| Contributor | Latest relevant change | Commit | Confidence | Evidence |",
                "|---|---|---|---|---|",
            ]
        )
        for person in candidates:
            assert isinstance(person, dict)
            contributor = f"{person['name']} <{person['email'] or 'no email'}>"
            lines.append(
                "| "
                + " | ".join(
                    markdown_escape(str(value))
                    for value in (
                        contributor,
                        person["latest_relevant_change"],
                        person["commit"],
                        ", ".join(person["confidence"]),
                        ", ".join(person["evidence"]),
                    )
                )
                + " |"
            )
    else:
        lines.append("- No other contributor was found in the available local history for this scope.")
    if not report["self_filtering_available"]:
        lines.extend(["", "> Acting Git identity was unavailable, so all relevant authors are shown as candidates."])
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    return "\n".join(lines)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Scan planned Git change targets for contributor and working-tree overlap."
    )
    result.add_argument("--repo", default=".", help="Repository or a path inside it")
    result.add_argument("--path", action="append", default=[], help="Whole-file or directory target")
    result.add_argument(
        "--line-range",
        action="append",
        default=[],
        metavar="PATH:START:END",
        help="Localized target; repeat as needed",
    )
    result.add_argument("--self-name", help="Override the acting user's Git name")
    result.add_argument("--self-email", help="Override the acting user's Git email")
    result.add_argument(
        "--max-commits",
        type=int,
        default=0,
        help="Maximum commits inspected per whole path; 0 means unlimited (default: 0)",
    )
    result.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        report = build_report(args)
    except (OSError, ScanError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
