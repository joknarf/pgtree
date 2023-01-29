"""pgtree tests"""
import os
import sys
import unittest
from unittest.mock import patch
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import pgtree
#from unittest.mock import MagicMock, Mock, patch

class ProctreeTest(unittest.TestCase):
    """tests for pgtree"""
    @patch('os.kill')
    @patch('pgtree.pgtree.runcmd')
    def test_tree1(self, mock_runcmd, mock_kill):
        """test"""
        ps_out = 4*(130*'-'+' ')
        print("tree: =======")
        ps_out = 4*(130*'-'+' ') + "\n"
        ps_out += f'{"1":>130} {"0":>130} {"root":<130} {"Aug12":<130} {"init":<130} /init\n'
        ps_out += f'{"10":>130} {"1":>130} {"joknarf":<130} {"Aug12":<130} {"bash":<130} -bash\n'
        ps_out += f'{"20":>130} {"10":>130} {"joknarf":<130} {"10:10":<130} {"sleep":<130} /bin/sleep 60\n'
        ps_out += f'{"30":>130} {"10":>130} {"joknarf":<130} {"10:10":<130} {"top":<130} /bin/top\n'
        ps_out += f'{"40":>130} {"1":>130} {"root":<130} {"11:01":<130} {"bash":<130} -bash'
        print(ps_out)
#        ps_out = """-------------------- -------------------- ------------------------------ -------------------------------------------------- ---------------------------------------------------------------------------------------------------------------------------------- ---
#                   1                    0 root                                                                        Aug12 init                                                                                                                               /init
#                  10                    1 joknarf                                                                     Aug12 bash                                                                                                                               -bash
#                  20                   10 joknarf                                                                     10:10 sleep                                                                                                                              /bin/sleep 60
#                  30                   10 joknarf                                                                     10:10 top                                                                                                                                /bin/top
#                  40                    1 root                                                                        11:01 bash                                                                                                                               -bash"""
        mock_runcmd.return_value = ps_out
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
        pgtree.main(['-O', '%cpu', 'bash'])

    def test_ospgrep(self):
        """pgrep os"""
        print("test os pgrep")
        pgtree.main(['-C','y','-w','n','-f', '-i', '-u', 'root', '-x', '-t', 'pts/1', 'bash'])
        pgtree.main("-1")

    def test_pgrep(self):
        """pgrep built-in"""
        print("test pgrep built-in")
        try:
            pgtree.main(['-R','-t', 'pts/1'])
        except SystemExit:
            pass
        pgtree.main(['-R','-I','-C','n','-w','n','-f', '-i', '-u', 'root', '-x', '/sbin/init'])


if __name__ == "__main__":
    unittest.main(failfast=True)
