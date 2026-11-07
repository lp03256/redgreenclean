"""Commit classification shared by rgc-drift and rgc-report."""

import re
import subprocess
import sys


TEST_PATH = re.compile(
    r"(^|/)(tests?|specs?|__tests__|testdata)(/|$)"
    r"|(^|/)test_[^/]+$"
    r"|_test\.(go|py|rb|rs|js|ts)$"
    r"|[.-](test|spec)\.(js|jsx|ts|tsx|mjs)$"
    r"|Tests?\.(java|kt|cs|scala)$"
    r"|Spec\.(java|kt|scala|groovy)$",
    re.IGNORECASE,
)

BUILD_PATH = re.compile(
    r"(^|/)(package(-lock)?\.json|pnpm-lock\.yaml|yarn\.lock|go\.(mod|sum)"
    r"|pom\.xml|build\.gradle(\.kts)?|Cargo\.(toml|lock)|requirements.*\.txt"
    r"|Gemfile(\.lock)?|\.gitignore|Dockerfile|Makefile)$"
    r"|(^|/)(\.github|\.gitlab|ci|docs?)(/|$)"
    r"|\.(md|txt|rst|yml|yaml|toml|ini|cfg|lock)$",
    re.IGNORECASE,
)

RENAME_THRESHOLD = "30%"
TRIVIAL_CHURN = 3


def git(*args):
    out = subprocess.run(
        ["git", *args], capture_output=True, text=True, check=False
    )
    if out.returncode != 0:
        sys.exit(f"git {' '.join(args)}: {out.stderr.strip()}")
    return out.stdout


def classify_path(path):
    if TEST_PATH.search(path):
        return "test"
    if BUILD_PATH.search(path):
        return "scaffold"
    return "prod"


def read_commits(rev_range, subdir, limit, extra_since):
    sep = "\x1e"
    args = ["log", f"--format={sep}%H{sep}%an{sep}%aI{sep}%P{sep}%s",
            f"--find-renames={RENAME_THRESHOLD}", "--no-merges", "--numstat"]
    if limit:
        args.append(f"-n{limit}")
    if extra_since:
        args.append(f"--since={extra_since}")
    if rev_range:
        args.append(rev_range)
    if subdir:
        args += ["--", subdir]
    return parse_log(git(*args), sep)


def resolve_rename(path):
    """git renders renames as 'a/{old.py => new.py}' or 'old.py => new.py'."""
    if " => " not in path:
        return path, False
    brace = re.search(r"\{([^{}]*) => ([^{}]*)\}", path)
    if brace:
        return path[:brace.start()] + brace.group(2) + path[brace.end():], True
    return path.split(" => ", 1)[1], True


def parse_log(raw, sep):
    commits = []
    current = None
    for line in raw.split("\n"):
        if line.startswith(sep):
            sha, author, date, parents, subject = line[1:].split(sep, 4)
            current = {"sha": sha, "author": author, "date": date,
                       "parents": parents.split(), "subject": subject.strip(),
                       "files": [], "renames": 0}
            commits.append(current)
            continue
        if current is None or not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        add, dele, raw_path = parts
        path, renamed = resolve_rename(raw_path)
        if renamed:
            current["renames"] += 1
        current["files"].append({
            "path": path,
            "kind": classify_path(path),
            "add": 0 if add == "-" else int(add),
            "dele": 0 if dele == "-" else int(dele),
            "renamed": renamed,
        })
    return commits


def git_quiet(*args):
    out = subprocess.run(["git", *args], capture_output=True, text=True,
                         check=False)
    return out.stdout if out.returncode == 0 else None


