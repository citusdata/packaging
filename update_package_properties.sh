#!/bin/bash

PRJ_NAME="citus"
PRJ_VER="10.0.3"
TAG_NAME="v${PRJ_VER}"
FANCY="True"
FANCY_VERSION_NO=2
MICROSOFT_EMAIL="gindibay@gmail.com"
NAME="Gurkan Indibay"

[ -z "${PRJ_NAME}" ] && echo "PRJ_NAME should be non-empty value" && exit 1
[ -z "${PRJ_VER}" ] && echo "PRJ_VER should be non-empty value" && exit 1
[ -z "${TAG_NAME}" ] && echo "TAG_NAME should be non-empty value" && exit 1
[ -z "${FANCY}" ] && echo "FANCY should be non-empty value" && exit 1
[ -z "${FANCY_VERSION_NO}" ] && echo "FANCY_VERSION_NO should be non-empty value" && exit 1
[ -z "${MICROSOFT_EMAIL}" ] && echo "MICROSOFT_EMAIL should be non-empty value" && exit 1
[ -z "${NAME}" ] && echo "NAME should be non-empty value" && exit 1

main_branch_name=$(git branch --show-current)

pr_branch_name="${main_branch_name}-$(date +%s)"

commit_message="Bump to ${PRJ_NAME} ${PRJ_VER}"

git checkout -b "${pr_branch_name}"

python tools/python/update_package_properties.py --gh_token "${GH_TOKEN}" --prj_name "${PRJ_NAME}" --prj_ver "${PRJ_VER}" --tag_name "${TAG_NAME}" --fancy "${FANCY}" \
  --fancy_ver_no "${FANCY_VERSION_NO}" --email "${MICROSOFT_EMAIL}" --name "${NAME}" --date "$(date '+%Y.%m.%d %H:%M:%S %z')" --exec_path "$(pwd)"

git commit -a -m "${commit_message}"

echo "{\"title\":\"${commit_message}\", \"head\":\"${pr_branch_name}\", \"base\":\"${main_branch_name}\"}"

git push origin "${pr_branch_name}"

curl -g -H "Accept: application/vnd.github.v3.full+json" -X POST --user "${GH_TOKEN}:x-oauth-basic" -d "{\"title\":\"${commit_message}\", \"head\":\"${pr_branch_name}\", \"base\":\"${main_branch_name}\"}" https://api.github.com/repos/citusdata/packaging/pulls
