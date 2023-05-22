#!/bin/bash

unknown_os ()
{
  echo "Unfortunately, your operating system distribution and version are not supported by this script."
  echo
  echo "Please contact us via https://www.citusdata.com/about/contact_us with any issues."
  exit 1
}

arch_check ()
{
  if [ "$(uname -m)" != 'x86_64' ]; then
    echo "Unfortunately, the Citus repository does not contain packages for non-x86_64 architectures."
    echo
    echo "Please contact us via https://www.citusdata.com/about/contact_us with any issues."
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
    yum install -d0 -e0 -y curl
    echo "done."
  fi
}

pgdg_check ()
{
  echo "Checking for postgresql15-server..."
  if yum list -q postgresql15-server &> /dev/null; then
    echo "Detected postgresql15-server..."
  else
    echo -n "Installing pgdg repo... "

    if [ "${dist}" = "8" ]; then
      dnf -qy module disable postgresql
    fi

    yum install -d0 -e0 -y "${repo_url}"

    if ! yum info -q -y postgresql15-server &> /dev/null; then
      echo "PGDG repositories don't have postgresql15-server package for your operating system"
      echo "Cannot install Citus, exiting."
      exit 1
    fi

    echo "done."
  fi
}

epel_check()
{
  echo "Checking for EPEL repositories..."

  epel_release_check=`rpm -qa | grep -qw epel-release`
  if [ "$?" == "0" ]; then
    echo "Detected EPEL repoitories"
  else
    echo -n "Installing epel-release repo... "

    if [ "${os}" = "centos" ]; then
      yum install -d0 -e0 -y epel-release &> /dev/null
    elif [ ${os} = "rhel" ] || [ ${os} = "redhatenterpriseserver" ] || [ "${os}" = "ol" ]; then
      if [ ${dist} = "7" ]; then
        yum install -d0 -e0 -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-${dist}.noarch.rpm &> /dev/null
      elif [ ${dist} = "8" ]; then
        dnf install -d0 -e0 -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-${dist}.noarch.rpm &> /dev/null
      fi
    fi

    epel_release_check=`rpm -qa | grep -qw epel-release`
    if [ "$?" != "0" ]; then
      echo
      echo "WARNING: "
      echo "The EPEL repository could not be installed. This means You may not be able to satisfy package dependencies. "
      echo "To fix this, manually install EPEL repository and then install packages."
      echo "More information: https://fedoraproject.org/wiki/EPEL#How_can_I_use_these_extra_packages.3F"
      echo
    else
      echo 'done.'
    fi
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
    if [ -e /etc/os-release ]; then
      . /etc/os-release
      os=${ID}
      if [ "${os}" = "poky" ]; then
        dist=`echo ${VERSION_ID}`
      elif [ "${os}" = "sles" ]; then
        dist=`echo ${VERSION_ID}`
      elif [ "${os}" = "opensuse" ]; then
        dist=`echo ${VERSION_ID}`
      else
        dist=`echo ${VERSION_ID} | awk -F '.' '{ print $1 }'`
      fi

    elif [ `which lsb_release 2>/dev/null` ]; then
      # get major version (e.g. '5' or '6')
      dist=`lsb_release -r | cut -f2 | awk -F '.' '{ print $1 }'`

      # get os (e.g. 'centos', 'redhatenterpriseserver', etc)
      os=`lsb_release -i | cut -f2 | awk '{ print tolower($1) }'`

    elif [ -e /etc/oracle-release ]; then
      dist=`cut -f5 --delimiter=' ' /etc/oracle-release | awk -F '.' '{ print $1 }'`
      os='ol'

    elif [ -e /etc/fedora-release ]; then
      dist=`cut -f3 --delimiter=' ' /etc/fedora-release`
      os='fedora'

    elif [ -e /etc/redhat-release ]; then
      os_hint=`cat /etc/redhat-release  | awk '{ print tolower($1) }'`
      if [ "${os_hint}" = "centos" ]; then
        dist=`cat /etc/redhat-release | awk '{ print $3 }' | awk -F '.' '{ print $1 }'`
        os='centos'
      elif [ "${os_hint}" = "scientific" ]; then
        dist=`cat /etc/redhat-release | awk '{ print $4 }' | awk -F '.' '{ print $1 }'`
        os='scientific'
      else
        dist=`cat /etc/redhat-release  | awk '{ print tolower($7) }' | cut -f1 --delimiter='.'`
        os='redhatenterpriseserver'
      fi

    else
      aws=`grep -q Amazon /etc/issue`
      if [ "$?" = "0" ]; then
        dist='6'
        os='aws'
      else
        unknown_os
      fi
    fi
  fi

  if [[ ( -z "${os}" ) || ( -z "${dist}" ) ]]; then
    unknown_os
  fi

  # remove whitespace from OS and dist name
  os="${os// /}"
  dist="${dist// /}"

  echo "Detected operating system as ${os}/${dist}."
}

