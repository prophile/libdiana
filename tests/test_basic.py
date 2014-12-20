import diana.packet as p
from nose.tools import *
import time
import functools
from nose import SkipTest

def xfail(test):
    @functools.wraps(test)
    def inner(*args, **kwargs):
        try:
            test(*args, **kwargs)
        except Exception:
            raise SkipTest
        else:
            raise AssertionError('Failure expected')
    return inner

def test_undecoded_round_trip():
    packet = (b'\xef\xbe\xad\xde' # packet heading
              b'\x1c\x00\x00\x00' # total packet length
              b'\x02\x00\x00\x00' # origin
              b'\x00\x00\x00\x00' # padding
              b'\x08\x00\x00\x00' # remaining length
              b'\xdd\xcc\xbb\xaa' # packet type
              b'\xfe\x83\x4c\x00') # packet data
    decoded, rest = p.decode(packet, provenance=p.PacketProvenance.client)
    eq_(len(decoded), 1)
    eq_(rest, b'')
    encoded = p.encode(decoded[0], provenance=p.PacketProvenance.client)
    eq_(packet, encoded)

def test_welcome_encode():
    wp = p.WelcomePacket('Welcome to eyes')
    encoding = p.encode(wp)
    eq_(encoding, b'\xef\xbe\xad\xde+\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x17\x00\x00\x00\xda\xb3\x04m\x0f\x00\x00\x00Welcome to eyes')

def test_welcome_decode():
    packet = b'\xef\xbe\xad\xde+\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x17\x00\x00\x00\xda\xb3\x04m\x0f\x00\x00\x00Welcome to eyes'
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
    packet = b'\xef\xbe\xad\xde+\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x17\x00\x00\x00\xda\xb3\x04m\x0f\x00\x00\x00Welcome to eyes\xef'
    decoded, trailer = p.decode(packet)
    eq_(trailer, b'\xef')

def test_double_decode():
    packet = b'\xef\xbe\xad\xde+\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x17\x00\x00\x00\xda\xb3\x04m\x0f\x00\x00\x00Welcome to eyes'
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

def test_gm_dmx_encode():
    dp = p.DmxPacket(flag='bees', state=True)
    eq_(dp.encode(), b'\x10\x00\x00\x00\x05\x00\x00\x00b\x00e\x00e\x00s\x00\x00\x00\x01\x00\x00\x00')

def test_gm_dmx_decode():
    dp = p.GameMessagePacket.decode(b'\x10\x00\x00\x00\x02\x00\x00\x00y\x00\x00\x00\x00\x00\x00\x00')
    assert isinstance(dp, p.DmxPacket)
    eq_(dp.flag, 'y')
    eq_(dp.state, False)

def test_gm_jump_start_encode():
    ep = p.JumpStartPacket()
    eq_(ep.encode(), b'\x0c\x00\x00\x00')

def test_gm_jump_start_decode():
    ep = p.GameMessagePacket.decode(b'\x0c\x00\x00\x00')
    assert isinstance(ep, p.JumpStartPacket)

GM_ALL_SHIPS_PACKET = b'\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x08\x00\x00\x00A\x00r\x00t\x00e\x00m\x00i\x00s\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\t\x00\x00\x00I\x00n\x00t\x00r\x00e\x00p\x00i\x00d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x06\x00\x00\x00A\x00e\x00g\x00i\x00s\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x08\x00\x00\x00H\x00o\x00r\x00a\x00t\x00i\x00o\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\n\x00\x00\x00E\x00x\x00c\x00a\x00l\x00i\x00b\x00u\x00r\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x05\x00\x00\x00H\x00e\x00r\x00a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x06\x00\x00\x00C\x00e\x00r\x00e\x00s\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x06\x00\x00\x00D\x00i\x00a\x00n\x00a\x00\x00\x00'

