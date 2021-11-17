"""This is going to be an instantiation of the GameTask
framework to implement one version of the q/a game

Author: Noor
Date: March 10, 2021

"""
# The class we'll use to design this game's tasks
from server_code.game_task import GameTask

# Keeping it in the form of a class to support future extension
class PiDayGame:
	game_intro = "=*"*40
	game_intro += "\n\n\nWelcome to  Pi-Day 2021 Game!\n\n\nYou will follow Pypy on his journey and help him solve puzzles.\nEach puzzle will earn you a set of points.\nYou will also have 2 hints, in total for the whole game.\nThe player with the highest score will be rewarded worthily.\n\nOh, and your progress will be automatically saved as you play along. No worries!\n\nLet's get started. Good luck!\n\n"
	game_intro += "NOTE: Some tasks may not have a hint available!\n"
	game_intro += "=*"*40 + "\n"

	game_outro = "=*"*40
	game_outro += "\nThanks for playing! Your answers (if any) have been saved. If you haven't finished the game, resume any time with 'start', if you have, check out the leaderboard with 'leaderboard' event command!\n"
	game_outro += "=*"*40

	task1 = GameTask(1, "This is the first dummy task",
	"This is a dummy hint.", "DUMMY", 5)
	task2 = GameTask(2, "This is the second dummy task",
	"This is a dummy hint", "DUMMY", 5)
	task3 = GameTask(3, "This is the third dummy task",
	"", "dummy", 5)
	task4 = GameTask(4, "This is the fourth dummy task",
		"This is a dummy hint", "DUMMY", 5)
	task5 = GameTask(5, "This is the fifth dummy task",
	"", "DUMMY", 5)
	tasks = [task1, task2, task3, task4, task5]