import diana.packet as p
from nose.tools import *

def test_welcome_encode():
    wp = p.WelcomePacket('Welcome to eyes')
    encoding = p.encode(wp)
    eq_(encoding, b'\xef\xbe\xad\xde\x27\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00\xda\xb3\x04\x6dWelcome to eyes')

def test_welcome_decode():
    packet = b'\xef\xbe\xad\xde\x27\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00\xda\xb3\x04\x6dWelcome to eyes'
    decoded, trailer = p.decode(packet)
    eq_(len(decoded), 1)
    decoded = decoded[0]
    assert isinstance(decoded, p.WelcomePacket)
    eq_(decoded.message, 'Welcome to eyes')

def test_truncated_header():
    packet = b'\xef\xbe\xad\xde\x27\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00'
    decoded, trailer = p.decode(packet)
    eq_(decoded, [])
    eq_(trailer, packet)

def test_truncated_payload():
    packet = b'\xef\xbe\xad\xde\x27\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00\xda\xb3\x04\x6dWelcome to '
    decoded, trailer = p.decode(packet)
    eq_(decoded, [])
    eq_(trailer, packet)

def test_overflow_payload():
    packet = b'\xef\xbe\xad\xde\x27\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00\xda\xb3\x04\x6dWelcome to eyes\xef'
    decoded, trailer = p.decode(packet)
    eq_(trailer, b'\xef')

def test_double_decode():
    packet = b'\xef\xbe\xad\xde\x27\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00\xda\xb3\x04\x6dWelcome to eyes'
    packet = packet + packet
    decoded, trailer = p.decode(packet)
    eq_(len(decoded), 2)
    eq_(trailer, b'')

def test_version_encode():
    wp = p.VersionPacket(2, 1, 1)
    encoding = p.encode(wp)
    eq_(encoding, b'\xef\xbe\xad\xde\x2c\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x4a\xe7\x48\xe5\x00\x00\x00\x00ff\x06@\x02\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00')

def test_version_decode():
    packet = b'\xef\xbe\xad\xde\x2c\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x4a\xe7\x48\xe5\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00'
    decoded, trailer = p.decode(packet)
    eq_(len(decoded), 1)
    decoded = decoded[0]
    assert isinstance(decoded, p.VersionPacket)
    eq_(decoded.major, 2)
    eq_(decoded.minor, 1)
    eq_(decoded.patch, 1)

def test_difficulty_encode():
    dp = p.DifficultyPacket(5, p.GameType.deep_strike)
    eq_(dp.encode(), b'\x05\x00\x00\x00\x03\x00\x00\x00')

def test_difficulty_decode():
    dp = p.DifficultyPacket.decode(b'\x0a\x00\x00\x00\x02\x00\x00\x00')
    eq_(dp.difficulty, 10)
    eq_(dp.game_type, p.GameType.double_front)

def test_heartbeat_encode():
    hp = p.HeartbeatPacket()
    eq_(hp.encode(), b'')

def test_gm_start_encode():
    sp = p.GameStartPacket()
    eq_(sp.encode(), b'\x00\x00\x00\x00\x0a\x00\x00\x00\x00\x00\x00\x00')

def test_gm_start_decode():
    sp = p.GameMessagePacket.decode(b'\x00\x00\x00\x00\x0a\x00\x00\x00\xf6\x03\x00\x00')
    assert isinstance(sp, p.GameStartPacket)

def test_gm_end_encode():
    ep = p.GameEndPacket()
    eq_(ep.encode(), b'\x06\x00\x00\x00')

def test_gm_end_decode():
    ep = p.GameMessagePacket.decode(b'\x06\x00\x00\x00')
    assert isinstance(ep, p.GameEndPacket)

def test_intel_encode():
    ip = p.IntelPacket(object=0xaabbccdd, intel='bees')
    eq_(ip.encode(), b'\xdd\xcc\xbb\xaa\x03\x05\x00\x00\x00b\x00e\x00e\x00s\x00\x00\x00')

def test_intel_decode():
    ip = p.IntelPacket.decode(b'\xdd\xcc\xbb\xaa\x03\x05\x00\x00\x00b\x00e\x00e\x00s\x00\x00\x00')
    eq_(ip.object, 0xaabbccdd)
    eq_(ip.intel, 'bees')

def test_gm_popup_encode():
    pp = p.PopupPacket(message='bees')
    eq_(pp.encode(), b'\x0a\x00\x00\x00\x05\x00\x00\x00b\x00e\x00e\x00s\x00\x00\x00')

def test_gm_popup_decode():
    pp = p.GameMessagePacket.decode(b'\x0a\x00\x00\x00\x05\x00\x00\x00b\x00e\x00e\x00s\x00\x00\x00')
    assert isinstance(pp, p.PopupPacket)
    eq_(pp.message, 'bees')

