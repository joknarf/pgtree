[![Joknarf Tools](https://img.shields.io/badge/Joknarf%20Tools-Visit-darkgreen?logo=github)](https://joknarf.github.io/joknarf-tools)
[![Codecov](https://codecov.io/github/joknarf/pgtree/coverage.svg?branch=master)](https://codecov.io/gh/joknarf/pgtree)
[![Upload Python Package](https://github.com/joknarf/pgtree/workflows/Upload%20Python%20Package/badge.svg)](https://github.com/joknarf/pgtree/actions?query=workflow%3A%22Upload+Python+Package%22)
[![Pypi version](https://img.shields.io/pypi/v/pgtree.svg?logo=pypi)](https://pypi.org/project/pgtree/)
[![Python versions](https://img.shields.io/badge/python-2.3+%20|%203.x-blue.svg?logo=python)](https://shields.io/)
[![Licence](https://img.shields.io/badge/licence-MIT-blue.svg)](https://shields.io/)
[![Downloads](https://pepy.tech/badge/pgtree)](https://pepy.tech/project/pgtree)

# pgtree
Unix process hierachy tree display for specific processes (kind of mixed pgrep + pstree)

pgtree is also able to send signal to found processes and all their children

The purpose is to have the tool working out of the box on any Unix box, using the default OS python installed, without installing anything else.
The code must be compatible with python 2.x + 3.x

Should work on any Unix that can execute :
```
# /usr/bin/pgrep 
# /usr/bin/ps ax -o pid,ppid,stime,user,ucomm,args
```

if `pgrep` command not available (AIX), pgtree uses built-in pgrep (`-f -i -x -u <user>` supported).

`-T` option to display threads only works if `ps ax -T -o spid,ppid` available on system (ubuntu/redhat...)

_pgtree Tested on various versions of RedHat / CentOS / Ubuntu / Debian / Suse / FreeBSD / ArchLinux / MacOS / Solaris / AIX including old versions_

_(uses -o fname on Solaris)_

## Installation
FYI, the `pgtree/pgtree.py` is standalone and can be directly copied/used anywhere without any installation.

installation using pip:
```
# pip install pgtree
```

## Usage
```
# pgtree -h
    usage: pgtree.py [-W] [-RIya] [-C <when>] [-O <psfield>] [-c|-k|-K] [-1|-p <pid1>,...|<pgrep args>]

    -I : use -o uid instead of -o user for ps command
         (if uid/user mapping is broken ps command can be stuck)
    -c : display processes and children only 
    -k : kill -TERM processes and children
    -K : kill -KILL processes and children
    -y : do not ask for confirmation to kill
    -R : force use of internal pgrep
    -C : color preference : y/yes/always or n/no/never (default auto)
    -w : tty wrap text : y/yes or n/no (default y)
    -W : watch and follow process tree every 2s
    -a : use ascii characters
    -T : display threads (ps -T)
    -O <psfield>[,psfield,...] : display multiple <psfield> instead of 'stime' in output
                   <psfield> must be valid with ps -o <psfield> command

    by default display full process hierarchy (parents + children of selected processes)

    -p <pids> : select processes pids to display hierarchy (default 0)
    -1 : display hierachy children of pid 1 (not including pid 0)
    <pgrep args> : use pgrep to select processes (see pgrep -h)

    found pids are prefixed with ▶
```
## Examples
show all parents and children of processes matching `bash`

<img alt="# pgtree bash" src="https://user-images.githubusercontent.com/10117818/91555007-7d69a900-e930-11ea-98a2-8d81b7fdf0d3.png" width="850px">

show processes matching `bash` and their children

<img alt="# pgtree -c bash" src="https://user-images.githubusercontent.com/10117818/91555156-c15cae00-e930-11ea-9479-7c9b2c7b249e.png" width="850px">

kill all `sh` processes of user joknarf and their children

<img alt="#pgtree -k -u joknarf -x sh" src="https://user-images.githubusercontent.com/10117818/91555424-48aa2180-e931-11ea-8f19-6054458aa79c.png" width="850px">

Customize ps output fields:

<img width="719" alt="image" src="https://user-images.githubusercontent.com/10117818/215278250-83440d9c-f1a1-4ac7-afa5-db4f1b1c6395.png">

Put default options in PGTREE env variable:
```
# export PGTREE='-1 -O %cpu,stime -C y'
# pgtree
```

Use watch utility to follow process tree:
```
# pgtree -W bash
```
![image](https://user-images.githubusercontent.com/10117818/215317322-7df4559c-ccf4-41f6-b008-55d1fc8f0bb7.png)

## Demo

<img alt="output" src="https://user-images.githubusercontent.com/10117818/91558307-64fc8d00-e936-11ea-85bc-08eae29a58ce.gif" width="850px">

