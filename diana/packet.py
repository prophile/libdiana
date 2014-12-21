import struct
import sys
import math
from .encoding import encode as base_pack, decode as unpack
from .object_update import decode_obj_update_packet
from .enumerations import *

def pack(fmt, *args):
    return base_pack(fmt, args)

class SoftDecodeFailure(RuntimeError):
    pass

PACKETS = {}

def packet(n):
    def wrapper(cls):
        PACKETS[n] = cls
        cls.packet_id = n
        return cls
    return wrapper

class UndecodedPacket:
    def __init__(self, packet_id, data):
        self.packet_id = packet_id
        self.data = data

    def encode(self):
        return self.data

    @classmethod
    def decode(cls, data):
        return cls(0, data)

    def __str__(self):
        return "<UndecodedPacket id=0x{0:08x} data={1!r}>".format(self.packet_id, self.data)

@packet(0x6d04b3da)
class WelcomePacket:
    def __init__(self, message=''):
        self.message = message

    def encode(self):
        encoded_message = self.message.encode('ascii')
        return struct.pack('<I', len(encoded_message)) + encoded_message

    @classmethod
    def decode(cls, packet):
        string_length, = struct.unpack('<I', packet[:4])
        decoded_message = packet[4:].decode('ascii')
        if string_length != len(decoded_message):
            raise ValueError('String length inconsistent with decoded length (should be {}, actually {})'.format(len(decoded_message), string_length))
        return cls(decoded_message)

    def __str__(self):
        return "<WelcomePacket {0!r}>".format(self.message)

@packet(0xe548e74a)
class VersionPacket:
    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch

    def encode(self):
        return pack('IfIII', 0,
                     float('{}.{}'.format(self.major, self.minor)),
                     self.major, self.minor, self.patch)

    @classmethod
    def decode(cls, packet):
        unknown_1, legacy_version, major, minor, patch = unpack('IfIII', packet)
        return cls(major, minor, patch)

    def __str__(self):
        return "<VersionPacket {}.{}.{}>".format(self.major, self.minor, self.patch)

@packet(0x3de66711)
class DifficultyPacket:
    def __init__(self, difficulty, game_type):
        self.difficulty = difficulty
        self.game_type = game_type

    def encode(self):
        return pack('II', self.difficulty, self.game_type.value)

    @classmethod
    def decode(cls, packet):
        difficulty, game_type_raw = unpack('II', packet)
        return cls(difficulty, GameType(game_type_raw))

    def __str__(self):
        return "<DifficultyPacket difficulty={} game_type={}>".format(self.difficulty, self.game_type)

@packet(0x19c6e2d4)
class ConsoleStatusPacket:
    def __init__(self, ship, consoles):
        self.consoles = {key: consoles.get(key, ConsoleStatus.available) for key in Console}
        self.ship = ship

    def encode(self):
        return pack('I[B]', self.ship,
                    [(self.consoles[console].value,) for console in Console])

    @classmethod
    def decode(cls, packet):
        ship, body = unpack('I[B]', packet)
        body = [x[0] for x in body]
        if len(body) != len(Console):
            raise ValueError("Incorrect console count ({}, should be {})".format(len(body), len(Console)))
        consoles = {console: ConsoleStatus(body[console.value]) for console in Console}
        return cls(ship, consoles)

    def __str__(self):
        return '<ConsoleStatusPacket ship={0} consoles={1!r}>'.format(self.ship,
                                                                      {console: status
                                                                         for console, status in self.consoles.items()
                                                                         if status != ConsoleStatus.available})

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

@packet(0xee665279)
class IntelPacket:
    def __init__(self, object, intel):
        self.object = object
        self.intel = intel

    def encode(self):
        return pack('Ibu', self.object, 3, self.intel)

    @classmethod
    def decode(cls, packet):
        object, _unk, intel = unpack('Ibu', packet)
        return cls(object, intel)

    def __str__(self):
        return '<IntelPacket object={0} intel={1!r}>'.format(self.object, self.intel)

@packet(0xd672c35f)
class CommsIncomingPacket:
    def __init__(self, priority, sender, message):
        self.priority = priority
        self.sender = sender
        self.message = message

    def encode(self):
        return pack('Iuu', self.priority, self.sender, self.message.replace('\n', '^'))

    @classmethod
    def decode(cls, packet):
        prio, sender, message = unpack('Iuu', packet)
        return cls(prio, sender, message.replace('^', '\n'))

    def __str__(self):
        return '<CommsIncomingPacket priority={0} sender={1!r} message={2!r}>'.format(self.priority, self.sender, self.message)

