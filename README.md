# pgtree
Unix process hierachy tree for specific processes (kind of mixed pgrep + pstree)

The purpose is to have the tool working out of the box on any Unix box, using the default OS python installed, without installing anything else.
The code must be compatible with python 2 + 3

Should work on any Unix that can execute :
```
# /usr/bin/pgrep 
# /usr/bin/ps -e -o pid,ppid,user,fname,args
```

## Usage
```
# ./pgtree.py -h
usage: pgtree.py [-c|-k|-K] [-p <pid1>,...|<pgrep args>]

-c : display processes and children only 
-k : kill -TERM processes and children
-K : kill -KILL processes and children

by default display full process hierarchy (parents + children of selected processes)

-p <pids> : select processes pids to display hierarchy
<pgrep args> : use pgrep to select processes

found pids are prefixed with ▶  

```

## Examples
show all parents and children of processes matching `bash`
``` 
# ./pgtree.py bash
  1 (root) [init] /init
  ├─6 (root) [init] /init
  │ └─7 (root) [init] /init
▶ │   └─8 (joknarf) [bash] -bash
  │     └─2435 (joknarf) [python] python /mnt/c/Users/knarf/PycharmProjects/pgtree/pgtree.py bash
  │       └─2437 (joknarf) [ps] ps -e -o pid,ppid,user,comm,args
  └─1723 (root) [init] /init
    └─1725 (root) [init] /init
▶     └─1729 (joknarf) [bash] -bash
        └─1902 (root) [sudo] sudo su -
          └─1903 (root) [su] su -
▶           └─1905 (root) [bash] -su
```

show processes matching `bash` and their children
```
# ./pgtree.py -c bash
▶ 8 (joknarf) [bash] -bash
  └─2441 (joknarf) [python] python /mnt/c/Users/knarf/PycharmProjects/pgtree/pgtree.py -c bash
    └─2443 (joknarf) [ps] ps -e -o pid,ppid,user,comm,args
▶ 1729 (joknarf) [bash] -bash
  └─1902 (root) [sudo] sudo su -
    └─1903 (root) [su] su -
▶     └─1905 (root) [bash] -su
```
 
 kill all `sh`processes of user joknarf  and its children
 ```
# ./pgtree.py -K -u joknarf -x sh
▶ 2478 (joknarf) [sh] sh
  ├─2480 (joknarf) [sleep] sleep 9999
  └─2481 (joknarf) [top] top
kill 2481 2480 2478
Confirm (y/[n]) ? y
```
