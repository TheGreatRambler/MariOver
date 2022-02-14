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
scrape_worlds = False
scrape_users2 = False
check = False
scrape_ninji = False
scrape_ninji_levels = False
scrape_random = False
optimize_database = False
if sys.argv[1] == "levels":
	scrape_levels = True
if sys.argv[1] == "users":
	scrape_users = True
if sys.argv[1] == "worlds":
	scrape_worlds = True
if sys.argv[1] == "users2":
	scrape_users2 = True
if sys.argv[1] == "check":
	check = True
if sys.argv[1] == "ninji":
	scrape_ninji = True
if sys.argv[1] == "ninji_levels":
	scrape_ninji_levels = True
if sys.argv[1] == "random":
	scrape_random = True
if sys.argv[1] == "optimize":
	optimize_database = True

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

if scrape_levels:
	keep_going = True
	with open("log.txt", "a") as logging_file:
		print_both("Start logging", logging_file)
		while keep_going:
			time.sleep(1)
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
				estimated_days_left = (((last_timer_reading / (last_data_id - 3000000)) * 35000000) - last_timer_reading) / 86400
				print_both("Estimated days left: {:0.2f}".format(estimated_days_left), logging_file)
				if last_data_id > 38000000:
					print_both("Stopping due to completion case", logging_file)
					keep_going = False
				logging_file.flush()
			except timeout:
				print_both("Attempt to restart server", logging_file)
				restart_server()
			except Exception as e:
				print_both("API error (%s), continuing" % str(e), logging_file)
			print_both("-----------------------------", logging_file)

def data_id_to_maker_id(id):
	charset = "0123456789BCDFGHJKLMNPQRSTVWXY"
	fieldB = (id - 31) % 64
	exed = id ^ 0b00010110100000001110000001111100
	fieldC = exed & 0b00000000000011111111111111111111
	fieldF = exed >> 20
	fieldD = 0b1
	intermediate = (0b1000 << 40) + (fieldB << 34) + (fieldC << 14) + (fieldD << 13) + (0b1 << 12) + fieldF
	converted_id = ""
	index = 0
	while intermediate > 0:
		charIndex = intermediate % 30
		converted_id += charset[charIndex]
		intermediate //= 30
		index += 1
	return converted_id

if scrape_users:
	with open("log2.txt", "a") as logging_file:
		con = sqlite3.connect("dump.db")
		pids = con.execute("SELECT data_id FROM user")
		i = 0
		maximum_data_id = 0
		users = set()
		for pid in pids:
			data_id = int(pid[0])
			if data_id > maximum_data_id:
				print("New maximum data_id is %d" % data_id)
				maximum_data_id = data_id
			users.add(data_id)
			i += 1
			if i % 10000 == 0:
				print("Checked %d players so far" % i)
		print_both("Len users %d maximum data_id %d" % (len(users), maximum_data_id), logging_file)
		con.close()

		current_user_index = 0
		if os.path.exists("last_user_id.txt"):
			with open("last_user_id.txt", mode="r") as f:
				current_user_index = int(f.read())

		while current_user_index < maximum_data_id:
			print_both(str(datetime.now()), logging_file)
			print_both("Data id start: %d" % current_user_index, logging_file)

			users_to_request = []
			while len(users_to_request) < 3000:
				if not current_user_index in users:
					users_to_request.append(data_id_to_maker_id(current_user_index))
				current_user_index += 1
			contents = orjson.loads(urlopen("http://127.0.0.1:9876/scraping2?ids=" + ",".join(users_to_request), timeout=5000).read())

			with open("last_user_id.txt", mode="w+") as f:
				f.write(str(current_user_index))

			con = sqlite3.connect("dump.db")
			users_so_far = con.execute("SELECT MAX(_ROWID_) FROM user LIMIT 1").fetchone()[0]
			print_both("Users gotten so far: %d" % users_so_far, logging_file)
			con.close()

			print_both("-----------------------------", logging_file)
			logging_file.flush()
			time.sleep(1)
		print_both("Stopped due to data_id exceeding maximum", logging_file)

if scrape_worlds:
	orjson.loads(urlopen("http://127.0.0.1:9876/scraping3", timeout=5000).read())

if scrape_users2:
	with open("log3.txt", "a") as logging_file:
		con = sqlite3.connect("dump.db")

		current_user_index = 0
		if os.path.exists("last_user_id2.txt"):
			with open("last_user_id2.txt", mode="r") as f:
				current_user_index = int(f.read())

		pids = con.execute("SELECT pid FROM user")
		i = 0
		users = []
		for pid in pids:
			if i >= current_user_index:
				users.append(pid[0])
			i += 1
			if i % 10000 == 0:
				print("Checked %d players so far" % i)
		print_both("Len users %d" % len(users), logging_file)
		con.close()

		user_chunks = [users[i:i+1000] for i in range(len(users))[::1000]]

		chunk_index = 0
		chunk = user_chunks[chunk_index]
		while chunk is not None:
			try:
				print_both(str(datetime.now()), logging_file)
				print_both("User index is %d" % current_user_index, logging_file)
	
				contents = orjson.loads(urlopen("http://127.0.0.1:9876/scraping4?pids=" + ",".join(chunk), timeout=5000).read())
	
				current_user_index += len(chunk)
				with open("last_user_id2.txt", mode="w+") as f:
					f.write(str(current_user_index))
	
				print_both("Posted this run: %d" % contents["posted"], logging_file)
				print_both("Liked this run: %d" % contents["liked"], logging_file)
				print_both("Played this run: %d" % contents["played"], logging_file)
				print_both("First cleared this run: %d" % contents["first_cleared"], logging_file)
				print_both("World record this run: %d" % contents["world_record"], logging_file)
				logging_file.flush()
				time.sleep(1)
				chunk_index += 1
				if chunk_index == len(user_chunks):
					chunk = None
				else:
					chunk = user_chunks[chunk_index]
			except Exception as e:
				print_both("API error (%s), continuing" % str(e), logging_file)
			print_both("-----------------------------", logging_file)
		print_both("Every chunk done", logging_file)

