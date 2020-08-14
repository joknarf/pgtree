import unittest
from unittest.mock import MagicMock, Mock, patch
from pgtree import Proctree

class ProctreeTest(unittest.TestCase):
    @patch('pgtree.runcmd')
    def test_tree1(self, mock_runcmd):
        ps = """  PID  PPID USER     COMMAND         COMMAND
    1     0 root     init            /init
   10     1 joknarf  bash            -bash
   20    10 joknarf  sleep           /bin/sleep 60
   30    10 joknarf  top             /bin/top
   40     1 root     bash            -bash"""
        mock_runcmd.return_value = (0, ps, '')
        ptree = Proctree(pids=['10'])

        children = {
                '0': ['1'],
                '1': ['10','40'],
                '10': ['20','30'],
        }
        ps_info = {
                '1': {
                    'ppid': '0',
                    'user': 'root',
                    'comm': 'init',
                    'args': '/init',
                },
                '10': {
                    'ppid': '1',
                    'user': 'joknarf',
                    'comm': 'bash',
                    'args': '-bash',
                },
                '20': {
                    'ppid': '10',
                    'user': 'joknarf',
                    'comm': 'sleep',
                    'args': '/bin/sleep 60',
                },
                '30': {
                    'ppid': '10',
                    'user': 'joknarf',
                    'comm': 'top',
                    'args': '/bin/top',
                },
                '40': {
                    'ppid': '1',
                    'user': 'root',
                    'comm': 'bash',
                    'args': '-bash',
                },
        }
        pids_tree = {
                '10': ['20', '30'],
                '1': ['10'],
                '0': ['1'],
        }
        selected_pids = [ '30', '20', '10' ]
        print(ptree.pids_tree)
        ptree.print_tree(True)
        self.assertEqual(ptree.children, children)
        self.assertEqual(ptree.ps_info, ps_info)
        self.assertEqual(ptree.pids_tree, pids_tree)
        self.assertEqual(ptree.selected_pids, selected_pids)