"""config.php tests for the sendy_install Molecule scenario.

Each rendered value gets its own single-purpose test function -- never
combine an existence/permission check and a content check in one test.
Secret values (DB password, encryption key) are checked for presence of
the constant only, never for their actual value, so nothing sensitive
ends up in test output or a failure traceback.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._data import DB_HOST, DB_NAME, DB_USERNAME, INSTALL_DIR, INSTALL_URL, TIMEZONE, WEB_GROUP, WEB_USER

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


def test_config_contains_db_host(host: Host) -> None:
    content = host.file(CONFIG_PATH).content_string
    assert f"define('HOST', '{DB_HOST}')" in content


def test_config_contains_db_name(host: Host) -> None:
    content = host.file(CONFIG_PATH).content_string
    assert f"define('DB_NAME', '{DB_NAME}')" in content


def test_config_contains_db_username(host: Host) -> None:
    content = host.file(CONFIG_PATH).content_string
    assert f"define('DB_USERNAME', '{DB_USERNAME}')" in content


def test_config_contains_install_url(host: Host) -> None:
    content = host.file(CONFIG_PATH).content_string
    assert f"define('INSTALL_URL', '{INSTALL_URL}')" in content


def test_config_contains_timezone(host: Host) -> None:
    content = host.file(CONFIG_PATH).content_string
    assert f"define('TIMEZONE', '{TIMEZONE}')" in content


def test_config_defines_db_password_constant(host: Host) -> None:
    content = host.file(CONFIG_PATH).content_string
    assert "define('DB_PASSWORD'," in content


def test_config_defines_encryption_key_constant(host: Host) -> None:
    content = host.file(CONFIG_PATH).content_string
    assert "define('ENCRYPTION_KEY'," in content
