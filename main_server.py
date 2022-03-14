# This will be the main game server
# Author: Noor
# Date: March 10, 2021
from server_code.my_time import show_time_since, convert_str_secs, show_time_to
from server_code.game import Game
from server_code.game_handler import GameHandler
from server_code.db_handler import DBHandler

import logging
import socket
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import queue
from pyfiglet import Figlet
 
#TODO: add strong exception handling EVERYWHERE

# Setup game logging
logging.basicConfig(filename="logs/server.log",
					level=logging.DEBUG,
					format="%(asctime)s: %(name)s: %(levelname)s: %(message)s" )
# The logger for this module
game_logger = logging.getLogger(__name__)

# Event starting and ending times
# TODO: Move these into a configuration file for the project
event_start_str = "Mon Mar 14 13:00:00 2022"
event_end_str = "Mon Mar 21 17:00:00 2022"

def game_handler_thread(client_conn, client_addr, db_query_q, db_resp_q, db_query_lock, event_started, event_ended):
	"""The thread which will run one client connection"""	
	client_handler = GameHandler(client_conn, client_addr, db_query_q, db_resp_q, db_query_lock, event_started, event_ended)
	client_handler.run_game()

def db_handler_thread(db_query_q, db_resp_q, db_query_lock):
	"""This is the only thread that will manipulate the DB"""
	db_handler = DBHandler()
	while True:
		"""
		Each game thread will send 2 items on the queue, after acquiring the lock:
		1- the type of operation
		2- the data needed for the operation in CSV format

		The handler will parse the operation type to determine how to make sense
		of the data it has received as object 2.

		Operation types can be:
		create_player
		player_exists
		update_login
		update_hints
		update_task
		and so on

		Only need locks for player_exists type of operation
		"""
		op_type = db_query_q.get()	# first item is operation
		op_data = db_query_q.get()	# second item is the data
		op_data = op_data.split(",")	# CSV to list conversion

		if op_type == "create_player":
			db_handler.create_new_player(op_data[0], op_data[1], op_data[2], op_data[3], op_data[4], op_data[5], op_data[6], op_data[7])
		elif op_type == "player_exists":
			resp = db_handler.check_player_exists(op_data[0])
			db_resp_q.put(resp)
		elif op_type == "update_login_time":
			db_handler.update_login_time(op_data[0], op_data[1])
		elif op_type == "update_hints":
			db_handler.update_hints_left(op_data[0], op_data[1])
		elif op_type == "update_task":
			db_handler.update_current_task(op_data[0], op_data[1])
		elif op_type == "update_points":
			db_handler.update_points(op_data[0], op_data[1])
		elif op_type == "update_online_status":
			db_handler.update_online_status(op_data[0], op_data[1])
		elif op_type == "update_hint_used":
			db_handler.update_hint_used(op_data[0], op_data[1])
		
		# the operations to resume progress
		elif op_type == "get_hints":
			resp = db_handler.get_hints(op_data[0])
			db_resp_q.put(resp)
		elif op_type == "get_task":
			resp = db_handler.get_task(op_data[0])
			db_resp_q.put(resp)
		elif op_type == "get_points":
			resp = db_handler.get_points(op_data[0])
			db_resp_q.put(resp)
		elif op_type == "get_hint_used":
			resp = db_handler.get_hint_used(op_data[0])
			db_resp_q.put(resp)
		elif op_type == "get_online_status":
			resp = db_handler.get_online_status(op_data[0])
			db_resp_q.put(resp)

		# data to populate the leaderboard
		elif op_type == "get_leaderboard_data":
			resp = db_handler.get_leaderboard_data()
			db_resp_q.put(resp)

def get_player_data(db_query_q, db_resp_q, db_query_lock):
	"""Perform a db operation to get total and online player count"""
	player_data = []
	n_players = 0
	n_online = 0

	with db_query_lock:
		db_query_q.put("get_leaderboard_data")
		db_query_q.put("")	# dummy data
		player_data = db_resp_q.get()

	n_players = len(player_data)
	n_online = 0
	for each_player in player_data:
		if each_player[1] == "ONLINE":
			n_online += 1
	return (n_players, n_online)

