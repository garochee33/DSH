#!/usr/bin/env python3
"""Tests for the /implement skill memory file helper.

Run from the workspace root:

    python3 .grok/skills/implement/tests/test_memory.py

Or with pytest:

    pytest .grok/skills/implement/tests/test_memory.py -v

Stdlib only (matches the helper's dependency profile). Multiprocessing is used
for the locking smoke test.
"""

from __future__ import annotations

import importlib.util
import json
import multiprocessing as mp
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Locate the helper module by file path so the test file can live in a sibling
# directory without requiring a package layout.
_HERE = Path(__file__).resolve().parent
_HELPER = _HERE.parent / "scripts" / "memory.py"

_spec = importlib.util.spec_from_file_location("implement_memory_helper", _HELPER)
assert _spec is not None and _spec.loader is not None, f"Could not load {_HELPER}"
memory = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(memory)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _run_helper(repo_dir: Path, *args: str, stdin: str = "", env: dict | None = None):
    """Run memory.py as a subprocess and return (rc, stdout, stderr)."""
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    result = subprocess.run(
        [sys.executable, str(_HELPER), *args],
        cwd=str(repo_dir),
        input=stdin,
        capture_output=True,
        text=True,
        env=full_env,
        timeout=30,
    )
    return result.returncode, result.stdout, result.stderr


def _git_init(repo_dir: Path, remote: str | None = None) -> None:
    repo_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=str(repo_dir), check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(repo_dir),
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(repo_dir),
        check=True,
    )
    if remote:
        subprocess.run(
            ["git", "remote", "add", "origin", remote],
            cwd=str(repo_dir),
            check=True,
        )


# ---------------------------------------------------------------------------
# Pure-function tests (no subprocess; in-process module)
# ---------------------------------------------------------------------------


class TestCanonicalizeRemote(unittest.TestCase):
    def test_collapses_ssh_https_with_and_without_dot_git(self):
        variants = [
            "git@github.com:owner/repo.git",
            "git@github.com:owner/repo",
            # Bare SSH shorthand (no `user@`); common with ~/.ssh/config
            # `Host github.com\n  User git` mappings, where the username is
            # supplied by ssh_config rather than the URL.
            "github.com:owner/repo",
            "github.com:owner/repo.git",
            "https://github.com/owner/repo.git",
            "https://github.com/owner/repo",
            "https://user@github.com/owner/repo.git",
            "HTTPS://GitHub.com/owner/repo.git/",
            "ssh://git@github.com/owner/repo.git",
            # Round 2: explicit ports
            "ssh://git@github.com:22/owner/repo.git",
            "https://github.com:443/owner/repo.git",
            # Round 2: case-insensitive host means path is also lowercased
            # for known forges (github/gitlab/bitbucket)
            "https://github.com/Owner/Repo.git",
            "git@GITHUB.COM:OWNER/REPO.git",
            "GITHUB.COM:OWNER/REPO.git",
            # Round 2: doubled .git suffix
            "https://github.com/owner/repo.git.git",
        ]
        canonical = {memory.canonicalize_remote(v) for v in variants}
        self.assertEqual(
            canonical,
            {"github.com/owner/repo"},
            f"Expected one canonical form, got {canonical}",
        )

    def test_case_sensitive_forge_preserves_path_case(self):
        # Non-listed hosts (e.g., a self-hosted Gitea) must preserve path case.
        a = memory.canonicalize_remote("https://gitea.example.com/Owner/Repo.git")
        b = memory.canonicalize_remote("https://gitea.example.com/owner/repo.git")
        self.assertNotEqual(a, b)

    def test_different_repos_dont_collapse(self):
        a = memory.canonicalize_remote("git@github.com:owner/a.git")
        b = memory.canonicalize_remote("git@github.com:owner/b.git")
        self.assertNotEqual(a, b)

    def test_unparseable_url_returned_as_is(self):
        self.assertEqual(
            memory.canonicalize_remote("not-a-url"),
            "not-a-url",
        )


class TestNormalize(unittest.TestCase):
    def test_case_insensitive(self):
        self.assertEqual(
            memory.normalize("Foo Bar"),
            memory.normalize("foo BAR"),
        )

    def test_strips_trailing_punctuation_and_collapses_whitespace(self):
        self.assertEqual(
            memory.normalize("missing  null check on input."),
            memory.normalize("Missing null check on input"),
        )


