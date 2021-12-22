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

import django.db.transaction

from .db import (find_ecosystem,
                 find_project,
                 add_ecosystem as add_ecosystem_db,
                 add_project as add_project_db,
                 update_ecosystem as update_ecosystem_db,
                 update_project as update_project_db,
                 delete_ecosystem as delete_ecosystem_db,
                 delete_project as delete_project_db,
                 link_parent_project as link_parent_project_db,
                 find_datasource_uri as find_datasource_uri_db,
                 add_datasource as add_datasource_db,
                 add_dataset as add_dataset_db,
                 add_credential as add_credential_db,
                 find_dataset as find_dataset_db,
                 find_datasource_type as find_datasource_type_db,
                 find_credential as find_credential_db,
                 delete_dataset as delete_dataset_db,
                 delete_datasource as delete_datasource_db,
                 delete_credential as delete_credential_db,
                 archive_dataset as archive_dataset_db,
                 unarchive_dataset as unarchive_dataset_db)
from .errors import AlreadyExistsError, InvalidValueError, NotFoundError
from .log import TransactionsLog


@django.db.transaction.atomic
def add_ecosystem(ctx, name, title=None, description=None):
    """Add an ecosystem to the registry.

    This function adds an ecosystem to the registry.
    It checks first whether the ecosystem is already on the registry.
    When it is not found, the new ecosystem is added. Otherwise,
    it raises a 'AlreadyExistsError' exception to notify that the ecosystem
    already exists.

    :param ctx: context from where this method is called
    :param name: name of the ecosystem
    :param title: title of the ecosystem
    :param description: description of the ecosystem

    :raises InvalidValueError: raised when name is None or an empty string
    :raises TypeError: raised when name is not a string or a NoneType
    :raises AlreadyExistsError: raised when the ecosystem already exists
        in the registry
    """
    if name is None:
        raise InvalidValueError(msg="'name' cannot be None")
    if name == '':
        raise InvalidValueError(msg="'name' cannot be an empty string")
    if title == '':
        raise InvalidValueError(msg="'title' cannot be an empty string")
    if description == '':
        raise InvalidValueError(msg="'description' cannot be an empty string")

    trxl = TransactionsLog.open('add_ecosystem', ctx)

    try:
        ecosystem = add_ecosystem_db(trxl,
                                     name=name,
                                     title=title,
                                     description=description)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except AlreadyExistsError as exc:
        raise exc

    trxl.close()

    return ecosystem


@django.db.transaction.atomic
def add_project(ctx, ecosystem_id, name, title=None, parent_id=None):
    """Add a project to the registry.

    This function adds a project to the registry.
    It checks first whether the project is already on the registry.
    When it is not found, the new project is added. Otherwise,
    it raises a 'AlreadyExistsError' exception to notify that the project
    already exists.

    :param ctx: context from where this method is called
    :param ecosystem_id: ID of the ecosystem where this project belongs to
    :param name: name of the project
    :param title: title of the project
    :param parent_id: ID of the parent project to be set to the new project

    :raises InvalidValueError: raised when name is None or an empty string
        or when the parent project to be set is invalid
    :raises TypeError: raised when name is not a string or a NoneType
    :raises AlreadyExistsError: raised when the project already exists
        in the registry
    """
    if name is None:
        raise InvalidValueError(msg="'name' cannot be None")
    if ecosystem_id is None:
        raise InvalidValueError(msg="'ecosystem_id' cannot be None")
    if name == '':
        raise InvalidValueError(msg="'name' cannot be an empty string")
    if title == '':
        raise InvalidValueError(msg="'title' cannot be an empty string")

    trxl = TransactionsLog.open('add_project', ctx)

    try:
        ecosystem = find_ecosystem(ecosystem_id)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except NotFoundError as exc:
        raise exc

    try:
        parent = find_project(parent_id) if parent_id else None
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except NotFoundError as exc:
        raise exc

    try:
        project = add_project_db(trxl,
                                 ecosystem,
                                 name,
                                 title=title,
                                 parent=parent)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except AlreadyExistsError as exc:
        raise exc

    trxl.close()

    return project


