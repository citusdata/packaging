class Citus < Formula
  desc "PostgreSQL-based distributed RDBMS"
  homepage "https://www.citusdata.com"
  version "5.0.0-rc.3"
  url "https://api.github.com/repos/citusdata/citus/tarball/v#{version}?access_token=#{ENV["GITHUB_TOKEN"]}"
  sha256 "e6d55066a721c64d677c1325778e6466892610836bec56e9d588d945a0286682"

  bottle do
    root_url "https://s3.amazonaws.com/packages.citusdata.com/homebrew"
    cellar :any
    sha256 "e5a7988f14f3dfb65f516190d0818c66388c198a80691f5db9f3d92d1262bfba" => :el_capitan
  end

  depends_on "postgresql"

  def install
    config_args = %W[--prefix=#{prefix} PG_CONFIG=#{Formula["postgresql"].opt_bin}/pg_config]

    system "./configure", *config_args
    system "make"

    mkdir "stage"
    system "make", "install", "DESTDIR=#{buildpath}/stage"

    bin.install Dir["stage/**/bin/*"]
    lib.install Dir["stage/**/lib/*"]
    include.install Dir["stage/**/include/*"]
    (share/"postgresql/extension").install Dir["stage/**/share/postgresql/extension/*"]
  end

  test do
    system "true"
  end
end
