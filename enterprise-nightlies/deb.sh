#!/bin/bash

unknown_os ()
{
  echo "Unfortunately, your operating system distribution and version are not supported by this script."
  echo
  echo "Please email engage@citusdata.com with any issues."
  exit 1
}

arch_check ()
{
  if [ "$(uname -m)" != 'x86_64' ]; then
    echo "Unfortunately, the Citus repository does not contain packages for non-x86_64 architectures."
    echo
    echo "Please email engage@citusdata.com with any issues."
    exit 1
  fi
}

curl_check ()
{
  echo "Checking for curl..."
  if command -v curl > /dev/null; then
    echo "Detected curl..."
  else
    echo -n "Installing curl... "
    apt-get install -y --no-install-recommends curl &> /dev/null
    echo "done."
  fi
}

pgdg_check ()
{
  echo "Checking for postgresql-9.6..."
  if apt-cache show postgresql-9.6 &> /dev/null; then
    echo "Detected postgresql-9.6..."
  else
    pgdg_list='/etc/apt/sources.list.d/pgdg.list'
    pgdg_source_path="deb http://apt.postgresql.org/pub/repos/apt/ ${codename}-pgdg main"
    pgdg_key_url='https://www.postgresql.org/media/keys/ACCC4CF8.asc'

    if [ -e $pgdg_list ]; then
      echo "Unable to install PostgreSQL Apt Repository"
      echo
      echo "The file ${pgdg_list} already exists."
      echo
      echo "Contact engage@citusdata.com with information about your system for help."
      exit 1
    fi

    echo -n "Installing ${pgdg_list}... "

    # create an apt config file for the PGDG repository
    echo "${pgdg_source_path}" > $pgdg_list
    echo "done."

    echo -n "Installing ca-certificates... "
    apt-get install -y --no-install-recommends ca-certificates &> /dev/null
    echo "done."

    echo -n "Importing PostgreSQL gpg key... "
    # import the gpg key
    curl -L "${pgdg_key_url}" 2> /dev/null | apt-key add - &>/dev/null
    echo "done."
  fi
}

install_debian_keyring ()
{
  if [ "${os}" = "debian" ]; then
    echo "Installing debian-archive-keyring which is needed for installing "
    echo "apt-transport-https on many Debian systems."
    apt-get install -y debian-archive-keyring &> /dev/null
  fi
}

get_unique_id ()
{
  echo "A host ID was not specified, using the machine's hostname..."

  CITUS_REPO_HOST_ID=`hostname -f 2>/dev/null`
  if [ "$CITUS_REPO_HOST_ID" = "" ]; then
    CITUS_REPO_HOST_ID=`hostname 2>/dev/null`
    if [ "$CITUS_REPO_HOST_ID" = "" ]; then
      CITUS_REPO_HOST_ID=$HOSTNAME
    fi
  fi

  if [ "$CITUS_REPO_HOST_ID" = "" -o "$CITUS_REPO_HOST_ID" = "(none)" ]; then
    echo "This script tries to use your machine's hostname as a host ID by"
    echo "default, however, this script was not able to determine your "
    echo "hostname!"
    echo
    echo "You can override this by setting 'CITUS_REPO_HOST_ID' to any unique "
    echo "identifier (hostname, shasum of hostname, "
    echo "etc) prior to running this script."
    echo
    echo
    echo "If you'd like to use your hostname, please consult the documentation "
    echo "for your system. The files you need to modify to do this vary "
    echo "between Linux distribution and version."
    echo
    echo
    exit 1
  fi
}

detect_os ()
{
  if [[ ( -z "${os}" ) && ( -z "${dist}" ) ]]; then
    # some systems dont have lsb-release yet have the lsb_release binary and
    # vice-versa
    if [ -e /etc/lsb-release ]; then
      . /etc/lsb-release

      if [ "${ID}" = "raspbian" ]; then
        os=${ID}
        dist=`cut --delimiter='.' -f1 /etc/debian_version`
      else
        os=${DISTRIB_ID}
        dist=${DISTRIB_CODENAME}

        if [ -z "$dist" ]; then
          dist=${DISTRIB_RELEASE}
        fi
      fi

    elif [ `which lsb_release 2>/dev/null` ]; then
      dist=`lsb_release -c | cut -f2`
      os=`lsb_release -i | cut -f2 | awk '{ print tolower($1) }'`

    elif [ -e /etc/debian_version ]; then
      # some Debians have jessie/sid in their /etc/debian_version
      # while others have '6.0.7'
      os=`cat /etc/issue | head -1 | awk '{ print tolower($1) }'`
      if grep -q '/' /etc/debian_version; then
        dist=`cut --delimiter='/' -f1 /etc/debian_version`
      else
        dist=`cut --delimiter='.' -f1 /etc/debian_version`
      fi

    else
      unknown_os
    fi
  fi

  if [ -z "$dist" ]; then
    unknown_os
  fi

  # remove whitespace from OS and dist name
  os="${os// /}"
  dist="${dist// /}"

  echo "Detected operating system as $os/$dist."
}

