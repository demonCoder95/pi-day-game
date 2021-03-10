# Implements all the functionality necessary to make a player feasible
import uuid
import logging
from server_code.game import Game

"""All the logic related to a player, will be here
"""

# THe logger for this module
game_logger = logging.getLogger(__name__)


class Player:
	def __init__(self, player_conn, player_addr, login_time, db_query_q, db_resp_q, db_query_lock):
		self.player_conn = player_conn
		self.player_addr = player_addr
		game_logger.debug("A new player created")
		self.player_game = Game(player_conn, player_addr, login_time, db_query_q, db_resp_q, db_query_lock)

	def start_playing(self):
		self.player_game.start_game()

	def __del__(self):
		pass