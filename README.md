# Bestiary [![Build Status](https://github.com/chaoss/grimoirelab-bestiary/workflows/tests/badge.svg?branch=unicorn)](https://github.com/chaoss/grimoirelab-bestiary/actions?query=workflow:tests+branch:unicorn+event:push)

**Warning**: This is the developing branch of the new version of Bestiary. We're moving Bestiary into a service.
The documentation below would be totally incorrect or inaccurate. 

A tool to visually manage software development ecosystems description.

## Concepts

A software development **ecosystem** can be described as a set of software development **projects**. Each project, is defined by a set of **data sources** (git, issue tracking system, mailing list, etc.) with some specific parameters each (url, filters, etc.), that we would call **repository views**, or just **repositories**.

Bestiary is a tool to manage this kind of description using a web based interface.

It also provides an interface to connect with [GrimoireLab](http://grimoirelab.github.io) to work as analytics scope manager.


## Requirements

- Python >= 3.6
- Poetry >= 1.1.0
- MySQL >= 5.7 or MariaDB >= 10.2
- Django = 3.1
- Graphene-Django >= 2.0
- Django-graphql-jwt
- uWSGI >= 2.0

You will also need some other libraries for running the tool, you can find the whole list of dependencies in [pyproject.toml](pyproject.toml) file.

## Installation

### Getting the source code

Clone the repository, and change to the `unicorn` branch

```
$ git clone https://github.com/chaoss/grimoirelab-bestiary
$ git checkout unicorn
```

### Backend

#### Prerequisites

##### Poetry

We use [Poetry](https://python-poetry.org/docs/) for managing the project.
You can install it following [these steps](https://python-poetry.org/docs/#installation).

##### mysql_config

Before you install Bestiary tool you might need to install `mysql_config`
command. If you are using a Debian based distribution, this command can be
found either in `libmysqlclient-dev` or `libmariadbclient-dev` packages
(depending on if you are using MySQL or MariaDB database server). You can
install these packages in your system with the next commands:

* **MySQL**

```
$ apt install libmysqlclient-dev
```

* **MariaDB**

```
$ apt install libmariadbclient-dev
```

#### Installation and configuration

Install the required dependencies (this will also create a virtual environment).
```
$ poetry install
```

Activate the virtual environment:
```
$ poetry shell
```

Migrations, and create a superuser:
```
(.venv)$ ./manage.py migrate --settings=config.settings.devel
(.venv)$ ./manage.py createsuperuser --settings=config.settings.devel
```

#### Running the backend

Run Bestiary backend Django app:
```
(.venv)$ ./manage.py runserver --settings=config.settings.devel
```

### Frontend

#### Prerequisites

##### yarn

To compile and run the frontend you will need to install `yarn` first.
The latest versions of `yarn` can only be installed with `npm` - which
is distributed with [NodeJS](https://nodejs.org/en/download/).

When you have `npm` installed, then run the next command to install `yarn`
on the system:

```
npm install -g yarn
```

Check the [official documentation](https://yarnpkg.com/getting-started)
for more information.

#### Installation and configuration

Install the required dependencies
```
$ cd ui/
$ yarn install
```

#### Running the frontend

Run Bestiary frontend Vue app:
```
$ yarn serve
```


## Bestiary service

Bestiary is released with a server app. The server has two
modes, `production` and `development`.

When `production` mode is active, a WSGI app is served. The idea is to use a reverse
proxy like NGINX or similar, that will be connected with the WSGI app to provide
an interface HTTP.

When `development` mode is active, an HTTP server is launched, so you can interact
directly with Bestiary using HTTP requests. Take into account this mode is not
suitable nor safe for production.


In order to run the service for the first time, you need to execute the next commands:

Build the UI interface:
```
$ cd ui
$ yarn build
```

Copy the static files to the location where they will be served (`STATIC_ROOT` var):
```
$ ./manage.py collectstatic --settings=config.settings.devel
```

Run the server (use `--dev` flag for `development` mode):
```
$ bestiaryd --config config.settings.devel
```

By default, this runs a WSGI server in `127.0.0.1:9314`. The `--dev` flag runs
a server in `127.0.0.1:8000`.


## Running tests

Bestiary comes with a comprehensive list of unit tests for both 
frontend and backend.

#### Backend test suite
```
(.venv)$ ./manage.py test --settings=config.settings.testing
```

#### Frontend test suite
```
$ cd ui/
$ yarn test:unit
```

## License

Licensed under GNU General Public License (GPL), version 3 or later.
