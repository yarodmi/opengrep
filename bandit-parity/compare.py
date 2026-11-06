#!/usr/bin/env python3
"""Compare unfiltered scanner findings on the pinned Bandit examples corpus."""

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

IDS = ("B602", "B307", "B301", "B506", "B324")
COMMIT = "92ae8b82fb422a639f0ed8d99e96cea769594e08"
REFERENCE_ERRORS = {"new_candidates-none.py", "nonsense.py", "nonsense2.py"}
HERE = Path(__file__).resolve().parent
HOME = Path.home() / "opengrep-bandit"


def relative(filename, corpus):
    """Do not flatten basenames or permit findings outside the corpus."""
    path = Path(filename)
    if not path.is_absolute():
        path = corpus.parent / path
    return path.resolve().relative_to(corpus.resolve()).as_posix()


def findings(document, corpus, tool):
    result = Counter()
    for row in document["results"]:
        check = row["test_id"] if tool == "bandit" else row["check_id"].split(".")[-1]
        if check not in IDS:
            if tool == "bandit":
                continue
            raise ValueError(f"Unexpected opengrep rule: {check}")
        file = row["filename"] if tool == "bandit" else row["path"]
        line = row["line_number"] if tool == "bandit" else row["start"]["line"]
        if not isinstance(line, int) or line < 1:
            raise ValueError(f"Invalid finding line: {line}")
        result[check, relative(file, corpus), line] += 1
    return result


def compare(expected, actual):
    common, missing, extra = expected & actual, expected - actual, actual - expected
    return {
        check: {
            "matched": sum(n for key, n in common.items() if key[0] == check),
            "missing": [list(key[1:]) for key in sorted(missing.elements()) if key[0] == check],
            "extra": [list(key[1:]) for key in sorted(extra.elements()) if key[0] == check],
        }
        for check in IDS
    }


def run(command, allowed=(0,)):
    completed = subprocess.run(
        [str(arg) for arg in command],
        capture_output=True, text=True, timeout=120,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        cwd=HOME if HOME.exists() else HERE,
    )
    if completed.returncode not in allowed:
        raise RuntimeError(
            f"{command[0]} exited {completed.returncode}: {completed.stderr.strip()}"
        )
    return completed


def run_json(command, output, allowed=(0,)):
    # Bandit's progress display precedes JSON on stdout even without a TTY.
    # Use each tool's output-file option instead of stripping arbitrary text.
    output.unlink(missing_ok=True)
    completed = run([*command, "--output", output], allowed)
    output.with_suffix(".stderr.txt").write_text(completed.stderr)
    output.with_suffix(".stdout.txt").write_text(completed.stdout)
    document = json.loads(output.read_text())
    if not isinstance(document.get("results"), list):
        raise ValueError(f"Missing results array in {output}")
    return document


def corpus_digest(corpus):
    digest = hashlib.sha256()
    for file in sorted(p for p in corpus.rglob("*") if p.is_file()):
        digest.update(file.relative_to(corpus).as_posix().encode() + b"\0")
        digest.update(file.read_bytes())
    return "sha256:" + digest.hexdigest()


