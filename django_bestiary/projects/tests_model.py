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

from .models import Organization, Project, Repository, RepositoryView, DataSource


class OrganizationModelTests(TestCase):

    def test_init(self):
        # The CharField name is filled as en empty string by default, not None
        org = Organization()
        self.assertIsNot(org, None)
        org.save()

        org = Organization(name=None)
        with self.assertRaises(django.db.utils.IntegrityError):
            # The exception tested breaks the test transaction
            with transaction.atomic():
                org.save()

        # Strange that in a CharField you can store dicts!
        org = Organization(name={'trash': 90})
        org.save()


class ProjectModelTests(TestCase):

    def test_init(self):
        project = Project()
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
        ds = DataSource(name='git')
        ds.save()
        rep = Repository(data_source=ds)
        rep.save()


class RepositoryViewModelTests(TestCase):

    def test_init(self):
        rview = RepositoryView()
        self.assertIsNot(rview, None)
        with self.assertRaises(django.db.utils.IntegrityError):
            # The exception tested breaks the test transaction
            with transaction.atomic():
                rview.save()

        ds = DataSource(name='git')
        ds.save()
        rep = Repository(data_source=ds, name='test')
        rview = RepositoryView(rep=rep)
        # rep must be saved before using it in rview above
        # it is saved before rview but it fails because of that
        rep.save()
        with self.assertRaises(django.db.utils.IntegrityError):
            with transaction.atomic():
                rview.save()

        # rep is saved already so we can now use it
        rview = RepositoryView(rep=rep)
        rview.save()

        return


class DataSourceModelTests(TestCase):

    def test_init(self):
        ds = DataSource()
        self.assertIsNot(ds, None)
        ds.save()
