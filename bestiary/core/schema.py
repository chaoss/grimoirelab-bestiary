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

import graphene
import graphql_jwt

from django.conf import settings
from django.core.paginator import Paginator

from django_mysql.models import JSONField

from graphene.types.generic import GenericScalar

from graphene_django.converter import convert_django_field
from graphene_django.types import DjangoObjectType

from .api import (add_ecosystem,
                  update_ecosystem,
                  delete_ecosystem)
from .context import BestiaryContext
from .decorators import check_auth
from .models import (Ecosystem,
                     Transaction,
                     Operation)


@convert_django_field.register(JSONField)
def convert_json_field_to_generic_scalar(field, registry=None):
    """Convert the content of a `JSONField` loading it as an object"""

    return OperationArgsType(description=field.help_text, required=not field.null)


class PaginationType(graphene.ObjectType):
    """Generic type to define pagination information when returning sets of results"""

    class Meta:
        description = "Generic type to define pagination information when returning sets of results."

    page = graphene.Int(
        description='Number of the current page'
    )
    page_size = graphene.Int(
        description='Number of results per page'
    )
    num_pages = graphene.Int(
        description='Total number of pages with results'
    )
    has_next = graphene.Boolean(
        description='Boolean value, `True` if exists at least one more page with results'
    )
    has_prev = graphene.Boolean(
        description='Boolean value, `True` if exists at least one previous page with results'
    )
    start_index = graphene.Int(
        description='Starting index of the returned results compared to the total set'
    )
    end_index = graphene.Int(
        description='Final index of the returned results compared to the total set'
    )
    total_results = graphene.Int(
        description='Number of total results'
    )


class OperationArgsType(GenericScalar):
    """Type including the input arguments from Operation objects loaded from JSON format"""

    class Meta:
        description = "Operation input arguments in JSON format."

    @classmethod
    def serialize(cls, value):
        value = super().serialize(value)
        value = json.loads(value)
        return value


class OperationType(DjangoObjectType):
    """Base type for Operation objects as defined in models"""

    class Meta:
        model = Operation
        description = "Operation objects representing atomic operations modifying the registry."


class TransactionType(DjangoObjectType):
    """Base type for Transaction objects as defined in models"""

    class Meta:
        model = Transaction
        description = "Transaction objects representing atomic sets of operations modifying the registry."


class EcosystemType(DjangoObjectType):
    """Ecosystem objects are meant to gather a set of projects sharing a common context"""

    class Meta:
        model = Ecosystem


class EcosystemInputType(graphene.InputObjectType):
    """Fieds which can be used as an input for Ecosystem-related mutations"""

    name = graphene.String(required=False)
    title = graphene.String(required=False)
    description = graphene.String(required=False)


class TransactionFilterType(graphene.InputObjectType):
    """Fields which can be used as a filter for TransactionPaginatedType objects"""

    class Meta:
        description = """Use this type to apply filters when retrieving transactions information.
        Note that these filters are concatenated as `AND` conditions.
        """

    tuid = graphene.String(
        required=False,
        description='Transaction unique id'
    )
    name = graphene.String(
        required=False,
        description='Name of the method creating the transaction'
    )
    is_closed = graphene.Boolean(
        required=False,
        description='Boolean value, `True` if the transaction is closed'
    )
    from_date = graphene.DateTime(
        required=False,
        description='Transactions which creation date is greater or equal'
    )
    to_date = graphene.DateTime(
        required=False,
        description='Transactions which creation date is less or equal'
    )
    authored_by = graphene.String(
        required=False,
        description='`username` from the user who created the transaction'
    )


