#!/usr/bin/env python2

import datetime
from copy import deepcopy
from random import choice, shuffle
from time import time, sleep

MAX_REWARD = 3 * 68
MIN_REWARD = -MAX_REWARD

class Team36:

    def __init__(self):
        self.player = 'x'
        self.game_start = datetime.datetime.now()
        self.wins = 0
        self.win_history = {'x': 0, 'o': 0}
        self.max_depth = 5

    def move(self, a_board, old_move, flag):
        '''
                @param a_board -> Actual board NEVER mutate
                @param old_move -> The last move played
                @param flag -> String: current_player
                @return best_move -> Tuple (r, c)
        '''

        self.start_time = time()

        self.board = deepcopy(a_board)
        self.player = flag
        self.alpha = 2 * MIN_REWARD
        self.beta = 2 * MAX_REWARD

        # check small board wins first
        wins = [self._has_won((r, c), self.player)
                for c in range(4) for r in range(4)]
        if any(wins) and len(wins) > self.wins:
            self.wins = len(wins)
        self.win_history = {'x': 0, 'o': 0}

        best_move, best_score = self.minimax(old_move, self.player, 1)

        self.end_time = time()
        d_t = self.end_time - self.start_time

        # if d_t < 0.25 * 15:
        #     self.max_depth += 2
        # elif d_t > 0.95 * 15:
        #     self.max_depth -= 1

        print("t(m, d) :", d_t, self.max_depth)
        # sleep(1)

        return best_move

    def minimax(self, old_move, current_player, depth, maximizing_player=None,
                alpha=None, beta=None, max_depth=None):
        '''
                @param old_move -> the last move played
                @param current_player -> the player for the current chance
                @param maximizing_player -> our player
                @param alpha -> alpha beta pruning
                @param beta -> alpha beta pruning
                @param depth -> current depth
                @param max_depth -> max_depth
                @return (best_score, best_move) -> tuple
        '''

        # initial parameter filling
        if maximizing_player is None:
            maximizing_player = self.player
        if alpha is None:
            alpha = self.alpha
        if beta is None:
            beta = self.beta
        if max_depth is None:
            max_depth = self.max_depth

        # quit if the time has exceeded
        if(time() - self.start_time > 15):
            return old_move, 0

        # if winner, previous move to be rewarded
        winner, status = self.board.find_terminal_state()
        if status == "WON":
            self.win_history['x'] = 0
            self.win_history['o'] = 0
            if current_player == maximizing_player:
                return old_move, MAX_REWARD
            return old_move, MIN_REWARD

        elif status == "DRAW":
            return old_move, 0


        # if max depth reached pop out
        if depth == max_depth:
            return old_move, 0

        # current round common settings
        if current_player == maximizing_player:
            best_val =  MIN_REWARD
        else:
            best_val = MAX_REWARD


        # find new moves
        valid_moves = self.board.find_valid_move_cells(old_move)
        shuffle(valid_moves)  # insert the heuristic here
        if not len(valid_moves): valid_moves = self.board.find_valid_move_cells((-1, -1))
        # set the current value (this move will be checked next iteration)

        # value evaluating the current_move on
        # the basis of the future moves

        current_value = 0
        move_scores = []
        for cur_move in valid_moves:
            c_r, c_c = cur_move
            has_won = self._has_won(
                (c_r / 4, c_c / 4), current_player)
            self.board.board_status[c_r][c_c] = current_player
            # self.board.print_board()

            # default next player
            if current_player == 'x':
                next_player = 'o'
            else:
                next_player = 'x'

            if has_won == True:
                # if current_player has won the block
                self.win_history[current_player] += 1
                if self.win_history[current_player] <= 2:
                    next_player = current_player

                self.board.block_status[c_r / 4][c_c / 4] = current_player
                next_move, current_value = self.minimax(cur_move, next_player,
                    depth + 1, maximizing_player, alpha, beta, max_depth)
                self.board.block_status[c_r / 4][c_c / 4] = '-'

                if current_player == maximizing_player:
                    current_value -= (1 / depth) * MAX_REWARD
                else:
                    current_value += (1 / depth) * MIN_REWARD

            elif has_won == False:
                # if the board has been drawn

                self.board.block_status[c_r / 4][c_c / 4] = 'd'
                next_move, current_value = self.minimax(
                    cur_move, next_player, depth + 1, maximizing_player, alpha, beta, max_depth)
                self.board.block_status[c_r / 4][c_c / 4] = '-'

            elif has_won is None:
                self.board.block_status[c_r / 4][c_c / 4] = '-'
                next_move, current_value = self.minimax(
                    cur_move, next_player, depth + 1, maximizing_player, alpha, beta, max_depth)

            del next_move
            self.board.board_status[c_r][c_c] = '-'
            move_scores.append((cur_move, current_value))
            # alpha beta pruning
            # setting of best_value
            is_max = (current_player == maximizing_player)
            if is_max and current_value > best_val:
                best_move = cur_move
                best_val = current_value
            elif (not is_max) and current_value < best_val:
                best_move = cur_move
                best_val = current_value

            if is_max:
                alpha = max(alpha, best_val)
            else:
                beta = min(beta, best_val)

            if (alpha > beta):
                break
        try:
            best_move[0] == 1
        except NameError:
            sleep(2)
            print(move_scores)
            best_move, best_score = sorted(move_scores, key=lambda x: x[-1], reverse=(current_player == maximizing_player))[0]
        return best_move, best_val

    def heuristic(self, board, pot_mov):
        '''
                @param board -> board object
                @param pot_move -> potential move
                @return score -> score of the current move
        '''
        pass

    def _has_won(self, move, current_player):
        '''
                @param move -> tuple: the (x, y) of the move played
                @param current_player -> String: The player who just moved
                @return Boolean/None
                                -> True: Current has made a win combo
                                -> False: Other player won
                                -> None: Board is drawn
        '''
        _b = self.board.board_status
        _r, _c = tuple(map(lambda x: 4 * int(x), move))

        # check for horizontal or vertical
        is_normal = False
        for _ in range(4):
            if ((_b[_r + _][_c] == _b[_r + _][_c + 1] == _b[_r + _][_c + 2] == _b[_r + _][_c + 3]) and
                (_b[_r + _][_c] == current_player)) or ((_b[_r][_c + _] == _b[_r + 1][_c + _] == _b[_r + 2]
                                                         [_c + _] == _b[_r + 3][_c + _]) and (_b[_r][_c + _] == current_player)):
                is_normal = True
                break

        # check for diagonals
        is_diagonal = False
        if ((_b[_r + 1][_c] == _b[_r][_c + 1] == _b[_r + 2][_c + 1] == _b[_r + 1][_c + 2]) and (_b[_r + 1][_c] == current_player)) or \
        ((_b[_r + 1][_c + 1] == _b[_r][_c + 2] == _b[_r + 2][_c + 2] == _b[_r + 1][_c + 3]) and (_b[_r + 1][_c + 1] == current_player)) or \
        ((_b[_r + 2][_c] == _b[_r + 1][_c + 1] == _b[_r + 3][_c + 1] == _b[_r + 2][_c + 2]) and (_b[_r + 2][_c] == current_player)) or \
        ((_b[_r + 2][_c + 1] == _b[_r + 1][_c + 2] == _b[_r + 3][_c + 2] == _b[_r + 2][_c + 3]) and (_b[_r + 2][_c + 1] == current_player)):
            is_diagonal = True

        # check whether the board has any moves
        # is_draw is None when it is a draw
        is_drawn = not any([True for c in range(4) for r in range(4) if
                            _b[_r + r][_c + c] == '-'])
        if is_drawn == False:
            is_drawn = None

        # True -> Won | False -> Draw | None -> Continue
        return (is_normal or is_diagonal or is_drawn)


def main():
    t = Team36()


if __name__ == '__main__':
    main()
