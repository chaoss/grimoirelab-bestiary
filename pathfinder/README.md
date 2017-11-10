**This is ALPHA quality code yet. Stay tuned.**

# Pathfinder

Find and collect software repositories data.

## Usage

```
usage: pathfinder.py [-h] [-d DATA_SOURCE] [-g] [-t TOKEN]
                     [-o [OWNERS [OWNERS ...]]]

optional arguments:
  -h, --help            show this help message and exit
  -d DATA_SOURCE, --data-source DATA_SOURCE
                        Data source to get repositories from
  -g, --debug
  -t TOKEN, --token TOKEN
                        Auth token
  -o [OWNERS [OWNERS ...]], --owners [OWNERS [OWNERS ...]]
                        GitHub owners to get repos from
```

Some samples:

```
pathfinder.py -b gerrit --url git.eclipse.org --user gerrit_ssh_user
pathfinder.py -b github -t XXXXXX  -o grimoirelab
pathfinder.py -b eclipse -d git
```