@django.db.transaction.atomic
def add_datasets(ctx, project_id, datasource_name, datasets):
    """Add datasets to the registry

    This functions adds a list of datasets to the registry.
    All datasets have in common that are from the same datasource type
    and inserted in the same project.

    :param ctx: context from where this method is called
    :param project_id: ID of the project where this dataset belongs to
    :param datasource_name: name of the type of data source
    :param datasets: uri, category and filters for the datasets

    :returns: list of datasets inserted
    """
    trxl = TransactionsLog.open('add_datasets', ctx)

    if project_id is None:
        raise InvalidValueError(msg="'project_id' cannot be None")
    if datasource_name is None:
        raise InvalidValueError(msg="'datasource_name' cannot be None")
    if datasets is None:
        raise InvalidValueError(msg="'datasets' cannot be None")

    datasource_type = find_datasource_type_db(name=datasource_name)
    project = find_project(project_id)

    added = []
    exception = None

    for dataset in datasets:
        try:
            datasource = find_datasource_uri_db(datasource_type, dataset['uri'])
        except NotFoundError:
            datasource = add_datasource_db(trxl, datasource_type, dataset['uri'])

        try:
            new_dataset = add_dataset_db(trxl, project, datasource, dataset['category'], dataset['filters'])
            added.append(new_dataset)
        except ValueError as e:
            exception = InvalidValueError(msg=str(e))
            continue
        except AlreadyExistsError as exc:
            exception = exc
            continue

    if exception:
        raise exception

    trxl.close()

    return added


@django.db.transaction.atomic
def add_dataset(ctx, project_id, datasource_name, uri, category, filters):
    """Add a data set to the registry.

    This function adds a data set to the registry.
    It checks first whether the project and data source are already
    on the registry.
    When they are found, a new dataset is added. In case it is duplicated
    it raises a 'AlreadyExistsError' exception to notify that it
    already exists.

    :param ctx: context from where this method is called
    :param project_id: ID of the project where this dataset belongs to
    :param datasource_name: name of the type of data source
    :param uri: uri of data source
    :param category: type of data source analysis
    :param filters: attributes to filter the view of the data source

    :returns: a new data set

    :raises ValueError: when any of the arguments is empty or not valid
    :raises AlreadyExistsError: raised when the dataset already exists
        in the registry
    """
    trxl = TransactionsLog.open('add_dataset', ctx)

    if project_id is None:
        raise InvalidValueError(msg="'project_id' cannot be None")
    if datasource_name is None:
        raise InvalidValueError(msg="'datasource_name' cannot be None")
    if uri is None:
        raise InvalidValueError(msg="'uri' cannot be None")
    if uri == '':
        raise InvalidValueError(msg="'uri' cannot be an empty string")
    if category is None:
        raise InvalidValueError(msg="'category' cannot be None")
    if filters is None:
        raise InvalidValueError(msg="'filters' cannot be None")

    try:
        datasource_type = find_datasource_type_db(name=datasource_name)
    except NotFoundError as exc:
        raise exc

    project = find_project(project_id)
    try:
        datasource = find_datasource_uri_db(datasource_type, uri)
    except NotFoundError:
        datasource = add_datasource_db(trxl, datasource_type, uri)

    try:
        dataset = add_dataset_db(trxl, project, datasource, category, filters)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except AlreadyExistsError as exc:
        raise exc

    trxl.close()

    return dataset


@django.db.transaction.atomic
def add_credential(ctx, user, name, datasource_name, token):
    """Add a new credential to the registry.

    This function adds a credential to the registry.
    It checks first whether the user and datasource are already
    on the registry.
    When they are found, a new credential is added. In case it is duplicated
    it raises a 'AlreadyExistsError' exception to notify that it
    already exists.

    :param ctx: context from where this method is called
    :param user: user this credential belongs to
    :param name: name for the credential
    :param datasource_name: name of the type of data source
    :param token: code that contains authentication for the datasource

    :returns: a credential object

    :raises ValueError: when any of the arguments is empty or not valid
    :raises AlreadyExistsError: raised when the dataset already exists
        in the registry
    """
    trxl = TransactionsLog.open('add_credential', ctx)

    if not user:
        raise InvalidValueError(msg="'user' cannot be None")
    if not user.is_authenticated:
        raise InvalidValueError(msg="Unauthenticated user cannot add credentials")
    if name is None:
        raise InvalidValueError(msg="'name' cannot be None")
    if name == '':
        raise InvalidValueError(msg="'name' cannot be an empty string")
    if not datasource_name:
        raise InvalidValueError(msg="'datasource_name' cannot be empty")
    if not token:
        raise InvalidValueError(msg="'token' cannot be empty")

    try:
        datasource_type = find_datasource_type_db(name=datasource_name)
    except NotFoundError as exc:
        raise exc

    try:
        credential = add_credential_db(trxl, user, name, datasource_type, token)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except AlreadyExistsError as exc:
        raise exc

    trxl.close()

    return credential