if scrape_ninji:
	con = sqlite3.connect("dump.db")

	print("RS     %d" % (365366 - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=12171034 LIMIT 1").fetchone()[0]))
	print("TSoL   %d" % (204849 - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=12619193 LIMIT 1").fetchone()[0]))
	print("CoDW   %d" % (209097 - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=13428950 LIMIT 1").fetchone()[0]))
	print("CMD    %d" % (202793 - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=14328331 LIMIT 1").fetchone()[0]))
	print("BBCC   %d" % (168703 - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=14827235 LIMIT 1").fetchone()[0]))
	print("SCF    %d" % (189040 - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=15675466 LIMIT 1").fetchone()[0]))
	print("HH     %d" % (218865 - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=17110274 LIMIT 1").fetchone()[0]))
	print("BR     %d" % (220576 - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=20182790 LIMIT 1").fetchone()[0]))
	print("YPPP   %d" % (150860 - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=21858065 LIMIT 1").fetchone()[0]))
	print("PCPUP  %d" % (140888 - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=22587491 LIMIT 1").fetchone()[0]))
	print("BSGitD %d" % (108323 - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=23303835 LIMIT 1").fetchone()[0]))
	print("SAE    %d" % (121491 - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=23738173 LIMIT 1").fetchone()[0]))
	print("AtCoM  %d" % (69813  - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=24477739 LIMIT 1").fetchone()[0]))
	print("AAM    %d" % (133055 - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=25045367 LIMIT 1").fetchone()[0]))
	print("CBB    %d" % (78050  - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=25459053 LIMIT 1").fetchone()[0]))
	print("GBU    %d" % (100664 - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=25984384 LIMIT 1").fetchone()[0]))
	print("CYDI   %d" % (93664  - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=26746705 LIMIT 1").fetchone()[0]))
	print("DBS    %d" % (84862  - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=27439231 LIMIT 1").fetchone()[0]))
	print("CMM    %d" % (52811  - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=28460377 LIMIT 1").fetchone()[0]))
	print("BCTLD  %d" % (101019 - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=29234075 LIMIT 1").fetchone()[0]))
	print("LLL    %d" % (73801  - con.execute("SELECT COUNT(*) FROM ninji WHERE data_id=33883306 LIMIT 1").fetchone()[0]))

	con.close()

	orjson.loads(urlopen("http://127.0.0.1:9876/scraping5", timeout=5000).read())

if scrape_ninji_levels:
	orjson.loads(urlopen("http://127.0.0.1:9876/scraping6", timeout=5000).read())

if scrape_random:
	orjson.loads(urlopen("http://127.0.0.1:9876/scraping7", timeout=5000).read())

if optimize_database:
	con = sqlite3.connect("dump.db")
	con.execute("CREATE INDEX IF NOT EXISTS idx_level_data_id ON level (data_id);")
	print("idx_level_data_id")
	con.execute("CREATE INDEX IF NOT EXISTS idx_level_comments_data_id ON level_comments (data_id);")
	print("idx_level_comments_data_id")
	con.execute("CREATE INDEX IF NOT EXISTS idx_level_deaths_data_id ON level_deaths (data_id);")
	print("idx_level_deaths_data_id")
	con.execute("CREATE INDEX IF NOT EXISTS idx_level_played_data_id ON level_played (data_id);")
	print("idx_level_played_data_id")
	con.execute("CREATE INDEX IF NOT EXISTS idx_ninji_data_id ON ninji (data_id);")
	print("idx_ninji_data_id")
	con.execute("CREATE INDEX IF NOT EXISTS idx_user_pid ON user (pid);")
	print("idx_user_pid")
	con.execute("CREATE INDEX IF NOT EXISTS idx_user_badges_pid ON user_badges (pid);")
	print("idx_user_badges_pid")
	con.execute("CREATE INDEX IF NOT EXISTS idx_user_first_cleared_pid ON user_first_cleared (pid);")
	print("idx_user_first_cleared_pid")
	con.execute("CREATE INDEX IF NOT EXISTS idx_user_liked_pid ON user_liked (pid);")
	print("idx_user_liked_pid")
	con.execute("CREATE INDEX IF NOT EXISTS idx_user_played_pid ON user_played (pid);")
	print("idx_user_played_pid")
	con.execute("CREATE INDEX IF NOT EXISTS idx_user_posted_pid ON user_posted (pid);")
	print("idx_user_posted_pid")
	con.execute("CREATE INDEX IF NOT EXISTS idx_user_world_record_pid ON user_world_record (pid);")
	print("idx_user_world_record_pid")
	con.execute("CREATE INDEX IF NOT EXISTS idx_world_pid ON world (pid);")
	print("idx_world_pid")
	con.execute("CREATE INDEX IF NOT EXISTS idx_world_levels_pid ON world_levels (pid);")
	print("idx_world_levels_pid")
	con.execute("PRAGMA optimize;")
	con.close()