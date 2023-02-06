import yaml
import subprocess
import os

platform = os.getenv("PLATFORM")
github_token = os.getenv("GH_TOKEN")
packaging_secret_key = os.getenv("PACKAGING_SECRET_KEY")
packaging_passphrase = os.getenv("PACKAGING_PASSPHRASE")
current_path = os.getcwd()

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
    print(f"Running for version:  {version}")
    print(f"Platform: {platform}")
    print(f"Github token: {github_token}")
    print(f"packaging_secret_key: {packaging_secret_key}")
    print(f"packaging_passphrase: {packaging_passphrase}")
    with open(postgres_matrix_filename, 'w') as file:
        yaml.dump(data, file)
        print()
        result = subprocess.run(
            ["python", "-m", "tools.packaging_automation.citus_package", "--gh_token", github_token, "--platform",
             platform,
             "--build_type", "nightly",
             "--secret_key", packaging_secret_key,
             "--passphrase", packaging_passphrase,
             "--output_dir", f"{current_path}/packages/",
             "--input_files_dir", f"{current_path}/packaging"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.stderr:
            print(result.stderr.decode("utf-8"))
        if result.stdout:
            print(result.stdout.decode("utf-8"))

version_matrix[0][list(version_matrix[0].keys())[0]]['postgres_versions'] = postgres_versions
with open(postgres_matrix_filename, 'w') as file:
    yaml.dump(data, file)