import struct
from enum import Enum

class PacketProvenance(Enum):
    server = 0x01
    client = 0x02

PACKETS = {}

def packet(n):
    def wrapper(cls):
        PACKETS[n] = cls
        cls.packet_id = n
        return cls
    return wrapper

@packet(0x6d04b3da)
class WelcomePacket:
    def __init__(self, message=''):
        self.message = message

    def encode(self):
        return self.message.encode('ascii')

    @classmethod
    def decode(cls, packet):
        return cls(packet.decode('ascii'))

@packet(0xe548e74a)
class VersionPacket:
    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch

    def encode(self):
        return struct.pack('<IfIII', 0,
                                     float('{}.{}'.format(self.major, self.minor)),
                                    self.major, self.minor, self.patch)

    @classmethod
    def decode(cls, packet):
        unknown_1, legacy_version, major, minor, patch = struct.unpack('<IfIII', packet)
        return cls(major, minor, patch)

class GameType(Enum):
    siege = 0
    single_front = 1
    double_front = 2
    deep_strike = 3
    peacetime = 4
    border_war = 5

@packet(0x3de66711)
class DifficultyPacket:
    def __init__(self, difficulty, game_type):
        self.difficulty = difficulty
        self.game_type = game_type

    def encode(self):
        return struct.pack('<II', self.difficulty, self.game_type.value)

    @classmethod
    def decode(cls, packet):
        difficulty, game_type_raw = struct.unpack('<II', packet)
        return cls(difficulty, GameType(game_type_raw))

@packet(0xf5821226)
class HeartbeatPacket:
    def encode(self):
        return b''

    @classmethod
    def decode(cls, packet):
        if packet != b'':
            raise ValueError('Payload in heartbeat')
        return cls()

def encode(packet, provenance=PacketProvenance.client):
    encoded_block = packet.encode()
    block_len = len(encoded_block)
    return (struct.pack('<IIIIII',
                        0xdeadbeef,
                        24 + block_len,
                        provenance.value,
                        0x00,
                        4 + block_len,
                        packet.packet_id) + encoded_block)

def decode(packet, provenance=PacketProvenance.server): # returns packets, trail
    buffer_len = len(packet)
    if buffer_len < 24:
        return [], packet
    header, packet_len, origin, padding, remaining, ptype = struct.unpack('<IIIIII', packet[:24])
    if header != 0xdeadbeef:
        raise ValueError("Incorrect packet header")
    if packet_len < 24:
        raise ValueError("Packet too short")
    if origin != provenance.value:
        raise ValueError("Incorrect packet origin field")
    if remaining != packet_len - 20:
        raise ValueError("Inconsistent packet length fields")
    if buffer_len < packet_len:
        return [], packet
    trailer = packet[packet_len:]
    payload = packet[24:packet_len]
    rest, trailer = decode(trailer)
    if ptype in PACKETS:
        # we know how to decode this one
        return [PACKETS[ptype].decode(payload)] + rest, trailer
    else:
        return rest, trailer

