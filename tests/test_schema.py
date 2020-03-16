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

import django.test
import graphene
import graphene.test

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from grimoirelab_toolkit.datetime import datetime_utcnow, str_to_datetime

from bestiary.core.context import BestiaryContext
from bestiary.core.log import TransactionsLog
from bestiary.core.models import (Transaction,
                                  Operation)
from bestiary.core.schema import BestiaryQuery, BestiaryMutation


AUTHENTICATION_ERROR = "You do not have permission to perform this action"

# Test queries
BT_TRANSACTIONS_QUERY = """{
  transactions {
    entities {
      name
      createdAt
      tuid
      isClosed
      closedAt
      authoredBy
    }
  }
}"""
BT_TRANSACTIONS_QUERY_FILTER = """{
  transactions(
    filters: {
      tuid: "%s",
      name: "%s",
      fromDate: "%s",
      authoredBy: "%s"
    }
  ){
    entities {
      name
      createdAt
      tuid
      isClosed
      closedAt
      authoredBy
    }
  }
}"""
BT_TRANSACTIONS_QUERY_PAGINATION = """{
  transactions(
    page: %d
    pageSize: %d
  ){
    entities {
      name
      createdAt
      tuid
      isClosed
      closedAt
      authoredBy
    }
    pageInfo{
      page
      pageSize
      numPages
      hasNext
      hasPrev
      startIndex
      endIndex
      totalResults
    }
  }
}"""
BT_OPERATIONS_QUERY = """{
  operations {
    entities {
      ouid
      opType
      entityType
      target
      timestamp
      args
      trx{
        name
        createdAt
        tuid
      }
    }
  }
}"""
BT_OPERATIONS_QUERY_FILTER = """{
  operations(
    filters:{
      opType:"%s",
      entityType:"%s",
      fromDate:"%s"
    }
  ){
    entities {
      ouid
      opType
      entityType
      target
      timestamp
      args
      trx{
        name
        createdAt
        tuid
      }
    }
  }
}"""
BT_OPERATIONS_QUERY_PAGINATION = """{
  operations(
    page: %d
    pageSize: %d
  ){
    entities{
      ouid
      opType
      entityType
      target
      timestamp
      args
      trx{
        name
        createdAt
        tuid
      }
    }
    pageInfo{
      page
      pageSize
      numPages
      hasNext
      hasPrev
      startIndex
      endIndex
      totalResults
    }
  }
}"""
BT_OPERATIONS_QUERY_PAGINATION_NO_PAGE = """{
  operations(
    pageSize: %d
  ){
    entities{
      ouid
      opType
      entityType
      target
      timestamp
      args
      trx{
        name
        createdAt
        tuid
      }
    }
    pageInfo{
      page
      pageSize
      numPages
      hasNext
      hasPrev
      startIndex
      endIndex
      totalResults
    }
  }
}"""
BT_OPERATIONS_QUERY_PAGINATION_NO_PAGE_SIZE = """{
  operations(
    page: %d
  ){
    entities{
      ouid
      opType
      entityType
      target
      timestamp
      args
      trx{
        name
        createdAt
        tuid
      }
    }
    pageInfo{
      page
      pageSize
      numPages
      hasNext
      hasPrev
      startIndex
      endIndex
      totalResults
    }
  }
}"""

# API endpoint to obtain a context for executing queries
GRAPHQL_ENDPOINT = '/graphql/'


class TestQuery(BestiaryQuery, graphene.ObjectType):
    pass


class TestQueryPagination(django.test.TestCase):
    pass


class TestMutations(BestiaryMutation):
    pass


schema = graphene.Schema(query=TestQuery,
                         mutation=TestMutations)


