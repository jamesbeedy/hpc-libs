# Copyright 2024 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Detect if machine is a container instance.

Even though Juju supports using LXD containers as the backing cloud for
deploying charmed operators, not all HPC applications work within system containers,
and some need additional configuration. This simple charm library provides the `is_container`
function, a simple, deterministic way to identify if the charm is deployed into
a system container using `systemd-detect-virt`.

Exit code 0 means that the charm is running with a container. A non-zero exit code
means that the charm is not running within a container.

### Example Usage:

```python3
from charms.hpc_libs.v0.is_container import is_container

class ApplicationCharm(CharmBase):

    def __init__(self, *args):
        super().__init__(*args)

        self.framework.observe(self.on.install, self._on_install)

    def _on_install(self, _: InstallEvent) -> None:
        if is_container():
            self.unit.status = BlockedStatus("app does not support container runtime")

        # Proceed with installation.
        ...
```
"""

import shutil
import subprocess

# The unique Charmhub library identifier, never change it
LIBID = "eb95ad73da1941c0af186ee670f96507"

# Increment this major API version when introducing breaking changes
LIBAPI = 0

# Increment this PATCH version before using `charmcraft publish-lib` or reset
# to 0 if you are raising the major API version
LIBPATCH = 1


class DetectVirtNotFoundError(Exception):
    """Raise error if `systemd-detect-virt` executable is not found on machine."""

    @property
    def message(self) -> str:
        """Return message passed as argument to exception."""
        return self.args[0]


def is_container() -> bool:
    """Detect if the machine is a container instance.

    Raises:
        DetectVirtNotFoundError: Raised if `systemd-detect-virt` is not found on machine.
    """
    if shutil.which("systemd-detect-virt") is None:
        raise DetectVirtNotFoundError(
            (
                "executable `systemd-detect-virt` not found. "
                + "cannot determine if machine is a container instance"
            )
        )

    result = subprocess.run(["systemd-detect-virt", "--container"])
    return result.returncode == 0