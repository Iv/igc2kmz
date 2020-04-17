import sys
import os

from igc2kmz.optimisation import OptimisationDeterministic, Optimisation
from igc2kmz.igc import IGC


BASE_PATH = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, BASE_PATH)

EXAMPLES_DIR = os.path.join(BASE_PATH, 'examples_jonatan')
Opt = OptimisationDeterministic

def main(argv):
    with open(os.path.join(EXAMPLES_DIR, '118_1.igc')) as f:
        igc = IGC(f)
        track = igc.track()
        opt = Opt(track)

        # d, start, finish = opt.find_max_distance()
        # print ("Max distance: %0.2f" % d)

        d, start, p1, p2 , finish = opt.find_max_free_flight()
        print ("Max free flight through up to tree points: %0.2f" % d)


if __name__ == "__main__":
    main(sys.argv)