
############################################################
# Imports
############################################################

import sys
import random
import math
import Queue

############################################################
# Section 1: Tile Puzzle
############################################################

def create_tile_puzzle(rows, cols):
    board = [range(cols*r+1, cols*r+cols+1) for r in xrange(rows)]
    board[rows-1][cols-1] = 0
    
    return TilePuzzle(board)
    
class TilePuzzle(object):
    
    # Required
    def __init__(self, board, blank=None):
        self.board = board
        self.row_num = len(board)
        self.col_num = len(board[0])
        self.parent = None
        self.movein = ""
        self.cost = 0
        if blank != None:
            self.blank = blank
        else:
            try:
                self.blank = next([self.board.index(row),row.index(elem)]
                for row in self.board for elem in row if elem == 0)
            except StopIteration:
                print "Unable to create puzzle. No blank tile was found."
                raise
    
    def __cmp__(self, other):
            return cmp(self.get_md() + self.cost, other.get_md() + other.cost)
    
    def get_md(self):
        total_md = 0
                
        for r in xrange(self.row_num):
            for c in xrange(self.col_num):
                target = self.board[r][c]
                if target == 0: continue
                md = abs(r - (target-1)/self.col_num) + abs(c - (target-1)%self.col_num)
                # print str(r) + "," + str(c) + ": " + str(md)
                total_md += md
                
        return total_md
        
        
    def get_board(self):
        return self.board

        
    def get_mirror(self, move):
        mirror_move = {"left":"right", "right":"left", "up":"down", "down":"up", "":""}
        return mirror_move[move]

        

    def perform_move(self, direction):
        r = self.blank[0]
        c = self.blank[1]
        if direction == "right":
            if c == self.col_num-1: return False
            else:
                self.blank[1] += 1
                self.board[r][c], self.board[r][c+1] = self.board[r][c+1], self.board[r][c]
                return True
        elif direction == "left":
            if c == 0: return False
            else:
                self.blank[1] -= 1
                self.board[r][c], self.board[r][c-1] = self.board[r][c-1], self.board[r][c]
                return True
        elif direction == "up":
            if r == 0: return False
            else:
                self.blank[0] -= 1
                self.board[r][c], self.board[r-1][c] = self.board[r-1][c], self.board[r][c]
                return True
        elif direction == "down":
            if r == self.row_num-1: return False
            else:
                self.blank[0] += 1
                self.board[r][c], self.board[r+1][c] = self.board[r+1][c], self.board[r][c]
                return True
        else: return False
                

    def scramble(self, num_moves):
        moves = ["right", "left", "up", "down"]
        for _ in xrange(num_moves):
            self.perform_move(random.choice(moves))

    def is_solved(self):
        if self.board[self.row_num-1][self.col_num-1] != 0: return False

        i = 1
        max = self.row_num * self.col_num
        
        for r in xrange(self.row_num):
            for c in xrange(self.col_num):
                if i == max: return True
                if i != self.board[r][c]: return False
                i += 1
                
    def copy(self):
        # print "befre cpy: " + str(self.board)
        return TilePuzzle([[elem for elem in row] for row in self.board], [self.blank[0],self.blank[1]])

    def successors(self):
        for move in ["up","down","left","right"]:
            copy = self.copy()
            if copy.perform_move(move): yield (move,copy)

    # Required
    def find_solutions_iddfs(self):
        found = False
        i = 1
        
        # assume there is always an answer
        while not found:
            for ans in self.iddfs_helper(i, []):
                found = True
                yield ans
            i += 1
            
    def iddfs_helper(self, limit, moves):
        if limit == 1:
            #do checking here
            if not moves:
                for direction, puzzle in self.successors():
                    if puzzle.is_solved():
                        yield [direction]
            else:
                for direction, puzzle in self.successors():
                    if direction != self.get_mirror(moves[-1]) and puzzle.is_solved():
                        yield moves+[direction]
        else:
            #no checking here
            if not moves:
                for direction, puzzle in self.successors():
                    for ans in puzzle.iddfs_helper(limit-1, [direction]):
                        yield ans
            else:
                for direction, puzzle in self.successors():
                    if direction != self.get_mirror(moves[-1]):
                        for ans in puzzle.iddfs_helper(limit-1, moves+[direction]):
                            yield ans
                            
        
    # Required
    def find_solution_a_star(self):
        q = Queue.PriorityQueue()
        q.put(self)

        while not q.empty():
            target = q.get()
            if target.is_solved(): return self.backtrace(target)
            # list = list(target.successors())
            for direction, puzzle in target.successors():
                if direction != target.get_mirror(target.movein):
                    puzzle.parent = target
                    puzzle.movein = direction
                    puzzle.cost = target.cost + 1
                    q.put(puzzle)
        
        return None
        
    def backtrace(self, other):
        trace = []
        while other is not self:
            trace.append(other.movein)
            other = other.parent
        
        return trace[::-1]



# a = TilePuzzle([[3,4],[4,0]])
# print a.blank
#
# b = create_tile_puzzle(3,3)
# print b.board
# print b.perform_move("down")
# print b.board
# print b.perform_move("up")
# print b.board
# b.scramble(50)
# print b.board
# print
# p = TilePuzzle([[1, 2], [3, 0]])
# r = p.copy()
# print p.board
# print r.board
# r.scramble(50)
# print p.board
# print r.board
# print
# p = TilePuzzle([[1,2,3], [4,0,8], [7,6,5]])
# solutions = p.find_solutions_iddfs()
# print list(solutions)
# print
# a = TilePuzzle([[1,2,3], [4,0,5], [6,7,8]])
# print a.find_solution_a_star()
# a = TilePuzzle([[1, 2, 3], [4, 5, 0], [6, 7, 8]])
# a.perform_move("left")
# print a.get_board()
# a = TilePuzzle([[1, 2, 3], [4, 5, 0], [6, 7, 8]])
# a.perform_move("right")
# print a.get_board()
# a = TilePuzzle([[1, 2, 3], [4, 5, 0], [6, 7, 8]])
# a.perform_move("up")
# print a.get_board()
# a = TilePuzzle([[1, 2, 3], [4, 5, 0], [6, 7, 8]])
# a.perform_move("down")
# print a.get_board()