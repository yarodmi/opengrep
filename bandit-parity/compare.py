#!/usr/bin/env python3
"""Run pinned tools and compare finding multisets on Bandit's examples.

Exit 0: complete default-output evidence and equal findings; 1: differing findings;
2: incomplete scan, invalid tool/provenance, or malformed output.
No tool output is supplied or edited by the caller.
Bandit's per-file syntax errors define baseline coverage limitations, not
findings exclusions. Additional Opengrep parse failures are incomplete evidence.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


CHECKS = ("B602", "B307", "B301", "B506", "B324")
BANDIT_COMMIT = "92ae8b82fb422a639f0ed8d99e96cea769594e08"


def run(command, cwd, timeout=180):
    result = subprocess.run(
        [str(arg) for arg in command], cwd=cwd, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
    )
    return {
        "command": [str(arg) for arg in command],
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def relative_path(filename, corpus, cwd):
    """Normalize actual tool paths, rejecting findings outside the corpus."""
    path = Path(filename)
    if not path.is_absolute():
        path = cwd / path
    return path.resolve().relative_to(corpus.resolve()).as_posix()


def identities(data, tool, corpus, cwd, rule_ids):
    findings = Counter()
    for result in data["results"]:
        if tool == "bandit":
            check = result["test_id"]
            if check not in CHECKS:
                continue
            filename, line = result["filename"], result["line_number"]
        else:
            check = rule_ids[result["check_id"]]
            filename, line = result["path"], result["start"]["line"]
        if type(line) is not int or line < 1:
            raise ValueError(f"Invalid finding line: {line!r}")
        findings[check, relative_path(filename, corpus, cwd), line] += 1
    return findings


def records(counter):
    return [
        {"check": check, "path": path, "line": line, "count": count}
        for (check, path, line), count in sorted(counter.items())
    ]


def compare(expected, actual):
    matched, missing, extra = expected & actual, expected - actual, actual - expected
    return {
        "counts": {
            check: {
                name: sum(n for key, n in counter.items() if key[0] == check)
                for name, counter in (
                    ("bandit", expected), ("opengrep", actual),
                    ("matched", matched), ("missing", missing), ("extra", extra),
                )
            }
            for check in CHECKS
        },
        "findings_match": not missing and not extra,
        "matched": records(matched),
        "missing": records(missing),
        "extra": records(extra),
    }


def coverage(bandit, opengrep, corpus, cwd):
    expected = {p.relative_to(corpus).as_posix() for p in corpus.rglob("*.py")}
    bandit_paths = {
        relative_path(p, corpus, cwd)
        for p in bandit["metrics"] if p != "_totals"
    }
    scanned = {
        relative_path(p, corpus, cwd) for p in opengrep["paths"]["scanned"]
    }
    baseline_parse_errors = {
        relative_path(error["filename"], corpus, cwd)
        for error in bandit["errors"]
        if error["reason"] == "syntax error while parsing AST from file"
    }
    unexpected_bandit_errors = [
        error for error in bandit["errors"]
        if error["reason"] != "syntax error while parsing AST from file"
    ]
    baseline_opengrep_parse_paths = set()
    unexpected_opengrep_errors = []
    for error in opengrep["errors"]:
        kind = error["type"]
        if isinstance(kind, list):
            kind = kind[0]
        path = relative_path(error["path"], corpus, cwd) if error.get("path") else None
        if (kind in ("Syntax error", "Other syntax error", "PartialParsing")
                and path in baseline_parse_errors):
            baseline_opengrep_parse_paths.add(path)
        else:
            unexpected_opengrep_errors.append(error)
    skipped, unexpected_skips = [], []
    for item in opengrep["paths"].get("skipped", []):
        try:
            path = relative_path(item["path"], corpus, cwd)
        except ValueError:
            continue
        if path in expected:
            skipped.append(item)
            if not (path in baseline_opengrep_parse_paths
                    and item["reason"] == "analysis_failed_parser_or_internal_error"):
                unexpected_skips.append(item)
    return {
        "python_files": len(expected),
        "bandit_accounted_files": len(bandit_paths),
        "opengrep_scanned_files": len(scanned),
        "bandit_unaccounted_files": sorted(expected - bandit_paths),
        "opengrep_unscanned_files": sorted(expected - scanned),
        "opengrep_skipped_python_files": skipped,
        "bandit_errors": bandit["errors"],
        "opengrep_errors": opengrep["errors"],
        "bandit_syntax_error_files": sorted(baseline_parse_errors),
        "unexpected_bandit_errors": unexpected_bandit_errors,
        "unexpected_opengrep_errors": unexpected_opengrep_errors,
        "unexpected_opengrep_skips": unexpected_skips,
        "opengrep_skipped_rules": opengrep.get("skipped_rules", []),
        "both_tools_parsed_every_file": not (
            bandit["errors"] or opengrep["errors"] or skipped
            or expected - bandit_paths or expected - scanned
        ),
    }


def is_complete(details):
    return not any(details[key] for key in (
        "bandit_unaccounted_files", "opengrep_unscanned_files",
        "unexpected_opengrep_skips", "unexpected_bandit_errors",
        "unexpected_opengrep_errors", "opengrep_skipped_rules",
    ))


def git_value(source, *args):
    result = run(["git", "-C", source, *args], source)
    if result["returncode"]:
        raise ValueError(f"Git provenance check failed: {result['stderr']}")
    return result["stdout"].strip()


def provenance(corpus):
    source = corpus.parent
    head = git_value(source, "rev-parse", "HEAD")
    tag = git_value(source, "rev-parse", "1.9.4^{commit}")
    dirty = git_value(source, "status", "--porcelain", "--untracked-files=all")
    if corpus.name != "examples" or head != BANDIT_COMMIT or tag != head or dirty:
        raise ValueError(
            "Corpus must be unmodified examples/ at Bandit tag 1.9.4 "
            f"({BANDIT_COMMIT}); head={head}, tag={tag}, dirty={bool(dirty)}"
        )
    return {"bandit_source_commit": head, "bandit_source_tag": "1.9.4",
            "bandit_source_clean": True, "corpus": str(corpus)}


def check_version(executable, version, cwd):
    result = run([executable, "--version"], cwd)
    text = result["stdout"] + result["stderr"]
    if result["returncode"] or not re.search(
        rf"(?<![\d.]){re.escape(version)}(?![\d.])", text
    ):
        raise ValueError(f"Expected {executable} version {version}, got {text!r}")
    return result


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path,
                        default=Path("~/opengrep-bandit/bandit-src/examples"))
    parser.add_argument("--bandit", type=Path,
                        default=Path("~/opengrep-bandit/.venv/bin/bandit"))
    parser.add_argument("--opengrep", default="opengrep")
    parser.add_argument("--rules", type=Path,
                        default=Path(__file__).resolve().parent / "rules",
                        help="Rule directory or YAML file")
    parser.add_argument("--rule-id", action="append", default=[], metavar="RULE=CHECK",
                        help="Explicit Opengrep rule ID to Bandit ID mapping")
    parser.add_argument("--json-report", type=Path, help="Write full comparison report")
    parser.add_argument("--evidence-dir", type=Path,
                        help="Save untouched tool stdout/stderr plus invocation metadata")
    return parser.parse_args()


def main():
    args = parse_args()
    report = {"status": "incomplete", "complete": False, "findings_match": False}
    exit_code = 2
    try:
        corpus = args.corpus.expanduser().resolve()
        rules = args.rules.expanduser().resolve()
        cwd = corpus.parent
        if not corpus.is_dir() or not rules.exists():
            raise ValueError("Corpus directory and rule path must exist")
        report.update(provenance(corpus))
        rule_ids = {check: check for check in CHECKS}
        for mapping in args.rule_id:
            rule, check = mapping.split("=", 1)
            if not rule or check not in CHECKS:
                raise ValueError(f"Invalid rule mapping: {mapping}")
            rule_ids[rule] = check
        bandit = str(args.bandit.expanduser().resolve())
        opengrep = str(Path(args.opengrep).expanduser()) if "/" in args.opengrep else args.opengrep
        report["versions"] = {
            "bandit": check_version(bandit, "1.9.4", cwd),
            "opengrep": check_version(opengrep, "1.33.1", cwd),
        }
        report["rule_ids"] = rule_ids
        invocations = {
            "bandit": [bandit, "-r", corpus, "-f", "json"],
            "opengrep": [
                opengrep, "--config", rules, "--json",
                "--disable-version-check", "--no-rewrite-rule-ids",
                "--no-git-ignore", "--disable-nosem", "--include", "*.py",
                "--max-target-bytes", "0", "--timeout", "0", "--verbose", corpus,
            ],
        }
        outputs = {}
        report["invocations"] = outputs
        data = {}
        for tool, command in invocations.items():
            with tempfile.TemporaryDirectory(prefix="bandit-parity-") as temporary:
                if tool == "bandit":
                    json_path = Path(temporary) / "bandit.json"
                    command += ["-o", json_path]
                output = run(command, cwd)
                # Rich writes Bandit's progress display to stdout, even with
                # JSON formatting. Ask Bandit to write its JSON file directly.
                output["json_output"] = (
                    json_path.read_text() if tool == "bandit" and json_path.exists()
                    else output["stdout"]
                )
            outputs[tool] = output
            if args.evidence_dir:
                folder = args.evidence_dir.expanduser().resolve()
                folder.mkdir(parents=True, exist_ok=True)
                for stream in ("stdout", "stderr"):
                    (folder / f"{tool}.{stream}.txt").write_text(output[stream])
                (folder / f"{tool}.json").write_text(output["json_output"])
                (folder / f"{tool}.invocation.json").write_text(
                    json.dumps({k: v for k, v in output.items()
                                if k not in ("stdout", "stderr", "json_output")}, indent=2) + "\n"
                )
            data[tool] = json.loads(output["json_output"])
        report.update(compare(
            identities(data["bandit"], "bandit", corpus, cwd, rule_ids),
            identities(data["opengrep"], "opengrep", corpus, cwd, rule_ids),
        ))
        report["coverage"] = coverage(data["bandit"], data["opengrep"], corpus, cwd)
        report["unexpected_exit_codes"] = {
            tool: output["returncode"] for tool, output in outputs.items()
            if output["returncode"] not in ((0, 1) if tool == "bandit" else (0,))
        }
        report["complete"] = (
            is_complete(report["coverage"]) and not report["unexpected_exit_codes"]
        )
        if report["complete"]:
            report["status"] = "pass" if report["findings_match"] else "mismatch"
            exit_code = 0 if report["findings_match"] else 1
        print("Check  Bandit  Opengrep  Matched  Missing  Extra")
        for check, counts in report["counts"].items():
            print(f"{check:5}  {counts['bandit']:6}  {counts['opengrep']:8}  "
                  f"{counts['matched']:7}  {counts['missing']:7}  {counts['extra']:5}")
        for name in ("missing", "extra"):
            for item in report[name]:
                print(f"{name.upper()}: {item['check']} {item['path']}:"
                      f"{item['line']} x{item['count']}")
        print("Coverage: " + json.dumps(report["coverage"], sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        report["error"] = str(error)
        print(f"ERROR: {error}", file=sys.stderr)
    print(f"Status: {report['status']}; findings_match={report['findings_match']}; "
          f"complete={report['complete']}")
    if args.json_report:
        path = args.json_report.expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
