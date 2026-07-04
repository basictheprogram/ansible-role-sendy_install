"""Shared test constants for the sendy_install Molecule scenario.

sendy_install has no OS-varying config directory -- both Debian and
Ubuntu use the same install path -- so there is no CONFIG_DIR_BY_FAMILY
split here, unlike the packaged skeletons this file is based on. It does
now install packages directly (see PACKAGES below), the same names on
both families, so there's no DEBIAN_PACKAGES / REDHAT_PACKAGES split
either.
"""

from __future__ import annotations

INSTALL_DIR: str = "/var/www/html/sendy"
WEB_USER: str = "www-data"
WEB_GROUP: str = "www-data"

# Packages this role installs directly (both Debian and Ubuntu use the
# same package name).
PACKAGES: list[str] = ["unzip", "rsync", "cron"]

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
APP_PATH: str = "https://sendy.example.com"
DB_HOST: str = "127.0.0.1"
DB_NAME: str = "sendy_test"
DB_USERNAME: str = "sendy_test"
# Not overridden in converge.yml -- role defaults apply.
DB_CHARSET: str = "utf8mb4"
COOKIE_DOMAIN: str = ""

# Fragment that must appear in the managed cron job's command line.
CRON_COMMAND_FRAGMENT: str = "cron/campaigns.php"

# converge.yml points sendy_install_zip_src at /tmp/sendy-9.9.9.zip --
# preflight must parse "9.9.9" from that filename and record it here
# after a successful install.
VERSION_MARKER_PATH: str = "/var/lib/sendy_install/version"
EXPECTED_VERSION: str = "9.9.9"
