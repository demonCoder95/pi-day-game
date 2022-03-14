# This will implement the main Game class
# Author: Noor
# Date: March 10, 2021

""" There will be a single game object per player which will
include all the necessary dynamics for a correct gameplay.
Multiple players will play simultaneously by invoking multiple
game object through concurrency"""
import uuid
import logging
import time

game_logger = logging.getLogger(__name__)

from pyfiglet import Figlet
from server_code.pi_day_game import PiDayGame
from server_code.my_time import show_time_since, show_time_to

event_end_str = "Mon Mar 21 17:00:00 2022"

# Global to hold the welcome message
welcome_message = Figlet().renderText("\nWelcome to Pi-Day Event!")
welcome_message += "\nEnter 'help' any time to see command-line help and 'quit' to exit the event."
welcome_message += "\nCommands are case-insensitive. Type 'Start' to start a new game or resume an existing one.\nHappy gaming!\n"

class Game:
	def __init__(self, player_conn, player_addr, login_time, db_query_q, db_resp_q, db_query_lock, event_ended):
		self.game_uuid = str(uuid.uuid4())
		self.login_time = login_time

		game_logger.debug('A game with uuid {} was created'.format(self.game_uuid))
		
		self.game_log_file = open("logs/games/{}.log".format(self.game_uuid), "w")
		
		self.player_log_file = None		# later initializing this with the log file
		self.player_conn = player_conn
		self.player_addr = player_addr
		self.player_resuming = False	# determine if a player is resuming

		# these are overwritten when a new player joins and progress is loaded
		self.player_uuid = "WAITING"	# A player could be waiting before the event
		self.player_hints = 2 # every new player starts with 2 hints possible
		self.player_points = 0	# every new player starts with 0 points
		self.current_task = 1	# every new player starts at task 1
		self.online_status = "ONLINE"	# player is online when the object was created
		self.hint_used = "FALSE"	# a new player hasn't used the hint on the current level

		# DB query synchronization elements
		self.db_query_q = db_query_q
		self.db_resp_q = db_resp_q
		self.db_query_lock = db_query_lock

		# event synchronization elements
		self.event_ended = event_ended

	def _handle_id(self):
		"""This is going to handle player ID"""
		self._sendmsg("Write 'new' to set a new player ID (case-sensitive,alphanumeric only). Or enter your existing ID to resume playing.\n")
		while True:	
			self._show_command_prompt()
			user_input = self._handle_user_input("event")
			if user_input == "new":
				self._sendmsg("Enter a new player ID: ")
				self._show_command_prompt()
				input_id = self._handle_user_input("event")
				# check if the ID already exists
				if self._player_id_valid(input_id):
					# ask the user to choose another one, it's taken!
					self._sendmsg("{} is already taken. Choose another one!\n".format(input_id))
					# restart the loop
					continue
				# if not, then create a new player
				else:
					self.player_uuid = input_id
					self._create_new_player()

			elif self._player_id_valid(user_input):
				self.player_uuid = user_input
				# check if a player is already logged in with this name
				with self.db_query_lock:
					self.db_query_q.put("get_online_status")
					self.db_query_q.put(self.player_uuid)
					online_status = self.db_resp_q.get()
				if online_status == "ONLINE":
					self._sendmsg("Player {} is already logged in!".format(self.player_uuid))
					continue

				self._sendmsg("Welcome back {}!\n".format(self.player_uuid))
				game_logger.info("Player {} is now ONLINE".format(self.player_uuid))
				self.player_resuming = True
				
				if not self.event_ended.is_set():
					# get player data from the database
					with self.db_query_lock:
						# get the player hints
						self.db_query_q.put("get_hints")
						self.db_query_q.put(self.player_uuid)
						self.player_hints = self.db_resp_q.get()

						# get the player's current task
						self.db_query_q.put("get_task")
						self.db_query_q.put(self.player_uuid)
						self.current_task = self.db_resp_q.get()

						# get player's points
						self.db_query_q.put("get_points")
						self.db_query_q.put(self.player_uuid)
						self.player_points = self.db_resp_q.get()

						# get hint_used status
						self.db_query_q.put("get_hint_used")
						self.db_query_q.put(self.player_uuid)
						self.hint_used = self.db_resp_q.get()

						# update the login time of player
						self.db_query_q.put("update_login_time")
						self.db_query_q.put(",".join([self.player_uuid, self.login_time]))

					# Check if the player has already finished playing
					if self.current_task == len(PiDayGame.tasks) +1:
						player_status = "You've already finished playing. Check out the leader board to see where you stand."
					else:
						player_status = "\nEvent is LIVE\n"
						player_status += "Hints: {}, Points: {}, Currently solving task {}.\n".format(self.player_hints, self.player_points, self.current_task)
					
					self._sendmsg(player_status)
				# if the event has already ended, there's no need for this data
				else:
					self._sendmsg("Event has ENDED! Go check out the 'leaderboard'!\n")

			else:
				self._sendmsg("Player {} doesn't seem to exist. Try again, or you can create a new ID with 'new'.\n".format(user_input))
				continue

			# start the player log file to store their responses
			self.player_log_file = open("logs/players/{}.log".format(self.player_uuid), "w")

			with self.db_query_lock:
				# set the player's online status
				self.db_query_q.put("update_online_status")
				self.db_query_q.put(",".join([self.player_uuid, "ONLINE"]))

			self._sendmsg("You're all set. Letting you in")
			time.sleep(1)
			self._sendmsg(".")
			time.sleep(1)
			self._sendmsg(".")
			time.sleep(1)
			self._sendmsg(".\n")
			break

	def _player_id_valid(self, player_id):
		resp = False
		# acquire the lock to ensure synchronization
		with self.db_query_lock:
			# put the operation type on the queue
			self.db_query_q.put("player_exists")
			self.db_query_q.put(player_id)

			# wait for the response in blocking mode
			resp = self.db_resp_q.get()
		return resp

	# a small wrapper to handle bytes encoding of str
	def _sendmsg(self, msg):
		self.player_conn.sendall(bytes(msg, 'utf-8'))
		
		# keeping record of every msg sent to user in the game
		self.game_log_file.writelines(msg)
	
	def _handle_event_help(self):
		"""Prints a help message to the player to understand the commandline"""
		help_text = "The EVENT commands are given below:\n\n" + \
			"start       : Starts/resumes a game. \n" + \
			"leaderboard : Provides the event leaderboard.\n" + \
			"my_id       : Provides your player ID.\n" + \
			"time_left   : Provides time left in the event.\n" + \
			"help        : Provides this help.\n" + \
			"quit        : Quits the event. \n"
		self._sendmsg(help_text)

	def _handle_game_help(self):
		"""Prints a help message to the player during the game"""
		help_text = "The game commands are given below:\n\n"
		help_text += "hint          : Get a hint to solve this level.\n"
		help_text += "response <str>: Submit your response. Case insensitive.\n"
		help_text += "next          : Move onto the next task.\n"
		help_text += "end           : End the game at any task.\n"
		help_text += "time_left     : Show the remaining time.\n"
		help_text += "help          : Get this help.\n"
		self._sendmsg(help_text)

	def _handle_start(self):

		# check if the player has already finished the game
		if self.current_task == len(PiDayGame.tasks)+1:
			self._sendmsg("\n\nYou've already finished your game! Go to the leaderboard to see where you stand!\n")
			return

		# show the game intro message
		self._sendmsg(PiDayGame.game_intro)

		# use slicing to skip tasks already done
		for each_task in PiDayGame.tasks[self.current_task-1:]:
			# Show the task description
			# Modifying the string for final task
			
			# Don't print any more tasks if the event has ended
			if self.event_ended.is_set():
				break

			if each_task.task_id == len(PiDayGame.tasks):
				task_str = Figlet().renderText("\nTASK    {} - FINAL\n".format(each_task.task_id))
			else:
				task_str = Figlet().renderText("\nTASK    {}\n".format(each_task.task_id))
			task_str += "\n\n" + each_task.desc + "\n\n"
			task_str += "NOTE: Response is NOT case sensitive.\n"
			task_str += "Points: {}\n".format(each_task.points)
			task_str += "(Your points: {}, hints left: {})\n".format(self.player_points, self.player_hints)
			task_str += "=*"*40 + "\n"
			self._sendmsg(task_str)

			if self._task_input_handler(each_task) == "end":
				# premature end doesn't update the current_task
				break

			# update the variable one the task has been handled
			self.current_task += 1
			# update the player's current task in the DB
			with self.db_query_lock:
				self.db_query_q.put("update_task")
				self.db_query_q.put(",".join([self.player_uuid, str(self.current_task)]))

		self._sendmsg(PiDayGame.game_outro)

	def _task_input_handler(self, current_task):
		"""This will handle user input parsing during a running game"""
		# use this to determine if a task is solved
		task_solved = False

		# Infinite loop that only breaks once the task is over or event ends
		while not self.event_ended.is_set():
			self._show_game_prompt()
			user_input = self._handle_user_input("game")
			if user_input == "hint":
				# check if the current task actually has a hint. Also, is hint was used on this round,
				# and the player disconnected, and wants to see it again, it should be given.
				if self.player_hints == 0 and self.hint_used != "TRUE":
					self._sendmsg("You've used up all your hints! Think harder, you can do this!\n")
				else:
					if current_task.hint != "":
						self._sendmsg("{}\n".format(current_task.hint))
						# update the hint count, if being used for the first time
						if self.hint_used != "TRUE":
							self.player_hints -= 1
							self.hint_used = "TRUE"
							with self.db_query_lock:
								self.db_query_q.put("update_hints")
								self.db_query_q.put(",".join([self.player_uuid, str(self.player_hints)]))
								self.db_query_q.put("update_hint_used")
								self.db_query_q.put(",".join([self.player_uuid, self.hint_used]))
							
						self._sendmsg("(hints left: {})\n".format(self.player_hints))
						
					else:
						self._sendmsg("Too bad! This task doesn't have a hint!\n")

			elif user_input.split(" ")[0] == "response":
				# Make sure players don't keep submitting a correct response to accumulate points
				if task_solved:
					self._sendmsg("You've already solved this one. Move forward with 'next'!\n")
				else:
					given_ans = user_input[9:].strip().upper()
					self.player_log_file.writelines("Task {}: {}".format(current_task.task_id, given_ans))
					
					# if the user response is correct
					if current_task.check_answer(given_ans):
						# display a message
						self._sendmsg("CONGRATULATIONS! You've earned {} points! Enter 'next' to move on!\n".format(current_task.points))
						task_solved = True
						# update the points of the player with task points
						with self.db_query_lock:
							self.db_query_q.put("update_points")
							self.db_query_q.put(",".join([self.player_uuid, str(self.player_points+current_task.points)]))
						self.player_points += current_task.points
					# if the response is not correct, ask them to try again
					else:
						self._sendmsg("Oh no! That's not the right answer. Try again!\n")
					
			elif user_input == "next":
				# reset the hint_used status when a player types next
				self.hint_used = "FALSE"
				with self.db_query_lock:
					self.db_query_q.put("update_hint_used")
					self.db_query_q.put(",".join([self.player_uuid, self.hint_used]))

				if not task_solved:
					self._sendmsg("You haven't solved this one yet! Keep working!\n")
				elif current_task.task_id == len(PiDayGame.tasks):
					self._sendmsg("You're all done!\n")
					break
				else:
					break
			elif user_input == "help":
				self._handle_game_help()
			
			elif user_input == "time_left":
				self._show_time_left()

			elif user_input == "end":
				self._sendmsg("Exiting the game.\n")
				return user_input

			# handle empty 'return' or whitespace
			elif user_input == "":
				# do nothing, just ignore it
				continue
			else:
				self._sendmsg("Invalid command. Type 'help'.\n")

		if self.event_ended.is_set():
			self._sendmsg("The event has ENDED! Check the 'leaderboard' to see where you stand\n")

	def _handle_error(self):
		self._sendmsg("Invalid command. Try 'help'.\n")

	def _handle_my_id(self):
		self._sendmsg("Your player ID is {}\n".format(self.player_uuid))

	def _handle_user_input(self, input_type):
		while True:
			# start with each response as being valid
			response_valid = True
			# take the user input and perform some operations
			user_input = str(self.player_conn.recv(1024), 'utf-8').lower().strip().split(" ")
			# remove redundant spaces in the input
			user_input = " ".join([x for x in user_input if x != ""])
			# tokenize the entire input and look for invalid tokens, in the event of an empty 
			# response, the entire loop will be skipped
			for each_token in user_input.split(" "):
				# determine fishy input - this will only match [a-ZA-Z0-9]
				if  not each_token.isalnum():
					# for special input that contains nonalpha-num characters
					if each_token == "time_left" or each_token == "my_id":
						break
					# for non-blank fishy input, we notify the user
					if not each_token == "":
						self._sendmsg("Invalid characters in input. Try again.\n")
					response_valid = False
					break
			# in case of empty response, this will evaluated to false
			if response_valid and user_input != "":
				break
			else:
				# for blank input, we simply print the prompt, as a normal behavior for a CLI
				if input_type == "game":
					self._show_game_prompt()
				elif input_type == "event":
					self._show_command_prompt()
			
		# keeping record of every user input provided
		self.game_log_file.writelines(user_input + '\n')
		return user_input

	def _create_new_player(self):
		# the lock is not needed once we put everything on the queue
		# that is because the data is already is good order to be
		# correctly processed by the consumer thread of DB
		with self.db_query_lock:
			# the operation type is create_player
			self.db_query_q.put("create_player")
			player_data = ",".join([self.player_uuid,
				self.game_uuid,
				self.login_time, 
				str(self.current_task),
				str(self.player_hints),
				str(self.player_points),
				self.online_status,
				self.hint_used])
			game_logger.debug("Creating new player: {}".format(player_data))
			self.db_query_q.put(player_data)

	def _show_leaderboard(self):
		"""
		Provides a leaderboard to the players where they can keep track of each other's progress.
		Since the database will be frequently updated, it is necessary for now, to 
		fetch all the information, upon each call to 'leaderboard' command by a player.
		"""
		leaderboard = ""	# start with an empty string
		leaderboard += Figlet().renderText("EVENT LEADERBOARD")
		leaderboard += "\n{:<20}{:^10}{:^30}{:>}\n".format("Player ID", "Status", "Last login", "Points")

		player_data = []	# empty list, to be populated by the DB
		
		with self.db_query_lock:
			self.db_query_q.put("get_leaderboard_data")
			self.db_query_q.put("")	# null data for this query			
			# get all the data off of the queue
			player_data = self.db_resp_q.get()
		game_logger.info("Fetched leaderboard for player {}".format(self.player_uuid))

		# TODO: highlight the top 3 players
		for each_player in player_data:
			# restrict player name printed to first 20 characters only
			player_id = each_player[0]
			
			# highlight the player's ID on the leaderboard
			if player_id == self.player_uuid:
				player_id = player_id.upper()

			player_status = each_player[1]
			last_login = show_time_since(each_player[2])
			leaderboard += "{:<20}{:^10}{:^30}{:>}\n".format(player_id[:20], player_status, last_login, each_player[3])

		self._sendmsg(leaderboard)

	def _show_time_left(self):
		if self.event_ended.is_set():
			self._sendmsg("Event is already over!")
		else:
			msg_figlet = Figlet()
			status_msg = ""
			status_msg += "\nEVENT ENDS IN"
			status_msg += "\n{}\n".format(msg_figlet.renderText(show_time_to(event_end_str)))
			self._sendmsg(status_msg)

	def start_game(self):
		game_logger.info("Game {} started".format(self.game_uuid))
		self._handle_id()
		# no need for welcome message on a player that is resuming a game
		# but if the event has already ended, it's okay to show the banner
		if self.player_resuming and not self.event_ended.is_set():
			self._sendmsg("Type 'start' to resume where you left off.")
		else:
			self._show_welcome_message()
	
		self._show_command_prompt()

		while True:
			# Take the user input
			user_input = self._handle_user_input("event")
			if user_input == "start":
				if not self.event_ended.is_set():
					# allow starting a game if the event hasn't ended
					self._handle_start()
				else:
					# notify otherwise
					self._sendmsg("The event ended already! Try 'leaderboard'!\n")

			elif user_input == "help":
				self._handle_event_help()

			elif user_input == "quit":
				break

			elif user_input == "my_id":
				self._handle_my_id()

			elif user_input == "time_left":
				self._show_time_left()

			elif user_input == "leaderboard":
				self._sendmsg("\nLoading the leaderboard...\n\n")
				self._show_leaderboard()

			elif user_input == "":
				# ignore white-space response
				pass
			else:
				self._handle_error()

			self._show_command_prompt()
		
	def _show_welcome_message(self):
		self._sendmsg(welcome_message)

	def _show_command_prompt(self):
		self._sendmsg("\nEVENT> ")

	def _show_game_prompt(self):
		self._sendmsg("\nGAME>")

	def __del__(self):
		game_logger.info('A game with uuid {} was deleted'.format(self.game_uuid))
		self.game_log_file.close()
		# as the game object is no longer active, change the player status to OFFLINE
		# this also covers the case of accidental disconnect.
		if self.player_uuid != "WAITING":	# check if the player was in waiting while disconnected
			with self.db_query_lock:
				self.db_query_q.put("update_online_status")
				self.db_query_q.put(",".join([self.player_uuid, "OFFLINE"]))
