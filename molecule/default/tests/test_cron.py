"""Cron job tests for the sendy_install Molecule scenario."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._data import CRON_COMMAND_FRAGMENT, WEB_USER

if TYPE_CHECKING:
    from testinfra.host import Host


def test_send_queue_cron_job_present(host: Host) -> None:
    crontab = host.check_output(f"crontab -u {WEB_USER} -l")
    assert CRON_COMMAND_FRAGMENT in crontab