class TestSanitizeOneLine(unittest.TestCase):
    def test_collapses_only_line_breaking_whitespace(self):
        # Newlines and tabs collapse to spaces. Internal multi-space runs are
        # preserved (only normalize() collapses those, at the comparison layer).
        self.assertEqual(
            memory.sanitize_one_line("first\n\tsecond  third"),
            "first second  third",
        )

    def test_preserves_internal_multi_spaces(self):
        # Pathological case from round 2: a description that intentionally
        # contains multiple spaces (e.g., a code example) must round-trip.
        self.assertEqual(
            memory.sanitize_one_line("Use `   ` (3 spaces) for indent"),
            "Use `   ` (3 spaces) for indent",
        )

    def test_strips_outer_whitespace(self):
        self.assertEqual(memory.sanitize_one_line("  hi  "), "hi")


class TestParseRender(unittest.TestCase):
    """Parser/renderer round-trip and section-detection tests."""

    def test_round_trip_preserves_structure(self):
        original = (
            "# Title\n\n"
            "> Custom note.\n"
            "\n"
            "## Common Issues\n\n"
            "### Error Handling\n"
            "- Missing null check (seen 3 times)\n"
            "- Bad fallback (seen 1 time)\n"
            "\n"
            "## Recent Runs\n\n"
            '### 2026-04-23 \u2014 "First run"\n'
            "- **Rounds**: 1\n"
            "\n"
        )
        parsed = memory.parse_memory_file(original)
        rendered = memory.render_memory_file(parsed)
        # Re-parse the rendered output and compare structure
        re_parsed = memory.parse_memory_file(rendered)
        self.assertEqual(
            list(parsed["common_issues"].keys()),
            list(re_parsed["common_issues"].keys()),
        )
        self.assertEqual(
            parsed["common_issues"]["Error Handling"],
            re_parsed["common_issues"]["Error Handling"],
        )
        self.assertEqual(parsed["recent_runs"], re_parsed["recent_runs"])
        self.assertIn("Custom note.", "\n".join(re_parsed["header"]))

    def test_singular_time_form_parses_correctly(self):
        text = "## Common Issues\n\n### Cat\n- One occurrence (seen 1 time)\n"
        parsed = memory.parse_memory_file(text)
        self.assertEqual(
            parsed["common_issues"]["Cat"],
            [{"description": "One occurrence", "count": 1}],
        )

    def test_section_detection_requires_full_line_match(self):
        """A run-body line that *starts* with '## Common Issues' must NOT
        be treated as a section header. (Issue 6 from the second reviewer.)"""
        text = (
            "## Common Issues\n\n### Cat\n- A (seen 2 times)\n\n"
            "## Recent Runs\n\n"
            '### 2026-01-01 \u2014 "First"\n'
            "- **Rounds**: 1\n"
            "## Common Issues are great BTW\n"
            '### 2026-01-02 \u2014 "Second"\n'
            "- **Rounds**: 2\n"
        )
        parsed = memory.parse_memory_file(text)
        self.assertEqual(len(parsed["recent_runs"]), 2)
        self.assertEqual(parsed["recent_runs"][0]["date"], "2026-01-01")
        self.assertEqual(parsed["recent_runs"][1]["date"], "2026-01-02")
        self.assertIn(
            "## Common Issues are great BTW",
            parsed["recent_runs"][0]["body_lines"],
        )

    def test_blank_input_returns_empty_state(self):
        parsed = memory.parse_memory_file("   \n\n\n  ")
        self.assertEqual(parsed["header"], [])
        self.assertEqual(list(parsed["common_issues"].items()), [])
        self.assertEqual(parsed["recent_runs"], [])

    def test_en_dash_in_run_header_accepted(self):
        text = (
            "## Common Issues\n\n## Recent Runs\n\n"
            '### 2026-01-01 \u2013 "Uses en dash"\n- **Rounds**: 1\n'
        )
        parsed = memory.parse_memory_file(text)
        self.assertEqual(len(parsed["recent_runs"]), 1)
        self.assertEqual(parsed["recent_runs"][0]["description"], '"Uses en dash"')


