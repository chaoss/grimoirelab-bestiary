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
import os
from django.test import TestCase

import httpretty
from django.contrib.auth import get_user_model
from django_rq import enqueue
from grimoirelab_toolkit.datetime import datetime_utcnow

from bestiary.core.context import BestiaryContext
from bestiary.core.errors import NotFoundError
from bestiary.core.jobs import (find_job,
                                fetch_github_owner_repos, fetch_gitlab_owner_repos)
from bestiary.core.models import Transaction

from tests.retrieval.test_github import GITHUB_REPOS_URL
from tests.retrieval.test_gitlab import (GITLAB_USER_REPOS_URL,
                                         GITLAB_USER_URL,
                                         GITLAB_API_URL)

JOB_NOT_FOUND_ERROR = "DEF not found in the registry"


def read_file(filename, mode='r'):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), mode) as f:
        content = f.read()
    return content


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


class TestGitHubOwnerReposJob(TestCase):
    """Unit tests for fetch_github_owner_repos job"""

    def setUp(self):
        user = get_user_model().objects.create(username='test')
        self.ctx = BestiaryContext(user)

    @httpretty.activate
    def test_fetch_owner_repos(self):
        """Check if the job for fetching owner repositories is executed correctly."""

        repos = read_file('data/github_repos_issues.json')

        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPOS_URL,
                               body=repos,
                               status=200)
        expected = {
            'errors': [],
            'results': [{'fork': False,
                         'has_issues': False,
                         'url': 'https://github.com/chaoss_example/eagle'},
                        {'fork': False,
                         'has_issues': True,
                         'url': 'https://github.com/chaoss_example/echarts'}]
        }

        job = fetch_github_owner_repos.delay(self.ctx, 'chaoss_example')

        self.assertDictEqual(job.result, expected)

    @httpretty.activate
    def test_fetch_owner_repos_token(self):
        """Check if the job for fetching owner repositories is executed when using api_token."""

        repos = read_file('data/github_repos_issues.json')

        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPOS_URL,
                               body=repos,
                               status=200)
        expected = {
            'errors': [],
            'results': [{'fork': False,
                         'has_issues': False,
                         'url': 'https://github.com/chaoss_example/eagle'},
                        {'fork': False,
                         'has_issues': True,
                         'url': 'https://github.com/chaoss_example/echarts'}]
        }

        job = fetch_github_owner_repos.delay(self.ctx, owner='chaoss_example', api_token='aaaa')

        self.assertDictEqual(job.result, expected)
        self.assertEqual(httpretty.last_request().headers["Authorization"], "token aaaa")

    @httpretty.activate
    def test_not_found_owner(self):
        """Check if the job for fetching owner repositories returns a not found user."""

        body = str({
            "message": "Not Found",
            "documentation_url": "https://docs.github.com/rest/reference/repos#list-repositories-for-a-user"
        })
        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPOS_URL,
                               body=body,
                               status=404)
        expected = {'errors': ['404 Client Error: Not Found for url: '
                               'https://api.github.com/users/chaoss_example/repos'],
                    'results': []}
        job = fetch_github_owner_repos.delay(self.ctx, 'chaoss_example')
        self.assertDictEqual(job.result, expected)

    @httpretty.activate
    def test_server_error(self):
        """Check if the job for fetching owner repositories returns a server error."""

        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPOS_URL,
                               body='',
                               status=500)
        expected = {'results': [],
                    'errors': ['500 Server Error: Internal Server Error for url: '
                               'https://api.github.com/users/chaoss_example/repos']}
        job = fetch_github_owner_repos.delay(self.ctx, 'chaoss_example')
        self.assertDictEqual(job.result, expected)

    @httpretty.activate
    def test_transactions(self):
        """Check if the right transactions were created"""

        timestamp = datetime_utcnow()

        repos = read_file('data/github_repos_issues.json')
        httpretty.register_uri(httpretty.GET,
                               GITHUB_REPOS_URL,
                               body=repos,
                               status=200)
        fetch_github_owner_repos.delay(self.ctx, owner='chaoss_example', job_id='1234-5678-90AB-CDEF')

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertIsInstance(trx, Transaction)
        self.assertEqual(trx.name, 'fetch_github_owner_repos-1234-5678-90AB-CDEF')
        self.assertGreater(trx.created_at, timestamp)
        self.assertEqual(trx.authored_by, self.ctx.user.username)


