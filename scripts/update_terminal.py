#!/usr/bin/env python3
"""Fetches the latest commit from LEo-dev5's repos and updates terminal.svg."""

import json
import re
import urllib.request
import urllib.error
import os

GITHUB_USER = "LEo-dev5"
SVG_PATH = "terminal.svg"
PLACEHOLDER_PATTERN = r'(id="recent-project">)[^<]*(</tspan>)'


def api_get(url: str) -> list | dict | None:
    token = os.environ.get("GH_TOKEN", "")
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as e:
        print(f"[warn] API error ({url}): {e}")
        return None


def fetch_latest_commit() -> str:
    # Get repos sorted by last push date
    repos = api_get(
        f"https://api.github.com/users/{GITHUB_USER}/repos"
        f"?sort=pushed&per_page=10&type=owner"
    )
    if not repos:
        return "no recent commits found"

    for repo in repos:
        # Skip forks and private repos
        if repo.get("fork") or repo.get("private"):
            continue
        repo_name = repo["name"]

        commits = api_get(
            f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/commits?per_page=1"
        )
        if not commits:
            continue

        message = commits[0]["commit"]["message"].splitlines()[0]
        # Skip auto-commits from this Action
        if "[skip ci]" in message:
            continue

        label = f"{repo_name}: {message}"
        if len(label) > 48:
            label = label[:45] + "..."
        return label

    return "no recent commits found"


def update_svg(text: str) -> None:
    with open(SVG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    replacement = rf'\g<1>:  {text}\g<2>'
    updated = re.sub(PLACEHOLDER_PATTERN, replacement, content)

    if updated == content:
        print("[warn] Pattern not found in SVG — nothing updated.")
        return

    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(updated)

    print(f"[ok] Updated terminal.svg → {text}")


if __name__ == "__main__":
    commit_text = fetch_latest_commit()
    update_svg(commit_text)
