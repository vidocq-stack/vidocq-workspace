#!/bin/bash
# Cross-corpus CPD scan: each Vidocq brick against the reference implementation of the same
# specification. Only clones spanning BOTH corpora are reported — clones internal to either
# corpus are noise for a provenance question.
#
# Prerequisites:
#   cd provenance-audit && mvn -q dependency:build-classpath -Dmdep.outputFile=cp.txt
#   bash provenance-audit/fetch-corpus.sh
#
# Usage:
#   TOKENS=50  MODE=strict bash provenance-audit/scan.sh   # verbatim copy-paste
#   TOKENS=100 MODE=loose  bash provenance-audit/scan.sh   # copied-then-renamed
set -uo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
WS=$(cd "$HERE/.." && pwd)
CORPUS=$HERE/corpus
CP=$(cat "$HERE/cp.txt")
TOKENS=${TOKENS:-50}
MODE=${MODE:-strict}
OUT=$HERE/reports-$MODE-$TOKENS
mkdir -p "$OUT"

# The loose pass ignores identifiers and literals, so renaming a copy no longer hides it.
EXTRA=""
[ "$MODE" = "loose" ] && EXTRA="--ignore-identifiers --ignore-literals"

pairs="vauban:cdi champollion:json cassini:jaxrs foy:servlet chappe:http ravel:mpconfig \
knock:mphealth dirac:mpmetrics heisenberg:mpft grimm:mpopenapi cervantes:mpjwt cyrano:mprest mansart:jpa"

printf "%-13s %-10s %8s %8s %s\n" "BRIQUE" "RI" "FICHIERS" "CLONES" "DETAIL"
for p in $pairs; do
  brick=${p%%:*}; ri=${p##*:}
  # Distributed production code only: no build output, no git worktrees, no TCK caches.
  src=$(find "$WS/$brick" -type d -path "*/src/main/java" 2>/dev/null \
        | grep -v "/target/" | grep -v "/\.claude/" | grep -v "/\.tck-cache/" | head -60)
  if [ -z "$src" ]; then
    printf "%-13s %-10s %8s %8s %s\n" "$brick" "$ri" "-" "-" "pas de src/main/java"; continue
  fi
  args=""; for d in $src; do args="$args --dir $d"; done
  nb=$(find $src -name "*.java" 2>/dev/null | wc -l | tr -d ' ')

  java -cp "$CP" net.sourceforge.pmd.cli.PmdCli cpd \
      --minimum-tokens "$TOKENS" --language java --format xml \
      --no-fail-on-violation --no-fail-on-error $EXTRA \
      $args --dir "$CORPUS/$ri" > "$OUT/$brick.xml" 2>"$OUT/$brick.err"

  python3 - "$OUT/$brick.xml" "$WS/$brick" "$CORPUS/$ri" "$brick" "$ri" "$nb" <<'PY'
import sys, os, xml.etree.ElementTree as ET
xmlf, brickroot, riroot, brick, ri, nb = sys.argv[1:7]
# CPD 7 emits a namespaced report: match on the local name, or everything reads as zero.
def local(e): return e.tag.split('}')[-1]
try:
    root = ET.parse(xmlf).getroot()
except Exception as e:
    print(f"{brick:<13} {ri:<10} {nb:>8} {'ERR':>8} {e}"); sys.exit()
dups = [e for e in root.iter() if local(e) == 'duplication']
cross = []
for dup in dups:
    files = [f.get('path') for f in dup if local(f) == 'file']
    inb = [f for f in files if f and f.startswith(brickroot)]
    inr = [f for f in files if f and f.startswith(riroot)]
    if inb and inr:
        frag = [x.text for x in dup if local(x) == 'codefragment']
        cross.append((int(dup.get('lines')), int(dup.get('tokens')), inb[0], inr[0],
                      (frag[0] if frag else '')))
cross.sort(reverse=True)
# Report the overall clone count too: zero there means a broken harness, not a clean result.
detail = f"(total clones toutes origines: {len(dups)})"
if cross:
    detail = f"max {cross[0][0]} lignes / {cross[0][1]} tokens  " + detail
print(f"{brick:<13} {ri:<10} {nb:>8} {len(cross):>8} {detail}")
with open(xmlf.replace('.xml', '.cross.txt'), 'w') as fh:
    for l, t, b, r, code in cross:
        fh.write(f"{l} lignes / {t} tokens\n  VIDOCQ: {os.path.relpath(b, brickroot)}\n"
                 f"  RI    : {os.path.relpath(r, riroot)}\n{code.strip()}\n\n{'-'*70}\n\n")
PY
done
