#!/usr/bin/env python3
"""List the published modules of every brick of the monorepo, grouped by brick, as BOM <dependency> entries.
Same rule as ApplicationBomAndParentTest: a module under a pom that skips its deploy or its publishing is not
published; aggregators are not artifacts. Usage: bom-bricks.py <monorepo checkout> [--xml]"""
import os, sys, xml.etree.ElementTree as ET

ROOT = sys.argv[1]
NS = "{http://maven.apache.org/POM/4.0.0}"
SKIPS = ("<maven.deploy.skip>true</maven.deploy.skip>", "<skipPublishing>true</skipPublishing>")


def child(e, name):
    c = e.find(NS + name)
    return c.text.strip() if c is not None and c.text else None


def collect(d, out):
    text = open(os.path.join(d, "pom.xml")).read()
    if any(s in text for s in SKIPS):
        return
    p = ET.parse(os.path.join(d, "pom.xml")).getroot()
    mods = [m.text.strip() for m in p.findall(f"{NS}modules/{NS}module")]
    if not mods and child(p, "packaging") != "pom":
        g = child(p, "groupId") or child(p.find(NS + "parent"), "groupId")
        out.append((g, child(p, "artifactId"), child(p, "packaging") or "jar"))
    for m in mods:
        collect(os.path.join(d, m), out)


def bricks(level):
    base = os.path.join(ROOT, level)
    for dp, dn, fn in sorted(os.walk(base)):
        dn.sort()
        if "pom.xml" in fn and os.path.basename(os.path.dirname(dp)).startswith("vidocq-components-") \
                and not os.path.basename(dp).startswith("vidocq-components"):
            dn[:] = []
            yield os.path.basename(dp), dp


for level in ("vidocq-components", "preview"):
    for name, d in bricks(level):
        out = []
        collect(d, out)
        print(f"## {level} {name} {len(out)}")
        for g, a, pk in out:
            print(f"{g}:{a}:{pk}")
