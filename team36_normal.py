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
from random import choice, shuffle, random
from copy import deepcopy, copy
from time import sleep
from hashlib import md5
from multiprocessing import Pool
import datetime
import json
# from threading import

DRAW = 2
EMPTY = -1
X = 1
O = 0

MAX_REWARD = 68
MIN_REWARD = -68

printJ = lambda x: print(json.dumps(x, indent=4))

# def thread_mini(func, )

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
		self.player = 'o'
		self.wins = 0
		self.is_end = False
		self.hash_map = {}
		print("Started : ", self.start_time)
		print("Info : ", json.dumps(self.team, indent=4))

	def move(self, a_board, old_move, flag):
		'''
			common signature as iterface for interaction with
			other bots
			@param board lofl
			@param old_move tuple
			@param flag int?
			@return tuple (row, col)

		'''
		# print(chr(27) + "[2J")
		board = copy(a_board)

		# check for the terminal state for move again.

		board.block_status = json.loads(json.dumps(a_board.block_status))
		board.board_status = json.loads(json.dumps(a_board.board_status))
		init_moves = board.find_valid_move_cells(old_move)
		best_move, best_score = (-1, -1), 4 * MIN_REWARD
		start_time = datetime.datetime.now()
		self.player = flag

		check_win_b = lambda board: any([True if c == self.player else False for r in board.block_status for c in r])
		# first player then modify valid_move_cells
		if old_move == (-1, -1) or (self.wins <= 2 and check_win_b(board)):
			if old_move != (-1, -1): self.wins += 1
			init_moves = [(r, c) for r, val in enumerate(board.block_status) for c, act in enumerate(val) if act == '-']

		shuffle(init_moves)
		self.allowed_time = 0.95 * (14.00 / len(init_moves))
		for cur_move in init_moves:
			self.start_time = datetime.datetime.now()
			self.is_end = False
			score = self.minimax(board, old_move, cur_move, 0, self.player,
				self.player, MIN_REWARD, MAX_REWARD)
			# print(score)
			if score > best_score:
				best_move = cur_move
				best_score = score

		end_time = datetime.datetime.now()
		# print(chr(27) + "[2J")
		# board.print_board()
		print("Total : ", (end_time - start_time))
		# sleep(1)
		return best_move

	def minimax(self, board, old_move, cur_move, cur_depth,
		current_player, maximizing_player, alpha, beta, max_depth=4):

		if self.is_end == True:
			# print("GOAL REVERSAL")
			return 0

		t_elapsed = (datetime.datetime.now() - self.start_time).total_seconds()
		# print(cur_depth * " \t " + "<->", t_elapsed)

		if t_elapsed > self.allowed_time:
			self.is_end = True
			# print("RETURNING")
			return 0

		self.is_end = False

		cur_board = copy(board)
		cur_board.block_status = json.loads(json.dumps(board.block_status))
		cur_board.board_status = json.loads(json.dumps(board.board_status))
		current_score = 0
		stat_string, stat = cur_board.update(old_move, cur_move, current_player)
		# print("\033[93m")
		# board.print_board()
		# print("\033[0m")
		# print(chr(27) + "[2J")
		# print(stat_string, stat)

		hash_key = md5(self.player + ''.join([''.join(_) for _ in board.board_status])).hexdigest()
		if hash_key in self.hash_map:
			# print("\nMemed\n")
			score, self.is_end = self.hash_map[hash_key]
			return score


		if stat_string == 'SUCCESSFUL' and stat:
			current_score += 0.5 * 68
		else:
			current_score -= 0.5 * 68

		who, status = cur_board.find_terminal_state()
		if status == "WON":
			# print("WON", who, "current ", current_player)
			if current_player == who:
				current_score += MAX_REWARD
			else:
				current_score -= MAX_REWARD
			if who == maximizing_player:
				self.is_end = True
				self.hash_map[hash_key] = (current_score, self.is_end)
			return current_score

		elif status == "DRAW":
			# print("DRAW", who, "current ", current_player)
			current_score -= 0.8 * 68
			self.hash_map[hash_key] = (current_score, self.is_end)
			return current_score

		if cur_depth == max_depth:
			current_score -= 0.9 * 68
			return current_score

		old_move = cur_move
		next_moves = board.find_valid_move_cells(old_move)
		shuffle(next_moves)

		if current_player == 'x':
			next_player = 'o'
		else:
			next_player = 'x'

		current_score = abs(current_score)
		if current_player != maximizing_player: current_score *= -1

		if (datetime.datetime.now() - self.start_time).total_seconds() > self.allowed_time:
			self.is_end = True
			# print("RETURNING")
			return current_score

		fncs = [max, min]
		scores = [ ]
		if current_player == maximizing_player:
			best_score = MIN_REWARD
		else:
			best_score = MAX_REWARD

		for next_move in next_moves:
			cur_score = self.minimax(cur_board, old_move, next_move, cur_depth + 1, next_player,
									maximizing_player, alpha, beta, max_depth)
			best_score = fncs[current_player == maximizing_player](cur_score, best_score)
			if current_player == maximizing_player:
				alpha = max(alpha, best_score)
			else:
				beta = min(beta, best_score)

			if beta <= alpha:
				break

		current_score += best_score
		# print(current_score)
		return current_score

def main():
	t = Team36()

if __name__ == '__main__':
	main()