@packet(0x80803df9)
class ObjectUpdatePacket:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    @property
    def _records(self):
        return decode_obj_update_packet(self.raw_data)

    @property
    def records(self):
        try:
            return self._records
        except Exception:
            return []

    @classmethod
    def decode(cls, packet):
        if packet == b'\x00\x00\x00\x00':
            return NoisePacket()
        return cls(packet)

    def encode(self):
        return self.raw_data

    def __str__(self):
        try:
            records = repr(self._records)
            return '<ObjectUpdatePacket records={}>'.format(records)
        except Exception as e:
            return '<ObjectUpdatePacket data={0!r} error={1!r}>'.format(self.raw_data, e)

class NoisePacket:
    def __init__(self):
        self.packet_id = 0x80803df9

    def encode(self):
        return b'\x00\x00\x00\x00'

    def __str__(self):
        return '<NoisePacket>'

@packet(0xcc5a3e30)
class DestroyObjectPacket:
    def __init__(self, type, object):
        self.type = type
        self.object = object

    def encode(self):
        return pack('BI', self.type.value, self.object)

    @classmethod
    def decode(cls, packet):
        type, object = unpack('BI', packet)
        return cls(type=ObjectType(type), object=object)

    def __str__(self):
        return '<DestroyObjectPacket type={0!r} object={1!r}>'.format(self.type, self.object)

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
        if subtype_index == 9:
            return SkyboxPacket.decode(packet)
        if subtype_index == 10:
            return PopupPacket.decode(packet)
        if subtype_index == 11:
            return AutonomousDamconPacket.decode(packet)
        if subtype_index == 12:
            return JumpStartPacket.decode(packet)
        if subtype_index == 13:
            return JumpEndPacket.decode(packet)
        if subtype_index == 15:
            return AllShipSettingsPacket.decode(packet)
        if subtype_index == 16:
            return DmxPacket.decode(packet)
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

class AllShipSettingsPacket(GameMessagePacket):
    def __init__(self, ships):
        self.ships = list(ships)
        if len(self.ships) != 8:
            raise ValueError('Must be 8 ships, {} given'.format(len(self.ships)))

    def encode(self):
        return pack('I[IIIu]', 15,
                    [(ship.drive.value, ship.type.value, 1, ship.name)
                        for ship in self.ships])

    @classmethod
    def decode(cls, packet):
        _id, records = unpack('I[IIIu]', packet)
        return cls(ShipSettingsRecord(DriveType(drv), ShipType(typ), name)
                      for drv, typ, _what, name in records)

    def __str__(self):
        return '<AllShipSettingsPacket settings={0!r}>'.format(self.ships)

class JumpStartPacket(GameMessagePacket):
    def encode(self):
        return b'\x0c\x00\x00\x00'

    @classmethod
    def decode(cls, packet):
        if len(packet) != 4:
            raise ValueError('Wrong packet length')
        return cls()

    def __str__(self):
        return '<JumpStartPacket>'

class JumpEndPacket(GameMessagePacket):
    def encode(self):
        return b'\x0d\x00\x00\x00'

    @classmethod
    def decode(cls, packet):
        if len(packet) != 4:
            raise ValueError('Wrong packet length')
        return cls()

    def __str__(self):
        return '<JumpEndPacket>'

class DmxPacket(GameMessagePacket):
    def __init__(self, flag, state):
        self.flag = flag
        self.state = state

    def encode(self):
        return pack('IuI', 0x10, self.flag, int(self.state))

    @classmethod
    def decode(cls, packet):
        _id, flag, state = unpack('IuI', packet)
        return cls(flag, state)

    def __str__(self):
        return '<DmxPacket flag={0!r} state={1!r}>'.format(self.flag, self.state)

class SkyboxPacket(GameMessagePacket):
    def __init__(self, skybox):
        self.skybox = skybox

    def encode(self):
        return pack('II', 9, self.skybox)

    @classmethod
    def decode(cls, packet):
        _id, skybox = unpack('II', packet)
        return cls(skybox)

    def __str__(self):
        return '<SkyboxPacket skybox={0!r}>'.format(self.skybox)

