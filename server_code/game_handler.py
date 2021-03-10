# This will be the object that handles the lifecycle of a game thread
# Author: Noor
# Date: March 10, 2021
import logging
import time

from server_code.player import Player

# setup logging for the module
game_logger = logging.getLogger(__name__)


#TODO: add last log in time to connection
class GameHandler:
	def __init__(self, player_conn, player_addr, db_query_q, db_resp_q, db_query_lock):
		game_logger.debug("Startin a handler for {}".format(player_addr))
		# Capture the login time
		self.login_time = time.asctime()

		# The player object that the handler will manipulate	
		self.game_player = Player(player_conn, player_addr, self.login_time, db_query_q, db_resp_q, db_query_lock)
		
		# The connection object to handle communication back to the player
		self.player_conn = player_conn
		# The address information of the player
		self.player_addr = player_addr

		# send a timestamp back to the player
		self._sendmsg("Connected with game server at {}\n".format(self.login_time))

		game_logger.debug("Started a handler for {}".format(player_addr))

	# a small wrapper to handle bytes encoding of str
	def _sendmsg(self, msg):
		self.player_conn.sendall(bytes(msg, 'utf-8'))

	def run_game(self):
		self.game_player.start_playing()

	def __del__(self):
		#TODO: handle premature closing of connection on client side
		self._sendmsg("Closing your connection with the game server.\nGood bye!")
		# close the connecition socket
		self.player_conn.close()
		game_logger.info("Handler for {} exited.".format(self.player_addr))
		print("Thread for connection {} exited".format(self.player_addr))


