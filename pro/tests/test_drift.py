"""Verdict tests for rgc-drift, against purpose-built git histories."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "bin", "rgc-drift")


class Repo:
    def __init__(self, path):
        self.path = path
        self.shas = {}
        self.git("init", "-q")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "T")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.path, check=True,
                              capture_output=True, text=True).stdout

    def write(self, rel, body):
        full = os.path.join(self.path, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as fh:
            fh.write(body)

    def commit(self, label):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", label)
        self.shas[label] = self.git("rev-parse", "HEAD").strip()[:8]

    def verdicts(self):
        out = subprocess.run([sys.executable, TOOL, "--json", "-n", "50"],
                             cwd=self.path, capture_output=True, text=True)
        data = json.loads(out.stdout)
        by_sha = {c["sha"][:8]: c["verdict"] for c in data["commits"]}
        return {label: by_sha[sha] for label, sha in self.shas.items()}, data


class DriftVerdicts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp(prefix="rgc-drift-test-")
        r = Repo(cls.dir)

        r.write("src/app.py", "def charge(n):\n    return n\n")
        r.commit("root-with-code")

        r.write("tests/test_app.py",
                "def test_charge_returns_amount():\n    assert charge(5) == 5\n")
        r.commit("tests-only")

        r.write("src/app.py", "def charge(n):\n    if n < 0:\n"
                              "        raise ValueError\n    return n\n")
        r.write("tests/test_app.py",
                "def test_charge_returns_amount():\n    assert charge(5) == 5\n"
                "def test_charge_rejects_negative():\n    pass\n")
        r.commit("prod-and-test")

        r.git("mv", "src/app.py", "src/billing.py")
        r.commit("pure-rename")

        r.write("src/billing.py",
                "def charge(n, currency='INR'):\n"
                "    if n < 0:\n        raise ValueError\n"
                "    if currency not in ('INR', 'USD'):\n"
                "        raise ValueError\n"
                "    return n\n\n"
                "def refund(n):\n    return -n\n")
        r.commit("prod-only-substantive")

        r.git("mv", "src/billing.py", "src/payments.py")
        r.write("src/payments.py",
                "def charge(n, currency='INR', tier='std'):\n"
                "    rate = 0.9 if tier == 'gold' else 1.0\n"
                "    if n < 0:\n        raise ValueError\n"
                "    return n * rate\n\n"
                "def refund(n, fee=0):\n    return -(n - fee)\n")
        r.commit("move-and-edit")

        r.write("src/payments.py",
                "def charge(n, tier='std'):\n    return n\n\n"
                "def refund(n):\n    return -n\n")
        r.write("tests/test_app.py",
                "def test_charge_returns_amount():\n    assert charge(5) == 5\n")
        r.commit("prod-change-tests-shrink")

        r.write("docs/guide.md", "# guide\n")
        r.commit("docs-only")

        r.write("tests/test_refund.py",
                "def test_refund_applies_fee():\n    assert refund(10, 2) == -8\n")
        r.commit("red-half")

        r.write("src/payments.py",
                "def charge(n, tier='std'):\n    return n\n\n"
                "def refund(n, fee=0):\n"
                "    if fee > n:\n        raise ValueError\n"
                "    return -(n - fee)\n")
        r.commit("green-half")

        cls.verdicts, cls.summary = r.verdicts()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir, ignore_errors=True)

    def assertVerdict(self, label, expected):
        self.assertEqual(self.verdicts[label], expected,
                         f"{label}: expected {expected}, "
                         f"got {self.verdicts[label]}")

    def test_testsOnlyCommit_isGradedRed(self):
        self.assertVerdict("tests-only", "red")

    def test_prodAndTestTogether_isGradedGreen(self):
        self.assertVerdict("prod-and-test", "green")

    def test_pureRename_isGradedStructural(self):
        self.assertVerdict("pure-rename", "structural")

    def test_prodOnlySubstantive_isGradedUnprotected(self):
        self.assertVerdict("prod-only-substantive", "unprotected")

    def test_moveAndEditInOneCommit_isGradedMixed(self):
        self.assertVerdict("move-and-edit", "mixed")

    def test_testsShrinkAlongsideProdChange_isGradedTestCut(self):
        self.assertVerdict("prod-change-tests-shrink", "test-cut")

    def test_docsOnly_isGradedScaffold(self):
        self.assertVerdict("docs-only", "scaffold")

    def test_rootCommit_isNotGradedAsUnprotected(self):
        self.assertVerdict("root-with-code", "scaffold")

    def test_prodOnlyCommitFollowingRed_isGradedGreen(self):
        self.assertVerdict("green-half", "green")

    def test_summaryCountsOnlyGradeableCommits(self):
        self.assertEqual(
            self.summary["gradeable"],
            len(self.verdicts) - sum(
                1 for v in self.verdicts.values() if v == "scaffold"),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
