# Copyright Mario Possamato https://github.com/MarioPossamato/SMM2

import struct
import zlib
from Crypto.Hash import CMAC
from Crypto.Cipher import AES
from Crypto import Random
from nintendo.sead import Random
from nintendo.enl import crypto
from SMM2 import streams
from SMM2 import keytables

class Course:
	def __init__(self, data=None):
		if not data:
			return None
		else:
			self.load(data)

	def load(self, data=None):
		if not data:
			return None
		else:
			self.data = data
			self.stream = streams.StreamIn(data)

	def decrypt(self):
		self.stream = streams.StreamIn(self.data)

		self.header = self.stream.substream(0x10)
		self.encrypted = self.stream.read(0x5BFC0)
		self.cryptoConfig = self.stream.substream(0x30)

		self.header.skip(0x4)
		self.filetype = self.header.read(0x2)
		self.header.skip(0x2)
		self.crc32 = self.header.read(0x4)
		self.magic = self.header.read(0x4)

		self.iv = self.cryptoConfig.read(0x10)
		self.randomState = self.cryptoConfig.read(0x10)
		self.cmac = self.cryptoConfig.read(0x10)

		self.context = struct.unpack_from("<IIII", self.cryptoConfig.data, 0x10)
		self.rand = Random(*self.context)

		self.key = crypto.create_key(self.rand, keytables.course, 0x10)
		self.aes = AES.new(self.key, AES.MODE_CBC, self.iv)
		self.decrypted = self.aes.decrypt(self.encrypted)

		self.key = crypto.create_key(self.rand, keytables.course, 0x10)
		self.mac = CMAC.new(self.key, ciphermod=AES)
		self.mac.update(self.decrypted)
		self.mac.verify(self.cmac)

		self.data = self.decrypted

		return None

	def encrypt(self):
		self.stream = streams.StreamIn(self.data)

		self.header = streams.StreamOut()
		self.decrypted = self.stream.read(0x5BFC0)

		self.header.write(struct.pack("<I", 0x1))
		self.header.write(struct.pack("<H", 0x10))
		self.header.write(struct.pack("<H", 0x0))
		self.header.write(struct.pack("<I", zlib.crc32(self.decrypted)))
		self.header.write("SCDL".encode("utf-8"))

		self.randomState = Random.get_random_bytes(0x10)

		self.context = struct.unpack("<IIII", self.randomState)
		self.rand = Random(*self.context)
		
		self.key = crypto.create_key(self.rand, keytables.course, 0x10)
		self.aes = AES.new(self.key, AES.MODE_CBC, Random.get_random_bytes(0x10))
		self.encrypted = self.aes.encrypt(self.decrypted)

		self.key = crypto.create_key(self.rand, keytables.course, 0x10)
		self.mac = CMAC.new(self.key, ciphermod=AES)
		self.mac.update(self.decrypted)
		self.mac.digest()

		self.data = self.header.data() + self.encrypted + self.aes.iv + self.randomState + self.mac.digest()

		return None

class Thumbnail:
	def __init__(self, data=None):
		if not data:
			return None
		else:
			self.load(data)

	def load(self, data=None):
		if not data:
			return None
		else:
			self.data = data
			self.stream = streams.StreamIn(data)

	def decrypt(self):
		self.stream = streams.StreamIn(self.data)

		self.encrypted = self.stream.read(0x1BFD0)
		self.cryptoConfig = self.stream.substream(0x30)

		self.iv = self.cryptoConfig.read(0x10)
		self.randomState = self.cryptoConfig.read(0x10)
		self.cmac = self.cryptoConfig.read(0x10)

		self.context = struct.unpack_from("<IIII", self.cryptoConfig.data, 0x10)
		self.rand = Random(*self.context)

		self.key = crypto.create_key(self.rand, keytables.thumbnail, 0x10)
		self.aes = AES.new(self.key, AES.MODE_CBC, self.iv)
		self.decrypted = self.aes.decrypt(self.encrypted)

		self.key = crypto.create_key(self.rand, keytables.thumbnail, 0x10)
		self.mac = CMAC.new(self.key, ciphermod=AES)
		self.mac.update(self.decrypted)
		self.mac.verify(self.cmac)

		self.data = self.decrypted

		return None

	def encrypt(self):
		self.stream = streams.StreamIn(self.data)

		self.decrypted = self.stream.read(0x1BFD0)

		self.randomState = Random.get_random_bytes(0x10)

		self.context = struct.unpack("<IIII", self.randomState)
		self.rand = Random(*self.context)
		
		self.key = crypto.create_key(self.rand, keytables.thumbnail, 0x10)
		self.aes = AES.new(self.key, AES.MODE_CBC, Random.get_random_bytes(0x10))
		self.encrypted = self.aes.encrypt(self.decrypted)

		self.key = crypto.create_key(self.rand, keytables.thumbnail, 0x10)
		self.mac = CMAC.new(self.key, ciphermod=AES)
		self.mac.update(self.decrypted)
		self.mac.digest()

		self.data = self.encrypted + self.aes.iv + self.randomState + self.mac.digest()

		return None

class Save:
	def __init__(self, data=None):
		if not data:
			return None
		else:
			self.load(data)

	def load(self, data=None):
		if not data:
			return None
		else:
			self.data = data
			self.stream = streams.StreamIn(data)

	def decrypt(self):
		self.stream = streams.StreamIn(self.data)

		self.header = self.stream.substream(0x10)
		self.encrypted = self.stream.read(0xBFC0)
		self.cryptoConfig = self.stream.substream(0x30)

		self.header.skip(0x4)
		self.filetype = self.header.read(0x2)
		self.header.skip(0x2)
		self.crc32 = self.header.read(0x4)
		self.magic = self.header.read(0x4)

		self.iv = self.cryptoConfig.read(0x10)
		self.randomState = self.cryptoConfig.read(0x10)
		self.cmac = self.cryptoConfig.read(0x10)

		self.context = struct.unpack_from("<IIII", self.cryptoConfig.data, 0x10)
		self.rand = Random(*self.context)

		self.key = crypto.create_key(self.rand, keytables.save, 0x10)
		self.aes = AES.new(self.key, AES.MODE_CBC, self.iv)
		self.decrypted = self.aes.decrypt(self.encrypted)

		self.key = crypto.create_key(self.rand, keytables.save, 0x10)
		self.mac = CMAC.new(self.key, ciphermod=AES)
		self.mac.update(self.decrypted)
		self.mac.verify(self.cmac)

		self.data = self.decrypted

		return None
