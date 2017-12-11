#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Bestiary Tests
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

import django

from django.db import transaction
from django.test import TestCase

from .models import Ecosystem, Project, Repository, DataSource, DataSourceType


class EcosystemModelTests(TestCase):

    def test_init(self):
        # The CharField name is filled as en empty string by default, not None
        eco = Ecosystem()
        self.assertIsNot(eco, None)
        eco.save()

        eco = Ecosystem(name=None)
        with self.assertRaises(django.db.utils.IntegrityError):
            # The exception tested breaks the test transaction
            with transaction.atomic():
                eco.save()

        # Strange that in a CharField you can store dicts!
        eco = Ecosystem(name={'trash': 90})
        eco.save()


class ProjectModelTests(TestCase):

    def test_init(self):
        # All projects are related to a ecosystem
        eco = Ecosystem()
        eco.save()
        project = Project(eco=eco)
        self.assertIsNot(project, None)
        project.save()


class RepositoryModelTest(TestCase):

    def test_init(self):
        rep = Repository()
        self.assertIsNot(rep, None)
        with self.assertRaises(django.db.utils.IntegrityError):
            # The exception tested breaks the test transaction
            with transaction.atomic():
                rep.save()
        ds_type = DataSourceType(name='git')
        ds_type.save()
        rep = Repository(data_source_type=ds_type)
        rep.save()


class DataSourceModelTests(TestCase):

    def test_init(self):
        data_source = DataSource()
        self.assertIsNot(data_source, None)
        with self.assertRaises(django.db.utils.IntegrityError):
            # The exception tested breaks the test transaction
            with transaction.atomic():
                data_source.save()

        ds_type = DataSourceType(name='git')
        ds_type.save()
        rep = Repository(data_source_type=ds_type, name='test')
        data_source = DataSource(rep=rep)
        # rep must be saved before using it in data_source above
        # it is saved before data_source but it fails because of that
        rep.save()
        with self.assertRaises(django.db.utils.IntegrityError):
            with transaction.atomic():
                data_source.save()

        # rep is saved already so we can now use it
        data_source = DataSource(rep=rep)
        data_source.save()

        return


class DataSourceTypeModelTests(TestCase):

    def test_init(self):
        ds_type = DataSourceType()
        self.assertIsNot(ds_type, None)
        ds_type.save()
