#!/usr/bin/env bash
# coding: utf-8
# pylint: disable=C0114,C0413,R0902,C0209
# determine available python executable
_=''''
#[ "$1" = -W ] && shift && exec watch -x -c -- "$0" -C y "$@"
export PGT_PGREP=$(type -p pgrep)
python=$(type -p python || type -p python3 || type -p python2)
[ "$python" ] && exec $python "$0" "$@"
echo "ERROR: cannot find python interpreter" >&2
exit 1
'''

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

Reminder for compatibility with old python versions:
no dict comprehension or dict simili comprehension
no f string or string .format()
no inline if
"""

__author__ = "Franck Jouvanceau"
__copyright__ = "Copyright 2020, Franck Jouvanceau"
__license__ = "MIT"

import sys
import os
import getopt
import platform
import re
import time

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
    #COLOR_FG = "\x1b[38;5;"  # 256 colors
    COLOR_FG = "\x1b[01;"    # 16 colors more compatible
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
        self.use_color = use_color
        self.colors = {
            'pid': '34',   # 12
            'user': '33',  # 3
            'comm': '32',  # 2
            '%cpu': '31',
            'vsz': '35',
            '%mem': '35',
            'time': '35',
            'default': '36', # 8
        }

    def colorize(self, field, value):
        """colorize fields"""
        if not self.use_color:
            return value
        if field in self.colors:
            return self.COLOR_FG + self.colors[field] + "m" + value + self.COLOR_RESET
        return self.colorize('default', value)


class Proctree:
    """
    Manage process tree of pids
    Proctree([ 'pid1', 'pid2' ])
    """

    # pylint: disable=R0913
    def __init__(self, use_uid=False, use_ascii=False, use_color=False,
                 pid_zero=True, opt_fields=None):
        """constructor"""
        self.pids = []
        self.ps_info = {}        # ps command info stored
        self.children = {}       # children of pid
        self.selected_pids = []  # pids and their children
        self.pids_tree = {}
        self.top_parents = []
        self.treedisp = Treedisplay(use_ascii, use_color)
        self.ps_fields = self.get_fields(opt_fields, use_uid)
        self.get_psinfo(pid_zero)

    def get_fields(self, opt_fields=None, use_uid=False):
        """ Get ps fields from OS / optionnal fields """
        osname = platform.system()
        if not opt_fields:
            if osname in ['AIX', 'Darwin']:
                opt_fields = ['start']
            else:
                opt_fields = ['stime']
        if use_uid:
            user = 'uid'
        else:
            user = 'user'
        if osname == 'SunOS':
            comm = 'comm'
        else:
            comm = 'ucomm'

        return ['pid', 'ppid', user, comm] + opt_fields

    def get_psinfo(self, pid_zero):
        """parse unix ps command"""
        widths = [30, 30, 30, 130] + [50 for i in self.ps_fields[4:]]
        ps_cmd = 'ps -e ' + ' '.join(
                    ['-o '+ o +'='+ widths[i]*'-' for i,o in enumerate(self.ps_fields)]
                ) + ' -o args'
        # print(ps_cmd)
        ps_out = runcmd(ps_cmd.split(' ')).split('\n')
        pid_z = ["0", "0"] + self.ps_fields[2:]
        ps_out[0] = ' '.join(
                [('%-'+ str(widths[i]) +'s') % opt for i,opt in enumerate(pid_z)] + ['args']
        )
        ps_opts = ['pid', 'ppid', 'user', 'comm'] + self.ps_fields[4:]
        # print(ps_out[0])
        for line in ps_out:
            # print(line)
            infos = {}
            col = 0
            for i,field in enumerate(ps_opts):
                infos[field] = line[col:col+widths[i]].strip()
                col = col + widths[i] + 1
            infos['args'] = line[col:len(line)]
            infos['comm'] = os.path.basename(infos['comm'])
            # print(infos)
            pid = infos['pid']
            ppid = infos['ppid']
            if pid == str(os.getpid()):
                continue
            if ppid == pid:
                ppid = '-1'
                infos['ppid'] = '-1'
            if ppid not in self.children:
                self.children[ppid] = []
            self.children[ppid].append(pid)
            self.ps_info[pid] = infos
        if not pid_zero:
            del self.ps_info['0']
            del self.children['0']

    def pgrep(self, argv):
        """mini built-in pgrep if pgrep command not available
           [-f] [-x] [-i] [-u <user>] [pattern]"""
        if "PGT_PGREP" not in os.environ or os.environ["PGT_PGREP"]:
            pgrep = runcmd(['pgrep'] + argv)
            return pgrep.split("\n")

        try:
            opts, args = getopt.getopt(argv, "ifxu:")
        except getopt.GetoptError:
            print("bad pgrep parameters")
            sys.exit(2)
        psfield = "comm"
        flag = 0
        exact = False
        user = ".*"
        pattern = ".*"
        for opt, arg in opts:
            if opt == "-f":
                psfield = "args"
            elif opt == "-i":
                flag = re.IGNORECASE
            elif opt == "-x":
                exact = True
            elif opt == "-u":
                user = arg

        if args:
            pattern = args[0]
        if exact:
            pattern = "^" + pattern + "$"
        pids = []
        for pid,info in self.ps_info.items():
            if pid == '0':
                continue
            if re.search(pattern, info[psfield], flag) and \
               re.match(user, info["user"]):
                pids.append(pid)
        return pids


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
            ps_info = self.treedisp.colorize('pid', pid.ljust(5)) + \
                      self.treedisp.colorize('user', ' (' + self.ps_info[pid]['user'] + ') ') + \
                      self.treedisp.colorize('comm', '[' + self.ps_info[pid]['comm'] + '] ')
            ps_info += ' '.join(
                [self.treedisp.colorize(f, self.ps_info[pid][f]) for f in self.ps_fields[4:]]
            )
            ps_info += ' ' + self.ps_info[pid]['args']
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

    def print_tree(self, pids=None, child_only=False, sig=0, confirmed=False):
        """display full or children only process tree"""
        if pids:
            self.pids = pids
        else:
            if '0' in self.children:
                self.pids = ['0']
            else:
                self.pids = ['1']
        self.build_tree()
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

def colored(opt):
    """colored output or not"""
    if opt in ('y', 'yes', 'always'):
        opt = True
    elif opt in ('n', 'no', 'never'):
        opt = False
    elif opt == 'auto':
        opt = sys.stdout.isatty()
    return opt

def wrap_text(opt):
    """wrap/nowrap text on tty (default wrap with tty)"""
    if opt in ('y', 'yes'):
        opt = True
    elif opt in ('n', 'no'):
        opt = False

    if sys.stdout.isatty() and opt:
        sys.stdout.write("\x1b[?7l")  # rmam
        after = "\x1b[?7h"            # smam
    else:
        after = ''
    return after

def pgtree(options, psfields, pgrep_args):
    """ Display process tree from options """
    ptree = Proctree(use_uid='-I' in options,
                     use_ascii='-a' in options,
                     use_color=colored(options['-C']),
                     pid_zero='-1' not in options,
                     opt_fields=psfields)

    found = None
    if '-p' in options:
        found = options['-p'].split(',')
    elif pgrep_args:
        found = ptree.pgrep(pgrep_args)
    return (ptree, found)

def watch_pgtree(options, psfields, pgrep_args, sig):
    """ follow process hierarchy """
    while True:
        try:
            (ptree, found) = pgtree(options, psfields, pgrep_args)
            cur_time = time.strftime("%c", time.localtime())
            sys.stdout.write("\033c")
            wrap_text(options['-w'])
            sys.stdout.write("Every 2.0s: " + ' '.join(sys.argv) + "    " + cur_time + "\n\n")
            ptree.print_tree(pids=found, child_only='-c' in options, sig=sig,
                     confirmed='-y' in options)
            if time.sleep(2):
                break
        except KeyboardInterrupt:
            break


def main(argv):
    """pgtree command line"""
    usage = """
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
    -O <psfield>[,psfield,...] : display multiple <psfield> instead of 'stime' in output
                   <psfield> must be valid with ps -o <psfield> command

    by default display full process hierarchy (parents + children of selected processes)

    -p <pids> : select processes pids to display hierarchy (default 0)
    -1 : display hierachy children of pid 1 (not including pid 0)
    <pgrep args> : use pgrep to select processes (see pgrep -h)

    found pids are prefixed with ►     
    """

    # allow options after pattern : pgtree mysearch -fc
    if len(argv) > 1 and argv[0][0] != '-':
        argv.append(argv.pop(0))
    if 'PGTREE' in os.environ:
        argv = os.environ["PGTREE"].split(' ') + argv
    try:
        opts, args = getopt.getopt(argv,
                                   "W1IRckKfxvinoyap:u:U:g:G:P:s:t:F:O:C:w:",
                                   ["ns=", "nslist="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)

    sig = 0
    pgrep_args = []
    options = {}
    psfields = None
    options['-C'] = 'auto'
    options['-w'] = 'yes'
    for opt, arg in opts:
        options[opt] = arg
        if opt == "-k":
            sig = 15
        elif opt == "-K":
            sig = 9
        elif opt == "-O":
            psfields = arg.split(',')
        elif opt == "-R":
            os.environ["PGT_PGREP"] = ""
        elif opt in ("-f", "-x", "-v", "-i", "-n", "-o"):
            pgrep_args.append(opt)
        elif opt in ("-u", "-U", "-g", "-G", "-P", "-s", "-t", "-F", "--ns", "--nslist"):
            pgrep_args += [opt, arg]
    pgrep_args += args
    after = wrap_text(options['-w'])
    if '-W' in options:
        watch_pgtree(options, psfields, pgrep_args, sig)
    else:
        (ptree, found) = pgtree(options, psfields, pgrep_args)
        ptree.print_tree(pids=found, child_only='-c' in options, sig=sig,
                         confirmed='-y' in options)
    sys.stdout.write(after)


if __name__ == '__main__':
    main(sys.argv[1:])