def validate_coverage(bandit, opengrep, corpus):
    owed = {p.relative_to(corpus).as_posix() for p in corpus.rglob("*.py")}
    if not owed:
        raise ValueError("Empty corpus")
    b_errors = bandit["errors"]
    error_files = {relative(e["filename"], corpus) for e in b_errors}
    if error_files != REFERENCE_ERRORS or any(
        e["reason"] != "syntax error while parsing AST from file" for e in b_errors
    ):
        raise ValueError(f"Unexpected Bandit errors: {b_errors}")
    b_scanned = {
        relative(p, corpus) for p in bandit["metrics"] if p != "_totals"
    }
    o_scanned = {relative(p, corpus) for p in opengrep["paths"]["scanned"]}
    if (b_scanned | error_files) != owed or o_scanned != owed:
        raise ValueError(
            f"Coverage mismatch: Bandit missing={sorted(owed - b_scanned - error_files)}, "
            f"opengrep missing={sorted(owed - o_scanned)}, "
            f"unexpected paths={sorted((b_scanned | error_files | o_scanned) - owed)}"
        )
    for error in opengrep["errors"]:
        kind = error["type"]
        kind = kind[0] if isinstance(kind, list) else kind
        if (
            kind not in ("PartialParsing", "ParseError")
            or relative(error["path"], corpus) not in REFERENCE_ERRORS
        ):
            raise ValueError(f"Unexpected opengrep error: {error}")
    return {
        "owed_python_files": len(owed),
        "bandit_scanned": len(b_scanned),
        "bandit_syntax_errors": sorted(error_files),
        "opengrep_scanned": len(o_scanned),
        "opengrep_errors": opengrep["errors"],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=HOME / "bandit-src/examples")
    parser.add_argument("--output", type=Path, default=HOME / "results")
    parser.add_argument("--bandit", default=shutil.which("bandit") or str(HOME / ".venv/bin/bandit"))
    parser.add_argument("--opengrep", default=shutil.which("opengrep") or str(HOME / "bin/opengrep"))
    args = parser.parse_args(argv)
    corpus = args.corpus.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if output.is_relative_to(corpus.parent):
        raise ValueError("Output must not modify the reference checkout")
    head = run(["git", "-C", corpus.parent, "rev-parse", "HEAD"]).stdout.strip()
    dirty = run(["git", "-C", corpus.parent, "status", "--porcelain"]).stdout
    if head != COMMIT or dirty:
        raise ValueError("Reference must be the clean Bandit 1.9.4 checkout")
    versions = {
        "bandit": run([args.bandit, "--version"]).stdout.strip(),
        "opengrep": run([args.opengrep, "--version"]).stdout.strip(),
    }
    if versions["bandit"].splitlines()[0] != "bandit 1.9.4" or versions["opengrep"] != "1.33.1":
        raise ValueError(f"Wrong tool versions: {versions}")
    before = corpus_digest(corpus)
    output.mkdir(parents=True, exist_ok=True)
    b_command = [args.bandit, "-r", corpus, "-f", "json"]
    # Explicit Python paths bypass default ignore lists, without excluding errors.
    o_command = [
        args.opengrep, "scan", "--config", HERE / "rules", "--json",
        "--no-rewrite-rule-ids", "--jobs", "2", "--no-git-ignore",
        "--disable-nosem", "--max-target-bytes", "0",
        *sorted(corpus.rglob("*.py")),
    ]
    bandit = run_json(b_command, output / "bandit.json", allowed=(0, 1))
    opengrep = run_json(o_command, output / "opengrep.json")
    coverage = validate_coverage(bandit, opengrep, corpus)
    after = corpus_digest(corpus)
    if before != after:
        raise ValueError("Reference corpus changed during comparison")
    table = compare(findings(bandit, corpus, "bandit"), findings(opengrep, corpus, "opengrep"))
    report = {
        "versions": versions, "reference_commit": head, "corpus_digest": after,
        "comparison": "multiset(check ID, examples-relative path, starting line)",
        "commands": [
            [str(a) for a in [*command, "--output", output / f"{tool}.json"]]
            for command, tool in ((b_command, "bandit"), (o_command, "opengrep"))
        ],
        "coverage": coverage, "checks": table,
    }
    (output / "comparison.json").write_text(json.dumps(report, indent=2) + "\n")
    print("| Check | Matched | Missing | Extra |")
    print("| --- | ---: | ---: | ---: |")
    for check, row in table.items():
        print(f"| {check} | {row['matched']} | {len(row['missing'])} | {len(row['extra'])} |")
        for kind in ("missing", "extra"):
            for file, line in row[kind]:
                print(f"  {kind}: {check} {file}:{line}", file=sys.stderr)
    print(f"\nCoverage: {json.dumps(coverage)}")
    print(f"Raw output and detailed report: {output}")
    return int(any(row["missing"] or row["extra"] for row in table.values()))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"Comparison failed: {error}", file=sys.stderr)
        sys.exit(2)