class TestSeveritySummary(unittest.TestCase):
    def test_skips_zero_counts(self):
        summary, total = memory._format_severity_summary({"bug": 0, "suggestion": 1, "nit": 0})
        self.assertEqual(summary, "1 suggestion")
        self.assertEqual(total, 1)

    def test_canonical_order_then_extras_sorted(self):
        summary, total = memory._format_severity_summary(
            {"zebra": 1, "alpha": 2, "bug": 3, "nit": 1}
        )
        # bugs first, then nit (per SEVERITY_ORDER), then "alpha"/"zebra" sorted
        self.assertTrue(summary.startswith("3 bugs, 1 nit"))
        self.assertIn("2 alphas", summary)
        self.assertIn("1 zebra", summary)
        self.assertEqual(total, 7)

    def test_pluralization(self):
        summary, _ = memory._format_severity_summary({"bug": 1, "nit": 5})
        self.assertEqual(summary, "1 bug, 5 nits")


class TestMergeValidation(unittest.TestCase):
    """All malformed inputs should raise SpecError, never AttributeError."""

    def _empty_state(self):
        return memory.parse_memory_file("")

    def test_non_string_category_rejected(self):
        with self.assertRaises(memory.SpecError):
            memory.merge_run(
                self._empty_state(),
                {"patterns": [{"category": 123, "description": "ok"}]},
            )

    def test_non_string_description_rejected(self):
        with self.assertRaises(memory.SpecError):
            memory.merge_run(
                self._empty_state(),
                {"patterns": [{"category": "Cat", "description": 42}]},
            )

    def test_pattern_entry_must_be_dict(self):
        with self.assertRaises(memory.SpecError):
            memory.merge_run(
                self._empty_state(),
                {"patterns": ["not-a-dict"]},
            )

    def test_patterns_must_be_list(self):
        with self.assertRaises(memory.SpecError):
            memory.merge_run(self._empty_state(), {"patterns": "single"})

    def test_run_must_be_dict(self):
        with self.assertRaises(memory.SpecError):
            memory.merge_run(self._empty_state(), {"run": "scalar"})

    def test_run_date_calendar_invalid_rejected(self):
        for bad in ("2026-13-99", "2026-02-30", "9999-99-99"):
            with self.subTest(date=bad):
                with self.assertRaises(memory.SpecError):
                    memory.merge_run(
                        self._empty_state(),
                        {"run": {"date": bad, "description": "x"}},
                    )

    def test_run_date_string_required(self):
        with self.assertRaises(memory.SpecError):
            memory.merge_run(
                self._empty_state(),
                {"run": {"date": 20260423, "description": "x"}},
            )

    def test_run_rounds_must_be_int(self):
        for bad in ("three", 3.7, [1, 2], True):
            with self.subTest(rounds=bad):
                with self.assertRaises(memory.SpecError):
                    memory.merge_run(
                        self._empty_state(),
                        {"run": {"description": "x", "rounds": bad}},
                    )

    def test_run_key_patterns_string_rejected(self):
        with self.assertRaises(memory.SpecError):
            memory.merge_run(
                self._empty_state(),
                {"run": {"description": "x", "key_patterns": "single"}},
            )

    def test_run_specializations_string_rejected(self):
        with self.assertRaises(memory.SpecError):
            memory.merge_run(
                self._empty_state(),
                {"run": {"description": "x", "specializations": "general"}},
            )

    def test_issues_by_severity_non_int_rejected(self):
        with self.assertRaises(memory.SpecError):
            memory.merge_run(
                self._empty_state(),
                {"run": {"description": "x", "issues_by_severity": {"bug": "many"}}},
            )

    def test_issues_by_severity_must_be_dict(self):
        with self.assertRaises(memory.SpecError):
            memory.merge_run(
                self._empty_state(),
                {"run": {"description": "x", "issues_by_severity": [1, 2]}},
            )


