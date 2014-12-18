import struct
from enum import Enum
import sys

class SoftDecodeFailure(RuntimeError):
    pass

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

    def __str__(self):
        return "<WelcomePacket {0!r}>".format(self.message)

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

    def __str__(self):
        return "<VersionPacket {}.{}.{}>".format(self.major, self.minor, self.patch)

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

    def __str__(self):
        return "<DifficultyPacket difficulty={} game_type={}>".format(self.difficulty, self.game_type)

@packet(0xf5821226)
class HeartbeatPacket:
    def encode(self):
        return b''

    @classmethod
    def decode(cls, packet):
        if packet != b'':
            raise ValueError('Payload in heartbeat')
        return cls()

    def __str__(self):
        return "<HeartbeatPacket>"

def pack_string(s):
    packed = s.encode('utf-16le') + b'\x00\x00'
    return struct.pack('<I', len(packed) // 2) + packed

def unpack_string(s):
    return s[4:-2].decode('utf-16le')

@packet(0xee665279)
class IntelPacket:
    def __init__(self, object, intel):
        self.object = object
        self.intel = intel

    def encode(self):
        return struct.pack('<Ib', self.object, 3) + pack_string(self.intel)

    @classmethod
    def decode(cls, packet):
        object, unknown_1 = struct.unpack('<Ib', packet[:5])
        intel = unpack_string(packet[5:])
        return cls(object, intel)

    def __str__(self):
        return '<IntelPacket object={0} intel={1!r}>'.format(self.object, self.intel)

@packet(0xf754c8fe)
class GameMessagePacket:
    @classmethod
    def decode(cls, packet):
        if not packet:
            raise ValueError('No payload in game message')
        subtype_index = packet[0]
        if subtype_index == 0:
            return GameStartPacket.decode(packet)
        if subtype_index == 6:
            return GameEndPacket.decode(packet)
        if subtype_index == 10:
            return PopupPacket.decode(packet)
        raise SoftDecodeFailure()

class GameStartPacket(GameMessagePacket):
    def encode(self):
        return b'\x00\x00\x00\x00\x0a\x00\x00\x00\x00\x00\x00\x00'

    @classmethod
    def decode(cls, packet):
        if len(packet) != 12:
            raise ValueError('Wrong packet length')
        return cls()

    def __str__(self):
        return '<GameStartPacket>'

class GameEndPacket(GameMessagePacket):
    def encode(self):
        return b'\x06\x00\x00\x00'

    @classmethod
    def decode(cls, packet):
        if len(packet) != 4:
            raise ValueError('Wrong packet length')
        return cls()

    def __str__(self):
        return '<GameEndPacket>'

class PopupPacket(GameMessagePacket):
    def __init__(self, message):
        self.message = message

    def encode(self):
        return b'\x0a\x00\x00\x00' + pack_string(self.message)

    @classmethod
    def decode(cls, packet):
        return cls(unpack_string(packet[4:]))

    def __str__(self):
        return '<PopupPacket message={0!r}>'.format(self.message)

@packet(0x0351a5ac)
class ShipAction3Packet:
    @classmethod
    def decode(cls, packet):
        if not packet:
            raise ValueError('No payload in game message')
        subtype_index = packet[0]
        if subtype_index == 0:
            return HelmSetImpulsePacket.decode(packet)
        if subtype_index == 1:
            return HelmSetSteeringPacket.decode(packet)
        raise SoftDecodeFailure()

class HelmSetSteeringPacket(ShipAction3Packet):
    def __init__(self, rudder):
        self.rudder = rudder

    def encode(self):
        return struct.pack('<If', 1, self.rudder)

    @classmethod
    def decode(cls, packet):
        _idx, rudder = struct.unpack('<If', packet)
        return cls(rudder)

    def __str__(self):
        return '<HelmSetSteeringPacket rudder={0!r}>'.format(self.rudder)

class HelmSetImpulsePacket(ShipAction3Packet):
    def __init__(self, impulse):
        self.impulse = impulse

    def encode(self):
        return struct.pack('<If', 0, self.impulse)

    @classmethod
    def decode(cls, packet):
        _idx, impulse = struct.unpack('<If', packet)
        return cls(impulse)

    def __str__(self):
        return '<HelmSetImpulsePacket impulse={0!r}>'.format(self.impulse)

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
    if not packet:
        return [], b''
    de_index = packet.find(0xef)
    if de_index > 0:
        sys.stderr.print("WARNING: skipping {} bytes of stream to resync\n".format(de_index))
        sys.stderr.flush()
        packet = packet[de_index:]
    elif de_index == -1:
        # wtf?
        return [], b''
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
        try:
            return [PACKETS[ptype].decode(payload)] + rest, trailer
        except SoftDecodeFailure: # meaning unhandled bits
            return rest, trailer
    else:
        return rest, trailer

