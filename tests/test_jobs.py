# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2021 Bitergia
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
#     Jose Javier Merchante <jjmerchante@cauldron.io>
#

from unittest import TestCase

from django_rq import enqueue

from bestiary.core.errors import NotFoundError
from bestiary.core.jobs import find_job


JOB_NOT_FOUND_ERROR = "DEF not found in the registry"


def job_echo(s):
    """Function to test job queuing"""
    return s


class TestFindJob(TestCase):
    """Unit tests for find_job"""

    def test_find_job(self):
        """Check if it finds a job in the registry"""

        job = enqueue(job_echo, 'ABC')
        qjob = find_job(job.id)
        self.assertEqual(qjob, job)

    def test_not_found_job(self):
        """Check if it raises an exception when the job is not found"""

        enqueue(job_echo, 'ABC')

        with self.assertRaisesRegex(NotFoundError,
                                    JOB_NOT_FOUND_ERROR):
            find_job('DEF')
