#!/usr/bin/env python3
"""Nonpublishing release reproduction; never invoke the signing build_packages CLI."""

import base64
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tarfile

CONTAINER = "arm64-release-diagnostic"
EVIDENCE = Path("evidence").resolve()
HELPER = Path(__file__).resolve()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def record(directory, name, command, cwd=None):
    """Keep streams separate, and retain the real command exit status."""
    prefix = directory / name
    prefix.parent.mkdir(parents=True, exist_ok=True)
    Path(f"{prefix}.command.txt").write_text(shlex.join(command) + "\n")
    with Path(f"{prefix}.stdout.log").open("wb") as stdout:
        with Path(f"{prefix}.stderr.log").open("wb") as stderr:
            result = subprocess.run(command, cwd=cwd, stdout=stdout, stderr=stderr)
    Path(f"{prefix}.exit-code.txt").write_text(f"{result.returncode}\n")
    print(f"{name}: exit {result.returncode}", flush=True)
    return result.returncode


def prepare():
    sys.path.insert(0, str(Path.cwd()))
    from dotenv import dotenv_values
    from tools.packaging_automation.citus_package import (
        get_docker_image_name,
        get_package_version_without_release_stage_from_pkgvars,
        write_postgres_versions_into_file,
    )

    checkouts = {}
    for directory, expected in (
        (".", os.environ["GITHUB_SHA"]),
        ("input", os.environ["INPUT_SHA"]),
        ("tooling", os.environ["TOOLING_SHA"]),
        ("tools", os.environ["TOOLS_SHA"]),
    ):
        actual = subprocess.check_output(
            ["git", "-C", directory, "rev-parse", "HEAD"], text=True
        ).strip()
        if actual != expected:
            raise ValueError(f"{directory}: expected {expected}, found {actual}")
        checkouts[directory] = actual

    inputs = str(Path("input").resolve())
    platform = os.environ["PLATFORM"]
    version = get_package_version_without_release_stage_from_pkgvars(inputs)
    write_postgres_versions_into_file(inputs, version, platform.split("/")[0], platform)
    pkgvars = dotenv_values(f"{inputs}/pkgvars")
    manifest = {
        "checkouts": checkouts,
        "tools_tag": "v0.8.36",
        "platform": platform,
        "image": f"citus/packaging:{get_docker_image_name(platform)}-all",
        "source_version": pkgvars["pkglatest"].rsplit("-", 1)[0],
        "source_package": pkgvars.get("deb_pkgname", pkgvars["pkgname"]),
        "source_repository": "citusdata/" + pkgvars.get("hubproj", pkgvars["pkgname"]),
        "pg_exclude_present": Path(inputs, "pg_exclude.yml").exists(),
        "warning_handler_sha256": digest(
            Path("tools/packaging_automation/packaging_warning_handler.py")
        ),
    }
    write_json(EVIDENCE / "manifest.json", manifest)
    dest = EVIDENCE / "inputs"
    dest.mkdir()
    for name in (
        "pkgvars",
        "postgres-matrix.yml",
        "pg_exclude.yml",
        "packaging_ignore.yml",
        "supported-postgres",
    ):
        source = Path(inputs, name)
        if name == "pg_exclude.yml" and not source.exists():
            continue  # Absence is the original hll/topn policy, recorded above.
        shutil.copy2(source, dest / name)


def build():
    manifest = json.loads((EVIDENCE / "manifest.json").read_text())
    image = manifest["image"]
    architecture = subprocess.check_output(
        ["docker", "image", "inspect", "--format", "{{.Architecture}}", image],
        text=True,
    ).strip()
    if architecture != "arm64":
        raise ValueError(f"Builder must be native arm64, not {architecture}")
    status = record(
        EVIDENCE,
        "image",
        [
            "docker",
            "image",
            "inspect",
            "--format",
            "{{.Id}} {{.Os}} {{.Architecture}} workdir={{json .Config.WorkingDir}}",
            image,
        ],
    )
    if status:
        return status
    packages = Path("packages", manifest["platform"].replace("/", "-")).resolve()
    packages.mkdir(parents=True)
    # The pinned entrypoint already supports waiting mode. Only the exec enables
    # compilation; its exit status, not the keepalive's status, is authoritative.
    subprocess.run(
        [
            "docker",
            "run",
            "--detach",
            "--name",
            CONTAINER,
            "-v",
            f"{packages}:/packages",
            "-v",
            f"{Path('input').resolve()}:/buildfiles:ro",
            "-e",
            "GITHUB_TOKEN",
            "-e",
            "CI",
            image,
            "release",
        ],
        check=True,
    )
    subprocess.run(
        ["docker", "exec", CONTAINER, "test", "-r", "/buildfiles/pkgvars"], check=True
    )
    return record(
        EVIDENCE,
        "build",
        [
            "docker",
            "exec",
            "-e",
            "CONTAINER_BUILD_RUN_ENABLED=true",
            CONTAINER,
            "/scripts/fetch_and_build_deb",
            "release",
        ],
    )


