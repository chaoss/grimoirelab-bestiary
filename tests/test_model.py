# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2020 Bitergia
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
#     Miguel Ángel Fernández <mafesan@bitergia.com>
#

import json

from django.db.utils import IntegrityError
from django.test import TransactionTestCase

from grimoirelab_toolkit.datetime import datetime_utcnow

from bestiary.core.models import (Ecosystem,
                                  Project,
                                  Transaction,
                                  Operation)

# Test check errors messages
DUPLICATE_CHECK_ERROR = "Duplicate entry .+"
NULL_VALUE_CHECK_ERROR = "Column .+ cannot be null"


class TestEcosystem(TransactionTestCase):
    """Unit tests for Ecosystem class"""

    def test_unique_ecosystems(self):
        """Check whether ecosystems are unique based on the id"""

        with self.assertRaises(IntegrityError):
            Ecosystem.objects.create(id=128)
            Ecosystem.objects.create(id=128)

    def test_unique_name(self):
        """Check whether ecosystems are unique based on the name"""

        with self.assertRaises(IntegrityError):
            Ecosystem.objects.create(name='Test')
            Ecosystem.objects.create(name='Test')

    def test_charset(self):
        """Check encoding charset"""

        # With an invalid encoding both names wouldn't be inserted;
        # In MySQL, chars 'ı' and 'i' are considered the same with a
        # collation distinct to <charset>_unicode_ci
        Ecosystem.objects.create(name='ıEcosystem')
        Ecosystem.objects.create(name='iEcosystem')

        eco1 = Ecosystem.objects.get(name='ıEcosystem')
        eco2 = Ecosystem.objects.get(name='iEcosystem')

        self.assertEqual(eco1.name, 'ıEcosystem')
        self.assertEqual(eco2.name, 'iEcosystem')

    def test_created_at(self):
        """Check creation date is only set when the object is created"""

        before_dt = datetime_utcnow()
        eco = Ecosystem.objects.create(name='example')
        after_dt = datetime_utcnow()

        self.assertGreaterEqual(eco.created_at, before_dt)
        self.assertLessEqual(eco.created_at, after_dt)

        eco.save()

        self.assertGreaterEqual(eco.created_at, before_dt)
        self.assertLessEqual(eco.created_at, after_dt)

    def test_last_modified(self):
        """Check last modification date is set when the object is updated"""

        before_dt = datetime_utcnow()
        eco = Ecosystem.objects.create(name='example')
        after_dt = datetime_utcnow()

        self.assertGreaterEqual(eco.last_modified, before_dt)
        self.assertLessEqual(eco.last_modified, after_dt)

        before_modified_dt = datetime_utcnow()
        eco.save()
        after_modified_dt = datetime_utcnow()

        self.assertGreaterEqual(eco.last_modified, before_modified_dt)
        self.assertLessEqual(eco.last_modified, after_modified_dt)


class TestProject(TransactionTestCase):
    """Unit tests for Project class"""

    def test_unique_ecosystems(self):
        """Check whether projects are unique based on the id"""

        with self.assertRaises(IntegrityError):
            Project.objects.create(id=128)
            Project.objects.create(id=128)

    def test_unique_name(self):
        """Check whether projects are unique based on the name"""

        with self.assertRaises(IntegrityError):
            Project.objects.create(name='Test')
            Project.objects.create(name='Test')

    def test_add_parent(self):
        """Check whether parent projects can be added to projects"""

        proj_parent = Project.objects.create(name='Test-parent')
        Project.objects.create(name='Test', parent_project=proj_parent)

        proj = Project.objects.get(name='Test')

        self.assertEqual(proj.parent_project, proj_parent)

    def test_charset(self):
        """Check encoding charset"""

        # With an invalid encoding both names wouldn't be inserted;
        # In MySQL, chars 'ı' and 'i' are considered the same with a
        # collation distinct to <charset>_unicode_ci
        Project.objects.create(name='ıProject')
        Project.objects.create(name='iProject')

        proj1 = Project.objects.get(name='ıProject')
        proj2 = Project.objects.get(name='iProject')

        self.assertEqual(proj1.name, 'ıProject')
        self.assertEqual(proj2.name, 'iProject')

    def test_created_at(self):
        """Check creation date is only set when the object is created"""

        before_dt = datetime_utcnow()
        proj = Project.objects.create(name='example')
        after_dt = datetime_utcnow()

        self.assertGreaterEqual(proj.created_at, before_dt)
        self.assertLessEqual(proj.created_at, after_dt)

        proj.save()

        self.assertGreaterEqual(proj.created_at, before_dt)
        self.assertLessEqual(proj.created_at, after_dt)

    def test_last_modified(self):
        """Check last modification date is set when the object is updated"""

        before_dt = datetime_utcnow()
        proj = Project.objects.create(name='example')
        after_dt = datetime_utcnow()

        self.assertGreaterEqual(proj.last_modified, before_dt)
        self.assertLessEqual(proj.last_modified, after_dt)

        before_modified_dt = datetime_utcnow()
        proj.save()
        after_modified_dt = datetime_utcnow()

        self.assertGreaterEqual(proj.last_modified, before_modified_dt)
        self.assertLessEqual(proj.last_modified, after_modified_dt)


