import pathlib
import asyncio
import time
from threading import Thread
import os
import json
import orjson
import os
import time
from binascii import hexlify
from struct import pack
from PIL import Image
import zlib
import base64
import io
from fastapi import FastAPI
from fastapi.responses import Response, ORJSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from gen3_switchgame import Gen3Switchgame
from nintendo.baas import BAASClient
from nintendo.dauth import DAuthClient
from nintendo.aauth import AAuthClient
from nintendo.switch import ProdInfo, KeySet
from nintendo.nex import backend, authentication, settings, datastore_smm2 as datastore
from nintendo.games import SMM2
from anynet import http
from enum import IntEnum

import logging
logging.basicConfig(level=logging.INFO)

args = {}
with open("webserver_args.json") as f:
	args = json.load(f)

if args["system_version"] is None:
	print("System version not set")
	print("Error")
	exit(1)
else:
	SYSTEM_VERSION = args["system_version"]

if args["user_id"] is None:
	print("User ID not set")
	print("Error")
	exit(1)
else:
	BAAS_USER_ID = int(args["user_id"], 16)

if args["password"] is None:
	print("Password not set")
	print("Error")
	exit(1)
else:
	BAAS_PASSWORD = args["password"]

if args["keys"] is None:
	print("Prod.keys not set")
	print("Error")
	exit(1)
else:
	keys = KeySet.load(args["keys"])

if args["prodinfo"] is None:
	print("Prodinfo not set")
	print("Error")
	exit(1)
else:
	info = ProdInfo(keys, args["prodinfo"])

if args["ticket"] is None:
	print("Ticket not set")
	print("Error")
	exit(1)
else:
	with open(args["ticket"], "rb") as f:
		ticket = f.read()

# Used for scraping
debug_enabled = False
if os.environ.get("SERVER_DEBUG_ENABLED") != None:
	print("Server debug enabled")
	debug_enabled = True

GameStyles = {
	0: "SMB1",
	1: "SMB3",
	2: "SMW",
	3: "NSMBU",
	4: "SM3DW"
}

Difficulties = {
	0: "Easy",
	1: "Normal",
	2: "Expert",
	3: "Super expert"
}

CourseThemes = {
	0: "Overworld",
	1: "Underground",
	2: "Castle",
	3: "Airship",
	4: "Underwater",
	5: "Ghost house",
	6: "Snow",
	7: "Desert",
	8: "Sky",
	9: "Forest"
}

TagNames = {
	0: "None",
	1: "Standard",
	2: "Puzzle solving",
	3: "Speedrun",
	4: "Autoscroll",
	5: "Auto mario",
	6: "Short and sweet",
	7: "Multiplayer versus",
	8: "Themed",
	9: "Music",
	10: "Art",
	11: "Technical",
	12: "Shooter",
	13: "Boss battle",
	14: "Single player",
	15: "Link"
}

Regions = {
	0: "Asia",
	1: "Americas",
	2: "Europe",
	3: "Other"
}

BadgeTypes = {
	0: "Maker Points (All-Time)",
	1: "Endless Challenge (Easy)",
	2: "Endless Challenge (Normal)",
	3: "Endless Challenge (Expert)",
	4: "Endless Challenge (Super Expert)",
	5: "Multiplayer Versus",
	6: "Number of Clears",
	7: "Number of First Clears",
	8: "Number of World Records",
	9: "Maker Points (Weekly)"
}

BadgeRanks = {
	6: "Bronze",
	5: "Silver",
	4: "Gold",
	3: "Bronze Ribbon",
	2: "Silver Ribbon",
	1: "Gold Ribbon"
}

CommentType = {
	0: "Custom Image",
	1: "Text",
	2: "Reaction Image"
}

CommentReactionImage = {
	0: "Nice!",
	1: "Good stuff!",
	2: "So tough...",
	3: "EASY",
	4: "Seriously?!",
	5: "Wow!",
	6: "Cool idea!",
	7: "SPEEDRUN!",
	8: "How?!",
	9: "Be careful!",
	10: "So close!",
	11: "Beat it!"
}

CommentReactionFace = {
	0: "Normal",
	16: "Wink",
	1: "Happy",
	4: "Surprised",
	18: "Scared",
	3: "Confused"
}

MultiplayerVersusRanks = {
	1: "D",
	2: "C",
	3: "B",
	4: "A",
	5: "S",
	6: "S+"
}

ClearConditions = {
	137525990: "Reach the goal without landing after leaving the ground.",
	199585683: "Reach the goal after defeating at least/all (n) Mechakoopa(s).",
	272349836: "Reach the goal after defeating at least/all (n) Cheep Cheep(s).",
	375673178: "Reach the goal without taking damage.",
	426197923: "Reach the goal as Boomerang Mario.",
	436833616: "Reach the goal while wearing a Shoe.",
	713979835: "Reach the goal as Fire Mario.",
	744927294: "Reach the goal as Frog Mario.",
	751004331: "Reach the goal after defeating at least/all (n) Larry(s).",
	900050759: "Reach the goal as Raccoon Mario.",
	947659466: "Reach the goal after defeating at least/all (n) Blooper(s).",
	976173462: "Reach the goal as Propeller Mario.",
	994686866: "Reach the goal while wearing a Propeller Box.",
	998904081: "Reach the goal after defeating at least/all (n) Spike(s).",
	1008094897: "Reach the goal after defeating at least/all (n) Boom Boom(s).",
	1051433633: "Reach the goal while holding a Koopa Shell.",
	1061233896: "Reach the goal after defeating at least/all (n) Porcupuffer(s).",
	1062253843: "Reach the goal after defeating at least/all (n) Charvaargh(s).",
	1079889509: "Reach the goal after defeating at least/all (n) Bullet Bill(s).",
	1080535886: "Reach the goal after defeating at least/all (n) Bully/Bullies.",
	1151250770: "Reach the goal while wearing a Goomba Mask.",
	1182464856: "Reach the goal after defeating at least/all (n) Hop-Chops.",
	1219761531: "Reach the goal while holding a Red POW Block. OR Reach the goal after activating at least/all (n) Red POW Block(s).",
	1221661152: "Reach the goal after defeating at least/all (n) Bob-omb(s).",
	1259427138: "Reach the goal after defeating at least/all (n) Spiny/Spinies.",
	1268255615: "Reach the goal after defeating at least/all (n) Bowser(s)/Meowser(s).",
	1279580818: "Reach the goal after defeating at least/all (n) Ant Trooper(s).",
	1283945123: "Reach the goal on a Lakitu's Cloud.",
	1344044032: "Reach the goal after defeating at least/all (n) Boo(s).",
	1425973877: "Reach the goal after defeating at least/all (n) Roy(s).",
	1429902736: "Reach the goal while holding a Trampoline.",
	1431944825: "Reach the goal after defeating at least/all (n) Morton(s).",
	1446467058: "Reach the goal after defeating at least/all (n) Fish Bone(s).",
	1510495760: "Reach the goal after defeating at least/all (n) Monty Mole(s).",
	1656179347: "Reach the goal after picking up at least/all (n) 1-Up Mushroom(s).",
	1665820273: "Reach the goal after defeating at least/all (n) Hammer Bro(s.).",
	1676924210: "Reach the goal after hitting at least/all (n) P Switch(es). OR Reach the goal while holding a P Switch.",
	1715960804: "Reach the goal after activating at least/all (n) POW Block(s). OR Reach the goal while holding a POW Block.",
	1724036958: "Reach the goal after defeating at least/all (n) Angry Sun(s).",
	1730095541: "Reach the goal after defeating at least/all (n) Pokey(s).",
	1780278293: "Reach the goal as Superball Mario.",
	1839897151: "Reach the goal after defeating at least/all (n) Pom Pom(s).",
	1969299694: "Reach the goal after defeating at least/all (n) Peepa(s).",
	2035052211: "Reach the goal after defeating at least/all (n) Lakitu(s).",
	2038503215: "Reach the goal after defeating at least/all (n) Lemmy(s).",
	2048033177: "Reach the goal after defeating at least/all (n) Lava Bubble(s).",
	2076496776: "Reach the goal while wearing a Bullet Bill Mask.",
	2089161429: "Reach the goal as Big Mario.",
	2111528319: "Reach the goal as Cat Mario.",
	2131209407: "Reach the goal after defeating at least/all (n) Goomba(s)/Galoomba(s).",
	2139645066: "Reach the goal after defeating at least/all (n) Thwomp(s).",
	2259346429: "Reach the goal after defeating at least/all (n) Iggy(s).",
	2549654281: "Reach the goal while wearing a Dry Bones Shell.",
	2694559007: "Reach the goal after defeating at least/all (n) Sledge Bro(s.).",
	2746139466: "Reach the goal after defeating at least/all (n) Rocky Wrench(es).",
	2749601092: "Reach the goal after grabbing at least/all (n) 50-Coin(s).",
	2855236681: "Reach the goal as Flying Squirrel Mario.",
	3036298571: "Reach the goal as Buzzy Mario.",
	3074433106: "Reach the goal as Builder Mario.",
	3146932243: "Reach the goal as Cape Mario.",
	3174413484: "Reach the goal after defeating at least/all (n) Wendy(s).",
	3206222275: "Reach the goal while wearing a Cannon Box.",
	3314955857: "Reach the goal as Link.",
	3342591980: "Reach the goal while you have Super Star invincibility.",
	3346433512: "Reach the goal after defeating at least/all (n) Goombrat(s)/Goombud(s).",
	3348058176: "Reach the goal after grabbing at least/all (n) 10-Coin(s).",
	3353006607: "Reach the goal after defeating at least/all (n) Buzzy Beetle(s).",
	3392229961: "Reach the goal after defeating at least/all (n) Bowser Jr.(s).",
	3437308486: "Reach the goal after defeating at least/all (n) Koopa Troopa(s).",
	3459144213: "Reach the goal after defeating at least/all (n) Chain Chomp(s).",
	3466227835: "Reach the goal after defeating at least/all (n) Muncher(s).",
	3481362698: "Reach the goal after defeating at least/all (n) Wiggler(s).",
	3513732174: "Reach the goal as SMB2 Mario.",
	3649647177: "Reach the goal in a Koopa Clown Car/Junior Clown Car.",
	3725246406: "Reach the goal as Spiny Mario.",
	3730243509: "Reach the goal in a Koopa Troopa Car.",
	3748075486: "Reach the goal after defeating at least/all (n) Piranha Plant(s)/Jumping Piranha Plant(s).",
	3797704544: "Reach the goal after defeating at least/all (n) Dry Bones.",
	3824561269: "Reach the goal after defeating at least/all (n) Stingby/Stingbies.",
	3833342952: "Reach the goal after defeating at least/all (n) Piranha Creeper(s).",
	3842179831: "Reach the goal after defeating at least/all (n) Fire Piranha Plant(s).",
	3874680510: "Reach the goal after breaking at least/all (n) Crates(s).",
	3974581191: "Reach the goal after defeating at least/all (n) Ludwig(s).",
	3977257962: "Reach the goal as Super Mario.",
	4042480826: "Reach the goal after defeating at least/all (n) Skipsqueak(s).",
	4116396131: "Reach the goal after grabbing at least/all (n) Coin(s).",
	4117878280: "Reach the goal after defeating at least/all (n) Magikoopa(s).",
	4122555074: "Reach the goal after grabbing at least/all (n) 30-Coin(s).",
	4153835197: "Reach the goal as Balloon Mario.",
	4172105156: "Reach the goal while wearing a Red POW Box.",
	4209535561: "Reach the Goal while riding Yoshi.",
	4269094462: "Reach the goal after defeating at least/all (n) Spike Top(s).",
	4293354249: "Reach the goal after defeating at least/all (n) Banzai Bill(s)."
}

