#!/bin/sh
# Import the user module under each variant and optimization level.
# rc=0 is a clean import, rc=139 is SIGSEGV.
set -e
cd "$(dirname "$0")"
printf '%-10s %-4s %s\n' variant opt result
for opt in O0 O1 O2 O3; do
  for variant in before after before_va after_va; do
    rm -f ratlike.c user_*.c ./*.so
    python setup.py "$variant" "$opt" >/dev/null 2>&1
    rc=0
    sh -c 'python -c "import user; user.check()"' >/dev/null 2>&1 || rc=$?
    case $rc in
      0)   result="ok" ;;
      139) result="SIGSEGV" ;;
      *)   result="rc=$rc" ;;
    esac
    printf '%-10s %-4s %s\n' "$variant" "$opt" "$result"
  done
done
rm -f ratlike.c user_*.c ./*.so
rm -rf build