class TestTransaction(TransactionTestCase):
    """Unit tests for Transaction class"""

    def test_unique_transactions(self):
        """Check whether transactions are unique"""

        with self.assertRaisesRegex(IntegrityError, DUPLICATE_CHECK_ERROR):
            timestamp = datetime_utcnow()
            Transaction.objects.create(tuid='12345abcd',
                                       name='test',
                                       created_at=timestamp,
                                       authored_by='username')
            Transaction.objects.create(tuid='12345abcd',
                                       name='test',
                                       created_at=timestamp,
                                       authored_by='username')

    def test_created_at(self):
        """Check creation date is only set when the object is created"""

        before_dt = datetime_utcnow()
        trx = Transaction.objects.create(tuid='12345abcd',
                                         name='test',
                                         created_at=datetime_utcnow(),
                                         authored_by='username')
        after_dt = datetime_utcnow()

        self.assertGreaterEqual(trx.created_at, before_dt)
        self.assertLessEqual(trx.created_at, after_dt)

        trx.save()

        # Check if creation date does not change after saving the object
        self.assertGreaterEqual(trx.created_at, before_dt)
        self.assertLessEqual(trx.created_at, after_dt)


class TestOperation(TransactionTestCase):
    """Unit tests for Operation class"""

    def setUp(self):
        """Load initial dataset"""

        Transaction.objects.create(tuid='0123456789abcdef',
                                   name='test', created_at=datetime_utcnow())

    def test_unique_operation(self):
        """Check whether contexts are unique"""

        timestamp = datetime_utcnow()
        trx = Transaction.objects.get(tuid='0123456789abcdef')
        args = json.dumps({'test': 'test_value'})

        with self.assertRaisesRegex(IntegrityError, DUPLICATE_CHECK_ERROR):
            Operation.objects.create(ouid='12345abcd', op_type=Operation.OpType.ADD,
                                     entity_type='test_entity', target='test',
                                     timestamp=timestamp, args=args, trx=trx)
            Operation.objects.create(ouid='12345abcd', op_type=Operation.OpType.ADD,
                                     entity_type='test_entity', target='test',
                                     timestamp=timestamp, args=args, trx=trx)

    def test_created_at(self):
        """Check creation date is only set when the object is created"""

        trx = Transaction.objects.get(tuid='0123456789abcdef')
        args = json.dumps({'test': 'test_value'})

        before_dt = datetime_utcnow()
        operation = Operation.objects.create(ouid='12345abcd', op_type=Operation.OpType.ADD,
                                             entity_type='test_entity', target='test',
                                             timestamp=datetime_utcnow(), args=args, trx=trx)
        after_dt = datetime_utcnow()

        self.assertGreaterEqual(operation.timestamp, before_dt)
        self.assertLessEqual(operation.timestamp, after_dt)

        operation.save()

        # Check if timestamp does not change after saving the object
        self.assertGreaterEqual(operation.timestamp, before_dt)
        self.assertLessEqual(operation.timestamp, after_dt)

    def test_invalid_operation_type_none(self):
        """Check if an error is raised when the operation type is `None`"""

        trx = Transaction.objects.get(tuid='0123456789abcdef')
        args = json.dumps({'test': 'test_value'})

        with self.assertRaisesRegex(IntegrityError, NULL_VALUE_CHECK_ERROR):
            Operation.objects.create(ouid='12345abcd', op_type=None,
                                     entity_type='test_entity', target='test-target',
                                     timestamp=datetime_utcnow(), args=args, trx=trx)

    def test_empty_args(self):
        """Check if an error is raised when no args are set"""

        trx = Transaction.objects.get(tuid='0123456789abcdef')

        with self.assertRaisesRegex(IntegrityError, NULL_VALUE_CHECK_ERROR):
            Operation.objects.create(ouid='12345abcd', op_type=Operation.OpType.ADD,
                                     entity_type='test_entity', target='test',
                                     timestamp=datetime_utcnow(), args=None, trx=trx)
