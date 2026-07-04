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

## Open questions

If a task touches one of these, leave a `# TODO(open-q):` comment:

* **config.php field names are unverified against a real Sendy zip.**
  `templates/config.php.j2` was written from public/community knowledge
  of Sendy's `includes/config.php` format (HOST, DB_PORT, DB_USERNAME,
  DB_PASSWORD, DB_NAME, INSTALL_URL, TIMEZONE, ENCRYPTION_KEY). Sendy is
  closed-source — compare this template against the actual
  `includes/config.php` (or a `config.php.example`, if one ships) inside
  a real licensed Sendy zip before the first production run, and update
  the template if any constant name differs.
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

## Consumer side notes

<!-- TODO: fill in consumer notes -->
