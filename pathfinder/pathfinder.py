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

import argparse
import logging
import os
import sys

from repositories.eclipse import ReposEclipse
from repositories.gerrit import ReposGerrit
from repositories.github import ReposGitHub

import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_bestiary.settings'
django.setup()

from projects.models import DataSource, Project, Repository, RepositoryView


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

    parser.add_argument('-b', '--backend', help='Repositories backend to use',
                        default='github')
    parser.add_argument('-d', '--data-source',
                        help='Data source to get repositories from',
                        default='github')
    parser.add_argument('-g', '--debug', action='store_true')
    parser.add_argument('-t', '--token', help="Auth token")
    parser.add_argument('-o', '--owner', help='GitHub owner to get repos from')
    parser.add_argument('--host', help="repositories server host")
    parser.add_argument('-u', '--user', help="User for accessing the repositories host")
    parser.add_argument('-p', '--project', help="Import repositories to project in Bestiary")

    args = parser.parse_args()

    if not args.backend:
        parser.error("backend must be provided.")
        sys.exit(1)

    if args.backend == 'github' and (not args.token or not args.owner):
        parser.error("github backend needs token and owner.")
        sys.exit(1)

    if args.backend == 'gerrit' and (not args.host or not args.user):
        parser.error("gerrit backend needs host and user.")
        sys.exit(1)


    return args


if __name__ == '__main__':

    args = get_params()

    config_logging(args.debug)

    # Retrieve all the repositories
    if args.backend == 'github':
        repos = ReposGitHub("github.com", args.owner, args.token)
    elif args.backend == 'eclipse':
        repos = ReposEclipse(args.data_source)
    elif args.backend == 'gerrit':
        repos = ReposGerrit(args.host, args.user)
    else:
        logger.error("Backend %s not supported", args.backend)
        sys.exit(1)

    project_orm = None
    if args.project:
        # Try to find the project in bestiary
        try:
            project_orm = Project.objects.get(name=args.project)
            logger.debug('%s found in Bestiary', project_orm)
            logger.debug('Adding repositories to project %s', project_orm)
        except Project.DoesNotExist:
            logger.error("Can not find project %s", args.project)
            logger.error("The project must already exists in Beastiary")
            sys.exit(1)

    for repo in repos.get_ids():
        if not args.project:
            print(repo)
        else:
            try:
                ds_orm = DataSource.objects.get(name=args.backend)
            except DataSource.DoesNotExist:
                logger.error("The data source %s does not exists in Bestiary", args.backend)
                sys.exit(1)
            try:
                rep = Repository(name=repo, data_source=ds_orm)
                rep.save()
            except django.db.utils.IntegrityError:
                logger.debug('Repository already exists %s', repo)
                rep = Repository.objects.get(name=repo, data_source=ds_orm)
            try:
                # Don't support filters yet
                rep_view = RepositoryView(rep=rep, filters='')
                rep_view.save()
            except:
                logger.debug('Repository View already exists %s', repo)
                rep_view = RepositoryView.objects.get(rep=rep, filters='')

            project_orm.rep_views.add(rep_view)

    if args.project:
        project_orm.save()
