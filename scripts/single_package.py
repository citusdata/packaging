import yaml
import subprocess

# load yaml file
with open("postgres-matrix.yaml") as file:
    data = yaml.full_load(file)

# get the postgres_versions list
postgres_versions = data['version_matrix'][0]['postgres_versions']

# loop through each version and write to a separate file
for version in postgres_versions:
    data['version_matrix'][0]['postgres_versions'] = [version]
    filename = f"postgres-matrix.yaml"
    with open(filename, 'w') as file:
        yaml.dump(data, file)
    result = subprocess.run(
        ["python", "-m ", "tools.packaging_automation.citus_package", "--gh_token", "'${GH_TOKEN}'", "--platform",
         "'${PLATFORM}'",
         "--build_type", "nightly",
         "--secret_key", "'${PACKAGING_SECRET_KEY}'",
         "--passphrase", "'${PACKAGING_PASSPHRASE}'",
         "--output_dir", "$(pwd)/packages/",
         "--input_files_dir", "$(pwd)/packaging"],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
