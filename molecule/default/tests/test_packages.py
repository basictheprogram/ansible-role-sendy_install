"""Package installation tests for the sendy_install Molecule scenario.

sendy_install installs the same package(s) regardless of OS family (see
PACKAGES in _data.py), unlike the packaged skeleton this file is based
on, so there's no per-family branching here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ._data import PACKAGES

if TYPE_CHECKING:
    from testinfra.host import Host


@pytest.mark.parametrize("package_name", PACKAGES)
def test_expected_package_installed(host: Host, package_name: str) -> None:
    assert host.package(package_name).is_installed
