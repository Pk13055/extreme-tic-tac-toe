#!/usr/bin/env python2

from __future__ import print_function
import json
from hashlib import md5
from random import shuffle
from time import time
import numpy as np

X = 1
O = 0
REWARD = 10000
MAX_TIME = 16
printJ = lambda x: print(json.dumps(x, indent=4))

class Team36:

	def __init__(self):
		self.init_time = time()
		self.details = {
			'team' : "AI-PMT",
			'members' : [
				"Pratik Kamble",
				"Yaseen Harris",
			],
			'start' : self.init_time
		}

		printJ(self.details)

		self.hash_map = {}
		self.player = X
		self.max_depth = 5
		self.depth_limit_max = 6
		self.depth_limit_min = 5
		self.wins = 0
		self.win_history = { 'x' : 0, 'o' : 0 }
		self.alpha = -REWARD
		self.beta = REWARD
		self.depth_check = lambda x: self.depth_limit_min <= x <= self.depth_limit_max

	def move(self, a_board, old_move, flag):
		'''
			@param a_board -> actual board object. Do not change this
			@param old_move -> The old move played
			@param flag -> The player who is playing
			@return best_move -> tuple(r, c) best possible move
		'''
		self.start_time = time()

		self.player = (X if (flag == 'x' or old_move == (-1, -1)) else O)
		self.win_history = { 'x' : 0, 'o' : 0 }

		self.board = a_board
		self.board.board_status = [[_ for _ in i[:]] for i in a_board.board_status]
		self.board.block_status = [[_ for _ in i[:]] for i in a_board.block_status]

		# check small board wins first
		flags = []
		if flag == 'x':
			flags.append('o')
		else:
			flags.append('x')
		flags.append(flag)

		for flag in flags:
			wins = [self._has_won((r, c), flag)
					for c in range(4) for r in range(4)]
			wins = [_ for _ in wins if _ == True]
			if self.win_history[flag] != len(wins) and self.win_history[flag] < 2:
				self.win_history[flag] = len(wins)
			else:
				self.win_history[flag] = 0

		if self.wins < len(wins):
			self.wins = len(wins)

		possible = self.heuristic(flag, self.board.find_valid_move_cells(old_move))

		best_move, best_value = self.minimax(old_move,self.player, 1)
		d_t = time() - self.start_time
		print("M(t, d) :", d_t, self.max_depth)

		if 15 < time() - self.init_time < 3500:
			d_check = self.depth_check(self.max_depth)
			if d_t > 0.90 * MAX_TIME and d_check:
				self.depth_limit_max -= 1
			elif d_t < 0.5 * MAX_TIME and d_check:
				self.max_depth += 1

		try:
			return best_move
		except UnboundLocalError:
			return possible[0]


	def minimax(self, old_move, current_player, current_depth, alpha=None, beta=None):

		'''
			@param old_move -> the last move played
			@param current_player -> the player for the current chance
			@param depth -> current depth
			@param alpha -> alpha beta pruning
			@param beta -> alpha beta pruning
			@return (best_score, best_move) -> tuple
		'''

		if alpha is None:
			alpha = self.alpha
		if beta is None:
			beta = self.beta


		if time() - self.start_time > 0.80 * MAX_TIME:
			return old_move, 0

		x, status = self.board.find_terminal_state()
		if status == 'WON':
			return old_move, (1 if current_player == X else -1) * current_depth
		elif status == 'DRAW':
			return old_move, 0

		if current_depth > self.max_depth:
			return old_move, 0

		possible_moves = self.board.find_valid_move_cells(old_move)
		if len(possible_moves) == 0:
			possible_moves = self.board.find_valid_move_cells((-1,-1))

		shuffle(possible_moves)
		current_value = 0
		best_value = (-1 if current_player == X else 1) * REWARD
		player_symbol = 'x' if current_player == X else 'o'
		possible_moves = self.heuristic(player_symbol, possible_moves, True)

		start_loop = time()

		for cur_move, cur_prob in possible_moves:

			if time() - self.start_time > 0.8 * MAX_TIME:
				print("Returning")
				self.depth_limit_max -= 1
				break

			c_r, c_c = cur_move
			self.board.board_status[c_r][c_c] = player_symbol
			has_won = self._has_won((c_r / 4, c_c / 4), player_symbol)

			if has_won == True:
				self.board.block_status[c_r / 4][c_c / 4] = player_symbol
				if self.win_history[player_symbol] < 2:
					self.win_history[player_symbol] += 1
					current_move,current_value = self.minimax(cur_move, current_player,
						current_depth + 1, alpha, beta)
					self.win_history[player_symbol] -= 1
				else:
					self.win_history[player_symbol] = 0
					current_move,current_value = self.minimax(cur_move, current_player ^ 1,
						current_depth + 1, alpha, beta)

				current_value += current_depth

			elif has_won == False:
				self.board.block_status[c_r / 4][c_c / 4] = 'd'
				current_move,current_value = self.minimax(cur_move, current_player ^ 1,
					current_depth + 1, alpha, beta)

			else:
				current_move,current_value = self.minimax(cur_move, current_player ^ 1,
					current_depth + 1, alpha, beta)

			del current_move
			self.board.block_status[c_r / 4][c_c / 4] = '-'
			self.board.board_status[c_r][c_c] = '-'

			# Alpha beta pruning
			if current_player == X:
				current_value += cur_prob
				if current_value > best_value:
					best_value = current_value
					best_move = cur_move
				alpha = max(alpha,best_value)

			else:
				current_value -= cur_prob
				if current_value < best_value:
					best_value = current_value
					best_move = cur_move
				beta = min(beta,best_value)

			if alpha > beta:
				break

		try:
			return best_move, best_value
		except UnboundLocalError:
			move, score = possible_moves[0]
			return move, score


	def heuristic(self, current_player, move_set, send_score=False):
			'''
				@param current_player -> player to be maximized
				@param move_set list of moves
				@return list -> ordered by best move

			'''

			# helper functions
			is_centre = lambda row, col: (row == 1 and col == 1) or \
				(row == 1 and col == 2) or \
				(row == 2 and col == 1) or \
				(row == 2 and col == 2)

			is_corner = lambda row, col: (row == 0 and col == 0) or \
				(row == 0 and col == 3) or \
				(row == 3 and col == 0) or \
				(row == 3 and col == 3)

			final_set = []
			c_bo = np.array(self.board.board_status)
			c_bl = np.array(self.board.block_status)
			r, c = np.where(np.matrix(c_bo) == '-')
			empties = [(_r, _c) for _r, _c in zip(r, c)]
			other_player = ('o' if current_player == 'x' else 'x')

			main_key = ''.join([''.join(_) for _ in self.board.board_status]) + \
						''.join([''.join(_) for _ in self.board.block_status]) + \
						current_player

			for cur_move in move_set:

				# current_player cur_move, board_state, block_state
				hash_key =  main_key + str(cur_move)
				hash_key = md5(hash_key).hexdigest()
				if hash_key in self.hash_map:
					final_set.append((cur_move, self.hash_map[hash_key]))
					continue

				bo_r, bo_c = tuple(map(lambda x: x / 4, cur_move))
				r_r, r_c = tuple(map(lambda x: x % 4, (bo_r, bo_c)))

				cur_board = c_bo[bo_r:bo_r + 4, bo_c:bo_c + 4]
				current_score = 0

				# board wise heuristics
				# common for within small board move
				for r, c in zip(cur_board, cur_board.T):
					if r[r == current_player].shape[0] == 3:
						current_score += 3
					if c[c == current_player].shape[0] == 3:
						current_score += 3

				# current move wise heuristics
				if is_corner(r_r, r_c) or is_centre(r_r, r_c):
					current_score += 1

				current_row = [_ for _ in cur_board[r_r]]
				current_col = [_ for _ in cur_board[r_c]]

				if current_row.count(other_player) == 3:
					current_score += 2

				if current_row.count(current_player) == 3:
					current_score += 3
				elif current_row.count(current_player) == 2:
					current_score += 1.5


				if current_col.count(other_player) == 3:
					current_score += 2

				if current_col.count(current_player) == 3:
					current_score += 3
				elif current_col.count(current_player) == 2:
					current_score += 1.5

				# diamond wise scores
				if is_centre(r_r, r_c):
					current_diamond = []
					if 	r_r == 1 and r_c == 1:
						tries = [cur_board[r_r + 1, r_c - 1] != other_player,
						cur_board[r_r + 1, r_c + 1] != other_player,
						cur_board[r_r + 2, r_c] != other_player,
						cur_board[r_r - 1, r_c + 1] != other_player,
						cur_board[r_r, r_c + 2] != other_player,]
					elif r_r == 1 and r_c == 2:
						tries = [cur_board[r_r + 1, r_c - 1] != other_player,
						cur_board[r_r + 1, r_c + 1] != other_player,
						cur_board[r_r + 1, r_c + 1] != other_player,
						cur_board[r_r - 1, r_c - 1] != other_player,
						cur_board[r_r, r_c - 2] != other_player,]
					elif r_r == 2 and r_c == 1:
						tries = [cur_board[r_r + 1, r_c + 1] != other_player,
						cur_board[r_r - 1, r_c + 1] != other_player,
						cur_board[r_r, r_c + 2] != other_player,
						cur_board[r_r - 2, r_c] != other_player,
						cur_board[r_r - 1, r_c - 1] != other_player,]
					elif r_r == 2 and r_c == 2:
						tries = [cur_board[r_r - 1, r_c - 1] != other_player,
						cur_board[r_r, r_c - 2] != other_player,
						cur_board[r_r + 1, r_c - 1] != other_player,
						cur_board[r_r - 2, r_c] != other_player,
						cur_board[r_r - 1, r_c + 1] != other_player,]

					current_diamond = [_ for _ in tries if _ == True]
					current_score += len(current_diamond)

				self.hash_map[hash_key] = current_score
				final_set.append((cur_move, current_score))

			final_set = sorted(final_set, key=lambda x: x[-1], reverse=True)
			if send_score:
				return final_set

			final_set = [_ for _, i in final_set]
			return final_set

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
		is_diamond = ((_b[_r + 1][_c] == _b[_r][_c + 1] == _b[_r + 2][_c + 1] == _b[_r + 1][_c + 2]) and (_b[_r + 1][_c] == current_player)) or \
		((_b[_r + 1][_c + 1] == _b[_r][_c + 2] == _b[_r + 2][_c + 2] == _b[_r + 1][_c + 3]) and (_b[_r + 1][_c + 1] == current_player)) or \
		((_b[_r + 2][_c] == _b[_r + 1][_c + 1] == _b[_r + 3][_c + 1] == _b[_r + 2][_c + 2]) and (_b[_r + 2][_c] == current_player)) or \
		((_b[_r + 2][_c + 1] == _b[_r + 1][_c + 2] == _b[_r + 3][_c + 2] == _b[_r + 2][_c + 3]) and (_b[_r + 2][_c + 1] == current_player))

		# check whether the board has any moves
		# is_draw is None when it is a draw
		is_drawn = not any([True for c in range(4) for r in range(4) if
							_b[_r + r][_c + c] == '-'])
		if is_drawn == False:
			is_drawn = None

		# True -> Won | False -> Draw | None -> Continue
		return (is_normal or is_diamond or is_drawn)

def main():
	t = Team36()

if __name__ == '__main__':
	main()