finalize_yum_repo ()
{
  echo -n "Installing pygpgme to verify GPG signatures... "
  yum install -d0 -e0 -y pygpgme --disablerepo='citusdata_enterprise-nightlies' &> /dev/null
  pypgpme_check=`rpm -qa | grep -qw pygpgme`
  if [ "$?" != "0" ]; then
    echo
    echo "WARNING: "
    echo "The pygpgme package could not be installed. This means GPG verification is not possible for any RPM installed on your system. "
    echo "To fix this, add a repository with pygpgme. Usualy, the EPEL repository for your system will have this. "
    echo "More information: https://fedoraproject.org/wiki/EPEL#How_can_I_use_these_extra_packages.3F"
    echo

    # set the repo_gpgcheck option to 0
    sed -i'' 's/repo_gpgcheck=1/repo_gpgcheck=0/' /etc/yum.repos.d/citusdata_enterprise-nightlies.repo
  fi
  echo 'done.'

  echo -n "Installing yum-utils... "
  yum install -d0 -e0 -y yum-utils --disablerepo='citusdata_enterprise-nightlies' &> /dev/null
  yum_utils_check=`rpm -qa | grep -qw yum-utils`
  if [ "$?" != "0" ]; then
    echo
    echo "WARNING: "
    echo "The yum-utils package could not be installed. This means you may not be able to install source RPMs or use other yum features."
    echo
  fi
  echo 'done.'

  echo -n "Generating yum cache for citusdata_enterprise-nightlies... "
  yum -d0 -e0 -q makecache -y --disablerepo='*' --enablerepo='citusdata_enterprise-nightlies' &> /dev/null
  echo 'done.'
}

finalize_zypper_repo ()
{
  zypper --gpg-auto-import-keys refresh citusdata_enterprise-nightlies
}

detect_repo_url ()
{
  # set common defaults used by all flavors
  # Various repositories of different flavors are stored in EL (e.g. Centos and OL)
  family='redhat'
  family_short='EL'
  pkg_dist="${dist}"

  case "${os}" in
    ol|centos|rhel|redhatenterpriseserver)
      ;;
    *)
      unknown_os
      ;;
  esac

  repo_url="https://download.postgresql.org/pub/repos/yum/reporpms"
  repo_url+="/${family_short}-${pkg_dist}-x86_64"
  repo_url+="/pgdg-${family}-repo-latest.noarch.rpm"
}

main ()
{
  detect_os
  detect_repo_url

  arch_check
  curl_check
  pgdg_check
  epel_check

  if [ -z "$CITUS_REPO_HOST_ID" ]; then
    get_unique_id
  fi

  if [ -z "${CITUS_REPO_TOKEN}" ]; then
    echo "Could not determine enterprise-nightlies repository token."
    echo "Please set the CITUS_REPO_TOKEN environment variable."
    echo
    echo "Contact us via https://www.citusdata.com/about/contact_us if you continue to have problems."
    exit 1
  fi

  # escape any colons in repo token (they separate it from empty password)
  CITUS_REPO_TOKEN="${CITUS_REPO_TOKEN//:/%3A}"

  yum_repo_config_url="https://packagecloud.io/install/repositories/citusdata/enterprise-nightlies/config_file.repo?os=${os}&dist=${dist}&source=script"
  echo "Found host ID: ${CITUS_REPO_HOST_ID}"

  if [ "${os}" = "sles" ] || [ "${os}" = "opensuse" ]; then
    yum_repo_path=/etc/zypp/repos.d/citusdata_enterprise-nightlies.repo
  else
    yum_repo_path=/etc/yum.repos.d/citusdata_enterprise-nightlies.repo
  fi

  echo -n "Downloading repository file: ${yum_repo_config_url}... "

  curl -GsSf -u "${CITUS_REPO_TOKEN}:" --data-urlencode "name=${CITUS_REPO_HOST_ID}" "${yum_repo_config_url}" > $yum_repo_path
  curl_exit_code=$?

  if [ "$curl_exit_code" = "22" ]; then
    echo
    echo
    echo -n "Unable to download repo config from: "
    echo "${yum_repo_config_url}"
    echo
    echo "This usually happens if your operating system is not supported by "
    echo "Citus Data, or this script's OS detection failed."
    echo
    echo "If you are running a supported OS, please contact us via https://www.citusdata.com/about/contact_us and report this."
    [ -e $yum_repo_path ] && rm $yum_repo_path
    exit 1
  elif [ "$curl_exit_code" = "35" -o "$curl_exit_code" = "60" ]; then
    echo
    echo "curl is unable to connect to citusdata.com over TLS when running: "
    echo "    curl ${yum_repo_config_url}"
    echo
    echo "This is usually due to one of two things:"
    echo
    echo " 1.) Missing CA root certificates (make sure the ca-certificates package is installed)"
    echo " 2.) An old version of libssl. Try upgrading libssl on your system to a more recent version"
    echo
    echo "Contact us via https://www.citusdata.com/about/contact_us with information about your system for help."
    [ -e $yum_repo_path ] && rm $yum_repo_path
    exit 1
  elif [ "$curl_exit_code" -gt "0" ]; then
    echo
    echo "Unable to run: "
    echo "    curl ${yum_repo_config_url}"
    echo
    echo "Double check your curl installation and try again."
    [ -e $yum_repo_path ] && rm $yum_repo_path
    exit 1
  else
    echo "done."
  fi

  if [ "${os}" = "sles" ] || [ "${os}" = "opensuse" ]; then
    finalize_zypper_repo
  else
    finalize_yum_repo
  fi

  echo
  echo "The repository is set up! You can now install packages."
}

main
