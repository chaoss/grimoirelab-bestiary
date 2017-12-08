#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#
# Copyright (C) 2017 Bitergia
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#   Alvaro del Castillo San Felix <acs@bitergia.com>
#

""" Sample script for managing projects from GitHub repositories """

import argparse
import logging
import sys

sys.path.insert(0, '../..')
from pathfinder.repositories.github import ReposGitHub
from projects import Projects

logger = logging.getLogger(__name__)


def config_logging(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
        logging.debug("Debug mode activated")
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_params():
    """Parse command line arguments"""

    parser = argparse.ArgumentParser()

    parser.add_argument('-g', '--debug', dest='debug', action='store_true')
    parser.add_argument('-t', '--token', dest='token', help="GitHub token")
    parser.add_argument('-o', '--owners', dest='owners', nargs='*',
                        help='GitHub owners to get repos from')
    parser.add_argument('-r', '--repos', dest='repos', nargs='*',
                        help='GitHub repos ids to include')
    parser.add_argument('-b', '--blacklist', dest='blacklist', nargs='*',
                        help='GitHub repos ids to exclude')
    parser.add_argument('-p', '--project', dest='project',
                        help='Project repos to be updated')
    parser.add_argument('--projects-file', dest='projects_file',
                        help='Projects file to be updated')
    parser.add_argument('-f', '--forks', dest='forks', action='store_true',
                        help='Include forked repos')

    args = parser.parse_args()

    if not args.owners or not args.token or not args.projects_file or not args.project:
        parser.error("token, owner, project and projects file params must be provided.")
        sys.exit(1)

    return args


if __name__ == '__main__':

    args = get_params()

    config_logging(args.debug)

    # Just github in this first iteration
    data_source = "github"

    # Load the projects to be updated
    project = args.project
    projects = Projects(args.projects_file)

    # Retrieve all the repositories
    repos = ReposGitHub(args.owners, args.token)
    repos_list = []
    for repo in repos.get_repos():
        if not args.forks and repos.is_fork(repo):
            logger.debug("Not adding fork %s", repos.get_id(repo))
            continue

        if args.blacklist and repos.get_id(repo) in args.blacklist:
            logger.debug("Not adding blacklisted repo %s", repos.get_id(repo))
            continue

        repos_list.append(repos.get_id(repo))

    # Adding additional repos
    if args.repos:
        for add_repo_id in args.repos:
            logger.debug("Adding extra repo %s", add_repo_id)
            repos_list.append(add_repo_id)

    logger.debug("Added repos: %s", set(repos_list) - set(projects.get_project_repos(project, 'github')))
    logger.debug("Removed repos: %s", set(projects.get_project_repos(project, 'github')) - set(repos_list))

    # projects.set_project_repos(project, data_source, repos_list)
    projects.update_project_repos(project, data_source, repos_list)
    projects.dump()
