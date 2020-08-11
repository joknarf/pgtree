#!/usr/bin/env python
# coding: utf-8
"""
Program for showing the hierarchy of specific processes on a Unix computer.
Like pstree but with searching for specific processes with pgrep first and display
hierarchy of matching processes (parents and children)
should work on any Unix supporting commands :
# pgrep
# ps -e -o pid,ppid,comm,args
(RedHat/CentOS/Fedora/Ubuntu/Suse/Solaris...)
Compatible python 2 / 3

Usage :
$ pgtree.py <pgrep args>
Example:
$ pgtree.py sshd
  1 (root) [init] /init
  └─6 (root) [init] /init
    └─144 (root) [systemd] /lib/systemd/systemd --system-unit=basic.target
▶     └─483 (root) [sshd] /usr/sbin/sshd -D
▶       └─1066 (root) [sshd] sshd: joknarf [priv]
▶         └─1181 (joknarf) [sshd] sshd: joknarf@pts/1
            └─1182 (joknarf) [bash] -bash
              ├─1905 (joknarf) [sleep] sleep 60
              └─1906 (joknarf) [top] top
"""

__author__ = "Franck Jouvanceau"
__copyright__ = "Copyright 2020, Franck Jouvanceau"
__license__ = "MIT"

import sys
import os
import getopt
import subprocess

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')

def runcmd(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = proc.communicate()
    return proc.returncode, std_out.decode('utf8').rstrip('\n'), std_err

def ask(prompt):
    try:
        answer = raw_input(prompt)
    except NameError:
        answer = input(prompt)
    return answer


class Proctree:
    """
    Manage process tree of pids
    Proctree([ 'pid1', 'pid2' ])
    """
    def __init__(self, pids=['1'], use_uid=False):
        self.pids = pids         # pids to display hierarchy
        self.psinfo = {}         # ps command info stored
        self.parent = {}         # parent of pid
        self.children = {}       # children of pid
        self.parents = {}        # all parents of pid in self.pids
        self.tree = {}           # tree for self.pids
        self.selected_pids = []  # pids and their children
        self.get_psinfo(use_uid)
        self.build_tree()

    def get_psinfo(self, use_uid):
        user = 'uid' if use_uid else 'user'
        (code, out, err) = runcmd(['ps', '-e', '-o', 'pid,ppid,'+user+',comm,args'])
        ps_out = out.split('\n')
        ps_header = ps_out[0]
        # guess columns width from ps header :
        # PID and PPID right aligned (and UID if used)
        # '  PID  PPID USER     COMMAND  COMMAND'
        b_ppid = ps_header.find('PID') + 4
        b_user = ps_header.find('PPID') + 5
        b_comm = ps_header.find('COMMAND')
        b_args = ps_header.find('COMMAND', b_comm+1)
        for line in ps_out:
            #(pid, ppid, user, comm, args) = line.split(maxsplit=4)
            pid = line[0:b_ppid-1].strip(' ')
            ppid = line[b_ppid:b_user-1].strip(' ')
            user = line[b_user:b_comm-1].strip(' ')
            comm = line[b_comm:b_args-1].strip(' ')
            args = line[b_args:]
            #print(pid,ppid,user)
            if not (ppid in self.children):
                self.children[ppid] = []
            self.children[ppid].append(pid)
            self.parent[pid] = ppid
            self.psinfo[pid] = {
                'ppid': ppid,
                'user': user,
                'comm': comm,
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
                ppre = '▶' + pre[1:]   # ⇒ 🠖 🡆 ➤ ➥ ► ▶
            if print_it:
                self.selected_pids.insert(0, pid)
                if pre == ' ':         # head of hierarchy
                    curr_p = next_p = ' '
                elif n == len(tree):   # last child
                    curr_p = '└─'
                    next_p = '  '
                else:                  # not last child
                    curr_p = '├─'
                    next_p = '│ '
                psinfo = pid+' ('+info['user']+') ['+info['comm']+'] '+info['args']
                output = ppre + curr_p + psinfo
                print(output)
            self._print_tree(info['children'], print_it, pre+next_p)
            n += 1

    def print_tree(self, child_only):
        self._print_tree(self.tree, not child_only)

    def kill_with_children(self, sig=15, confirmed=False):
        self._print_tree(self.tree, False)
        if len(self.selected_pids) == 0:
            return
        print("kill "+" ".join(self.selected_pids))
        if not confirmed:
            answer = ask('Confirm (y/[n]) ? ')
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
    usage = """
    usage: pgtree.py [-I] [-c|-k|-K] [-p <pid1>,...|<pgrep args>]

    -I : use -o uid instead of -o user for ps command
         (if uid/user mapping is broken ps command can be stuck)
    -c : display processes and children only 
    -k : kill -TERM processes and children
    -K : kill -KILL processes and children

    by default display full process hierarchy (parents + children of selected processes)

    -p <pids> : select processes pids to display hierarchy
    <pgrep args> : use pgrep to select processes (see pgrep -h)

    found pids are prefixed with ▶
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "IckKfxvinop:u:U:g:G:P:s:t:F:", ["ns=","nslist="] )
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)

    use_uid = False
    child_only = False
    sig = 0
    pgrep_args = []
    found = []
    for o, a in opts:
        if o == "-I":
            use_uid = True
        elif o in ("-c"):
            child_only = True
        elif o in ("-k"):
            sig = 15
        elif o in ("-K"):
            sig = 9
        elif o in ("-p"):
            found = a.split(',')
        elif o in ("-f","-x","-v","-i","-n","-o"):
            pgrep_args.append(o)
        elif o in ("-u","-U","-g","-G","-P","-s","-t","-F","--ns","--nslist"):
            pgrep_args += [ o, a ]
    pgrep_args += args
    if not found:
        code, pgrep, err = runcmd(['/usr/bin/pgrep'] + pgrep_args)
        if pgrep:
            found = pgrep.split("\n")
        else:
            exit(1)
    pid = str(os.getpid())
    if pid in found:
        found.remove(pid)
    rmam="\x1b[?7l"
    smam="\x1b[?7h"
    ptree = Proctree(pids=found, use_uid=use_uid)
    # truncate lines if tty output
    if sys.stdout.isatty():
        sys.stdout.write(rmam)
    if sig:
        ptree.kill_with_children(sig)
    else:
        ptree.print_tree(child_only)
    if sys.stdout.isatty():
       sys.stdout.write(smam)


if __name__ == '__main__':
    main()
