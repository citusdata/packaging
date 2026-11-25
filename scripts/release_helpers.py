#!/usr/bin/env python3
"""Minimal stdlib helpers for Citus packaging release workflows."""

from __future__ import annotations

import glob
import json
import os
import re
import sys
from pathlib import Path

TAG_RE = re.compile(r"^v([0-9]{1,2})\.([0-9]{1,2})\.([0-9]{1,2})(?:_(beta|rc)([0-9]*))?$")
SEMVER_RE = re.compile(r"^v?([0-9]{1,2})\.([0-9]{1,2})\.([0-9]{1,2})$")
MAJOR_MINOR_RE = re.compile(r"^v?([0-9]{1,2})\.([0-9]{1,2})(?:\.[0-9]{1,2})?")
FORCE_DOCKER_RE = re.compile(r"^\s*(?:[-*]\s+)?Force-Docker:\s*(true|false)\s*$", re.IGNORECASE)


def parse_tag(tag: str) -> dict[str, object]:
    m = TAG_RE.match(tag.strip())
    if not m:
        raise ValueError(f"Invalid Citus tag {tag!r}; expected vX.Y.Z or vX.Y.Z_(beta|rc)[N]")
    maj, min_, pat = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return {
        "tag": tag.strip(),
        "version": tag.strip()[1:],
        "base_version": f"{maj}.{min_}.{pat}",
        "major": maj,
        "minor": min_,
        "patch": pat,
        "major_minor": f"{maj}.{min_}",
        "is_prerelease": m.group(4) is not None,
    }


