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
from django.core.exceptions import PermissionDenied
from django.db.models import Q, JSONField
from django_rq import enqueue

from graphene.types.generic import GenericScalar

from graphene_django.converter import convert_django_field
from graphene_django.types import DjangoObjectType

from .api import (add_ecosystem,
                  add_project,
                  add_dataset,
                  add_datasets,
                  add_credential,
                  update_ecosystem,
                  update_project,
                  delete_ecosystem,
                  delete_project,
                  delete_dataset,
                  delete_credential,
                  move_project,
                  archive_dataset,
                  unarchive_dataset)
from .context import BestiaryContext
from .decorators import check_auth
from .models import (Ecosystem,
                     Project,
                     DataSet,
                     Credential,
                     Transaction,
                     Operation,
                     DataSourceType,
                     DataSource)
from .jobs import (find_job,
                   get_jobs,
                   fetch_github_owner_repos,
                   fetch_gitlab_owner_repos)


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


class ProjectType(DjangoObjectType):
    """Project objects are meant to group a set of data locations"""

    class Meta:
        model = Project


class DatasetInputType(graphene.InputObjectType):
    """Dataset objects are meant to define a data source analysis"""
    uri = graphene.String()
    category = graphene.String()
    filters = graphene.JSONString()


class DatasetType(DjangoObjectType):
    """Dataset objects are meant to define a data source analysis"""

    class Meta:
        model = DataSet


class CredentialType(DjangoObjectType):
    """Credential objects are meant to define an authentication code for a datasource"""

    class Meta:
        model = Credential


class DataSourceTypeModelType(DjangoObjectType):
    class Meta:
        model = DataSourceType


class DataSourceModelType(DjangoObjectType):
    class Meta:
        model = DataSource


class GitHubRepoResultType(graphene.ObjectType):
    url = graphene.String(description='URL of the repository.')
    fork = graphene.Boolean(description='Whether the repository is a fork or not.')
    has_issues = graphene.Boolean(description='Whether the repository has issues or not.')


class GitLabRepoResultType(graphene.ObjectType):
    url = graphene.String(description='URL of the repository.')
    fork = graphene.Boolean(description='Whether the repository is a fork or not.')
    has_issues = graphene.Boolean(description='Whether the repository has issues or not.')


class JobResultType(graphene.Union):
    class Meta:
        types = (GitHubRepoResultType, GitLabRepoResultType)


class JobType(graphene.ObjectType):
    job_id = graphene.String(description='Job identifier.')
    job_type = graphene.String(description='Type of job.')
    status = graphene.String(description='Job status (`started`, `deferred`, `finished`, `failed` or `scheduled`).')
    result = graphene.List(JobResultType, description='List of job results.')
    errors = graphene.List(graphene.String, description='List of errors.')
    enqueued_at = graphene.DateTime(description='Time the job was enqueued at.')


class EcosystemInputType(graphene.InputObjectType):
    """Fields which can be used as an input for Ecosystem-related mutations"""

    name = graphene.String(
        required=False,
        description="Ecosystem name.")
    title = graphene.String(
        required=False,
        description="Ecosystem title.")
    description = graphene.String(
        required=False,
        description="Brief text describing the ecosystem.")


class ProjectInputType(graphene.InputObjectType):
    """Fields which can be used as an input for Project-related mutations"""

    name = graphene.String(
        required=False,
        description="Project name.")
    title = graphene.String(
        required=False,
        description="Project title.")
    parent_project = graphene.ID(
        required=False,
        description="Parent project identifier.")


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

    id = graphene.ID(
        required=False,
        description="Find an ecosystem by its unique identifier.")
    name = graphene.String(
        required=False,
        description="Find an ecosystem by its unique name.")


