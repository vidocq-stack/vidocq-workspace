#!/usr/bin/env python3
"""Insert the published brick modules (bom-bricks.py) into vidocq-runtime-bom, before the closing
</dependencies> of its dependencyManagement: stable bricks first, then a <!-- preview --> section. Maven plugins are
left out (never a dependency). Usage: bom-insert.py <monorepo checkout>"""
import os, subprocess, sys

ROOT = sys.argv[1]
VERSION = "0.4.0-SNAPSHOT"
out = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "bom-bricks.py"),
                      ROOT], check=True, capture_output=True, text=True).stdout.splitlines()
stable, preview, current = [], [], None
for line in out:
    if line.startswith("## "):
        _, level, name, _ = line.split()
        current = (preview if level == "preview" else stable)
        current.append(("brick", name))
    else:
        g, a, packaging = line.split(":")
        if packaging != "maven-plugin":
            current.append((g, a))


def render(entries):
    s = ""
    for e in entries:
        if e[0] == "brick":
            s += f"\n            <!-- {e[1].capitalize()} -->\n"
        else:
            s += (f"            <dependency>\n                <groupId>{e[0]}</groupId>\n"
                  f"                <artifactId>{e[1]}</artifactId>\n                <version>{VERSION}</version>\n"
                  f"            </dependency>\n")
    return s


block = ("\n            <!-- Components: the published modules of each stable brick, at the same version -->"
         + render(stable)
         + "\n            <!-- preview: usable and released, not complete or not certified (MONOREPO.md §3) -->"
         + render(preview))
path = os.path.join(ROOT, "vidocq-runtime", "vidocq-runtime-bom", "pom.xml")
text = open(path).read()
marker = "        </dependencies>\n    </dependencyManagement>"
if "<!-- Components: the published modules" in text:
    sys.exit("already inserted")
assert text.count(marker) == 1
open(path, "w").write(text.replace(marker, block.rstrip("\n") + "\n" + marker))
print(sum(1 for e in stable if e[0] != "brick"), "stable,", sum(1 for e in preview if e[0] != "brick"), "preview")
