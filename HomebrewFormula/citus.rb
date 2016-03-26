class Citus < Formula
  desc "PostgreSQL-based distributed RDBMS"
  homepage "https://www.citusdata.com"
  url "https://github.com/citusdata/citus/archive/v5.0.0.tar.gz"
  sha256 "a72bd7e9020c11f19d08e58f1f8aa8e83e7f1f377facb6c8020fcaa917f9a3ee"

  head "https://github.com/citusdata/citus.git"

  bottle do
    root_url "https://s3.amazonaws.com/packages.citusdata.com/homebrew"
    cellar :any
    sha256 "b3674e884b60b9f2d846bf857e3fc53e9b51a2e13dae2ced44d5a2844296d764" => :el_capitan
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
    pg_bin = Formula["postgresql"].opt_bin
    pg_port = "55561"
    system "#{pg_bin}/initdb", testpath/"test"
    pid = fork do
      exec("#{pg_bin}/postgres",
           "-D", testpath/"test",
           "-c", "shared_preload_libraries=citus",
           "-p", pg_port)
    end

    begin
      sleep 2

      count_workers_query = "SELECT COUNT(*) FROM master_get_active_worker_nodes();"

      system "#{pg_bin}/createdb", "-p", pg_port, "test"
      system "#{pg_bin}/psql", "-p", pg_port, "-d", "test", "--command", "CREATE EXTENSION citus;"

      assert_equal "0", shell_output("#{pg_bin}/psql -p #{pg_port} -d test -Atc" \
                                     "'#{count_workers_query}'").strip
    ensure
      Process.kill 9, pid
      Process.wait pid
    end
  end
end