class OperationFilterType(graphene.InputObjectType):
    """Fields which can be used as a filter for OperationPaginatedType objects"""

    class Meta:
        description = """Use this type to apply filters when retrieving operations information.
        Note that these filters are concatenated as `AND` conditions.
        """

    ouid = graphene.String(
        required=False,
        description='Operation unique id'
    )
    op_type = graphene.String(
        required=False,
        description='Operation type (`ADD`, `DELETE` or `UPDATE`)'
    )
    entity_type = graphene.String(
        required=False,
        description='Type of the main entity involved in the operation'
    )
    target = graphene.String(
        required=False,
        description='Identifier of the targeted entity for the operation'
    )
    from_date = graphene.DateTime(
        required=False,
        description='Operations which creation date is greater or equal'
    )
    to_date = graphene.DateTime(
        required=False,
        description='Operations which creation date is less or equal'
    )


class EcosystemFilterType(graphene.InputObjectType):
    """Fields which can be used as a filter for EcosystemPaginatedType objects"""

    id = graphene.ID(required=False)
    name = graphene.String(required=False)


class AbstractPaginatedType(graphene.ObjectType):
    """Generic class for objects returning paginated results

    This class aims to represent in a generic way objects
    which can be returned as a set of paginated results.

    These paginated results will be returned within the `entities`
    object list. On top of that, the class provides information
    about the pagination, such as the total number of results
    or the current cursors referred to the results.

    An `AbstractPaginatedType` object must be created using its
    constructor method, which receives as input the `QuerySet`
    object with the results, the number of the page to show
    and the page size.
    """
    @classmethod
    def create_paginated_result(cls, query, page=1,
                                page_size=settings.DEFAULT_GRAPHQL_PAGE_SIZE):
        paginator = Paginator(query, page_size)
        result = paginator.page(page)

        entities = result.object_list

        page_info = PaginationType(
            page=result.number,
            page_size=page_size,
            num_pages=paginator.num_pages,
            has_next=result.has_next(),
            has_prev=result.has_previous(),
            start_index=result.start_index(),
            end_index=result.end_index(),
            total_results=len(query)
        )

        return cls(entities=entities, page_info=page_info)


class TransactionPaginatedType(AbstractPaginatedType):
    """Type returning paginated results of TransactionType objects"""

    class Meta:
        description = "Type returning paginated results of TransactionType objects."

    entities = graphene.List(
        TransactionType,
        description='List of TransactionType objects'
    )
    page_info = graphene.Field(
        PaginationType,
        description='Pagination information'
    )


class OperationPaginatedType(AbstractPaginatedType):
    """Type returning paginated results of OperationType objects"""

    class Meta:
        description = "Type returning paginated results of OperationType objects."

    entities = graphene.List(
        OperationType,
        description='List of OperationType objects'
    )
    page_info = graphene.Field(
        PaginationType,
        description='Pagination information'
    )


class EcosystemPaginatedType(AbstractPaginatedType):
    """Type returning paginated results of EcosystemType objects"""

    entities = graphene.List(EcosystemType)
    page_info = graphene.Field(PaginationType)


class AddEcosystem(graphene.Mutation):
    """Mutation which adds a new Ecosystem on the registry"""

    class Arguments:
        name = graphene.String()
        title = graphene.String(required=False)
        description = graphene.String(required=False)

    ecosystem = graphene.Field(lambda: EcosystemType)

    @check_auth
    def mutate(self, info, name, title=None, description=None):
        user = info.context.user
        ctx = BestiaryContext(user)

        ecosystem = add_ecosystem(ctx, name, title=title, description=description)

        return AddEcosystem(
            ecosystem=ecosystem
        )


class UpdateEcosystem(graphene.Mutation):
    """Mutation which updates an existing Ecosystem"""

    class Arguments:
        id = graphene.ID()
        data = EcosystemInputType()

    ecosystem = graphene.Field(lambda: EcosystemType)

    @check_auth
    def mutate(self, info, id, data):
        user = info.context.user
        ctx = BestiaryContext(user)

        # Forcing this conversion explicitly, as input value is taken as a string
        id_value = int(id)

        ecosystem = update_ecosystem(ctx, id_value, **data)

        return UpdateEcosystem(
            ecosystem=ecosystem
        )