class TestMergeBehavior(unittest.TestCase):
    def test_newline_in_description_is_collapsed(self):
        state = memory.parse_memory_file("")
        memory.merge_run(
            state,
            {"patterns": [{"category": "Cat", "description": "first\nsecond"}]},
        )
        rendered = memory.render_memory_file(state)
        # Description must live on a single line; round-trip must not lose it
        self.assertIn("first second", rendered)
        re_parsed = memory.parse_memory_file(rendered)
        self.assertEqual(
            re_parsed["common_issues"]["Cat"],
            [{"description": "first second", "count": 1}],
        )

    def test_dedup_is_case_and_punct_insensitive(self):
        state = memory.parse_memory_file("")
        memory.merge_run(
            state,
            {
                "patterns": [
                    {"category": "Cat", "description": "Missing null check"},
                    {"category": "Cat", "description": "missing  null check."},
                    {"category": "Cat", "description": "MISSING NULL CHECK"},
                ]
            },
        )
        self.assertEqual(
            state["common_issues"]["Cat"],
            [{"description": "Missing null check", "count": 3}],
        )

    def test_per_category_cap_drops_lowest_count(self):
        state = memory.parse_memory_file("")
        # 30 distinct patterns, all count=1
        spec = {"patterns": [{"category": "Cat", "description": f"variant {i}"} for i in range(30)]}
        stats = memory.merge_run(state, spec)
        self.assertIn("Cat", stats["categories_capped"])
        self.assertEqual(stats["categories_capped"]["Cat"], 5)
        self.assertEqual(len(state["common_issues"]["Cat"]), memory.MAX_PATTERNS_PER_CATEGORY)

    def test_recent_runs_cap_drops_oldest(self):
        state = memory.parse_memory_file("")
        for i in range(memory.MAX_RECENT_RUNS + 5):
            stats = memory.merge_run(
                state,
                {"run": {"date": "2026-01-01", "description": f"run {i}"}},
            )
        self.assertEqual(stats["recent_runs_dropped"], 1)
        self.assertEqual(len(state["recent_runs"]), memory.MAX_RECENT_RUNS)
        # newest at top
        self.assertEqual(
            state["recent_runs"][0]["description"],
            f'"run {memory.MAX_RECENT_RUNS + 4}"',
        )

    def test_quote_wrapping_strips_all_internal_quotes(self):
        # Round 2: descriptions with internal quotes must produce clean markup
        # (exactly one outer pair, no inner quotes that confuse markdown viewers).
        state = memory.parse_memory_file("")
        memory.merge_run(
            state,
            {"run": {"description": 'Add retry "logic" to client'}},
        )
        rendered = memory.render_memory_file(state)
        re_parsed = memory.parse_memory_file(rendered)
        desc = re_parsed["recent_runs"][0]["description"]
        # Outer quotes only — count of `"` characters must be exactly 2.
        self.assertEqual(desc.count('"'), 2)
        self.assertEqual(desc, '"Add retry logic to client"')

    def test_quote_wrapping_pathological_single_quote_char(self):
        # Round 1 [General #18]: a description that is exactly `"` must not
        # round-trip as a broken header.
        state = memory.parse_memory_file("")
        memory.merge_run(state, {"run": {"description": '"'}})
        rendered = memory.render_memory_file(state)
        re_parsed = memory.parse_memory_file(rendered)
        desc = re_parsed["recent_runs"][0]["description"]
        # The lone `"` is stripped, so the description falls back to the placeholder.
        self.assertEqual(desc, '"(no description)"')

    def test_all_zero_severities_produce_no_issues_line(self):
        # Round 2 [General-2 #15]: all-zero severities must omit the line.
        state = memory.parse_memory_file("")
        memory.merge_run(
            state,
            {
                "run": {
                    "description": "Run",
                    "issues_by_severity": {"bug": 0, "suggestion": 0, "nit": 0},
                }
            },
        )
        rendered = memory.render_memory_file(state)
        self.assertNotIn("**Issues**", rendered)

    def test_omitted_and_null_description_both_silently_skip(self):
        # Round 2 [General-2 #5]: explicit null and omission must behave the same.
        state_omitted = memory.parse_memory_file("")
        state_null = memory.parse_memory_file("")
        # Both should silently skip the entry (empty description -> skip).
        stats_omitted = memory.merge_run(state_omitted, {"patterns": [{"category": "Cat"}]})
        stats_null = memory.merge_run(
            state_null,
            {"patterns": [{"category": "Cat", "description": None}]},
        )
        self.assertEqual(stats_omitted["new_patterns"], 0)
        self.assertEqual(stats_null["new_patterns"], 0)
        self.assertEqual(stats_omitted["merged_patterns"], 0)
        self.assertEqual(stats_null["merged_patterns"], 0)

    def test_dedup_lookup_reused_across_patterns(self):
        # Round 2 [General-2 #4]: dedup work must be O(n+k), not O(n*k). We
        # verify behaviour by feeding many patterns to the same category and
        # confirming the post-state is consistent (the dict-reuse refactor
        # must not regress merging).
        state = memory.parse_memory_file("")
        spec = {
            "patterns": [
                # 5 distinct patterns, each repeated 3 times in the spec
                {"category": "C", "description": f"variant {i}"}
                for i in range(5)
                for _ in range(3)
            ]
        }
        stats = memory.merge_run(state, spec)
        self.assertEqual(stats["new_patterns"], 5)
        self.assertEqual(stats["merged_patterns"], 10)
        # Every variant has count == 3 (1 add + 2 merges)
        for entry in state["common_issues"]["C"]:
            self.assertEqual(entry["count"], 3)