class TestQueryTransactions(django.test.TestCase):
    """Unit tests for transaction queries"""

    def setUp(self):
        """Load initial dataset and set queries context"""

        self.user = get_user_model().objects.create(username='test')
        self.context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        self.context_value.user = self.user

        self.ctx = BestiaryContext(self.user)

        # Create a transaction controlling input values
        self.timestamp = datetime_utcnow()  # This will be used as a filter
        self.trx = Transaction(name='test_trx',
                               tuid='012345abcdef',
                               created_at=datetime_utcnow(),
                               authored_by=self.user.username)
        self.trx.save()

    def test_transaction(self):
        """Check if it returns the registry of transactions"""

        timestamp = datetime_utcnow()
        client = graphene.test.Client(schema)
        executed = client.execute(BT_TRANSACTIONS_QUERY,
                                  context_value=self.context_value)

        transactions = executed['data']['transactions']['entities']
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertEqual(trx['name'], self.trx.name)
        self.assertEqual(str_to_datetime(trx['createdAt']), self.trx.created_at)
        self.assertEqual(trx['tuid'], self.trx.tuid)
        self.assertIsNone(trx['closedAt'])
        self.assertFalse(trx['isClosed'])
        self.assertEqual(trx['authoredBy'], 'test')

    def test_filter_registry(self):
        """Check whether it returns the transaction searched when using filters"""

        client = graphene.test.Client(schema)
        test_query = BT_TRANSACTIONS_QUERY_FILTER % ('012345abcdef', 'test_trx',
                                                     self.timestamp.isoformat(),
                                                     'test')
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        transactions = executed['data']['transactions']['entities']
        self.assertEqual(len(transactions), 1)

        trx = transactions[0]
        self.assertEqual(trx['name'], self.trx.name)
        self.assertEqual(str_to_datetime(trx['createdAt']), self.trx.created_at)
        self.assertEqual(trx['tuid'], self.trx.tuid)
        self.assertIsNone(trx['closedAt'])
        self.assertFalse(trx['isClosed'])
        self.assertEqual(trx['authoredBy'], 'test')

    def test_filter_non_existing_registry(self):
        """Check whether it returns an empty list when searched with a non existing transaction"""

        client = graphene.test.Client(schema)
        test_query = BT_TRANSACTIONS_QUERY_FILTER % ('012345abcdefg', 'test_trx',
                                                     self.timestamp.isoformat(),
                                                     'test')
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        transactions = executed['data']['transactions']['entities']
        self.assertListEqual(transactions, [])

    def test_pagination(self):
        """Check whether it returns the transactions searched when using pagination"""

        # Creating additional transactions
        trx = Transaction(name='test_trx_2',
                          tuid='567890abcdef',
                          created_at=datetime_utcnow(),
                          authored_by=self.user.username,
                          is_closed=True,
                          closed_at=datetime_utcnow())
        trx.save()

        trx = Transaction(name='test_trx_3',
                          tuid='098765fedcba',
                          created_at=datetime_utcnow(),
                          authored_by=self.user.username,
                          is_closed=True,
                          closed_at=datetime_utcnow())
        trx.save()

        timestamp = datetime_utcnow()

        client = graphene.test.Client(schema)
        test_query = BT_TRANSACTIONS_QUERY_PAGINATION % (1, 2)
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        transactions = executed['data']['transactions']['entities']
        self.assertEqual(len(transactions), 2)

        trx = transactions[0]
        self.assertEqual(trx['name'], 'test_trx')
        self.assertLess(str_to_datetime(trx['createdAt']), timestamp)
        self.assertEqual(trx['tuid'], '012345abcdef')
        self.assertIsNone(trx['closedAt'])
        self.assertFalse(trx['isClosed'])
        self.assertEqual(trx['authoredBy'], 'test')

        trx = transactions[1]
        self.assertEqual(trx['name'], 'test_trx_2')
        self.assertLess(str_to_datetime(trx['createdAt']), timestamp)
        self.assertEqual(trx['tuid'], '567890abcdef')
        self.assertLess(str_to_datetime(trx['closedAt']), timestamp)
        self.assertTrue(trx['isClosed'])
        self.assertEqual(trx['authoredBy'], 'test')

        pag_data = executed['data']['transactions']['pageInfo']
        self.assertEqual(len(pag_data), 8)
        self.assertEqual(pag_data['page'], 1)
        self.assertEqual(pag_data['pageSize'], 2)
        self.assertEqual(pag_data['numPages'], 2)
        self.assertTrue(pag_data['hasNext'])
        self.assertFalse(pag_data['hasPrev'])
        self.assertEqual(pag_data['startIndex'], 1)
        self.assertEqual(pag_data['endIndex'], 2)
        self.assertEqual(pag_data['totalResults'], 3)

    def test_empty_registry(self):
        """Check whether it returns an empty list when the registry is empty"""

        # Delete Transactions created in `setUp` method
        Transaction.objects.all().delete()
        transactions = Transaction.objects.all()

        self.assertEqual(len(transactions), 0)

        # Test query
        client = graphene.test.Client(schema)
        executed = client.execute(BT_TRANSACTIONS_QUERY,
                                  context_value=self.context_value)

        q_transactions = executed['data']['transactions']['entities']
        self.assertListEqual(q_transactions, [])

    def test_authentication(self):
        """Check if it fails when a non-authenticated user executes the query"""

        context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        context_value.user = AnonymousUser()

        client = graphene.test.Client(schema)

        executed = client.execute(BT_TRANSACTIONS_QUERY,
                                  context_value=context_value)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, AUTHENTICATION_ERROR)


