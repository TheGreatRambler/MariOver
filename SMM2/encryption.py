import io
import struct
import zlib

from Crypto.Cipher import _mode_cbc, AES
from Crypto.Hash import CMAC
from Crypto.Random import get_random_bytes
from nintendo.enl import crypto
from nintendo.sead import Random

from . import keytables


def decrypt_bcd(data: bytes, *args, **kwargs) -> bytes:
    stream: io.BytesIO = io.BytesIO(
        data
    )

    header: io.BytesIO = io.BytesIO(
        stream.read(
            0x10
        )
    )
    encrypted: bytes = stream.read(
        0x5bfc0
    )
    footer: io.BytesIO = io.BytesIO(
        stream.read(
            0x30
        )
    )

    header.seek(
        header.tell() +
        0x4
    )
    filetype: int = struct.unpack(
        '<H',
        header.read(
            0x2
        )
    )[0]
    header.seek(
        header.tell() +
        0x2
    )
    crc32: int = struct.unpack(
        '<I',
        header.read(0x4)
    )[0]
    magic: str = header.read(
        0x4
    ).decode(
        'utf-8'
    )

    iv: bytes = footer.read(
        0x10
    )
    seed: bytes = footer.read(
        0x10
    )
    cmac: bytes = footer.read(
        0x10
    )

    context: tuple = struct.unpack_from(
        '<IIII',
        footer.getvalue(),
        0x10
    )
    random: Random = Random(
        *context
    )

    key: bytes = crypto.create_key(
        random,
        keytables.bcd,
        0x10
    )
    aes: _mode_cbc.CbcMode = AES.new(
        key,
        AES.MODE_CBC,
        iv
    )
    decrypted: bytes = aes.decrypt(
        encrypted
    )


    key: bytes = crypto.create_key(
        random,
        keytables.bcd,
        0x10
    )
    mac: CMAC.CMAC = CMAC.new(
        key,
        ciphermod=AES
    )
    mac.update(
        decrypted
    )
    mac.verify(
        cmac
    )

    return decrypted


def encrypt_bcd(data: bytes, *args, **kwargs) -> bytes:
    stream: io.BytesIO = io.BytesIO(
        data
    )

    header: io.BytesIO = io.BytesIO()
    decrypted: bytes = stream.read(
        0x5bfc0
    )

    header.write(
        struct.pack(
            '<I',
            0x1
        ) +
        struct.pack(
            '<H',
            0x10
        ) +
        struct.pack(
            '<H',
            0x0
        ) +
        struct.pack(
            '<I',
            zlib.crc32(
                decrypted
            )
        ) +
        'SCDL'.encode(
            'utf-8'
        )
    )

    seed: bytes = get_random_bytes(
        0x10
    )

    context: tuple = struct.unpack_from(
        '<IIII',
        seed
    )
    random: Random = Random(
        *context
    )

    key: bytes = crypto.create_key(
        random,
        keytables.bcd,
        0x10
    )
    aes: _mode_cbc.CbcMode = AES.new(
        key,
        AES.MODE_CBC,
        get_random_bytes(
            0x10
        )
    )
    encrypted: bytes = aes.encrypt(
        decrypted
    )

    key: bytes = crypto.create_key(
        random,
        keytables.bcd,
        0x10
    )
    mac: CMAC.CMAC = CMAC.new(
        key,
        ciphermod=AES
    )
    mac.update(
        decrypted
    )

    return header.getvalue() + encrypted + aes.iv + seed + mac.digest()


def decrypt_btl(data: bytes, *args, **kwargs) -> bytes:
    stream: io.BytesIO = io.BytesIO(
        data
    )

    encrypted: bytes = stream.read(
        0x1bfd0
    )
    footer: io.BytesIO = io.BytesIO(
        stream.read(
            0x30
        )
    )

    iv: bytes = footer.read(
        0x10
    )
    seed: bytes = footer.read(
        0x10
    )
    cmac: bytes = footer.read(
        0x10
    )

    context: tuple = struct.unpack_from(
        '<IIII',
        footer.getvalue(),
        0x10
    )
    random: Random = Random(*context)

    key: bytes = crypto.create_key(
        random,
        keytables.btl,
        0x10
    )
    aes: _mode_cbc.CbcMode = AES.new(
        key,
        AES.MODE_CBC,
        iv
    )
    decrypted: bytes = aes.decrypt(
        encrypted
    )

    key: bytes = crypto.create_key(
        random,
        keytables.btl,
        0x10
    )
    mac: CMAC.CMAC = CMAC.new(
        key,
        ciphermod=AES
    )
    mac.update(
        decrypted
    )
    mac.verify(
        cmac
    )

    return decrypted


def encrypt_btl(data: bytes, *args, **kwargs) -> bytes:
    stream: io.BytesIO = io.BytesIO(
        data
    )

    decrypted: bytes = stream.read(
        0x1bfd0
    )

    seed: bytes = get_random_bytes(
        0x10
    )

    context: tuple = struct.unpack_from(
        '<IIII',
        seed
    )
    random: Random = Random(
        *context
    )

    key: bytes = crypto.create_key(
        random,
        keytables.btl,
        0x10
    )
    aes: _mode_cbc.CbcMode = AES.new(
        key,
        AES.MODE_CBC,
        get_random_bytes(
            0x10
        )
    )
    encrypted: bytes = aes.encrypt(
        decrypted
    )

    key: bytes = crypto.create_key(
        random,
        keytables.btl,
        0x10
    )
    mac: CMAC.CMAC = CMAC.new(
        key,
        ciphermod=AES
    )
    mac.update(
        decrypted
    )

    return encrypted + aes.iv + seed + mac.digest()


class Course(object):

    def __init__(self, data: bytes, *args, **kwargs) -> None:
        self.data: bytes = data

    def decrypt(self, *args, **kwargs) -> None:
        self.data: bytes = decrypt_bcd(self.data)

    def encrypt(self, *args, **kwargs) -> None:
        self.data: bytes = encrypt_bcd(self.data)