class TestSnapshotPayload(unittest.TestCase):
    def test_build_snapshot_shape(self):
        state = memory.parse_memory_file(
            "## Common Issues\n\n### Cat\n- A (seen 2 times)\n- B (seen 1 time)\n\n"
            '## Recent Runs\n\n### 2026-04-23 \u2014 "Run"\n- **Rounds**: 1\n'
        )
        payload = memory._build_snapshot(state, exists=True)
        self.assertTrue(payload["exists"])
        self.assertEqual(
            payload["common_issues"],
            [
                {"category": "Cat", "description": "A", "count": 2},
                {"category": "Cat", "description": "B", "count": 1},
            ],
        )
        self.assertEqual(len(payload["recent_runs"]), 1)
        self.assertEqual(payload["recent_runs"][0]["date"], "2026-04-23")


# ---------------------------------------------------------------------------
# Subprocess / CLI tests (run helper as a child process with isolated $HOME)
# ---------------------------------------------------------------------------


class CLIBase(unittest.TestCase):
    def setUp(self):
        self.test_root = Path(tempfile.mkdtemp(prefix="memory-py-test-"))
        self.home = self.test_root / "home"
        self.home.mkdir()
        self.repo_a = self.test_root / "worktree-a"
        self.repo_b = self.test_root / "worktree-b"
        self.repo_c = self.test_root / "other"
        _git_init(self.repo_a, remote="https://github.com/org/proj.git")
        _git_init(self.repo_b, remote="git@github.com:org/proj.git")  # SSH form
        _git_init(self.repo_c, remote="https://github.com/org/other.git")
        self.env = {"HOME": str(self.home)}

    def tearDown(self):
        shutil.rmtree(self.test_root, ignore_errors=True)


