#!/usr/bin/env python3
"""Fetches the latest public commit from LEo-dev5 and updates terminal.svg."""

import json
import re
import urllib.request
import urllib.error
import os

GITHUB_USER = "LEo-dev5"
SVG_PATH = "terminal.svg"
PLACEHOLDER = "GH_RECENT_PLACEHOLDER"


def fetch_latest_commit() -> str:
    token = os.environ.get("GH_TOKEN", "")
    url = f"https://api.github.com/users/{GITHUB_USER}/events?per_page=30"

    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            events = json.loads(resp.read())
    except urllib.error.URLError as e:
        print(f"[warn] GitHub API error: {e}")
        return PLACEHOLDER

    for event in events:
        if event.get("type") != "PushEvent":
            continue
        commits = event.get("payload", {}).get("commits", [])
        if not commits:
            continue
        repo = event.get("repo", {}).get("name", "unknown")
        # Strip the owner prefix (LEo-dev5/repo-name → repo-name)
        repo_short = repo.split("/")[-1]
        message = commits[-1].get("message", "").splitlines()[0]
        # Trim to 45 chars so it fits in the SVG
        label = f"{repo_short}: {message}"
        if len(label) > 48:
            label = label[:45] + "..."
        return label

    return "no recent commits found"


def update_svg(text: str) -> None:
    with open(SVG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace the tspan content with id="recent-project"
    # Matches: >GH_RECENT_PLACEHOLDER< or whatever the current value is
    pattern = r'(id="recent-project">)[^<]*(</tspan>)'
    replacement = rf'\g<1>:  {text}\g<2>'
    updated = re.sub(pattern, replacement, content)

    if updated == content:
        print("[warn] Pattern not found in SVG — nothing updated.")
        return

    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(updated)

    print(f"[ok] Updated terminal.svg with: {text}")


if __name__ == "__main__":
    commit_text = fetch_latest_commit()
    update_svg(commit_text)
