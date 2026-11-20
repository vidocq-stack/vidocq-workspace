#!/usr/bin/env python3
"""Find the reactor modules whose maven-compiler-plugin takes an annotation processor of the reactor
(annotationProcessorPaths) without depending on it, directly or transitively through the reactor: a parallel
build (-T) may then compile them before the processor is built, with an earlier processor from a repository.

Reads the effective POM of the whole reactor (`mvn help:effective-pom -Doutput=<file>` at the root).
Usage: processor-edges.py <effective-pom.xml> [--json]   prints module -> missing processors."""
import json, re, sys
import xml.etree.ElementTree as ET

NS = "{http://maven.apache.org/POM/4.0.0}"
text = open(sys.argv[1]).read()
projects = re.findall(r"<project [^>]*>.*?</project>", text, re.S)


def t(e, name):
    c = e.find(NS + name)
    return c.text.strip() if c is not None and c.text else None


mods = {}
for p in projects:
    root = ET.fromstring(p)
    key = f"{t(root, 'groupId')}:{t(root, 'artifactId')}"
    deps = {f"{t(d, 'groupId')}:{t(d, 'artifactId')}" for d in root.findall(f"{NS}dependencies/{NS}dependency")}
    procs = set()
    for plugin in root.iter(NS + "plugin"):
        if t(plugin, "artifactId") != "maven-compiler-plugin":
            continue
        for path in plugin.iter(NS + "annotationProcessorPaths"):
            for entry in path:
                procs.add(f"{t(entry, 'groupId')}:{t(entry, 'artifactId')}")
    # only the build section, not pluginManagement: iter() above also walks pluginManagement, filter it out
    managed = set()
    for pm in root.iter(NS + "pluginManagement"):
        for plugin in pm.iter(NS + "plugin"):
            if t(plugin, "artifactId") == "maven-compiler-plugin":
                for path in plugin.iter(NS + "annotationProcessorPaths"):
                    for entry in path:
                        managed.add(f"{t(entry, 'groupId')}:{t(entry, 'artifactId')}")
    build_procs = set()
    build = root.find(NS + "build")
    if build is not None:
        plugins = build.find(NS + "plugins")
        for plugin in (plugins if plugins is not None else []):
            if t(plugin, "artifactId") == "maven-compiler-plugin":
                for path in plugin.iter(NS + "annotationProcessorPaths"):
                    for entry in path:
                        build_procs.add(f"{t(entry, 'groupId')}:{t(entry, 'artifactId')}")
    mods[key] = {"deps": deps, "procs": build_procs}

reactor = set(mods)


def closure(k, seen=None):
    seen = seen if seen is not None else set()
    for d in mods[k]["deps"]:
        if d in reactor and d not in seen:
            seen.add(d)
            closure(d, seen)
    return seen


missing = {}
for k, m in mods.items():
    procs = {p for p in m["procs"] if p in reactor and p != k}
    if not procs:
        continue
    reach = closure(k)
    gap = sorted(p for p in procs if p not in reach)
    if gap:
        missing[k] = gap
if "--json" in sys.argv:
    print(json.dumps(missing, indent=1))
else:
    print(len(missing), "modules lack a build-order edge to a processor of the reactor")
    for k, v in sorted(missing.items()):
        print(k, "->", ", ".join(v))
