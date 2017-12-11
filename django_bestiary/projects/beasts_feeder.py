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
import tempfile

from time import time


from django.test import TestCase

import django
# settings.configure()
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_bestiary.settings'
django.setup()

from projects.models import Ecosystem, Project, Repository, DataSource, DataSourceType
from projects.beasts_exporter import export_projects


def get_params():
    parser = argparse.ArgumentParser(usage="usage: beasts_feeder.py [options]",
                                     description="Feed beastiary with projects")
    parser.add_argument("-f", "--file", required=True, help="JSON projects file")
    parser.add_argument('-g', '--debug', action='store_true')
    parser.add_argument('-o', '--ecosystem', required='True',
                        help='Ecosystem for the projects')
    parser.add_argument('-c', '--check', action='store_true',
                        help='Export the data and compare it with the imported')

    return parser.parse_args()


def find_repo_name(data_source_str, data_source_type):
    """ Given a data_source and its type extract the repository """

    repo = None
    if data_source_type in ['askbot', 'functest', 'hyperkitty', 'jenkins', 'mediawiki',
                            'mozillaclub', 'phabricator', 'pipermail',
                            'redmine', 'remo', 'rss']:
        repo = data_source_str
    elif data_source_type in ['bugzilla', 'bugzillarest']:
        tokens = data_source_str.split("?", 1)
        repo = tokens[0].replace('/bugs/buglist.cgi', '')
    elif data_source_type in ['confluence', 'discourse', 'git', 'github', 'jira',
                              'supybot', 'nntp']:
        repo = data_source_str.split(" ")[0]
    elif data_source_type in ['crates', 'dockerhub', 'google_hits',
                              'meetup', 'puppetforge', 'slack', 'telegram',
                              'twitter']:
        repo = ''  # not needed because it is always the same
    elif data_source_type in ['gerrit']:
        tokens = data_source_str.split("_")
        repo = tokens[0]
    elif data_source_type in ['mbox']:
        tokens = data_source_str.split(" ")
        repo = tokens[0] + " " + tokens[1]
    elif data_source_type in ['stackexchange']:
        repo = data_source_str.split("questions")[0]

    return repo


def find_params(data_source_str, data_source_type):
    """ Given a data_source and its type extract the params for the repository """

    params = ''

    if data_source_type in ['askbot', 'crates', 'functest',
                            'hyperkitty', 'jenkins', 'mediawiki', 'mozillaclub',
                            'phabricator', 'pipermail', 'puppetforge', 'redmine',
                            'remo', 'rss']:
        # THese data sources does not support filtering
        params = ''
    elif data_source_type in ['bugzilla', 'bugzillarest']:
        tokens = data_source_str.split("?", 1)
        if len(tokens) > 1:
            params = tokens[1]
    elif data_source_type in ['confluence', 'discourse', 'git', 'github', 'jira',
                              'supybot', 'nntp']:
        tokens = data_source_str.split(" ", 1)
        if len(tokens) > 1:
            params = tokens[1]
    elif data_source_type in ['dockerhub', 'google_hits', 'meetup', 'slack',
                              'telegram', 'twitter']:
        params = data_source_str
    elif data_source_type in ['gerrit']:
        tokens = data_source_str.split("_", 1)
        if len(tokens) > 1:
            params = tokens[1]
    elif data_source_type in ['mbox']:
        tokens = data_source_str.split(" ", 2)
        if len(tokens) > 2:
            params = tokens[2]
    elif data_source_type in ['stackexchange']:
        params = data_source_str.split("tagged/")[1]

    return params


def add(cls_orm, **params):
    """ Add an object if it does not exists """

    obj_orm = None

    try:
        obj_orm = cls_orm.objects.get(**params)
        # logging.debug('Already exists %s: %s', cls_orm.__name__, params)
    except cls_orm.DoesNotExist:
        obj_orm = cls_orm(**params)
        try:
            obj_orm.save()
            logging.debug('Added %s: %s', cls_orm.__name__, params)
        except django.db.utils.IntegrityError as ex:
            logging.error("Can't add %s: %s", cls_orm.__name__, params)
            logging.error(ex)

    return obj_orm


def list_not_ds_fields():
    return ['meta']


def load_projects(projects_file, ecosystem):

    # fields in project that are not a data source
    no_ds = list_not_ds_fields()

    eco_orm = add(Ecosystem, **{"name": ecosystem})

    projects = None
    nprojects = 0
    nrepos = 0

    with open(projects_file) as pfile:
        projects = json.load(pfile)

    for project in projects.keys():
        pparams = {"name": project, "eco": eco_orm}
        if 'meta' in projects[project].keys():
            pparams.update({"meta_title": projects[project]['meta']['title']})
        project_orm = add(Project, **pparams)
        eco_orm.projects.add(project_orm)

        nprojects += 1

        for data_source_type in projects[project]:
            if data_source_type in no_ds:
                continue

            ds_type_obj = add(DataSourceType, **{"name": data_source_type})

            for data_source_str in projects[project][data_source_type]:
                repo_name = find_repo_name(data_source_str, data_source_type)
                if repo_name is None:
                    logging.error('Can not find repository for %s %s', data_source_type, data_source_str)
                    continue

                repo_obj = add(Repository, **{"name": repo_name, "data_source_type": ds_type_obj})
                nrepos += 1
                repo_params = find_params(data_source_str, data_source_type)
                data_source_orm = add(DataSource, **{"params": repo_params, "rep": repo_obj})
                project_orm.data_sources.add(data_source_orm)

        # Register all the repo views added
        project_orm.save()

    # Register all the projects added
    eco_orm.save()

    return (nprojects, nrepos)


def compare_projects_files(orig_file, new_file):
    with open(orig_file) as orig:
        orig_json = json.load(orig)
        with open(new_file) as exported:
            exported_json = json.load(exported)
            test = TestCase()
            test.maxDiff = None
            test.assertDictEqual(orig_json, exported_json)


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

    (nprojects, nrepos) = load_projects(args.file, args.ecosystem)

    logging.debug("Total loading time ... %.2f sec", time() - task_init)
    print("Projects loaded", nprojects)
    print("Repositories loaded", nrepos)

    if args.check:
        logging.info('Checking data ...')
        with tempfile.NamedTemporaryFile() as temp:
            export_projects(temp.name, args.ecosystem)
            compare_projects_files(args.file, temp.name)
