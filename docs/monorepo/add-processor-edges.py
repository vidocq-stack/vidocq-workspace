#!/usr/bin/env python3
"""Add a build-order edge from each module to the reactor processors it compiles with (processor-edges.py):
a dependency on the processor's POM, provided, every transitive dependency excluded. It puts nothing on the
class path or the module path; it only makes a parallel build (-T) wait for the processor.
Usage: add-processor-edges.py <monorepo checkout> <effective-pom.xml>"""
import json, os, re, subprocess, sys

ROOT, EFF = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
missing = json.loads(subprocess.run([sys.executable, "-I", os.path.join(here, "processor-edges.py"), EFF, "--json"],
                                    check=True, capture_output=True, text=True).stdout)

# groupId:artifactId -> pom.xml of the reactor
index = {}
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in (".git", "target", "src", "node_modules")]
    if "pom.xml" not in fn:
        continue
    path = os.path.join(dp, "pom.xml")
    text = open(path).read()
    body = re.sub(r"<parent>.*?</parent>", "", text, count=1, flags=re.S)
    am = re.search(r"<artifactId>([^<]+)</artifactId>", body)
    a = am.group(1)
    g = re.search(r"<groupId>([^<]+)</groupId>", body[:am.start()])  # the project's own, before its artifactId
    g = g.group(1) if g else re.search(r"<parent>.*?<groupId>([^<]+)</groupId>", text, re.S).group(1)
    index[f"{g}:{a}"] = path

MARK = "<!-- Build order only (-T): the processors this module compiles with, see docs/monorepo in the workspace. -->"
done = 0
for module, procs in sorted(missing.items()):
    path = index[module]
    text = open(path).read()
    if MARK in text:
        continue
    entries = "".join(
        f"""        <dependency>
            <groupId>{p.split(':')[0]}</groupId>
            <artifactId>{p.split(':')[1]}</artifactId>
            <version>${{project.version}}</version>
            <type>pom</type>
            <scope>provided</scope>
            <exclusions>
                <exclusion>
                    <groupId>*</groupId>
                    <artifactId>*</artifactId>
                </exclusion>
            </exclusions>
        </dependency>
""" for p in procs)
    block = f"        {MARK}\n{entries}"
    # the project's own <dependencies>, not one of <dependencyManagement> or a <profile>
    stripped = re.sub(r"<(dependencyManagement|profiles|build|reporting)>.*?</\1>", lambda m: " " * len(m.group(0)),
                      text, flags=re.S)
    m = re.search(r"\n(\s*)</dependencies>", stripped)
    if m:
        pos = m.start() + 1
        text = text[:pos] + block + text[pos:]
    else:
        m = re.search(r"\n(\s*)<build>", stripped) or re.search(r"\n</project>", stripped)
        pos = m.start() + 1
        text = text[:pos] + f"    <dependencies>\n{block}    </dependencies>\n\n" + text[pos:]
    open(path, "w").write(text)
    done += 1
print("modules edited:", done, "of", len(missing))
