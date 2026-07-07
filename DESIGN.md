# DESIGN.md — ansible-role-sendy_install

Authoritative spec for this role. If code disagrees with this file, this
file is right — flag the discrepancy and ask before changing this file
to match the code.

## Scope

First-time install of Sendy on a host that already has a web server,
PHP, and MySQL/MariaDB provisioned by other roles/processes. Pairs with
the sibling `realtime.sendy` role, which handles upgrading an existing
install. OS patching, web server/PHP installation, and database/schema
provisioning are all explicitly out of scope for this role.

## Settled decisions

These were confirmed with the role owner (Bob Tanner) when this role was
first scaffolded (2026-07-03):

* **Sendy source** = a zip staged on the Ansible control node
  (`sendy_install_zip_src`), matching the sibling `realtime.sendy` role's
  pattern. Sendy is commercial software with no public download URL.
* **Database** = the MySQL/MariaDB *server* is assumed pre-provisioned
  and already running on the target. This role creates the Sendy
  database, user, and grants (added 2026-07-04, confirmed with Bob
  Tanner) using `ansible.mysql`. Something else in the deployment
  pipeline must still install/start the database server and import
  Sendy's schema (tables); this role does not do either of those.
* **Database connection = TCP, not unix socket** (changed 2026-07-06,
  confirmed with Bob Tanner; **breaking change** from the original
  2026-07-04 decision above). Production database is RDS, which has no
  unix socket to connect over, so `tasks/database.yml` now authenticates
  to `sendy_install_db_host:sendy_install_db_port` over TCP as
  `sendy_install_db_admin_user`/`sendy_install_db_admin_password` — a
  privileged account analogous to an RDS instance's master user — rather
  than the local root user via `auth_socket`. `sendy_install_db_socket`
  is removed entirely; there is no toggle between socket and TCP, since
  nothing currently exercises a socket-only target. This role never
  assumes an implicit root/admin login — admin credentials must always
  be supplied explicitly, vault-managed like `sendy_install_db_password`.
* **Web server** = Apache only, no `sendy_install_webserver_service`
  variable. This role never restarts or configures the web server
  itself — there's currently nothing in this role's own tasks that
  requires it to.
* **Supported platforms** = Debian (bookworm, trixie), Ubuntu (jammy,
  noble, resolute) — checked against EOL via `scripts/lookup_platform.py`
  on 2026-07-03. Revisit this list on the next sync rather than trusting
  it indefinitely.
* **Zip layout** = assumed to extract to exactly one top-level directory
  (matches the layout the sibling `realtime.sendy` role's `deploy.yml`
  already validated against a real Sendy release zip).
* **Version guard** (added 2026-07-03, after the initial scaffold) = the
  role parses a semantic version (X.Y.Z) from `sendy_install_zip_src`'s
  filename (e.g. `sendy-7.0.6.zip` -> `7.0.6`) and records the version
  it installs at `sendy_install_version_marker`
  (`/var/lib/sendy_install/version` by default, outside the web root).
  On every run, preflight fails if the new zip's version is the same as
  or older than what's recorded there. This guard exists alongside, not
  instead of, the pre-existing "fail if `includes/config.php` already
  exists" check — this role is still install-only; the version guard is
  a filename-sanity/downgrade safety net, not a path to reinstalling or
  upgrading in place.
* **`sendy_install_force_reinstall`** (added 2026-07-04, for testing the
  upgrade path against `realtime.sendy`) = bypasses only the version
  guard above, so a rebuilt test host with a stale
  `sendy_install_version_marker` doesn't block a repeat run. Deliberately
  does not touch the "already installed" guard — bypassing that one
  would mean this role can reinstall over an existing Sendy, which
  contradicts install-only Scope above. Defaults to `false`.
