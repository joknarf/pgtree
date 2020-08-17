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

#    from ._version import __version__
import subprocess
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
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = proc.communicate()
    return proc.returncode, std_out.decode('utf8').rstrip('\n'), std_err

def ask(prompt):
    """input text"""
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
    COLOR_FG = "\x1b[38;5;"
    COLOR_RESET = "\x1b[0m"

    def __init__(self, pids=('1'), use_uid=False, color=False):
        """constructor"""
        self.pids = pids         # pids to display hierarchy
        self.ps_info = {}        # ps command info stored
        self.children = {}       # children of pid
        self.selected_pids = []  # pids and their children
        self.pids_tree = {}
        self.top_parents = []
        self.colors = {}
        if color:
            self.colors = {
                'pid': '12',
                'user': '3',
                'comm': '2',
            }
        self.get_psinfo(use_uid)
        self.build_tree()

    def get_psinfo(self, use_uid):
        """parse unix ps command"""
        user = 'uid' if use_uid else 'user'
        out = runcmd(['ps', '-e', '-o', 'pid,ppid,'+user+',comm,args'])[1]
        ps_out = out.split('\n')
        # cannot split as space char can occur in comm
        # guess columns width from ps header :
        # PID and PPID right aligned (and UID if used)
        # '  PID  PPID USER     COMMAND  COMMAND'
        col_b = {
            'pid': 0,
            'ppid': ps_out[0].find('PID') + 4,
            'user': ps_out[0].find('PPID') + 5,
            'comm': ps_out[0].find('COMMAND'),
        }
        col_b['args'] = ps_out[0].find('COMMAND', col_b['comm']+1)
        for line in ps_out[1:]:
            pid = line[0:col_b['ppid']-1].strip(' ')
            ppid = line[col_b['ppid']:col_b['user']-1].strip(' ')
            if not ppid in self.children:
                self.children[ppid] = []
            self.children[ppid].append(pid)
            self.ps_info[pid] = {
                'ppid': ppid,
                'user': line[col_b['user']:col_b['comm']-1].strip(' '),
                'comm': line[col_b['comm']:col_b['args']-1].strip(' '),
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


    def colorize(self, field, value):
        """colorize fields"""
        if field in self.colors:
            return self.COLOR_FG + self.colors[field] + "m" + value + self.COLOR_RESET
        return value

    def print_proc(self, pid, pre, print_it, last):
        """display process information with indent/tree/colors"""
        next_p = ''
        ppre = pre
        if pid in self.pids:
            print_it = True
            ppre = '▶' + pre[1:]  # ⇒ 🠖 🡆 ➤ ➥ ► ▶
        if print_it:
            self.selected_pids.insert(0, pid)
            if pre == ' ':  # head of hierarchy
                curr_p = next_p = ' '
            elif last:  # last child
                curr_p = '└─'
                next_p = '  '
            else:  # not last child
                curr_p = '├─'
                next_p = '│ '
            ps_info = self.colorize('pid', pid) + \
                      self.colorize('user', ' (' + self.ps_info[pid]['user'] + ') ') + \
                      self.colorize('comm', '[' + self.ps_info[pid]['comm'] + '] ') + \
                      self.ps_info[pid]['args']
            output = ppre + curr_p + ps_info
            print(output)
        return (next_p, print_it)

    # recursive
    def _print_tree(self, pids, print_it=True, pre=' '):
        """display wonderful process tree"""
        for idx, pid in enumerate(pids):
            (next_p, print_it) = self.print_proc(pid, pre, print_it, idx == len(pids)-1)
            if pid in self.pids_tree:
                self._print_tree(self.pids_tree[pid], print_it, pre+next_p)

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
            if pid == str(os.getpid()):
                continue
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
    usage: pgtree.py [-I] [-c|-k|-K] [-p <pid1>,...|<pgrep args>]

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
    """
    try:
        opts, args = getopt.getopt(argv,
                                   "ICckKfxvinoyp:u:U:g:G:P:s:t:F:",
                                   ["ns=", "nslist="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)

    sig = 0
    pgrep_args = []
    found = ('1')
    options = {}
    for opt, arg in opts:
        options[opt] = args
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
        pgrep = runcmd(['/usr/bin/pgrep'] + pgrep_args)[1]
        found = pgrep.split("\n")
    pid = str(os.getpid())
    if pid in found:
        found.remove(pid)
    # truncate lines if tty output / disable color if not tty
    if sys.stdout.isatty():
        sys.stdout.write("\x1b[?7l")  # rmam
        after = "\x1b[?7h"            # smam
    else:
        options['-C'] = ''
        after = ''
    ptree = Proctree(pids=found, use_uid='-I' in options, color='-C' not in options)
    ptree.print_tree(child_only='-c' in options, sig=sig, confirmed='-y' in options)
    sys.stdout.write(after)


if __name__ == '__main__':
    main(sys.argv[1:])
