# Package Installation Tests

Verifies that Citus packages can be installed from the package repository on all supported platforms.

Each test:
* spins up a Docker container for the target OS
* installs the PostgreSQL and Citus packages
* sets up a cluster and runs very basic tests
* runs `make check-multi` regression tests from the Citus repository against the installed Citus version

## Running locally

Requires **Python 3.10+** and **Docker**. No additional Python packages needed.

```bash
python3 test_package_installation/run_test.py <platform> <pg_major_version> <citus_full_version>
```

Examples:

```bash
python3 test_package_installation/run_test.py ubuntu/noble 18 14.0.0
python3 test_package_installation/run_test.py el/9 17 14.0.0
python3 test_package_installation/run_test.py debian/bookworm 16 14.0.0
```

## Running via GitHub Actions

You can manually trigger the workflow using [this GitHub Actions tab](https://github.com/citusdata/packaging/actions/workflows/test-package-installation.yml).

It automatically discovers the supported platforms, latest Citus version that we published
packages for, and compatible PostgreSQL versions from the `all-citus` branch, using
[pkgvars](https://github.com/citusdata/packaging/blob/all-citus/pkgvars),
[.github/workflows/build-package.yml](https://github.com/citusdata/packaging/blob/all-citus/.github/workflows/build-package.yml) and
[postgres-matrix.yml](https://github.com/citusdata/packaging/blob/all-citus/postgres-matrix.yml) files.
