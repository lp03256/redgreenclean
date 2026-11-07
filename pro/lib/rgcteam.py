"""Team-tier analysis: fix detection, defect correlation, trend, coaching."""

import re
import subprocess
from collections import Counter, defaultdict

from rgcdrift import PROBLEMS

FIX_WORDS = re.compile(
    r"\b(fix(e[sd])?|bugfix|hotfix|patch(e[sd])?|revert(s|ed)?|correct(s|ed)?"
    r"|repair(s|ed)?|resolve[sd]?)\b"
    r"|\b(def|bug|issue)[-_ ]?\d+\b",
    re.IGNORECASE,
)

HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? ")
OLD_FILE = re.compile(r"^--- (?:a/)?(.+)$")


def is_fix(subject):
    return bool(FIX_WORDS.search(subject or ""))


def trend(rows):
    buckets = defaultdict(lambda: {"gradeable": 0, "problems": 0})
    for r in rows:
        period = r["date"][:7]
        if r["verdict"] == "scaffold":
            buckets[period]
            continue
        buckets[period]["gradeable"] += 1
        if r["verdict"] in PROBLEMS:
            buckets[period]["problems"] += 1
    out = []
    for period in sorted(buckets):
        b = buckets[period]
        pct = (b["problems"] / b["gradeable"] * 100) if b["gradeable"] else 0.0
        out.append({"period": period, "gradeable": b["gradeable"],
                    "problems": b["problems"], "pct": round(pct, 1)})
    return out


def coaching(counts):
    graded = sum(n for v, n in counts.items() if v != "scaffold")
    if not graded:
        return []
    share = lambda v: counts.get(v, 0) / graded
    advice = []
    if share("unprotected") > 0.25:
        advice.append(
            "Most changes arrive without a test in the same commit. Write the "
            "failing test first — see /rgc-rhythm."
        )
    if share("mixed") > 0.15:
        advice.append(
            "Moving code and changing it land together. Separate them into two "
            "commits so a reviewer can actually read the diff — see /rgc-tidy."
        )
    if share("test-cut") > 0.10:
        advice.append(
            "Tests shrink alongside production changes. When a test blocks a "
            "change, decide deliberately whether the test or the code is wrong."
        )
    if share("red") == 0 and graded >= 10:
        advice.append(
            "No test-only commits at all. Committing the failing test on its "
            "own records what you set out to do — see /rgc-rhythm."
        )
    return advice


def _git(repo, *args):
    out = subprocess.run(["git", *args], cwd=repo, capture_output=True,
                         text=True, check=False)
    return out.stdout if out.returncode == 0 else ""


def changed_ranges(repo, sha):
    """Old-side line ranges a commit touched, per file, in its parent."""
    diff = _git(repo, "show", "--format=", "--unified=0", "--no-color", sha)
    ranges = defaultdict(list)
    path = None
    for line in diff.split("\n"):
        m = OLD_FILE.match(line)
        if m:
            path = None if m.group(1) == "/dev/null" else m.group(1)
            continue
        m = HUNK.match(line)
        if m and path:
            start = int(m.group(1))
            count = int(m.group(2)) if m.group(2) is not None else 1
            if count == 0:
                # pure insertion: blame the code it was inserted against
                lo = max(1, start)
                ranges[path].append((lo, lo + 1))
            else:
                ranges[path].append((start, start + count - 1))
    return ranges


def blame_origins(repo, sha, ranges):
    origins = set()
    for path, spans in ranges.items():
        for lo, hi in spans:
            out = _git(repo, "blame", "--porcelain", f"-L{lo},{hi}",
                       f"{sha}^", "--", path)
            for line in out.split("\n"):
                m = re.match(r"^([0-9a-f]{40}) ", line)
                if m:
                    origins.add(m.group(1))
    return origins


def correlate(repo, rows):
    verdict_of = {r["sha"]: r["verdict"] for r in rows}
    graded = [r for r in rows if r["verdict"] != "scaffold"]
    base_problems = sum(1 for r in graded if r["verdict"] in PROBLEMS)
    base_rate = (base_problems / len(graded) * 100) if graded else 0.0

    fixes = [r for r in rows if is_fix(r["subject"])]
    origins = set()
    for f in fixes:
        if not f["parents"]:
            continue
        origins |= blame_origins(repo, f["sha"], changed_ranges(repo, f["sha"]))

    known = [s for s in origins if s in verdict_of
             and verdict_of[s] != "scaffold" and s not in
             {f["sha"] for f in fixes}]
    verdicts = Counter(verdict_of[s] for s in known)
    origin_problems = sum(verdicts[v] for v in PROBLEMS)
    origin_rate = (origin_problems / len(known) * 100) if known else 0.0

    return {
        "fix_commits": len(fixes),
        "origin_shas": sorted(known),
        "origin_verdicts": dict(verdicts),
        "origins_traced": len(known),
        "base_rate": round(base_rate, 1),
        "origin_problem_rate": round(origin_rate, 1),
        "lift": round(origin_rate / base_rate, 2) if base_rate else None,
    }
