#!/usr/bin/env python
"""
Program for showing the hierarchy of specific processes on a Unix computer.
Like pstree but with searching for specific processes with pgrep first and display
hierarchy of matching processes (parents and children)
Usage :
$ pgtree.py <pgrep args>
Example:
$ pgtree.py sshd
  1 (root) /init
  └─6 (root) /init
    └─144 (root) /lib/systemd/systemd --system-unit=basic.target
      └─483 (root) /usr/sbin/sshd -D
        └─1066 (root) sshd: joknarf [priv]
          └─1181 (joknarf) sshd: joknarf@pts/1
            └─1182 (joknarf) -bash
              ├─1905 (joknarf) sleep 60
              └─1906 (joknarf) top
"""

__author__ = "Franck Jouvanceau"
__copyright__ = "Copyright 2020, Franck Jouvanceau"
__license__ = "MIT"

import sys
import os
import subprocess


def runcmd(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = proc.communicate()
    return proc.returncode, std_out.decode('utf8').rstrip('\n'), std_err


class Proctree:
    """
    Display process tree of pids
    Proctree([ 'pid1', 'pid2' ])
    """
    def __init__(self, pids=['1']):
        self.pids = pids         # pids to display hierarchy
        self.psinfo = {}         # ps command info stored
        self.parent = {}         # parent of pid
        self.children = {}       # children of pid
        self.parents = {}        # all parents of pid in self.pids
        self.tree = {}           # tree for self.pids
        self.selected_pids = []  # pids and their children
        self.get_psinfo()
        self.build_tree()

    def get_psinfo(self):
        out = subprocess.check_output(['ps', '-e', '-o', 'pid,ppid,user,fname,args']).decode('utf8').rstrip("\n").split("\n")
        head = out[0]
        # guess columns width from ps header :
        # '  PID  PPID USER     COMMAND  COMMAND'
        ppidb = head.find('PID',0) + 4
        userb = head.find('USER',0)
        fnameb = head.find('COMMAND',0)
        argsb = head.find('COMMAND', fnameb+1)
        for line in out:
            #(pid, ppid, user, fname, args) = line.split(maxsplit=4)
            pid = line[0:ppidb-1].lstrip(' ')
            ppid = line[ppidb:userb-1].lstrip(' ')
            user = line[userb:fnameb-1].rstrip(' ')
            fname = line[fnameb:argsb-1].rstrip(' ')
            args = line[argsb:]
            #print(pid,ppid,user)
            if not (ppid in self.children):
                self.children[ppid] = []
            self.children[ppid].append(pid)
            self.parent[pid] = ppid
            self.psinfo[pid] = {
                'ppid': ppid,
                'user': user,
                'fname': fname,
                'args': args,
            }

    # parents[pid] = [ '1', '12', '130' ] (ordered parent pids)
    def get_parents(self):
        self.parents = {}
        for pid in self.pids:
            if not pid in self.parent:
                continue
            self.parents[pid] = []
            ppid = self.parent[pid]
            while ppid in self.parent:
                self.parents[pid].insert(0, ppid)
                ppid = self.parent[ppid]

    # recursive
    def children2tree(self, tree, pid):
        tree[pid] = self.psinfo[pid]
        tree[pid]['children'] = {}
        if pid in self.children:
            for cpid in self.children[pid]:
                self.children2tree(tree[pid]['children'], cpid)

    def build_tree(self):
        self.get_parents()
        for foundpid in self.parents:
            current = self.tree
            for ppid in self.parents[foundpid]:
                if ppid not in current:
                    current[ppid] = self.psinfo[ppid]
                    current[ppid]['children'] = {}
                current = current[ppid]['children']
            if foundpid not in current:
                self.children2tree(current, foundpid)

    # recursive process tree display
    def _print_tree(self, tree, print_it=True, pre=' '):
        n = 1
        for pid, info in tree.items():
            next_p = ''
            ppre = pre
            if pid in self.pids:
                print_it = True
                ppre = '⇒' + pre[1:]  # ⇒ 🠖
            if print_it:
                self.selected_pids.insert(0, pid)
                if pre == ' ':
                    curr_p = next_p = ' '
                elif n == len(tree):
                    curr_p = '└─'
                    next_p = '  '
                else:
                    curr_p = '├─'
                    next_p = '│ '
                print(ppre+curr_p+pid, '('+info['user']+')', '['+info['fname']+']', info['args'])
            self._print_tree(info['children'], print_it, pre+next_p)
            n += 1

    def print_tree(self, child_only):
        self._print_tree(self.tree, not child_only)

    def kill_with_children(self, sig=15, confirmed=False):
        self._print_tree(self.tree, False)
        print("kill "+" ".join(self.selected_pids))
        if not confirmed:
            answer = input('Confirm ? (y/n) ')
            if answer != 'y':
                return
        for pid in self.selected_pids:
            if pid == str(os.getpid()):
                continue
            try:
                os.kill(int(pid), sig)
            except ProcessLookupError:
                continue
            except PermissionError:
                print('kill ' + pid + ': Permission error')
                continue


def main():
    # We don't want to use argparse module as we are not in a fancy developer zone
    # We are sys admins we are facing very hazardous environments (python 2.4 or less)
    if len(sys.argv) < 2 or sys.argv[1] == '-h':
        print("usage: pgtree.py [-c|-k|-K] [-p <pid1>,...|<pgrep args>]")
        exit(1)
    sig = 0
    child_only = False
    found = []
    # switch case in python useless...
    if sys.argv[1] == '-k':
        sig = 15
        sys.argv.pop(1)
    elif sys.argv[1] == '-K':
        sig = 9
        sys.argv.pop(1)
    elif sys.argv[1] == '-c':
        child_only = True
        sys.argv.pop(1)

    if sys.argv[1] == '-p':
        found = sys.argv[2].split(',')
    else:
        code, pgrep, err = runcmd(['/usr/bin/pgrep'] + sys.argv[1:])
        if pgrep:
            found = pgrep.split("\n")
        else:
            exit(1)
    pid = str(os.getpid())
    if pid in found:
        found.remove(pid)
    ptree = Proctree(found)
    if sig:
        ptree.kill_with_children(sig)
    else:
        ptree.print_tree(child_only)


if __name__ == '__main__':
    main()