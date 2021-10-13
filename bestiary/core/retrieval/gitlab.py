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
#     Jose Javier Merchante <jjmerchante@bitergia.com>
#

import logging
import requests
from grimoirelab_toolkit.uris import urijoin

GITLAB_API_URL = "https://gitlab.com/api/v4"

logger = logging.getLogger(__name__)


class GitLab:
    """GitLab backend to fetch owner repositories.

    This class allows the fetch repositories from users or groups.

    :param api_token: GitLab auth token to access the API
    :param base_url: GitLab URL in enterprise edition case;
        when no value is set the backend will be fetch the data
        from the GitLab public site.
    """

    def __init__(self, api_token=None, base_url=None):
        self.api_token = api_token
        self.base_url = base_url if base_url else GITLAB_API_URL

    def _fetch(self, url, headers=None, params=None):
        """Fetch the data from a given URL.

        :param url: link to the resource
        :param headers: headers of the request
        """
        headers = headers if headers else {}
        if self.api_token:
            headers['Authorization'] = "Bearer %s" % self.api_token
        r = requests.get(url, headers=headers, params=params)
        return r

    def user_id(self, username):
        """Check if a username is a GitLab user and return its ID.

        :param username: GitLab username

        :returns: ID of the user if exists, else None.
        """
        res = self._fetch(url=urijoin(self.base_url, 'users'),
                          params={'username': username})
        if res.status_code == 404:
            return None
        else:
            res.raise_for_status()
        users = res.json()
        if len(users) > 0:
            return users[0]['id']

    def group_id(self, name):
        """Check if a name is a GitLab group and return its ID.

        :param name: GitLab name

        :returns: ID of the group if exists, else None.
        """
        res = self._fetch(url=urijoin(self.base_url, 'groups', name))
        if res.status_code == 404:
            return None
        else:
            res.raise_for_status()
        group = res.json()
        return group['id']

    def _iter_repositories(self, url):
        """Fetch repositories url using pagination from a given url"""

        while True:
            res = self._fetch(url)
            res.raise_for_status()
            for repo in res.json():
                repo_data = {
                    'url': repo['web_url'],
                    'fork': 'forked_from_project' in repo,
                    'has_issues': True if 'issues_enabled' not in repo else repo['issues_enabled']
                }
                yield repo_data
            if 'next' in res.links.keys():
                url = res.links['next']['url']
            else:
                break

    def _iter_subgroups(self, url):
        """Fetch subgroups id using pagination from a given url"""

        params = {'all_available': True}
        while True:
            res = self._fetch(url, params=params)
            res.raise_for_status()
            for group in res.json():
                yield group['id']
            if 'next' in res.links.keys():
                url = res.links['next']['url']
            else:
                break

    def fetch_user_repositories(self, user_id):
        """Fetch GitLab repositories from a user.

        This function fetch all the repositories from a GitLab owner.
        It return a list of repositories indicating whether the repository
        is a fork, has issues enabled, or has merge requests enabled.

        :param user_id: id of the GitLab user

        :returns: a list of repositories including url, has_issues and fork.
        """
        logger.debug(
            f"Fetching GitLab user repositories; "
            f"user_id={user_id}; ..."
        )

        url = urijoin(self.base_url, 'users', user_id, 'projects')
        return self._iter_repositories(url)

    def fetch_group_repositories(self, group_id):
        """Fetch GitLab repositories from a group.

        This function fetch all the repositories from a GitLab group
        and subgroups in a recursive way.
        It return an iterator with the list of repositories indicating
        whether the repository is a fork, has issues enabled, or
        has merge requests enabled.

        :param group_id: id of the GitLab group

        :returns: a list of repositories including url, has_issues and fork.
        """
        logger.debug(
            f"Fetching GitLab group repositories; "
            f"group_id={group_id}; ..."
        )

        url = urijoin(self.base_url, 'groups', group_id, 'projects')
        for repo in self._iter_repositories(url):
            yield repo
        url_subgroups = urijoin(self.base_url, 'groups', group_id, 'subgroups')
        for subgroup_id in self._iter_subgroups(url_subgroups):
            for repo in self.fetch_group_repositories(subgroup_id):
                yield repo

    def fetch_repositories(self, name):
        """Fetch GitLab repositories from a user or group.

        This function fetch all the repositories from a GitLab user
        or a GitLab group and subgroups. It checks what type is the name
        requested and returns an iterator with the repositories.
        If the name does not exist in GitLab, it raises an exception.
        """
        user_id = self.user_id(name)
        if user_id:
            return self.fetch_user_repositories(user_id)

        group_id = self.group_id(name)
        if group_id:
            return self.fetch_group_repositories(group_id)

        raise Exception(f'GitLab owner "{name}" not found')
