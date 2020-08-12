# pgtree
Unix process hierachy tree for specific processes (kind of mixed pgrep + pstree)

The purpose is to have the tool working out of the box on any Unix box, using the default OS python installed, without installing anything else.
The code must be compatible with python 2 + 3

Should work on any Unix that can execute :
```
# /usr/bin/pgrep 
# /usr/bin/ps -e -o pid,ppid,user,comm,args
```

## Usage
```
# ./pgtree.py -h
    usage: pgtree.py [-C] [-I] [-c|-k|-K] [-p <pid1>,...|<pgrep args>]

    -I : use -o uid instead of -o user for ps command
         (if uid/user mapping is broken ps command can be stuck)
    -c : display processes and children only
    -k : kill -TERM processes and children
    -K : kill -KILL processes and children
    -C : no color (default colored output on tty)

    by default display full process hierarchy (parents + children of selected processes)

    -p <pids> : select processes pids to display hierarchy (default 1)
    <pgrep args> : use pgrep to select processes (see pgrep -h)

    found pids are prefixed with ▶
```

## Examples
show all parents and children of processes matching `bash`
![pgtree_bash](https://user-images.githubusercontent.com/10117818/90019684-10f37680-dcaf-11ea-8e32-8f2b57304f92.png)

show processes matching `bash` and their children
![pgtree-c_bash](https://user-images.githubusercontent.com/10117818/90019719-19e44800-dcaf-11ea-8793-f32f50565406.png)

 kill all `sh`processes of user joknarf  and its children
![pgtree_-k](https://user-images.githubusercontent.com/10117818/90019713-16e95780-dcaf-11ea-95a1-b2a8c4edf31e.png)
 
