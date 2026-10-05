#!/bin/sh
# Build the compiler and compare it against the reference on all cases.
# Needs test/urbit135, see test/mkoracle.py.
cd "$(dirname "$0")"
clang -O2 hc.c -o hc || exit 1
# for the cases, checked for undefined behavior as it runs
clang hc.c -g3 -Wall -Wextra -Wconversion -Wdouble-promotion -Wno-unused-parameter \
  -Wno-unused-function -Wno-sign-conversion -fsanitize=undefined -fsanitize-trap -o hc-debug || exit 1
# with a table of where the time goes, on stderr
clang -O2 -DPROFILE hc.c -o hc-prof || exit 1
KERNEL=${KERNEL:-$HOME/Desktop/urbit/pkg/arvo/sys/hoon.hoon}

check() {
  printf '%s: ' "$*"
  test/cmp.py "$@" | tail -1
}

# the parser's cases, compiled against %noun
for f in ../test/cases[0-9]*.txt; do check -m m "$f"; done
check -m m ../test/cases_open.txt
check -m m ../test/cases_play.txt
# compiling against %noun, then against the kernel's type
check -m m test/cases_mint.txt
check -m k -k "$KERNEL" test/cases_kernel.txt
# whole files, as the kernel chain compiles them, with the kernel the
# reference runs as the compiling kernel: slow, so only with -f
if [ "$1" = -f ]; then
  S=$(dirname "$KERNEL")
  printf 'hoon.hoon: '; test/files.py "$S/hoon.hoon" | tail -1
  printf 'arvo.hoon: '; test/files.py -s "$S/hoon.hoon" "$S/arvo.hoon" | tail -1
  # lull against ..part in arvo, as arvo builds it, and zuse against lull
  printf 'lull.hoon: '; test/files.py -s "$S/hoon.hoon" -s "$S/arvo.hoon" -e ..part "$S/lull.hoon" | tail -1
  printf 'zuse.hoon: '; test/files.py -s "$S/hoon.hoon" -s "$S/arvo.hoon" -e ..part -s "$S/lull.hoon" \
    "$S/zuse.hoon" | tail -1
  # desk files through ford, with imports, against zuse as arvo builds it,
  # with -S: /$ in herm, /% in sur/hood, /* in merge
  D=$(dirname "$S")
  printf 'desk: '; test/desk.py -S "$S/hoon.hoon" -S "$S/arvo.hoon" -e ..part -S "$S/lull.hoon" \
    -S "$S/zuse.hoon" "$D" app/dojo.hoon lib/default-agent.hoon lib/pprint.hoon mar/json.hoon \
    gen/hood/commit.hoon app/herm.hoon sur/hood.hoon gen/hood/merge.hoon 2>/dev/null | tail -1
fi
