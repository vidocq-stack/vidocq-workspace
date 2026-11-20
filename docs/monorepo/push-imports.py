#!/usr/bin/env python3
"""Push the monorepo import to Vidocq/vidocq one repository at a time (MONOREPO.md §5): each merge commit of
import.py, oldest first, then the prefixed tags of that repository. Stops at the first refused push.
Usage: push-imports.py <monorepo checkout>"""
import datetime, re, subprocess, sys

mono = sys.argv[1]


def git(*args):
    return subprocess.run(["git"] + list(args), cwd=mono, check=True, capture_output=True, text=True).stdout.strip()


remote_head = git("ls-remote", "origin", "refs/heads/main").split()[0]
first_parent = git("log", "--first-parent", "--format=%H %s", f"{remote_head}..HEAD").splitlines()[::-1]
for line in first_parent:
    sha, subject = line.split(" ", 1)
    m = re.match(r"chore\(monorepo\): import (\S+) into ", subject)
    if not m:
        sys.exit(f"unexpected commit {sha[:10]} {subject}")
    repo = m.group(1)
    r = subprocess.run(["git", "push", "origin", f"{sha}:refs/heads/main"], cwd=mono, capture_output=True, text=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%SZ")
    if r.returncode:
        sys.exit(f"{stamp} {repo}: push refused\n{r.stderr}")
    tags = [t for t in git("tag", "--list", f"{repo}/*").splitlines() if t]
    if tags:
        r = subprocess.run(["git", "push", "origin"] + [f"refs/tags/{t}:refs/tags/{t}" for t in tags], cwd=mono,
                           capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"{stamp} {repo}: tags refused\n{r.stderr}")
    print(f"{stamp} {repo}: main -> {sha[:10]}, {len(tags)} tags", flush=True)
print("remote main:", git("ls-remote", "origin", "refs/heads/main").split()[0][:10])
