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
* **Database** = assumed fully pre-provisioned. This role only writes
  connection details into `config.php`; it never creates a database,
  user, or imports Sendy's schema. Something else in the deployment
  pipeline must do that before this role runs.
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
  `sendy_install_packages`** (`unzip`, `rsync`, `cron` by default; `cron`
  added 2026-07-04, after a real run failed with `crontab` missing).
  `ansible.builtin.unarchive` requires the system `unzip` binary for
  `.zip` files — it does not fall back to Python's `zipfile` module in
  practice — `ansible.posix.synchronize` requires `rsync` on both ends,
  and `ansible.builtin.cron` (used by `tasks/cron.yml`) requires the
  `crontab` executable, which ships in the `cron` package rather than
  the base OS install. This is a narrow exception to "no OS
  patching/package installation" in Scope above: these are direct,
  load-bearing dependencies of this role's own tasks, not general system
  package management, so `tasks/install.yml` updates the apt cache and
  installs `sendy_install_packages` before extracting. Same package
  names on both Debian and Ubuntu, so no `vars/<OsFamily>.yml` split is
  needed. The molecule test images already ship all three packages
  preinstalled, which is why this gap wasn't caught until a real host
  run.
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
* **The `sendy-X.Y.Z.zip` filename pattern is inferred from one example**
  (`sendy-7.0.6.zip`), not verified across multiple HelloSendy releases
  or download methods. If a future release ever ships under a different
  naming scheme (build metadata, an underscore instead of a hyphen, a
  suffix like `-full`), `tasks/preflight.yml`'s version-parsing regex
  will need updating — it currently just searches for the first
  `X.Y.Z` numeric substring in the basename.

## Consumer side notes

<!-- TODO: fill in consumer notes -->
