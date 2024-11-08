import asyncio

from anynet import tls
from nintendo import switch
from nintendo.switch import dauth, dragons
from struct import unpack

import logging

logging.basicConfig(level=logging.INFO)

# TODO ask user for country, no accessible endpoint gives the country of my account automatically
SMM2_TITLE_ID = 0x01009B90006DC000
COUNTRY = "US"

username = None
password = None
with open("ConsoleData/8000000000000010", mode="rb") as file:
	data = file.read()
	username_bytes = bytearray(data[0x49C020:0x49C028])
	username_bytes.reverse()
	username = "0x" + username_bytes.hex().upper()
	password = data[0x49C028:0x49C050].decode("ascii")


async def create_args():
	keys = switch.load_keys("./ConsoleData/prod.keys")
	info = switch.ProdInfo(keys, "./ConsoleData/PRODINFO.dec")
	cert = info.get_tls_cert()
	# with open("cert.pem", mode="wb") as cert_file:
	# 	cert_file.write(cert.encode(tls.TYPE_PEM))
	pkey = info.get_tls_key()
	# with open("privkey.pem", mode="wb") as key_file:
	# 	key_file.write(pkey.encode(tls.TYPE_PEM))

	dauth_client = dauth.DAuthClient(keys)
	dauth_client.set_certificate(cert, pkey)
	dauth_client.set_system_version(dauth.LATEST_VERSION)

	# Obtain device ID from prodinfo
	device_id = None
	with open("ConsoleData/PRODINFO.dec", mode="rb") as file:
		data = file.read()
		# It doesn't appear to matter what the device_id is
		device_id = int(data[0x546:0x556].decode("ascii"), 16)

	# account_id = None
	# with open("ConsoleData/SUPER MARIO MAKER 2 v0 (01009B90006DC000) (BASE).tik", "rb") as f:
	# 	ticket = f.read()
	# 	# Assumed the signature type is RSA_2048 SHA256 (https://switchbrew.org/wiki/Ticket)
	# 	ticket_start = 0x4 + 0x100 + 0x3C
	# 	account_id = unpack("L", ticket[ticket_start + 0x170:ticket_start + 0x170 + 0x4])[0]

	dragons_client = dragons.DragonsClient(device_id)
	dragons_client.set_certificate(cert, pkey)
	dragons_client.set_system_version(dauth.LATEST_VERSION)

	# Obtain dragons elicense
	response = await dauth_client.device_token(dauth.CLIENT_ID_DRAGONS)
	device_token_dragons = response["device_auth_token"]

	response = await dragons_client.publish_device_linked_elicenses(
		device_token_dragons
	)

	# There are many valid, just choose the first that is active
	for possible_license in response["elicenses"]:
		if (
			possible_license["status"] == "active"
			and int(possible_license["rights_id"], 16) == SMM2_TITLE_ID
		):
			with open("webserver_args.json", mode="w") as file:
				args = """{
	"system_version": %d,
	"user_id": "%s",
	"password": "%s",
	"keys": "./ConsoleData/prod.keys",
	"prodinfo": "./ConsoleData/PRODINFO.dec",
	"elicense_id": "%s",
	"na_id": "%s",
	"country": "%s"
}""" % (
					dauth.LATEST_VERSION,
					username,
					password,
					possible_license["elicense_id"],
					possible_license["account_id"],
					COUNTRY,
				)
				file.write(args)
			return

	# If here, no elicense found
	logging.critical("NO ELICENSE FOUND ON THIS DEVICE FOR SUPER MARIO MAKER 2")
	logging.critical(
		"Consider using Charles or another MITM proxy to find the elicense_id and na_id"
	)
	logging.critical("Additionally, ensure this switch is the primary switch")


asyncio.run(create_args())
