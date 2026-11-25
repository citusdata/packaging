#!/usr/bin/env python3
"""
Docker-based package installation tester.

Pulls a Docker image, starts a container, copies the test scripts into it,
and runs the appropriate installation + verification tests for the given OS.

Usage:
    python run_test.py <os_name>/<os_version> <pg_major_version> <citus_full_version>

Examples:
    python run_test.py ubuntu/noble 18 14.0.0
    python run_test.py el/9 18 14.0.0
"""

import argparse
import os
import re
import subprocess
import sys
from typing import Dict, Optional

# Force line-buffered stdout so print() output appears in order
# with subprocess output (Python fully buffers stdout in non-TTY
# environments like CI).
sys.stdout.reconfigure(line_buffering=True)

BARE_VER_RE = re.compile(r"^([0-9]+)\.([0-9]+)\.([0-9]+)$")
EXACT_STABLE_RE = re.compile(r"^([0-9]+)\.([0-9]+)\.([0-9]+)\.citus-([0-9]+)$")
PRERELEASE_RE = re.compile(
    r"^([0-9]+)\.([0-9]+)\.([0-9]+)[_-]((beta|rc)[0-9]*)(?:\.citus-([0-9]+))?$"
)
NIGHTLY_DEB_RE = re.compile(
    r"^([0-9]+)\.([0-9]+)\.([0-9]+)\.citus~git\.([0-9]+)\.([0-9a-f]+)-([0-9]+)$"
)
NIGHTLY_RPM_RE = re.compile(
    r"^([0-9]+)\.([0-9]+)\.([0-9]+)\.citus-0\.0\.git\.([0-9]+)\.([0-9a-f]+)$"
)


def parse_citus_version(raw: str, os_name: str) -> Dict[str, str]:
    """Parse bare X.Y.Z, exact revision (e.g. 14.3.0.citus-1), prerelease, or nightly."""
    is_deb = os_name in ("ubuntu", "debian")
    if m := BARE_VER_RE.match(raw):
        return {
            "pkg_revision": f"{raw}.citus-1",
            "expected_version": raw,
            "git_ref": f"v{raw}",
        }
    if m := EXACT_STABLE_RE.match(raw):
        base = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
        return {"pkg_revision": raw, "expected_version": base, "git_ref": f"v{base}"}
    if m := PRERELEASE_RE.match(raw):
        maj, min_, pat, stage, rev = (
            m.group(1),
            m.group(2),
            m.group(3),
            m.group(4),
            m.group(6) or "1",
        )
        base = f"{maj}.{min_}.{pat}"
        sep = "-" if is_deb else "_"
        return {
            "pkg_revision": f"{base}{sep}{stage}.citus-{rev}",
            "expected_version": f"{maj}.{min_}",
            "git_ref": f"v{base}_{stage}",
        }
    if m := NIGHTLY_DEB_RE.match(raw):
        maj, min_, pat, date, sha, rev = m.groups()
        base = f"{maj}.{min_}.{pat}"
        pkg_rev = raw if is_deb else f"{base}.citus-0.0.git.{date}.{sha}"
        return {
            "pkg_revision": pkg_rev,
            "expected_version": f"+git.{date}.{sha}",
            "git_ref": "main",
        }
    if m := NIGHTLY_RPM_RE.match(raw):
        maj, min_, pat, date, sha = m.groups()
        base = f"{maj}.{min_}.{pat}"
        pkg_rev = f"{base}.citus~git.{date}.{sha}-1" if is_deb else raw
        return {
            "pkg_revision": pkg_rev,
            "expected_version": f"+git.{date}.{sha}",
            "git_ref": "main",
        }
    raise ValueError(
        f"Invalid Citus version/revision {raw!r}; expected X.Y.Z, X.Y.Z.citus-N, prerelease, or nightly."
    )


