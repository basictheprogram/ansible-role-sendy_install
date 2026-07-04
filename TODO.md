# TODO — ansible-role-sendy_install

Flagged-but-unresolved items from the initial scaffold of this role
(2026-07-03). This role was built from scratch — the directory was
completely empty before this session — so treat these as first-run
follow-ups, not regressions.

## Needs manual action

### `.pre-commit-config.yaml` could not be written

Cowork blocked writing this file with "resolves to a protected
location" (a known, recurring issue — see this repo's
`ansible-sync-role` skill `references/known-issues.md`). Apply this
file by hand:

```yaml
---
default_stages: [pre-commit]

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ["--maxkb=600"]
      - id: detect-private-key
      - id: check-shebang-scripts-are-executable
      - id: file-contents-sorter
        files: requirements.txt|\.gitignore|\.dockerignore

  - repo: https://github.com/adrienverge/yamllint.git
    rev: v1.38.0
    hooks:
      - id: yamllint
        files: \.(yaml|yml)$
        types: [file, yaml]
        entry: yamllint --strict -f parsable

  - repo: https://github.com/zricethezav/gitleaks
    rev: v8.30.0
    hooks:
      - id: gitleaks

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.16
    hooks:
      - id: ruff
        name: Ruff check
        description: "Run 'ruff check' for extremely fast Python linting"
        args: [--fix]

      - id: ruff-format
        name: Ruff format
        description: "Run 'ruff format' for extremely fast Python formatting"

  - repo: https://github.com/hadolint/hadolint
    rev: v2.14.0
    hooks:
      - id: hadolint
        name: Lint Dockerfiles
        description: Runs hadolint to lint Dockerfiles
        language: system
        types: ["dockerfile"]
        entry: hadolint

  - repo: local
    hooks:
      - id: ansible-lint
        name: Ansible Lint
        language: system
        entry: ansible-lint
        files: \.(yaml|yml)$
        pass_filenames: false

  - repo: https://github.com/jumanjihouse/pre-commit-hooks
    rev: 3.0.0
    hooks:
      - id: shellcheck
      - id: shfmt

ci:
  autoupdate_schedule: weekly
```

### No git repository yet

Unlike its sibling roles under `roles/git_repository/`, this directory
has no `.git` of its own — it's untracked content inside the
`ansible-playbooks` superproject's working tree. To match the project
convention:

1. `git init` this directory as its own repository.
2. Create the actual GitHub (or GitLab) repo and add it as `origin`.
3. Add a `roles/realtime.sendy_install -> git_repository/ansible-role-sendy_install`
   symlink from the `ansible-playbooks` roles root, matching the
   `realtime.sendy -> git_repository/ansible-role-sendy` pattern.
4. Register it wherever new roles get declared for this project (checked
   `.gitmodules` and `requirements.yml` — neither currently reference
   this role name; there may be another mechanism not found in this
   session).

### `meta/main.yml`'s `issue_tracker_url` is a placeholder

Set to `https://github.com/basictheprogram/ansible-role-sendy_install/issues`,
following the sibling `realtime.sendy` role's naming convention on
GitHub — but that repository does not actually exist yet (see above).
Fix this URL once the real repo is created, if it ends up somewhere else.

## Needs verification before production use

### `templates/config.php.j2` field names are unverified

Sendy is closed-source. This template was written from public/community
knowledge of `includes/config.php`'s constants (`HOST`, `DB_PORT`,
`DB_USERNAME`, `DB_PASSWORD`, `DB_NAME`, `INSTALL_URL`, `TIMEZONE`,
`ENCRYPTION_KEY`). Compare it against the actual `includes/config.php`
(or a `config.php.example`, if one ships) inside a real licensed Sendy
zip before the first production run, and fix the template if a constant
name differs by version.

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
