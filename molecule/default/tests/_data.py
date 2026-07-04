"""Shared test constants for the sendy_install Molecule scenario.

sendy_install has no OS-varying config directory or package list -- both
Debian and Ubuntu use the same install path and this role installs no
packages itself -- so there is no CONFIG_DIR_BY_FAMILY / DEBIAN_PACKAGES
/ REDHAT_PACKAGES split here, unlike the packaged skeletons this file is
based on.
"""

from __future__ import annotations

INSTALL_DIR: str = "/var/www/html/sendy"
WEB_USER: str = "www-data"
WEB_GROUP: str = "www-data"

# Files that must exist under INSTALL_DIR after a successful install.
EXPECTED_FILES: list[str] = [
    "index.php",
    "includes/config.php",
    "cron/campaigns.php",
]

# Subdirectories that must be group-writable after install.
WRITABLE_DIRS: list[str] = ["uploads"]

# Values molecule/default/converge.yml passes to the role -- config.php's
# rendered content must reflect these.
INSTALL_URL: str = "https://sendy.example.com"
TIMEZONE: str = "America/Chicago"
DB_HOST: str = "127.0.0.1"
DB_NAME: str = "sendy_test"
DB_USERNAME: str = "sendy_test"

# Fragment that must appear in the managed cron job's command line.
CRON_COMMAND_FRAGMENT: str = "cron/campaigns.php"
