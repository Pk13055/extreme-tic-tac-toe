#!/usr/bin/env python2

'''
	Implementation of an extreme Tic-Tac-Toe bot using
	(almost) Vanilla Python.
	@author Pratik Kamble
	@author Yaseen Harris

'''

from __future__ import print_function
import datetime
import json
from random import choice, random, randint
from time import sleep

import numpy as np
import pandas as pd

DRAW = 2
EMPTY = -1
X = 1
O = 0

MAX_REWARD = 100
MIN_REWARD = -100

printJ = lambda x: print(json.dumps(x, indent=4))


class Team36:

	def __init__(self):
		self.start_time = datetime.datetime.now()
		self.team = {
			'name' : "AI-PMT",
			'members' : [
				"Pratik Kamble",
				"Yaseen Harris",
			]
		}
		self.player = X
		print("Started : ", self.start_time)
		print("Info : ", json.dumps(self.team, indent=4))

	def move(self, board, old_move, flag):
		'''
			common signature as iterface for interaction with
			other bots
			@param board lofl
			@param old_move tuple
			@param flag int?
			@return tuple (row, col)

		'''
		# if old_move == (-1, -1):
		# 	print("First Player")
		# 	first_moves = [ (5, 5), (5, 10), (10, 5), (10, 10) ]
		# 	return choice(first_moves)

		print("Old Move", old_move)
		if board.board_status[old_move[0]][old_move[1]] == 'x':
			self.player = O
		else:
			self.player = X

		self.board_state = np.array([[EMPTY if _ == '-' else X if _ == 'x' else O for _ in r]
		 for r in board.board_status])
		self.block_state = np.array([[X if _ == 'x' else O if _ == 'o' else EMPTY if _ == '-' else DRAW for _ in r]
		 for r in board.block_status])
		init_moves = self.valid_moves(old_move, self.block_state, self.board_state)
		print(init_moves)
		best_move = choice(init_moves)
		print("Returning", best_move, self.player)
		sleep(2)

		# # add learning and AI part here
		# best_move, best_score = (-1, -1), MIN_REWARD

		# # for cur_move in init_moves:
		# # 	score = minimax(self.board_state, self.blocksck_state, old_move,
		# # 		cur_move, 0, self.player, self.player)
		# # 	if score >= best_score:
		# # 		best_score = score
		# # 		best_move = cur_move

		# if not valid, find row col here
		# returns a tuple with x row and y col (16 x 16)
		return best_move

	def minimax(self, board_state, block_state, old_move, new_move, cur_depth,
		current_player, maximizing_player, max_depth=6):
		'''
			returns the best possible move after looking
			till a certain depth
			@param nparr -> board_state state of the board
			@param nparr -> block_state state of the overall blocks of 4
			@param tuple -> current played move
			@param cur_depth -> the current depth
			@param max_depth -> default 6 -> the depth till which the algorithm should run
			@return score -> the max value for a given move
		'''
		# make the valid play here
		status, stat, board_state, block_state = self.update_board(old_move, new_move,
			current_player, block_state, board_state)

		if status != 'SUCCESSFUL':
			if current_player == maximizing_player:
				return MIN_REWARD
			return MAX_REWARD

		# check if the new state is terminal state
		if self.is_terminal(block_state, board_state):
			return MAX_REWARD - cur_depth

		if cur_depth == max_depth:
			if current_player == maximizing_player:
				return MIN_REWARD
			return MAX_REWARD

		# now that the current move has been successfully played, we can update old_move
		# to new_move
		old_move = new_move
		allowed_moves = self.valid_moves(old_move, block_state, board_state)
		if current_player == maximizing_player:
			best_val = MIN_REWARD
		else:
			best_val = MAX_REWARD
		# iterate over all the possible allowed moves
		for new_move in allowed_moves:
			new_val = self.minimax(board_state, block_state, old_move, new_move, cur_depth + 1,
				not current_player, maximizing_player, max_depth)
			if current_player == maximizing_player:
				best_val = max(best_val, new_val)
			else:
				best_val = min(best_val, new_val)

		return best_val

	def valid_moves(self, old_move, block_state, board_state):
		'''
			returns a list consisting of valid moves
			@param old_move tuple (r, c)
			@return moves list
		'''

		o_r, o_c = old_move
		a_r, a_c = (o_r % 4, o_c % 4)
		if block_state[a_r, a_c] == EMPTY and old_move != (-1, -1) :
			r, c = np.where(board_state[4 * a_r: 4 * a_r + 4, 4 * a_c: 4 * a_c + 4] == EMPTY)
			return [(_r, _c) for _r, _c in zip(r + 4 * a_r, c + 4 * a_c)]
		else:
			r, c = np.where(board_state == EMPTY)
			return [(_r, _c) for _r, _c, in zip(r, c) if block_state[_r / 4, _c / 4] == EMPTY]


	def is_terminal(self, block_state, board_state):
		'''
			returns whether this is a final state or not
			@return tuple -> STATUS, TYPE
		'''

		types, counts = np.unique(block_state, return_counts=True)
		stats = dict(zip(types, counts))
		if EMPTY in stats: del stats[EMPTY]

		# check winner for normal row or col-wise
		# 0 -> col-wise | 1 -> row-wise
		for dimen in [0, 1]:
			if np.any(np.all(block_state == X, dimen) | np.all(block_state == O, dimen)):
				if np.any(np.all(block_state == X, dimen)):
					winner = X
				else:
					winner = O
				return (winner, 'WON')

		# check winner for diamond pattern
		for r_c, c_c in zip([1, 2], [1, 2]):
			if(block_state[r_c - 1, c_c] == block_state[r_c, c_c - 1] == block_state[r_c + 1,
			 c_c] == block_state[r_c, c_c + 1]):
				return (block_state[r_c - 1, c_c], 'WON')

		if sum(counts) < 16:
			return ('CONTINUE', EMPTY)
		elif sum(counts) == 16:
			return ('NONE', DRAW)


	def check_move(self, old_move, new_move, block_state, board_state):
		'''
			checks if a given "new" move is valid with
			reference to an old move. A wrapper for the `valid_moves`
			function.
			@param old_move -> previous move made
			@param new_move -> new move to be made
			@return bool -> validity of a new_move
		'''

		return type(old_move) == type(new_move) and new_move \
			in self.valid_moves(old_move, block_state, board_state)


	def update_board(self, old_move, new_move, current_player, block_state, board_state):
		'''
			update the status of the board and place the given move as required
			@param old_move -> Old move that was played
			@param new_move -> New move to be played right now
			@param current_player -> Current player playing
			@return tuple -> (status, TYPE, board_state, block_state)
		'''

		if not self.check_move(old_move, new_move, block_state, board_state):
			return ('UNSUCCESSFUL', False, None, None)

		new_r, new_c = new_move
		board_state[new_r, new_c] = current_player
		block_r, block_c = int(new_r / 4), int(new_c / 4)

		# get the percentage stats for the relevant section of the board
		types, counts = np.unique(board_state[block_r:block_r + 4, block_c:block_c + 4],
			return_counts=True)
		stats = dict(zip(types, counts))
		if EMPTY in stats: del stats[EMPTY]

		# check winner for normal row or col-wise
		# 0 -> col-wise | 1 -> row-wise
		for dimen in [0, 1]:
			if np.any(np.all(board_state == current_player, dimen)):
				return ('SUCCESSFUL', True, board_state, block_state)

		# check winner for diamond pattern
		r_v, c_v = [[t + _ for _ in [1, 2]] for t in [new_r, new_c]]
		for r_c, c_c in zip(r_v, r_c):
			if(board_state[r_c - 1, c_c] == board_state[r_c, c_c - 1] ==
				board_state[r_c + 1, c_c] == board_state[r_c, c_c + 1]):
				return ('SUCCESSFUL', True, board_state, block_state)

		if sum(counts) < 16:
			return ('SUCCESSFUL', False, board_state, block_state)
		elif sum(counts) == 16:
			block_state[block_r, block_c] = DRAW
			return ('SUCCESSFUL', False, board_state, block_state)


def main():
	t = Team36()

if __name__ == "__main__":
	main()