class PopupPacket(GameMessagePacket):
    def __init__(self, message):
        self.message = message

    def encode(self):
        return pack('Iu', 0x0a, self.message)

    @classmethod
    def decode(cls, packet):
        _id, message = unpack('Iu', packet)
        return cls(message)

    def __str__(self):
        return '<PopupPacket message={0!r}>'.format(self.message)

class AutonomousDamconPacket(GameMessagePacket):
    def __init__(self, autonomy):
        self.autonomy = autonomy

    def encode(self):
        return pack('II', 0x0b, int(self.autonomy))

    @classmethod
    def decode(cls, packet):
        _id, autonomy = unpack('II', packet)
        return cls(bool(autonomy))

    def __str__(self):
        return '<AutonomousDamconPacket autonomy={0!r}>'.format(self.autonomy)

@packet(0x4c821d3c)
class ShipAction1Packet:
    @classmethod
    def decode(cls, packet):
        if not packet:
            raise ValueError('No payload in game message')
        subtype_index = packet[0]
        if subtype_index == 0:
            return HelmSetWarpPacket.decode(packet)
        if subtype_index == 1:
            return SetMainScreenPacket.decode(packet)
        if subtype_index == 2:
            return SetWeaponsTargetPacket.decode(packet)
        if subtype_index == 3:
            return ToggleAutoBeamsPacket.decode(packet)
        if subtype_index == 4:
            return ToggleShieldsPacket.decode(packet)
        if subtype_index == 7:
            return HelmRequestDockPacket.decode(packet)
        if subtype_index == 10:
            return ToggleRedAlertPacket.decode(packet)
        if subtype_index == 11:
            return SetBeamFreqPacket.decode(packet)
        if subtype_index == 13:
            return SetShipPacket.decode(packet)
        if subtype_index == 14:
            return SetConsolePacket.decode(packet)
        if subtype_index == 15:
            return ReadyPacket.decode(packet)
        if subtype_index == 16:
            return SciSelectPacket.decode(packet)
        if subtype_index == 18:
            return GameMasterSelectPacket.decode(packet)
        if subtype_index == 19:
            return SciScanPacket.decode(packet)
        if subtype_index == 22:
            return SetShipSettingsPacket.decode(packet)
        if subtype_index == 24:
            return HelmToggleReversePacket.decode(packet)
        if subtype_index == 25:
            return Ready2Packet.decode(packet)
        if subtype_index == 26:
            return TogglePerspectivePacket.decode(packet)
        if subtype_index == 27:
            return ClimbDivePacket.decode(packet)
        raise SoftDecodeFailure()

class SciScanPacket(ShipAction1Packet):
    def __init__(self, target):
        self.target = target

    def encode(self):
        return pack('II', 19, self.target)

    @classmethod
    def decode(cls, packet):
        _idx, tgt = unpack('II', packet)
        return cls(tgt)

    def __str__(self):
        return "<SciScanPacket target={0!r}>".format(self.target)

class GameMasterSelectPacket(ShipAction1Packet):
    def __init__(self, object):
        self.object = object

    def encode(self):
        if self.object is not None:
            return pack('II', 18, self.object)
        else:
            return pack('II', 18, 1)

    @classmethod
    def decode(cls, packet):
        _idx, tgt = unpack('II', packet)
        if tgt != 1:
            return cls(tgt)
        else:
            return cls(None)

    def __str__(self):
        return "<GameMasterSelectPacket object={0!r}>".format(self.object)

class SciSelectPacket(ShipAction1Packet):
    def __init__(self, object):
        self.object = object

    def encode(self):
        if self.object is not None:
            return pack('II', 16, self.object)
        else:
            return pack('II', 16, 1)

    @classmethod
    def decode(cls, packet):
        _idx, tgt = unpack('II', packet)
        if tgt != 1:
            return cls(tgt)
        else:
            return cls(None)

    def __str__(self):
        return "<SciSelectPacket object={0!r}>".format(self.object)

