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

import os
import subprocess
import sys
from typing import Optional

# Force line-buffered stdout so print() output appears in order
# with subprocess output (Python fully buffers stdout in non-TTY
# environments like CI).
sys.stdout.reconfigure(line_buffering=True)


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


def run_command_in_container(container_id: str, command: str) -> bool:
    print(f"Executing command in container {container_id}")

    try:
        result = subprocess.run(
            ["docker", "exec", container_id, "bash", "-c", command],
            stdout=sys.stdout,
            stderr=sys.stdout,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error during command execution: {e}", file=sys.stderr)
        return False


def main(os_name: str, os_version: str, pg_major_version: str, citus_full_version: str):
    if os_name == "ubuntu" or os_name == "debian":
        os_specific_dir = "deb"
        install_package_command = (
            f"bash /install_package.sh {pg_major_version} {citus_full_version}"
        )
        pg_binary_path = f"/usr/lib/postgresql/{pg_major_version}/bin"
        image_name = f"{os_name}:{os_version}"
    elif os_name == "el" or os_name == "ol":
        os_specific_dir = "rpm"
        install_package_command = f"bash /install_package.sh {pg_major_version} {citus_full_version} {os_version}"
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
        install_package_command,
        f"bash /test_basics.sh {pg_major_version} {citus_full_version} {pg_binary_path}",
        f"bash /install_regression_test_deps.sh {pg_major_version} {citus_full_version}",
        f"bash /run_multi_schedule.sh {pg_binary_path}",
    ]

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
            if not run_command_in_container(container_id, c):
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
    if len(sys.argv) != 4:
        print(
            "Usage: python run_test.py <os_name/os_version> <pg_major_version> <citus_full_version>",
            file=sys.stderr,
        )
        print("Example: python run_test.py ubuntu/noble 18 14.0.0", file=sys.stderr)
        sys.exit(1)

    os_name, os_version = sys.argv[1].split("/")
    postgres_version = sys.argv[2]
    citus_version = sys.argv[3]

    if not postgres_version.isdigit():
        print(
            "PostgreSQL major version must be a number (e.g., 18). Exiting.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not (
        len(citus_version.split(".")) == 3
        and all(p.isdigit() for p in citus_version.split("."))
    ):
        print(
            "Citus version must be in the format major.minor.patch (e.g., 14.0.0). Exiting.",
            file=sys.stderr,
        )
        sys.exit(1)

    main(os_name, os_version, postgres_version, citus_version)
