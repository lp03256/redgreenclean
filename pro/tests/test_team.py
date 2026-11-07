"""Tests for the team-tier analysis: fix detection, correlation, trend."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "lib"))

import rgcdrift          # noqa: E402
import rgcteam           # noqa: E402


class FixDetection(unittest.TestCase):
    def test_isFix_givenCommonFixWording_returnsTrue(self):
        for subject in ("fix rounding error", "Fix: null on empty cart",
                        "bugfix for DEF-1021", "hotfix stock check",
                        "revert bad merge", "correct off-by-one",
                        "DEF1021 wrong total", "patch overflow"):
            self.assertTrue(rgcteam.is_fix(subject), subject)

    def test_isFix_givenWordsThatMerelyContainFix_returnsFalse(self):
        for subject in ("add prefix to ids", "build test fixtures",
                        "add suffix handling", "refactor fixture loader"):
            self.assertFalse(rgcteam.is_fix(subject), subject)

    def test_isFix_givenFeatureWork_returnsFalse(self):
        for subject in ("add backorder support", "extract validator",
                        "rename order to billing"):
            self.assertFalse(rgcteam.is_fix(subject), subject)


class Trend(unittest.TestCase):
    def test_trend_groupsCommitsByMonthAndCountsProblems(self):
        rows = [
            {"date": "2026-03-04T10:00:00+00:00", "verdict": "unprotected"},
            {"date": "2026-03-20T10:00:00+00:00", "verdict": "green"},
            {"date": "2026-04-02T10:00:00+00:00", "verdict": "green"},
            {"date": "2026-04-09T10:00:00+00:00", "verdict": "scaffold"},
        ]
        got = rgcteam.trend(rows)
        self.assertEqual([p["period"] for p in got], ["2026-03", "2026-04"])
        self.assertEqual(got[0]["gradeable"], 2)
        self.assertEqual(got[0]["problems"], 1)
        self.assertEqual(got[1]["gradeable"], 1)
        self.assertEqual(got[1]["problems"], 0)

    def test_trend_excludesScaffoldFromGradeableCount(self):
        rows = [{"date": "2026-05-01T00:00:00+00:00", "verdict": "scaffold"}]
        self.assertEqual(rgcteam.trend(rows)[0]["gradeable"], 0)


class Coaching(unittest.TestCase):
    def test_coaching_givenManyUnprotected_recommendsWritingTestsFirst(self):
        advice = rgcteam.coaching({"unprotected": 8, "green": 2})
        self.assertTrue(any("test" in a.lower() for a in advice))

    def test_coaching_givenManyMixed_recommendsSeparatingCommits(self):
        advice = rgcteam.coaching({"mixed": 6, "green": 4})
        self.assertTrue(any("separate" in a.lower() or "split" in a.lower()
                            for a in advice))

    def test_coaching_givenCleanHistory_returnsNoAdvice(self):
        self.assertEqual(rgcteam.coaching({"green": 10, "red": 5}), [])


class Correlation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp(prefix="rgc-team-test-")
        g = lambda *a: subprocess.run(["git", *a], cwd=cls.dir, check=True,
                                      capture_output=True, text=True)
        w = lambda rel, body: (
            os.makedirs(os.path.join(cls.dir, os.path.dirname(rel)),
                        exist_ok=True),
            open(os.path.join(cls.dir, rel), "w").write(body))
        g("init", "-q")
        g("config", "user.email", "t@example.com")
        g("config", "user.name", "T")

        w("README.md", "# x\n")
        g("add", "-A"); g("commit", "-q", "-m", "root")

        w("tests/test_t.py", "def test_total():\n    assert total([1]) == 1\n")
        g("add", "-A"); g("commit", "-q", "-m", "add total test")
        w("src/t.py", "def total(xs):\n    return sum(xs)\n")
        g("add", "-A"); g("commit", "-q", "-m", "implement total")

        # the commit that will later need fixing: production only, no test
        w("src/t.py",
          "def total(xs):\n    return sum(xs)\n\n"
          "def average(xs):\n    return sum(xs) / len(xs)\n\n"
          "def median(xs):\n    return sorted(xs)[len(xs) // 2]\n")
        g("add", "-A"); g("commit", "-q", "-m", "add average and median")
        cls.culprit = g("rev-parse", "HEAD").stdout.strip()

        w("src/t.py",
          "def total(xs):\n    return sum(xs)\n\n"
          "def average(xs):\n"
          "    if not xs:\n        return 0\n"
          "    return sum(xs) / len(xs)\n\n"
          "def median(xs):\n    return sorted(xs)[len(xs) // 2]\n")
        g("add", "-A"); g("commit", "-q", "-m", "fix divide by zero in average")

        cls.rows = rgcdrift.analyse(None, None, 50, None)
        cls.result = rgcteam.correlate(cls.dir, cls.rows)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir, ignore_errors=True)

    def test_correlate_findsTheFixCommit(self):
        self.assertEqual(self.result["fix_commits"], 1)

    def test_correlate_blamesTheCommitThatIntroducedTheFixedLines(self):
        origins = self.result["origin_shas"]
        self.assertIn(self.culprit[:8], [s[:8] for s in origins])

    def test_correlate_reportsVerdictOfOriginCommits(self):
        self.assertEqual(self.result["origin_verdicts"].get("unprotected"), 1)

    def test_correlate_reportsBaseRateForComparison(self):
        self.assertGreater(self.result["base_rate"], 0)
        self.assertLessEqual(self.result["base_rate"], 100)


if __name__ == "__main__":
    unittest.main(verbosity=2)