def pull_docker_image(image_name: str) -> bool:
    print(f"Pulling Docker image: {image_name}")

    try:
        result = subprocess.run(
            ["docker", "pull", image_name], stdout=sys.stdout, stderr=sys.stdout
        )

        if result.returncode == 0:
            print(f"Successfully pulled image: {image_name}")
            return True
        else:
            print(f"Error pulling image: {image_name}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"Error during image pull: {e}", file=sys.stderr)
        return False


def start_container(image_name: str) -> Optional[str]:
    print(f"Starting container from image: {image_name}")

    try:
        result = subprocess.run(
            ["docker", "run", "-d", image_name, "sleep", "infinity"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            container_id = result.stdout.strip()
            print(f"Container started with ID: {container_id}")
            return container_id
        else:
            print(f"Error starting container: {result.stderr}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"Error during container start: {e}", file=sys.stderr)
        return None


def copy_into_container(
    container_id: str, local_path: str, container_path: str
) -> bool:
    print(f"Copying {local_path} to container {container_id}:{container_path}")

    try:
        result = subprocess.run(
            ["docker", "cp", local_path, f"{container_id}:{container_path}"],
            stdout=sys.stdout,
            stderr=sys.stdout,
        )

        if result.returncode == 0:
            print(f"Successfully copied {local_path} to container")
            return True
        else:
            print(f"Error copying file into container.", file=sys.stderr)
            return False
    except Exception as e:
        print(f"Error during file copy: {e}", file=sys.stderr)
        return False


def run_command_in_container(
    container_id: str, command: str, env_vars: Optional[Dict[str, str]] = None
) -> bool:
    print(f"Executing command in container {container_id}")

    try:
        cmd = ["docker", "exec"]
        for k, v in (env_vars or {}).items():
            cmd.extend(["-e", f"{k}={v}"])
        cmd.extend([container_id, "bash", "-c", command])
        result = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stdout)
        return result.returncode == 0
    except Exception as e:
        print(f"Error during command execution: {e}", file=sys.stderr)
        return False


def main(
    os_name: str,
    os_version: str,
    pg_major_version: str,
    citus_version_arg: str,
    channel: str = "community",
    retry_attempts: int = 1,
    retry_delay: int = 30,
    smoke_only: bool = False,
):
    parsed = parse_citus_version(citus_version_arg, os_name)
    pkg_revision = parsed["pkg_revision"]
    expected_version = parsed["expected_version"]
    git_ref = parsed["git_ref"]

    if os_name == "ubuntu" or os_name == "debian":
        os_specific_dir = "deb"
        install_package_command = (
            f"bash /install_package.sh {pg_major_version} {pkg_revision}"
        )
        pg_binary_path = f"/usr/lib/postgresql/{pg_major_version}/bin"
        image_name = f"{os_name}:{os_version}"
    elif os_name == "el" or os_name == "ol":
        os_specific_dir = "rpm"
        install_package_command = (
            f"bash /install_package.sh {pg_major_version} {pkg_revision} {os_version}"
        )
        pg_binary_path = f"/usr/pgsql-{pg_major_version}/bin"
        image_name = (
            f"almalinux:{os_version}"
            if os_name == "el"
            else f"oraclelinux:{os_version}"
        )
    else:
        print(f"Unsupported OS: {os_name}. Exiting.", file=sys.stderr)
        sys.exit(1)

    script_relative_paths = [
        f"{os_specific_dir}/install_package.sh",
        "common/test_basics.sh",
        f"{os_specific_dir}/install_regression_test_deps.sh",
        "common/run_multi_schedule.sh",
    ]

    commands = [
        "sed -i 's/\\r$//' /install_package.sh /test_basics.sh /install_regression_test_deps.sh /run_multi_schedule.sh",
        install_package_command,
        f"bash /test_basics.sh {pg_major_version} {expected_version} {pg_binary_path}",
    ]
    if not smoke_only:
        commands.extend(
            [
                f"bash /install_regression_test_deps.sh {pg_major_version} {expected_version}",
                f"bash /run_multi_schedule.sh {pg_binary_path}",
            ]
        )

    container_env = {
        "CITUS_CHANNEL": channel,
        "CITUS_INSTALL_RETRIES": str(retry_attempts),
        "CITUS_INSTALL_RETRY_DELAY": str(retry_delay),
        "CITUS_GIT_REF": git_ref,
    }

    # Pull the Docker image
    if not pull_docker_image(image_name):
        print("Failed to pull Docker image. Exiting.", file=sys.stderr)
        sys.exit(1)

    container_id = start_container(image_name)
    if not container_id:
        print("Failed to start Docker container. Exiting.", file=sys.stderr)
        sys.exit(1)

    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Copy all necessary scripts into the container first
        for p in script_relative_paths:
            script_path = os.path.join(script_dir, p)
            if not copy_into_container(container_id, script_path, "/"):
                print(f"Failed to copy {p} into container. Exiting.", file=sys.stderr)
                sys.exit(1)

        # Execute the scripts in order
        for c in commands:
            print(f"Running {c} in container...")
            if not run_command_in_container(container_id, c, container_env):
                print(f"Failed to execute {c} in container. Exiting.", file=sys.stderr)
                sys.exit(1)
    finally:
        # Cleanup: force-remove the container (stops it if still running)
        print(f"Removing container {container_id}")
        try:
            subprocess.run(
                ["docker", "rm", "-f", container_id],
                stdout=sys.stdout,
                stderr=sys.stdout,
            )
            print(f"Container {container_id} removed successfully.")
        except Exception as e:
            print(f"Error removing container: {e}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Docker-based exact-version Citus package installation tester."
    )
    parser.add_argument("platform", help="Target OS in os_name/os_version form")
    parser.add_argument("pg_major_version", help="PostgreSQL major version (e.g. 17)")
    parser.add_argument(
        "citus_version",
        help="Exact package revision (e.g. 14.3.0.citus-1) or X.Y.Z",
    )
    parser.add_argument(
        "--channel",
        default="community",
        choices=["community", "community-nightlies"],
    )
    parser.add_argument("--retry-attempts", type=int, default=1)
    parser.add_argument("--retry-delay", type=int, default=30)
    parser.add_argument("--smoke-only", action="store_true")
    args = parser.parse_args()

    if "/" not in args.platform:
        print("Platform must be in os_name/os_version format.", file=sys.stderr)
        sys.exit(1)
    os_name, os_version = args.platform.split("/", 1)

    if not args.pg_major_version.isdigit():
        print(
            "PostgreSQL major version must be a number (e.g., 18). Exiting.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        parse_citus_version(args.citus_version, os_name)
    except ValueError as err:
        print(str(err), file=sys.stderr)
        sys.exit(1)

    main(
        os_name,
        os_version,
        args.pg_major_version,
        args.citus_version,
        channel=args.channel,
        retry_attempts=max(1, args.retry_attempts),
        retry_delay=max(1, args.retry_delay),
        smoke_only=args.smoke_only,
    )
