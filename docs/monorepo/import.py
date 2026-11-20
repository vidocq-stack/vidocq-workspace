#!/usr/bin/env python3
"""Build the Vidocq monorepo history (MONOREPO.md §5, Saturday step 1).

Starting from a fresh clone of Vidocq/vidocq at its frozen head:
  1. one commit moves the whole runtime into vidocq-runtime/ (its history keeps its SHAs);
  2. for each of the 20 other repositories, a fresh clone of main at its frozen head is rewritten with
     `git filter-repo --to-subdirectory-filter <path>`, then merged with `git merge --allow-unrelated-histories`.
Every new commit is signed and signed off. The tags of an imported repository get its name as a prefix
(vauban's v0.3.0 becomes vauban/v0.3.0); the runtime's own tags keep their names.
Nothing is pushed: the result is a local repository in <workdir>/vidocq.

Usage: import.py <workdir> [--heads <main-heads.txt>]
  --heads checks that each fresh clone is at the frozen head recorded at the freeze.
"""
import argparse, os, re, shutil, subprocess, sys

SSH = "git@codefloe.com:Vidocq/{}.git"
CORE = "vidocq-components/vidocq-components-jakartaee/vidocq-components-jakartaee-core"
WEB = "vidocq-components/vidocq-components-jakartaee/vidocq-components-jakartaee-webprofile"
PREVIEW_WEB = "preview/vidocq-components-jakartaee/vidocq-components-jakartaee-webprofile"
MP = "vidocq-components/vidocq-components-microprofile"
# The import table of MONOREPO.md §3, in dependency order (parent first, runtime last is not needed: it is the base).
IMPORTS = [
    ("vidocq-parent", "vidocq-parent"),
    ("chappe", "vidocq-components/vidocq-components-transport/chappe"),
    ("vauban", f"{CORE}/vauban"),
    ("champollion", f"{CORE}/champollion"),
    ("cassini", f"{CORE}/cassini"),
    ("foy", f"{WEB}/foy"),
    ("peano", f"{WEB}/peano"),
    ("ibarra", f"{WEB}/ibarra"),
    ("bodoni", f"{WEB}/bodoni"),
    ("mansart", f"{WEB}/mansart"),
    ("ravel", f"{MP}/ravel"),
    ("knock", f"{MP}/knock"),
    ("dirac", f"{MP}/dirac"),
    ("heisenberg", f"{MP}/heisenberg"),
    ("cervantes", f"{MP}/cervantes"),
    ("cyrano", f"{MP}/cyrano"),
    ("humboldt", f"{MP}/humboldt"),
    ("grimm", f"{MP}/grimm"),
    ("noether", f"{PREVIEW_WEB}/noether"),
    ("kerckhoffs", f"{PREVIEW_WEB}/kerckhoffs"),
]
TRAILERS = ("\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n"
            "Claude-Session: https://claude.ai/code/session_01DQoEaLnfwGpxVYSXFoFQA8")


def run(*cmd, cwd=None):
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def clone(repo, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    run("git", "clone", "-q", "--single-branch", "--branch", "main", SSH.format(repo), dest)
    # Release tags often point at commits outside main's history: fetch every tag, with its commits.
    run("git", "fetch", "-q", "--tags", "origin", cwd=dest)
    return run("git", "rev-parse", "HEAD", cwd=dest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workdir")
    ap.add_argument("--heads")
    a = ap.parse_args()
    heads = {}
    if a.heads:
        for line in open(a.heads):
            m = re.match(r"(\S+)\s+([0-9a-f]{10})\s", line)
            if m:
                heads[m.group(1)] = m.group(2)
    src = os.path.join(a.workdir, "src")
    mono = os.path.join(a.workdir, "vidocq")
    os.makedirs(src, exist_ok=True)

    def check(repo, sha):
        if heads and not sha.startswith(heads[repo]):
            sys.exit(f"{repo}: main is {sha[:10]}, the freeze recorded {heads[repo]}")

    # 1. The runtime moves into vidocq-runtime/.
    check("vidocq", clone("vidocq", mono))
    entries = [e for e in os.listdir(mono) if e != ".git"]
    os.makedirs(os.path.join(mono, "vidocq-runtime"))
    run("git", "mv", "-k", *entries, "vidocq-runtime/", cwd=mono)
    left = [e for e in os.listdir(mono) if e not in (".git", "vidocq-runtime")]
    if left:  # untracked or ignored leftovers of a fresh clone: there should be none
        sys.exit(f"not moved: {left}")
    run("git", "commit", "-q", "-S", "-s", "-m",
        "chore(monorepo): move the runtime into vidocq-runtime/" + TRAILERS, cwd=mono)

    # 2. The other repositories, each under its path.
    for repo, path in IMPORTS:
        d = os.path.join(src, repo)
        sha = clone(repo, d)
        check(repo, sha)
        run("git", "filter-repo", "--force", "--quiet", "--to-subdirectory-filter", path,
            "--tag-rename", f":{repo}/", cwd=d)
        run("git", "fetch", "-q", "--no-tags", d, f"main:refs/import/{repo}", f"refs/tags/{repo}/*:refs/tags/{repo}/*",
            cwd=mono)
        run("git", "merge", "-q", "--allow-unrelated-histories", "--no-edit", "-S", "--signoff", "-m",
            f"chore(monorepo): import {repo} into {path}\n\nFrom Vidocq/{repo} main {sha}." + TRAILERS,
            f"refs/import/{repo}", cwd=mono)
        run("git", "update-ref", "-d", f"refs/import/{repo}", cwd=mono)

    print(run("git", "log", "--oneline", "-25", cwd=mono))
    print("commits:", run("git", "rev-list", "--count", "HEAD", cwd=mono))


if __name__ == "__main__":
    main()
