# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2019 Bitergia
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
#     Jose Javier Merchante <jjmerchante@cauldron.io>
#

import os
import unittest

import httpretty
import requests

from bestiary.core.retrieval.gitlab import GitLab

GITLAB_API_URL = "https://gitlab.com/api/v4"

GITLAB_USER_NAME = "user_example"
GITLAB_USER_ID = 123456
GITLAB_USER_URL = "{}/users?username={}".format(GITLAB_API_URL, GITLAB_USER_NAME)
GITLAB_USER_REPOS_URL = "{}/users/{}/projects".format(GITLAB_API_URL, GITLAB_USER_ID)

GITLAB_GROUP_NAME = "group_example"
GITLAB_GROUP_ID = 654321
GITLAB_SUBGROUP_ID = 1234562
GITLAB_GROUP_URL = "{}/groups/{}".format(GITLAB_API_URL, GITLAB_GROUP_NAME)
GITLAB_GROUP_REPOS_URL = "{}/groups/{}/projects".format(GITLAB_API_URL, GITLAB_GROUP_ID)
GITLAB_SUBGROUPS_URL = "{}/groups/{}/subgroups".format(GITLAB_API_URL, GITLAB_GROUP_ID)
GITLAB_SUBGROUP_REPOS_URL = "{}/groups/{}/projects".format(GITLAB_API_URL, GITLAB_SUBGROUP_ID)
GITLAB_SUB_SUBGROUPS_URL = "{}/groups/{}/subgroups".format(GITLAB_API_URL, GITLAB_SUBGROUP_ID)

NAME_NOT_FOUND_ERROR = 'GitLab owner "user_unknown" not found'


def read_file(filename, mode='r'):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), mode) as f:
        content = f.read()
    return content


