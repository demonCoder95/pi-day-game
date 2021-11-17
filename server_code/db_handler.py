"""This will be responsible for doing everything that is DB oriented
including sanitizing input data, performing queries and so on.

Aurthor: Noor
Date: March 10, 2021
"""
import sqlite3
import logging

game_logger = logging.getLogger(__name__)

db_filename = "data/game.db"
player_table_schema = "(player_id TEXT, game_id TEXT, login_time TEXT, current_task INTEGER, hints_left INTEGER, points INTEGER, online_status TEXT, hint_used TEXT)"
player_table_name = "players"

"""
The database schema is explained below:
player_id: the ID provided by the player for identification
game_id: a UUID4 used internally to keep track of games that the player has played
login_time: the last time the player logged into the server
current_task: the task player is currently solving
hints_left: the number of hints left
points: the points earned by the player
online_status: whether a player is currently playing the game
hint_used: to determine if the hint was used on a level before the player disconnected.
	this is to solve the problem where if a player disconnects after using the hint,
	the program will treat it as if he never used the hint and subtract an extra hint
	if he wishes to see the hint again.
"""

class DBHandler:
	def __init__(self):
		game_logger.debug("Initializing game database...")
		self.conn = sqlite3.connect(db_filename)
		self.cur = self.conn.cursor()

		if not self._check_table_exists():
			self.cur.execute("CREATE TABLE " + player_table_name + player_table_schema)
		self._reset_online_status()
		game_logger.debug("Game database initialized successfully.")

	def _reset_online_status(self):
		"""Need to reset the online status of each player,
		when the server boots up after a shutdown"""
		query = "UPDATE {} SET online_status='OFFLINE'".format(player_table_name)
		self.cur.execute(query)
		self.conn.commit()
		game_logger.info("Player status reset to OFFLINE for all players")

	def create_new_player(self, player_id, game_id, login_time, current_task, hints_left, points, online_status, hint_used):
		values_str = "('{}', '{}', '{}', {}, {}, {}, '{}', '{}')".format(
			player_id, game_id, login_time, current_task, hints_left, points, online_status, hint_used)
		query_str = "INSERT INTO {} VALUES {}".format(player_table_name, values_str)
		self.cur.execute(query_str)
		self.conn.commit()
		game_logger.info("Added player to db: {}".format(values_str))

	def check_player_exists(self, player_id):
		"""Check is a player exists in the database"""
		query= "SELECT player_id from " + player_table_name
		self.cur.execute(query)
		resp = self.cur.fetchall()
		for each_item in resp:
			if each_item[0] == player_id:
				return True
		return False

	def update_login_time(self, player_id, new_time):
		"""Update the player login time in the database"""
		query = "UPDATE {} SET login_time='{}' WHERE player_id='{}'".format(player_table_name, new_time, player_id)
		self.cur.execute(query)
		self.conn.commit()
		game_logger.info("Login_time of player {} updated to {}".format(player_id, new_time))

	def update_current_task(self, player_id, current_task):
		"""Update the task the player is currently on to save progress"""
		query = "UPDATE {} SET current_task={} WHERE player_id='{}'".format(player_table_name, current_task, player_id)
		self.cur.execute(query)
		self.conn.commit()
		game_logger.info("Current_task of player {} updated to {}".format(player_id, current_task))

	def update_hints_left(self, player_id, hints_left):
		"""Update the hints left for the player in the database"""
		query = "UPDATE {} SET hints_left={} WHERE player_id='{}'".format(player_table_name, hints_left, player_id)
		self.cur.execute(query)
		self.conn.commit()
		game_logger.info("Hints_left of player {} updated to {}".format(player_id, hints_left))

	def update_points(self, player_id, points):
		"""Update the points for the player in the database"""
		query = "UPDATE {} SET points={} WHERE player_id='{}'".format(player_table_name, points, player_id)
		self.cur.execute(query)
		self.conn.commit()
		game_logger.info("Points of player {} updated to {}".format(player_id, points))

	def update_online_status(self, player_id, status):
		"""Update the player online status as he leaves the game, or is disconnected."""
		query = "UPDATE {} SET online_status='{}' WHERE player_id='{}'".format(player_table_name, status, player_id)
		self.cur.execute(query)
		self.conn.commit()
		game_logger.info("Player {} status now {}.".format(player_id, status))

	def update_hint_used(self, player_id, hint_used):
		"""Update the fact that the player has used the hint on this task"""
		query = "UPDATE {} SET hint_used='{}' WHERE player_id='{}'".format(player_table_name, hint_used, player_id)
		self.cur.execute(query)
		self.conn.commit()
		game_logger.info("Player {} hint_used set to {}".format(player_id, hint_used))

	def _check_table_exists(self):
		# the sqlite_master table holds a list of all tables
		self.cur.execute("SELECT * FROM sqlite_master WHERE type='table'")
		tables = self.cur.fetchall()
		for each_item in tables:
			if each_item[1] == player_table_name:
				return True
		return False

	# Operations that resume the player progress when existing player returns. They are all returned
	# as INT type
	def get_hints(self, player_id):
		query = "SELECT hints_left FROM {} WHERE player_id='{}'".format(player_table_name, player_id)
		self.cur.execute(query)
		resp = self.cur.fetchone()
		return resp[0]

	def get_points(self, player_id):
		query = "SELECT points FROM {} WHERE player_id='{}'".format(player_table_name, player_id)
		self.cur.execute(query)
		resp = self.cur.fetchone()
		return resp[0]

	def get_task(self, player_id):
		query = "SELECT current_task FROM {} WHERE player_id='{}'".format(player_table_name, player_id)
		self.cur.execute(query)
		resp = self.cur.fetchone()
		return resp[0]

	def get_hint_used(self, player_id):
		query = "SELECT hint_used FROM {} WHERE player_id='{}'".format(player_table_name, player_id)
		self.cur.execute(query)
		resp = self.cur.fetchone()
		return resp[0]

	def get_online_status(self, player_id):
		query = "SELECT online_status FROM {} WHERE player_id='{}'".format(player_table_name, player_id)
		self.cur.execute(query)
		resp = self.cur.fetchone()
		return resp[0]

	# Operation to get all the database data to populate leaderboard
	def get_leaderboard_data(self):
		query = "SELECT player_id,online_status,login_time,points FROM {} ORDER BY points DESC".format(player_table_name)
		self.cur.execute(query)
		resp = self.cur.fetchall()
		return resp

	def __del__(self):
		pass

