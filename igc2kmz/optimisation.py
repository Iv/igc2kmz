from operator import itemgetter

from coord import Coord
from track import Track


SET_RADIUS = 500


class Set:
    center = None
    coords = [] 

    def __init__(self, coords):
        """
        :param Coord[] coords: list of coordinates
        """
        self.coords = coords

        lon_sum = 0
        lat_sum = 0
        ele_sum = 0
        for c in coords:
            lon_sum += c.lon
            lat_sum += c.lat
            ele_sum += c.ele
        n = len(coords)
        self.center = Coord(lat_sum/n, lon_sum/n, ele_sum/n)


class BaseOptimisation(object):
    track = None
    coords = []
    sets = []
    
    def __init__(self, track):
        """
        :param Track track: track to analyse
        """
        self.track = track
        self.coords = track.coords
        self.make_sets(radius=SET_RADIUS)


    def make_sets(self, radius=SET_RADIUS):
        self.sets = []
        c1 = self.coords[0]
        cs = [c1,]
        for i, c in enumerate(self.coords[1:]):
            if c1.distance_to(c) < radius:
                cs.append(c)
                flag = False
            else:
                self.sets.append(Set(cs))
                c1 = c
                cs = [c1,]
                flag = True
        if not flag:
            self.sets.append(Set(cs))


class OptimisationDeterministic(BaseOptimisation):
    def find_max_distance(self, coords=[]):
        if not coords:
            coords = self.coords

        distance = 0
        start = None
        finish = None
        n = len(coords)
        for i, c1 in enumerate(coords):
            if i < n:
                for j in range(i + 1, n):
                    c2 = coords[j]
                    d = c1.distance_to(c2)
                    if d > distance:
                        distance = d
                        start = c1
                        finish = c2

        return distance, start, finish
    
    def find_max_free_flight(self):
        distance = 0
        start = p1 = p2 = p3 = finish = None
        n = len(self.coords)
        for i, c1 in enumerate(self.coords):
            for j in range(i, n):
                for k in range(j,n):
                    for l in range(k, n):
                        for m in range(l, n):
                            c2 = self.coords[j]
                            c3 = self.coords[k]
                            c4 = self.coords[l]
                            c5 = self.coords[m]

                            d = c1.distance_to(c2) + c2.distance_to(c3) \
                                + c3.distance_to(c4) + c4.distance_to(c5)

                            if d > distance:
                                distance = d
                                start = c1
                                p1 = c2
                                p2 = c3
                                p3 = c4
                                finish = c5

        return distance, start, p1, p2, p3, finish
    

class Optimisation(BaseOptimisation):

    def find_max_distance(self):
        sets = []
        
        max_distance = 0
        for i, s1 in enumerate(self.sets):
            if i < len(self.sets):
                for j, s2 in enumerate(self.sets[i+1:]):
                    d = s1.center.distance_to(s2.center)
                    if max_distance < d:
                        max_distance = d
                    
                    if abs(max_distance - d) < 4*SET_RADIUS:
                        sets.append((d, s1, s2))
                        

        max_distance = 0
        for s in sets:
            if max_distance < s[0]:
                max_distance = s[0]

        sets = filter(lambda item: abs(max_distance - item[0]) < 4*SET_RADIUS, sets)

        coords = []
        distance = 0
        start = None
        finish = None
        for s in sets:
          for c1 in s[1].coords:
              for c2 in s[2].coords:
                  d = c1.distance_to(c2)
                  if d > distance:
                      distance = d
                      start = c1
                      finish = c2

        return distance, start, finish

    def find_max_free_flight(self):
        distance = 0
        start = p1 = p2 = p3 = finish = None
        n = len(self.coords)

        sets = []
        ns = len(self.sets)
        max_distance = 0
        for i, s1 in enumerate(self.sets):
            for j in range(i, ns):
                for k in range(j, ns):
                    for l in range(k, ns):
                        for m in range(l, ns):
                            s2 = self.sets[j]
                            s3 = self.sets[k]
                            s4 = self.sets[l]
                            s5 = self.sets[m]
                            d = (
                                s1.center.distance_to(s2.center) +
                                s2.center.distance_to(s3.center) +
                                s3.center.distance_to(s4.center) +
                                s4.center.distance_to(s5.center)
                            )

                            if max_distance < d:
                                max_distance = d

                            if abs(max_distance - d) < 18 * SET_RADIUS:
                                sets.append((d, s1, s2, s3, s4, s5))

        max_distance = 0
        for s in sets:
            if max_distance < s[0]:
                max_distance = s[0]

        sets = filter(lambda item: abs(max_distance - item[0]) < 18 * SET_RADIUS, sets)
        
        distance = 0
        start = p1 = p2 = p3 = finish = None
        
        for s in sets:
            for c1 in s[1].coords:
                for c2 in s[2].coords:
                    for c3 in s[3].coords:
                        for c4 in s[4].coords:
                            for c5 in s[5].coords:
                                d = (
                                    c1.distance_to(c2) +
                                    c2.distance_to(c3) +
                                    c3.distance_to(c4) +
                                    c4.distance_to(c5)
                                )

                                if d > distance:
                                    distance = d
                                    start, p1, p2, p3, finish = c1, c2, c3, c4

        return start, p1, p2, p3, finish