def collect_inside(version, package, repository):
    dest = Path("/arm64-diagnostic-evidence")
    dest.mkdir()
    statuses = {}

    def capture(name, command, cwd=None):
        statuses[name] = record(dest, name, command, cwd)
        return (dest / f"{name}.stdout.log").read_text(errors="surrogateescape")

    def missing(name, message):
        statuses[name] = 1
        (dest / f"{name}.error.txt").write_text(message + "\n")

    # Recover binaries before any optional post-build inspection can fail.
    archives = sorted(Path.cwd().glob("*.deb")) + sorted(Path.cwd().glob("*.ddeb"))
    (dest / "packages").mkdir()
    if not archives:
        missing("packages", "No unsigned binary packages were produced.")
    for archive in archives:
        shutil.copy2(archive, dest / "packages" / archive.name)
        capture(f"controls/{archive.name}", ["dpkg-deb", "--field", str(archive)])
    write_json(dest / "package-sha256.json", {p.name: digest(p) for p in archives})

    capture("location", ["pwd"])
    capture("identity", ["id"])
    capture("architecture", ["dpkg", "--print-architecture"])
    capture(
        "installed-packages",
        [
            "dpkg-query",
            "-W",
            "-f=${binary:Package}\t${Version}\t${Architecture}\n",
        ],
    )
    capture(
        "scanner-sha256",
        [
            "sha256sum",
            "/usr/bin/dpkg-shlibdeps",
            "/usr/bin/dh_shlibdeps",
        ],
    )
    legacy = "/lib/ld-linux-aarch64.so.1"
    canonical = capture("loader-realpath", ["readlink", "-e", legacy]).strip()
    capture("loader-legacy-owner", ["dpkg-query", "--search", legacy])
    if canonical:
        capture("loader-canonical-owner", ["dpkg-query", "--search", canonical])
    capture("loader-diversion", ["dpkg-divert", "--list", "*ld-linux-aarch64.so.1*"])
    lines = Path("/var/lib/dpkg/diversions").read_text().splitlines()
    records = [
        lines[i : i + 3] for i in range(0, len(lines), 3) if legacy in lines[i : i + 2]
    ]
    write_json(dest / "loader-diversion-records.json", records)
    capture("libc-file-list", ["dpkg-query", "-L", "libc6:arm64"])
    for suffix in ("symbols", "shlibs"):
        capture(
            f"libc-{suffix}",
            [
                "cat",
                f"/var/lib/dpkg/info/libc6:arm64.{suffix}",
            ],
        )

    source = Path.cwd() / version
    debian = source / "debian"
    if debian.is_dir():
        metadata = dest / "debian"
        metadata.mkdir()
        for path in sorted(debian.glob("*.substvars")) + [
            debian / name for name in ("control", "control.in", "rules", "pgversions")
        ]:
            shutil.copy2(path, metadata / path.name)
        originals = {p.name: digest(p) for p in debian.glob("*.substvars")}
        write_json(dest / "substvars-before.json", originals)
        if not originals:
            missing("substvars", "No original debian/*.substvars were produced.")
        packages = capture(
            "package-selection", ["dh_listpackages", "-a"], source
        ).split()
        shared_objects = []
        for name in packages:
            staged = debian / name
            if (staged / "DEBIAN/control").is_file():
                shutil.copy2(staged / "DEBIAN/control", metadata / f"{name}.control")
            for path in sorted(staged.rglob("*")):
                if path.is_file() and (
                    path.name.endswith(".so") or ".so." in path.name
                ):
                    shared_objects.append(str(path.relative_to(source)))
                    capture(
                        f"elf/{path.relative_to(debian)}",
                        [
                            "readelf",
                            "--wide",
                            "--file-header",
                            "--dynamic",
                            "--version-info",
                            "--dyn-syms",
                            str(path),
                        ],
                    )
        write_json(dest / "staged-shared-objects.json", shared_objects)
        if not shared_objects:
            missing("shared-objects", "No staged packaged shared objects were found.")
        # No rules override dh_shlibdeps in these inputs. -a reproduces binary-arch
        # selection; -O makes dpkg-shlibdeps print instead of updating substvars.
        capture(
            "scanner-replay", ["dh_shlibdeps", "-a", "-v", "--", "-v", "-O"], source
        )
        after = {p.name: digest(p) for p in debian.glob("*.substvars")}
        write_json(dest / "substvars-after.json", after)
        if originals != after:
            missing("substvars-mutated", "Scanner replay changed original substvars.")
    else:
        missing("source-directory", f"Missing expected source directory: {source}")

    tarball = Path.cwd() / f"{package}_{version}.orig.tar.gz"
    if tarball.is_file():
        with tarfile.open(tarball) as archive:
            first = archive.next()
            archive_root = first.name.rstrip("/") if first else ""
        write_json(
            dest / "source-archive.json",
            {
                "filename": tarball.name,
                "sha256": digest(tarball),
                "root": archive_root,
            },
        )
        tag = "v" + version.replace("~", "-", 1).removesuffix(".citus")
        # curl uses the entrypoint's private ~/.curlrc; never copy that file.
        ref = capture(
            "source-tag-ref",
            [
                "curl",
                "-fsS",
                f"https://api.github.com/repos/{repository}/git/refs/tags/{tag}",
            ],
        )
        if statuses["source-tag-ref"] == 0:
            tag_sha = json.loads(ref)["object"]["sha"]
            result = capture(
                "source-tag",
                [
                    "curl",
                    "-fsS",
                    f"https://api.github.com/repos/{repository}/git/tags/{tag_sha}",
                ],
            )
            if statuses["source-tag"] == 0:
                tag_info = json.loads(result)
                commit = tag_info["object"]["sha"]
                if not tag_info["verification"][
                    "verified"
                ] or not archive_root.endswith(commit[:7]):
                    missing(
                        "source-identity",
                        "Signed tag does not match the fetched archive root.",
                    )
    else:
        missing("source-archive", f"Missing original source tarball: {tarball}")
    write_json(dest / "diagnostic-status.json", statuses)
    return int(any(statuses.values()))


