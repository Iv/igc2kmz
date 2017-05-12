import os.path
import sys
import unittest

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, BASE_DIR)

EXAMPLES_DIR = os.path.join(BASE_DIR, 'examples_jonatan')
ACCURACY = 2

import igc2kmz.igc
from igc2kmz.optimisation import OptimisationDeterministic


class TestTrackDet(unittest.TestCase):
    FILE = '118_1.igc'

    def get_file_name(self):
        return os.path.join(EXAMPLES_DIR, self.FILE)

    def get_igc(self):
        igc = None
        try:
            igc = igc2kmz.igc.IGC(open(self.get_file_name()))
        except igc2kmz.igc.SyntaxError, line:
            print "%s" % line
        return igc
        
    def test_points_count(self):
        igc = self.get_igc()
        track = igc.track()

        self.assertEqual(len(track.coords), 5890)
        
    def test_find_max_distance(self):
        o = OptimisationDeterministic(self.get_igc().track())
        distance, start, finish = o.find_max_distance()
        self.assertTrue(abs(distance - 108047) < ACCURACY)
