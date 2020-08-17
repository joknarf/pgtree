[![Travis CI](https://travis-ci.com/joknarf/pgtree.svg?branch=master)](https://travis-ci.com/github/joknarf/pgtree)
[![Codecov](https://codecov.io/github/joknarf/pgtree/coverage.svg?branch=master)](https://codecov.io/gh/joknarf/pgtree)
[![Python versions](https://img.shields.io/pypi/v/pgtree.svg)](https://pypi.org/project/pgtree/)

# pgtree
Unix process hierachy tree display for specific processes (kind of mixed pgrep + pstree)

pgtree is also able to send signal to found processes and all their children

The purpose is to have the tool working out of the box on any Unix box, using the default OS python installed, without installing anything else.
The code must be compatible with python 2.x + 3.x

Should work on any Unix that can execute :
```
# /usr/bin/pgrep 
# /usr/bin/ps -e -o pid,ppid,user,comm,args
```
## Installation
root install in `/usr/local/bin`
```
# ./setup.py install
```
user install
```
# ./setup.py install --prefix=~/.local
```
## Usage
```
# pgtree -h
    usage: pgtree.py [-C] [-I] [-c|-k|-K][-y] [-p <pid1>,...|<pgrep args>]

    -I : use -o uid instead of -o user for ps command
         (if uid/user mapping is broken ps command can be stuck)
    -c : display processes and children only
    -k : kill -TERM processes and children
    -K : kill -KILL processes and children
    -y : do not ask for confirmation to kill
    -C : no color (default colored output on tty)

    by default display full process hierarchy (parents + children of selected processes)

    -p <pids> : select processes pids to display hierarchy (default 1)
    <pgrep args> : use pgrep to select processes (see pgrep -h)

    found pids are prefixed with ▶
```
## Examples
show all parents and children of processes matching `bash`

<img alt="# pgtree bash" src="https://user-images.githubusercontent.com/10117818/90019684-10f37680-dcaf-11ea-8e32-8f2b57304f92.png" width="600px">

show processes matching `bash` and their children

<img alt="# pgtree -c bash" src="https://user-images.githubusercontent.com/10117818/90019719-19e44800-dcaf-11ea-8793-f32f50565406.png" width="600px">

kill all `sh` processes of user joknarf and their children

i<img alt="#pgtree -k -u joknarf -x sh" src="https://user-images.githubusercontent.com/10117818/90019713-16e95780-dcaf-11ea-95a1-b2a8c4edf31e.png" width="600px">