def move_pairs(commit):
    """Find delete-here/add-there pairs git declined to call a rename."""
    prod = [f for f in commit["files"]
            if f["kind"] == "prod" and not f["renamed"]]
    gone = [f for f in prod if f["add"] == 0 and f["dele"] >= 5]
    came = [f for f in prod if f["dele"] == 0 and f["add"] >= 5]
    pairs = []
    claimed = set()
    for g in gone:
        for c in came:
            if c["path"] in claimed:
                continue
            lo, hi = sorted((g["dele"], c["add"]))
            if hi <= lo * 2:
                pairs.append((g["path"], c["path"]))
                claimed.add(c["path"])
                break
    return pairs


def is_pure_move(sha, old, new):
    before = git_quiet("show", f"{sha}^:{old}")
    after = git_quiet("show", f"{sha}:{new}")
    if before is None or after is None:
        return True
    squash = lambda s: "\n".join(
        ln.strip() for ln in s.split("\n") if ln.strip()
    )
    return squash(before) == squash(after)


def churn(files, kind=None, exclude_renamed=False):
    return sum(
        f["add"] + f["dele"]
        for f in files
        if (kind is None or f["kind"] == kind)
        and not (exclude_renamed and f["renamed"])
    )


def classify(commit):
    if not commit["parents"]:
        return "scaffold", "root commit, nothing behind it to protect"

    files = commit["files"]
    prod = [f for f in files if f["kind"] == "prod"]
    tests = [f for f in files if f["kind"] == "test"]

    if not prod and not tests:
        return "scaffold", "no production or test code touched"

    prod_churn = churn(prod, exclude_renamed=True)
    test_churn = churn(tests, exclude_renamed=True)
    test_added = sum(f["add"] for f in tests)
    test_deleted = sum(f["dele"] for f in tests)

    has_moves = commit["renames"] > 0

    if has_moves and prod_churn > TRIVIAL_CHURN:
        return "mixed", (
            f"{commit['renames']} file move(s) plus {prod_churn} edited lines "
            "in one commit"
        )

    for old, new in move_pairs(commit):
        if not is_pure_move(commit["sha"], old, new):
            has_moves = True
            return "mixed", (
                f"{old} moved to {new} and its contents changed in the "
                "same commit"
            )

    if not prod:
        if test_added > test_deleted:
            return "red", f"tests only, +{test_added} lines"
        return "test-cut", f"tests only, net -{test_deleted - test_added} lines"

    if not tests:
        if has_moves or prod_churn <= TRIVIAL_CHURN:
            return "structural", "moves or near-zero churn, no test change"
        return "unprotected", (
            f"{prod_churn} lines of production code changed, no test touched"
        )

    if test_deleted > test_added and prod_churn > 0:
        return "test-cut", (
            f"production changed while tests shrank by "
            f"{test_deleted - test_added} lines"
        )

    return "green", f"prod +{prod_churn}, tests +{test_churn}"


VERDICTS = {
    "red":          ("RED       ", "test written first"),
    "green":        ("GREEN     ", "prod and test together"),
    "structural":   ("STRUCTURAL", "moves only, behaviour unchanged"),
    "scaffold":     ("SCAFFOLD  ", "config, docs, deps"),
    "mixed":        ("MIXED     ", "structural and behavioural in one commit"),
    "unprotected":  ("UNPROTECT ", "behaviour changed with no test"),
    "test-cut":     ("TEST-CUT  ", "tests weakened alongside a change"),
}
PROBLEMS = {"mixed", "unprotected", "test-cut"}


def pair_red_and_green(rows):
    """A prod-only commit directly after a test-only commit is its green half."""
    for newer, older in zip(rows, rows[1:]):
        if newer["verdict"] == "unprotected" and older["verdict"] == "red":
            newer["verdict"] = "green"
            newer["why"] = "production code completing the preceding red commit"
    return rows


def analyse(rev_range=None, subdir=None, limit=None, since=None):
    commits = read_commits(rev_range, subdir, limit, since)
    rows = []
    for c in commits:
        verdict, why = classify(c)
        rows.append({**c, "verdict": verdict, "why": why})
    return pair_red_and_green(rows)
