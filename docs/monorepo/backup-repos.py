#!/usr/bin/env python3
"""Back up the 21 repositories of the monorepo migration before any of them is archived or deleted.

For each repository, under <dest>/<repo>/:
  - <repo>.git     `git clone --mirror` over SSH: every branch, tag and refs/pull/* ref;
  - <repo>.bundle  `git bundle create --all` of that mirror, checked with `git bundle verify`;
  - issues.json, pulls.json, comments.json, releases.json, labels.json, milestones.json  the forge data git
    does not hold (public API, anonymous), and releases/<tag>/ the files attached to each release;
  - heads.txt      `git show-ref` of the mirror, to compare with the forge later.
Re-running refreshes the mirrors (`git remote update`) and rewrites the rest. Read-only on the forge.
Usage: backup-repos.py <dest>"""
import json, os, subprocess, sys, time, urllib.error, urllib.request

REPOS = ["vidocq-parent", "vidocq", "chappe", "vauban", "champollion", "foy", "cassini", "mansart", "noether",
         "kerckhoffs", "peano", "ibarra", "bodoni", "ravel", "knock", "dirac", "heisenberg", "cervantes", "cyrano",
         "humboldt", "grimm"]
API = "https://codefloe.com/api/v1/repos/Vidocq/"
dest = os.path.expanduser(sys.argv[1])


def run(*cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True).stdout


def fetch(url):
    # The anonymous API answers 403, 429 or 503 now and then: wait and try again.
    for attempt in range(8):
        try:
            return json.load(urllib.request.urlopen(url, timeout=120))
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == 7:
                raise
            print(f"  retry {url}: {e}", flush=True)
            time.sleep(30 * (attempt + 1))


def pages(url):
    out, page = [], 1
    while True:
        sep = "&" if "?" in url else "?"
        batch = fetch(f"{url}{sep}limit=50&page={page}")
        if not batch:
            return out
        out += batch
        page += 1


for repo in REPOS:
    d = os.path.join(dest, repo)
    os.makedirs(d, exist_ok=True)
    mirror = os.path.join(d, repo + ".git")
    if os.path.isdir(mirror):
        run("git", "remote", "update", "--prune", cwd=mirror)
    else:
        run("git", "clone", "-q", "--mirror", f"git@codefloe.com:Vidocq/{repo}.git", mirror)
    bundle = os.path.join(d, repo + ".bundle")
    run("git", "bundle", "create", "-q", bundle, "--all", cwd=mirror)
    run("git", "bundle", "verify", "-q", bundle, cwd=mirror)
    refs = run("git", "show-ref", cwd=mirror)
    open(os.path.join(d, "heads.txt"), "w").write(refs)
    issues = pages(API + repo + "/issues?state=all&type=issues")
    pulls = pages(API + repo + "/pulls?state=all")
    comments = pages(API + repo + "/issues/comments")
    releases = pages(API + repo + "/releases")
    labels = pages(API + repo + "/labels")
    milestones = pages(API + repo + "/milestones?state=all")
    for name, data in (("issues", issues), ("pulls", pulls), ("comments", comments), ("releases", releases),
                       ("labels", labels), ("milestones", milestones)):
        json.dump(data, open(os.path.join(d, name + ".json"), "w"), indent=1)
    # The files attached to each release: git does not hold them.
    for rel in releases:
        for asset in rel.get("assets") or []:
            folder = os.path.join(d, "releases", rel["tag_name"].replace("/", "_"))
            os.makedirs(folder, exist_ok=True)
            target = os.path.join(folder, os.path.basename(asset["name"]))
            if not os.path.exists(target) or os.path.getsize(target) != asset["size"]:
                urllib.request.urlretrieve(asset["browser_download_url"], target)
    size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(d) for f in fs) // (1 << 20)
    print(f"{repo:14} refs={len(refs.splitlines()):5} issues={len(issues):4} pulls={len(pulls):4} "
          f"comments={len(comments):5} {size} MiB", flush=True)
