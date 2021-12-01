# Citus Packaging

A set of scripts that generate a set of Dockerfiles that generate a set of Docker images which generate PostgreSQL 9.6/10/11-compatible builds of Citus projects on many platforms.

## Prerequisites

Building on all these platforms brings some complexity, so be sure you’ve got the prerequisites set up. Packages build using `docker` , so you’ll need that. In addition, you’ll need to generate a GitHub personal access token to allow scripts to call  GitHub APIs on your behalf.

### Docker

You need `docker` installed and configured. On Linux, just install Docker.

#### OS X

If you’re on OS X, this dependency presently means you also need `docker-machine` with a running `default` machine. This means you’ll also want VirtualBox to drive that `default` machine. Full details would take too long to explain, but if you’re already running Homebrew, just do:

  1. `brew install docker docker-machine`
  2. Install VirtualBox from [here](https://www.virtualbox.org/wiki/Downloads)
  3. `docker-machine create --driver virtualbox default`

After this, `docker` commands will work so long as you’ve run `eval "$(docker-machine env default)"` in the window you’re using. The [Docker Mac beta](https://blog.docker.com/2016/03/docker-for-mac-windows-beta/) will simplify this _greatly_ (no explicit need for `docker-machine` , no need for VirtualBox).

### GitHub Authentication

Ensure you’re logged in to GitHub, then visit [this page](https://github.com/settings/tokens) and press the “Generate new token” button. Name the token something like _packaging_, then check the top-level _repo_ and _user_ buttons, then press the “Generate token” button.

**Do not leave the next page until you’ve copied your new token**. Add a line like the following to your `.bash_profile` or `.zshrc` to ensure shells have access to your new token:

    export GITHUB_TOKEN=<your token here>

## Usage

Unless you have a reason to change the Dockerfiles, just use the images hosted on Docker Hub. They’ll be pulled automatically as they’re needed.

### Building Packages

To build all packages, run the `build_packages` script from the project root. Output will be put in OS/release-specific subdirectories of a `packages` directory in the project root. `build_packages` expects two arguments: a project name and build type.

The project name must be one of: `citus` , `enterprise` , or `rebalancer`

The build type can be `release` , `nightly` , or any valid git reference. `release` builds the latest release tag (which must be signed by a key known to GitHub). `nightly` builds the latest commit from the “main” branch for the specified project. Any other value is interpreted by what it means to git… tags, branches, and commit identifiers are all accepted.

By default, `build_packages` builds on _all_ supported operating systems. Edit `os-list.csv` if you wish to build for fewer.

### Updating Dockerfiles

`update_dockerfiles` generates a new set of Dockerfiles. This repository has automated builds configured, so if you need to change the Docker images, run `update_dockerfiles` , commit the resulting Dockerfile changes, and push.

### Updating Docker Images

Before building the packages yourself you should run `./pull_images` , so that you
get the current upstream layers. This can save some time when building the
packages.
`update_images` will build Docker images for all operating systems specified in `os-list.csv` using the files in the `dockerfiles` directory. This is handy for testing changes to our Docker images.

### Pushing images

Do not push docker images yourself. This should be done by merging your PR into
the `develop` branch instead.

## License

The following license information (and associated [license](LICENSE) file) apply _only to the files within **this** repository_. Please consult the repositories for the individual projects for information regarding their licensing.

Copyright © 2016–2017 Citus Data, Inc.

Licensed under the Apache License, Version 2.0 (the “License”); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an “AS IS” BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
