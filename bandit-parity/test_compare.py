"""Independent controls for the comparison instrument, not security rules."""

from collections import Counter
import importlib.util
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "compare", Path(__file__).with_name("compare.py")
)
compare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compare)


class ComparisonTests(unittest.TestCase):
    def test_equal_and_deliberate_difference(self):
        key = ("B602", "a.py", 3)
        equal = compare.compare(Counter({key: 1}), Counter({key: 1}))
        self.assertTrue(equal["findings_match"])
        self.assertEqual(equal["counts"]["B602"]["matched"], 1)
        changed = compare.compare(
            Counter({key: 2}), Counter({key: 1, ("B307", "b.py", 8): 1})
        )
        self.assertFalse(changed["findings_match"])
        self.assertEqual(changed["missing"], [
            {"check": "B602", "path": "a.py", "line": 3, "count": 1}
        ])
        self.assertEqual(changed["extra"], [
            {"check": "B307", "path": "b.py", "line": 8, "count": 1}
        ])

    def test_duplicate_and_line_identity(self):
        a, b = ("B301", "a.py", 1), ("B301", "a.py", 2)
        result = compare.compare(Counter({a: 1}), Counter({a: 2, b: 1}))
        self.assertEqual(result["counts"]["B301"]["extra"], 2)
        self.assertFalse(result["findings_match"])

    def test_path_normalization_mapping_and_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corpus = root / "examples"
            corpus.mkdir()
            expected = compare.identities({"results": [
                {"test_id": "B301", "filename": str(corpus / "a.py"), "line_number": 4},
                {"test_id": "B999", "filename": "/outside.py", "line_number": 1},
            ]}, "bandit", corpus, root, {})
            actual = compare.identities({"results": [
                {"check_id": "custom", "path": "examples/./a.py", "start": {"line": 4}},
            ]}, "opengrep", corpus, root, {"custom": "B301"})
            self.assertEqual(expected, actual)
            with self.assertRaises(ValueError):
                compare.relative_path("../outside.py", corpus, root)
            with self.assertRaises(KeyError):
                compare.identities({"results": [
                    {"check_id": "unmapped", "path": "examples/a.py", "start": {"line": 4}},
                ]}, "opengrep", corpus, root, {})

    def test_coverage_fails_closed_for_errors_and_nonfinding_file_omission(self):
        with tempfile.TemporaryDirectory() as tmp:
            corpus = Path(tmp) / "examples"
            corpus.mkdir()
            for name in ("finding.py", "nonfinding.py"):
                (corpus / name).touch()
            bandit = {"metrics": {str(p): {} for p in corpus.glob("*.py")},
                      "errors": []}
            opengrep = {"paths": {"scanned": [str(p) for p in corpus.glob("*.py")]},
                        "errors": []}
            details = compare.coverage(bandit, opengrep, corpus, corpus.parent)
            self.assertTrue(compare.is_complete(details))
            opengrep["paths"]["scanned"].remove(str(corpus / "nonfinding.py"))
            details = compare.coverage(bandit, opengrep, corpus, corpus.parent)
            self.assertFalse(compare.is_complete(details))
            self.assertEqual(details["opengrep_unscanned_files"], ["nonfinding.py"])
            details["opengrep_unscanned_files"] = []
            details["unexpected_bandit_errors"] = [{"filename": "known-broken.py"}]
            self.assertFalse(compare.is_complete(details))

    def test_baseline_parse_limits_do_not_exclude_findings_or_new_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            corpus = Path(tmp) / "examples"
            corpus.mkdir()
            broken, valid = corpus / "broken.py", corpus / "valid.py"
            broken.touch()
            valid.touch()
            bandit = {
                "metrics": {str(broken): {}, str(valid): {}},
                "errors": [{"filename": str(broken),
                            "reason": "syntax error while parsing AST from file"}],
            }
            error = {"path": str(broken), "type": ["PartialParsing", []]}
            opengrep = {
                "paths": {
                    "scanned": [str(broken), str(valid)],
                    "skipped": [{"path": str(broken),
                                 "reason": "analysis_failed_parser_or_internal_error"}],
                },
                "errors": [error],
            }
            details = compare.coverage(bandit, opengrep, corpus, corpus.parent)
            self.assertTrue(compare.is_complete(details))
            self.assertFalse(details["both_tools_parsed_every_file"])
            actual = compare.identities({"results": [
                {"check_id": "B301", "path": str(broken), "start": {"line": 1}}
            ]}, "opengrep", corpus, corpus.parent, {"B301": "B301"})
            self.assertEqual(compare.compare(Counter(), actual)["counts"]["B301"]["extra"], 1)
            error["path"] = str(valid)
            details = compare.coverage(bandit, opengrep, corpus, corpus.parent)
            self.assertFalse(compare.is_complete(details))


if __name__ == "__main__":
    unittest.main()