def parse_semver(version: str) -> tuple[int, int, int]:
    m = SEMVER_RE.match(version.strip())
    if not m:
        raise ValueError(f"Invalid stable semver {version!r}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def should_update_pgxn(tag: str, current_pgxn_version: str) -> tuple[bool, str]:
    info = parse_tag(tag)
    if info["is_prerelease"]:
        return False, f"prerelease tag {info['tag']} is skipped for PGXN"
    cur = parse_semver(current_pgxn_version)
    tgt = (int(info["major"]), int(info["minor"]), int(info["patch"]))
    if tgt <= cur:
        return False, f"{info['version']} is not newer than current PGXN {current_pgxn_version.strip()}"
    return True, f"{info['version']} > {current_pgxn_version.strip()}"


def parse_postgres_matrix(text: str) -> list[tuple[tuple[int, int], list[int]]]:
    rows: list[tuple[tuple[int, int], list[int]]] = []
    in_list = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if m := re.match(r'^-\s*["\']?([0-9]+)\.([0-9]+)["\']?\s*:$', line):
            rows.append(((int(m.group(1)), int(m.group(2))), []))
            in_list = False
        elif rows and (m := re.match(r"^postgres_versions\s*:\s*\[([^\]]*)\]\s*$", line)):
            rows[-1][1].extend(int(x.strip().strip("'\"")) for x in m.group(1).split(",") if x.strip())
            in_list = False
        elif rows and re.match(r"^postgres_versions\s*:\s*$", line):
            in_list = True
        elif rows and in_list and (m := re.match(r'^-\s*["\']?([0-9]+)["\']?\s*$', line)):
            rows[-1][1].append(int(m.group(1)))
        else:
            in_list = False
    if not rows:
        raise ValueError("No version_matrix entries found in postgres-matrix.yml")
    return rows


def resolve_pg_versions(matrix_text: str, version_or_tag: str) -> list[int]:
    m = MAJOR_MINOR_RE.match(version_or_tag.strip())
    if not m:
        raise ValueError(f"Cannot extract Citus major.minor from {version_or_tag!r}")
    target = (int(m.group(1)), int(m.group(2)))
    matched = None
    for key, pgs in sorted(parse_postgres_matrix(matrix_text), key=lambda r: r[0]):
        if key <= target:
            matched = pgs
        else:
            break
    if not matched:
        raise ValueError(f"No postgres-matrix.yml entry for Citus {target[0]}.{target[1]}")
    return list(matched)


def resolve_pg_min_major(matrix_text: str, version_or_tag: str) -> int:
    return min(resolve_pg_versions(matrix_text, version_or_tag))


def build_test_matrix(
    platforms: list[str], matrix_text: str, citus_version: str, channel: str = "community", exclude_text: str = ""
) -> list[dict[str, str]]:
    is_nightly = channel == "community-nightlies"
    pgs = list(parse_postgres_matrix(matrix_text)[-1][1]) if is_nightly else resolve_pg_versions(matrix_text, citus_version)
    excl: dict[str, set[int]] = {}
    section = None
    for raw in exclude_text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if line in ("release:", "nightly:"):
            section = line[:-1]
        elif section == ("nightly" if is_nightly else "release") and (m := re.match(r"^([^:]+):\s*\[([^\]]*)\]\s*$", line)):
            excl[m.group(1).strip().strip("'\"")] = {int(x.strip().strip("'\"")) for x in m.group(2).split(",") if x.strip()}
    return [
        {"platform": p, "pg_version": str(pg)}
        for p in platforms
        for pg in pgs
        if pg not in (excl.get("all", set()) | excl.get(p, set()))
    ]


def detect_force_docker(commit_text: str) -> bool:
    val = False
    for line in commit_text.splitlines():
        if m := FORCE_DOCKER_RE.match(line):
            val = m.group(1).lower() == "true"
    return val


def extract_nightly_version(packages_dir: str) -> str:
    debs = [f for f in glob.glob(f"{packages_dir}/**/*.deb", recursive=True) if "-dbgsym_" not in os.path.basename(f)]
    if debs:
        return os.path.basename(debs[0]).split("_")[1]
    rpms = [f for f in glob.glob(f"{packages_dir}/**/*.rpm", recursive=True) if "-debug" not in os.path.basename(f)]
    if rpms and (m := re.search(r"-([0-9]+\.[0-9]+\.[0-9]+\.citus)-0\.0\.(git\.[0-9]+\.[0-9a-f]+)\.", os.path.basename(rpms[0]))):
        return f"{m.group(1)}~{m.group(2)}-1"
    raise ValueError(f"Could not determine nightly package version in {packages_dir}")


def upload_idempotent(packages_dir: str, platform: str, token: str, repo: str, current_branch: str, main_branch: str) -> None:
    from tools.packaging_automation.upload_to_package_cloud import upload_files_in_directory_to_package_cloud

    res = upload_files_in_directory_to_package_cloud(packages_dir, platform, token, repo, current_branch, main_branch)
    if not res.return_values:
        raise RuntimeError(f"No packages found to upload in {packages_dir}")
    failed = []
    for rv in res.return_values:
        name = os.path.basename(rv.file_name)
        if rv.success_status:
            print(f"Uploaded {name} ({rv.distro} -> {rv.repo})")
        elif "has already been taken" in (rv.message or "").lower():
            print(f"Already exists on {rv.repo} ({rv.distro}), skipping {name}")
        else:
            print(f"Upload failed for {name}: {rv.message}", file=sys.stderr)
            failed.append(name)
    if failed:
        raise RuntimeError(f"Failed to upload: {', '.join(failed)}")


def main(argv: list[str]) -> int:
    cmd = argv[1]
    if cmd == "parse-tag":
        info = parse_tag(argv[2])
        for k in ("version", "base_version", "major_minor"):
            print(f"{k}={info[k]}")
        print(f"is_prerelease={'true' if info['is_prerelease'] else 'false'}")
    elif cmd == "pgxn-check":
        ok, reason = should_update_pgxn(argv[2], argv[3])
        print(f"should_update={'true' if ok else 'false'}\nreason={reason}")
    elif cmd == "pg-min-major":
        print(resolve_pg_min_major(Path(argv[2]).read_text(encoding="utf-8"), argv[3]))
    elif cmd == "test-matrix":
        excl = Path(argv[6]).read_text(encoding="utf-8") if len(argv) > 6 and Path(argv[6]).is_file() else ""
        entries = build_test_matrix(json.loads(argv[4]), Path(argv[2]).read_text(encoding="utf-8"), argv[3], argv[5], excl)
        print(json.dumps({"include": entries}, separators=(",", ":")))
    elif cmd == "force-docker":
        print("true" if detect_force_docker(sys.stdin.read()) else "false")
    elif cmd == "nightly-ver":
        print(extract_nightly_version(argv[2]))
    elif cmd == "upload":
        upload_idempotent(argv[2], argv[3], os.environ["PACKAGE_CLOUD_API_TOKEN"], argv[4], argv[5], argv[6])
    else:
        raise SystemExit(f"Unknown command: {cmd}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