class DeleteEcosystem(graphene.Mutation):
    """Mutation which deletes an existing Ecosystem from the registry"""

    class Arguments:
        id = graphene.ID()

    ecosystem = graphene.Field(lambda: EcosystemType)

    @check_auth
    def mutate(self, info, id):
        user = info.context.user
        ctx = BestiaryContext(user)

        # Forcing this conversion explicitly, as input value is taken as a string
        id_value = int(id)

        ecosystem = delete_ecosystem(ctx, id_value)

        return DeleteEcosystem(
            ecosystem=ecosystem
        )


class BestiaryQuery(graphene.ObjectType):
    """Queries supported by Bestiary"""

    ecosystems = graphene.Field(
        EcosystemPaginatedType,
        page_size=graphene.Int(),
        page=graphene.Int(),
        filters=EcosystemFilterType(required=False)
    )
    transactions = graphene.Field(
        TransactionPaginatedType,
        page_size=graphene.Int(),
        page=graphene.Int(),
        filters=TransactionFilterType(required=False)
    )
    operations = graphene.Field(
        OperationPaginatedType,
        page_size=graphene.Int(),
        page=graphene.Int(),
        filters=OperationFilterType(required=False),
    )

    @check_auth
    def resolve_ecosystems(self, info, filters=None,
                           page=1,
                           page_size=settings.DEFAULT_GRAPHQL_PAGE_SIZE,
                           **kwargs):
        query = Ecosystem.objects.order_by('name')

        if filters and 'id' in filters:
            query = query.filter(id=filters['id'])
        if filters and 'name' in filters:
            query = query.filter(name=filters['name'])

        return EcosystemPaginatedType.create_paginated_result(query,
                                                              page,
                                                              page_size=page_size)

    @check_auth
    def resolve_transactions(self, info, filters=None,
                             page=1,
                             page_size=settings.DEFAULT_GRAPHQL_PAGE_SIZE,
                             **kwargs):
        query = Transaction.objects.order_by('created_at')

        if filters and 'tuid' in filters:
            query = query.filter(tuid=filters['tuid'])
        if filters and 'name' in filters:
            query = query.filter(name=filters['name'])
        if filters and 'is_closed' in filters:
            query = query.filter(is_closed=filters['isClosed'])
        if filters and 'from_date' in filters:
            query = query.filter(created_at__gte=filters['from_date'])
        if filters and 'to_date' in filters:
            query = query.filter(created_at__lte=filters['to_date'])
        if filters and 'authored_by' in filters:
            query = query.filter(authored_by=filters['authored_by'])

        return TransactionPaginatedType.create_paginated_result(query,
                                                                page,
                                                                page_size=page_size)

    @check_auth
    def resolve_operations(self, info, filters=None,
                           page=1,
                           page_size=settings.DEFAULT_GRAPHQL_PAGE_SIZE,
                           **kwargs):
        query = Operation.objects.order_by('timestamp')

        if filters and 'ouid' in filters:
            query = query.filter(ouid=filters['ouid'])
        if filters and 'op_type' in filters:
            query = query.filter(op_type=filters['op_type'])
        if filters and 'entity_type' in filters:
            query = query.filter(entity_type=filters['entity_type'])
        if filters and 'target' in filters:
            query = query.filter(target=filters['target'])
        if filters and 'from_date' in filters:
            query = query.filter(timestamp__gte=filters['from_date'])
        if filters and 'to_date' in filters:
            query = query.filter(timestamp__lte=filters['to_date'])

        return OperationPaginatedType.create_paginated_result(query,
                                                              page,
                                                              page_size=page_size)


class BestiaryMutation(graphene.ObjectType):
    """Mutations supported by Bestiary"""
    add_ecosystem = AddEcosystem.Field()
    update_ecosystem = UpdateEcosystem.Field()
    delete_ecosystem = DeleteEcosystem.Field()

    # JWT authentication
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
