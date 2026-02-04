import asyncio

from anynet import tls
from nintendo import switch
from nintendo.switch import dauth, dragons
from struct import unpack
import os
import json

import logging

logging.basicConfig(level=logging.INFO)

# TODO ask user for country, no accessible endpoint
# gives the country of an account automatically
SMM2_TITLE_ID = 0x01009B90006DC000
COUNTRY = "US"

username = None
password = None
with open("ConsoleData/8000000000000010", mode="rb") as file:
    data = file.read()
    username_bytes = bytearray(data[0x90020:0x90028])
    username_bytes.reverse()
    username = "0x" + username_bytes.hex().upper()
    password = data[0x90028:0x90050].decode("ascii")

penne_id = None
with open("ConsoleData/8000000000000110", mode="rb") as file:
    data = file.read()
    start = 0x50000
    penne_data = json.JSONDecoder().raw_decode(
        data[start : start + 0x1000].decode("ascii")
    )[0]
    if not "id" in penne_data:
        logging.critical("Penne ID not found, aborting")
        os._exit(1)
    penne_id = penne_data["id"]


async def create_args():
    keys = switch.load_keys("./ConsoleData/prod.keys")
    info = switch.ProdInfo(keys, "./ConsoleData/PRODINFO.dec")
    cert = info.get_tls_cert()
    # with open("cert.pem", mode="wb") as cert_file:
    # 	cert_file.write(cert.encode(tls.TYPE_PEM))
    pkey = info.get_tls_key()
    # with open("privkey.pem", mode="wb") as key_file:
    # 	key_file.write(pkey.encode(tls.TYPE_PEM))

    # account_id = None
    # with open("ConsoleData/SUPER MARIO MAKER 2 v0 (01009B90006DC000) (BASE).tik", "rb") as f:
    # 	ticket = f.read()
    # 	# Assumed the signature type is RSA_2048 SHA256 (https://switchbrew.org/wiki/Ticket)
    # 	ticket_start = 0x4 + 0x100 + 0x3C
    # 	account_id = unpack("L", ticket[ticket_start + 0x170:ticket_start + 0x170 + 0x4])[0]

    dauth_client = dauth.DAuthClient(keys)
    dauth_client.set_certificate(cert, pkey)
    dauth_client.set_system_version(dauth.LATEST_VERSION)

    dauth_cache = dauth.DAuthCache(dauth_client)

    dragons_client = dragons.DragonsClient(info.get_device_id())
    dragons_client.set_certificate(cert, pkey)
    dragons_client.set_system_version(dauth.LATEST_VERSION)

    # All client IDs will be preloaded, get Dragons from cache
    device_token_dragons = await dauth_cache.device_token(dauth.CLIENT_ID_DRAGONS)

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
    "country": "%s",
    "penne_id": "%s"
}""" % (
                    dauth.LATEST_VERSION,
                    username,
                    password,
                    possible_license["elicense_id"],
                    possible_license["account_id"],
                    COUNTRY,
                    penne_id,
                )
                file.write(args)
            return

    # If here, no elicense found
    logging.critical("NO ELICENSE FOUND ON THIS DEVICE FOR SUPER MARIO MAKER 2")
    logging.critical(
        "Consider using Charles or another MITM proxy to find the elicense_id and na_id"
    )
    logging.critical(
        "This is usually at URL `https://dragons.hac.lp1.dragons.nintendo.net/v2/contents_authorization_token_for_aauth/issue`"
    )
    logging.critical("Additionally, ensure this switch is the primary switch")

    # Still create the file if the user must MITM
    with open("webserver_args.json", mode="w") as file:
        args = """{
    "system_version": %d,
    "user_id": "%s",
    "password": "%s",
    "keys": "./ConsoleData/prod.keys",
    "prodinfo": "./ConsoleData/PRODINFO.dec",
    "elicense_id": "",
    "na_id": "",
    "country": "%s",
    "penne_id": "%s"
}""" % (
            dauth.LATEST_VERSION,
            username,
            password,
            COUNTRY,
            penne_id,
        )
        file.write(args)


asyncio.run(create_args())
