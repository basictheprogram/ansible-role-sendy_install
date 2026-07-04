"""config.php tests for the sendy_install Molecule scenario.

Each rendered value gets its own single-purpose test function -- never
combine an existence/permission check and a content check in one test.
Secret values (DB password) are checked for presence of the variable
assignment only, never for their actual value, so nothing sensitive ends
up in test output or a failure traceback.

Field names verified 2026-07-04 against a real production
includes/config.php (Sendy 7.0.6) -- see templates/config.php.j2.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._data import APP_PATH, COOKIE_DOMAIN, DB_CHARSET, DB_HOST, DB_NAME, DB_USERNAME, INSTALL_DIR, WEB_GROUP, WEB_USER

if TYPE_CHECKING:
    from testinfra.host import Host

CONFIG_PATH: str = f"{INSTALL_DIR}/includes/config.php"


def test_config_file_exists(host: Host) -> None:
    f = host.file(CONFIG_PATH)
    assert f.exists
    assert f.is_file


def test_config_file_mode(host: Host) -> None:
    f = host.file(CONFIG_PATH)
    assert oct(f.mode) == "0o640"


def test_config_file_owner(host: Host) -> None:
    f = host.file(CONFIG_PATH)
    assert f.user == WEB_USER
    assert f.group == WEB_GROUP


def test_config_contains_app_path(host: Host) -> None:
    content = host.file(CONFIG_PATH).content_string
    assert f"define('APP_PATH', '{APP_PATH}')" in content


def test_config_contains_db_host(host: Host) -> None:
    content = host.file(CONFIG_PATH).content_string
    assert f"$dbHost = '{DB_HOST}'" in content


def test_config_contains_db_name(host: Host) -> None:
    content = host.file(CONFIG_PATH).content_string
    assert f"$dbName = '{DB_NAME}'" in content


def test_config_contains_db_username(host: Host) -> None:
    content = host.file(CONFIG_PATH).content_string
    assert f"$dbUser = '{DB_USERNAME}'" in content


def test_config_contains_db_charset(host: Host) -> None:
    content = host.file(CONFIG_PATH).content_string
    assert f"$charset = '{DB_CHARSET}'" in content


def test_config_contains_cookie_domain(host: Host) -> None:
    content = host.file(CONFIG_PATH).content_string
    assert f"define('COOKIE_DOMAIN', '{COOKIE_DOMAIN}')" in content


def test_config_defines_db_password_variable(host: Host) -> None:
    content = host.file(CONFIG_PATH).content_string
    assert "$dbPass = " in content
