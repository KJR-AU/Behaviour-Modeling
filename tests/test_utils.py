# coding=utf-8
'''
Unit Tests for functions in the utils.py
'''
import unittest
import sys
import os
import random
from pprint import pformat

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

_DEBUG = True
import utils


# noinspection PyMethodMayBeStatic
class ReversePath(unittest.TestCase):
    def test_example(self):
        '''
        e.g.      {A: [B, D], B: [C]}       # A ─┬─> B ──> C
                                            #    └─> D
        becomes   {C: [B], B: [A], D: [A]}  # A <─┬─ B <── C
                                            #     └─ D
        '''
        backward = {'C': ['B'], 'B': ['A'], 'D': ['A']}
        forward = {'A': ['B', 'D'], 'B': ['C']}
        self.assertEqual(backward, utils.reverse_paths(forward))
        self.assertEqual(forward, utils.reverse_paths(backward))

    def test_Simple(self):
        branches = {10: [11]}
        self.assertEqual({11: [10]}, utils.reverse_paths(branches))

    def test_Fork(self):
        branches = {10: [11, 12]}
        self.assertEqual({11: [10], 12: [10]}, utils.reverse_paths(branches))

    def test_Loop(self):
        branches = {10: [11, 12], 12: [12, 13]}
        self.assertEqual({11: [10], 12: [10, 12], 13: [12]}, utils.reverse_paths(branches))

    def test_3_Deep(self):
        branches = {10: [11, 12], 12: [14, 13]}
        self.assertEqual({11: [10], 12: [10], 14: [12], 13: [12]}, utils.reverse_paths(branches))

    def test_Multiple_Start_Points(self):
        branches = {1: [2], 4: [2], 2: [3, 5], 3: [6], 6: [7]}
        self.assertEqual({7: [6], 6: [3], 3: [2], 5: [2], 2: [1, 4]}, utils.reverse_paths(branches))

    def test_example_branched(self):
        '''
        e.g.       A ─┬─> B ─┬─> C
                      └─> D ─┘
        becomes    A <─┬─ B <─┬─ C
                       └─ D <─┘
        '''
        forward = {'A': ['B', 'D'], 'B': ['C'], 'D': ['C']}
        backward = {'C': ['B', 'D'], 'B': ['A'], 'D': ['A']}
        actualbackward = utils.reverse_paths(forward)
        actualforward = utils.reverse_paths(backward)
        self.assertEqual(backward, actualbackward)
        self.assertEqual(forward, actualforward)


# noinspection PyMethodMayBeStatic
class SortNodesByPath(unittest.TestCase):
    def test_simple(self):
        '''
        3 -> 2 -> 1
        '''
        expected = [3, 2, 1]
        edges = {2: [1], 3: [2]}
        self.assertEqual(expected, utils.nodes_by_path(edges))

    def test_order1(self):
        '''
        1 ──> 2 ─┬─> 3 ──> 7
                 └─> 4 ──> 5 ──> 6
        '''
        expected = [1, 2, 3, 7, 4, 5, 6]
        edges = {1: [2], 2: [3, 4], 4: [5], 5: [6], 3: [7]}

        actual = utils.nodes_by_path(edges)
        self.assertEqual(expected, actual)

    def test_order2(self):
        '''
        1 ──> 2 ─┬─> 3 ──> 7
                 └─> 4 ──> 5 ──> 6
        '''
        expected = [1, 2, 4, 5, 6, 3, 7]
        edges = {1: [2], 2: [4, 3], 4: [5], 5: [6], 3: [7]}

        actual = utils.nodes_by_path(edges)
        self.assertEqual(expected, actual)

    def test_extra2(self):
        '''
        Two separate lists are extracted if the paths do not connect

              1 ──> 2 ──> 3
              4 ──> 5 ──> 6
        '''
        expected1 = [1, 2, 3]
        expected2 = [4, 5, 6]
        edges = {1: [2], 2: [3], 4: [5], 5: [6]}

        actual = utils.nodes_by_path(edges)

        # paths are kept togeather but order is not guaranted
        self.assertIn(expected1, [actual[0:3], actual[3:7]])
        self.assertIn(expected2, [actual[0:3], actual[3:7]])

    def test_loop(self):
        '''
              1 ─┬─> 2 ──┬─> 3 ──> 5
                 │       │
                 └── 4 <─┘

        NOTE: Loops and everything down stream are lost
        '''
        expected = [1]
        edges = {1: [2], 2: [3, 4], 3: [5], 4: [2]}

        actual = utils.nodes_by_path(edges)

        # paths are kept togeather but order is not guaranted
        self.assertEqual(expected, actual)

    def test_shared_node(self):
        '''
              1 ─┐      ┌─> 3
                 ├─> 2 ─┤
              4 ─┘      └─> 6
        '''
        edges = {1: [2], 2: [3, 6], 4: [2]}

        actual = utils.nodes_by_path(edges)

        # branches are arbitrarily ordered each side of the shared node
        self.assertIn(1, actual[0:2])
        self.assertIn(4, actual[0:2])
        self.assertIn(2, actual[2:3])
        self.assertIn(3, actual[3:6])
        self.assertIn(6, actual[3:6])


if __name__ == '__main__':
    unittest.main()
