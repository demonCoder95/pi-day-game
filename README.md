# pi-day-game
A multi-threaded text interface game based on a fictional adventure, themed around Pi-day (March 14).

## How to Setup

1. First things first, you'll have to setup some directories that the game needs to run. For this,
run the ``setup.sh`` script. It will create the ``logs\``, ``logs\games``, ``logs\players`` and
``data`` directories.

2. Then you need to install the Python requirements on your machine.
  ```bash
  pip3 install -r requirements.txt
  ```
3. Then you need to configure event start and end times in the ``main_server.py`` file. 
```bash
event_start_str = "Mon Mar 14 13:00:00 2022"   <===== CHANGE HERE!
event_end_str = "Mon Mar 21 17:00:00 2022"     <===== CHANGE HERE!
```
Also, edit the ``server_code/game.py`` and configure the end time.
```bash
event_end_str = "Mon Mar 21 17:00:00 2022"     <===== CHANGE HERE!
```

4. Then you need to configure the IP address of the server in the ``main_server.py`` file.
```bash
...
def game_server_loop():
	"""This will be the main server loop for the game"""

	# get the timestamp to determine server uptime
	server_up_timestamp = time.asctime()
	
	# The server socket
	# server_ip = "172.30.235.100"
	server_ip = "127.0.0.1"   <===== CHANGE HERE!
...
```

Finally, just run the game, if required as a service as ``python3 main_server.py``.

The players can connect over with the service using netcat as ``nc $SERVER_IP 3141``. Here,
the ``$SERVER_IP`` is the IP address as configured in step 4.

The number of concurrent players supported is upto 50. More than 50 haven't been tested, but should
work fine.
The game has been tested with Python versions ``3.9``, ``3.8`` and ``3.6``.