class SetWeaponsTargetPacket(ShipAction1Packet):
    def __init__(self, object):
        self.object = object

    def encode(self):
        if self.object is not None:
            return pack('II', 2, self.object)
        else:
            return pack('II', 2, 1)

    @classmethod
    def decode(cls, packet):
        _idx, tgt = unpack('II', packet)
        if tgt != 1:
            return cls(tgt)
        else:
            return cls(None)

    def __str__(self):
        return "<SetWeaponsTargetPacket object={0!r}>".format(self.object)

class SetBeamFreqPacket(ShipAction1Packet):
    def __init__(self, freq):
        self.freq = freq

    def encode(self):
        return pack('II', 11, self.freq)

    @classmethod
    def decode(cls, packet):
        _idx, freq = unpack('II', packet)
        return cls(freq)

    def __str__(self):
        return "<SetBeamFreqPacket freq={}>".format(self.freq)

class HelmToggleReversePacket(ShipAction1Packet):
    def encode(self):
        return b'\x18\x00\x00\x00\x00\x00\x00\x00'

    @classmethod
    def decode(cls, packet):
        if packet != b'\x18\x00\x00\x00\x00\x00\x00\x00':
            raise ValueError('Unexpected payload in reverse packet')
        return cls()

    def __str__(self):
        return '<HelmToggleReversePacket>'

class ReadyPacket(ShipAction1Packet):
    def encode(self):
        return b'\x0f\x00\x00\x00\x00\x00\x00\x00'

    @classmethod
    def decode(cls, packet):
        if packet != b'\x0f\x00\x00\x00\x00\x00\x00\x00':
            raise ValueError('Unexpected payload in ready packet')
        return cls()

    def __str__(self):
        return '<ReadyPacket>'

class Ready2Packet(ShipAction1Packet):
    def encode(self):
        return b'\x19\x00\x00\x00\x00\x00\x00\x00'

    @classmethod
    def decode(cls, packet):
        if packet != b'\x19\x00\x00\x00\x00\x00\x00\x00':
            raise ValueError('Unexpected payload in ready2 packet')
        return cls()

    def __str__(self):
        return '<Ready2Packet>'

class SetShipSettingsPacket(ShipAction1Packet):
    def __init__(self, drive, type, name):
        self.drive = drive
        self.type = type
        self.name = name

    def encode(self):
        return pack('IIIIu', 0x16, self.drive.value, self.type.value, 1, self.name)

    @classmethod
    def decode(cls, packet):
        _id, drv, typ, _unk, name = unpack('IIIIu', packet)
        return cls(drive=DriveType(drv),
                   type=ShipType(typ),
                   name=name)

    def __str__(self):
        return '<SetShipSettingsPacket drive={0!r} type={1!r} name={2!r}>'.format(self.drive, self.type, self.name)

class HelmRequestDockPacket(ShipAction1Packet):
    def encode(self):
        return b'\x07\x00\x00\x00\x00\x00\x00\x00'

    @classmethod
    def decode(cls, data):
        if data != b'\x07\x00\x00\x00\x00\x00\x00\x00':
            raise SoftDecodeFailure()
        return cls()

    def __str__(self):
        return '<HelmRequestDockPacket>'

class ToggleShieldsPacket(ShipAction1Packet):
    def encode(self):
        return b'\x04\x00\x00\x00\x00\x00\x00\x00'

    @classmethod
    def decode(cls, data):
        if data != b'\x04\x00\x00\x00\x00\x00\x00\x00':
            raise SoftDecodeFailure()
        return cls()

    def __str__(self):
        return '<ToggleShieldsPacket>'

class ToggleRedAlertPacket(ShipAction1Packet):
    def encode(self):
        return b'\x0a\x00\x00\x00\x00\x00\x00\x00'

    @classmethod
    def decode(cls, data):
        if data != b'\x0a\x00\x00\x00\x00\x00\x00\x00':
            raise SoftDecodeFailure()
        return cls()

    def __str__(self):
        return '<ToggleRedAlertPacket>'

class ToggleAutoBeamsPacket(ShipAction1Packet):
    def encode(self):
        return b'\x03\x00\x00\x00\x00\x00\x00\x00'

    @classmethod
    def decode(cls, data):
        if data != b'\x03\x00\x00\x00\x00\x00\x00\x00':
            raise SoftDecodeFailure()
        return cls()

    def __str__(self):
        return '<ToggleAutoBeamsPacket>'