class TestCLI(CLIBase):
    def test_path_stable_across_canonicalised_remotes(self):
        rc_a, out_a, _ = _run_helper(self.repo_a, "path", env=self.env)
        rc_b, out_b, _ = _run_helper(self.repo_b, "path", env=self.env)
        rc_c, out_c, _ = _run_helper(self.repo_c, "path", env=self.env)
        self.assertEqual(rc_a, 0)
        self.assertEqual(rc_b, 0)
        self.assertEqual(rc_c, 0)
        # SSH and HTTPS forms of the same repo collapse onto one path
        self.assertEqual(out_a.strip(), out_b.strip())
        self.assertNotEqual(out_a.strip(), out_c.strip())

    def test_read_missing_file_is_empty(self):
        rc, out, _ = _run_helper(self.repo_a, "read", env=self.env)
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_read_does_not_create_directory(self):
        # Path/read calls must not have side effects on the directory tree
        memory_dir = self.home / ".grok" / "implement-memory"
        self.assertFalse(memory_dir.exists())
        _run_helper(self.repo_a, "path", env=self.env)
        _run_helper(self.repo_a, "read", env=self.env)
        _run_helper(self.repo_a, "snapshot", env=self.env)
        self.assertFalse(memory_dir.exists())

    def test_first_update_creates_file_with_existed_before_false(self):
        spec = json.dumps(
            {
                "patterns": [{"category": "Error Handling", "description": "Missing null"}],
                "run": {
                    "date": "2026-04-23",
                    "description": "First run",
                    "rounds": 1,
                    "issues_by_severity": {"bug": 1},
                    "specializations": ["general"],
                },
            }
        )
        rc, out, err = _run_helper(self.repo_a, "update", stdin=spec, env=self.env)
        self.assertEqual(rc, 0, msg=err)
        result = json.loads(out)
        self.assertFalse(result["existed_before"])
        self.assertEqual(result["stats"]["new_patterns"], 1)
        self.assertEqual(result["total_patterns"], 1)
        self.assertEqual(result["total_recent_runs"], 1)
        self.assertTrue(Path(result["file"]).is_file())

    def test_second_update_existed_before_true_and_dedup(self):
        spec = json.dumps({"patterns": [{"category": "C", "description": "Missing null"}]})
        _run_helper(self.repo_a, "update", stdin=spec, env=self.env)
        rc, out, err = _run_helper(
            self.repo_a,
            "update",
            stdin=json.dumps({"patterns": [{"category": "C", "description": "missing  null."}]}),
            env=self.env,
        )
        self.assertEqual(rc, 0, msg=err)
        result = json.loads(out)
        self.assertTrue(result["existed_before"])
        self.assertEqual(result["stats"]["merged_patterns"], 1)
        self.assertEqual(result["stats"]["new_patterns"], 0)
        self.assertEqual(result["total_patterns"], 1)

    def test_snapshot_returns_structured_json(self):
        spec = json.dumps(
            {
                "patterns": [
                    {"category": "Error Handling", "description": "A"},
                    {"category": "Error Handling", "description": "B"},
                ],
                "run": {"date": "2026-04-23", "description": "Run"},
            }
        )
        _run_helper(self.repo_a, "update", stdin=spec, env=self.env)
        rc, out, err = _run_helper(self.repo_a, "snapshot", env=self.env)
        self.assertEqual(rc, 0, msg=err)
        payload = json.loads(out)
        self.assertTrue(payload["exists"])
        self.assertEqual(len(payload["common_issues"]), 2)
        self.assertEqual(payload["common_issues"][0]["category"], "Error Handling")
        self.assertEqual(len(payload["recent_runs"]), 1)

    def test_snapshot_missing_file_returns_exists_false(self):
        rc, out, err = _run_helper(self.repo_a, "snapshot", env=self.env)
        self.assertEqual(rc, 0, msg=err)
        payload = json.loads(out)
        self.assertFalse(payload["exists"])
        self.assertEqual(payload["common_issues"], [])
        self.assertEqual(payload["recent_runs"], [])

    def test_invalid_json_exits_4(self):
        rc, _, err = _run_helper(self.repo_a, "update", stdin="not-json", env=self.env)
        self.assertEqual(rc, 4)
        self.assertIn("memory.py:", err)

    def test_calendar_invalid_date_exits_4(self):
        rc, _, err = _run_helper(
            self.repo_a,
            "update",
            stdin=json.dumps({"run": {"date": "2026-13-99", "description": "x"}}),
            env=self.env,
        )
        self.assertEqual(rc, 4)
        self.assertIn("calendar-valid", err)

    def test_string_key_patterns_exits_4(self):
        rc, _, err = _run_helper(
            self.repo_a,
            "update",
            stdin=json.dumps({"run": {"description": "x", "key_patterns": "single"}}),
            env=self.env,
        )
        self.assertEqual(rc, 4)

    def test_workspace_id_falls_back_to_cwd_for_non_git(self):
        nogit = self.test_root / "no-git"
        nogit.mkdir()
        rc, out, err = _run_helper(nogit, "path", env=self.env)
        self.assertEqual(rc, 0, msg=err)
        # Path should still be under $HOME/.grok/implement-memory/
        self.assertTrue(out.strip().startswith(str(self.home / ".grok" / "implement-memory")))

    def test_lock_file_mode_under_restrictive_umask(self):
        # Round 2 [General #70 / General-2 #2]: both files must end up at
        # FILE_MODE (0o600) regardless of the process umask. The memory file
        # was force-chmod'd in round 1, but the lock file's os.open(...,
        # FILE_MODE) was umask-affected. The fix adds os.chmod after open.
        old_umask = os.umask(0o077)
        try:
            spec = json.dumps({"patterns": [{"category": "C", "description": "x"}]})
            rc, out, err = _run_helper(self.repo_a, "update", stdin=spec, env=self.env)
            self.assertEqual(rc, 0, msg=err)
            result = json.loads(out)
            mem_path = Path(result["file"])
            lock_path = mem_path.with_suffix(".lock")
            self.assertEqual(
                mem_path.stat().st_mode & 0o777,
                memory.FILE_MODE,
                f"memory file mode {oct(mem_path.stat().st_mode & 0o777)} != {oct(memory.FILE_MODE)}",
            )
            self.assertEqual(
                lock_path.stat().st_mode & 0o777,
                memory.FILE_MODE,
                f"lock file mode {oct(lock_path.stat().st_mode & 0o777)} != {oct(memory.FILE_MODE)}",
            )
        finally:
            os.umask(old_umask)

    def test_memory_and_lock_files_are_owner_only(self):
        # Threat model: the memory file may contain security-review patterns
        # and key_patterns from non-public source review. The workspace id
        # is a deterministic SHA-256 of the canonical remote URL, so an
        # unprivileged account on a shared host that knows or can guess the
        # public-repo URL can compute the workspace id and attempt to read
        # ~/.grok/implement-memory/<workspace-id>.md directly. We rely on
        # 0o600 file mode (owner read/write, no group/other) to deny that.
        # Pin the literal so accidental future widening (e.g., 0o644) gets
        # caught here rather than only in production.
        self.assertEqual(memory.FILE_MODE, 0o600)
        # Run with a permissive umask to exercise the explicit os.chmod path.
        old_umask = os.umask(0o000)
        try:
            spec = json.dumps({"patterns": [{"category": "C", "description": "x"}]})
            rc, out, err = _run_helper(self.repo_a, "update", stdin=spec, env=self.env)
            self.assertEqual(rc, 0, msg=err)
            result = json.loads(out)
            mem_path = Path(result["file"])
            lock_path = mem_path.with_suffix(".lock")
            for path in (mem_path, lock_path):
                mode = path.stat().st_mode & 0o777
                self.assertEqual(
                    mode,
                    0o600,
                    f"{path.name} mode {oct(mode)} != 0o600 (owner-only)",
                )
                # Belt-and-braces: assert no group or other bits at all.
                self.assertEqual(
                    mode & 0o077,
                    0,
                    f"{path.name} has group/other bits set: {oct(mode)}",
                )
        finally:
            os.umask(old_umask)

    def test_lock_file_open_failure_clean_message(self):
        # Round 2 [General #71]: an OSError on os.open (e.g., parent dir not
        # writable) must surface as a clean memory.py: ... message via
        # MemoryHelperError, not as a Python traceback.
        # First create the directory by running update once.
        spec = json.dumps({"patterns": [{"category": "C", "description": "x"}]})
        _run_helper(self.repo_a, "update", stdin=spec, env=self.env)
        memory_dir = self.home / ".grok" / "implement-memory"
        # Remove write/execute so a new os.open(O_CREAT) fails.
        # NOTE: the lock file already exists from the previous update, so
        # os.open with O_CREAT against an existing file in a 0o555 dir would
        # actually still succeed (the file exists, no creation needed).
        # Force the failure path by deleting the lock file first, then chmod.
        for entry in memory_dir.iterdir():
            if entry.suffix == ".lock":
                entry.unlink()
        old_mode = memory_dir.stat().st_mode
        os.chmod(memory_dir, 0o555)
        try:
            rc, out, err = _run_helper(self.repo_a, "update", stdin=spec, env=self.env)
            self.assertNotEqual(rc, 0)
            # Must be a clean memory.py: error, not a traceback.
            self.assertIn("memory.py:", err)
            self.assertNotIn("Traceback", err)
        finally:
            os.chmod(memory_dir, old_mode)

    def test_corrupted_memory_file_clean_message(self):
        # An invalid-UTF-8 memory file (e.g., truncated mid-multibyte by an
        # unrelated process or copy) must surface a clean `memory.py: ...`
        # message instead of a Python traceback. parse_memory_file is reached
        # via Path.read_text(encoding="utf-8") which raises UnicodeDecodeError
        # rather than OSError, so it would escape the OSError handler unless
        # the generic Exception catch-all is in place.
        spec = json.dumps({"patterns": [{"category": "C", "description": "x"}]})
        _run_helper(self.repo_a, "update", stdin=spec, env=self.env)
        memory_dir = self.home / ".grok" / "implement-memory"
        # Find the memory file we just created and overwrite with garbage.
        mem_files = [p for p in memory_dir.iterdir() if p.suffix == ".md"]
        self.assertEqual(len(mem_files), 1)
        # 0xff is not a valid UTF-8 start byte; this guarantees decode failure.
        mem_files[0].write_bytes(b"\xff\xfe\xfd not valid utf-8\n")
        rc, out, err = _run_helper(self.repo_a, "update", stdin=spec, env=self.env)
        self.assertNotEqual(rc, 0)
        self.assertIn("memory.py:", err)
        self.assertNotIn("Traceback", err)


