"""Scenario tests for Citus release helpers and exact-version install parsing."""

from __future__ import annotations

import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "test_package_installation"))

import release_helpers as rh  # noqa: E402
import run_test  # noqa: E402

SAMPLE_MATRIX = """
name: Postgres Version Matrix
project_name: citus

version_matrix:
  - 12.0:
      postgres_versions: [ 14, 15 ]
  - 12.1:
      postgres_versions: [ 14, 15, 16 ]
  - 13.0:
      postgres_versions: [ 15, 16, 17 ]
  - 13.2:
      postgres_versions: [ 15, 16, 17 ]
  - 14.0:
      postgres_versions: [ 16, 17, 18 ]
  - 15.0:
      postgres_versions: [ 17, 18, 19 ]
"""

SAMPLE_EXCLUDE = """
exclude:
  nightly:
    all: [19]
  release:
    el/8: [19]
    ol/8: [19]
"""


class TagGrammarTests(unittest.TestCase):
    def test_valid_stable_and_prerelease_tags(self):
        stable = rh.parse_tag("v14.3.0")
        self.assertEqual(stable["version"], "14.3.0")
        self.assertEqual(stable["major_minor"], "14.3")
        self.assertFalse(stable["is_prerelease"])

        beta = rh.parse_tag("v15.0.0_beta1")
        self.assertEqual(beta["version"], "15.0.0_beta1")
        self.assertTrue(beta["is_prerelease"])

        rc = rh.parse_tag("v14.10.2_rc")
        self.assertEqual(rc["base_version"], "14.10.2")
        self.assertTrue(rc["is_prerelease"])

    def test_rejects_malformed_or_shell_injection_tags(self):
        for bad in ("14.3.0", "v14.3", "v14.3.0-beta1", "v14.3.0;id", "v100.0.0", ""):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    rh.parse_tag(bad)


class PgxnForwardOnlyTests(unittest.TestCase):
    def test_newer_stable_including_numeric_minor_rollover(self):
        ok, _ = rh.should_update_pgxn("v14.3.0", "14.0.0")
        self.assertTrue(ok)
        ok, _ = rh.should_update_pgxn("v14.10.0", "14.2.0")
        self.assertTrue(ok)

    def test_skips_equal_older_line_and_prereleases(self):
        for tag, current in (
            ("v14.0.0", "14.0.0"),
            ("v13.5.0", "14.0.0"),
            ("v12.1.14", "14.0.0"),
            ("v15.0.0_beta1", "14.0.0"),
            ("v15.0.0_rc1", "14.0.0"),
        ):
            with self.subTest(tag=tag, current=current):
                ok, _ = rh.should_update_pgxn(tag, current)
                self.assertFalse(ok)


class PostgresMatrixTests(unittest.TestCase):
    def test_pg_min_major_floor_lookup_across_lines(self):
        expected = {
            "v12.1.14": 14,
            "v13.0.0": 15,
            "v13.4.0": 15,
            "v14.0.0": 16,
            "v14.3.0": 16,
            "v15.0.0": 17,
            "v15.0.0_beta1": 17,
        }
        for tag, pg_min in expected.items():
            with self.subTest(tag=tag):
                self.assertEqual(rh.resolve_pg_min_major(SAMPLE_MATRIX, tag), pg_min)

    def test_block_sequence_yaml_and_unknown_old_version(self):
        block_yaml = "version_matrix:\n  - 14.0:\n      postgres_versions:\n        - 16\n        - 17\n"
        self.assertEqual(rh.resolve_pg_min_major(block_yaml, "v14.3.0"), 16)
        with self.assertRaises(ValueError):
            rh.resolve_pg_min_major(block_yaml, "v11.0.0")

    def test_test_matrix_applies_release_and_nightly_excludes(self):
        rel = rh.build_test_matrix(
            ["el/8", "debian/bookworm"], SAMPLE_MATRIX, "15.0.0.citus-1", "community", SAMPLE_EXCLUDE
        )
        self.assertNotIn({"platform": "el/8", "pg_version": "19"}, rel)
        self.assertIn({"platform": "debian/bookworm", "pg_version": "19"}, rel)

        nightly = rh.build_test_matrix(
            ["el/8", "debian/bookworm"],
            SAMPLE_MATRIX,
            "15.1.0.citus~git.20261125.abc1234-1",
            "community-nightlies",
            SAMPLE_EXCLUDE,
        )
        self.assertEqual({e["pg_version"] for e in nightly}, {"17", "18"})