class TestGitLabOwnerRepos(unittest.TestCase):
    """Unit tests for fetching GitLab repositories"""

    @httpretty.activate
    def test_get_user_id(self):
        """Test whether a user_id is returned when there is an existing GitLab username"""

        body = read_file('../data/gitlab_user.json')

        httpretty.register_uri(httpretty.GET,
                               GITLAB_USER_URL,
                               body=body,
                               status=200)

        user_id = GitLab().user_id(GITLAB_USER_NAME)

        self.assertEqual(user_id, 123456)

    @httpretty.activate
    def test_wrong_user_id(self):
        """Test whether no user_id is returned when querying a not existing username"""

        httpretty.register_uri(httpretty.GET,
                               GITLAB_USER_URL,
                               body="[]",
                               status=200)

        user_id = GitLab().user_id(GITLAB_USER_NAME)

        self.assertIsNone(user_id)

    @httpretty.activate
    def test_get_group_id(self):
        """Test whether a group_id is returned when there is an existing group"""

        body = read_file('../data/gitlab_group.json')

        httpretty.register_uri(httpretty.GET,
                               GITLAB_GROUP_URL,
                               body=body,
                               status=200)

        group_id = GitLab().group_id(GITLAB_GROUP_NAME)

        self.assertEqual(group_id, 654321)

    @httpretty.activate
    def test_wrong_group_id(self):
        """Test whether no group_id is returned when querying a not existing group"""

        httpretty.register_uri(httpretty.GET,
                               GITLAB_GROUP_URL,
                               body=str({"message": "404 Group Not Found"}),
                               status=404)

        group_id = GitLab().group_id(GITLAB_GROUP_NAME)

        self.assertIsNone(group_id)

    @httpretty.activate
    def test_fetch_user_repositories(self):
        """Test whether it retrieves a list of repositories of a user"""

        body_repos_1 = read_file('../data/gitlab_user_repos_1.json')

        httpretty.register_uri(httpretty.GET,
                               GITLAB_USER_REPOS_URL,
                               body=body_repos_1,
                               status=200)

        repos_iter = GitLab().fetch_user_repositories(user_id=123456)
        repositories = list(repos_iter)

        repo = repositories[0]
        self.assertEqual(repo['url'], 'https://gitlab.com/user_example/project-1')
        self.assertEqual(repo['fork'], True)
        self.assertEqual(repo['has_issues'], True)

        repo = repositories[1]
        self.assertEqual(repo['url'], 'https://gitlab.com/user_example/project-2')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], False)

        repo = repositories[2]
        self.assertEqual(repo['url'], 'https://gitlab.com/user_example/project-3')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], True)

    @httpretty.activate
    def test_fetch_more_repos(self):
        """Test whether a list of repositories from different pages is returned from an owner"""

        repos_1 = read_file('../data/gitlab_user_repos_1.json')
        repos_2 = read_file('../data/gitlab_user_repos_2.json')

        httpretty.register_uri(httpretty.GET,
                               GITLAB_USER_REPOS_URL,
                               body=repos_1,
                               status=200,
                               forcing_headers={
                                   'Link': '<{}/?&page=2>; rel="next", '
                                           '<{}/?&page=2>; rel="last"'.format(GITLAB_USER_REPOS_URL,
                                                                              GITLAB_USER_REPOS_URL)
                               })

        httpretty.register_uri(httpretty.GET,
                               GITLAB_USER_REPOS_URL + '/?&page=2',
                               body=repos_2,
                               status=200)

        repos_iter = GitLab().fetch_user_repositories(user_id=123456)
        repositories = list(repos_iter)

        repo = repositories[0]
        self.assertEqual(repo['url'], 'https://gitlab.com/user_example/project-1')
        self.assertEqual(repo['fork'], True)
        self.assertEqual(repo['has_issues'], True)

        repo = repositories[1]
        self.assertEqual(repo['url'], 'https://gitlab.com/user_example/project-2')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], False)

        repo = repositories[2]
        self.assertEqual(repo['url'], 'https://gitlab.com/user_example/project-3')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], True)

        repo = repositories[3]
        self.assertEqual(repo['url'], 'https://gitlab.com/user_example/project-4')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], True)

    @httpretty.activate
    def test_fetch_group_repositories(self):
        """Test whether it retrieves a list of repositories of a group"""

        repos_1 = read_file('../data/gitlab_group_repos_1.json')
        repos_2 = read_file('../data/gitlab_group_repos_2.json')
        subgroups = read_file('../data/gitlab_subgroups.json')
        subgroup_repos = read_file('../data/gitlab_subgroup_repos.json')

        httpretty.register_uri(httpretty.GET,
                               GITLAB_GROUP_REPOS_URL,
                               body=repos_1,
                               status=200,
                               forcing_headers={
                                   'Link': '<{}/?&page=2>; rel="next", '
                                           '<{}/?&page=2>; rel="last"'.format(GITLAB_GROUP_REPOS_URL,
                                                                              GITLAB_GROUP_REPOS_URL)
                               })
        httpretty.register_uri(httpretty.GET,
                               GITLAB_GROUP_REPOS_URL + '/?&page=2',
                               body=repos_2,
                               status=200)
        httpretty.register_uri(httpretty.GET,
                               GITLAB_SUBGROUPS_URL,
                               body=subgroups,
                               status=200)
        httpretty.register_uri(httpretty.GET,
                               GITLAB_SUBGROUP_REPOS_URL,
                               body=subgroup_repos,
                               status=200)

        httpretty.register_uri(httpretty.GET,
                               GITLAB_SUB_SUBGROUPS_URL,
                               body="[]",
                               status=200)

        repos_iter = GitLab().fetch_group_repositories(group_id=654321)
        repositories = list(repos_iter)

        repo = repositories[0]
        self.assertEqual(repo['url'], 'https://gitlab.com/group_example/project-1')
        self.assertEqual(repo['fork'], True)
        self.assertEqual(repo['has_issues'], True)

        repo = repositories[1]
        self.assertEqual(repo['url'], 'https://gitlab.com/group_example/project-2')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], False)

        repo = repositories[2]
        self.assertEqual(repo['url'], 'https://gitlab.com/group_example/project-3')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], True)

        repo = repositories[3]
        self.assertEqual(repo['url'], 'https://gitlab.com/group_example/project-4')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], True)

        repo = repositories[4]
        self.assertEqual(repo['url'], 'https://gitlab.com/group_example/subgroup/project-5')
        self.assertEqual(repo['fork'], True)
        self.assertEqual(repo['has_issues'], True)

    @httpretty.activate
    def test_fetch_repositories(self):
        """Test whether it retrieves a list of repositories of a user"""

        body_user = read_file('../data/gitlab_user.json')
        body_repos = read_file('../data/gitlab_user_repos_1.json')

        httpretty.register_uri(httpretty.GET,
                               GITLAB_USER_URL,
                               body=body_user,
                               status=200)
        httpretty.register_uri(httpretty.GET,
                               GITLAB_USER_REPOS_URL,
                               body=body_repos,
                               status=200)

        repos_iter = GitLab().fetch_repositories(name='user_example')
        repositories = list(repos_iter)

        repo = repositories[0]
        self.assertEqual(repo['url'], 'https://gitlab.com/user_example/project-1')
        self.assertEqual(repo['fork'], True)
        self.assertEqual(repo['has_issues'], True)

        repo = repositories[1]
        self.assertEqual(repo['url'], 'https://gitlab.com/user_example/project-2')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], False)

        repo = repositories[2]
        self.assertEqual(repo['url'], 'https://gitlab.com/user_example/project-3')
        self.assertEqual(repo['fork'], False)
        self.assertEqual(repo['has_issues'], True)

    @httpretty.activate
    def test_fetch_with_token(self):
        """Test whether it includes an api token when provided"""

        body = read_file('../data/gitlab_user.json')

        httpretty.register_uri(httpretty.GET,
                               GITLAB_USER_URL,
                               body=body,
                               status=200)

        user_id = GitLab(api_token='aaaa').user_id(GITLAB_USER_NAME)

        self.assertEqual(user_id, 123456)
        self.assertEqual(httpretty.last_request().headers["Authorization"], "Bearer aaaa")

    @httpretty.activate
    def test_wrong_server_status(self):
        """Test whether a it fails when it gets a server error"""

        httpretty.register_uri(httpretty.GET,
                               GITLAB_USER_REPOS_URL,
                               body=[],
                               status=500)

        with self.assertRaises(requests.exceptions.HTTPError):
            repos = GitLab().fetch_user_repositories(123456)
            list(repos)

    @httpretty.activate
    def test_not_name_found(self):
        """Test whether a it fails when it gets a server error"""

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

        with self.assertRaisesRegex(Exception,
                                    NAME_NOT_FOUND_ERROR):
            _ = GitLab().fetch_repositories('user_unknown')
