
############################################################
# Imports
############################################################

import sys
import random
import math
import Queue

############################################################
# Section 2: Grid Navigation
############################################################

def find_path(start, goal, scene):
    rows = len(scene)
    cols = len(scene[0])
    obstacles = list(get_obstacles(scene))
    visited = set()
    q = Queue.PriorityQueue()
    q.put(Point(start, goal))
    visited.add(start)

    while not q.empty():
        target = q.get()
        if target.coord == goal: return backtrace(start, target)
        for cand in candidates(target.coord, rows, cols):
            if cand not in obstacles and cand not in visited:
                p = Point(cand, goal)
                p.parent = target
                p.cost = get_distance(p.coord, target.coord) + target.cost
                q.put(p)
                visited.add(cand)

    return None

def backtrace(start, target):
    trace = []
    while target.coord != start:
        trace.append(target.coord)
        target = target.parent

    trace.append(start)
    return trace[::-1]


def get_distance(p1, p2):
    return math.sqrt((p2[1]-p1[1])**2 + (p2[0]-p1[0])**2)

def get_obstacles(scene):
        for r in xrange(len(scene)):
                for c in xrange(len(scene[0])):
                    if scene[r][c]:
                        yield (r, c)

def candidates(s, rows, cols):
        for r, c in [(s[0]+1, s[1]), (s[0], s[1]+1), (s[0]-1, s[1]), (s[0], s[1]-1),
                  (s[0]+1, s[1]+1), (s[0]-1, s[1]-1), (s[0]+1, s[1]-1), (s[0]-1, s[1]+1)]:
            if 0 <= r < rows and 0 <= c < cols:
                yield (r, c)

class Point(object):

    # Required
    def __init__(self, coordinates, goal):
        self.coord = coordinates
        self.cost = 0
        self.dist_to_goal = get_distance(coordinates, goal)
        self.parent = self

    def __cmp__(self, other):
        return cmp(self.cost + self.dist_to_goal, other.cost + other.dist_to_goal)




############################################################
# Section 3: Linear Disk Movement
############################################################

def solve_distinct_disks(length, n):
    puzzle = DiskPuzzle(create_disk_array(length, n), n)
    return puzzle.find_solution();

class DiskPuzzle(object):

    def __init__(self, array, n):
        self.array = array
        self.length = len(array)
        self.disk_count = n
        self.set_parent(None)
        self.set_movein(None)
        self.cost = 0

    def __cmp__(self, other):
            return cmp(self.get_h() + self.cost, other.get_h() + other.cost)

    def set_parent(self, parent):
        self.parent = parent

    def set_movein(self, movein):
        self.movein = movein

    def get_parent(self):
        return self.parent

    def get_movein(self):
        return self.movein

    def get_array(self):
        return self.array

    def get_h(self):
        h = 0
        for i in xrange(self.length):
            disk = self.array[i]
            if disk == 0:
                continue
            goal_i = self.length - disk
            h += abs(goal_i - i)

        return h

    def perform_move(self, i, is_forward):

        if self.array[i] == 0:
            return None

        if is_forward:
            if i+1 == self.length:
                return None

            if self.array[i+1] != 0:
                if i+2 == self.length or self.array[i+2] != 0:
                    return None
                else:
                    self.array[i], self.array[i+2] = self.array[i+2], self.array[i]
                    return i+2
            else:
                self.array[i], self.array[i+1] = self.array[i+1], self.array[i]
                return i+1

        else:
            if i-1 < 0:
                return None
            if self.array[i-1] != 0:
                if i-2 < 0 or self.array[i-2] != 0:
                    return None
                else:
                    self.array[i], self.array[i-2] = self.array[i-2], self.array[i]
                    return i-2
            else:
                self.array[i], self.array[i-1] = self.array[i-1], self.array[i]
                return i-1



    def is_solved(self):
        for i in xrange(-1, -(self.disk_count+1), -1):
            if self.array[i] != -i:
                return False

        for j in xrange(-(self.disk_count+1), -self.length, -1):
            print j
            if self.array[j] != 0:
                return False

        return True


    def copy(self):
        return DiskPuzzle([elem for elem in self.array], self.disk_count)

    def successors(self):

        for s in xrange(self.length):
            for forward in [True, False]:
                copy = self.copy()
                t = copy.perform_move(s, forward)

                if t is None:
                    continue
                else:
                    # print str(self.array) + " -> " + str((s, t)) + str(copy.array)
                    if self.movein != (t, s):
                        yield ((s, t), copy)


    def find_solution(self):
        q = Queue.PriorityQueue()
        q.put(self)

        while not q.empty():
            target = q.get()
            if target.is_solved():
                return self.backtrace(target)
            for move, puzzle in target.successors():
                puzzle.set_parent(target)
                puzzle.set_movein(move)
                puzzle.cost = target.cost + 1
                q.put(puzzle)

        return None

    def backtrace(self, other):
        trace = []
        while other is not self:
            trace.append(other.get_movein())
            other = other.get_parent()

        return trace[::-1]

def create_disk_array(length, n):
    array = [0] * length
    for i in xrange(n):
        array[i] = i + 1

    return array



# scene = [[False, False, True, False], [True, False, True, False], [True, False, True, False], [True, False, True, False], [True, False, True, False],[True, True, False, False]]
# print find_path((0, 0), (0, 3), scene)

# print solve_distinct_disks(4, 3)

# g = DominoesGame([[False, False, False], [False, False, False], [False, False, False]])
# g.perform_move(0, 1, True)
# print g.get_random_move(True)
# for m, new_g in g.successors(True):
#     print m, new_g.get_board()


# print g.get_best_move(True, 1)
# print g.get_best_move(False, 2)
# q = Queue.PriorityQueue()
# q.put(Point((0,0), (9,9)))
# q.put(Point((1,0), (9,9)))
# print q.get().coord