def test_gm_all_ship_encode():
    ShipSettingsRecord = p.ShipSettingsRecord
    DriveType = p.DriveType
    ShipType = p.ShipType
    ships = [ShipSettingsRecord(drive=DriveType.warp,
                                type=ShipType.light_cruiser,
                                name='Artemis'),
             ShipSettingsRecord(drive=DriveType.warp,
                                type=ShipType.light_cruiser,
                                name='Intrepid'),
             ShipSettingsRecord(drive=DriveType.warp,
                                type=ShipType.light_cruiser,
                                name='Aegis'),
             ShipSettingsRecord(drive=DriveType.warp,
                                type=ShipType.light_cruiser,
                                name='Horatio'),
             ShipSettingsRecord(drive=DriveType.warp,
                                type=ShipType.light_cruiser,
                                name='Excalibur'),
             ShipSettingsRecord(drive=DriveType.warp,
                                type=ShipType.light_cruiser,
                                name='Hera'),
             ShipSettingsRecord(drive=DriveType.warp,
                                type=ShipType.light_cruiser,
                                name='Ceres'),
             ShipSettingsRecord(drive=DriveType.warp,
                                type=ShipType.light_cruiser,
                                name='Diana')]
    data = p.AllShipSettingsPacket(ships).encode()
    eq_(data, GM_ALL_SHIPS_PACKET)

def test_gm_all_ship_decode():
    packet = p.GameMessagePacket.decode(GM_ALL_SHIPS_PACKET)
    assert isinstance(packet, p.AllShipSettingsPacket)
    eq_(packet.ships[7].name, 'Diana')

def test_gm_skybox_encode():
    sp = p.SkyboxPacket(6)
    eq_(sp.encode(), b'\x09\x00\x00\x00\x06\x00\x00\x00')

def test_gm_skybox_decode():
    sp = p.GameMessagePacket.decode(b'\x09\x00\x00\x00\xff\xff\xff\xff')
    assert isinstance(sp, p.SkyboxPacket)
    eq_(sp.skybox, 0xffffffff)

def test_gm_jump_end_encode():
    ep = p.JumpEndPacket()
    eq_(ep.encode(), b'\x0d\x00\x00\x00')

def test_gm_jump_end_decode():
    ep = p.GameMessagePacket.decode(b'\x0d\x00\x00\x00')
    assert isinstance(ep, p.JumpEndPacket)

def test_intel_encode():
    ip = p.IntelPacket(object=0xaabbccdd, intel='bees')
    eq_(ip.encode(), b'\xdd\xcc\xbb\xaa\x03\x05\x00\x00\x00b\x00e\x00e\x00s\x00\x00\x00')

def test_intel_decode():
    ip = p.IntelPacket.decode(b'\xdd\xcc\xbb\xaa\x03\x05\x00\x00\x00b\x00e\x00e\x00s\x00\x00\x00')
    eq_(ip.object, 0xaabbccdd)
    eq_(ip.intel, 'bees')

def test_comms_encode():
    cp = p.CommsIncomingPacket(priority=3, sender='x', message='y\nz')
    eq_(cp.encode(), b'\x03\x00\x00\x00\x02\x00\x00\x00x\x00\x00\x00\x04\x00\x00\x00y\x00^\x00z\x00\x00\x00')

def test_comms_decode():
    cp = p.CommsIncomingPacket.decode(b'\x01\x00\x00\x00\x02\x00\x00\x00x\x00\x00\x00\x04\x00\x00\x00y\x00^\x00z\x00\x00\x00')
    eq_(cp.priority, 1)
    eq_(cp.sender, 'x')
    eq_(cp.message, 'y\nz')

def test_gm_popup_encode():
    pp = p.PopupPacket(message='bees')
    eq_(pp.encode(), b'\x0a\x00\x00\x00\x05\x00\x00\x00b\x00e\x00e\x00s\x00\x00\x00')

def test_gm_popup_decode():
    pp = p.GameMessagePacket.decode(b'\x0a\x00\x00\x00\x05\x00\x00\x00b\x00e\x00e\x00s\x00\x00\x00')
    assert isinstance(pp, p.PopupPacket)
    eq_(pp.message, 'bees')

