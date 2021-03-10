""" This module will provide the game specific-tasks
 including the static definitions of the tasks and the
 correct answers of the same

 Author: Noor
 Date: March 10, 2021

 """

class GameTask:
	def __init__(self, task_id, desc, hint, ans, points):
		self.task_id = task_id
		self.desc = desc
		self.hint = hint
		self.ans = ans
		self.points = points

	def check_answer(self, given_ans):
		"""Returns true if given_ans is correct."""
		if self.ans == given_ans:
			return True
		else:
			return False

	def give_hint(self):
		return self.hint
		

