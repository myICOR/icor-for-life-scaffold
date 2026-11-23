#!/bin/bash
# Every suite, from the repository root. Exit 1 if any fails.
cd "$(dirname "$0")/.." || exit 1
rc=0
for t in tests/test-vault.py tests/check-bases.py tests/test-note-scripts.py tests/test-life-snapshot.py tests/test-link-dates-to-daily-notes.py tests/test-guard.py tests/test-migrate.py tests/test-tidy.py; do
  out=$(python3 -B "$t" 2>&1); code=$?
  echo "$(echo "$out" | tail -1)   ($t)"
  [ $code -eq 0 ] || { rc=1; echo "$out" | grep -E "FAIL" | head -20; }
done
exit $rc
