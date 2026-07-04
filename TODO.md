# TODO — ansible-role-sendy_install

Flagged-but-unresolved items from the initial scaffold of this role
(2026-07-03). This role was built from scratch — the directory was
completely empty before this session — so treat these as first-run
follow-ups, not regressions.

## Needs manual action

### `.pre-commit-config.yaml` — resolved 2026-07-04 (applied by hand)

Cowork couldn't write this file itself ("resolves to a protected
location" — a known, recurring issue, see this repo's `ansible-sync-role`
skill `references/known-issues.md`), so Bob copied it in manually. The
applied file matches the version proposed here functionally (the
`jumanjihouse/pre-commit-hooks` block just has more of its unused hooks
listed as comments) — no further action needed.

### Git repository — resolved 2026-07-04

`git init` and `origin` (`git@github.com:basictheprogram/ansible-role-sendy_install.git`)
are done — the role now has its own history on branch `ansible-core-2.20`
with one commit. This also resolves `meta/main.yml`'s `issue_tracker_url`
placeholder, which pointed at this same URL — it's no longer a
placeholder as long as the GitHub repo itself exists at that path (this
session's sandbox has no network access to GitHub to confirm that
directly).

Still unconfirmed from inside this role's directory (out of scope for
what's mounted in this session — verify from the `ansible-playbooks`
superproject):

1. The `roles/realtime.sendy_install -> git_repository/ansible-role-sendy_install`
   symlink from the superproject's roles root, matching the
   `realtime.sendy -> git_repository/ansible-role-sendy` pattern.
2. Registration wherever new roles get declared for this project
   (`.gitmodules`, `requirements.yml`, or another mechanism).

## Needs verification before production use

### `templates/config.php.j2` field names — resolved 2026-07-04

Verified against a real production `includes/config.php` (Sendy 7.0.6)
after a live run hit `Undefined constant "APP_PATH"`. The template,
`defaults/main.yml`, `meta/argument_specs.yml`, and `tasks/preflight.yml`
were all fixed to match — see `DESIGN.md`'s Settled decisions section
for the full list of changes, including the removal of
`sendy_install_timezone` and `sendy_install_encryption_key` (neither
exists in real Sendy config.php) and the addition of
`sendy_install_db_charset` / `sendy_install_cookie_domain`. This was a
breaking change to the role's public interface.

### `sendy_install_cron_jobs` may not cover every required cron script

The default only includes the send-queue processor
(`cron/campaigns.php`), which is the one job every Sendy install guide
documents. Some versions document additional scripts (e.g. an
API-triggered blast processor) — check your specific Sendy version's
documentation and add entries if it lists more.

### Molecule scenario has not actually been run

This session's sandbox has Python 3.10 (ansible-core 2.20+ requires
3.12) and no network access to Ansible Galaxy, so `molecule test` could
not be executed here. What was verified in this session:

* Every YAML file parses cleanly (`yaml.safe_load_all`).
* `ansible-playbook --syntax-check` against a throwaway playbook loading
  this role passed cleanly under ansible-core 2.17.14 (an older version
  than this role targets, since 2.20+ isn't installable under Python
  3.10 — treat this as a structural smoke check, not full validation).
* `ansible.posix` and `community.general` module resolution could not be
  checked (no Galaxy network access in this sandbox to install them).

Run `molecule test` for real (with `ansible-core >= 2.20`, Python 3.12,
and both collections installed) before trusting this role in production.

### Ubuntu 26.04 (resolute) is very new

It's the current Ubuntu release as of 2026-07-03. If the geerlingguy
image or molecule testing proves unreliable for it, ask before dropping
it from the platform matrix rather than assuming it should go.

## Explicitly out of scope (by design, not an oversight)

* This role never creates the Sendy database, user, or imports its
  schema — that must happen before this role runs. See `DESIGN.md`'s
  Settled decisions.
* This role never installs or configures the web server, PHP, or
  MySQL/MariaDB.
* This role never restarts anything — it has no handlers, since nothing
  in its own tasks currently requires one.
