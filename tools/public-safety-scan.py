#!/usr/bin/env python3
"""Local, value-redacting pre-publication scan of tracked files and Git history."""
import re
import subprocess
import sys


PATTERNS = {
    "private-key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "github-token": re.compile(rb"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "openai-token": re.compile(rb"\bsk-[A-Za-z0-9_-]{24,}\b"),
    "contact-email-review": re.compile(rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "mac-address-review": re.compile(rb"(?i)(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}"),
    "credential-assignment-review": re.compile(
        rb"(?im)^\s*(?:password|passwd|pppoe_password|wifi_password|admin_password|api[_-]?key|secret)\s*[:=]\s*([^\s<#]+)"
    ),
}
SAFE_VALUES = (b"<redacted>", b"<redacted>", b"<your", b"example", b"changeme", b"placeholder")


def git(*args):
    return subprocess.check_output(["git", *args])


def findings(data):
    out = []
    for name, pattern in PATTERNS.items():
        matches = list(pattern.finditer(data))
        if name == "credential-assignment-review":
            matches = [m for m in matches if not any(s in m.group(1).lower() for s in SAFE_VALUES)]
        if name == "contact-email-review":
            matches = [m for m in matches if b"users.noreply.github.com" not in m.group(0).lower()]
        if matches:
            out.append(f"{name} ({len(matches)} match(es))")
    return out


def main():
    results = []
    paths = git("ls-files", "-z").decode().split("\0")
    for path in filter(None, paths):
        try:
            with open(path, "rb") as f:
                hits = findings(f.read())
            if hits:
                results.append((path, hits))
        except OSError as exc:
            results.append((path, [f"read-error: {exc.__class__.__name__}"]))

    seen = set()
    for line in git("rev-list", "--objects", "--all").decode(errors="replace").splitlines():
        parts = line.split(" ", 1)
        oid = parts[0]
        label = parts[1] if len(parts) == 2 else f"blob:{oid[:12]}"
        if oid in seen:
            continue
        seen.add(oid)
        kind = subprocess.check_output(["git", "cat-file", "-t", oid], text=True).strip()
        if kind != "blob":
            continue
        data = git("cat-file", "blob", oid)
        hits = findings(data)
        if hits:
            results.append((f"history:{label}", hits))

    print(f"tracked_files={len(list(filter(None, paths)))} reachable_git_objects={len(seen)}")
    if results:
        print("REVIEW REQUIRED (values are never printed):")
        for path, labels in results:
            print(f"{path}: {', '.join(labels)}")
        return 1
    print("No configured high-risk patterns found in tracked files or reachable Git blob history.")
    print("This heuristic scan is not a substitute for human review of new files and ignored artifacts.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"git scan command failed: {exc.cmd[0]}", file=sys.stderr)
        raise SystemExit(2)
