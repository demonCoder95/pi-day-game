# This will be the object that handles the lifecycle of a game thread
# Author: Noor
# Date: March 10, 2021
import logging
import time

from server_code.player import Player
from server_code.my_time import show_time_to
from pyfiglet import Figlet

# setup logging for the module
game_logger = logging.getLogger(__name__)

# TODO: add this in a project wide config
event_start_str = "Mon Mar 15 09:00:00 2021"

class GameHandler:
	def __init__(self, player_conn, player_addr, db_query_q, db_resp_q, db_query_lock, event_started, event_ended):
		game_logger.debug("Startin a handler for {}".format(player_addr))
		# Capture the login time
		self.login_time = time.asctime()

		# The player object that the handler will manipulate	
		self.game_player = Player(player_conn, player_addr, self.login_time, db_query_q, db_resp_q, db_query_lock, event_ended)
		
		# The connection object to handle communication back to the player
		self.player_conn = player_conn
		# The address information of the player
		self.player_addr = player_addr

		# send a timestamp back to the player
		self._sendmsg("Connected with game server at {}\n".format(self.login_time))

		# save the event started flag only, for gate-keeping logic
		self.event_started = event_started
		self.event_ended = event_ended

		game_logger.debug("Started a handler for {}".format(player_addr))

	# a small wrapper to handle bytes encoding of str
	def _sendmsg(self, msg):
		self.player_conn.sendall(bytes(msg, 'utf-8'))

	def run_game(self):
		# while the event is not set, block the player from entering
		msg_figlet = Figlet()
		while not self.event_started.is_set() and not self.event_ended.is_set():
			status_msg = ""
			status_msg += "\nEVENT STARTS IN"
			status_msg += "\n{}\n".format(msg_figlet.renderText(show_time_to(event_start_str)))
			self._sendmsg(status_msg)
			time.sleep(1)

		if not self.event_ended.is_set():
			self._sendmsg("The event is LIVE. Let's go!\n")
		else:
			self._sendmsg("The event has ENDED. Check the 'leaderboard' after you get in!\n")
		self.game_player.start_playing()

	def __del__(self):
		try:
			self._sendmsg("Closing your connection with the game server.\nGood bye!")
			game_logger.info("Connection closed by {}. Reason : {}".format(self.player_addr, "Player left"))
			print("Connection closed by {}. Reason : {}".format(self.player_addr, "Player left"))
		except BrokenPipeError as error:
			game_logger.info("Connection closed by {}. Reason : {}".format(self.player_addr, error))
			print("Connection closed by {}. Reason : {}".format(self.player_addr, error))
		finally:
			# close the connection socket
			self.player_conn.close()