def collect():
    manifest = json.loads((EVIDENCE / "manifest.json").read_text())
    subprocess.run(
        ["docker", "cp", str(HELPER), f"{CONTAINER}:/tmp/diagnostics.py"], check=True
    )
    status = record(
        EVIDENCE,
        "collection",
        [
            "docker",
            "exec",
            "-e",
            "LC_ALL=C",
            CONTAINER,
            "python3",
            "/tmp/diagnostics.py",
            "inside",
            manifest["source_version"],
            manifest["source_package"],
            manifest["source_repository"],
        ],
    )
    # Recover the allowlisted partial evidence even if an inspection failed.
    copied = subprocess.run(
        [
            "docker",
            "cp",
            f"{CONTAINER}:/arm64-diagnostic-evidence",
            str(EVIDENCE / "container"),
        ]
    )
    return status or copied.returncode


def validate():
    status = record(
        EVIDENCE,
        "validation",
        [
            sys.executable,
            "-m",
            "tools.packaging_automation.validate_build_output",
            "--output_file",
            str(EVIDENCE / "build.stdout.log"),
            "--ignore_file",
            str(Path("input/packaging_ignore.yml").resolve()),
            "--package_type",
            "deb",
        ],
    )
    for stream in ("stdout", "stderr"):
        print(
            (EVIDENCE / f"validation.{stream}.log").read_text(errors="surrogateescape")
        )
    return status


def cleanup():
    names = subprocess.check_output(
        ["docker", "container", "ls", "--all", "--format", "{{.Names}}"], text=True
    ).splitlines()
    if CONTAINER in names:
        subprocess.run(["docker", "rm", "--force", "--volumes", CONTAINER], check=True)
    else:
        print("No diagnostic container was created.")


def redact():
    token = os.environ["GITHUB_TOKEN"].encode()
    if not token:
        raise ValueError("A job token is required for artifact redaction.")
    secrets = (token, base64.b64encode(b"x-access-token:" + token))
    for path in EVIDENCE.rglob("*"):
        if path.is_symlink() or path.name in (".git", ".curlrc"):
            raise ValueError(f"Forbidden artifact path: {path}")
        if path.is_file():
            data = path.read_bytes()
            if path.suffix in (".deb", ".ddeb"):
                if any(secret in data for secret in secrets):
                    raise ValueError(f"Token found in binary artifact: {path}")
            else:
                for secret in secrets:
                    data = data.replace(secret, b"[REDACTED_JOB_TOKEN]")
                path.write_bytes(data)
    print(
        "Artifact text redacted; no environment or whole source/filesystem was collected."
    )


if __name__ == "__main__":
    if sys.argv[1] == "inside":
        sys.exit(collect_inside(*sys.argv[2:]))
    actions = {
        "prepare": prepare,
        "build": build,
        "collect": collect,
        "validate": validate,
        "cleanup": cleanup,
        "redact": redact,
    }
    sys.exit(actions[sys.argv[1]]())
