"""Database creation tests for the sendy_install Molecule scenario.

Verifies tasks/database.yml actually created the Sendy database and
user against the MariaDB server converge.yml's pre_tasks install
(simulating the "server already provisioned" assumption this role
makes) -- schema/table import remains out of scope and is not tested
here. The DB user's password is a fixed test-only value, never a real
secret, so it's fine to reference directly rather than masking output.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._data import DB_HOST, DB_NAME, DB_PASSWORD, DB_USERNAME

if TYPE_CHECKING:
    from testinfra.host import Host


def test_database_exists(host: Host) -> None:
    cmd = host.run(f"mysql -N -e \"SHOW DATABASES LIKE '{DB_NAME}'\"")
    assert cmd.rc == 0
    assert DB_NAME in cmd.stdout


def test_database_user_can_connect_and_has_privileges(host: Host) -> None:
    cmd = host.run(f"mysql -u {DB_USERNAME} -p{DB_PASSWORD} -h {DB_HOST} {DB_NAME} -e 'SELECT 1'")
    assert cmd.rc == 0