class ForceDockerDetectionTests(unittest.TestCase):
    def test_commit_and_squash_and_override_trailers(self):
        self.assertFalse(rh.detect_force_docker("Bump to citus 14.3.0\n"))
        self.assertTrue(rh.detect_force_docker("Bump to citus 14.3.0\n\nForce-Docker: true\n"))
        self.assertTrue(rh.detect_force_docker("* Bump to citus 14.3.0\n  * force-docker: TRUE\n"))
        self.assertFalse(
            rh.detect_force_docker("Bump\nForce-Docker: true\n\nRevert flag\nForce-Docker: false\n")
        )
        self.assertFalse(rh.detect_force_docker("Mention Force-Docker: true in prose"))

    def test_rebase_merge_pr_body_fallback_and_override_scenarios(self):
        import subprocess
        import tempfile

        def git(repo: str, *args: str) -> str:
            return subprocess.check_output(["git", "-C", repo, *args], text=True).strip()

        with tempfile.TemporaryDirectory() as td:
            git(td, "init", "-q", "-b", "all-citus")
            git(td, "config", "user.name", "Test")
            git(td, "config", "user.email", "test@example.com")
            (pathlib.Path(td) / "pkgvars").write_text("pkglatest=14.2.0.citus-1\n", encoding="utf-8")
            git(td, "add", "pkgvars")
            git(td, "commit", "-q", "-m", "Base commit")
            base_sha = git(td, "rev-parse", "HEAD")

            # Scenario 1: multi-commit rebase-merge (trailer on first commit, follow-up fix commit has none)
            (pathlib.Path(td) / "pkgvars").write_text("pkglatest=14.3.0.citus-1\n", encoding="utf-8")
            git(td, "commit", "-q", "-am", "Bump to citus 14.3.0\n\nForce-Docker: true")
            (pathlib.Path(td) / "note.txt").write_text("lint fix\n", encoding="utf-8")
            git(td, "add", "note.txt")
            git(td, "commit", "-q", "-m", "Fix changelog formatting")
            self.assertTrue(rh.resolve_force_docker(td, event_before=base_sha, pr_body=""))
            # Without event_before, HEAD alone would miss commit 1 unless PR body has the trailer
            self.assertFalse(rh.resolve_force_docker(td, event_before="0" * 40, pr_body=""))

            # Scenario 2: body-stripped squash-merge recovered via merged PR body fallback
            git(td, "reset", "--hard", "-q", base_sha)
            (pathlib.Path(td) / "pkgvars").write_text("pkglatest=14.3.0.citus-1\n", encoding="utf-8")
            git(td, "commit", "-q", "-am", "Bump to citus 14.3.0 (#123)")
            self.assertTrue(
                rh.resolve_force_docker(
                    td, event_before=base_sha, pr_body="Automated update.\n\nForce-Docker: true"
                )
            )

            # Scenario 3: explicit Force-Docker: false commit overrides PR body Force-Docker: true
            (pathlib.Path(td) / "note.txt").write_text("override\n", encoding="utf-8")
            git(td, "add", "note.txt")
            git(td, "commit", "-q", "-m", "Disable docker force\n\nForce-Docker: false")
            self.assertFalse(
                rh.resolve_force_docker(
                    td, event_before=base_sha, pr_body="Automated update.\n\nForce-Docker: true"
                )
            )

            # Scenario 4: merge commit fallback when event_before is empty, unreachable, diverged, or HEAD
            git(td, "reset", "--hard", "-q", base_sha)
            git(td, "checkout", "-q", "-b", "diverged-old")
            (pathlib.Path(td) / "old.txt").write_text("diverged\n", encoding="utf-8")
            git(td, "add", "old.txt")
            git(td, "commit", "-q", "-m", "Diverged commit")
            diverged_sha = git(td, "rev-parse", "HEAD")

            git(td, "checkout", "-q", "all-citus")
            git(td, "checkout", "-q", "-b", "release/all-citus-v14.3.0")
            (pathlib.Path(td) / "pkgvars").write_text("pkglatest=14.3.0.citus-1\n", encoding="utf-8")
            git(td, "commit", "-q", "-am", "Bump to citus 14.3.0\n\nForce-Docker: true")
            git(td, "checkout", "-q", "all-citus")
            git(td, "merge", "-q", "--no-ff", "release/all-citus-v14.3.0", "-m", "Merge PR #124")
            merge_head = git(td, "rev-parse", "HEAD")
            for before in ("", "a" * 40, diverged_sha, merge_head):
                with self.subTest(before=before):
                    self.assertTrue(rh.resolve_force_docker(td, event_before=before, pr_body=""))


