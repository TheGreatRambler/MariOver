import struct
import codecs

BIG_ENDIAN = codecs.BOM_UTF16_BE
LITTLE_ENDIAN = codecs.BOM_UTF16_LE

class StreamIn:
	def __init__(self, data=None):
		self.position = 0
		self.byteorder = BIG_ENDIAN
		if not data:
			return None
		else:
			self.load(data)

	def load(self, data=None):
		if not data:
			return None
		else:
			self.data = data

	def substream(self, length=None, byteorder=None):
		if not byteorder:
			read = self.read(length)
		else:
			if byteorder == BIG_ENDIAN:
				read = self.read(length, BIG_ENDIAN)
			elif byteorder == LITTLE_ENDIAN:
				read = self.read(length, LITTLE_ENDIAN)
			else:
				return None
		return StreamIn(read)

	def seek(self, pos=None):
		if pos is None:
			return None
		else:
			self.position = pos

	def skip(self, length=None):
		if not length:
			return None
		else:
			self.seek(self.position + length)

	def read(self, length=None, byteorder=None):
		if not length:
			return False
		else:
			read = self.data[ self.position : self.position + length ]
			self.position += length
		if not byteorder:
			if self.byteorder == BIG_ENDIAN:
				return read
			elif self.byteorder == LITTLE_ENDIAN:
				return struct.pack("<I", struct.unpack(">I", read)[0])
			else:
				return None
		else:
			if byteorder == BIG_ENDIAN:
				return read
			elif byteorder == LITTLE_ENDIAN:
				return struct.pack("<I", struct.unpack(">I", read)[0])
			else:
				return None

	def read8(self):
		read = self.read(1)
		if not len(read) == 1:
			return None
		else:
			return struct.unpack(">B", read)[0]

	def read16(self, byteorder=None):
		if not byteorder:
			read = self.read(2)
		else:
			read = self.read(2, byteorder)
		if not len(read) == 2:
			return None
		else:
			return struct.unpack(">H", read)[0]

	def read32(self, byteorder=None):
		if not byteorder:
			read = self.read(4)
		else:
			read = self.read(4, byteorder)
		if not len(read) == 4:
			return None
		else:
			return struct.unpack(">I", read)[0]

	def read64(self, byteorder=None):
		if not byteorder:
			read = self.read(8)
		else:
			read = self.read(8, byteorder)
		if not len(read) == 8:
			return None
		else:
			return struct.unpack(">Q", read)[0]

class StreamOut:
	def __init__(self, data=None):
		self.byteorder = BIG_ENDIAN
		if not data:
			self.chunks = []
		else:
			self.chunks = [data]

	def data(self):
		return b"".join(self.chunks)

	def write(self, data=None, byteorder=None):
		if not data:
			return None
		else:
			if not byteorder:
				if self.byteorder == BIG_ENDIAN:
					self.chunks.append(data)
				elif self.byteorder == LITTLE_ENDIAN:
					self.chunks.append(struct.pack("<I", struct.unpack(">I", data)[0]))
				else:
					return None
			else:
				if byteorder == BIG_ENDIAN:
					self.chunks.append(data)
				elif byteorder == LITTLE_ENDIAN:
					self.chunks.append(struct.pack("<I", struct.unpack(">I", data)[0]))
				else:
					return None
		

	def write8(self, value=None):
		if value is None:
			return None
		else:
			self.chunks.append(struct.pack(">B", value))

	def write16(self, value=None, byteorder=None):
		if value is None:
			return None
		else:
			if not byteorder:
				if self.byteorder == BIG_ENDIAN:
					self.chunks.append(struct.pack(">H", value))
				elif self.byteorder == LITTLE_ENDIAN:
					self.chunks.append(struct.pack("<H", value))
			else:
				if byteorder == BIG_ENDIAN:
					self.chunks.append(struct.pack(">H", value))
				elif byteorder == LITTLE_ENDIAN:
					self.chunks.append(struct.pack("<H", value))

	def write32(self, value=None, byteorder=None):
		if value is None:
			return None
		else:
			if not byteorder:
				if self.byteorder == BIG_ENDIAN:
					self.chunks.append(struct.pack(">I", value))
				elif self.byteorder == LITTLE_ENDIAN:
					self.chunks.append(struct.pack("<I", value))
			else:
				if byteorder == BIG_ENDIAN:
					self.chunks.append(struct.pack(">I", value))
				elif byteorder == LITTLE_ENDIAN:
					self.chunks.append(struct.pack("<I", value))

	def write64(self, value=None, byteorder=None):
		if value is None:
			return None
		else:
			if not byteorder:
				if self.byteorder == BIG_ENDIAN:
					self.chunks.append(struct.pack(">Q", value))
				elif self.byteorder == LITTLE_ENDIAN:
					self.chunks.append(struct.pack("<Q", value))
			else:
				if byteorder == BIG_ENDIAN:
					self.chunks.append(struct.pack(">Q", value))
				elif byteorder == LITTLE_ENDIAN:
					self.chunks.append(struct.pack("<Q", value))