class TogglePerspectivePacket(ShipAction1Packet):
    def encode(self):
        return b'\x1a\x00\x00\x00\x00\x00\x00\x00'

    @classmethod
    def decode(cls, data):
        if data != b'\x1a\x00\x00\x00\x00\x00\x00\x00':
            raise SoftDecodeFailure()
        return cls()

    def __str__(self):
        return '<TogglePerspectivePacket>'

class ClimbDivePacket(ShipAction1Packet):
    def __init__(self, direction):
        self.direction = direction

    def encode(self):
        return pack('Ii', 27, self.direction)

    @classmethod
    def decode(cls, packet):
        _id, direction = unpack('Ii', packet)
        return cls(direction)

    def __str__(self):
        return "<ClimbDivePacket direction={0!r}>".format(self.direction)

class SetMainScreenPacket(ShipAction1Packet):
    def __init__(self, screen):
        self.screen = screen

    def encode(self):
        return pack('II', 1, self.screen.value)

    @classmethod
    def decode(cls, packet):
        _idx, screen_id = unpack('II', packet)
        return cls(MainView(screen_id))

    def __str__(self):
        return "<SetMainScreenPacket screen={0!r}>".format(self.screen)

class SetConsolePacket(ShipAction1Packet):
    def __init__(self, console, selected):
        self.console = console
        self.selected = selected

    def encode(self):
        return pack('III', 0x0e, self.console.value, 1 if self.selected else 0)

    @classmethod
    def decode(cls, packet):
        _idx, console_id, selected = unpack('III', packet)
        return cls(Console(console_id), bool(selected))

    def __str__(self):
        return "<SetConsolePacket console={0!r} selected={1!r}>".format(self.console, self.selected)

class HelmSetWarpPacket(ShipAction1Packet):
    def __init__(self, warp):
        self.warp = warp

    def encode(self):
        return pack('II', 0, self.warp)

    @classmethod
    def decode(cls, packet):
        _idx, warp = unpack('II', packet)
        return cls(warp)

    def __str__(self):
        return "<HelmSetWarpPacket warp={}>".format(self.warp)

class SetShipPacket(ShipAction1Packet):
    def __init__(self, ship):
        self.ship = ship

    def encode(self):
        return pack('II', 0x0d, self.ship)

    @classmethod
    def decode(cls, packet):
        _idx, ship = unpack('II', packet)
        return cls(ship)

    def __str__(self):
        return "<SetShipPacket ship={}>".format(self.ship)

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
        if subtype_index == 5:
            return HelmJumpPacket.decode(packet)
        raise SoftDecodeFailure()

class HelmSetSteeringPacket(ShipAction3Packet):
    def __init__(self, rudder):
        self.rudder = rudder

    def encode(self):
        return pack('If', 1, self.rudder)

    @classmethod
    def decode(cls, packet):
        _idx, rudder = unpack('If', packet)
        return cls(rudder)

    def __str__(self):
        return '<HelmSetSteeringPacket rudder={0!r}>'.format(self.rudder)

class HelmSetImpulsePacket(ShipAction3Packet):
    def __init__(self, impulse):
        self.impulse = impulse

    def encode(self):
        return pack('If', 0, self.impulse)

    @classmethod
    def decode(cls, packet):
        _idx, impulse = unpack('If', packet)
        return cls(impulse)

    def __str__(self):
        return '<HelmSetImpulsePacket impulse={0!r}>'.format(self.impulse)

class HelmJumpPacket(ShipAction3Packet):
    def __init__(self, bearing, distance):
        self.bearing = bearing
        self.distance = distance

    def encode(self):
        return pack('Iff', 5, self.bearing / (math.pi * 2), self.distance / 50)

    @classmethod
    def decode(cls, packet):
        _idx, bearing, distance = unpack('Iff', packet)
        return cls(bearing * (math.pi * 2), distance * 50)

    def __str__(self):
        return '<HelmJumpPacket bearing={0!r} distance={1!r}>'.format(self.bearing, self.distance)

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
        sys.stderr.write("WARNING: skipping {} bytes of stream to resync\n".format(de_index))
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
    try:
        if ptype in PACKETS:
            # we know how to decode this one
            return [PACKETS[ptype].decode(payload)] + rest, trailer
        else:
            raise SoftDecodeFailure()
    except SoftDecodeFailure: # meaning unhandled bits
        return [UndecodedPacket(ptype, payload)] + rest, trailer

