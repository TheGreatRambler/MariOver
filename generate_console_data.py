from nintendo.dauth import LATEST_VERSION

username = None
password = None
with open("ConsoleData/8000000000000010", mode="rb") as file:
	data = file.read()
	username_bytes = bytearray(data[0x00064020:0x00064028])
	username_bytes.reverse()
	username = "0x" + username_bytes.hex().upper()
	password = data[0x00064028:0x00064050].decode("ascii")
with open("webserver_args.json", mode="w") as file:
	args = """{
	"system_version": %d,
	"user_id": "%s",
	"password": "%s",
	"keys": "./ConsoleData/prod.keys",
	"prodinfo": "./ConsoleData/PRODINFO.dec",
	"ticket": "./ConsoleData/SUPER MARIO MAKER 2 v0 (01009B90006DC000) (BASE).tik"
}""" % (LATEST_VERSION, username, password)
	file.write(args)