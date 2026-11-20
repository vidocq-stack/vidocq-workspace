#!/usr/bin/env python3
"""Unify the build of the imported monorepo (MONOREPO.md §4, Saturday step 2), in place.

- writes the grouping POMs (packaging pom, inherit the root, which skips their deploy);
- points the <parent> of each brick root at ../…/vidocq-parent/pom.xml, so the reactor's own vidocq-parent is used;
- replaces the literal version of a sibling brick property (<vauban.version>0.4.0-SNAPSHOT</…>) by ${project.version}.
The root pom.xml and the root files are written by hand, not here. Idempotent.
Usage: unify-build.py <monorepo checkout>"""
import os, re, sys

ROOT = sys.argv[1]
VERSION = "0.4.0-SNAPSHOT"
BRICKS = ["vauban", "chappe", "champollion", "foy", "cassini", "mansart", "noether", "kerckhoffs", "peano", "ibarra",
          "bodoni", "ravel", "knock", "dirac", "heisenberg", "cervantes", "cyrano", "humboldt", "grimm"]
# folder -> (artifactId, name, modules)
GROUPS = {
    "vidocq-components": ("vidocq-components", "Vidocq Components",
                          ["vidocq-components-transport", "vidocq-components-jakartaee",
                           "vidocq-components-microprofile"]),
    "vidocq-components/vidocq-components-transport": ("vidocq-components-transport", "Vidocq Components: transport",
                                                      ["chappe"]),
    "vidocq-components/vidocq-components-jakartaee": ("vidocq-components-jakartaee", "Vidocq Components: Jakarta EE",
                                                      ["vidocq-components-jakartaee-core",
                                                       "vidocq-components-jakartaee-webprofile"]),
    "vidocq-components/vidocq-components-jakartaee/vidocq-components-jakartaee-core": (
        "vidocq-components-jakartaee-core", "Vidocq Components: Jakarta EE Core Profile",
        ["vauban", "champollion", "cassini"]),
    "vidocq-components/vidocq-components-jakartaee/vidocq-components-jakartaee-webprofile": (
        "vidocq-components-jakartaee-webprofile", "Vidocq Components: Jakarta EE Web Profile",
        ["foy", "peano", "ibarra", "bodoni", "mansart"]),
    "vidocq-components/vidocq-components-microprofile": (
        "vidocq-components-microprofile", "Vidocq Components: MicroProfile",
        ["ravel", "knock", "dirac", "heisenberg", "cervantes", "cyrano", "humboldt", "grimm"]),
    "preview": ("vidocq-preview", "Vidocq Preview", ["vidocq-components-jakartaee"]),
    "preview/vidocq-components-jakartaee": ("vidocq-preview-jakartaee", "Vidocq Preview: Jakarta EE",
                                            ["vidocq-components-jakartaee-webprofile"]),
    "preview/vidocq-components-jakartaee/vidocq-components-jakartaee-webprofile": (
        "vidocq-preview-jakartaee-webprofile", "Vidocq Preview: Jakarta EE Web Profile", ["noether", "kerckhoffs"]),
    "incubator": ("vidocq-incubator", "Vidocq Incubator", []),
}
HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
"""


def parent_of(folder):
    up = os.path.dirname(folder)
    if not up:
        return "io.vidocq", "vidocq-build"
    return "io.vidocq.build", GROUPS[up][0]


def write_group(folder, artifact, name, modules):
    g, a = parent_of(folder)
    mods = "".join(f"        <module>{m}</module>\n" for m in modules)
    body = (HEADER + f"""
    <!-- A grouping POM (MONOREPO.md §4): it aggregates, publishes nothing, and is the parent of no brick. -->
    <parent>
        <groupId>{g}</groupId>
        <artifactId>{a}</artifactId>
        <version>{VERSION}</version>
    </parent>

    <groupId>io.vidocq.build</groupId>
    <artifactId>{artifact}</artifactId>
    <packaging>pom</packaging>
    <name>{name}</name>
""" + (f"""
    <modules>
{mods}    </modules>
""" if modules else """
    <!-- Not usable, never released, not in the BOM: a module here repeats the folder tree of vidocq-components/. -->
    <modules/>
""") + "</project>\n")
    path = os.path.join(ROOT, folder, "pom.xml")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(body)


for folder, (artifact, name, modules) in GROUPS.items():
    write_group(folder, artifact, name, modules)

# Brick roots: every folder of a group listed as a module that is a brick (or the runtime).
brick_roots = [os.path.join(f, m) for f, (_, _, mods) in GROUPS.items() for m in mods if m in BRICKS]
brick_roots.append("vidocq-runtime")
sibling = re.compile(r"<(" + "|".join(BRICKS) + r")\.version>" + re.escape(VERSION) + r"</\1\.version>")
parent_block = re.compile(r"(<parent>\s*<groupId>io\.vidocq</groupId>\s*<artifactId>vidocq-parent</artifactId>\s*"
                          r"<version>[^<]+</version>)(\s*<relativePath\s*/>|\s*<relativePath>[^<]*</relativePath>)?",
                          re.S)
for b in brick_roots:
    path = os.path.join(ROOT, b, "pom.xml")
    text = open(path).read()
    rel = os.path.relpath(os.path.join(ROOT, "vidocq-parent", "pom.xml"), os.path.join(ROOT, b))
    new, n = parent_block.subn(lambda m: m.group(1) + f"\n        <relativePath>{rel}</relativePath>", text, count=1)
    if n != 1:
        sys.exit(f"{b}: no vidocq-parent <parent> block")
    new, k = sibling.subn(lambda m: f"<{m.group(1)}.version>${{project.version}}</{m.group(1)}.version>", new)
    open(path, "w").write(new)
    print(f"{b}: parent -> {rel}, {k} sibling versions")
