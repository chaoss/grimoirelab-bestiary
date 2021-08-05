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

import logging

import django_rq
import django_rq.utils

from .errors import NotFoundError

logger = logging.getLogger(__name__)


def find_job(job_id):
    """Find a job in the jobs registry.
    Search for a job using its identifier. When the job is
    not found, a `NotFoundError` exception is raised.
    :param job_id: job identifier
    :returns: a Job instance
    :raises NotFoundError: when the job identified by `job_id`
        is not found.
    """
    logger.debug(f"Finding job {job_id} ...")

    queue = django_rq.get_queue()
    jobs = django_rq.utils.get_jobs(queue, [job_id])

    if not jobs:
        logger.debug(f"Job with id {job_id} does not exist")
        raise NotFoundError(entity=job_id)

    logger.debug(f"Job with id {job_id} was found")

    return jobs[0]


def get_jobs():
    """Get a list of all jobs
    This function returns a list of all jobs found in the main queue and its
    registries, sorted by date.
    :returns: a list of Job instances
    """
    logger.debug("Retrieving list of jobs ...")

    queue = django_rq.get_queue()
    started_jobs = [find_job(id)
                    for id
                    in queue.started_job_registry.get_job_ids()]
    deferred_jobs = [find_job(id)
                     for id
                     in queue.deferred_job_registry.get_job_ids()]
    finished_jobs = [find_job(id)
                     for id
                     in queue.finished_job_registry.get_job_ids()]
    failed_jobs = [find_job(id)
                   for id
                   in queue.failed_job_registry.get_job_ids()]
    scheduled_jobs = [find_job(id)
                      for id
                      in queue.scheduled_job_registry.get_job_ids()]
    jobs = (queue.jobs + started_jobs + deferred_jobs + finished_jobs + failed_jobs + scheduled_jobs)

    sorted_jobs = sorted(jobs, key=lambda x: x.enqueued_at)

    logger.debug(f"List of jobs retrieved; total jobs: {len(sorted_jobs)};")

    return sorted_jobs