class TestGitLabOwnerReposJob(TestCase):
    """Unit tests for fetch_gitlab_owner_repos job"""

    def setUp(self):
        user = get_user_model().objects.create(username='test')
        self.ctx = BestiaryContext(user)

    @httpretty.activate
    def test_fetch_owner_repos(self):
        """Check if the job for fetching owner repositories is executed correctly."""

        body_user = read_file('data/gitlab_user.json')
        body_repos = read_file('data/gitlab_user_repos_1.json')

        httpretty.register_uri(httpretty.GET,
                               GITLAB_USER_URL,
                               body=body_user,
                               status=200)
        httpretty.register_uri(httpretty.GET,
                               GITLAB_USER_REPOS_URL,
                               body=body_repos,
                               status=200)

        expected = {
            'errors': [],
            'results': [{'fork': True,
                         'has_issues': True,
                         'url': 'https://gitlab.com/user_example/project-1'},
                        {'fork': False,
                         'has_issues': False,
                         'url': 'https://gitlab.com/user_example/project-2'},
                        {'fork': False,
                         'has_issues': True,
                         'url': 'https://gitlab.com/user_example/project-3'}]
        }

        job = fetch_gitlab_owner_repos.delay(self.ctx, owner='user_example', api_token='aaaa')

        self.assertDictEqual(job.result, expected)
        self.assertEqual(httpretty.last_request().headers["Authorization"], "Bearer aaaa")

    @httpretty.activate
    def test_not_found_owner(self):
        """Check if the job for fetching owner repositories returns a not found error."""

        user_unknown = 'user_unknown'
        user_unknown_url = "{}/users?username={}".format(GITLAB_API_URL, user_unknown)
        group_unknown_url = "{}/groups/{}".format(GITLAB_API_URL, user_unknown)

        httpretty.register_uri(httpretty.GET,
                               user_unknown_url,
                               body="[]",
                               status=200)

        httpretty.register_uri(httpretty.GET,
                               group_unknown_url,
                               body=str({"message": "404 Group Not Found"}),
                               status=404)
        expected = {'errors': ['GitLab owner "user_unknown" not found'],
                    'results': []}
        job = fetch_gitlab_owner_repos.delay(self.ctx, 'user_unknown')
        self.assertDictEqual(job.result, expected)

    @httpretty.activate
    def test_transactions(self):
        """Check if the right transactions were created"""

        body_user = read_file('data/gitlab_user.json')
        body_repos = read_file('data/gitlab_user_repos_1.json')

        httpretty.register_uri(httpretty.GET,
                               GITLAB_USER_URL,
                               body=body_user,
                               status=200)
        httpretty.register_uri(httpretty.GET,
                               GITLAB_USER_REPOS_URL,
                               body=body_repos,
                               status=200)

        expected = {
            'errors': [],
            'results': [{'fork': True,
                         'has_issues': True,
                         'url': 'https://gitlab.com/user_example/project-1'},
                        {'fork': False,
                         'has_issues': False,
                         'url': 'https://gitlab.com/user_example/project-2'},
                        {'fork': False,
                         'has_issues': True,
                         'url': 'https://gitlab.com/user_example/project-3'}]
        }

        timestamp = datetime_utcnow()
        job = fetch_gitlab_owner_repos.delay(self.ctx, owner='user_example', job_id='1234-5678-90AB-CDEF')

        transactions = Transaction.objects.filter(created_at__gte=timestamp)
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertIsInstance(trx, Transaction)
        self.assertEqual(trx.name, 'fetch_gitlab_owner_repos-1234-5678-90AB-CDEF')
        self.assertGreater(trx.created_at, timestamp)
        self.assertEqual(trx.authored_by, self.ctx.user.username)
