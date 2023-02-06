import yaml
import subprocess

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
    with open(postgres_matrix_filename, 'w') as file:
        yaml.dump(data, file)
        result = subprocess.run(
            ["python", "-m ", "tools.packaging_automation.citus_package", "--gh_token", "'${GH_TOKEN}'", "--platform",
             "'${PLATFORM}'",
             "--build_type", "nightly",
             "--secret_key", "'${PACKAGING_SECRET_KEY}'",
             "--passphrase", "'${PACKAGING_PASSPHRASE}'",
             "--output_dir", "$(pwd)/packages/",
             "--input_files_dir", "$(pwd)/packaging"],
            capture_output=True)
        print(result.stdout.decode("utf-8"))

version_matrix[0][list(version_matrix[0].keys())[0]]['postgres_versions'] = postgres_versions
with open(postgres_matrix_filename, 'w') as file:
    yaml.dump(data, file)