* **This role installs its own direct dependencies via
  `sendy_install_packages`** (`unzip`, `rsync`, `cron`, `python3-pymysql`
  by default; `cron` added 2026-07-04 after a real run failed with
  `crontab` missing; `python3-pymysql` added 2026-07-04 alongside the
  database task below, since `ansible.mysql`'s modules require a
  Python MySQL library on the target). `ansible.builtin.unarchive`
  requires the system `unzip` binary for `.zip` files — it does not fall
  back to Python's `zipfile` module in practice — `ansible.posix.synchronize`
  requires `rsync` on both ends, `ansible.builtin.cron` (used by
  `tasks/cron.yml`) requires the `crontab` executable, which ships in the
  `cron` package rather than the base OS install, and `ansible.mysql.mysql_db`/
  `mysql_user` (used by `tasks/database.yml`) require PyMySQL. This is a
  narrow exception to "no OS patching/package installation" in Scope
  above: these are direct, load-bearing dependencies of this role's own
  tasks, not general system package management, so `tasks/install.yml`
  updates the apt cache and installs `sendy_install_packages` before
  extracting. Same package names on both Debian and Ubuntu, so no
  `vars/<OsFamily>.yml` split is needed. The molecule test images already
  ship `unzip`/`rsync`/`cron` preinstalled, which is why that gap wasn't
  caught until a real host run.
* **Molecule `idempotence` step dropped.** This role deliberately fails
  on a second run (both the config.php-exists check and, now, the
  version guard would trigger) — it is not meant to be idempotent in
  the "safe to reconverge" sense. `molecule/default/molecule.yml`'s
  `test_sequence` no longer includes `idempotence`; this was already
  effectively broken by the config.php guard before the version guard
  existed, and the version guard just made it unambiguous that it
  should be removed rather than worked around.