@django.db.transaction.atomic
def update_ecosystem(ctx, ecosystem_id, **kwargs):
    """Update an ecosystem.

    This function allows to edit or update the ecosystem information
    of the `Ecosystem` object identified by `id`.

    The values to update are given as keyword arguments. The allowed
    keys are listed below (other keywords will be ignored):

       - `name`: unique name of the ecosystem
       - `title`: title of the ecosystem
       - `description`: description of the ecosystem

    The result of calling this function will be the updated
    `Ecosystem` object.

    :param ctx: context from where this method is called
    :param ecosystem_id: identifier of the ecosystem to be updated
    :param kwargs: keyword arguments with data to update the ecosystem

    :returns: an updated ecosystem

    :raises NotFoundError: raised when either ecosystem do not exist in
        the registry.
    :raises InvalidValueError: raised when any of the keyword arguments
        has an invalid value.
    """
    if ecosystem_id is None:
        raise InvalidValueError(msg="'ecosystem_id' cannot be None")

    trxl = TransactionsLog.open('update_ecosystem', ctx)

    ecosystem = find_ecosystem(ecosystem_id)

    try:
        ecosystem = update_ecosystem_db(trxl, ecosystem, **kwargs)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))

    trxl.close()

    return ecosystem


@django.db.transaction.atomic
def update_project(ctx, project_id, **kwargs):
    """Update the information of a given project.

    This function allows to edit or update the project information
    of the `Project` object identified by `id`.

    The values to update are given as keyword arguments. The allowed
    keys are listed below (other keywords will be ignored):

       - `name`: unique name of the project
       - `title`: title of the project

    The result of calling this function will be the updated
    `Project` object.

    :param ctx: context from where this method is called
    :param project_id: identifier of the project to be updated
    :param kwargs: keyword arguments with data to update the project

    :returns: an updated project

    :raises NotFoundError: raised when either project do not exist in
        the registry.
    :raises InvalidValueError: raised when any of the keyword arguments
        has an invalid value.
    """
    if project_id is None:
        raise InvalidValueError(msg="'project_id' cannot be None")

    trxl = TransactionsLog.open('update_project', ctx)

    project = find_project(project_id)

    try:
        project = update_project_db(trxl, project, **kwargs)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))

    trxl.close()

    return project


@django.db.transaction.atomic
def delete_ecosystem(ctx, ecosystem_id):
    """Remove an ecosystem from the registry.

    This function removes the given ecosystem from the registry.
    It checks first whether the ecosystem is already on the registry.
    When it is found, the ecosystem is removed. Otherwise,
    it will raise a 'NotFoundError'.

    :param ctx: context from where this method is called
    :param ecosystem_id: id of the ecosystem to remove

    :raises InvalidValueError: raised when ecosystem is None or an empty string
    :raises NotFoundError: raised when the ecosystem does not exist
        in the registry
    """
    if ecosystem_id is None:
        raise InvalidValueError(msg="'ecosystem_id' cannot be None")

    trxl = TransactionsLog.open('delete_ecosystem', ctx)

    try:
        ecosystem = find_ecosystem(ecosystem_id)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except NotFoundError as exc:
        raise exc

    delete_ecosystem_db(trxl, ecosystem=ecosystem)

    trxl.close()

    # Setting former ID manually, as it can't be referenced once it has been removed
    ecosystem.id = ecosystem_id

    return ecosystem


@django.db.transaction.atomic
def delete_project(ctx, project_id):
    """Remove a project from the registry.

    This function removes the given project from the registry.
    It checks first whether the project is already on the registry.
    When it is found, the project is removed. Otherwise,
    it will raise a 'NotFoundError'.

    :param ctx: context from where this method is called
    :param project_id: id of the project to remove

    :raises InvalidValueError: raised when project is None or an empty string
    :raises NotFoundError: raised when the project does not exist
        in the registry
    """
    if project_id is None:
        raise InvalidValueError(msg="'project_id' cannot be None")

    trxl = TransactionsLog.open('delete_project', ctx)

    try:
        project = find_project(project_id)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except NotFoundError as exc:
        raise exc

    delete_project_db(trxl, project=project)

    trxl.close()

    # Setting former ID manually, as it can't be referenced once it has been removed
    project.id = project_id

    return project


@django.db.transaction.atomic
def delete_dataset(ctx, dataset_id):
    """Remove a dataset from the registry.

    This function removes the given dataset from the registry.
    It checks first whether the dataset is already on the registry.
    When it is found, the dataset is removed. Otherwise,
    it will raise a 'NotFoundError'.
    It also removes a datasource when it is not linked with any dataset.

    :param ctx: context from where this method is called
    :param dataset_id: id of the dataset to remove

    :raises InvalidValueError: raised when dataset_id is None
    :raises NotFoundError: raised when the dataset does not exist
        in the registry
    """
    if dataset_id is None:
        raise InvalidValueError(msg="'dataset_id' cannot be None")

    trxl = TransactionsLog.open('delete_dataset', ctx)

    try:
        dataset = find_dataset_db(dataset_id)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except NotFoundError as exc:
        raise exc

    delete_dataset_db(trxl, dataset=dataset)

    # Check if the related data source has no data set associated
    if not dataset.datasource.dataset_set.exists():
        delete_datasource_db(trxl, dataset.datasource)

    trxl.close()

    # Setting former ID manually, as it can't be referenced once it has been removed
    dataset.id = dataset_id

    return dataset


