#!/bin/bash
# Pass 3: structural similarity (JPlag / Greedy String Tiling) between each Vidocq brick and
# the reference implementation of the same specification.
#
# CPD compares raw token windows; JPlag works on a parsed, language-aware token stream, so it
# still matches code that was renamed, reordered or restructured. This is the pass that
# addresses limit 1 of PROVENANCE-AUDIT.md §5.
#
# Prerequisites:
#   cd provenance-audit && mvn -q dependency:build-classpath -Dmdep.outputFile=cp.txt
#   bash provenance-audit/fetch-corpus.sh
#
# Usage:
#   MIN_TOKENS=9 bash provenance-audit/jplag.sh
set -uo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
WS=$(cd "$HERE/.." && pwd)
CORPUS=$HERE/corpus
CP=$(cat "$HERE/cp.txt")
MIN=${MIN_TOKENS:-9}          # JPlag's default for Java; lower = more sensitive
STAGE=$HERE/stage
OUT=$HERE/reports-jplag-$MIN
mkdir -p "$OUT"

# JPlag takes a directory whose sub-directories are the submissions to compare, so each pair
# is staged as <brick>/{vidocq,ri}. Copies, not symlinks: JPlag resolves real paths.
echo "=== compilation du runner ==="
javac -cp "$CP" -d "$HERE" "$HERE/JPlagRunner.java" 2>&1 | head -5 || exit 1

# JPlag parses through the javac API, and JavacAdapter picks ONE charset for the whole
# submission via FileUtils.detectCharsetFromMultiple(). On a mostly-ASCII tree holding a few
# UTF-8 files it settles on windows-1252, javac then reports "unmappable character", and the
# entire submission is discarded (this silently killed ravel, mansart and champollion).
#
# Fix: make every staged file pure ASCII by escaping non-ASCII characters as \uXXXX — exactly
# what the old native2ascii tool did. The source stays *semantically identical* (Java resolves
# these escapes before lexing) so tokens are unchanged, and charset detection can no longer
# get it wrong. Deleting the bytes instead would corrupt the code: it turned a character
# literal into an empty one and broke champollion.
ascii_escape() {
  python3 - "$1" <<'PY'
import sys, pathlib
root = pathlib.Path(sys.argv[1])
for f in root.rglob("*.java"):
    try:
        raw = f.read_bytes()
        if all(b < 0x80 for b in raw):
            continue
        text = raw.decode("utf-8", errors="replace")
        out = "".join(c if ord(c) < 128 else "\\u%04x" % ord(c) for c in text)
        f.write_text(out, encoding="ascii")
    except Exception:
        pass
PY
}

# Stage one Vidocq brick. Each Maven module goes into its own sub-directory: modules share
# the io/vidocq/<brick> package root, so a flat copy would let same-named files (every
# module-info.java) overwrite each other.
stage_brick() {
  local brick=$1 dest=$2 i=0
  local src
  src=$(find "$WS/$brick" -type d -path "*/src/main/java" 2>/dev/null \
        | grep -v "/target/" | grep -v "/\.claude/" | grep -v "/\.tck-cache/" | head -60)
  [ -z "$src" ] && return 1
  for d in $src; do
    i=$((i+1)); mkdir -p "$dest/m$i"
    (cd "$d" && find . -name "*.java" | tar cf - -T - 2>/dev/null) | tar xf - -C "$dest/m$i/" 2>/dev/null
  done
  return 0
}

run_pair() { # label leftDir rightDir   (dirs already staged)
  java -cp "$CP:$HERE" JPlagRunner "$2" "$MIN" "$1" 2>"$OUT/$1.err" | tee -a "$OUT/summary.txt"
}

pairs="vauban:cdi champollion:json cassini:jaxrs foy:servlet chappe:http ravel:mpconfig \
knock:mphealth dirac:mpmetrics heisenberg:mpft grimm:mpopenapi cervantes:mpjwt cyrano:mprest mansart:jpa"

printf "%-13s %8s %10s  %s\n" "BRIQUE" "SIMIL." "TOKENS" "DETAIL"
for p in $pairs; do
  brick=${p%%:*}; ri=${p##*:}
  st=$STAGE/$brick
  rm -rf "$st"; mkdir -p "$st/vidocq" "$st/ri"
  if ! stage_brick "$brick" "$st/vidocq"; then
    printf "%-13s %8s %10s  %s\n" "$brick" "-" "-" "pas de src/main/java"; continue
  fi
  (cd "$CORPUS/$ri" && find . -name "*.java" | tar cf - -T - 2>/dev/null) | tar xf - -C "$st/ri/" 2>/dev/null
  ascii_escape "$st"
  run_pair "$brick" "$st"
done

# --- Calibration ----------------------------------------------------------------------
# A raw percentage is meaningless without a scale. Two controls bound it:
#   negative — two unrelated Java projects: the floor imposed by sharing a language and an
#              ecosystem, i.e. what "no relationship" looks like;
#   positive — two releases of the SAME project: what genuinely shared lineage looks like.
# A brick's score must be read against those two, never in absolute terms.
if [ "${CALIBRATE:-1}" = "1" ]; then
  echo
  printf "%-13s %8s %10s  %s\n" "CALIBRATION" "SIMIL." "TOKENS" "DETAIL"
  ctl=$STAGE/_ctl_neg; rm -rf "$ctl"; mkdir -p "$ctl/a" "$ctl/b"
  (cd "$CORPUS/cdi" && find . -name "*.java" | tar cf - -T - 2>/dev/null) | tar xf - -C "$ctl/a/" 2>/dev/null
  (cd "$CORPUS/jpa" && find . -name "*.java" | tar cf - -T - 2>/dev/null) | tar xf - -C "$ctl/b/" 2>/dev/null
  ascii_escape "$ctl"; run_pair "neg:weld-hib" "$ctl"

  pos=$STAGE/_ctl_pos; rm -rf "$pos"; mkdir -p "$pos/a" "$pos/b"
  w5=$(find "$CORPUS/cdi" -maxdepth 1 -type d -name "weld-core-impl-5*" | head -1)
  w6=$(find "$CORPUS/cdi" -maxdepth 1 -type d -name "weld-core-impl-6*" | head -1)
  if [ -n "$w5" ] && [ -n "$w6" ]; then
    (cd "$w5" && find . -name "*.java" | tar cf - -T - 2>/dev/null) | tar xf - -C "$pos/a/" 2>/dev/null
    (cd "$w6" && find . -name "*.java" | tar cf - -T - 2>/dev/null) | tar xf - -C "$pos/b/" 2>/dev/null
    ascii_escape "$pos"; run_pair "pos:weld5-6" "$pos"
  fi
fi
rm -rf "$STAGE"
echo
echo "Rapports: $OUT/"