# ---------------------------------------------------------------------------
# Concurrency smoke test
# ---------------------------------------------------------------------------


def _concurrent_worker(args):
    """Top-level for picklability under spawn start methods."""
    repo_dir, helper, home, n = args
    spec = json.dumps({"patterns": [{"category": "Concurrent", "description": f"pattern {n}"}]})
    env = os.environ.copy()
    env["HOME"] = home
    result = subprocess.run(
        [sys.executable, helper, "update"],
        cwd=repo_dir,
        input=spec,
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )
    return result.returncode, result.stdout, result.stderr


class TestConcurrency(CLIBase):
    def test_eight_concurrent_writers_serialised(self):
        N = 8
        args = [(str(self.repo_a), str(_HELPER), str(self.home), i) for i in range(N)]
        # Use spawn to avoid macOS fork issues with multiprocessing
        ctx = mp.get_context("spawn")
        with ctx.Pool(processes=N) as pool:
            results = pool.map(_concurrent_worker, args)
        for rc, _, err in results:
            self.assertEqual(rc, 0, msg=err)

        rc, out, _ = _run_helper(self.repo_a, "snapshot", env=self.env)
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        descriptions = {e["description"] for e in payload["common_issues"]}
        for i in range(N):
            self.assertIn(f"pattern {i}", descriptions)
        # No double-counting: every pattern landed exactly once
        for e in payload["common_issues"]:
            self.assertEqual(e["count"], 1)


