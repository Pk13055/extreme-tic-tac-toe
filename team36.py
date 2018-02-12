#!/usr/bin/env python3

'''
	Implementation of an extreme Tic-Tac-Toe bot using
	(almost) Vanilla Python.
	@author Pratik Kamble
	@author Yaseen Harris

'''

import datetime
import json
from random import choice, random, randint

import numpy as np
import pandas as pd

DRAW = 2
EMPTY = 0
X = 1
O = -1

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
		print("Started : ", self.start_time)
		print("Info : ", json.dumps(self.team, indent=4))

	@classmethod
	def move(board, old_move, flag):
		'''
			common signature as iterface for interaction with
			other bots
			@param board lofl
			@param old_move tuple
			@param flag int?
			@return tuple (row, col)

		'''

		self.board_state = np.array([[EMPTY if _ == '-' else X if _ == 'x' else O for _ in r] for r in board.board_status])
		self.block_state = np.array([[X if _ == 'x' else O if _ == 'o' else DRAW for _ in r] for r in board.block_status])
		init_moves = board.valid_moves(old_move, self.block_state, self.board_state)

		# add learning and AI part here

		# if not valid, find row col here
		row, col = choice(init_moves)
		# returns a tuple with x row and y col (16 x 16)
		return (row, col)

	@classmethod
	def valid_moves(old_move, block_state, board_state):
		'''
			returns a list consisting of valid moves
			@param old_move tuple (r, c)
			@return moves list
		'''

		o_r, o_c = old_move
		a_r, a_c = (o_r % 4, o_c % 4)
		if old_move != (-1, -1) and block_state[a_r, a_c] == EMPTY:
			r, c = np.where(board_state[4 * a_r: 4 * a_r + 4, 4 * a_c: 4 * a_c + 4] == EMPTY)
			return [(_r, _c) for _r, _c in zip(r, c)]
		else:
			r, c = np.where(board_state == EMPTY)
			return [(_r, _c) for _r, _c, in zip(r, c) if block_state[_r / 4, _c / 4] == EMPTY]


	@classmethod
	def is_terminal(block_state, board_state):
		'''
			returns whether this is a final state or not
			@return tuple -> STATUS, TYPE
		'''

		types, counts = np.unique(block_state, return_counts=True)
		stats = dict(zip(types, counts))

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


	@classmethod
	def check_move(old_move, new_move, block_state, board_state):
		''' checks if a given "new" move is valid with
		reference to an old move. A wrapper for the `valid_moves`
		function.
			@param old_move -> previous move made
			@param new_move -> new move to be made
			@return bool -> validity of a new_move
		'''

		return type(old_move == new_move) and new_move in self.valid_moves(old_move, block_state, board_state)


	@classmethod
	def update_board(old_move, new_move, current_player, block_state, board_state):
		'''
			update the status of the board and place the given move as required
			@param old_move -> Old move that was played
			@param new_move -> New move to be played right now
			@param current_player -> Current player playing
			@return tuple -> (status, TYPE)
		'''

		if not self.check_move(old_move, new_move, block_state, board_state):
			return ('UNSUCCESSFUL', False)

		new_r, new_c = new_move
		board_state[new_r, new_c] = current_player
		block_r, block_c = int(new_r / 4), int(new_c / 4)

		types, counts = np.unique(board_state[block_r:block_r + 4, block_c:block_c + 4],
			return_counts=True)
		stats = dict(zip(types, counts))

		# check winner for normal row or col-wise
		# 0 -> col-wise | 1 -> row-wise
		for dimen in [0, 1]:
			if np.any(np.all(board_state == current_player, dimen)):
				return ('SUCCESSFUL', True)

		# check winner for diamond pattern
		r_v, c_v = [[t + _ for _ in [1, 2]] for t in [block_r, block_c]]
		for r_c, c_c in zip(r_v, r_c):
			if(board_state[r_c - 1, c_c] == board_state[r_c, c_c - 1] ==
				board_state[r_c + 1, c_c] == board_state[r_c, c_c + 1]):
				return ('SUCCESSFUL', True)

		if sum(counts) < 16:
			return ('SUCCESSFUL', False)
		elif sum(counts) == 16:
			block_state[block_r, block_c] = DRAW
			return ('SUCCESSFUL', False)


def main():
	t = Team36()

if __name__ == "__main__":
	main()