def status_message_thread(db_query_q, db_resp_q, db_query_lock, server_up_timestamp, event_started, event_ended, event_start_str, event_end_str):
	"""Prints various statistics about the game server every few seconds"""
	# a figlet object is only created once in a thread
	msg_figlet = Figlet()
	while not event_started.is_set() and not event_ended.is_set():
		status_msg = ""
		status_msg += "\nEVENT STARTS IN"
		status_msg += "\n{}\n".format(msg_figlet.renderText(show_time_to(event_start_str)))
		status_msg += "Server up since: {}({})\n".format(server_up_timestamp, show_time_since(server_up_timestamp))
		status_msg += "=-"*30
		print(status_msg)
		time.sleep(1)
	
	event_started.wait()
	while event_started.is_set() and not event_ended.is_set():
		n_players, n_online = get_player_data(db_query_q, db_resp_q, db_query_lock)
		status_msg = ""
		status_msg += "\nEVENT ENDS IN\n"
		status_msg += "\n{}\n".format(msg_figlet.renderText(show_time_to(event_end_str)))
		status_msg += "Total players: {}, Online: {}\n".format(n_players, n_online)
		status_msg += "Server up since: {}({})\n".format(server_up_timestamp, show_time_since(server_up_timestamp))
		status_msg += "=-"*30
		print(status_msg)
		# to save processing during the event, delay the status a bit
		time.sleep(3)

	event_ended.wait()
	while event_ended.is_set():
		n_players, n_online = get_player_data(db_query_q, db_resp_q, db_query_lock)
		status_msg = ""
		status_msg += "\nEVENT HAS ENDED\n"
		status_msg += "Total players: {}, Online: {}\n".format(n_players, n_online)
		status_msg += "Server up since: {}({})\n".format(server_up_timestamp, show_time_since(server_up_timestamp))
		status_msg += "=-"*30
		print(status_msg)
		# restore per second status after the event
		time.sleep(1)

def event_notifier_thread(event_started, event_ended, event_start_str, event_end_str):
	"""
	This thread will use the given timestamps for the event and will independently
	monitor if the given event has started/ended and set threading.Event flags appropriately"""
	# Convert the event_start and end times to seconds
	event_start = convert_str_secs(event_start_str)
	event_end = convert_str_secs(event_end_str)

	while True:
		# time right now in seconds since epoch
		time_now = time.time()

		# if the event hasn't started yet, or is not already started
		if time_now >= event_start and not event_started.is_set():
			event_started.set()
			game_logger.info("Event has started!")

		# if the event hasn't ended yet, or is not already ended
		if time_now >= event_end and not event_ended.is_set():
			event_ended.set()
			game_logger.info("Event has ended!")

		# otherwise, don't mess with the flags, just sleep and do nothing
		time.sleep(1)

def game_server_loop():
	"""This will be the main server loop for the game"""

	# get the timestamp to determine server uptime
	server_up_timestamp = time.asctime()
	
	# The server socket
	# server_ip = "172.30.235.100"
	server_ip = "127.0.0.1"
	server_addr = (server_ip, 3141)	# will listen on any interface and port 3141
	server_backlog = 5	# the connections to keep on hold before refusing
	
	# Flags to determine event starting and stopping
	event_started = threading.Event()
	event_ended = threading.Event()

	# a thread pool to handle game threads
	server_thread_executor = ThreadPoolExecutor(max_workers=50)

	# the query/resp queues which will be used by the threads to 
	# communicate with the database
	db_query_q = queue.Queue(10)
	db_resp_q = queue.Queue(10)
	# a lock to ensure synchronization between threads
	db_query_lock = threading.Lock()

	# a separate thread pool executor for management threads
	management_thread_executor = ThreadPoolExecutor(max_workers=10)

	# start the event notifier thread
	management_thread_executor.submit(event_notifier_thread, event_started, event_ended, event_start_str, event_end_str)
	# start the db thread
	management_thread_executor.submit(db_handler_thread, db_query_q, db_resp_q, db_query_lock)
	# start the server monitor thread
	management_thread_executor.submit(status_message_thread, db_query_q, db_resp_q, db_query_lock, server_up_timestamp, event_started, event_ended, event_start_str, event_end_str)



	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		# to avoid a Address in Use error, make the binding reusable
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(server_addr)
		
		while True:
			print("Server listening...")
			# start listening with a backlog of 5 connections
			s.listen(server_backlog)
			
			# For debugging purposes
			try:
				client_conn, client_addr = s.accept()
			except KeyboardInterrupt:
				print("Exiting Server")
				# On a force closure, make sure to close the socket object properly
				s.close()
				exit()

			print("Accepted a new connection from {} on port {}".format(client_addr[0], client_addr[1]))
			server_thread_executor.submit(game_handler_thread, client_conn, client_addr,db_query_q, db_resp_q, db_query_lock, event_started, event_ended)

if __name__ == '__main__':
	print("Server Started.")
	game_server_loop()

	