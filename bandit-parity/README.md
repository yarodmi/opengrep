# Bandit 1.9.4 parity rules

Five Python rules for **B602, B307, B301, B506, B324**. Their scope follows
Bandit's IDs: B301 also covers dill, shelve, jsonpickle and pandas; B324
includes weak `crypt` methods. No other checks are implemented.

## Rerun

Use the existing pinned tools, without building opengrep or installing globally:

```sh
cd /path/to/your/opengrep-fork
export PATH="$HOME/opengrep-bandit/bin:$HOME/opengrep-bandit/.venv/bin:$PATH"
opengrep --version          # 1.33.1
bandit --version            # 1.9.4
opengrep --test --jobs 2 bandit-parity/rules
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s bandit-parity -p test_compare.py -v
python3 bandit-parity/compare.py --output "$HOME/opengrep-bandit/results"
```

The comparator defaults to `~/opengrep-bandit/bandit-src/examples` and checks
the clean tag commit `92ae8b82fb422a639f0ed8d99e96cea769594e08`. Override
`--corpus`, `--bandit`, or `--opengrep` for the same pinned setup elsewhere.
It runs Bandit with default settings, then selects the five IDs from its output.
It scans every Python corpus file with opengrep and these five rules. It never
filters candidate findings using the reference answer.

Comparison is a **multiset of (check ID, examples-relative file, starting line)**.
Rule-ID prefixes and paths are normalized; messages, severity, confidence,
columns and end lines are not compared. B602 focuses the shell value because
Bandit reports that argument's line, not necessarily the call's first line.
Exit status: 0 parity, 1 missing/extra findings, 2 execution/coverage/version error.

The output directory contains raw `bandit.json`, `opengrep.json`, stderr logs,
and `comparison.json` with per-check counts, all differences, commands, tool
versions, corpus digest, errors and coverage. Nothing is written into bandit-src.

## Important semantics and limits

Rules disable constant propagation to follow Bandit's syntax-based decisions.
`shell="False"` is truthy; absent/false/empty shell arguments are not findings.
SafeLoader and CSafeLoader are excluded, as are non-security weak hashes.
Suppression patterns recognize real `# nosec` comments, scoped IDs and plugin
names, and distinguish them from strings containing `#nosec`. The suppression
token registry is pinned to Bandit 1.9.4, not an extra set of security rules.
Use `--disable-nosem` when scanning for Bandit parity so opengrep-specific
suppression comments do not remove findings Bandit would report.

The reference has three syntax-error files: `new_candidates-none.py`,
`nonsense.py`, and `nonsense2.py`. They remain in the scan inventory and errors
are disclosed, never silently excluded. Corpus parity is not proof of equivalent
behavior on arbitrary Python programs. Severity/message equivalence, other
Bandit checks, and full-program semantic equivalence are not claimed.

## Corpus result

| Check | Matched | Missing | Extra |
| --- | ---: | ---: | ---: |
| B602 | 28 | 0 | 0 |
| B307 | 3 | 0 | 0 |
| B301 | 13 | 0 | 0 |
| B506 | 3 | 0 | 0 |
| B324 | 24 | 0 | 0 |

All 94 Python files are accounted for. Bandit reports the three syntax errors
above; opengrep reports partial parsing of `nonsense2.py`. These numbers
describe reported findings, not successful parsing of every file.
