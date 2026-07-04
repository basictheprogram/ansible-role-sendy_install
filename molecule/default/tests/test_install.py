"""Install-layout tests for the sendy_install Molecule scenario.

Checks that the extracted Sendy tree landed in the right place with the
right ownership, that the runtime-writable directories got their
group-writable mode, and that the staging directory was cleaned up.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ._data import EXPECTED_FILES, INSTALL_DIR, WEB_GROUP, WEB_USER, WRITABLE_DIRS

if TYPE_CHECKING:
    from testinfra.host import Host


@pytest.mark.parametrize("relative_path", EXPECTED_FILES)
def test_expected_file_exists(host: Host, relative_path: str) -> None:
    f = host.file(f"{INSTALL_DIR}/{relative_path}")
    assert f.exists
    assert f.is_file


@pytest.mark.parametrize("relative_path", EXPECTED_FILES)
def test_expected_file_owner(host: Host, relative_path: str) -> None:
    f = host.file(f"{INSTALL_DIR}/{relative_path}")
    assert f.user == WEB_USER
    assert f.group == WEB_GROUP


@pytest.mark.parametrize("writable_dir", WRITABLE_DIRS)
def test_writable_dir_exists(host: Host, writable_dir: str) -> None:
    d = host.file(f"{INSTALL_DIR}/{writable_dir}")
    assert d.exists
    assert d.is_directory


@pytest.mark.parametrize("writable_dir", WRITABLE_DIRS)
def test_writable_dir_mode(host: Host, writable_dir: str) -> None:
    d = host.file(f"{INSTALL_DIR}/{writable_dir}")
    assert oct(d.mode) == "0o775"


def test_staging_directory_removed(host: Host) -> None:
    # This is the actual staging path converge.yml sets via
    # sendy_install_staging_dir, not an insecure temp-file pattern.
    staging = host.file("/tmp/sendy_install")  # noqa: S108
    assert not staging.exists