@django.db.transaction.atomic
def delete_credential(ctx, user, credential_id):
    """A user removes a credential from the registry.

    This function removes the given credential from the registry.
    It checks first whether the credential is already on the registry.
    When it is found, check if the user is the owner of the credencial,
    if so, the credential is removed. Otherwise, it will raise
    a 'NotFoundError'.

    :param ctx: context from where this method is called
    :param user: user asking to remove the credential
    :param credential_id: id of the credential to remove

    :raises InvalidValueError: raised when credential_id is None
    :raises NotFoundError: raised when the credential does not exist
        in the registry
    """
    if credential_id is None:
        raise InvalidValueError(msg="'credential_id' cannot be None")

    trxl = TransactionsLog.open('delete_credential', ctx)

    try:
        credential = find_credential_db(credential_id)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except NotFoundError as exc:
        raise exc

    if credential.user == user:
        delete_credential_db(trxl, credential=credential)
    else:
        raise PermissionError("User not allowed to remove credential ID {}.".format(credential_id))

    trxl.close()

    # Setting former ID manually, as it can't be referenced once it has been removed
    credential.id = credential_id

    return credential


@django.db.transaction.atomic
def move_project(ctx, from_project_id, to_project_id):
    """Move a project to a parent project.

    Link a project with another one with a child-parent relation. If a project
    is not linked to any project, it is a root project.
    If the source project was already linked to a parent project, it will be
    overwritten.

    :param ctx: context from where this method is called
    :param from_project_id: Project to be linked to another project or to an ecosystem
    :param to_project_id: Destination project which will be linked as a parent project

    :returns: the updated project object

    :raises InvalidValueError: raised when from_project_id is None or any of the
        other IDs are invalid, or when the parent project to be set is invalid
    :raises NotFoundError: raised when the any of the projects or the ecosystem
        do not exist in the registry
    """
    if from_project_id is None:
        raise InvalidValueError(msg="'from_project_id' cannot be None")

    trxl = TransactionsLog.open('move_project', ctx)

    try:
        from_project = find_project(from_project_id)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except NotFoundError as exc:
        raise exc

    try:
        to_project = find_project(to_project_id) if to_project_id else None
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except NotFoundError as exc:
        raise exc

    from_project = link_parent_project_db(trxl, from_project, to_project)

    return from_project


@django.db.transaction.atomic
def archive_dataset(ctx, dataset_id):
    """Archive a dataset.

    This function archives the given dataset.
    It checks first whether the dataset is on the registry.
    When it is found, the dataset is archived. Otherwise,
    it will raise a 'NotFoundError'.

    :param ctx: context from where this method is called
    :param dataset_id: id of the dataset to archive

    :raises InvalidValueError: raised when dataset_id is None
    :raises NotFoundError: raised when the dataset does not exist
        in the registry
    """
    if dataset_id is None:
        raise InvalidValueError(msg="'dataset_id' cannot be None")

    trxl = TransactionsLog.open('archive_dataset', ctx)

    try:
        dataset = find_dataset_db(dataset_id)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except NotFoundError as exc:
        raise exc

    dataset_archived = archive_dataset_db(trxl, dataset=dataset)

    trxl.close()

    return dataset_archived


@django.db.transaction.atomic
def unarchive_dataset(ctx, dataset_id):
    """Unarchive a dataset.

    This function unarchives the given dataset.
    It checks first whether the dataset is on the registry.
    When it is found, the dataset is unarchived. Otherwise,
    it will raise a 'NotFoundError'.

    :param ctx: context from where this method is called
    :param dataset_id: id of the dataset to unarchive

    :raises InvalidValueError: raised when dataset_id is None
    :raises NotFoundError: raised when the dataset does not exist
        in the registry
    """
    if dataset_id is None:
        raise InvalidValueError(msg="'dataset_id' cannot be None")

    trxl = TransactionsLog.open('unarchive_dataset', ctx)

    try:
        dataset = find_dataset_db(dataset_id)
    except ValueError as e:
        raise InvalidValueError(msg=str(e))
    except NotFoundError as exc:
        raise exc

    dataset_unarchived = unarchive_dataset_db(trxl, dataset=dataset)

    trxl.close()

    return dataset_unarchived