class ProjectFilterType(graphene.InputObjectType):
    """Fields which can be used as a filter for ProjectPaginatedType objects"""

    id = graphene.ID(
        required=False,
        description="Find a project by its unique identifier.")
    name = graphene.String(
        required=False,
        description="Find a project by its unique name.")
    ecosystem_id = graphene.ID(
        required=False,
        description="Filter projects belonging to this ecosystem.")
    has_parent = graphene.Boolean(
        required=False,
        description="Filter projects that have parent.")
    term = graphene.String(
        required=False,
        description="Filter projects whose name or title include the term.")
    title = graphene.String(
        required=False,
        description="Filter projects with this title.")


class DatasetFilterType(graphene.InputObjectType):
    """Fields which can be used as a filter for DatasetPaginatedType objects"""

    id = graphene.ID(
        required=False,
        description="Find a dataset by its unique identifier.")
    project_id = graphene.ID(
        required=False,
        description="Filter datasets belonging to this project.")
    datasource_name = graphene.String(
        required=False,
        description="Filter datasets using the name of the datasource.")
    uri = graphene.String(
        required=False,
        description="Filter datasets using the uri of the datasource.")
    category = graphene.String(
        required=False,
        description="Filter datasets by category.")
    is_archived = graphene.Boolean(
        required=False,
        description="Filter datasets by archived status.")


class CredentialFilterType(graphene.InputObjectType):
    """Fields which can be used as a filter for CredentialPaginatedType objects"""

    id = graphene.ID(
        required=False,
        description="Find a credential by its unique identifier.")
    name = graphene.String(
        required=False,
        description="Find a credential by its name."
    )
    datasource_name = graphene.ID(
        required=False,
        description="Filter credential using the name of the datasource.")


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


class ProjectPaginatedType(AbstractPaginatedType):
    """Type returning paginated results of ProjectType objects"""

    entities = graphene.List(ProjectType)
    page_info = graphene.Field(PaginationType)


class DatasetPaginatedType(AbstractPaginatedType):
    """Type returning paginated results of Dataset objects"""

    entities = graphene.List(DatasetType)
    page_info = graphene.Field(PaginationType)


class CredentialPaginatedType(AbstractPaginatedType):
    """Type returning paginated results of Credentials objects"""

    entities = graphene.List(CredentialType)
    page_info = graphene.Field(PaginationType)


class JobPaginatedType(AbstractPaginatedType):
    entities = graphene.List(JobType, description='A list of jobs.')
    page_info = graphene.Field(PaginationType, description='Information to aid in pagination.')


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


class AddProject(graphene.Mutation):
    """Mutation which adds a new Project on the registry"""

    class Arguments:
        ecosystem_id = graphene.ID()
        name = graphene.String()
        title = graphene.String(required=False)
        parent_id = graphene.ID(required=False)

    project = graphene.Field(lambda: ProjectType)

    @check_auth
    def mutate(self, info, ecosystem_id, name, title=None, parent_id=None):
        user = info.context.user
        ctx = BestiaryContext(user)

        ecosystem_id_value = int(ecosystem_id) if ecosystem_id else None
        parent_id_value = int(parent_id) if parent_id else None

        project = add_project(ctx, ecosystem_id_value, name, title, parent_id_value)

        return AddProject(
            project=project
        )


class AddDataset(graphene.Mutation):
    """Mutation which adds a new Dataset on the registry"""

    class Arguments:
        project_id = graphene.ID()
        datasource_name = graphene.String()
        uri = graphene.String()
        category = graphene.String()
        filters = graphene.JSONString()

    dataset = graphene.Field(lambda: DatasetType)

    @check_auth
    def mutate(self, info, project_id, datasource_name, uri, category, filters):
        user = info.context.user
        ctx = BestiaryContext(user)

        project_id_value = int(project_id) if project_id else None

        dataset = add_dataset(ctx, project_id_value, datasource_name,
                              uri, category, filters)

        return AddDataset(
            dataset=dataset
        )


