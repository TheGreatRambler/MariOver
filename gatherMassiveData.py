from socket import timeout
from urllib.request import urlopen
import orjson
import time
import os
import sys
import subprocess
from timeit import default_timer as timer
import psutil
from urllib.error import HTTPError
from datetime import datetime
import random
import sqlite3
import linecache

server_proc = None
server_proc_psutil = None
def restart_server():
	global server_proc
	global server_proc_psutil
	if server_proc != None:
		server_proc_psutil.terminate()
	env = os.environ.copy()
	env["SERVER_DEBUG_ENABLED"] = "1"
	server_proc = subprocess.Popen(["start", "cmd", "/c", "python", "-m", "uvicorn", "levelInfoWebserver:app", "--port", "9876"], env=env, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
	time.sleep(3)
	for proc in psutil.process_iter():
		try:
			if "uvicorn" in proc.cmdline():
				print("Found uvicorn")
				server_proc_psutil = proc
		except:
			None

# Unneccesary
def fix_levels_without_data():
	level_infos = set()
	for d in os.scandir("cache/level_info"):
		if d.is_file():
			level_infos.add(d.name)

	all_thumbnail_files = set()
	for d in os.scandir("cache/level_thumbnail"):
		if d.is_file():
			all_thumbnail_files.add(d.name)

	all_level_data_files = set()
	for d in os.scandir("cache/level_data"):
		if d.is_file():
			all_level_data_files.add(d.name)
	
	all_thumbnail_ids = []
	all_ids = []
	for info in level_infos:
		if not (info + ".jpg") in all_thumbnail_files:
			print("Getting %s thumbnail" % info)
			all_thumbnail_ids.append(info)
		if not (info + ".bcd") in all_level_data_files:
			print("Getting %s level data" % info)
			all_ids.append(info)

	data_infos = []
	for d in os.scandir("cache/level_data"):
		if d.is_file():
			data_infos.append(os.path.splitext(d.name)[0])

	for data in data_infos:
		if not data in level_infos:
			print("Extra data info " + data + ", deleting")
			os.remove("cache/level_data/%s.bcd" % data) 

	if len(all_thumbnail_ids) != 0:
		print("Have %d thumbnails to process" % len(all_thumbnail_ids))
		for ids in [all_thumbnail_ids[i:i+5000] for i in range(len(all_thumbnail_ids))[::5000]]:
			all_thumbnail_ids_string = ""
			for id in ids:
				all_thumbnail_ids_string += id + ","
			all_thumbnail_ids_string = all_thumbnail_ids_string[:-1]
			try:
				urlopen("http://127.0.0.1:9876/level_thumbnail_multiple/" + all_thumbnail_ids_string, timeout=400).read()
			except HTTPError:
				# Ignore status code 500, timeout still restarts the server
				pass
			print("5000 thumbnails were processed")
		print("All thumbnails were processed")

	if len(all_ids) != 0:
		print("Have %d level data to process" % len(all_ids))
		for ids in [all_ids[i:i+5000] for i in range(len(all_ids))[::5000]]:
			all_ids_string = ""
			for id in ids:
				all_ids_string += id + ","
			all_ids_string = all_ids_string[:-1]
			try:
				urlopen("http://127.0.0.1:9876/level_data_multiple/" + all_ids_string, timeout=400).read()
			except HTTPError:
				# Ignore status code 500, timeout still restarts the server
				pass
			print("5000 level data were processed")
		print("All level data were processed")

restart_server()

scrape_levels = False
scrape_users = False
if sys.argv[1] == "levels":
	scrape_levels = True
if sys.argv[1] == "users":
	scrape_users = True

# https://stackoverflow.com/a/43690506
def human_readable_size(size, decimal_places=2):
	for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
		if size < 1024.0 or unit == 'PiB':
			break
		size /= 1024.0
	return f"{size:.{decimal_places}f} {unit}"

def elapsed_time(file):
	global last_timer_reading
	last_timer_reading = timer() - timer_start + timing_start
	print_both("Elapsed time in seconds: %d" % last_timer_reading, file)

def print_both(line, file):
	print(line)
	print(line, file=file)

timer_start = timer()
timing_start = 0
last_data_id_initial = 3000000
last_data_id = last_data_id_initial
if os.path.exists("last_data_id.txt"):
	with open("last_data_id.txt", mode="r") as f:
		parts = f.read().split(",")
		last_data_id = int(parts[0])
		timing_start = int(parts[1])

number_to_increase_by = 500
last_timer_reading = 0
last_users_count = 0
last_comments_count = 0

last_user_index = 0
if scrape_users:
	if not os.path.exists("cached_users.txt"):
		with open("cached_users.txt", mode="w") as f:
			con = sqlite3.connect("dump.db")
			pids = con.execute("SELECT pid FROM user")
			for pid in pids:
				f.write(pid[0] + "\n")
	if os.path.exists("last_user.txt"):
		with open("last_user.txt", mode="r") as f:
			user_index = int(f.read())

number_to_increase_by_users = 1000

keep_going = True
with open("log.txt", "a") as logging_file:
	print_both("Start logging", logging_file)
	while keep_going:
		time.sleep(1)
		if scrape_levels:
			try:
				print_both(str(datetime.now()), logging_file)
				print_both("Data id: %d" % last_data_id, logging_file)
				int_list = list(range(last_data_id, last_data_id + number_to_increase_by))
				random.shuffle(int_list)
				string_list = [str(id) for id in int_list]
				contents = orjson.loads(urlopen("http://127.0.0.1:9876/scraping?dataIds=" + ",".join(string_list), timeout=2000).read())
				last_data_id = last_data_id + number_to_increase_by
				last_timer_reading_old = last_timer_reading
				last_timer_reading = timer() - timer_start + timing_start
				with open("last_data_id.txt", mode="w+") as f:
					f.write(str(last_data_id) + "," + str(int(last_timer_reading)))
				if contents["num_courses"] > 0:
					print_both("Levels date: %s" % contents["uploaded"], logging_file)
				elapsed_time(logging_file)
				logging_file.flush()
				print_both("Time taken this run: %d" % (last_timer_reading - last_timer_reading_old), logging_file)
				print_both("Levels this run: %d" % contents["num_courses"], logging_file)
				con = sqlite3.connect("dump.db")
				cur = con.cursor()
				levels_so_far = cur.execute("SELECT MAX(_ROWID_) FROM level LIMIT 1").fetchone()[0]
				users_so_far = cur.execute("SELECT MAX(_ROWID_) FROM user LIMIT 1").fetchone()[0]
				comments_so_far = cur.execute("SELECT MAX(_ROWID_) FROM level_comments LIMIT 1").fetchone()[0]
				if last_users_count != 0:
					print_both("Users this run: %d" % (users_so_far - last_users_count), logging_file)
				if last_comments_count != 0:
					print_both("Comments this run: %d" % (comments_so_far - last_comments_count), logging_file)
				last_users_count = users_so_far
				last_comments_count = comments_so_far
				print_both("Levels so far: %d" % levels_so_far, logging_file)
				print_both("Users so far: %d" % users_so_far, logging_file)
				print_both("Comments so far: %d" % comments_so_far, logging_file)
				con.close()
				estimated_days_left = (((last_timer_reading / (last_data_id - 3000000)) * 32780000) - last_timer_reading) / 86400
				print_both("Estimated days left: {:0.2f}".format(estimated_days_left), logging_file)
				if last_data_id > 35780000:
					print_both("Stopping due to completion case", logging_file)
					keep_going = False
				logging_file.flush()
			except timeout:
				print_both("Attempt to restart server", logging_file)
				restart_server()
			except Exception as e:
				print_both("API error (%s), continuing" % str(e), logging_file)
			print_both("-----------------------------", logging_file)
		if scrape_users:
			try:
				print_both("User index: %d" % last_user_index, logging_file)
				users = []
				for i in range(0, number_to_increase_by_users):
					line = linecache.getline("cached_users.txt", last_user_index + i)
					if line:
						users.append(line)
					else:
						print_both("Stopping due to completion case", logging_file)
						keep_going = False
						break
				users = ",".join(users)
				contents = orjson.loads(urlopen("http://127.0.0.1:9876/scraping2?pids=" + users, timeout=2000).read())
				last_user_index += number_to_increase_by_users
				with open("last_user.txt", mode="w+") as f:
					f.write(str(last_user_index))
				elapsed_time(logging_file)
				logging_file.flush()
			except timeout:
				print_both("Attempt to restart server", logging_file)
				restart_server()
			except Exception as e:
				print_both("API error (%s), continuing" % str(e), logging_file)
			print_both("-----------------------------", logging_file)
