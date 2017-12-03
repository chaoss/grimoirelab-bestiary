#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Feed Bestiary with projects information
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
import json
import logging
import os

from time import time


import django
# settings.configure()
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_bestiary.settings'
django.setup()

from projects.models import Organization, Project, Repository, RepositoryView, DataSource


def get_params():
    parser = argparse.ArgumentParser(usage="usage: beasts_feeder.py [options]",
                                     description="Feed beastiary with projects")
    parser.add_argument("-f", "--file", required=True, help="JSON projects file")
    parser.add_argument('-g', '--debug', action='store_true')
    parser.add_argument('-o', '--organization', required='True', help='Organization for the projects')

    return parser.parse_args()


def find_repo(repo_view_str, data_source):
    """ Given a repo_view and its data source extract the repository """

    repo = None
    if data_source in ['git', 'github', 'confluence']:
        repo = repo_view_str.split(" ")[0]
    elif data_source in ['mbox']:
        tokens = repo_view_str.split(" ")[0]
        repo = tokens[0] + " " + tokens[1]

    return repo


def find_filters(repo_view_str, data_source):
    """ Given a repo_view and its data source extract the repository """

    filters = ''

    if data_source in ['git', 'github', 'confluence']:
        tokens = repo_view_str.split(" ", 1)
        if len(tokens) > 1:
            filters = tokens[1]
    elif data_source in ['mbox']:
        tokens = repo_view_str.split(" ", 2)
        if len(tokens) > 2:
            filters = tokens[2]

    return filters


def add(cls_orm, **params):
    """ Add an object if it does not exists """

    obj_orm = None

    try:
        obj_orm = cls_orm.objects.get(**params)
    except cls_orm.DoesNotExist:
        obj_orm = cls_orm(**params)
        obj_orm.save()

    return obj_orm


def list_not_ds_fields():
    return ['meta', 'git1']


def load_projects(projects_file, organization):

    # fields in project that are not a data source
    no_ds = list_not_ds_fields()

    add(Organization, **{"name": organization})

    projects = None

    with open(projects_file) as pfile:
        projects = json.load(pfile)

    for project in projects.keys():

        add(Project, **{"name": project})

        for data_source in projects[project]:
            if data_source in no_ds:
                continue

            ds_obj = add(DataSource, **{"name": data_source})

            for repo_view_str in projects[project][data_source]:
                repo = find_repo(repo_view_str, data_source)
                if repo is None:
                    logging.error('Can not find repository for %s %s', data_source, repo_view_str)
                    continue

                repo_obj = add(Repository, **{"name": repo, "data_source": ds_obj})
                repo_filters = find_filters(repo_view_str, data_source)
                add(RepositoryView, **{"filters": repo_filters, "rep": repo_obj})


if __name__ == '__main__':

    task_init = time()

    args = get_params()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
        logging.debug("Debug mode activated")
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    load_projects(args.file, args.organization)

    logging.debug("Total loading time ... %.2f sec", time() - task_init)
