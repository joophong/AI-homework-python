
############################################################
# Imports
############################################################

import time
import random

############################################################
# Section 1: Sudoku
############################################################

def sudoku_cells():
    return [(row, col) for row in xrange(9) for col in xrange(9)]

def sudoku_arcs():
    box_map = {0:0, 1:0, 2:0, 3:3, 4:3, 5:3, 6:6, 7:6, 8:6}
    list = []

    for row, col in sudoku_cells():
        for c in xrange(9):
            if c != col:
                list.append(((row, col), (row, c)))
        for r in xrange(9):
            if r != row:
                list.append(((row, col), (r, col)))

        r_start, c_start = box_map[row], box_map[col]
        for r in xrange(r_start, r_start+3):
            for c in xrange(c_start, c_start+3):
                if r != row and c != col:
                    list.append(((row, col), (r, c)))

    return list


def read_board(path):
    dic = {}
    with open(path, 'r+') as f:
        row = 0
        for line in f:
            col = 0
            for num in line.rstrip('\r\n'):
                if num == '*':
                    dic[(row, col)] = set([1, 2, 3, 4, 5, 6, 7, 8, 9])
                else:
                    dic[(row, col)] = set([int(num)])
                col += 1
            row += 1

    return dic

def init_counter(counter):
    for i in xrange(1, 10):
        counter[i] = [0, -1]

class Sudoku(object):

    CELLS = sudoku_cells()
    ARCS = sudoku_arcs()

    def __init__(self, board):
        self.board = board
        self.modified = True

    def __str__(self):
        a = []
        for x in xrange(9):
            for y in xrange(9):
                if len(self.board[(x, y)]) != 1:
                    a.append("x")
                    continue
                a.append(str(list(self.board[(x, y)])[0]))
            a.append('\r\n')

        return ''.join(a)

    def get_values(self, cell):
        return self.board[cell]

    def copy(self):
        return Sudoku({t: set(self.board[t]) for t in self.board})


    def set_manually(self, cell, number):
        self.board[cell] = set([number])
        for c1, c2 in self.ARCS:
            if c1 == cell:
                if number in self.board[c2]:
                    self.board[c2].remove(number)


    def remove_inconsistent_values(self, cell1, cell2):
        cell2_list = self.board[cell2]
        if cell1 == cell2:
            return False

        removed = False

        cell1_list = self.board[cell1]
        for p1 in tuple(cell1_list):
            if len([_ for _ in cell2_list if _ != p1]) > 0:
                continue
            else:
                removed = True
                self.modified = True
                cell1_list.remove(p1)

        return removed

    def remove_inconsistent_values_recursive(self, cell1, cell2):
        if self.remove_inconsistent_values(cell1, cell2):
            for x, y in self.ARCS:
                if x == cell1 and len(self.board[y]) != 1:
                    self.remove_inconsistent_values_recursive(y, cell1)

    def is_valid(self):

        for i in xrange(9):
            pool = range(1, 10)
            for c in xrange(9):
                nums = self.board[(i, c)]
                if len(nums) == 1:
                    try:
                        pool.remove(list(nums)[0])
                    except ValueError:
                        return False

            pool = range(1, 10)
            for r in xrange(9):
                nums = self.board[(r, i)]
                if len(nums) == 1:
                    try:
                        pool.remove(list(nums)[0])
                    except ValueError:
                        return False

        for i in xrange(0, 27, 3):
            r, c = 3*(i/9), i%9
            pool = range(1, 10)
            for r_os in xrange(3):
                for c_os in xrange(3):
                    nums = self.board[(r+r_os, c+c_os)]
                    if len(nums) == 1:
                        try:
                            pool.remove(list(nums)[0])
                        except ValueError:
                            return False

        return True


    def infer_ac3(self):
        for cell1 in self.CELLS:
            if len(self.board[cell1]) != 1:
                for x, cell2 in self.ARCS:
                    if x == cell1:
                     self.remove_inconsistent_values_recursive(cell1, cell2)

    def infer_supplement(self):
        counter = {}

        for i in xrange(9):
            init_counter(counter)
            singles = set()
            for c in xrange(9):
                nums = self.board[(i, c)]
                if len(nums) == 1:
                    singles.add(list(nums)[0])
                    continue
                for cand in nums:
                    counter[cand][0] += 1
                    counter[cand][1] = c
            for num in counter:
                if counter[num][0] == 1 and num not in singles:
                    self.board[(i, counter[num][1])] = set([num])
                    self.modified = True

            init_counter(counter)
            singles = set()
            for r in xrange(9):
                nums = self.board[(r, i)]
                if len(nums) == 1:
                    singles.add(list(nums)[0])
                    continue
                for cand in nums:
                    counter[cand][0] += 1
                    counter[cand][1] = r
            for num in counter:
                if counter[num][0] == 1 and num not in singles:
                    self.board[(counter[num][1], i)] = set([num])
                    self.modified = True

        for i in xrange(0, 27, 3):

            init_counter(counter)
            singles = set()
            r, c = 3*(i/9), i%9
            for r_os in xrange(3):
                for c_os in xrange(3):
                    nums = self.board[(r+r_os, c+c_os)]
                    if len(nums) == 1:
                        singles.add(list(nums)[0])
                        continue
                    for cand in nums:
                        counter[cand][0] += 1
                        counter[cand][1] = (r_os, c_os)
            for num in counter:
                if counter[num][0] == 1 and num not in singles:
                    offset = counter[num][1]
                    self.board[(r+offset[0], c+offset[1])] = set([num])
                    self.modified = True


    def infer_improved(self):
        while self.modified:
            self.modified = False
            self.infer_ac3()
            self.modified = False
            self.infer_supplement()



    def infer_with_guessing(self):
        self.infer_improved()
        unsolved_cells = [cell for cell in self.CELLS if len(self.board[cell]) != 1]

        if not unsolved_cells:
            if self.is_valid():
                return self.board
            else:
                return

        cell = random.choice(unsolved_cells)

        for cand in self.board[cell]:
            copy = self.copy()
            copy.set_manually(cell, cand)

            answer = copy.infer_with_guessing()
            if answer:
                self.board = answer
                return self.board



# sudoku = Sudoku(read_board("sudoku/hard2.txt"))
#
# start = time.time()
# for i in xrange(20):
#     sudoku.infer_with_guessing()
#
# # print sudoku
# print time.time() - start
# print sudoku