# pgtree
Unix process hierachy tree for specific processes (mixed pgrep + pstree)

show all parents and children of processes matching `bash`
```
# ./pgtree.py bash
 1 (root) /init
 ├─6 (root) /init
 │ └─7 (root) /init
 │   └─8 (joknarf) -bash
 │     ├─200 (joknarf) sleep 600
 │     └─201 (joknarf) python ./pgtree.py bash
 │       └─203 (joknarf) ps -e -o pid,ppid,user,fname,args
 └─160 (root) /init
   └─161 (root) /init
     └─162 (joknarf) -bash
       └─193 (joknarf) top
```

show all children on processes matching `bash`
```
# ./pgtree.py -c bash
 8 (joknarf) -bash
 ├─200 (joknarf) sleep 600
 └─204 (joknarf) python ./pgtree.py -c bash
   └─206 (joknarf) ps -e -o pid,ppid,user,fname,args
 162 (joknarf) -bash
 └─193 (joknarf) top
 ```
 
 kill all `sh`processes of user joknarf  and its children
 ```
 # ./pgtree -K -u joknarf -x sh
 207 (joknarf) sh
 ├─208 (joknarf) sleep 900
 └─209 (joknarf) top
kill 209 208 207
```