# ---------------------------------------------------------------------------
# Documentation drift checks
# ---------------------------------------------------------------------------


class TestDocsConsistency(unittest.TestCase):
    """Catch drift between code constants and the markdown docs that mirror them."""

    def test_skill_md_default_header_matches(self):
        # SKILL.md's "Memory File Format" section embeds the same lines as
        # `memory.DEFAULT_HEADER` inside a fenced ```markdown code block,
        # introduced by the marker comment
        # `<!-- mirror-of: scripts/memory.py DEFAULT_HEADER -->`.
        # If either copy drifts, users reading the docs will see a header
        # different from what the helper actually writes. This test parses
        # the file, locates the marker, extracts the next fenced block, and
        # asserts the first len(DEFAULT_HEADER) lines match exactly.
        skill_md = _HERE.parent / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")

        marker = "<!-- mirror-of: scripts/memory.py DEFAULT_HEADER -->"
        marker_idx = text.find(marker)
        self.assertNotEqual(
            marker_idx,
            -1,
            f"drift-check marker {marker!r} missing from {skill_md}; "
            "either restore it or update this test to match the new layout",
        )

        # Find the next ```markdown ... ``` block after the marker.
        after = text[marker_idx + len(marker) :]
        fence_open = after.find("```markdown")
        self.assertNotEqual(
            fence_open,
            -1,
            "expected ```markdown fenced block immediately after the "
            "drift-check marker; the SKILL.md layout has changed.",
        )
        body_start = after.find("\n", fence_open) + 1
        fence_close = after.find("```", body_start)
        self.assertNotEqual(
            fence_close,
            -1,
            "fenced ```markdown block after marker is unterminated",
        )
        block_lines = after[body_start:fence_close].rstrip("\n").splitlines()

        # Compare line-by-line so the failure message points at the first
        # diverging line rather than dumping the whole multi-line diff.
        expected = list(memory.DEFAULT_HEADER)
        self.assertGreaterEqual(
            len(block_lines),
            len(expected),
            f"SKILL.md mirror block has only {len(block_lines)} lines; "
            f"expected at least {len(expected)} (DEFAULT_HEADER)",
        )
        for i, (got, want) in enumerate(zip(block_lines, expected)):
            self.assertEqual(
                got,
                want,
                f"SKILL.md mirror block line {i} drifted from "
                f"memory.DEFAULT_HEADER[{i}]: got {got!r}, want {want!r}",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
