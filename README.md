# Bestiary [![Build Status](https://github.com/chaoss/grimoirelab-bestiary/workflows/build/badge.svg)](https://github.com/chaoss/grimoirelab-bestiary/actions?query=workflow:build+branch:master+event:push)

A tool to visually manage software development ecosystems description.

## Concepts

A software development **ecosystem** can be described as a set of software development **projects**. Each project, is defined by a set of **data sources** (git, issue tracking system, mailing list, etc.) with some specific parameters each (url, filters, etc.), that we would call **repository views**, or just **repositories**.

Bestiary is a tool to manage this kind of description using a web based interface.

It also provides an interface to connect with [GrimoireLab](http://grimoirelab.github.io) to work as analytics scope manager.

# How to run it?

Clone the repository, and we recommend to set up a Python virtual environment to run it

```
$ python3 -m venv bestiary
$ source bestiary/bin/activate
```

Install the requirements:

```
(bestiary)$ pip3 install -r requirements.txt
```

Run Bestiary as a typical Django app:

```
(bestiary)$ cd bestiary/django_bestiary
(bestiary)$ python3 manage.py makemigrations
(bestiary)$ python3 manage.py migrate
(bestiary)$ python3 manage.py runserver
```

# License

[GPL v3](LICENSE)
