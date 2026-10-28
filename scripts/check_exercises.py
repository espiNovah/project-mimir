#!/usr/bin/env python3
"""Check every exercise in exercises/: the starter must FAIL its tests and the
reference solution must PASS them.

For each exercise folder (one that has a solution/ subfolder) this script:

1. copies the exercise, without solution/, to a temp dir and runs its tests,
   expecting at least one failure (the starter is a stub or a buggy script);
2. copies each file in solution/ over the matching starter file and runs the
   tests again, expecting every test to pass.

Python exercises run with pytest under the current interpreter, so run this
script inside the exercises environment:

    uv run --project exercises python scripts/check_exercises.py

JS/TS exercises run with `node --test` (Node 22.18+). Pass --skip-node to check
only the Python sets on a machine without Node.

Usage: check_exercises.py [--skip-node] [-j N] [PATH ...]
PATH filters by set or exercise, e.g. `exercises/regex` or `regex/01_extract_emails`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXERCISES = ROOT / "exercises"
TIMEOUT = 180


@dataclass
class Result:
    name: str
    ok: bool
    detail: str = ""


def find_exercises() -> list[Path]:
    return sorted(p.parent for p in EXERCISES.glob("*/*/solution") if p.is_dir())


def language(ex: Path) -> str:
    if list(ex.glob("test_*.py")):
        return "python"
    if list(ex.glob("*.test.js")) or list(ex.glob("*.test.ts")):
        return "node"
    return "unknown"


def node_cmd() -> list[str]:
    """`node --test`, adding the type-stripping flag on Node versions that need it."""
    out = subprocess.run(
        ["node", "-p", "process.features.typescript ? 1 : 0"], capture_output=True, text=True
    )
    flags = [] if out.stdout.strip() not in ("0", "") else ["--experimental-strip-types"]
    return ["node", *flags, "--test"]


def run_tests(ex_dir: Path, lang: str, node: list[str]) -> tuple[int, str, int, int]:
    """Run the tests in ex_dir. Returns (returncode, output, n_tests, n_failed)."""
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "NO_COLOR": "1"}
    if lang == "python":
        cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rN", "."]
    else:
        tests = sorted(str(p.name) for p in ex_dir.iterdir() if re.search(r"\.test\.(js|ts)$", p.name))
        cmd = [*node, "--test-reporter=tap", *tests]
    try:
        proc = subprocess.run(
            cmd, cwd=ex_dir, capture_output=True, text=True, timeout=TIMEOUT, env=env
        )
    except subprocess.TimeoutExpired:
        return 124, "timed out", 0, 0
    out = proc.stdout + proc.stderr
    if lang == "python":
        passed = sum(int(n) for n in re.findall(r"(\d+) passed", out))
        failed = sum(int(n) for n in re.findall(r"(\d+) (?:failed|error)", out))
        return proc.returncode, out, passed + failed, failed
    n = re.search(r"^# tests (\d+)", out, re.M)
    f = re.search(r"^# fail (\d+)", out, re.M)
    return proc.returncode, out, int(n.group(1)) if n else 0, int(f.group(1)) if f else 0


def tail(text: str, lines: int = 25) -> str:
    return "\n".join("    " + line for line in text.strip().splitlines()[-lines:])


def check(ex: Path, node: list[str] | None) -> Result:
    name = str(ex.relative_to(EXERCISES))
    lang = language(ex)
    if lang == "unknown":
        return Result(name, False, "no test file found")
    if lang == "node" and node is None:
        return Result(name, True, "skipped (no Node)")
    if not (ex / "README.md").exists():
        return Result(name, False, "missing README.md")
    solution_files = [p for p in (ex / "solution").rglob("*") if p.is_file()]
    if not solution_files:
        return Result(name, False, "solution/ is empty")
    for sol in solution_files:
        if not (ex / sol.relative_to(ex / "solution")).exists():
            return Result(name, False, f"solution file {sol.name} has no matching starter file")

    with tempfile.TemporaryDirectory(prefix="mimir-ex-") as tmp:
        work = Path(tmp) / ex.name
        shutil.copytree(
            ex, work, ignore=shutil.ignore_patterns("solution", "__pycache__", ".pytest_cache")
        )
        if lang == "node":
            (work / "package.json").write_text(json.dumps({"type": "module"}))

        # 1. Starter must fail (with real test failures, not a crash or zero tests).
        rc, out, n, failed = run_tests(work, lang, node or [])
        if rc == 0:
            return Result(name, False, "starter PASSES its tests (it should fail)")
        if n == 0 or failed == 0:
            return Result(name, False, f"starter run broke instead of failing tests (rc={rc})\n{tail(out)}")
        if lang == "python" and rc != 1:
            return Result(name, False, f"starter run errored (pytest rc={rc}), expected test failures\n{tail(out)}")

        # 2. Solution must pass.
        for sol in solution_files:
            shutil.copy2(sol, work / sol.relative_to(ex / "solution"))
        rc, out, n, failed = run_tests(work, lang, node or [])
        if rc != 0 or n == 0:
            return Result(name, False, f"solution FAILS its tests (rc={rc})\n{tail(out)}")
        return Result(name, True, f"{n} tests; starter fails, solution passes")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="limit to these sets or exercises")
    ap.add_argument("--skip-node", action="store_true", help="skip JS/TS exercises")
    ap.add_argument("-j", "--jobs", type=int, default=os.cpu_count() or 4)
    args = ap.parse_args()

    exercises = find_exercises()
    if args.paths:
        wanted = [Path(p).as_posix().removeprefix("exercises/").strip("/") for p in args.paths]
        exercises = [
            e for e in exercises
            if any(str(e.relative_to(EXERCISES)).startswith(w) for w in wanted)
        ]
    if not exercises:
        print("No exercises found.", file=sys.stderr)
        return 1

    node: list[str] | None = None
    needs_node = any(language(e) == "node" for e in exercises)
    if needs_node and not args.skip_node:
        if shutil.which("node") is None:
            print("Node is not installed. Install Node 22.18+ or pass --skip-node.", file=sys.stderr)
            return 1
        node = node_cmd()

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(lambda e: check(e, node), exercises))

    bad = [r for r in results if not r.ok]
    for r in results:
        print(f"{'PASS' if r.ok else 'FAIL'}  {r.name}  {r.detail.splitlines()[0] if r.detail else ''}")
        if not r.ok and "\n" in r.detail:
            print("\n".join(r.detail.splitlines()[1:]))
    sets = sorted({r.name.split("/")[0] for r in results})
    print(f"\n{len(results) - len(bad)}/{len(results)} exercises OK across {len(sets)} sets.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