UserPose = {
	0: "Normal",
	15: "Fidgety",
	17: "Annoyed",
	18: "Buoyant",
	19: "Thrilled",
	20: "Let's go!",
	21: "Hello!",
	29: "Show-Off",
	31: "Cutesy",
	39: "Hyped!"
}

UserHat = {
	0: "None",
	1: "Mario Cap",
	2: "Luigi Cap",
	4: "Mushroom Hairclip",
	5: "Bowser Headpiece",
	8: "Princess Peach Wig",
	11: "Builder Hard Hat",
	12: "Bowser Jr. Headpiece",
	13: "Pipe Hat",
	15: "Cat Mario Headgear",
	16: "Propeller Mario Helmet",
	17: "Cheep Cheep Hat",
	18: "Yoshi Hat",
	21: "Faceplant",
	22: "Toad Cap",
	23: "Shy Cap",
	24: "Magikoopa Hat",
	25: "Fancy Top Hat",
	26: "Doctor Headgear",
	27: "Rocky Wrench Manhold Lid",
	28: "Super Star Barrette",
	29: "Rosalina Wig",
	30: "Fried-Chicken Headgear",
	31: "Royal Crown",
	32: "Edamame Barrette",
	33: "Superball Mario Hat",
	34: "Robot Cap",
	35: "Frog Cap",
	36: "Cheetah Headgear",
	37: "Ninji Cap",
	38: "Super Acorn Hat",
	39: "Pokey Hat",
	40: "Snow Pokey Hat"
}

UserShirt = {
	0: "Nintendo Shirt",
	1: "Mario Outfit",
	2: "Luigi Outfit",
	3: "Super Mushroom Shirt",
	5: "Blockstripe Shirt",
	8: "Bowser Suit",
	12: "Builder Mario Outfit",
	13: "Princess Peach Dress",
	16: "Nintendo Uniform",
	17: "Fireworks Shirt",
	19: "Refreshing Shirt",
	21: "Reset Dress",
	22: "Thwomp Suit",
	23: "Slobbery Shirt",
	26: "Cat Suit",
	27: "Propeller Mario Clothes",
	28: "Banzai Bill Shirt",
	29: "Staredown Shirt",
	31: "Yoshi Suit",
	33: "Midnight Dress",
	34: "Magikoopa Robes",
	35: "Doctor Coat",
	37: "Chomp-Dog Shirt",
	38: "Fish Bone Shirt",
	40: "Toad Outfit",
	41: "Googoo Onesie",
	42: "Matrimony Dress",
	43: "Fancy Tuxedo",
	44: "Koopa Troopa Suit",
	45: "Laughing Shirt",
	46: "Running Shirt",
	47: "Rosalina Dress",
	49: "Angry Sun Shirt",
	50: "Fried-Chicken Hoodie",
	51: "? Block Hoodie",
	52: "Edamame Camisole",
	53: "I-Like-You Camisole",
	54: "White Tanktop",
	55: "Hot Hot Shirt",
	56: "Royal Attire",
	57: "Superball Mario Suit",
	59: "Partrick Shirt",
	60: "Robot Suit",
	61: "Superb Suit",
	62: "Yamamura Shirt",
	63: "Princess Peach Tennis Outfit",
	64: "1-Up Hoodie",
	65: "Cheetah Tanktop",
	66: "Cheetah Suit",
	67: "Ninji Shirt",
	68: "Ninji Garb",
	69: "Dash Block Hoodie",
	70: "Fire Mario Shirt",
	71: "Raccoon Mario Shirt",
	72: "Cape Mario Shirt",
	73: "Flying Squirrel Mario Shirt",
	74: "Cat Mario Shirt",
	75: "World Wear",
	76: "Koopaling Hawaiian Shirt",
	77: "Frog Mario Raincoat",
	78: "Phanto Hoodie"
}

UserPants = {
	0: "Black Short-Shorts",
	1: "Denim Jeans",
	5: "Denim Skirt",
	8: "Pipe Skirt",
	9: "Skull Skirt",
	10: "Burner Skirt",
	11: "Cloudwalker",
	12: "Platform Skirt",
	13: "Parent-and-Child Skirt",
	17: "Mario Swim Trunks",
	22: "Wind-Up Shoe",
	23: "Hoverclown",
	24: "Big-Spender Shorts",
	25: "Shorts of Doom!",
	26: "Doorduroys",
	27: "Antsy Corduroys",
	28: "Bouncy Skirt",
	29: "Stingby Skirt",
	31: "Super Star Flares",
	32: "Cheetah Runners",
	33: "Ninji Slacks"
}

UserIsOutfit = {
	0: False,
	1: True,
	2: True,
	3: False,
	5: False,
	8: True,
	12: True,
	13: True,
	16: False,
	17: False,
	19: False,
	21: True,
	22: True,
	23: False,
	26: True,
	27: True,
	28: False,
	29: False,
	31: True,
	33: True,
	34: True,
	35: True,
	37: False,
	38: False,
	40: True,
	41: True,
	42: True,
	43: True,
	44: True,
	45: False,
	46: False,
	47: True,
	49: False,
	50: False,
	51: False,
	52: False,
	53: False,
	54: False,
	55: False,
	56: True,
	57: True,
	59: False,
	60: True,
	61: True,
	62: False,
	63: True,
	64: False,
	65: False,
	66: True,
	67: False,
	68: True,
	69: False,
	70: False,
	71: False,
	72: False,
	73: False,
	74: False,
	75: True,
	76: False,
	77: True,
	78: False
}

SuperWorldPlanetType = {
	0: "Earth",
	1: "Moon",
	2: "Sand",
	3: "Green",
	4: "Ice",
	5: "Ringed",
	6: "Red",
	7: "Spiral"
}

class CourseRequestType(IntEnum):
	course_id = 1
	courses_endless_mode = 2
	courses_latest = 3
	courses_point_ranking = 4
	data_ids = 5
	data_ids_no_stop = 6
	search = 7
	posted = 8
	liked = 9
	played = 10
	first_cleared = 11
	world_record = 12

class ServerDataTypes(IntEnum):
	level_thumbnail = 2
	entire_level_thumbnail = 3
	custom_comment_image = 10
	ninji_ghost_replay = 40
	world_map_thumbnails = 50

class ServerDataTypeHeader:
	headers = None
	last_updated = 0
	expiration = 0
	data_type = 0
	def __init__(self, type):
		self.data_type = type
	async def refresh(self, store):
		headers_info = await store.get_req_get_info_headers_info(self.data_type)
		self.headers = {h.key: h.value for h in headers_info.headers}
		self.expiration = headers_info.expiration * 1000
		self.last_updated = milliseconds_since_epoch()
	async def refresh_if_needed(self, store):
		if (milliseconds_since_epoch() - self.last_updated) > (self.expiration - 1000):
			await self.refresh(store)
	async def request_url(self, url, store):
		if (milliseconds_since_epoch() - self.last_updated) > (self.expiration - 1000):
			if store == None:
				return False
			else:
				await self.refresh(store)
		response = await http.get(url, headers=self.headers)
		response.raise_if_error()
		return response.body

class ServerHeaders:
	level_thumbnail = ServerDataTypeHeader(ServerDataTypes.level_thumbnail)
	entire_level_thumbnail = ServerDataTypeHeader(ServerDataTypes.entire_level_thumbnail)
	custom_comment_image = ServerDataTypeHeader(ServerDataTypes.custom_comment_image)
	ninji_ghost_replay = ServerDataTypeHeader(ServerDataTypes.ninji_ghost_replay)
	world_map_thumbnails = ServerDataTypeHeader(ServerDataTypes.world_map_thumbnails)

async def download_thumbnail(store, url, filename, data_type, save = True):
	if data_type == ServerDataTypes.level_thumbnail:
		body = await ServerHeaders.level_thumbnail.request_url(url, store)
		if body == False:
			return False
		else:
			image = Image.open(io.BytesIO(body))
			if save:
				image.save(filename, optimize=True, quality=95)
				return True
			else:
				image_bytes = io.BytesIO()
				image.save(image_bytes, optimize=True, quality=95, format="jpeg")
				return image_bytes.getvalue()

	if data_type == ServerDataTypes.entire_level_thumbnail:
		body = await ServerHeaders.entire_level_thumbnail.request_url(url, store)
		if body == False:
			return False
		else:
			image = Image.open(io.BytesIO(body))
			if save:
				image.save(filename, optimize=True, quality=95)
				return True
			else:
				image_bytes = io.BytesIO()
				image.save(image_bytes, optimize=True, quality=95, format="jpeg")
				return image_bytes.getvalue()

