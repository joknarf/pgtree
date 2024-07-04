"""pgtree tests"""
import os
import sys
import unittest
from unittest.mock import patch
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import pgtree
#from unittest.mock import MagicMock, Mock, patch
os.environ['PGT_COMM'] = 'ucomm'
os.environ['PGT_STIME'] = 'stime'

class ProctreeTest(unittest.TestCase):
    """tests for pgtree"""
    @patch('os.kill')
    @patch('pgtree.pgtree.runcmd')
    def test_tree1(self, mock_runcmd, mock_kill):
        """test"""
        ps_out = 4*(130*'-'+' ')
        print("tree: =======")
        ps_out = 4*(130*'-'+' ') + "\n"
        ps_out += f'{"1":>30} {"0":>30} {"root":<30} {"init":<130} {"Aug12":<50} /init\n'
        ps_out += f'{"10":>30} {"1":>30} {"joknarf":<30} {"bash":<130} {"Aug12":<50} -bash\n'
        ps_out += f'{"20":>30} {"10":>30} {"joknarf":<30} {"sleep":<130} {"10:10":<50} /bin/sleep 60\n'
        ps_out += f'{"30":>30} {"10":>30} {"joknarf":<30} {"top":<130} {"10:10":<50} /bin/top\n'
        ps_out += f'{"40":>30} {"1":>30} {"root":<30} {"bash":<130} {"11:01":<50} -bash'
        print(ps_out)
        mock_runcmd.return_value = 0, ps_out
        mock_kill.return_value = True
        ptree = pgtree.Proctree()

        children = {
            '-1': ['0'],
            '0': ['1'],
            '1': ['10', '40'],
            '10': ['20', '30'],
        }
        ps_info = {
            '0': {
                'pid': '0',
                'ppid': '-1',
                'stime': 'stime',
                'user': 'user',
                'comm': 'ucomm',
                'args': 'args',
            },
            '1': {
                'pid': '1',
                'ppid': '0',
                'stime': 'Aug12',
                'user': 'root',
                'comm': 'init',
                'args': '/init',
            },
            '10': {
                'pid': '10',
                'ppid': '1',
                'stime': 'Aug12',
                'user': 'joknarf',
                'comm': 'bash',
                'args': '-bash',
            },
            '20': {
                'pid': '20',
                'ppid': '10',
                'stime': '10:10',
                'user': 'joknarf',
                'comm': 'sleep',
                'args': '/bin/sleep 60',
            },
            '30': {
                'pid': '30',
                'ppid': '10',
                'stime': '10:10',
                'user': 'joknarf',
                'comm': 'top',
                'args': '/bin/top',
            },
            '40': {
                'pid': '40',
                'ppid': '1',
                'stime': '11:01',
                'user': 'root',
                'comm': 'bash',
                'args': '-bash',
            },
        }
        pids_tree = {
            '10': ['20', '30'],
            '1': ['10'],
            '0': ['1'],
            '-1': ['0'],
        }
        selected_pids = ['30', '20', '10']
        ptree.print_tree(pids=['10'], child_only=True)
        print(ptree.pids_tree)
        self.assertEqual(ptree.children, children)
        self.maxDiff = None
        self.assertEqual(ptree.ps_info, ps_info)
        self.assertEqual(ptree.pids_tree, pids_tree)
        self.assertEqual(ptree.selected_pids, selected_pids)
        ptree.print_tree(pids=['10'], child_only=True, sig=15, confirmed=True)

    def test_main(self):
        """test"""
        print('main =========')
        pgtree.main([])

    def test_main2(self):
        """test"""
        print('main2 ========')
        pgtree.main(['-c', '-u', 'root', '-f', 'sshd'])
        pgtree.main(['sshd', '-cf', '-u', 'root'])

    @patch('os.kill')
    def test_main3(self, mock_kill):
        """test"""
        print('main3 ========')
        mock_kill.return_value = True
        pgtree.main(['-k', '-p', '1111'])
        pgtree.main(['-K', '-p', '1111'])

    def test_main4(self):
        """test"""
        print('main4 ========')
        try:
            pgtree.main(['-h'])
        except SystemExit:
            pass

    @patch('builtins.input')
    def test_main5(self, mock_input):
        """test"""
        print('main5 ========')
        mock_input.return_value = 'n'
        pgtree.main(['-k', 'sshd'])

    def test_main6(self):
        """test"""
        print('main6 ========')
        pgtree.main(['-a'])

    def test_main7(self):
        """test"""
        print('main7 ========')
        pgtree.main(['-C', 'y', '-O', '%cpu', 'init'])

    def test_ospgrep(self):
        """pgrep os"""
        print("test os pgrep")
        pgtree.main(['-C','y','-w','n','-f', '-i', '-u', 'root', '-x', '-t', 'pts/1', 'bash'])
        pgtree.main("-1")

    @patch.dict(os.environ, {"PGT_PGREP": "", "PGTREE": "-1"})
    def test_pgrep(self):
        """pgrep built-in"""
        print("test pgrep built-in")
        try:
            pgtree.main(['-R','-t', 'pts/1'])
        except SystemExit:
            pass
        pgtree.main(['-I','-C','n','-w','n','-f', '-i', '-u', 'root', '-x', '/sbin/init'])

    @patch('time.sleep')
    def test_watch(self, mock_sleep):
        """watch built-in"""
        print("test watch built-in")
        mock_sleep.return_value = True
        pgtree.main(['-W', 'bash'])

    @patch.dict(os.environ, {"PGT_COMM": "", "PGT_STIME": ""})
    def test_simpleps(self):
        pgtree.main([])

    def test_psfail(self):
        """test"""
        print('psfail ========')
        try:
            pgtree.main(['-O abcd'])
        except SystemExit:
            pass

    def test_threads(self):
        pgtree.main(["-T"])