class RunTestVersionParsingTests(unittest.TestCase):
    def test_exact_revision_and_nightly_mapping(self):
        self.assertEqual(
            run_test.parse_citus_version("14.3.0.citus-99", "debian")["pkg_revision"],
            "14.3.0.citus-99",
        )
        self.assertEqual(
            run_test.parse_citus_version("14.3.0", "el")["pkg_revision"],
            "14.3.0.citus-1",
        )
        self.assertEqual(
            run_test.parse_citus_version("15.0.0_beta1.citus-1", "ubuntu")["pkg_revision"],
            "15.0.0-beta1.citus-1",
        )
        nightly = run_test.parse_citus_version("14.4.0.citus~git.20261125.abc1234-1", "el")
        self.assertEqual(nightly["pkg_revision"], "14.4.0.citus-0.0.git.20261125.abc1234")
        self.assertEqual(nightly["expected_version"], "+git.20261125.abc1234")
        with self.assertRaises(ValueError):
            run_test.parse_citus_version("latest", "debian")


class NightlyAndUploadHelperTests(unittest.TestCase):
    def test_extract_nightly_version_deb_and_rpm(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td)
            (p / "postgresql-17-citus-dbgsym_14.4.0.citus~git.20261125.abc1234-1_amd64.deb").touch()
            (p / "postgresql-17-citus_14.4.0.citus~git.20261125.abc1234-1_amd64.deb").touch()
            self.assertEqual(rh.extract_nightly_version(td), "14.4.0.citus~git.20261125.abc1234-1")
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td)
            (p / "citus144_17-14.4.0.citus-0.0.git.20261125.abc1234.el8.x86_64.rpm").touch()
            self.assertEqual(rh.extract_nightly_version(td), "14.4.0.citus~git.20261125.abc1234-1")

    def test_upload_idempotent_skips_422_and_fails_real_errors(self):
        from types import SimpleNamespace
        from unittest import mock

        ok_and_dup = SimpleNamespace(
            return_values=[
                SimpleNamespace(success_status=True, message="{}", file_name="/p/a.deb", distro="debian/bookworm", repo="citusdata/community"),
                SimpleNamespace(success_status=False, message='{"filename":["has already been taken"]}', file_name="/p/b.deb", distro="debian/bookworm", repo="citusdata/community"),
            ]
        )
        real_err = SimpleNamespace(
            return_values=[
                SimpleNamespace(success_status=False, message="Unauthorized", file_name="/p/c.deb", distro="debian/bookworm", repo="citusdata/community"),
            ]
        )
        fake_mod = SimpleNamespace(upload_files_in_directory_to_package_cloud=lambda *a: ok_and_dup)
        with mock.patch.dict(sys.modules, {"tools": SimpleNamespace(), "tools.packaging_automation": SimpleNamespace(), "tools.packaging_automation.upload_to_package_cloud": fake_mod}):
            rh.upload_idempotent("/p", "debian/bookworm", "tok", "citusdata/community", "all-citus", "all-citus")
            fake_mod.upload_files_in_directory_to_package_cloud = lambda *a: real_err
            with self.assertRaises(RuntimeError):
                rh.upload_idempotent("/p", "debian/bookworm", "tok", "citusdata/community", "all-citus", "all-citus")


if __name__ == "__main__":
    unittest.main()