def format_time(milliseconds):
	seconds = (milliseconds // 1000) % 60
	minutes = (milliseconds // 1000) // 60
	milliseconds = milliseconds % 1000
	return "%02i:%02i.%03i" % (minutes, seconds, milliseconds)

def in_cache(course_id):
	level_info_path = pathlib.Path("cache/level_info/%s" % course_id)
	return level_info_path.exists()

def in_user_cache(maker_id):
	user_info_path = pathlib.Path("cache/user_info/%s" % maker_id)
	return user_info_path.exists()

def ninji_ghosts_in_cache(ninji_data_id, time, num, include_replay_files):
	ninji_ghosts_path = pathlib.Path("cache/ninji_ghosts/%s_%s_%s_%i" % (str(ninji_data_id), str(time), num, include_replay_files))
	return ninji_ghosts_path.exists()

def ninji_ghost_replay_in_cache(replay_id):
	ninji_ghost_replay_path = pathlib.Path("cache/ninji_ghost_replays/%s.replay" % replay_id)
	return ninji_ghost_replay_path.exists()

def invalid_level(course_info):
	if "name" in course_info or "courses" in course_info or "comments" in course_info or "players" in course_info or "deaths" in course_info or "super_worlds" in course_info:
		return False
	else:
		return True

def invalid_ninji_ghosts(ghosts_info):
	if "ghosts" in ghosts_info:
		return False
	else:
		return True

def correct_course_id(course_id):
	return course_id.translate({ord('-'): None, ord(' '): None}).upper()

def invalid_course_id_length(course_id):
	if len(course_id) != 9:
		return True
	charset = "0123456789BCDFGHJKLMNPQRSTVWXY"
	for char in course_id:
		if not char in charset:
			return True
	return False

def difficulty_string_to_num(difficulty):
	if difficulty == "e":
		return 0
	if difficulty == "n":
		return 1
	if difficulty == "ex":
		return 2
	if difficulty == "sex":
		return 3
	return -1

def region_string_to_list(regions):
	regions_list = []
	if "j" in regions:
		regions_list.append(0)
	if "u" in regions:
		regions_list.append(1)
	if "e" in regions:
		regions_list.append(2)
	if "a" in regions:
		regions_list.append(3)
	return regions_list

def course_id_to_dataid(id):
	# https://github.com/kinnay/NintendoClients/wiki/Data-Store-Codes#super-mario-maker-2
	course_id = id[::-1]
	charset = "0123456789BCDFGHJKLMNPQRSTVWXY"
	number = 0
	for char in course_id:
		number = number * 30 + charset.index(char)
	left_side = number
	left_side = left_side << 34
	left_side_replace_mask = 0b1111111111110000000000000000000000000000000000
	number = number ^ ((number ^ left_side) & left_side_replace_mask)
	number = number >> 14
	number = number ^ 0b00010110100000001110000001111100
	return number

def is_maker_id(id):
	# https://github.com/kinnay/NintendoClients/wiki/Data-Store-Codes#super-mario-maker-2
	course_id = id[::-1]
	charset = "0123456789BCDFGHJKLMNPQRSTVWXY"
	number = 0
	for char in course_id:
		number = number * 30 + charset.index(char)
	if number & 8192:
		return True
	return False

def get_mii_data(data):
	# Based on https://github.com/HEYimHeroic/mii2studio/blob/master/mii2studio.py
	user_mii = Gen3Switchgame.from_bytes(data)
	mii_values = [
		user_mii.facial_hair_color,
		user_mii.facial_hair_beard,
		user_mii.body_weight,
		user_mii.eye_stretch,
		user_mii.eye_color,
		user_mii.eye_rotation,
		user_mii.eye_size,
		user_mii.eye_type,
		user_mii.eye_horizontal,
		user_mii.eye_vertical,
		user_mii.eyebrow_stretch,
		user_mii.eyebrow_color,
		user_mii.eyebrow_rotation,
		user_mii.eyebrow_size,
		user_mii.eyebrow_type,
		user_mii.eyebrow_horizontal,
		user_mii.eyebrow_vertical,
		user_mii.face_color,
		user_mii.face_makeup,
		user_mii.face_type,
		user_mii.face_wrinkles,
		user_mii.favorite_color,
		user_mii.gender,
		user_mii.glasses_color,
		user_mii.glasses_size,
		user_mii.glasses_type,
		user_mii.glasses_vertical,
		user_mii.hair_color,
		user_mii.hair_flip,
		user_mii.hair_type,
		user_mii.body_height,
		user_mii.mole_size,
		user_mii.mole_enable,
		user_mii.mole_horizontal,
		user_mii.mole_vertical,
		user_mii.mouth_stretch,
		user_mii.mouth_color,
		user_mii.mouth_size,
		user_mii.mouth_type,
		user_mii.mouth_vertical,
		user_mii.facial_hair_size,
		user_mii.facial_hair_mustache,
		user_mii.facial_hair_vertical,
		user_mii.nose_size,
		user_mii.nose_type,
		user_mii.nose_vertical
	]

	mii_data = b"00"
	mii_bytes = ""
	n = 256
	for v in mii_values:
		n = (7 + (v ^ n)) % 256
		mii_data += hexlify(pack(">B", n))
		mii_bytes += hexlify(pack(">B", v)).decode("ascii")

	url = "https://studio.mii.nintendo.com/miis/image.png?data=" + mii_data.decode("utf-8")
	return [url + "&type=face&width=512&instanceCount=1", mii_bytes]

async def obtain_course_info(course_id, store, noCaching = False):
	param = datastore.GetUserOrCourseParam()
	param.code = course_id
	param.course_option = datastore.CourseOption.ALL

	# Download a specific course
	course_info_json = await get_course_info_json(CourseRequestType.course_id, param, store, noCaching)

	return course_info_json

async def obtain_user_info(maker_id, store, noCaching = False, save = True):
	param = datastore.GetUserOrCourseParam()
	param.code = maker_id
	param.user_option = datastore.UserOption.ALL

	loc = "cache/user_info/%s" % maker_id

	# Prepare directories
	os.makedirs(os.path.dirname(loc), exist_ok=True)

	user_info_path = pathlib.Path(loc)
	if user_info_path.exists() and not noCaching:
		with open(loc, mode="rb") as f:
			return orjson.loads(zlib.decompress(f.read()))
	else:
		if not is_maker_id(maker_id):
			with open(loc, mode="wb+") as f:
				f.write(zlib.compress(('{"error": "Code corresponds to a level", "maker_id": "%s"}' % maker_id).encode("UTF8")))
				return {"error": "Code corresponds to a level", "maker_id": maker_id}
		else:
			try:
				response = await store.get_user_or_course(param)
			except:
				# Save (the empty) level info to json
				print("maker_id " + maker_id + " is invalid")
				with open(loc, mode="wb+") as f:
					f.write(zlib.compress(('{"error": "No user with that ID", "maker_id": "%s"}' % maker_id).encode("UTF8")))
					return {"error": "No user with that ID", "maker_id": maker_id}

		ret = {}
		add_user_info_json(response.user, ret)
		
		if save:
			with open(loc, mode="wb+") as f:
				f.write(zlib.compress(orjson.dumps(ret)))
				return ret

async def obtain_course_infos(course_ids, store):
	# Convert each course_id to a data_id
	data_ids = []
	for id in course_ids:
		data_ids.append(course_id_to_dataid(id))

	param = datastore.GetCoursesParam()
	param.data_ids = data_ids
	param.option = datastore.CourseOption.ALL

	courses_info_json = await get_course_info_json(CourseRequestType.data_ids, param, store)

	if invalid_level(courses_info_json):
		return {"error": "No course with that ID", "course_id": course_ids[data_ids.index(courses_info_json["data_id"])]}

	return courses_info_json

async def search_endless_courses(count, difficulty, store):
	param = datastore.SearchCoursesEndlessModeParam()
	param.count = count
	param.difficulty = difficulty
	param.option = datastore.CourseOption.ALL

	courses_info_json = await get_course_info_json(CourseRequestType.courses_endless_mode, param, store)

	return courses_info_json

async def search_latest_courses(size, store):
	param = datastore.SearchCoursesLatestParam()
	param.range.offset = 0
	param.range.size = size
	param.option = datastore.CourseOption.ALL

	courses_info_json = await get_course_info_json(CourseRequestType.courses_latest, param, store)

	return courses_info_json

async def search_courses_point_ranking(size, difficulty, rejectRegions, store):
	param = datastore.SearchCoursesPointRankingParam()
	param.range.offset = 0
	param.range.size = size
	param.difficulty = difficulty
	param.reject_regions = rejectRegions
	param.option = datastore.CourseOption.ALL

	courses_info_json = await get_course_info_json(CourseRequestType.courses_point_ranking, param, store)

	return courses_info_json

async def get_courses_data_id(data_ids, store):
	param = datastore.GetCoursesParam()
	param.data_ids = data_ids
	param.option = datastore.CourseOption.ALL

	courses_info_json = await get_course_info_json(CourseRequestType.data_ids, param, store)

	return courses_info_json

async def get_courses_posted(size, pid, store):
	param = datastore.SearchCoursesPostedByParam()
	param.range.offset = 0
	param.range.size = size
	param.pids = [pid]
	param.option = datastore.CourseOption.ALL

	courses_info_json = await get_course_info_json(CourseRequestType.posted, param, store)

	return courses_info_json

async def get_courses_liked(size, pid, store):
	param = datastore.SearchCoursesPositiveRatedByParam()
	param.count = size
	param.pid = pid
	param.option = datastore.CourseOption.ALL

	courses_info_json = await get_course_info_json(CourseRequestType.liked, param, store)

	return courses_info_json

async def get_courses_played(size, pid, store):
	param = datastore.SearchCoursesPlayedByParam()
	param.count = size
	param.pid = pid
	param.option = datastore.CourseOption.ALL

	courses_info_json = await get_course_info_json(CourseRequestType.played, param, store)

	return courses_info_json

async def get_courses_first_cleared(size, pid, store):
	param = datastore.SearchCoursesFirstClearParam()
	param.range.offset = 0
	param.range.size = size
	param.pid = pid
	param.option = datastore.CourseOption.ALL

	courses_info_json = await get_course_info_json(CourseRequestType.first_cleared, param, store)

	return courses_info_json

async def get_courses_world_record(size, pid, store):
	param = datastore.SearchCoursesBestTimeParam()
	param.range.offset = 0
	param.range.size = size
	param.pid = pid
	param.option = datastore.CourseOption.ALL

	courses_info_json = await get_course_info_json(CourseRequestType.world_record, param, store)

	return courses_info_json

def add_user_info_json(user, json_dict):
	json_dict["region"] = user.region
	json_dict["region_name"] = Regions[user.region]
	json_dict["code"] = user.code
	json_dict["pid"] = user.pid
	json_dict["name"] = user.name
	json_dict["country"] = user.country
	json_dict["last_active"] = user.last_active.timestamp()
	json_dict["last_active_pretty"] = str(user.last_active)

	if len(user.unk2) != 0:
		mii_info = get_mii_data(user.unk2)
		if debug_enabled:
			json_dict["mii_data"] = user.unk2
		else:
			json_dict["mii_data"] = base64.b64encode(user.unk2).decode("ascii")
		json_dict["mii_image"] = mii_info[0]
		json_dict["mii_studio_code"] = mii_info[1]

	wearing_outfit = UserIsOutfit[user.unk1.unk3]
	json_dict["pose"] = user.unk1.unk1
	json_dict["hat"] = user.unk1.unk2
	json_dict["shirt"] = user.unk1.unk3
	json_dict["pants"] = user.unk1.unk4

	json_dict["pose_name"] = UserPose[user.unk1.unk1]
	json_dict["hat_name"] = UserHat[user.unk1.unk2]
	json_dict["shirt_name"] = UserShirt[user.unk1.unk3]
	if user.unk1.unk4 == 0 and wearing_outfit:
		json_dict["pants_name"] = "None"
	else:
		json_dict["pants_name"] = UserPants[user.unk1.unk4]
	json_dict["wearing_outfit"] = wearing_outfit

	if len(user.play_stats) == 4:
		json_dict["courses_played"] = user.play_stats[0]
		json_dict["courses_cleared"] = user.play_stats[2]
		json_dict["courses_attempted"] = user.play_stats[1]
		json_dict["courses_deaths"] = user.play_stats[3]

	if len(user.maker_stats) == 2:
		json_dict["likes"] = user.maker_stats[0]
		json_dict["maker_points"] = user.maker_stats[1]

	if len(user.endless_challenge_high_scores) == 4:
		json_dict["easy_highscore"] = user.endless_challenge_high_scores[0]
		json_dict["normal_highscore"] = user.endless_challenge_high_scores[1]
		json_dict["expert_highscore"] = user.endless_challenge_high_scores[2]
		json_dict["super_expert_highscore"] = user.endless_challenge_high_scores[3]

	if len(user.multiplayer_stats) == 15:
		json_dict["versus_rating"] = user.multiplayer_stats[0]
		json_dict["versus_rank"] = user.multiplayer_stats[1]
		json_dict["versus_rank_name"] = MultiplayerVersusRanks[user.multiplayer_stats[1]]
		json_dict["versus_won"] = user.multiplayer_stats[3]
		json_dict["versus_lost"] = user.multiplayer_stats[4]
		json_dict["versus_win_streak"] = user.multiplayer_stats[5]
		json_dict["versus_lose_streak"] = user.multiplayer_stats[6]
		json_dict["versus_plays"] = user.multiplayer_stats[2]
		json_dict["versus_disconnected"] = user.multiplayer_stats[7]
		json_dict["coop_clears"] = user.multiplayer_stats[11]
		json_dict["coop_plays"] = user.multiplayer_stats[10]
		json_dict["recent_performance"] = user.multiplayer_stats[12]
		json_dict["versus_kills"] = user.multiplayer_stats[8]
		json_dict["versus_killed_by_others"] = user.multiplayer_stats[9]
		json_dict["multiplayer_stats_unk13"] = user.multiplayer_stats[13]
		json_dict["multiplayer_stats_unk14"] = user.multiplayer_stats[14]

	if len(user.unk8) == 2:
		json_dict["first_clears"] = user.unk8[0]
		json_dict["world_records"] = user.unk8[1]

	if len(user.unk15) == 1:
		json_dict["unique_super_world_clears"] = user.unk15[0]

	if len(user.unk9) == 2:
		json_dict["uploaded_levels"] = user.unk9[0]
		json_dict["maximum_uploaded_levels"] = user.unk9[1]

	if len(user.unk7) == 1:
		json_dict["weekly_maker_points"] = user.unk7[0]

	json_dict["last_uploaded_level"] = user.unk11.timestamp()
	json_dict["last_uploaded_level_pretty"] = str(user.unk11)
	json_dict["is_nintendo_employee"] = user.unk10
	json_dict["comments_enabled"] = user.unk4
	json_dict["tags_enabled"] = user.unk5
	json_dict["super_world_id"] = user.unk14
	json_dict["badges"] = []

	for badge in user.badges:
		badge_info = {}
		badge_info["type"] = badge.unk1
		badge_info["rank"] = badge.unk2
		badge_info["type_name"] = BadgeTypes[badge.unk1]
		badge_info["rank_name"] = BadgeRanks[badge.unk2]
		json_dict["badges"].append(badge_info)

	json_dict["unk3"] = user.unk3
	json_dict["unk12"] = user.unk12
	json_dict["unk16"] = user.unk16

async def add_comment_info_json(store, course_id, course_info, noCaching = False, save = True):
	loc = "cache/level_comments/%s" % course_id
	comments_arr = []

	if pathlib.Path(loc).exists() and not noCaching:
		with open(loc, mode="rb") as f:
			return orjson.loads(zlib.decompress(f.read()))

	if debug_enabled or course_info["uploader"]["comments_enabled"]:
		user_pids = []
		data_id = course_id_to_dataid(course_id)
		if course_info["num_comments"] < 100:
			comments = await store.search_comments(data_id)
		else:
			# Only 1000 comments are ever available, Nintendo appears to delete them automatically
			param = datastore.SearchCommentsInOrderParam()
			param.range.offset = 0
			param.range.size = 1000
			param.data_id = data_id
			comments = (await store.search_comments_in_order(param)).comments

		for comment in comments:
			if comment.unk5 != 0:
				comment_json = {}
				# Corresponds to course data id, redundant
				#comment_json["unk1"] = comment.unk1
				comment_json["comment_id"] = comment.unk2
				if comment.unk4 == 1:
					comment_json["text"] = comment.unk15
				comment_json["posted_pretty"] = str(comment.unk13)
				comment_json["posted"] = comment.unk13.timestamp()
				comment_json["clear_required"] = comment.unk11
				if comment.unk4 == 2:
					comment_json["reaction_image_id"] = comment.unk16
					comment_json["reaction_image_id_name"] = CommentReactionImage[comment.unk16]
				comment_json["type_name"] = CommentType[comment.unk4]
				comment_json["type"] = comment.unk4
				comment_json["has_beaten"] = bool(comment.unk3)
				comment_json["x"] = comment.unk6
				comment_json["y"] = comment.unk7
				comment_json["reaction_face"] = comment.unk9
				comment_json["reaction_face_name"] = CommentReactionFace[comment.unk9]
				comment_json["unk8"] = comment.unk8 # Usually 0
				comment_json["unk10"] = comment.unk10 # Usually 0
				comment_json["unk12"] = comment.unk12 # Usually false
				if not debug_enabled:
					comment_json["unk14"] = base64.b64encode(comment.unk14).decode("ascii") # Usually nothing
				else:
					comment_json["unk14"] = comment.unk14
				comment_json["unk17"] = comment.unk17 # Usually 0

				if comment.unk4 == 0:
					comment_image = {}
					comment_image["url"] = comment.picture.url
					comment_image["size"] = comment.picture.unk1
					comment_image["filename"] = comment.picture.filename
					comment_json["custom_comment_image"] = comment_image

					# How to extract image
					# response = await http.get(comment.picture.url, headers=custom_comment_image_headers)
					# img = Image.frombuffer("RGBA", (320, 180), zlib.decompress(response.body), "raw", "RGBA", 0, 1)
					# img.save(comment.picture.filename + ".png")

				comments_arr.append(comment_json)
				user_pids.append(comment.unk5)

		if len(user_pids) != 0:
			i = 0
			for users_partial in [user_pids[j:j+500] for j in range(len(user_pids))[::500]]:
				if not debug_enabled:
					param = datastore.GetUsersParam()
					param.pids = users_partial
					param.option = datastore.UserOption.ALL
					response = await store.get_users(param)
					for user in response.users:
						if user_pids[i] != 0:
							comments_arr[i]["poster"] = {}
							add_user_info_json(user, comments_arr[i]["poster"])
						i += 1
				else:
					for user_pid in users_partial:
						comments_arr[i]["commenter_pid"] = user_pid
						i += 1

		comments = {}
		comments["comments"] = comments_arr
	else:
		comments = {"error": "Uploader has disabled comments on their levels", "course_id": course_id}

	if save:
		os.makedirs("cache/level_comments", exist_ok=True)
		with open(loc, mode="wb+") as f:
			f.write(zlib.compress(orjson.dumps(comments)))
	return comments

async def get_world_maps_json(store):
	world_map_arr = []
	user_pids = []

	param = datastore.SearchWorldMapPickUpParam()
	param.count = 50
	response = await store.search_world_map_pick_up(param)

	for map in response:
		map_json = {}
		map_json["id"] = map.id
		map_json["worlds"] = map.worlds
		map_json["levels"] = map.levels
		map_json["planet_type"] = map.unk2
		map_json["planet_type_name"] = SuperWorldPlanetType[map.unk2]
		map_json["created_pretty"] = str(map.unk3)
		map_json["created"] = map.unk3.timestamp()

		map_json["unk5"] = map.unk5
		map_json["unk6"] = map.unk6
		map_json["unk7"] = map.unk7

		thumbnail = {}
		thumbnail["url"] = map.thumbnail.url
		thumbnail["size"] = map.thumbnail.size
		thumbnail["filename"] = map.thumbnail.filename
		map_json["thumbnail"] = thumbnail

		world_map_arr.append(map_json)
		user_pids.append(map.owner_id)

	if len(user_pids) != 0:
		i = 0
		param = datastore.GetUsersParam()
		param.pids = user_pids
		param.option = datastore.UserOption.ALL
		response = await store.get_users(param)
		for user in response.users:
			if user_pids[i] != 0:
				world_map_arr[i]["uploader"] = {}
				add_user_info_json(user, world_map_arr[i]["uploader"])

			i += 1

	world_maps = {}
	world_maps["super_worlds"] = world_map_arr
	return world_maps

async def search_world_map(store, ids, noCaching = False, save = True):
	world_map_arr = []

	if len(ids) == 1 and pathlib.Path("cache/super_worlds/%s" % ids[0]).exists() and not noCaching:
		with open("cache/super_worlds/%s" % ids[0], mode="rb") as f:
			return orjson.loads(zlib.decompress(f.read()))

	param = datastore.GetWorldMapParam()
	param.ids = ids
	param.option = 63
	response = await store.get_world_map(param)

	i = 0
	for map in response.maps:
		if map.owner_id == 0:
			if not debug_enabled:
				return {"error": "No super world with that id", "id": ids[i]}
			else:
				continue

		map_json = {}
		map_json["id"] = map.id
		map_json["worlds"] = map.worlds
		map_json["levels"] = map.levels
		map_json["planet_type"] = map.unk2
		map_json["planet_type_name"] = SuperWorldPlanetType[map.unk2]
		map_json["created_pretty"] = str(map.unk3)
		map_json["created"] = map.unk3.timestamp()

		map_json["ninjis"] = []
		for element in map.unk4:
			map_json["ninjis"].append(map.unk4[element])

		if debug_enabled and not save:
			map_json["unk1"] = map.unk1
		map_json["unk5"] = map.unk5
		map_json["unk6"] = map.unk6
		map_json["unk7"] = map.unk7

		thumbnail = {}
		thumbnail["url"] = map.thumbnail.url
		thumbnail["size"] = map.thumbnail.size
		thumbnail["filename"] = map.thumbnail.filename
		map_json["thumbnail"] = thumbnail

		if not debug_enabled:
			map_json["courses"] = (await get_courses_data_id(map.data_ids, store))["courses"]
			map_json["uploader"] = map_json["courses"][0]["uploader"]
		else:
			map_json["courses"] = map.data_ids

		world_map_arr.append(map_json)
		i += 1

	if save:
		os.makedirs("cache/super_worlds", exist_ok=True)
		for map in world_map_arr:
			with open("cache/super_worlds/%s" % map["id"], mode="wb+") as f:
				f.write(zlib.compress(orjson.dumps(map)))

	if len(world_map_arr) == 1 and not debug_enabled:
		return world_map_arr[0]
	else:
		world_map_json = {}
		world_map_json["super_worlds"] = world_map_arr
		return world_map_json

async def add_played_info_json(store, course_id, noCaching = False, save = True):
	loc = "cache/level_played/%s" % course_id
	played_info = {}
	played_info["players"] = []

	if pathlib.Path(loc).exists() and not noCaching:
		with open(loc, mode="rb") as f:
			return orjson.loads(zlib.decompress(f.read()))

	data_id = course_id_to_dataid(course_id)

	param = datastore.SearchUsersPlayedCourseParam()
	param.data_id = data_id
	param.option = datastore.UserOption.ALL
	param.count = 1000
	players = await store.search_users_played_course(param)

	for player in players:
		player_json = {}
		add_user_info_json(player, player_json)
		played_info["players"].append(player_json)

	if len(players) != 0:
		param = datastore.SearchUsersClearedCourseParam()
		param.data_id = data_id
		param.count = 1000
		clearing_players = await store.search_users_cleared_course(param)
		played_info["cleared"] = [user.pid for user in clearing_players]

		param = datastore.SearchUsersPositiveRatedCourseParam()
		param.data_id = data_id
		param.count = 1000
		liking_players = await store.search_users_positive_rated_course(param)
		played_info["liked"] = [user.pid for user in liking_players]

	if save:
		os.makedirs("cache/level_played", exist_ok=True)
		with open(loc, mode="wb+") as f:
			f.write(zlib.compress(orjson.dumps(played_info)))
	return played_info

async def add_death_positions_json(store, course_id, noCaching = False, save = True):
	loc = "cache/level_deaths/%s" % course_id
	deaths_arr = []

	if pathlib.Path(loc).exists() and not noCaching:
		with open(loc, mode="rb") as f:
			return orjson.loads(zlib.decompress(f.read()))

	deaths = await store.get_death_positions(course_id_to_dataid(course_id))

	for death in deaths:
		death_json = {}
		death_json["x"] = death.x
		death_json["y"] = death.y
		death_json["is_subworld"] = death.is_subworld
		deaths_arr.append(death_json)

	deaths = {}
	deaths["deaths"] = deaths_arr

	if save:
		os.makedirs("cache/level_deaths", exist_ok=True)
		with open(loc, mode="wb+") as f:
			f.write(zlib.compress(orjson.dumps(deaths)))
	return deaths

#async def search_courses(data_ids, store):
#	param = datastore.DataStoreSearchParam()
#	param.data_ids = data_ids
#	param.option = datastore.CourseOption.ALL
#
#	courses_info_json = await get_course_info_json(CourseRequestType.data_ids, param, store)
#
#	return courses_info_json

async def get_course_info_json(request_type, request_param, store, noCaching = False, save = True):
	courses = []
	from_cache = []
	stop_on_bad = True

	if request_type == CourseRequestType.course_id:
		loc = "cache/level_info/%s" % request_param.code

		# Prepare directories
		os.makedirs(os.path.dirname(loc), exist_ok=True)

		level_info_path = pathlib.Path(loc)
		if level_info_path.exists() and not noCaching:
			with open(loc, mode="rb") as f:
				courses.append(orjson.loads(zlib.decompress(f.read())))
				from_cache.append(True)
		else:
			if invalid_course_id_length(request_param.code):
				# Save (the empty) level info to json
				print("course_id " + request_param.code + " is wrong length")
				with open(loc, mode="wb+") as f:
					f.write(zlib.compress(('{"error": "Invalid course ID", "course_id": "%s"}' % request_param.code).encode("UTF8")))
					return {"error": "Invalid course ID", "course_id": request_param.code}

			if is_maker_id(request_param.code):
				print("course_id " + request_param.code + " is actually maker_id")
				with open(loc, mode="wb+") as f:
					f.write(zlib.compress(('{"error": "Code corresponds to a maker", "course_id": "%s"}' % request_param.code).encode("UTF8")))
					return {"error": "Code corresponds to a maker", "course_id": request_param.code}

			try:
				response = await store.get_user_or_course(request_param)
				if response.user.pid != 0:
					print("course_id " + request_param.code + " is invalid")
					with open(loc, mode="wb+") as f:
						f.write(zlib.compress(('{"error": "No course with that ID", "course_id": "%s"}' % request_param.code).encode("UTF8")))
						return {"error": "No course with that ID", "course_id": request_param.code}
			except:
				# Save (the empty) level info to json
				print("course_id " + request_param.code + " is invalid")
				with open(loc, mode="wb+") as f:
					f.write(zlib.compress(('{"error": "No course with that ID", "course_id": "%s"}' % request_param.code).encode("UTF8")))
					return {"error": "No course with that ID", "course_id": request_param.code}

			courses.append(response.course)
			from_cache.append(False)

	if request_type == CourseRequestType.courses_endless_mode:
		courses = await store.search_courses_endless_mode(request_param)
		from_cache = [None] * len(courses)

	if request_type == CourseRequestType.courses_latest:
		response = await store.search_courses_latest(request_param)
		courses = response.courses
		from_cache = [None] * len(courses)

	if request_type == CourseRequestType.courses_point_ranking:
		response = await store.search_courses_point_ranking(request_param)
		courses = response.courses
		from_cache = [None] * len(courses)

	if request_type == CourseRequestType.data_ids:
		response = await store.get_courses(request_param)
		courses = response.courses
		from_cache = [None] * len(courses)

	if request_type == CourseRequestType.data_ids_no_stop:
		response = await store.get_courses(request_param)
		courses = response.courses
		stop_on_bad = False
		from_cache = [None] * len(courses)

	if request_type == CourseRequestType.posted:
		response = await store.search_courses_posted_by(request_param)
		courses = response.courses
		from_cache = [None] * len(courses)

	if request_type == CourseRequestType.liked:
		courses = await store.search_courses_positive_rated_by(request_param)
		from_cache = [None] * len(courses)

	if request_type == CourseRequestType.played:
		courses = await store.search_courses_played_by(request_param)
		from_cache = [None] * len(courses)

	if request_type == CourseRequestType.first_cleared:
		response = await store.search_courses_first_clear(request_param)
		courses = response.courses
		from_cache = [None] * len(courses)

	if request_type == CourseRequestType.world_record:
		response = await store.search_courses_best_time(request_param)
		courses = response.courses
		from_cache = [None] * len(courses)

	uploader_pids = []
	first_clear_pids = []
	record_holder_pids = []

	course_info_json = {}
	course_info_json["courses"] = [None] * len(courses)

	i = 0;
	cache_hits = 0
	for course in courses:
		course_info = {}

		if from_cache[i]:
			course_info = course
			cache_hits += 1

			uploader_pids.append(0)
			first_clear_pids.append(0)
			record_holder_pids.append(0)
		else:
			if course.owner_id == 0:
				if stop_on_bad:
					# Invalid data id
					if request_type == CourseRequestType.data_ids:
						return {"error": "No course with that data id", "data_id": request_param.data_ids[i]}
				else:
					continue

			course_info["name"] = course.name
			course_info["description"] = course.description
			course_info["uploaded_pretty"] = str(course.upload_time)
			course_info["uploaded"] = course.upload_time.timestamp()
			course_info["data_id"] = course.data_id
			course_info["course_id"] = course.code
			course_info["game_style_name"] = GameStyles[course.game_style]
			course_info["game_style"] = course.game_style
			course_info["theme_name"] = CourseThemes[course.course_theme]
			course_info["theme"] = course.course_theme
			course_info["difficulty_name"] = Difficulties[course.difficulty]
			course_info["difficulty"] = course.difficulty
			course_info["tags_name"] = [TagNames[course.tag1], TagNames[course.tag2]]
			course_info["tags"] = [course.tag1, course.tag2]
			if course.time_stats.world_record != 4294967295:
				course_info["world_record_pretty"] = format_time(course.time_stats.world_record)
				course_info["world_record"] = course.time_stats.world_record
			course_info["upload_time_pretty"] = format_time(course.time_stats.upload_time)
			course_info["upload_time"] = course.time_stats.upload_time
			course_info["num_comments"] = course.comment_stats[0]
			course_info["clear_condition"] = course.clear_condition
			if course.clear_condition != 0:
				course_info["clear_condition_name"] = ClearConditions[course.clear_condition]
			course_info["clear_condition_magnitude"] = course.clear_condition_magnitude
			if len(course.play_stats) == 5:
				course_info["clears"] = course.play_stats[3]
				course_info["attempts"] = course.play_stats[1]
				if not debug_enabled:
					if course.play_stats[1] == 0:
						course_info["clear_rate"] = "0%"
					else:
						course_info["clear_rate"] = "%.2f%%" % ((course.play_stats[3] / course.play_stats[1]) * 100)
				else:
					if course.play_stats[1] == 0:
						course_info["clear_rate"] = 0
					else:
						course_info["clear_rate"] = (course.play_stats[3] / course.play_stats[1]) * 100
				course_info["plays"] = course.play_stats[0]
				course_info["versus_matches"] = course.play_stats[4]
				course_info["coop_matches"] = course.play_stats[2]
			if len(course.ratings) == 3:
				course_info["likes"] = course.ratings[0]
				course_info["boos"] = course.ratings[1]
				course_info["unique_players_and_versus"] = course.ratings[2]
			if len(course.unk4) == 2:
				course_info["weekly_likes"] = course.unk4[0]
				course_info["weekly_plays"] = course.unk4[1]

			one_screen_thumbnail = {}
			one_screen_thumbnail["url"] = course.one_screen_thumbnail.url
			one_screen_thumbnail["size"] = course.one_screen_thumbnail.size
			one_screen_thumbnail["filename"] = course.one_screen_thumbnail.filename
			course_info["one_screen_thumbnail"] = one_screen_thumbnail

			entire_thumbnail = {}
			entire_thumbnail["url"] = course.entire_thumbnail.url
			entire_thumbnail["size"] = course.entire_thumbnail.size
			entire_thumbnail["filename"] = course.entire_thumbnail.filename
			course_info["entire_thumbnail"] = entire_thumbnail

			course_info["unk2"] = course.unk2
			if debug_enabled and not save:
				course_info["unk3"] = course.unk3
			else:
				course_info["unk3"] = base64.b64encode(course.unk3).decode("ascii")
			course_info["unk9"] = course.unk9
			course_info["unk10"] = course.unk10
			course_info["unk11"] = course.unk11
			course_info["unk12"] = course.unk12

			if pathlib.Path("cache/level_info/%s" % course.code).exists():
				cache_hits += 1

			uploader_pids.append(course.owner_id)
			first_clear_pids.append(course.time_stats.first_completion)
			record_holder_pids.append(course.time_stats.world_record_holder)

		course_info_json["courses"][i] = course_info
		i += 1

	del course_info_json["courses"][i:]

	if store:
		all_pids = uploader_pids + first_clear_pids + record_holder_pids
		all_pids_split = [all_pids[i:i+500] for i in range(len(all_pids))[::500]]
		all_pids_result = []
		if not debug_enabled:
			for pids_chunk in all_pids_split:
				param = datastore.GetUsersParam()
				param.pids = pids_chunk
				param.option = datastore.UserOption.ALL

				all_pids_result += (await store.get_users(param)).users
		if len(uploader_pids) != 0:
			if not debug_enabled:
				i = 0
				for user in all_pids_result[:len(uploader_pids)]:
					if uploader_pids[i] != 0:
						course_info = course_info_json["courses"][i]
						course_info["uploader"] = {}
						add_user_info_json(user, course_info["uploader"])

					i += 1
			else:
				i = 0
				for user_pid in uploader_pids:
					if user_pid != 0:
						course_info_json["courses"][i]["uploader_pid"] = user_pid
					i += 1

		if len(first_clear_pids) != 0:
			if not debug_enabled:
				i = 0
				for user in all_pids_result[len(uploader_pids):len(uploader_pids)+len(first_clear_pids)]:
					if first_clear_pids[i] != 0:
						course_info = course_info_json["courses"][i]
						course_info["first_completer"] = {}
						add_user_info_json(user, course_info["first_completer"])

					i += 1
			else:
				i = 0
				for user_pid in first_clear_pids:
					if user_pid != 0:
						course_info_json["courses"][i]["first_completer_pid"] = user_pid
					i += 1

		if len(record_holder_pids) != 0:
			if not debug_enabled:
				i = 0
				for user in all_pids_result[len(uploader_pids)+len(first_clear_pids):]:
					if record_holder_pids[i] != 0:
						course_info = course_info_json["courses"][i]
						course_info["record_holder"] = {}
						add_user_info_json(user, course_info["record_holder"])

					i += 1
			else:
				i = 0
				for user_pid in record_holder_pids:
					if user_pid != 0:
						course_info_json["courses"][i]["record_holder_pid"] = user_pid
					i += 1

		if save:
			i = 0
			os.makedirs("cache/level_info", exist_ok=True)
			for course in course_info_json["courses"]:
				if not from_cache[i]:
					loc = "cache/level_info/%s" % course["course_id"]
					with open(loc, mode="wb+") as f:
						f.write(zlib.compress(orjson.dumps(course)))

				i += 1

	if request_type == CourseRequestType.course_id:
		return course_info_json["courses"][0]
	else:
		course_info_json["cache_hits"] = cache_hits
		return course_info_json

async def obtain_ninji_info(store):
	loc = "cache/level_info/ninji"

	level_info_path = pathlib.Path(loc)
	if level_info_path.exists():
		with open(loc, mode="rb") as f:
			return orjson.loads(zlib.decompress(f.read()))

	course_info_json = {}

	os.makedirs(os.path.dirname(loc), exist_ok=True)

	param = datastore.SearchCoursesEventParam()
	param.option = datastore.EventCourseOption.ALL
	courses = await store.search_courses_event(param)

	course_info_json["courses"] = [None] * len(courses)

	i = 0
	for course in courses:
		course_info_json["courses"][i] = {}
		course_info_json["courses"][i]["name"] = course.name
		course_info_json["courses"][i]["description"] = course.description
		course_info_json["courses"][i]["uploaded"] = str(course.upload_time)
		course_info_json["courses"][i]["game_style_name"] = GameStyles[course.game_style]
		course_info_json["courses"][i]["game_style"] = course.game_style
		course_info_json["courses"][i]["theme_name"] = CourseThemes[course.course_theme]
		course_info_json["courses"][i]["theme"] = course.course_theme
		course_info_json["courses"][i]["end_time"] = str(course.end_time)
		course_info_json["courses"][i]["data_id"] = course.data_id
		course_info_json["courses"][i]["clear_condition"] = course.unk7
		course_info_json["courses"][i]["clear_condition_magnitude"] = course.unk8
		course_info_json["courses"][i]["medal_time"] = course.medal_time
		course_info_json["courses"][i]["unk3_0"] = course.unk3[0]
		course_info_json["courses"][i]["unk3_1"] = course.unk3[1]
		course_info_json["courses"][i]["unk3_2"] = course.unk3[2]
		course_info_json["courses"][i]["unk5"] = course.unk5
		course_info_json["courses"][i]["unk6"] = course.unk6
		course_info_json["courses"][i]["unk9"] = course.unk9

		i = i + 1

	with open(loc, mode="wb+") as f:
		f.write(zlib.compress(orjson.dumps(course_info_json)))

	return course_info_json

async def obtain_ninji_ghosts(ninji_data_id, time, num, include_replay_files, should_cache, store):
	# If there is an answer within 1/100 of a second in the cache, return that
	loc = "cache/ninji_ghosts/%s_%s_%s_%i" % (str(ninji_data_id), str(time), num, include_replay_files)

	if should_cache:
		ninji_ghosts_path = pathlib.Path(loc)
		if ninji_ghosts_path.exists():
			with open(loc, mode="rb") as f:
				return orjson.loads(zlib.decompress(f.read()))

	# All Ninji info is in the same JSON
	ninji_ghosts_json = {}

	# Prepare directories
	os.makedirs(os.path.dirname(loc), exist_ok=True)

	if time > 199999 or time < 0:
		with open(loc, mode="wb+") as f:
			f.write(zlib.compress('{"error": "Time must be between 0 and 199999"}'.encode("UTF8")))
			return {"error": "Time must be between 0 and 199999"}

	if num > 100 or num < 2:
		with open(loc, mode="wb+") as f:
			f.write(zlib.compress('{"error": "Number of ninjis must be between 2 and 100"}'.encode("UTF8")))
			return {"error": "Number of ninjis must be between 2 and 100"}

	if include_replay_files and num > 3:
		with open(loc, mode="wb+") as f:
			f.write(zlib.compress('{"error": "You can only request up to 3 ninjis if you include replay files"}'.encode("UTF8")))
			return {"error": "You can only request up to 3 ninjis if you include replay files"}

	param = datastore.GetEventCourseGhostParam()
	param.data_id = ninji_data_id
	param.time = time
	param.count = num
	ghosts = await store.get_event_course_ghost(param)

	ninji_ghosts_json["ghosts"] = [None] * len(ghosts)
	user_pids = []

	i = 0
	for ghost in ghosts:
		ninji_ghosts_json["ghosts"][i] = {}
		ninji_ghosts_json["ghosts"][i]["time"] = ghost.time
		
		replay_file = {}
		replay_file["url"] = ghost.replay_file.url
		replay_file["size"] = ghost.replay_file.size
		replay_file["filename"] = ghost.replay_file.filename

		ninji_ghosts_json["ghosts"][i]["replay_file"] = replay_file

		if include_replay_files:
			ninji_ghosts_json["ghosts"][i]["replay_id"] = ghost.replay_file.filename

			replay_loc = "cache/ninji_ghost_replays/%s.replay" % ghost.replay_file.filename
			if not pathlib.Path(replay_loc).exists():
				os.makedirs(os.path.dirname(replay_loc), exist_ok=True)
				body = await ServerHeaders.ninji_ghost_replay.request_url(ghost.replay_file.url, store)

				with open(replay_loc, "wb") as f:
					f.write(body)

		user_pids.append(ghost.pid)
		i = i + 1

	param = datastore.GetUsersParam()
	param.pids = user_pids
	param.option = datastore.UserOption.ALL

	response = await store.get_users(param)
	users = response.users

	i = 0
	for user in users:
		add_user_info_json(user, ninji_ghosts_json["ghosts"][i])
		i = i + 1

	with open(loc, mode="wb+") as f:
		f.write(zlib.compress(orjson.dumps(ninji_ghosts_json)))

	return ninji_ghosts_json


HOST = "g%08x-lp1.s.n.srv.nintendo.net" % SMM2.GAME_SERVER_ID
PORT = 443
s = None
user_id = None
auth_info = None
device_token_generated_time = None
id_token_generated_time = None
device_token = None
app_token = None
access_token = None
id_token = None
getting_credentials = asyncio.Lock()

def milliseconds_since_epoch():
	return time.time_ns() // 1000000

async def check_tokens():
	global HOST
	global PORT
	global s
	global user_id
	global auth_info
	global device_token_generated_time
	global id_token_generated_time
	global device_token
	global app_token
	global access_token
	global id_token
	global getting_credentials
	if getting_credentials.locked():
		# Another thread is busy refreshing the credentials, wait until it is done and return
		async with getting_credentials:
			return
	# Either has never been generated or is older than 23.9 hours
	if device_token_generated_time is None or (milliseconds_since_epoch() - device_token_generated_time) > 85340000:
		async with getting_credentials:
			cert = info.get_tls_cert()
			pkey = info.get_tls_key()

			print("Generate device token")
			dauth = DAuthClient(keys)
			dauth.set_certificate(cert, pkey)
			dauth.set_system_version(SYSTEM_VERSION)
			response = await dauth.device_token(dauth.BAAS)
			device_token = response["device_auth_token"]
			print("Generated device token")

			print("Generate app token")
			aauth = AAuthClient()
			aauth.set_system_version(SYSTEM_VERSION)
			response = await aauth.auth_digital(
				SMM2.TITLE_ID, SMM2.LATEST_VERSION,
				device_token, ticket
			)
			app_token = response["application_auth_token"]
			print("Generated app token")

			device_token_generated_time = milliseconds_since_epoch()

			id_token = None
			print("Generate id token")
			baas = BAASClient()
			baas.set_system_version(SYSTEM_VERSION)
			response = await baas.authenticate(device_token)
			access_token = response["accessToken"]
			response = await baas.login(BAAS_USER_ID, BAAS_PASSWORD, access_token, app_token)
			id_token = response["idToken"]
			user_id = str(int(response["user"]["id"], 16))
			print("Generated id token")

			id_token_generated_time = milliseconds_since_epoch()

			auth_info = authentication.AuthenticationInfo()
			auth_info.token = id_token
			auth_info.ngs_version = 4
			auth_info.token_type = 2

			print("Loading settings")
			s = settings.load("switch")
			s.configure(SMM2.ACCESS_KEY, SMM2.NEX_VERSION, SMM2.CLIENT_VERSION)
			print("Loaded settings")
	# Either has never been generated or is older than 2.9 hours
	if id_token_generated_time is None or (milliseconds_since_epoch() - id_token_generated_time) > 1044000:
		async with getting_credentials:
			print("Generate id token")
			baas = BAASClient()
			baas.set_system_version(SYSTEM_VERSION)
			response = await baas.authenticate(device_token)
			access_token = response["accessToken"]
			response = await baas.login(BAAS_USER_ID, BAAS_PASSWORD, access_token, app_token)
			id_token = response["idToken"]
			user_id = str(int(response["user"]["id"], 16))
			print("Generated id token")

			id_token_generated_time = milliseconds_since_epoch()

			auth_info = authentication.AuthenticationInfo()
			auth_info.token = id_token
			auth_info.ngs_version = 4
			auth_info.token_type = 2

			print("Loading settings")
			s = settings.load("switch")
			s.configure(SMM2.ACCESS_KEY, SMM2.NEX_VERSION, SMM2.CLIENT_VERSION)
			print("Loaded settings")


async def main():
	print("Running API setup")
	await check_tokens()

class AsyncLoopThread(Thread):
	def __init__(self):
		super().__init__(daemon=True)
		self.loop = asyncio.new_event_loop()

	def run(self):
		asyncio.set_event_loop(self.loop)
		self.loop.run_forever()

app = FastAPI(openapi_url=None)
lock = asyncio.Semaphore(3)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

if "banned_ips" in args:
	banned_ips = args["banned_ips"]
else:
	banned_ips = []
@app.middleware("http")
async def add_process_time_header(request, call_next):
	if str(request.client.host) in banned_ips:
		return ORJSONResponse(status_code=400, content={})
	return await call_next(request)

print("Start FastAPI")

app.mount("/docs", StaticFiles(directory="docs", html=True), name="docs")

@app.get("/level_info/{course_id}")
async def read_level_info(course_id: str, noCaching: bool = False):
	course_id = correct_course_id(course_id)
	if (in_cache(course_id) or invalid_course_id_length(course_id) or is_maker_id(course_id)) and not noCaching:
		course_info_json = await obtain_course_info(course_id, None)

		if invalid_level(course_info_json):
			return ORJSONResponse(status_code=400, content=course_info_json)

		return ORJSONResponse(content=course_info_json)
	else:
		await check_tokens()
		async with lock:
			async with backend.connect(s, HOST, PORT) as be:
				async with be.login(str(user_id), auth_info=auth_info) as client:
					store = datastore.DataStoreClientSMM2(client)
					print("Want course info for " + course_id)
					course_info_json = await obtain_course_info(course_id, store, noCaching)

					if invalid_level(course_info_json):
						return ORJSONResponse(status_code=400, content=course_info_json)

					return ORJSONResponse(content=course_info_json)

@app.get("/user_info/{maker_id}")
async def read_user_info(maker_id: str, noCaching: bool = False):
	maker_id = correct_course_id(maker_id)
	if (in_user_cache(maker_id) or invalid_course_id_length(maker_id) or not is_maker_id(maker_id)) and not noCaching:
		user_info_json = await obtain_user_info(maker_id, None)

		if invalid_level(user_info_json):
			return ORJSONResponse(status_code=400, content=user_info_json)

		return ORJSONResponse(content=user_info_json)
	else:
		await check_tokens()
		async with lock:
			async with backend.connect(s, HOST, PORT) as be:
				async with be.login(str(user_id), auth_info=auth_info) as client:
					store = datastore.DataStoreClientSMM2(client)
					print("Want user info for " + maker_id)
					user_info_json = await obtain_user_info(maker_id, store, noCaching)

					if invalid_level(user_info_json):
						return ORJSONResponse(status_code=400, content=user_info_json)

					return ORJSONResponse(content=user_info_json)

@app.get("/level_info_multiple/{course_ids}")
async def read_level_infos(course_ids: str):
	corrected_course_ids = []
	for id in course_ids.split(","):
		id = correct_course_id(id)
		if invalid_course_id_length(id):
			return ORJSONResponse(status_code=400, content={"error": "Invalid course ID", "course_id": id})
		if is_maker_id(id):
			return ORJSONResponse(status_code=400, content={"error": "Code corresponds to a maker", "course_id": id})
		corrected_course_ids.append(id)

	if len(corrected_course_ids) > 500:
		return ORJSONResponse(status_code=400, content={"error": "Number of courses requested must be between 1 and 500"})

	await check_tokens()
	async with lock:
		async with backend.connect(s, HOST, PORT) as be:
			async with be.login(str(user_id), auth_info=auth_info) as client:
				store = datastore.DataStoreClientSMM2(client)
				print("Want course infos for " + course_ids)
				course_info_json = await obtain_course_infos(corrected_course_ids, store)

				if invalid_level(course_info_json):
					return ORJSONResponse(status_code=400, content=course_info_json)

				return ORJSONResponse(content=course_info_json)

@app.get("/level_comments/{course_id}")
async def read_level_comments(course_id: str, noCaching: bool = False):
	course_id = correct_course_id(course_id)
	print("Want comments for " + course_id)
	path = "cache/level_comments/%s" % course_id

	if invalid_course_id_length(course_id):
		return ORJSONResponse(status_code=400, content={"error": "Invalid course ID", "course_id": course_id})
	if is_maker_id(course_id):
		return ORJSONResponse(status_code=400, content={"error": "Code corresponds to a maker", "course_id": course_id})

	os.makedirs(os.path.dirname(path), exist_ok=True)

	if pathlib.Path(path).exists() and not noCaching:
		comments = await add_comment_info_json(None, course_id, None)
		if invalid_level(comments):
			return ORJSONResponse(status_code=400, content=comments)
		return ORJSONResponse(content=comments)
	else:
		await check_tokens()
		async with lock:
			async with backend.connect(s, HOST, PORT) as be:
				async with be.login(str(user_id), auth_info=auth_info) as client:
					store = datastore.DataStoreClientSMM2(client)
					course_info_json = await obtain_course_info(course_id, store)
					if invalid_level(course_info_json):
						return ORJSONResponse(status_code=400, content=course_info_json)
					comments = await add_comment_info_json(store, course_id, course_info_json, noCaching)
					if invalid_level(comments):
						return ORJSONResponse(status_code=400, content=comments)
					return ORJSONResponse(content=comments)

@app.get("/level_played/{course_id}")
async def read_level_played(course_id: str, noCaching: bool = False):
	course_id = correct_course_id(course_id)
	print("Want played for " + course_id)
	path = "cache/level_played/%s" % course_id

	if invalid_course_id_length(course_id):
		return ORJSONResponse(status_code=400, content={"error": "Invalid course ID", "course_id": course_id})
	if is_maker_id(course_id):
		return ORJSONResponse(status_code=400, content={"error": "Code corresponds to a maker", "course_id": course_id})

	os.makedirs(os.path.dirname(path), exist_ok=True)

	if pathlib.Path(path).exists() and not noCaching:
		played = await add_played_info_json(None, course_id)
		if invalid_level(played):
			return ORJSONResponse(status_code=400, content=played)
		return ORJSONResponse(content=played)
	else:
		await check_tokens()
		async with lock:
			async with backend.connect(s, HOST, PORT) as be:
				async with be.login(str(user_id), auth_info=auth_info) as client:
					store = datastore.DataStoreClientSMM2(client)
					course_info_json = await obtain_course_info(course_id, store)
					if invalid_level(course_info_json):
						return ORJSONResponse(status_code=400, content=course_info_json)
					played = await add_played_info_json(store, course_id, noCaching)
					if invalid_level(played):
						return ORJSONResponse(status_code=400, content=played)
					return ORJSONResponse(content=played)

@app.get("/level_deaths/{course_id}")
async def read_level_deaths(course_id: str, noCaching: bool = False):
	course_id = correct_course_id(course_id)
	print("Want deaths for " + course_id)
	path = "cache/level_deaths/%s" % course_id

	if invalid_course_id_length(course_id):
		return ORJSONResponse(status_code=400, content={"error": "Invalid course ID", "course_id": course_id})
	if is_maker_id(course_id):
		return ORJSONResponse(status_code=400, content={"error": "Code corresponds to a maker", "course_id": course_id})

	os.makedirs(os.path.dirname(path), exist_ok=True)

	if pathlib.Path(path).exists() and not noCaching:
		deaths = await add_death_positions_json(None, course_id)
		if invalid_level(deaths):
			return ORJSONResponse(status_code=400, content=deaths)
		return ORJSONResponse(content=deaths)
	else:
		await check_tokens()
		async with lock:
			async with backend.connect(s, HOST, PORT) as be:
				async with be.login(str(user_id), auth_info=auth_info) as client:
					store = datastore.DataStoreClientSMM2(client)
					course_info_json = await obtain_course_info(course_id, store)
					if invalid_level(course_info_json):
						return ORJSONResponse(status_code=400, content=course_info_json)
					deaths = await add_death_positions_json(store, course_id, noCaching)
					if invalid_level(deaths):
						return ORJSONResponse(status_code=400, content=deaths)
					return ORJSONResponse(content=deaths)

@app.get(
	"/level_thumbnail/{course_id}",
	responses = {
		200: {
			"content": {"image/jpg": {}}
		}
	},
	response_class=Response
)
async def read_level_thumbnail(course_id: str):
	course_id = correct_course_id(course_id)
	# Download thumbnails
	print("Want thumbnail for " + course_id)
	path = "cache/level_thumbnail/%s.jpg" % course_id
	os.makedirs(os.path.dirname(path), exist_ok=True)

	if pathlib.Path(path).exists():
		return FileResponse(path=path, media_type="image/jpg")

	course_info_json = None
	if in_cache(course_id) or invalid_course_id_length(course_id):
		course_info_json = await obtain_course_info(course_id, None)
		if invalid_level(course_info_json):
			return ORJSONResponse(status_code=400, content=course_info_json)

	if in_cache(course_id) and await download_thumbnail(None, course_info_json["one_screen_thumbnail"]["url"], path, ServerDataTypes.level_thumbnail):
		return FileResponse(path=path, media_type="image/jpg")
	else:
		await check_tokens()
		async with lock:
			async with backend.connect(s, HOST, PORT) as be:
				async with be.login(str(user_id), auth_info=auth_info) as client:
					store = datastore.DataStoreClientSMM2(client)
					if course_info_json == None:
						course_info_json = await obtain_course_info(course_id, store)
					if invalid_level(course_info_json):
						return ORJSONResponse(status_code=400, content=course_info_json)
					await download_thumbnail(store, course_info_json["one_screen_thumbnail"]["url"], path, ServerDataTypes.level_thumbnail)
					return FileResponse(path=path, media_type="image/jpg")

@app.get(
	"/level_entire_thumbnail/{course_id}",
	responses = {
		200: {
			"content": {"image/jpg": {}}
		}
	},
	response_class=Response
)
async def read_entire_level_thumbnail(course_id: str):
	course_id = correct_course_id(course_id)
	# Download thumbnails
	print("Want entire for " + course_id)
	path = "cache/level_entire_thumbnail/%s.jpg" % course_id
	os.makedirs(os.path.dirname(path), exist_ok=True)

	if pathlib.Path(path).exists():
		return FileResponse(path=path, media_type="image/jpg")

	course_info_json = None
	if in_cache(course_id) or invalid_course_id_length(course_id):
		course_info_json = await obtain_course_info(course_id, None)
		if invalid_level(course_info_json):
			return ORJSONResponse(status_code=400, content=course_info_json)

	if in_cache(course_id) and await download_thumbnail(None, course_info_json["entire_thumbnail"]["url"], path, ServerDataTypes.entire_level_thumbnail):
		return FileResponse(path=path, media_type="image/jpg")
	else:
		await check_tokens()
		async with lock:
			async with backend.connect(s, HOST, PORT) as be:
				async with be.login(str(user_id), auth_info=auth_info) as client:
					store = datastore.DataStoreClientSMM2(client)
					if course_info_json == None:
						course_info_json = await obtain_course_info(course_id, store)
					if invalid_level(course_info_json):
						return ORJSONResponse(status_code=400, content=course_info_json)
					await download_thumbnail(store, course_info_json["entire_thumbnail"]["url"], path, ServerDataTypes.entire_level_thumbnail)
					return FileResponse(path=path, media_type="image/jpg")

@app.get(
	"/level_data/{course_id}",
	responses = {
		200: {
			"content": {"application/octet-stream": {}}
		}
	},
	response_class=Response
)
async def read_level_data(course_id: str):
	course_id = correct_course_id(course_id)
	print("Want course data for " + course_id)
	loc = "cache/level_data/%s.bcd" % course_id
	os.makedirs(os.path.dirname(loc), exist_ok=True)

	if pathlib.Path(loc).exists():
		return FileResponse(path=loc, media_type="application/octet-stream")

	if invalid_course_id_length(course_id):
		return ORJSONResponse(status_code=400, content={"error": "Invalid course ID", "course_id": course_id})

	if is_maker_id(course_id):
		return ORJSONResponse(status_code=400, content={"error": "Code corresponds to a maker", "course_id": course_id})

	info_loc = "cache/level_info/%s" % course_id
	if pathlib.Path(info_loc).exists():
		with open(info_loc, mode="rb") as f:
			zlib_decompressed = zlib.decompress(f.read())
			if invalid_level(orjson.loads(zlib_decompressed)):
				return Response(status_code=400, content=zlib_decompressed, media_type="application/json")

	await check_tokens()
	async with lock:
		async with backend.connect(s, HOST, PORT) as be:
			async with be.login(str(user_id), auth_info=auth_info) as client:
				store = datastore.DataStoreClientSMM2(client)
				param = datastore.DataStorePrepareGetParam()
				param.data_id = course_id_to_dataid(course_id)
				try:
					req_info = await store.prepare_get_object(param)
				except:
					os.makedirs(os.path.dirname(info_loc), exist_ok=True)
					with open(info_loc, mode="wb+") as f:
						f.write(zlib.compress(('{"error": "No course with that ID", "course_id": "%s"}' % course_id).encode("UTF8")))
					return ORJSONResponse(status_code=400, content={"error": "No course with that ID", "course_id": course_id})
				response = await http.get(req_info.url)
				response.raise_if_error()
				with open(loc, "wb") as f:
					f.write(response.body)
					return Response(content=response.body, media_type="application/octet-stream")

@app.get(
	"/level_data_dataid/{dataid}",
	responses = {
		200: {
			"content": {"application/octet-stream": {}}
		}
	},
	response_class=Response
)
async def read_level_data_dataid(dataid: int):
	print("Want course data for dataid %d" % dataid)
	loc = "cache/level_data_dataid/%s.bcd" % dataid
	os.makedirs(os.path.dirname(loc), exist_ok=True)

	if pathlib.Path(loc).exists():
		if os.stat(loc).st_size == 0:
			os.remove(loc)
			return ORJSONResponse(status_code=400, content={"error": "Level data file cannot be downloaded", "data_id": dataid})
		else:
			return FileResponse(path=loc, media_type="application/octet-stream")

	await check_tokens()
	async with lock:
		async with backend.connect(s, HOST, PORT) as be:
			async with be.login(str(user_id), auth_info=auth_info) as client:
				store = datastore.DataStoreClientSMM2(client)
				param = datastore.DataStorePrepareGetParam()
				param.data_id = dataid
				try:
					req_info = await store.prepare_get_object(param)
				except:
					with open(loc, "wb") as f:
						return ORJSONResponse(status_code=400, content={"error": "Level data file cannot be downloaded", "data_id": dataid})
				response = await http.get(req_info.url)
				response.raise_if_error()
				with open(loc, "wb") as f:
					f.write(response.body)
					return Response(content=response.body, media_type="application/octet-stream")

@app.get("/ninji_info")
async def ninji_info():
	await check_tokens()
	async with lock:
		async with backend.connect(s, HOST, PORT) as be:
			async with be.login(str(user_id), auth_info=auth_info) as client:
				store = datastore.DataStoreClientSMM2(client)
				print("Want ninji info")
				course_info_json = await obtain_ninji_info(store)
				return ORJSONResponse(content=course_info_json)

@app.get("/ninji_ghosts/{index}")
async def ninji_ghosts(index: int, time: int = 10000, num: int = 10, includeReplayFiles: bool = False):
	print("Want ninji ghosts for " + str(index))
	# Can hardcode this
	if index < 0 or index > 20:
		return ORJSONResponse(status_code=400, content={"error": "Ninji index must be between 0 and 20"})
	ninji_course_info = None

	await check_tokens()
	async with lock:
		async with backend.connect(s, HOST, PORT) as be:
			async with be.login(str(user_id), auth_info=auth_info) as client:
				store = datastore.DataStoreClientSMM2(client)

				ninji_course_info = await obtain_ninji_info(store)
				ninji_course_id = ninji_course_info["courses"][index]["data_id"]

				ninji_ghosts_info = await obtain_ninji_ghosts(ninji_course_id, time, num, includeReplayFiles, False, store)
				if invalid_ninji_ghosts(ninji_ghosts_info):
					return ORJSONResponse(status_code=400, content=ninji_ghosts_info)
				return ORJSONResponse(content=ninji_ghosts_info)

@app.get("/ninji_replays/{replay_id}")
async def ninji_replays(replay_id: str):
	if ninji_ghost_replay_in_cache(replay_id):
		return FileResponse(path="cache/ninji_ghost_replays/%s.replay" % replay_id, media_type="application/octet-stream")
	else:
		return ORJSONResponse(status_code=404, content={"error": "This replay does not exist"})

@app.get("/get_posted/{maker_id}")
async def search_posted(maker_id: str):
	maker_id = correct_course_id(maker_id)

	user_info_json = None
	if (in_user_cache(maker_id) or invalid_course_id_length(maker_id) or not is_maker_id(maker_id)):
		user_info_json = await obtain_user_info(maker_id, None)
		if invalid_level(user_info_json):
			return ORJSONResponse(status_code=400, content=user_info_json)

	await check_tokens()
	async with lock:
		async with backend.connect(s, HOST, PORT) as be:
			async with be.login(str(user_id), auth_info=auth_info) as client:
				store = datastore.DataStoreClientSMM2(client)
				print("Want uploaded courses from %s" % maker_id)
				if user_info_json == None:
					user_info_json = await obtain_user_info(maker_id, store)

				courses_info_json = await get_courses_posted(100, user_info_json["pid"], store)

				if invalid_level(courses_info_json):
					return ORJSONResponse(status_code=400, content=courses_info_json)

				return ORJSONResponse(content=courses_info_json)

@app.get("/get_liked/{maker_id}")
async def search_liked(maker_id: str):
	maker_id = correct_course_id(maker_id)

	user_info_json = None
	if (in_user_cache(maker_id) or invalid_course_id_length(maker_id) or not is_maker_id(maker_id)):
		user_info_json = await obtain_user_info(maker_id, None)
		if invalid_level(user_info_json):
			return ORJSONResponse(status_code=400, content=user_info_json)

	await check_tokens()
	async with lock:
		async with backend.connect(s, HOST, PORT) as be:
			async with be.login(str(user_id), auth_info=auth_info) as client:
				store = datastore.DataStoreClientSMM2(client)
				print("Want liked courses from %s" % maker_id)
				if user_info_json == None:
					user_info_json = await obtain_user_info(maker_id, store)

				courses_info_json = await get_courses_liked(100, user_info_json["pid"], store)

				if invalid_level(courses_info_json):
					return ORJSONResponse(status_code=400, content=courses_info_json)

				return ORJSONResponse(content=courses_info_json)

@app.get("/get_played/{maker_id}")
async def search_played(maker_id: str):
	maker_id = correct_course_id(maker_id)

	user_info_json = None
	if (in_user_cache(maker_id) or invalid_course_id_length(maker_id) or not is_maker_id(maker_id)):
		user_info_json = await obtain_user_info(maker_id, None)
		if invalid_level(user_info_json):
			return ORJSONResponse(status_code=400, content=user_info_json)

	await check_tokens()
	async with lock:
		async with backend.connect(s, HOST, PORT) as be:
			async with be.login(str(user_id), auth_info=auth_info) as client:
				store = datastore.DataStoreClientSMM2(client)
				print("Want played courses from %s" % maker_id)
				if user_info_json == None:
					user_info_json = await obtain_user_info(maker_id, store)

				courses_info_json = await get_courses_played(100, user_info_json["pid"], store)

				if invalid_level(courses_info_json):
					return ORJSONResponse(status_code=400, content=courses_info_json)

				return ORJSONResponse(content=courses_info_json)

@app.get("/get_first_cleared/{maker_id}")
async def search_first_cleared(maker_id: str):
	maker_id = correct_course_id(maker_id)

	user_info_json = None
	if (in_user_cache(maker_id) or invalid_course_id_length(maker_id) or not is_maker_id(maker_id)):
		user_info_json = await obtain_user_info(maker_id, None)
		if invalid_level(user_info_json):
			return ORJSONResponse(status_code=400, content=user_info_json)

	await check_tokens()
	async with lock:
		async with backend.connect(s, HOST, PORT) as be:
			async with be.login(str(user_id), auth_info=auth_info) as client:
				store = datastore.DataStoreClientSMM2(client)
				print("Want first cleared courses from %s" % maker_id)
				if user_info_json == None:
					user_info_json = await obtain_user_info(maker_id, store)

				courses_info_json = await get_courses_first_cleared(100, user_info_json["pid"], store)

				if invalid_level(courses_info_json):
					return ORJSONResponse(status_code=400, content=courses_info_json)

				return ORJSONResponse(content=courses_info_json)

@app.get("/get_world_record/{maker_id}")
async def search_world_record(maker_id: str):
	maker_id = correct_course_id(maker_id)

	user_info_json = None
	if (in_user_cache(maker_id) or invalid_course_id_length(maker_id) or not is_maker_id(maker_id)):
		user_info_json = await obtain_user_info(maker_id, None)
		if invalid_level(user_info_json):
			return ORJSONResponse(status_code=400, content=user_info_json)

	await check_tokens()
	async with lock:
		async with backend.connect(s, HOST, PORT) as be:
			async with be.login(str(user_id), auth_info=auth_info) as client:
				store = datastore.DataStoreClientSMM2(client)
				print("Want world record courses from %s" % maker_id)
				if user_info_json == None:
					user_info_json = await obtain_user_info(maker_id, store)

				courses_info_json = await get_courses_world_record(100, user_info_json["pid"], store)

				if invalid_level(courses_info_json):
					return ORJSONResponse(status_code=400, content=courses_info_json)

				return ORJSONResponse(content=courses_info_json)

@app.get("/get_super_worlds")
async def get_world_maps():
	await check_tokens()
	async with lock:
		async with backend.connect(s, HOST, PORT) as be:
			async with be.login(str(user_id), auth_info=auth_info) as client:
				store = datastore.DataStoreClientSMM2(client)
				print("Want world maps")
				world_maps_json = await get_world_maps_json(store)
				return ORJSONResponse(content=world_maps_json)

@app.get("/super_world/{map_id}")
async def get_world_maps(map_id: str, noCaching: bool = False):
	if len(map_id) < 34:
		return ORJSONResponse(status_code=400, content={"error": "Super world ID is invalid", "id": map_id})

	path = "cache/super_worlds/%s" % map_id

	os.makedirs(os.path.dirname(path), exist_ok=True)

	if pathlib.Path(path).exists() and not noCaching:
		world_map = await search_world_map(None, [map_id])
		if invalid_level(world_map):
			return ORJSONResponse(status_code=400, content=world_map)
		return ORJSONResponse(content=world_map)
	else:
		await check_tokens()
		async with lock:
			async with backend.connect(s, HOST, PORT) as be:
				async with be.login(str(user_id), auth_info=auth_info) as client:
					store = datastore.DataStoreClientSMM2(client)
					print("Want world map %s" % map_id)
					world_map = await search_world_map(store, [map_id], noCaching)

					if invalid_level(world_map):
						return ORJSONResponse(status_code=400, content=world_map)

					return ORJSONResponse(content=world_map)

@app.get("/search_endless_mode")
async def search_endless_mode(count: int = 10, difficulty: str = "n"):
	difficulty_num = difficulty_string_to_num(difficulty)
	if difficulty_num == -1:
		return ORJSONResponse(status_code=400, content={"error": "Difficulty %s is an invalid difficulty" % difficulty})
	if count < 1 or count > 500:
		return ORJSONResponse(status_code=400, content={"error": "Count %d is an invalid count, must be between 1 and 500" % count})
	await check_tokens()
	async with lock:
		async with backend.connect(s, HOST, PORT) as be:
			async with be.login(str(user_id), auth_info=auth_info) as client:
				store = datastore.DataStoreClientSMM2(client)
				print("Want %d endless courses at difficulty %s" % (count, difficulty))
				courses_info_json = await search_endless_courses(count, difficulty_num, store)

				if invalid_level(courses_info_json):
					return ORJSONResponse(status_code=400, content=courses_info_json)

				return ORJSONResponse(content=courses_info_json)

@app.get("/search_new")
async def search_new(count: int = 10):
	if count < 1 or count > 20:
		return ORJSONResponse(status_code=400, content={"error": "Count %d is an invalid count, must be between 1 and 20" % count})
	await check_tokens()
	async with lock:
		async with backend.connect(s, HOST, PORT) as be:
			async with be.login(str(user_id), auth_info=auth_info) as client:
				store = datastore.DataStoreClientSMM2(client)
				print("Want %d latest courses" % count)
				courses_info_json = await search_latest_courses(count, store)

				if invalid_level(courses_info_json):
					return ORJSONResponse(status_code=400, content=courses_info_json)

				return ORJSONResponse(content=courses_info_json)

@app.get("/search_popular")
async def search_popular(count: int = 10, difficulty: str = "n", rejectRegions: str = ""):
	difficulty_num = difficulty_string_to_num(difficulty)
	if difficulty_num == -1:
		return ORJSONResponse(status_code=400, content={"error": "Difficulty %s is an invalid difficulty" % difficulty})
	if count < 1 or count > 100:
		return ORJSONResponse(status_code=400, content={"error": "Count %d is an invalid count, must be between 1 and 100" % count})
	reject_regions_list = region_string_to_list(rejectRegions)
	await check_tokens()
	async with lock:
		async with backend.connect(s, HOST, PORT) as be:
			async with be.login(str(user_id), auth_info=auth_info) as client:
				store = datastore.DataStoreClientSMM2(client)
				print("Want %d courses by point ranking, difficulty %s without regions %s" % (count, difficulty, rejectRegions))
				courses_info_json = await search_courses_point_ranking(count, difficulty_num, reject_regions_list, store)

				if invalid_level(courses_info_json):
					return ORJSONResponse(status_code=400, content=courses_info_json)

				return ORJSONResponse(content=courses_info_json)

loop_handler = AsyncLoopThread()
loop_handler.start()
asyncio.run_coroutine_threadsafe(main(), loop_handler.loop)