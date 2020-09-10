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

Example:
$ ./pgtree.py sshd
  1 (root) [init] /init
  └─6 (root) [init] /init
    └─144 (root) [systemd] /lib/systemd/systemd --system-unit=basic.target
►     └─483 (root) [sshd] /usr/sbin/sshd -D
►       └─1066 (root) [sshd] sshd: joknarf [priv]
►         └─1181 (joknarf) [sshd] sshd: joknarf@pts/1
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

# pylint: disable=E0602
# pylint: disable=E1101
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')

def runcmd(cmd):
    """run command"""
    pipe = os.popen('"' + '" "'.join(cmd) + '"', 'r')
    std_out = pipe.read()
    pipe.close()
    return std_out.rstrip('\n')

def ask(prompt):
    """input text"""
    try:
        answer = raw_input(prompt)
    except NameError:
        answer = input(prompt)
    return answer

# pylint: disable=R0903
class Treedisplay:
    """Tree display attributes"""
    COLOR_FG = "\x1b[38;5;"
    COLOR_RESET = "\x1b[0m"

    def __init__(self, use_ascii=False, use_color=False):
        """choose tree characters"""
        if use_ascii:
            self.selected = '>'
            self.child = '|_'
            self.notchild = '| '
            self.lastchild = '\\_'
        else:
            self.selected = '►' # ⇒ 🠖 🡆 ➤ ➥ ► ▶
            self.child = '├─'
            self.notchild = '│ '
            self.lastchild = '└─'
        self.colors = {}
        if use_color:
            self.colors = {
                'pid': '12',
                'user': '3',
                'comm': '2',
                'stime': '8',
            }

    def colorize(self, field, value):
        """colorize fields"""
        if field in self.colors:
            return self.COLOR_FG + self.colors[field] + "m" + value + self.COLOR_RESET
        return value


class Proctree:
    """
    Manage process tree of pids
    Proctree([ 'pid1', 'pid2' ])
    """

    def __init__(self, pids=('1'), use_uid=False, use_ascii=False, use_color=False):
        """constructor"""
        self.pids = pids         # pids to display hierarchy
        self.ps_info = {}        # ps command info stored
        self.children = {}       # children of pid
        self.selected_pids = []  # pids and their children
        self.pids_tree = {}
        self.top_parents = []
        self.treedisp = Treedisplay(use_ascii, use_color)
        self.get_psinfo(use_uid)
        self.build_tree()

    def get_psinfo(self, use_uid):
        """parse unix ps command"""
        if use_uid:
            user = 'uid'
        else:
            user = 'user'
        out = runcmd(['ps', '-e', '-o', 'pid,ppid,stime,'+user+',comm,args'])
        ps_out = out.split('\n')
        # cannot split as space char can occur in comm
        # guess columns width from ps header :
        # PID, PPID, STIME right aligned (and UID if used)
        # '  PID  PPID STIME USER     COMMAND  COMMAND'
        col_b = {
            'pid': 0,
            'ppid': ps_out[0].find('PID') + 4,
            'stime': ps_out[0].find('PPID') + 5,
            'user': ps_out[0].find('STIME') + 6,
            'comm': ps_out[0].find('COMMAND'),
        }
        col_b['args'] = ps_out[0].find('COMMAND', col_b['comm']+1)
        for line in ps_out[1:]:
            pid = line[0:col_b['ppid']-1].strip(' ')
            if pid == str(os.getpid()):
                continue
            ppid = line[col_b['ppid']:col_b['stime']-1].strip(' ')
            if ppid == pid:
                ppid = '-1'
            if ppid not in self.children:
                self.children[ppid] = []
            self.children[ppid].append(pid)
            self.ps_info[pid] = {
                'ppid': ppid,
                'stime': line[col_b['stime']:col_b['user']-1].strip(' '),
                'user': line[col_b['user']:col_b['comm']-1].strip(' '),
                'comm': os.path.basename(line[col_b['comm']:col_b['args']-1].strip(' ')),
                'args': line[col_b['args']:],
            }

    def get_parents(self):
        """get parents list of pids"""
        for pid in self.pids:
            if pid not in self.ps_info:
                continue
            while pid in self.ps_info:
                ppid = self.ps_info[pid]['ppid']
                if ppid not in self.pids_tree:
                    self.pids_tree[ppid] = []
                if pid not in self.pids_tree[ppid]:
                    self.pids_tree[ppid].append(pid)
                last_ppid = pid
                pid = ppid
            if last_ppid not in self.top_parents:
                self.top_parents.append(last_ppid)

    # recursive
    def children2tree(self, pids):
        """build children tree"""
        for pid in pids:
            if pid in self.pids_tree:
                continue
            if pid in self.children:
                self.pids_tree[pid] = self.children[pid]
                self.children2tree(self.children[pid])

    def build_tree(self):
        """build process tree"""
        self.children2tree(self.pids)
        self.get_parents()

    def print_proc(self, pid, pre, print_it, last):
        """display process information with indent/tree/colors"""
        next_p = ''
        ppre = pre
        if pid in self.pids:
            print_it = True
            ppre = self.treedisp.selected + pre[1:]
        if print_it:
            self.selected_pids.insert(0, pid)
            if pre == ' ':  # head of hierarchy
                curr_p = next_p = ' '
            elif last:  # last child
                curr_p = self.treedisp.lastchild
                next_p = '  '
            else:  # not last child
                curr_p = self.treedisp.child
                next_p = self.treedisp.notchild
            ps_info = self.treedisp.colorize('pid', pid.ljust(5, ' ')) + \
                      self.treedisp.colorize('user', ' (' + self.ps_info[pid]['user'] + ') ') + \
                      self.treedisp.colorize('comm', '[' + self.ps_info[pid]['comm'] + '] ') + \
                      self.treedisp.colorize('stime', self.ps_info[pid]['stime'] + ' ') + \
                      self.ps_info[pid]['args']
            output = ppre + curr_p + ps_info
            print(output)
        return (next_p, print_it)

    # recursive
    def _print_tree(self, pids, print_it=True, pre=' '):
        """display wonderful process tree"""
        for idx, pid in enumerate(pids):
            (next_p, print_children) = self.print_proc(pid, pre, print_it, idx == len(pids)-1)
            if pid in self.pids_tree:
                self._print_tree(self.pids_tree[pid], print_children, pre+next_p)

    def print_tree(self, child_only, sig=0, confirmed=False):
        """display full or children only process tree"""
        if sig:
            self.kill_with_children(sig=sig, confirmed=confirmed)
        else:
            self._print_tree(self.top_parents, not child_only)

    def kill_with_children(self, sig=15, confirmed=False):
        """kill processes and children with signal"""
        self._print_tree(self.top_parents, False)
        if not self.selected_pids:
            return
        print("kill "+" ".join(self.selected_pids))
        if not confirmed:
            answer = ask('Confirm (y/[n]) ? ')
            if answer != 'y':
                return
        for pid in self.selected_pids:
            try:
                os.kill(int(pid), sig)
            except ProcessLookupError:
                continue
            except PermissionError:
                print('kill ' + pid + ': Permission error')
                continue


