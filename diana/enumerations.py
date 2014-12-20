from enum import Enum
from collections import namedtuple

class PacketProvenance(Enum):
    server = 0x01
    client = 0x02

class GameType(Enum):
    siege = 0
    single_front = 1
    double_front = 2
    deep_strike = 3
    peacetime = 4
    border_war = 5

class Console(Enum):
    main_screen = 0
    helm = 1
    weapons = 2
    engineering = 3
    science = 4
    comms = 5
    data = 6
    observer = 7
    captain_map = 8
    game_master = 9

class ConsoleStatus(Enum):
    available = 0
    yours = 1
    unavailable = 2

class ObjectType(Enum):
    player_vessel = 1
    weapons_console = 2
    engineering_console = 3
    other_ship = 4
    base = 5
    mine = 6
    anomaly = 7
    nebula = 9
    torpedo = 10
    blackhole = 11
    asteroid = 12
    mesh = 13
    monster = 14
    whale = 15
    drone = 16

class DriveType(Enum):
    warp = 0
    jump = 1

class ShipType(Enum):
    light_cruiser = 0
    scout = 1
    battleship = 2
    missile_cruiser = 3
    dreadnought = 4

ShipSettingsRecord = namedtuple('ShipSettingsRecord', 'drive type name')

class MainView(Enum):
    forward = 0
    port = 1
    starboard = 2
    aft = 3
    tactical = 4
    lrs = 5
    status = 6

