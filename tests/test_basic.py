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