def test_gm_autonomous_damcon_encode():
    dp = p.AutonomousDamconPacket(autonomy=True)
    eq_(dp.encode(), b'\x0b\x00\x00\x00\x01\x00\x00\x00')

def test_gm_autonomous_damcon_decode():
    pp = p.GameMessagePacket.decode(b'\x0b\x00\x00\x00\x00\x00\x00\x00')
    assert isinstance(pp, p.AutonomousDamconPacket)
    eq_(pp.autonomy, False)

def test_steering_encode():
    pp = p.HelmSetSteeringPacket(0.0)
    eq_(pp.encode(), b'\x01\x00\x00\x00\x00\x00\x00\x00')

def test_steering_decode():
    pp = p.ShipAction3Packet.decode(b'\x01\x00\x00\x00\x00\x00\x00\x00')
    assert isinstance(pp, p.HelmSetSteeringPacket)
    eq_(pp.rudder, 0.0)

def test_impulse_encode():
    pp = p.HelmSetImpulsePacket(0.0)
    eq_(pp.encode(), b'\x00\x00\x00\x00\x00\x00\x00\x00')

def test_impulse_decode():
    pp = p.ShipAction3Packet.decode(b'\x00\x00\x00\x00\x00\x00\x00\x00')
    assert isinstance(pp, p.HelmSetImpulsePacket)
    eq_(pp.impulse, 0.0)

def test_jump_encode():
    pp = p.HelmJumpPacket(3.1415, 35.0)
    eq_(pp.encode(), b'\x04\x00\x00\x00\x11\xfe\xff>333?')