class AddDatasets(graphene.Mutation):
    """Mutation which adds a new Dataset on the registry"""

    class Arguments:
        project_id = graphene.ID()
        datasource_name = graphene.String()
        datasets = graphene.List(DatasetInputType)

    datasets = graphene.List(lambda: DatasetType)

    @check_auth
    def mutate(self, info, project_id, datasource_name, datasets):
        user = info.context.user
        ctx = BestiaryContext(user)

        datasets = add_datasets(ctx, project_id, datasource_name, datasets)

        return AddDatasets(
            datasets=datasets
        )


class AddCredential(graphene.Mutation):
    """Mutation which adds a new Credential on the registry"""

    class Arguments:
        name = graphene.String()
        datasource_name = graphene.String()
        token = graphene.String()

    credential = graphene.Field(lambda: CredentialType)

    @check_auth
    def mutate(self, info, name, datasource_name, token):
        user = info.context.user
        ctx = BestiaryContext(user)

        credential = add_credential(ctx, user, name, datasource_name, token)

        return AddCredential(
            credential=credential
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


class UpdateProject(graphene.Mutation):
    """Mutation which updates an existing Project"""

    class Arguments:
        id = graphene.ID()
        data = ProjectInputType()

    project = graphene.Field(lambda: ProjectType)

    @check_auth
    def mutate(self, info, id, data):
        user = info.context.user
        ctx = BestiaryContext(user)

        # Forcing this conversion explicitly, as input value is taken as a string
        id_value = int(id)

        project = update_project(ctx, id_value, **data)

        return UpdateProject(
            project=project
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


class DeleteProject(graphene.Mutation):
    """Mutation which deletes an existing Project from the registry"""

    class Arguments:
        id = graphene.ID()

    project = graphene.Field(lambda: ProjectType)

    @check_auth
    def mutate(self, info, id):
        user = info.context.user
        ctx = BestiaryContext(user)

        # Forcing this conversion explicitly, as input value is taken as a string
        id_value = int(id)

        project = delete_project(ctx, id_value)

        return DeleteProject(
            project=project
        )


class DeleteDataset(graphene.Mutation):
    """Mutation which deletes an existing data set from the registry"""

    class Arguments:
        id = graphene.ID()

    dataset = graphene.Field(lambda: DatasetType)

    @check_auth
    def mutate(self, info, id):
        user = info.context.user
        ctx = BestiaryContext(user)

        # Forcing this conversion explicitly, as input value is taken as a string
        id_value = int(id)

        dataset = delete_dataset(ctx, id_value)

        return DeleteDataset(
            dataset=dataset
        )


class DeleteCredential(graphene.Mutation):
    """Mutation which deletes an existing credential from the registry"""

    class Arguments:
        id = graphene.ID()

    credential = graphene.Field(lambda: CredentialType)

    @check_auth
    def mutate(self, info, id):
        user = info.context.user
        ctx = BestiaryContext(user)

        # Forcing this conversion explicitly, as input value is taken as a string
        id_value = int(id)

        credential = delete_credential(ctx, user, id_value)

        return DeleteCredential(
            credential=credential
        )


class MoveProject(graphene.Mutation):
    """Mutation which can move a project to a parent project"""

    class Arguments:
        from_project_id = graphene.ID()
        to_project_id = graphene.ID()

    project = graphene.Field(lambda: ProjectType)

    @check_auth
    def mutate(self, info, from_project_id, to_project_id=None):
        user = info.context.user
        ctx = BestiaryContext(user)

        # Forcing this conversion explicitly, as input value is taken as a string
        from_project_id_value = int(from_project_id)
        to_project_id_value = int(to_project_id) if to_project_id else None

        project = move_project(ctx,
                               from_project_id_value,
                               to_project_id=to_project_id_value)

        return MoveProject(
            project=project
        )


class ArchiveDataset(graphene.Mutation):
    """Mutation which archives an existing dataset from the registry"""

    class Arguments:
        id = graphene.ID()

    dataset = graphene.Field(lambda: DatasetType)

    @check_auth
    def mutate(self, info, id):
        user = info.context.user
        ctx = BestiaryContext(user)

        # Forcing this conversion explicitly, as input value is taken as a string
        id_value = int(id)

        dataset = archive_dataset(ctx, id_value)

        return ArchiveDataset(
            dataset=dataset
        )


class UnarchiveDataset(graphene.Mutation):
    """Mutation which unarchives an existing dataset from the registry"""

    class Arguments:
        id = graphene.ID()

    dataset = graphene.Field(lambda: DatasetType)

    @check_auth
    def mutate(self, info, id):
        user = info.context.user
        ctx = BestiaryContext(user)

        # Forcing this conversion explicitly, as input value is taken as a string
        id_value = int(id)

        dataset = unarchive_dataset(ctx, id_value)

        return UnarchiveDataset(
            dataset=dataset
        )


class GitHubOwnerRepos(graphene.Mutation):
    class Arguments:
        owner = graphene.String()

    job_id = graphene.Field(lambda: graphene.String)

    @check_auth
    def mutate(self, info, owner):
        user = info.context.user
        ctx = BestiaryContext(user)

        api_token = None
        if user.is_authenticated:
            credential = Credential.objects.filter(user=user,
                                                   datasource__name='GitHub').first()
            if credential:
                api_token = credential.token

        job = enqueue(fetch_github_owner_repos, ctx, owner, api_token)

        return GitHubOwnerRepos(
            job_id=job.id
        )


class GitLabOwnerRepos(graphene.Mutation):
    class Arguments:
        owner = graphene.String()

    job_id = graphene.Field(lambda: graphene.String)

    @check_auth
    def mutate(self, info, owner):
        user = info.context.user
        ctx = BestiaryContext(user)

        api_token = None
        if user.is_authenticated:
            credential = Credential.objects.filter(user=user,
                                                   datasource__name='GitLab').first()
            if credential:
                api_token = credential.token

        job = enqueue(fetch_gitlab_owner_repos, ctx, owner, api_token)

        return GitLabOwnerRepos(
            job_id=job.id
        )


class BestiaryQuery(graphene.ObjectType):
    """Queries supported by Bestiary"""

    ecosystems = graphene.Field(
        EcosystemPaginatedType,
        page_size=graphene.Int(),
        page=graphene.Int(),
        filters=EcosystemFilterType(required=False)
    )
    projects = graphene.Field(
        ProjectPaginatedType,
        page_size=graphene.Int(),
        page=graphene.Int(),
        filters=ProjectFilterType(required=False)
    )
    datasets = graphene.Field(
        DatasetPaginatedType,
        page_size=graphene.Int(),
        page=graphene.Int(),
        filters=DatasetFilterType(required=False)
    )
    credentials = graphene.Field(
        CredentialPaginatedType,
        page_size=graphene.Int(),
        page=graphene.Int(),
        filters=CredentialFilterType(required=False)
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
    job = graphene.Field(
        JobType,
        job_id=graphene.String(),
        description='Find a single job by its id.'
    )
    jobs = graphene.Field(
        JobPaginatedType,
        page_size=graphene.Int(),
        page=graphene.Int(),
        description='Get all jobs.'
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
    def resolve_projects(self, info, filters=None,
                         page=1,
                         page_size=settings.DEFAULT_GRAPHQL_PAGE_SIZE,
                         **kwargs):
        query = Project.objects.order_by('name')

        if filters and 'id' in filters:
            query = query.filter(id=filters['id'])
        if filters and 'name' in filters:
            query = query.filter(name=filters['name'])
        if filters and 'title' in filters:
            query = query.filter(title=filters['title'])
        if filters and 'ecosystem_id' in filters:
            query = query.filter(ecosystem__id=filters['ecosystem_id'])
        if filters and 'term' in filters:
            search_term = filters['term']
            query = query.filter(Q(name__icontains=search_term) |
                                 Q(title__icontains=search_term))

        return ProjectPaginatedType.create_paginated_result(query,
                                                            page,
                                                            page_size=page_size)

    @check_auth
    def resolve_datasets(self, info, filters=None,
                         page=1,
                         page_size=settings.DEFAULT_GRAPHQL_PAGE_SIZE,
                         **kwargs):
        query = DataSet.objects.order_by('id')

        if filters and 'id' in filters:
            query = query.filter(id=filters['id'])
        if filters and 'project_id' in filters:
            query = query.filter(project=filters['project_id'])
        if filters and 'datasource_name' in filters:
            query = query.filter(datasource__type=filters['datasource_name'])
        if filters and 'category' in filters:
            query = query.filter(category=filters['category'])
        if filters and 'uri' in filters:
            query = query.filter(datasource__uri=filters['uri'])
        if filters and 'is_archived' in filters:
            query = query.filter(is_archived=filters['is_archived'])

        return DatasetPaginatedType.create_paginated_result(query,
                                                            page,
                                                            page_size=page_size)

    @check_auth
    def resolve_credentials(self, info, filters=None,
                            page=1,
                            page_size=settings.DEFAULT_GRAPHQL_PAGE_SIZE,
                            **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("Unauthenticated user cannot get credentials")

        query = Credential.objects.order_by('id')
        query = query.filter(user=user)

        if filters and 'id' in filters:
            query = query.filter(id=filters['id'])
        if filters and 'name' in filters:
            query = query.filter(name__icontains=filters['name'])
        if filters and 'datasource_name' in filters:
            query = query.filter(datasource__name=filters['datasource_name'])

        return CredentialPaginatedType.create_paginated_result(query,
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

    @check_auth
    def resolve_job(self, info, job_id):
        job = find_job(job_id)

        status = job.get_status()
        job_type = job.func_name.split('.')[-1]
        enqueued_at = job.enqueued_at

        result = None
        errors = None

        if job.result and (job_type == 'fetch_github_owner_repos'):
            errors = job.result['errors']
            result = [
                GitHubRepoResultType(url=repo['url'], fork=repo['fork'], has_issues=repo['has_issues'])
                for repo in job.result['results']
            ]
        elif job.result and (job_type == 'fetch_gitlab_owner_repos'):
            errors = job.result['errors']
            result = [
                GitLabRepoResultType(url=repo['url'], fork=repo['fork'], has_issues=repo['has_issues'])
                for repo in job.result['results']
            ]
        if status == 'failed':
            errors = [job.exc_info]

        return JobType(job_id=job_id,
                       job_type=job_type,
                       status=status,
                       result=result,
                       errors=errors,
                       enqueued_at=enqueued_at)

    @check_auth
    def resolve_jobs(self, info, page=1, page_size=settings.DEFAULT_GRAPHQL_PAGE_SIZE):
        jobs = get_jobs()
        result = []

        for job in jobs:
            job_id = job.get_id()
            status = job.get_status()
            job_type = job.func_name.split('.')[-1]
            enqueued_at = job.enqueued_at

            result.append(JobType(job_id=job_id,
                                  job_type=job_type,
                                  status=status,
                                  result=[],
                                  errors=[],
                                  enqueued_at=enqueued_at))

        return JobPaginatedType.create_paginated_result(result,
                                                        page,
                                                        page_size=page_size)


class BestiaryMutation(graphene.ObjectType):
    """Mutations supported by Bestiary"""
    add_ecosystem = AddEcosystem.Field()
    add_project = AddProject.Field()
    add_dataset = AddDataset.Field()
    add_datasets = AddDatasets.Field()
    add_credential = AddCredential.Field()
    update_ecosystem = UpdateEcosystem.Field()
    update_project = UpdateProject.Field()
    delete_ecosystem = DeleteEcosystem.Field()
    delete_project = DeleteProject.Field()
    delete_dataset = DeleteDataset.Field()
    delete_credential = DeleteCredential.Field()
    move_project = MoveProject.Field()
    archive_dataset = ArchiveDataset.Field()
    unarchive_dataset = UnarchiveDataset.Field()
    fetch_github_owner_repos = GitHubOwnerRepos.Field()
    fetch_gitlab_owner_repos = GitLabOwnerRepos.Field()

    # JWT authentication
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