def main(argv):
    """pgtree command line"""
    usage = """
    usage: pgtree.py [-ICya] [-c|-k|-K] [-p <pid1>,...|<pgrep args>]

    -I : use -o uid instead of -o user for ps command
         (if uid/user mapping is broken ps command can be stuck)
    -c : display processes and children only 
    -k : kill -TERM processes and children
    -K : kill -KILL processes and children
    -y : do not ask for confirmation to kill
    -C : no color (default colored output on tty)
    -a : use ascii characters

    by default display full process hierarchy (parents + children of selected processes)

    -p <pids> : select processes pids to display hierarchy (default 1)
    <pgrep args> : use pgrep to select processes (see pgrep -h)

    found pids are prefixed with ►     
    """

    # allow options after pattern : pgtree mysearch -fc
    if len(argv) > 1 and argv[0][0] != '-':
        argv.append(argv.pop(0))

    try:
        opts, args = getopt.getopt(argv,
                                   "ICckKfxvinoyap:u:U:g:G:P:s:t:F:",
                                   ["ns=", "nslist="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)

    sig = 0
    pgrep_args = []
    found = ('1')
    options = {}
    for opt, arg in opts:
        options[opt] = arg
        if opt == "-k":
            sig = 15
        elif opt == "-K":
            sig = 9
        elif opt == "-p":
            found = arg.split(',')
        elif opt in ("-f", "-x", "-v", "-i", "-n", "-o"):
            pgrep_args.append(opt)
        elif opt in ("-u", "-U", "-g", "-G", "-P", "-s", "-t", "-F", "--ns", "--nslist"):
            pgrep_args += [opt, arg]
    pgrep_args += args
    if pgrep_args:
        pgrep = runcmd(['/usr/bin/pgrep'] + pgrep_args)
        found = pgrep.split("\n")
    # truncate lines if tty output / disable color if not tty
    if sys.stdout.isatty():
        sys.stdout.write("\x1b[?7l")  # rmam
        after = "\x1b[?7h"            # smam
    else:
        options['-C'] = ''
        after = ''
    ptree = Proctree(pids=found, use_uid='-I' in options,
                     use_ascii='-a' in options,
                     use_color='-C' not in options)
    ptree.print_tree(child_only='-c' in options, sig=sig,
                     confirmed='-y' in options)
    sys.stdout.write(after)


if __name__ == '__main__':
    main(sys.argv[1:])
