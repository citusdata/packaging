#!/bin/bash

main_branch_name=$(git branch --show-current)

pr_branch_name="${main_branch_name}-$(date +%s)"

git checkout -b "${pr_branch_name}"

python tools/python/update_package_properties.py --gh_token ${GH_TOKEN} --prj_name "${PRJ_NAME}" --prj_ver "${PRJ_VER}" --tag_name "${TAG_NAME}" --fancy "${FANCY}" \
  --fancy_ver_no "${FANCY_VERSION_NO}" --email "${MICROSOFT_EMAIL}" --name "${NAME}" --date "$(date '+%Y.%m.%d %H:%M:%S %z')" --exec_path "$(pwd)"

commit_message="Bump to Version ${PRJ_VER}"

git commit -m commit_message

git push origin "${pr_branch_name}"

echo "Message:"
echo "{\"title\":\"${commit_message}\", \"head\":\"${pr_branch_name}\", \"base\":\"${main_branch_name}\"}"
curl -g -H "Accept: application/vnd.github.v3.full+json" -X POST --user "${GH_TOKEN}:x-oauth-basic" -d "{\"title\":\"${commit_message}\", \"head\":\"${pr_branch_name}\", \"base\":\"${main_branch_name}\"}" https://api.github.com/repos/citusdata/packaging/pulls
