
############################################################
# Imports
############################################################

import sys
import random
import math
import Queue

############################################################
# Section 4: Dominoes Game
############################################################

def create_dominoes_game(rows, cols):
    return DominoesGame([[False for x in xrange(cols)] for y in xrange(rows)])

class DominoesGame(object):

    # Required
    def __init__(self, board):
        self.board = board
        self.rows = len(board)
        self.cols = len(board[0])
        self.moveout = None
        self.leaf_count = 0

    def get_board(self):
        return self.board

    def reset(self):
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                self.board[r][c] = False

    def is_legal_move(self, row, col, vertical):
        if vertical:
            if 0 <= row < self.rows-1 and 0 <= col < self.cols:
                return not self.board[row][col] and not self.board[row+1][col]
            return False
        else:
            if 0 <= row < self.rows and 0 <= col < self.cols-1:
                return not self.board[row][col] and not self.board[row][col+1]
            return False

    def legal_moves(self, vertical):
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                if self.is_legal_move(r, c, vertical):
                    yield (r, c)


    def perform_move(self, row, col, vertical):
        if vertical:
            self.board[row][col] = True
            self.board[row+1][col] = True
        else:
            self.board[row][col] = True
            self.board[row][col+1] = True


    def game_over(self, vertical):
        try:
            next(self.legal_moves(vertical))
            return False
        except StopIteration:
            return True


    def copy(self):
        return DominoesGame([[elem for elem in row] for row in self.board])


    def successors(self, vertical):

        for move in self.legal_moves(vertical):
            copy = self.copy()
            copy.perform_move(move[0], move[1], vertical)
            yield (move, copy)


    def get_random_move(self, vertical):
        return random.choice(list(self.legal_moves(vertical)))

    def get_h(self, vertical):
        return sum(1 for _ in self.legal_moves(vertical)) - sum(1 for _ in self.legal_moves(not vertical))

    # Required
    def get_best_move(self, vertical, limit):
        v = self.get_max_value(self, vertical, vertical, limit, -sys.maxint, sys.maxint)
        return (self.moveout, v, self.leaf_count)


    def get_max_value(self, root, root_vertical, vertical, limit, alpha, beta):
        if self.game_over(vertical) or limit == 0:
            root.leaf_count += 1
            return self.get_h(root_vertical)

        v = -sys.maxint
        for move, game in self.successors(vertical):
            # v = max(v, game.get_min_value(root, root_vertical, not vertical, limit-1, alpha, beta))
            g = game.get_min_value(root, root_vertical, not vertical, limit-1, alpha, beta)
            if v < g:
                self.moveout = move
                v = g
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v



    def get_min_value(self, root, root_vertical, vertical, limit, alpha, beta):
        if self.game_over(vertical) or limit == 0:
            root.leaf_count += 1
            return self.get_h(root_vertical)

        v = sys.maxint
        for move, game in self.successors(vertical):
            # v = min(v, game.get_max_value(root, root_vertical, not vertical, limit-1, alpha, beta))
            g = game.get_max_value(root, root_vertical, not vertical, limit-1, alpha, beta)
            if v > g:
                self.moveout = move
                v = g

            if v <= alpha:
                return v
            beta = min(beta, v)
        return v


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
