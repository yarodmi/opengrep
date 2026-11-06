import importlib.util
from pathlib import Path
import sys
import unittest

spec = importlib.util.spec_from_file_location("compare", Path(__file__).with_name("compare.py"))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class ComparisonTests(unittest.TestCase):
    def test_all_five_ids_and_duplicate_multiplicity(self):
        expected = c.Counter((i, "a.py", 1) for i in c.IDS)
        expected["B602", "a.py", 1] += 1
        actual = expected.copy()
        actual["B602", "a.py", 1] -= 1
        actual["B307", "b.py", 2] += 1
        rows = c.compare(expected, actual)
        self.assertEqual(set(rows), set(c.IDS))
        self.assertEqual(rows["B602"], {"matched": 1, "missing": [["a.py", 1]], "extra": []})
        self.assertEqual(rows["B307"], {"matched": 1, "missing": [], "extra": [["b.py", 2]]})
        self.assertTrue(all(rows[i]["matched"] == 1 for i in c.IDS))

    def test_normalization_preserves_paths_lines_and_ignores_only_unscoped_bandit_ids(self):
        root = Path("/corpus/examples")
        bandit = {"results": [
            {"test_id": i, "filename": f"/corpus/examples/nested/{i}.py", "line_number": n}
            for n, i in enumerate(c.IDS, 1)
        ] + [{"test_id": "B999"}]}
        opengrep = {"results": [
            {"check_id": f"prefix.{i}", "path": f"examples/nested/{i}.py", "start": {"line": n}}
            for n, i in enumerate(c.IDS, 1)
        ]}
        self.assertEqual(c.findings(bandit, root, "bandit"), c.findings(opengrep, root, "opengrep"))
        opengrep["results"][0]["start"]["line"] = 99
        rows = c.compare(c.findings(bandit, root, "bandit"), c.findings(opengrep, root, "opengrep"))
        self.assertEqual(rows["B602"]["missing"], [["nested/B602.py", 1]])
        self.assertEqual(rows["B602"]["extra"], [["nested/B602.py", 99]])

    def test_invalid_paths_rule_ids_and_lines_fail(self):
        with self.assertRaises(ValueError):
            c.relative("/outside/a.py", Path("/corpus/examples"))
        for check, line in (("B999", 1), ("B602", 0)):
            with self.subTest(check=check, line=line), self.assertRaises(ValueError):
                c.findings({"results": [{"check_id": check, "path": "/corpus/examples/a.py",
                                        "start": {"line": line}}]}, Path("/corpus/examples"), "opengrep")

    def test_process_failures_are_not_clean_scans(self):
        with self.assertRaises(RuntimeError):
            c.run([sys.executable, "-c", "raise SystemExit(2)"])
        self.assertEqual(c.run([sys.executable, "-c", "raise SystemExit(1)"], (0, 1)).returncode, 1)

    def test_empty_or_unaccounted_corpus_fails(self):
        with self.assertRaises(ValueError):
            c.validate_coverage({"errors": [], "metrics": {}}, {"paths": {"scanned": []}, "errors": []},
                                Path("/not-an-existing-corpus"))


if __name__ == "__main__":
    unittest.main()