def test_jump_decode():
    pp = p.ShipAction3Packet.decode(b'\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    assert isinstance(pp, p.HelmJumpPacket)
    eq_(pp.bearing, 0.0)
    eq_(pp.distance, 0.0)

def test_warp_encode():
    pp = p.HelmSetWarpPacket(2)
    eq_(pp.encode(), b'\x00\x00\x00\x00\x02\x00\x00\x00')

def test_warp_decode():
    pp = p.ShipAction1Packet.decode(b'\x00\x00\x00\x00\x02\x00\x00\x00')
    assert isinstance(pp, p.HelmSetWarpPacket)
    eq_(pp.warp, 2)

def test_ra_encode():
    rp = p.ToggleRedAlertPacket()
    eq_(rp.encode(), b'\x0a\x00\x00\x00\x00\x00\x00\x00')

def test_ra_decode():
    rp = p.ShipAction1Packet.decode(b'\x0a\x00\x00\x00\x00\x00\x00\x00')
    assert isinstance(rp, p.ToggleRedAlertPacket)

def test_shields_encode():
    rp = p.ToggleShieldsPacket()
    eq_(rp.encode(), b'\x04\x00\x00\x00\x00\x00\x00\x00')

def test_shields_decode():
    rp = p.ShipAction1Packet.decode(b'\x04\x00\x00\x00\x00\x00\x00\x00')
    assert isinstance(rp, p.ToggleShieldsPacket)

def test_perspective_encode():
    rp = p.TogglePerspectivePacket()
    eq_(rp.encode(), b'\x1a\x00\x00\x00\x00\x00\x00\x00')

def test_perspective_decode():
    rp = p.ShipAction1Packet.decode(b'\x1a\x00\x00\x00\x00\x00\x00\x00')
    assert isinstance(rp, p.TogglePerspectivePacket)

def test_auto_beams_encode():
    rp = p.ToggleAutoBeamsPacket()
    eq_(rp.encode(), b'\x03\x00\x00\x00\x00\x00\x00\x00')

def test_auto_beams_decode():
    rp = p.ShipAction1Packet.decode(b'\x03\x00\x00\x00\x00\x00\x00\x00')
    assert isinstance(rp, p.ToggleAutoBeamsPacket)

def test_pitch_encode():
    pp = p.ClimbDivePacket(-1)
    eq_(pp.encode(), b'\x1b\x00\x00\x00\xff\xff\xff\xff')

def test_pitch_decode():
    pp = p.ShipAction1Packet.decode(b'\x1b\x00\x00\x00\xff\xff\xff\xff')
    assert isinstance(pp, p.ClimbDivePacket)
    eq_(pp.direction, -1)

def test_main_screen_encode():
    pp = p.SetMainScreenPacket(p.MainView.aft)
    eq_(pp.encode(), b'\x01\x00\x00\x00\x03\x00\x00\x00')

def test_main_screen_decode():
    pp = p.ShipAction1Packet.decode(b'\x01\x00\x00\x00\x02\x00\x00\x00')
    assert isinstance(pp, p.SetMainScreenPacket)
    eq_(pp.screen, p.MainView.starboard)

def test_set_ship_encode():
    pp = p.SetShipPacket(4)
    eq_(pp.encode(), b'\x0d\x00\x00\x00\x04\x00\x00\x00')

def test_set_ship_decode():
    pp = p.ShipAction1Packet.decode(b'\x0d\x00\x00\x00\x07\x00\x00\x00')
    assert isinstance(pp, p.SetShipPacket)
    eq_(pp.ship, 7)

def test_console_encode():
    pp = p.SetConsolePacket(p.Console.data, True)
    eq_(pp.encode(), b'\x0e\x00\x00\x00\x06\x00\x00\x00\x01\x00\x00\x00')

def test_console_decode():
    pp = p.ShipAction1Packet.decode(b'\x0e\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00')
    assert isinstance(pp, p.SetConsolePacket)
    eq_(pp.console, p.Console.science)
    eq_(pp.selected, False)

def test_dock_encode():
    pp = p.HelmRequestDockPacket()
    eq_(pp.encode(), b'\x07\x00\x00\x00\x00\x00\x00\x00')

def test_dock_decode():
    pp = p.ShipAction1Packet.decode(b'\x07\x00\x00\x00\x00\x00\x00\x00')
    assert isinstance(pp, p.HelmRequestDockPacket)

def test_ship_settings_encode():
    sp = p.SetShipSettingsPacket(drive=p.DriveType.jump, type=p.ShipType.battleship, name='Art')
    eq_(sp.encode(), b'\x16\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00A\x00r\x00t\x00\x00\x00')

def test_ship_settings_decode():
    sp = p.ShipAction1Packet.decode(b'\x16\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00A\x00r\x00t\x00\x00\x00')
    assert isinstance(sp, p.SetShipSettingsPacket)
    eq_(sp.drive, p.DriveType.jump)
    eq_(sp.type, p.ShipType.battleship)
    eq_(sp.name, 'Art')

def test_cs_encode():
    cp = p.ConsoleStatusPacket(2, {p.Console.helm: p.ConsoleStatus.yours, p.Console.weapons: p.ConsoleStatus.unavailable})
    eq_(cp.encode(), b'\x02\x00\x00\x00\x00\x01\x02\x00\x00\x00\x00\x00\x00\x00')

def test_cs_decode():
    cp = p.ConsoleStatusPacket.decode(b'\x02\x00\x00\x00\x00\x01\x02\x00\x00\x00\x00\x00\x00\x00')
    eq_(cp.ship, 2)
    eq_(cp.consoles[p.Console.helm], p.ConsoleStatus.yours)
    eq_(cp.consoles[p.Console.weapons], p.ConsoleStatus.unavailable)
    eq_(cp.consoles[p.Console.data], p.ConsoleStatus.available)

def test_destroy_encode():
    dp = p.DestroyObjectPacket(type=p.ObjectType.blackhole,
                               object=0xaabbccdd)
    eq_(dp.encode(), b'\x0b\xdd\xcc\xbb\xaa')

def test_destroy_decode():
    dp = p.DestroyObjectPacket.decode(b'\x0b\xdd\xcc\xbb\xaa')
    assert isinstance(dp, p.DestroyObjectPacket)
    eq_(dp.type, p.ObjectType.blackhole)
    eq_(dp.object, 0xaabbccdd)