detect_codename ()
{
  if [ "${os}" = "debian" ]; then
    case "${dist}" in
      7)
        codename='wheezy'
        ;;
      8)
        codename='jessie'
        ;;
      wheezy)
        codename="${dist}"
        ;;
      jessie)
        codename="${dist}"
        ;;
      *)
        unknown_os
        ;;
    esac
  else
    codename=${dist}
  fi
}

main ()
{
  detect_os
  detect_codename

  # Need to first run apt-get update so that apt-transport-https can be
  # installed
  echo -n "Running apt-get update... "
  apt-get update &> /dev/null
  echo "done."

  arch_check
  curl_check
  pgdg_check

  # Install the debian-archive-keyring package on debian systems so that
  # apt-transport-https can be installed next
  install_debian_keyring

  echo -n "Installing apt-transport-https... "
  apt-get install -y apt-transport-https &> /dev/null
  echo "done."

  if [ -z "$CITUS_REPO_HOST_ID" ]; then
    get_unique_id
  fi

  if [ -z "${CITUS_REPO_TOKEN}" ]; then
    echo "Could not determine enterprise-nightlies repository token."
    echo "Please set the CITUS_REPO_TOKEN environment variable."
    echo
    echo "Contact engage@citusdata.com if you continue to have problems."
    exit 1
  fi

  # escape any colons in repo token (they separate it from empty password)
  CITUS_REPO_TOKEN="${CITUS_REPO_TOKEN//:/%3A}"

  echo "Found host ID: ${CITUS_REPO_HOST_ID}"
  gpg_key_install_url="https://repos.citusdata.com/enterprise-nightlies/gpg_key_url.list?os=${os}&dist=${dist}"
  apt_config_url="https://repos.citusdata.com/enterprise-nightlies/config_file.list?os=${os}&dist=${dist}&source=script"

  gpg_key_url=`curl -GL -u "${CITUS_REPO_TOKEN}:" --data-urlencode "name=${CITUS_REPO_HOST_ID}" "${gpg_key_install_url}"`
  if [ "${gpg_key_url}" = "" ]; then
    echo "Unable to retrieve GPG key URL from: ${gpg_key_url}."
    echo "Please contact engage@citusdata.com"
    exit 1
  fi


  apt_source_path="/etc/apt/sources.list.d/citusdata_enterprise-nightlies.list"

  echo -n "Installing $apt_source_path... "

  # create an apt config file for this repository
  curl -GsSf -u "${CITUS_REPO_TOKEN}:" --data-urlencode "name=${CITUS_REPO_HOST_ID}" "${apt_config_url}" > $apt_source_path
  curl_exit_code=$?

  if [ "$curl_exit_code" = "22" ]; then
    echo
    echo
    echo -n "Unable to download repo config from: "
    echo "${apt_config_url}"
    echo
    echo "This usually happens if your operating system is not supported by "
    echo "Citus Data, or this script's OS detection failed."
    echo
    echo "If you are running a supported OS, please email engage@citusdata.com and report this."
    [ -e $apt_source_path ] && rm $apt_source_path
    exit 1
  elif [ "$curl_exit_code" = "35" ]; then
    echo "curl is unable to connect to citusdata.com over TLS when running: "
    echo "    curl ${apt_config_url}"
    echo "This is usually due to one of two things:"
    echo
    echo " 1.) Missing CA root certificates (make sure the ca-certificates package is installed)"
    echo " 2.) An old version of libssl. Try upgrading libssl on your system to a more recent version"
    echo
    echo "Contact engage@citusdata.com with information about your system for help."
    [ -e $apt_source_path ] && rm $apt_source_path
    exit 1
  elif [ "$curl_exit_code" -gt "0" ]; then
    echo
    echo "Unable to run: "
    echo "    curl ${apt_config_url}"
    echo
    echo "Double check your curl installation and try again."
    [ -e $apt_source_path ] && rm $apt_source_path
    exit 1
  else
    sed -i 's#packagecloud.io/citusdata#repos.citusdata.com#g' "${apt_source_path}"
    echo "done."
  fi

  echo -n "Importing Citus Data gpg key... "
  # import the gpg key
  curl -L "${gpg_key_url}" 2> /dev/null | apt-key add - &>/dev/null
  echo "done."

  echo -n "Running apt-get update... "
  # update apt on this system
  apt-get update &> /dev/null
  echo "done."

  echo
  echo "The repository is set up! You can now install packages."
}

main