class TestQueryOperations(django.test.TestCase):
    """Unit tests for operation queries"""

    def setUp(self):
        """Load initial dataset and set queries context"""

        self.user = get_user_model().objects.create(username='test')
        self.context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        self.context_value.user = self.user

        self.ctx = BestiaryContext(self.user)

        # Create an operation controlling input values
        trx = Transaction(name='test_trx',
                          tuid='012345abcdef',
                          created_at=datetime_utcnow(),
                          authored_by=self.user.username)
        trx.save()

        self.trxl = TransactionsLog(trx, self.ctx)
        self.timestamp = datetime_utcnow()  # This will be used as a filter
        self.trxl.log_operation(op_type=Operation.OpType.UPDATE,
                                entity_type='test_entity',
                                timestamp=datetime_utcnow(),
                                args={'test_arg': 'test_value'},
                                target='test_target')
        self.trxl.log_operation(op_type=Operation.OpType.ADD,
                                entity_type='test_entity_2',
                                timestamp=datetime_utcnow(),
                                args={'test_arg_2': 'test_value_2'},
                                target='test_target_2')
        self.trxl.log_operation(op_type=Operation.OpType.DELETE,
                                entity_type='test_entity_3',
                                timestamp=datetime_utcnow(),
                                args={'test_arg_3': 'test_value_3'},
                                target='test_target_3')
        self.trxl.close()

    def test_operation(self):
        """Check if it returns the registry of operations"""

        client = graphene.test.Client(schema)
        executed = client.execute(BT_OPERATIONS_QUERY,
                                  context_value=self.context_value)

        operations = executed['data']['operations']['entities']
        self.assertEqual(len(operations), 3)

        for op in operations:
            # Check if the query returns the associated transaction
            trx = op['trx']
            self.assertEqual(trx['name'], self.trxl.trx.name)
            self.assertEqual(trx['tuid'], self.trxl.trx.tuid)
            self.assertEqual(str_to_datetime(trx['createdAt']), self.trxl.trx.created_at)

        op = operations[0]
        self.assertEqual(op['opType'], Operation.OpType.UPDATE.value)
        self.assertEqual(op['entityType'], 'test_entity')
        self.assertGreater(str_to_datetime(op['timestamp']), self.timestamp)
        self.assertEqual(op['target'], 'test_target')
        self.assertEqual(op['args'], {'test_arg': 'test_value'})

        op = operations[1]
        self.assertEqual(op['opType'], Operation.OpType.ADD.value)
        self.assertEqual(op['entityType'], 'test_entity_2')
        self.assertGreater(str_to_datetime(op['timestamp']), self.timestamp)
        self.assertEqual(op['target'], 'test_target_2')
        self.assertEqual(op['args'], {'test_arg_2': 'test_value_2'})

        op = operations[2]
        self.assertEqual(op['opType'], Operation.OpType.DELETE.value)
        self.assertEqual(op['entityType'], 'test_entity_3')
        self.assertGreater(str_to_datetime(op['timestamp']), self.timestamp)
        self.assertEqual(op['target'], 'test_target_3')
        self.assertEqual(op['args'], {'test_arg_3': 'test_value_3'})

    def test_filter_registry(self):
        """Check whether it returns the operation searched when using filters"""

        client = graphene.test.Client(schema)
        test_query = BT_OPERATIONS_QUERY_FILTER % ('UPDATE', 'test_entity',
                                                   self.timestamp.isoformat())
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        operations = executed['data']['operations']['entities']
        self.assertEqual(len(operations), 1)

        op1 = operations[0]
        self.assertEqual(op1['opType'], Operation.OpType.UPDATE.value)
        self.assertEqual(op1['entityType'], 'test_entity')
        self.assertGreater(str_to_datetime(op1['timestamp']), self.timestamp)
        self.assertEqual(op1['args'], {'test_arg': 'test_value'})

        # Check if the query returns the associated transaction
        trx1 = op1['trx']
        self.assertEqual(trx1['name'], self.trxl.trx.name)
        self.assertEqual(trx1['tuid'], self.trxl.trx.tuid)
        self.assertEqual(str_to_datetime(trx1['createdAt']), self.trxl.trx.created_at)

    def test_filter_non_existing_registry(self):
        """Check whether it returns an empty list when searched with a non existing operation"""

        client = graphene.test.Client(schema)
        test_query = BT_OPERATIONS_QUERY_FILTER % ('DELETE', 'test_entity',
                                                   self.timestamp.isoformat())
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        operations = executed['data']['operations']['entities']
        self.assertListEqual(operations, [])

    def test_pagination(self):
        """Check whether it returns the operations searched when using pagination"""

        client = graphene.test.Client(schema)
        test_query = BT_OPERATIONS_QUERY_PAGINATION % (1, 2)
        executed = client.execute(test_query,
                                  context_value=self.context_value)

        operations = executed['data']['operations']['entities']
        self.assertEqual(len(operations), 2)

        op1 = operations[0]
        self.assertEqual(op1['opType'], Operation.OpType.UPDATE.value)
        self.assertEqual(op1['entityType'], 'test_entity')
        self.assertGreater(str_to_datetime(op1['timestamp']), self.timestamp)
        self.assertEqual(op1['args'], {'test_arg': 'test_value'})

        op2 = operations[1]
        self.assertEqual(op2['opType'], Operation.OpType.ADD.value)
        self.assertEqual(op2['entityType'], 'test_entity_2')
        self.assertEqual(op2['target'], 'test_target_2')
        self.assertGreater(str_to_datetime(op2['timestamp']), self.timestamp)
        self.assertEqual(op2['args'], {'test_arg_2': 'test_value_2'})

        pag_data = executed['data']['operations']['pageInfo']
        self.assertEqual(len(pag_data), 8)
        self.assertEqual(pag_data['page'], 1)
        self.assertEqual(pag_data['pageSize'], 2)
        self.assertEqual(pag_data['numPages'], 2)
        self.assertTrue(pag_data['hasNext'])
        self.assertFalse(pag_data['hasPrev'])
        self.assertEqual(pag_data['startIndex'], 1)
        self.assertEqual(pag_data['endIndex'], 2)
        self.assertEqual(pag_data['totalResults'], 3)

    def test_empty_registry(self):
        """Check whether it returns an empty list when the registry is empty"""

        # Delete Operations created in `setUp` method
        Operation.objects.all().delete()
        operations = Operation.objects.all()

        self.assertEqual(len(operations), 0)

        # Test query
        client = graphene.test.Client(schema)
        executed = client.execute(BT_OPERATIONS_QUERY,
                                  context_value=self.context_value)

        q_operations = executed['data']['operations']['entities']
        self.assertListEqual(q_operations, [])

    def test_authentication(self):
        """Check if it fails when a non-authenticated user executes the query"""

        context_value = RequestFactory().get(GRAPHQL_ENDPOINT)
        context_value.user = AnonymousUser()

        client = graphene.test.Client(schema)

        executed = client.execute(BT_OPERATIONS_QUERY,
                                  context_value=context_value)

        msg = executed['errors'][0]['message']
        self.assertEqual(msg, AUTHENTICATION_ERROR)
