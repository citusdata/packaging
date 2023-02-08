import yaml
import subprocess
import os
import shlex

platform = os.getenv("PLATFORM")
github_token = os.getenv("GH_TOKEN")
packaging_secret_key = os.getenv("PACKAGING_SECRET_KEY")
packaging_passphrase = os.getenv("PACKAGING_PASSPHRASE")
build_type = os.getenv("BUILD_TYPE")
current_path = os.getcwd()


def run_with_output(command, *args, **kwargs):
    # this method's main objective is to return output. Therefore it is caller's responsibility to handle
    # success status
    # pylint: disable=subprocess-run-check
    result = subprocess.run(shlex.split(command), *args, capture_output=True, **kwargs)
    return result


# load yaml file
postgres_matrix_filename = f"postgres-matrix.yml"
with open(postgres_matrix_filename) as file:
    data = yaml.full_load(file)

# get the postgres_versions list

version_matrix = data['version_matrix']
print(f"Version matrix: {version_matrix[0][list(version_matrix[0].keys())[0]]['postgres_versions']}")
postgres_versions = version_matrix[0][list(version_matrix[0].keys())[0]]['postgres_versions']

# loop through each version and write to a separate file
for version in postgres_versions:
    version_matrix[0][list(version_matrix[0].keys())[0]]['postgres_versions'] = [version]

    with open(postgres_matrix_filename, 'w') as file:
        print(f"Package build for postgres version {version} started")
        yaml.dump(data, file)
        result = run_with_output(
            f"python -m tools.packaging_automation.citus_package --gh_token {github_token} --platform {platform} "
            f"--build_type nightly --secret_key '{packaging_secret_key}' --passphrase '{packaging_passphrase}' "
            f"--output_dir {current_path}/packages/ --input_files_dir {current_path}/packaging", text=True)
        if result.stderr:
            print(result.stderr)
        if result.stdout:
            print(result.stdout)

        print(f"Package build for postgres version {version} finished")

version_matrix[0][list(version_matrix[0].keys())[0]]['postgres_versions'] = postgres_versions
with open(postgres_matrix_filename, 'w') as file:
    yaml.dump(data, file)
