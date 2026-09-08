#!/bin/bash
# Run with: bash tests/deb-detection.sh
set -eo pipefail

repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)

check ()
{
  local expected=$1 input_os=$2 input_dist=$3 expected_codename=${4-}
  local output status
  if output=$(
    # Only detection functions are loaded, never main or installation helpers.
    eval "$detection_functions"
    for tool in apt apt-get apt-key apt-cache curl wget gpg mkdir mv rm chmod sed tee; do
      eval "$tool () { echo 'Unexpected $tool call' >&2; exit 99; }"
    done
    os=$input_os
    dist=$input_dist
    codename=
    if [ "$os" = '<unset>' ]; then unset os; fi
    detect_os
    detect_codename
    printf 'ACCEPTED:%s\n' "$codename"
  ); then
    status=0
  else
    status=$?
  fi

  if [ "$status" != "$expected" ] ||
     { [ "$expected" = 1 ] && [[ "$output" != *"Debian 11 (bullseye) is no longer supported."* ]]; } ||
     { [ "$expected" = 0 ] && [[ "$output" != *"ACCEPTED:$expected_codename" ]]; }; then
    printf 'FAIL %s os=%q dist=%q: status=%s\n%s\n' "$script" "$input_os" "$input_dist" "$status" "$output" >&2
    exit 1
  fi
}

for channel in community community-nightlies enterprise enterprise-nightlies; do
  script="$repo_dir/$channel/deb.sh"
  # Accept Windows checkout line endings without modifying the source files.
  script_text=$(tr -d '\r' < "$script")
  bash -n <<< "$script_text"
  detection_functions=$(awk '
    /^(unknown_os|detect_os|detect_codename) \(\)/ { copying=1 }
    copying { print }
    copying && /^}/ { copying=0 }
  ' <<< "$script_text")
  first_command=$(awk '
    /^main \(\)/ { in_main=1; next }
    in_main && /^[[:space:]]*(#|$|\{)/ { next }
    in_main { print; exit }
  ' <<< "$script_text")
  if [ "$first_command" != '  detect_os' ]; then
    echo "FAIL $script: detection must precede installer side effects." >&2
    exit 1
  fi

  # Nonempty explicit dist values skip host discovery, including with os unset.
  for input_os in debian Debian ' De bian ' '' '   ' '<unset>'; do
    for input_dist in 11 11.11 bullseye BULLSEYE ' Bull seye '; do
      check 1 "$input_os" "$input_dist"
    done
  done
  for pair in 12:bookworm 13:trixie 14:forky; do
    check 0 debian "${pair%%:*}" "${pair#*:}"
    check 0 debian "${pair#*:}" "${pair#*:}"
  done
  check 0 ubuntu jammy jammy
  check 0 Ubuntu noble noble
  check 0 ubuntu 11 11
  check 0 raspbian 11 11
  check 0 raspbian bullseye bullseye
  check 0 custom bullseye bullseye
  check 0 '' bookworm bookworm
  check 0 '<unset>' 12 12
  echo "PASS $channel/deb.sh"
done
