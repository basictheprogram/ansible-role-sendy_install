"""Version-marker tests for the sendy_install Molecule scenario.

Verifies that preflight's parsed version was actually recorded, since
that's what the same-or-older guard on the next run reads back.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._data import EXPECTED_VERSION, VERSION_MARKER_PATH

if TYPE_CHECKING:
    from testinfra.host import Host


def test_version_marker_exists(host: Host) -> None:
    f = host.file(VERSION_MARKER_PATH)
    assert f.exists
    assert f.is_file


def test_version_marker_content(host: Host) -> None:
    content = host.file(VERSION_MARKER_PATH).content_string.strip()
    assert content == EXPECTED_VERSION
