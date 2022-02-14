import matplotlib.pyplot as plt
import os
import sqlite3
from datetime import datetime


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

con = sqlite3.connect("dump/dump.db")

# Dump must be placed in the "dump" folder
if not os.path.exists("dump/2019uncleared.txt"):
	with open("dump/2019uncleared.txt", "a", encoding="utf-8") as logging_file:
		print("name,description,id,attempts,footprints,date,upload_time,likes,boos,comments,style,theme,tag1,tag2", file=logging_file)
		levels = con.execute("SELECT clears,name,description,course_id,attempts,plays,uploaded,upload_time,likes,boos,num_comments,gamestyle,theme,tag1,tag2 FROM level WHERE uploaded<157785840000")
		i = 0
		for level in levels:
			clears = int(level[0])
			if clears == 0:
				print("'%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (level[1], level[2], level[3], level[4], level[5], level[6], level[7], level[8], level[9], level[10], GameStyles[level[11]], CourseThemes[level[12]], TagNames[level[13]], TagNames[level[14]]), file=logging_file)
				logging_file.flush()
			i += 1
			if i % 10000 == 0:
				print("Handled %d levels" % i)
		con.close()
