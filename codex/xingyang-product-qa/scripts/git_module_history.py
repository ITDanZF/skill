#!/usr/bin/env python3
"""Summarize Git contributors for selected repository paths without exposing emails."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


AUTOMATION_PATTERN = re.compile(
    r"(?:\[bot\]|dependabot|renovate|github-actions|gitlab-ci|automation|bot\b|\bagent\b|hermes)",
    re.IGNORECASE,
)
FIELD_SEPARATOR = "\x1f"
RECORD_SEPARATOR = "\x1e"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize non-merge Git history for one or more repository-relative paths."
    )
    parser.add_argument("--repo", required=True, help="Git repository root")
    parser.add_argument(
        "--path",
        action="append",
        dest="paths",
        required=True,
        help="Repository-relative file or directory; repeat as needed",
    )
    parser.add_argument("--since-days", type=int, default=180)
    parser.add_argument("--limit", type=int, default=10)
    return parser.parse_args()


def run_git(repo: Path, arguments: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-c", "i18n.logOutputEncoding=utf-8", *arguments],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or "Git command failed"
        raise RuntimeError(message)
    return completed.stdout


def validate_repo(value: str) -> Path:
    repo = Path(value).expanduser().resolve()
    if not repo.is_dir():
        raise ValueError("--repo must be an existing directory")
    top_level = Path(run_git(repo, ["rev-parse", "--show-toplevel"]).strip()).resolve()
    if top_level != repo:
        raise ValueError("--repo must be the exact Git repository root")
    return repo


def validate_paths(values: list[str], repo: Path) -> list[str]:
    validated: list[str] = []
    for raw_value in values:
        normalized = raw_value.replace("\\", "/").strip().strip("/")
        path_value = PurePosixPath(normalized)
        if not normalized or path_value.is_absolute() or ".." in path_value.parts:
            raise ValueError(f"Invalid repository-relative path: {raw_value}")
        candidate = (repo / Path(*path_value.parts)).resolve()
        if repo != candidate and repo not in candidate.parents:
            raise ValueError(f"Path leaves repository root: {raw_value}")
        if not candidate.exists():
            raise ValueError(f"Path does not exist: {raw_value}")
        rendered = path_value.as_posix()
        if rendered not in validated:
            validated.append(rendered)
    return validated


def parse_log(repo: Path, paths: list[str]) -> list[dict[str, str]]:
    format_value = FIELD_SEPARATOR.join(["%H", "%aI", "%an", "%ae", "%s"]) + RECORD_SEPARATOR
    raw_log = run_git(
        repo,
        ["log", "--no-merges", f"--format={format_value}", "--", *paths],
    )
    commits: list[dict[str, str]] = []
    for record in raw_log.split(RECORD_SEPARATOR):
        fields = record.strip("\r\n").split(FIELD_SEPARATOR)
        if len(fields) != 5:
            continue
        commit_hash, authored_at, author_name, author_email, subject = fields
        commits.append(
            {
                "hash": commit_hash,
                "authoredAt": authored_at,
                "authorName": author_name.strip() or "Unknown",
                "identity": author_email.strip().casefold(),
                "subject": subject.strip(),
            }
        )
    return commits


def is_automation(commit: dict[str, str]) -> bool:
    identity_text = f"{commit['authorName']} {commit['identity']}"
    return AUTOMATION_PATTERN.search(identity_text) is not None


def iso_to_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def choose_display_name(name_counts: Counter[str], commits: list[dict[str, str]]) -> str:
    highest_count = max(name_counts.values())
    candidates = {name for name, count in name_counts.items() if count == highest_count}
    for commit in commits:
        if commit["authorName"] in candidates:
            return commit["authorName"]
    return sorted(candidates, key=str.casefold)[0]


def summarize(
    repo: Path,
    paths: list[str],
    since_days: int,
    limit: int,
) -> dict[str, Any]:
    commits = parse_log(repo, paths)
    cutoff = datetime.now(timezone.utc) - timedelta(days=since_days)
    excluded_automation = sum(1 for commit in commits if is_automation(commit))
    human_commits = [commit for commit in commits if not is_automation(commit)]

    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for index, commit in enumerate(human_commits):
        identity = commit["identity"] or f"missing-email:{commit['authorName'].casefold()}:{index}"
        groups[identity].append(commit)

    contributors: list[dict[str, Any]] = []
    for grouped_commits in groups.values():
        grouped_commits.sort(key=lambda item: iso_to_datetime(item["authoredAt"]), reverse=True)
        name_counts = Counter(commit["authorName"] for commit in grouped_commits)
        display_name = choose_display_name(name_counts, grouped_commits)
        aliases = sorted(
            (name for name in name_counts if name != display_name),
            key=str.casefold,
        )
        recent_commits = sum(
            1 for commit in grouped_commits if iso_to_datetime(commit["authoredAt"]) >= cutoff
        )
        latest = grouped_commits[0]
        contributors.append(
            {
                "name": display_name,
                "aliases": aliases,
                "commits": len(grouped_commits),
                "recentCommits": recent_commits,
                "latestCommit": latest["hash"][:12],
                "latestAt": latest["authoredAt"],
                "latestSubject": latest["subject"],
                "sampleSubjects": [commit["subject"] for commit in grouped_commits[:3]],
            }
        )

    contributors.sort(
        key=lambda item: (
            item["recentCommits"],
            item["latestAt"],
            item["commits"],
            item["name"].casefold(),
        ),
        reverse=True,
    )
    revision = run_git(repo, ["rev-parse", "--short=12", "HEAD"]).strip()
    return {
        "revision": revision,
        "paths": paths,
        "sinceDays": since_days,
        "totalRelevantCommits": len(commits),
        "excludedAutomationCommits": excluded_automation,
        "contributors": contributors[:limit],
        "limitations": [
            "Git history shows code participation, not product ownership, availability, or fault.",
            "Aliases are merged only when Git records use the same normalized email; emails are never emitted.",
            "Recent activity is counted within the requested window; review the cited commits before suggesting a contact.",
        ],
    }


def main() -> int:
    try:
        args = parse_args()
        if args.since_days <= 0:
            raise ValueError("--since-days must be positive")
        if args.limit <= 0:
            raise ValueError("--limit must be positive")
        repo = validate_repo(args.repo)
        paths = validate_paths(args.paths, repo)
        result = summarize(repo, paths, args.since_days, args.limit)
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0
    except (OSError, RuntimeError, ValueError) as error:
        print(f"git_module_history: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
