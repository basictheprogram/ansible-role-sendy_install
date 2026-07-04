# ansible-role-sendy_install

[![Ansible Galaxy](https://img.shields.io/badge/ansible--galaxy-sendy__install-blue.svg?style=popout-square)](https://galaxy.ansible.com/realtime/sendy_install)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Ansible role that performs a **first-time install** of
[Sendy](https://sendy.co), a self-hosted email newsletter application,
on a Linux host. It extracts a purchased Sendy release zip, writes
`includes/config.php`, sets ownership/permissions, and wires up the
send-queue cron job.

This role installs only — it does not upgrade an existing install. See
the sibling [`realtime.sendy`](../ansible-role-sendy) role for upgrades.

**Out of scope** (provision these separately, with their own roles,
before running this one):

* The web server (Apache/nginx) and its vhost
* PHP and its extensions
* The MySQL/MariaDB server, database, user, and Sendy's schema —
  this role only writes DB *connection details* into `config.php`; it
  never creates a database, user, or table.

---

## Requirements

* Ansible core ≥ 2.20 (`pip install ansible`)
* `ansible.posix` collection — `ansible-galaxy collection install ansible.posix`
  (declared in `requirements.yml`; install with
  `ansible-galaxy collection install -r requirements.yml`)
* A purchased Sendy release zip staged on the Ansible control node
* A web server, PHP, and MySQL/MariaDB already provisioned on the target,
  with Sendy's database and schema already created

### Supported platforms

| OS family | Versions |
|---|---|
| Debian | bookworm (12), trixie (13) |
| Ubuntu | jammy (22.04), noble (24.04), resolute (26.04) |

---

## Getting the Sendy zip onto the control node

Sendy is commercial software with no public download URL. Download the
zip from your Sendy account, copy it from a NAS share, or use any method
that places it at the path you set in `sendy_install_zip_src`.

```bash
# Confirm the zip is present
ls /mnt/sendy_releases/
```

---

## Role Variables

All variables can be overridden in `host_vars`, `group_vars`, or with `-e`.
Full descriptions and types are also documented in `meta/argument_specs.yml`.

| Variable | Default | Description |
|---|---|---|
| `sendy_install_dir` | `/var/www/html/sendy` | Live Sendy web root on the remote host |
| `sendy_install_staging_dir` | `/tmp/sendy_install` | Temp dir on remote for extraction |
| `sendy_install_web_user` | `www-data` | Web server process user |
| `sendy_install_web_group` | `www-data` | Web server process group |
| `sendy_install_dir_mode` | `"0755"` | Mode for directories this role creates directly |
| `sendy_install_writable_dirs` | `[uploads]` | Subdirs needing group-writable permissions |
| `sendy_install_writable_dir_mode` | `"0775"` | Mode applied to `sendy_install_writable_dirs` |
| `sendy_install_zip_src` | `""` | **Required.** Path to zip on Ansible control node |
| `sendy_install_url` | `""` | **Required.** Public URL Sendy is served from |
| `sendy_install_timezone` | `UTC` | PHP timezone written into `config.php` |
| `sendy_install_encryption_key` | `""` | **Required.** 32-character key written into `config.php` |
| `sendy_install_db_host` | `127.0.0.1` | Pre-provisioned database host |
| `sendy_install_db_port` | `3306` | Pre-provisioned database port |
| `sendy_install_db_name` | `sendy` | Pre-provisioned database name |
| `sendy_install_db_username` | `sendy` | Pre-provisioned database user |
| `sendy_install_db_password` | `""` | **Required.** Pre-provisioned database password. Never logged |
| `sendy_install_manage_cron` | `true` | Whether this role manages Sendy's cron jobs |
| `sendy_install_cron_user` | `{{ sendy_install_web_user }}` | User the cron jobs run as |
| `sendy_install_cron_jobs` | see `defaults/main.yml` | Cron job entries passed to `ansible.builtin.cron` |

This role has no OS-specific overrides in `vars/` — Debian and Ubuntu use
the same web user and this role installs no packages itself.

---

## Task Flow

1. **Preflight** (`tasks/preflight.yml`) — asserts ansible-core version,
   supported OS family, all required variables are set, the encryption
   key is exactly 32 characters, the zip exists on the control node, and
   that Sendy is *not* already installed at the target directory.
2. **Load OS-specific variables** — `include_vars` with `first_found`
   against `vars/` (currently a no-op; see above).
3. **Install** (`tasks/install.yml`) — uploads and extracts the zip to a
   staging directory, writes `includes/config.php`, syncs the result into
   `sendy_install_dir`, sets permissions on writable directories and
   `config.php`, then removes the staging directory.
4. **Cron** (`tasks/cron.yml`) — creates the send-queue cron job(s).

---

## Usage

Set the required host-specific variables in `host_vars/<hostname>.yml`:

```yaml
sendy_install_zip_src: /mnt/sendy_releases/sendy.zip
sendy_install_url: https://sendy.example.com
sendy_install_db_password: "{{ vault_sendy_db_password }}"
sendy_install_encryption_key: "{{ vault_sendy_encryption_key }}"
```

Then run:

```bash
# Install required collection
ansible-galaxy collection install -r requirements.yml

# Dry-run first (no changes made)
ansible-playbook install_sendy.yml --check --diff

# Run for real
ansible-playbook install_sendy.yml
```

### Limit to specific tasks with tags

```bash
# Preflight only
ansible-playbook install_sendy.yml --tags sendy_install_preflight

# Install only (skips preflight — use with caution)
ansible-playbook install_sendy.yml --tags sendy_install_install

# Cron only
ansible-playbook install_sendy.yml --tags sendy_install_cron
```

---

## Linting

```bash
# Full lint + format pass before every commit
pre-commit run --all-files
```

---

## License

[MIT](LICENSE) — Copyright (c) 2026 Bob Tanner