* **config.php field names verified 2026-07-04** against both a real
  production `includes/config.php` (from a live customer host) and the
  shipped default `includes/config.php`
  inside the actual licensed `files/sendy-7.0.6.zip` — the two agree
  exactly. Verification was triggered by a real run hitting `PHP Fatal
  error: Uncaught Error: Undefined constant "APP_PATH"`. The original template
  was written from public/community knowledge and was wrong on every
  field: real Sendy defines `APP_PATH` (not `INSTALL_URL`) for the
  install URL, uses plain PHP variable assignment — `$dbHost`, `$dbUser`,
  `$dbPass`, `$dbName`, `$dbPort`, `$charset` — for DB connection details
  instead of `define()` constants, and defines `COOKIE_DOMAIN` (present,
  can be empty). Sendy's `config.php` has no `TIMEZONE` or
  `ENCRYPTION_KEY` setting at all, so `sendy_install_timezone` and
  `sendy_install_encryption_key` (and preflight's 32-character check)
  were removed as dead public-interface variables — this is a breaking
  change for any consumer that set them. `sendy_install_db_charset`
  (default `utf8mb4`, matching the verified production value) and
  `sendy_install_cookie_domain` (default `""`) were added since real
  Sendy has settings for both that the role previously never exposed.
  See `templates/config.php.j2` for the corrected format.

## Open questions

If a task touches one of these, leave a `# TODO(open-q):` comment:

* **Cron script list may be incomplete.** `sendy_install_cron_jobs`
  defaults to only the send-queue processor (`cron/campaigns.php`).
  Some Sendy versions document additional cron scripts (e.g. an
  API-triggered blast processor) — check your specific Sendy version's
  documentation and add entries if it lists more.
* **Ubuntu 26.04 (resolute) is very new** as of this role's authoring
  (current release as of 2026-07-03). If the geerlingguy image or molecule
  testing proves unreliable for it, consider dropping it from the matrix
  rather than fighting image availability — ask before doing so, per the
  usual platform-removal rule.
* **Database user auth plugin set explicitly, via plugin_auth_string not
  password** (added 2026-07-07, confirmed with Bob Tanner, after a real
  run against a self-managed MySQL 8.4 container (sendy-portal, not RDS)
  failed with `(1524, "Plugin 'mysql_native_password' is not loaded")`
  on the "Create Sendy database user" task — reproduced even against a
  freshly recreated container and volume, ruling out stale state).
  Two stacked root causes:
  1. The target server has no `mysql_native_password` plugin loaded
     (deprecated since MySQL 8.0.34, disabled by default from 8.4
     onward).
  2. `ansible.mysql.mysql_user`'s `user_add()`/`user_mod()` (see the
     installed collection's `plugin_utils/user.py`) hardcode
     `CREATE`/`ALTER USER ... IDENTIFIED WITH mysql_native_password`
     whenever a plaintext `password:` is supplied, regardless of the
     `plugin:` parameter — `plugin:` only takes effect when the password
     is instead passed as `plugin_auth_string:`. An initial fix that
     added `plugin: "{{ sendy_install_db_auth_plugin }}"` while still
     passing `password:` looked correct but was silently overridden by
     the module every run.
  `tasks/database.yml`'s `mysql_user` task now sets `plugin:
  "{{ sendy_install_db_auth_plugin }}"` (new variable, default
  `caching_sha2_password`, the current MySQL default and supported by
  the existing `python3-pymysql` dependency) together with
  `plugin_auth_string: "{{ sendy_install_db_password }}"` in place of
  `password:`. This is independent of the TLS/SSL open question below.
  Note: `caching_sha2_password` is a MySQL default — self-managed
  MariaDB targets generally only load `mysql_native_password` by default
  (`caching_sha2_password` needs `INSTALL SONAME` first, and is only
  bundled at all from MariaDB 12.1+), so `molecule/default/converge.yml`'s
  MariaDB fixture overrides `sendy_install_db_auth_plugin` back to
  `mysql_native_password` to match. Any real MariaDB consumer of this
  role should do the same.
  * TODO(open-q): `plugin_auth_string` without a `salt` means
    `caching_sha2_password`'s idempotency comparison always sees a diff
    (its hash uses a random salt), so this task will report `changed`
    on every run, not just the first. Acceptable for now since this role
    is already not idempotent by design (see below), but worth revisiting
    if that ever changes.
* **Grant host split from connection host** (added 2026-07-07, confirmed
  with Bob Tanner, after a real deployment against a Dockerized MySQL
  target hit `mysqli::__construct(): (HY000/1044): Access denied for
  user 'sendy'@'%' to database 'sendy'` — valid password, no
  privileges). Root cause: the target database was a Dockerized MySQL
  (managed by the sibling `docker_mysql` role) reached via a published
  port, not a same-host process. That deployment's inventory had
  `docker_mysql`'s optional `mysql_docker_user`/`mysql_docker_password`
  *also* set (both driven by the same underlying username/password as
  `sendy_install_db_username`/`sendy_install_db_password`), which makes
  the MySQL image auto-create `'sendy'@'%'` with **no** database grants
  (`docker_mysql` never provisions schema access, by design).
  Separately, `tasks/database.yml` created
  `'sendy'@'{{ sendy_install_db_host }}'` (`127.0.0.1`) *with* full
  grants. Because the real connecting client's apparent source address
  (as MySQL sees it through Docker's networking) isn't literally
  `127.0.0.1`, authentication matched the privilege-less `'%'` account
  instead of the granted one — valid password, wrong account, 1044.
  Fixed two ways together (per Bob Tanner's direction — no one-off
  manual `GRANT`, since `docker_mysql` wipes/recreates its volume and
  container on every run and a manual fix wouldn't survive that):
  1. `docker_mysql`'s redundant user for that host was removed from its
     inventory, so `sendy_install`'s own user creation is the sole
     source of truth for the `sendy` database account.
  2. `sendy_install_db_host` was already dual-purpose (config.php's
     `$dbHost` *and* the grant's host pattern) and can't simply become
     `%`, since `$dbHost` needs a real, connectable address. Added a
     separate `sendy_install_db_grant_host` variable (defaults to
     `sendy_install_db_host` for backward compatibility) used only for
     the created user's host scope in `tasks/database.yml`, set to `'%'`
     in that inventory's host_vars to match how the containerized
     database actually sees the connecting client.
* **TLS/SSL for the database connection is not yet supported.** RDS
  often requires or recommends TLS. `tasks/database.yml`'s TCP
  connection (added 2026-07-06) has no `ca_cert`/SSL-mode variables
  yet — add them if a target RDS instance enforces
  `rds.force_ssl` or similar.
* **The `sendy-X.Y.Z.zip` filename pattern is inferred from one example**
  (`sendy-7.0.6.zip`), not verified across multiple HelloSendy releases
  or download methods. If a future release ever ships under a different
  naming scheme (build metadata, an underscore instead of a hyphen, a
  suffix like `-full`), `tasks/preflight.yml`'s version-parsing regex
  will need updating — it currently just searches for the first
  `X.Y.Z` numeric substring in the basename.

## Consumer side notes

<!-- TODO: fill in consumer notes -->
