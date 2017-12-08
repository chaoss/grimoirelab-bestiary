# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2017 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#     Alvaro del Castillo <acs@bitergia.com>
#

import logging
import subprocess
import time

from .fetcher import Fetcher


logger = logging.getLogger(__name__)


class GerritFetcher(Fetcher):
    """Fetch gerrit projects"""

    CMD = 'gerrit'
    CMD_LS_PROJECTS = 'ls-projects'
    PORT = '29418'
    MAX_RETRIES = 3  # max number of retries when a command fails
    RETRY_WAIT = 10  # number of seconds when retrying a ssh command

    def __init__(self, host, user):
        super().__init__(host, user=user)

    def fetch(self):
        """ Get the repository list for a data sources for all projects """

        cmd = self._build_cmd(self.CMD_LS_PROJECTS)
        stdout = self._execute_cmd(cmd)
        return stdout

    def _build_cmd(self, subcmd=None):
        """Buld gerrit command"""

        credentials = self.user + "@" + self.host
        cmd = ['ssh', '-p', self.PORT, credentials, self.CMD]

        if subcmd:
            cmd.append(subcmd)
        return cmd

    def _execute_cmd(self, cmd):
        """Execute gerrit command with retry if it fails"""

        stdout = None
        retries = 0

        while retries < self.MAX_RETRIES:
            try:
                stdout = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                break
            except subprocess.CalledProcessError as ex:
                logger.error("gerrit cmd %s failed: %s", cmd, ex)
                time.sleep(self.RETRY_WAIT * retries)
                retries += 1

        if stdout is None:
            raise RuntimeError(' '.join(cmd) + " failed " +
                               str(self.MAX_RETRIES) + " times. Giving up!")

        return stdout.decode("utf8")
