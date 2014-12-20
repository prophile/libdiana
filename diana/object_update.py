from .encoding import decode as unpack
from .enumerations import *

def unscramble_elites(field):
    return {ability for ability in EliteAbility
              if ability.value & field}

def decode_obj_update_packet(packet):
    entries = []
    while packet:
        update_type = packet[0]
        obj = {}
        if update_type == 0x00:
            break
        elif update_type == 0x01:
            _id, oid, fields_1, fields_2, fields_3, fields_4, fields_5, packet = unpack('BIBBBBB*', packet)
            obj['object'] = oid
            obj['type'] = ObjectType.player_vessel
            if fields_1 & 0x01:
                obj['tgt-weapons'], packet = unpack('I*', packet)
            if fields_1 & 0x02:
                obj['impulse'], packet = unpack('f*', packet)
            if fields_1 & 0x04:
                obj['rudder'], packet = unpack('f*', packet)
            if fields_1 & 0x08:
                obj['top-speed'], packet = unpack('f*', packet)
            if fields_1 & 0x10:
                obj['turn-rate'], packet = unpack('f*', packet)
            if fields_1 & 0x20:
                ab, packet = unpack('B*', packet)
                obj['auto-beams'] = bool(ab)
            if fields_1 & 0x40:
                obj['warp'], packet = unpack('B*', packet)
            if fields_1 & 0x80:
                obj['energy'], packet = unpack('f*', packet)
            if fields_2 & 0x01:
                obj['shields-state'], packet = unpack('s*', packet)
            if fields_2 & 0x02:
                obj['index'], packet = unpack('I*', packet)
            if fields_2 & 0x04:
                obj['vtype'], packet = unpack('I*', packet)
            if fields_2 & 0x08:
                obj['x'], packet = unpack('f*', packet)
            if fields_2 & 0x10:
                obj['y'], packet = unpack('f*', packet)
            if fields_2 & 0x20:
                obj['z'], packet = unpack('f*', packet)
            if fields_2 & 0x40:
                obj['pitch'], packet = unpack('f*', packet)
            if fields_2 & 0x80:
                obj['roll'], packet = unpack('f*', packet)
            if fields_3 & 0x01:
                obj['heading'], packet = unpack('f*', packet)
            if fields_3 & 0x02:
                obj['speed'], packet = unpack('f*', packet)
            if fields_3 & 0x04:
                _unk, packet = unpack('S*', packet)
            if fields_3 & 0x08:
                obj['name'], packet = unpack('u*', packet)
            if fields_3 & 0x10:
                obj['shields'], packet = unpack('f*', packet)
            if fields_3 & 0x20:
                obj['shields-max'], packet = unpack('f*', packet)
            if fields_3 & 0x40:
                obj['shields-aft'], packet = unpack('f*', packet)
            if fields_3 & 0x80:
                obj['shields-aft-max'], packet = unpack('f*', packet)
            if fields_4 & 0x01:
                obj['docked'], packet = unpack('I*', packet)
            if fields_4 & 0x02:
                red_alert, packet = unpack('B*', packet)
                obj['red-alert'] = bool(red_alert)
            if fields_4 & 0x04:
                packet = packet[4:]
            if fields_4 & 0x08:
                ms, packet = unpack('B*', packet)
                obj['main-view'] = MainView(ms)
            if fields_4 & 0x10:
                obj['beam-frequency'], packet = unpack('B*', packet)
            if fields_4 & 0x20:
                obj['coolant-avail'], packet = unpack('B*', packet)
            if fields_4 & 0x40:
                obj['tgt-science'], packet = unpack('I*', packet)
            if fields_4 & 0x80:
                obj['tgt-captain'], packet = unpack('I*', packet)
            if fields_5 & 0x01:
                dt, packet = unpack('B*', packet)
                obj['drive-type'] = DriveType(dt)
            if fields_5 & 0x02:
                obj['tgt-scan'], packet = unpack('I*', packet)
            if fields_5 & 0x04:
                obj['scan-progress'], packet = unpack('f*', packet)
            if fields_5 & 0x08:
                rv, packet = unpack('B*', packet)
                obj['reverse'] = bool(rv)
            if fields_5 & 0x10:
                packet = packet[4:]
            if fields_5 & 0x20:
                packet = packet[1:]
            if fields_5 & 0x40:
                packet = packet[4:]
            if fields_5 & 0x80:
                raise ValueError('Unknown data keys for player vessel')
        elif update_type == 0x04:
            _id, oid, fields_1, fields_2, fields_3, fields_4, fields_5, fields_6, packet = unpack('BIBBBBBB*', packet)
            obj['object'] = oid
            obj['type'] = ObjectType.other_ship
            if fields_1 & 0x01:
                obj['name'], packet = unpack('u*', packet)
            if fields_1 & 0x02:
                packet = packet[4:]
            if fields_1 & 0x04:
                obj['rudder'], packet = unpack('f*', packet)
            if fields_1 & 0x08:
                obj['max-impulse'], packet = unpack('f*', packet)
            if fields_1 & 0x10:
                obj['max-turn-rate'], packet = unpack('f*', packet)
            if fields_1 & 0x20:
                fef, packet = unpack('I*', packet)
                obj['iff-friendly'] = not bool(fef)
            if fields_1 & 0x40:
                obj['vtype'], packet = unpack('I*', packet)
            if fields_1 & 0x80:
                obj['x'], packet = unpack('f*', packet)
            if fields_2 & 0x01:
                obj['y'], packet = unpack('f*', packet)
            if fields_2 & 0x02:
                obj['z'], packet = unpack('f*', packet)
            if fields_2 & 0x04:
                obj['pitch'], packet = unpack('f*', packet)
            if fields_2 & 0x08:
                obj['roll'], packet = unpack('f*', packet)
            if fields_2 & 0x10:
                obj['heading'], packet = unpack('f*', packet)
            if fields_2 & 0x20:
                obj['speed'], packet = unpack('f*', packet)
            if fields_2 & 0x40:
                surr, packet = unpack('B*', packet)
                obj['surrender'] = bool(surr)
            if fields_2 & 0x80:
                packet = packet[2:]
            if fields_3 & 0x01:
                obj['shields'], packet = unpack('f*', packet)
            if fields_3 & 0x02:
                obj['shields-max'], packet = unpack('f*', packet)
            if fields_3 & 0x04:
                obj['shields-aft'], packet = unpack('f*', packet)
            if fields_3 & 0x08:
                obj['shields-aft-max'], packet = unpack('f*', packet)
            if fields_3 & 0x10:
                packet = packet[2:]
            if fields_3 & 0x20:
                packet = packet[1:]
            if fields_3 & 0x40:
                elt, packet = unpack('I*', packet)
                obj['elite'] = unscramble_elites(elt)
            if fields_3 & 0x80:
                elt, packet = unpack('I*', packet)
                obj['elite-active'] = unscramble_elites(elt)
            if fields_4 & 0x01:
                scn, packet = unpack('I*', packet)
                obj['scanned'] = bool(scn)
            if fields_4 & 0x02:
                obj['iff-side'], packet = unpack('I*', packet)
            if fields_4 & 0x04:
                packet = packet[4:]
            if fields_4 & 0x08:
                packet = packet[1:]
            if fields_4 & 0x10:
                packet = packet[1:]
            if fields_4 & 0x20:
                packet = packet[1:]
            if fields_4 & 0x40:
                packet = packet[1:]
            if fields_4 & 0x80:
                packet = packet[4:]
            if fields_5 & 0x01:
                packet = packet[4:]
            if fields_5 & 0x02:
                packet = packet[4:]
            if fields_5 & 0x04:
                obj['damage-beams'], packet = unpack('f*', packet)
            if fields_5 & 0x08:
                obj['damage-tubes'], packet = unpack('f*', packet)
            if fields_5 & 0x10:
                obj['damage-sensors'], packet = unpack('f*', packet)
            if fields_5 & 0x20:
                obj['damage-maneuvering'], packet = unpack('f*', packet)
            if fields_5 & 0x40:
                obj['damage-impulse'], packet = unpack('f*', packet)
            if fields_5 & 0x80:
                obj['damage-warp'], packet = unpack('f*', packet)
            if fields_6 & 0x01:
                obj['damage-shields'], packet = unpack('f*', packet)
            if fields_6 & 0x02:
                obj['damage-shields'], packet = unpack('f*', packet)
            if fields_6 & 0x04:
                obj['shields-0'], packet = unpack('f*', packet)
            if fields_6 & 0x08:
                obj['shields-1'], packet = unpack('f*', packet)
            if fields_6 & 0x10:
                obj['shields-2'], packet = unpack('f*', packet)
            if fields_6 & 0x20:
                obj['shields-3'], packet = unpack('f*', packet)
            if fields_6 & 0x40:
                obj['shields-4'], packet = unpack('f*', packet)
            if fields_6 & 0x80:
                raise ValueError('Unknown data key for NPC')
        elif update_type == 0x05:
            _id, oid, fields_1, fields_2, packet = unpack('BIBB*', packet)
            obj['object'] = oid
            obj['type'] = ObjectType.base
            if fields_1 & 0x01:
                obj['name'], packet = unpack('u*', packet)
            if fields_1 & 0x02:
                obj['shields'], packet = unpack('f*', packet)
            if fields_1 & 0x04:
                obj['shields-aft'], packet = unpack('f*', packet)
            if fields_1 & 0x08:
                obj['index'], packet = unpack('I*', packet)
            if fields_1 & 0x10:
                obj['vtype'], packet = unpack('I*', packet)
            if fields_1 & 0x20:
                obj['x'], packet = unpack('f*', packet)
            if fields_1 & 0x40:
                obj['y'], packet = unpack('f*', packet)
            if fields_1 & 0x80:
                obj['z'], packet = unpack('f*', packet)
            if fields_2 & 0x01:
                packet = packet[4:]
            if fields_2 & 0x02:
                packet = packet[4:]
            if fields_2 & 0x04:
                packet = packet[4:]
            if fields_2 & 0x08:
                packet = packet[4:]
            if fields_2 & 0x10:
                packet = packet[1:]
            if fields_2 & 0x20:
                packet = packet[1:]
            if fields_2 & 0xc0:
                raise ValueError('Unknown data keys for base')
        elif update_type == 0x06:
            _id, oid, fields, packet = unpack('BIB*', packet)
            obj['object'] = oid
            obj['type'] = ObjectType.mine
            if fields & 0x01:
                obj['x'] = unpack('f*', packet)
            if fields & 0x02:
                obj['y'] = unpack('f*', packet)
            if fields & 0x04:
                obj['z'] = unpack('f*', packet)
            if fields & 0x08:
                packet = packet[4:]
            if fields & 0x10:
                packet = packet[4:]
            if fields & 0x20:
                packet = packet[4:]
            if fields & 0x40:
                packet = packet[4:]
            if fields & 0x80:
                packet = packet[4:]
        elif update_type == 0x07:
            _id, oid, fields, packet = unpack('BIB*', packet)
            obj['object'] = oid
            obj['type'] = ObjectType.anomaly
            if fields & 0x01:
                obj['x'] = unpack('f*', packet)
            if fields & 0x02:
                obj['y'] = unpack('f*', packet)
            if fields & 0x04:
                obj['z'] = unpack('f*', packet)
            if fields & 0x08:
                obj['name'], packet = unpack('u*', packet)
            if fields & 0x10:
                packet = packet[4:]
            if fields & 0x20:
                packet = packet[4:]
            if fields & 0x40:
                packet = packet[4:]
            if fields & 0x80:
                packet = packet[4:]
        elif update_type == 0x09:
            _id, oid, fields, packet = unpack('BIB*', packet)
            obj['object'] = oid
            obj['type'] = ObjectType.nebula
            if fields & 0x01:
                obj['x'], packet = unpack('f*', packet)
            if fields & 0x02:
                obj['y'], packet = unpack('f*', packet)
            if fields & 0x04:
                obj['z'], packet = unpack('f*', packet)
            if fields & 0x08:
                obj['red'], packet = unpack('f*', packet)
            if fields & 0x10:
                obj['green'], packet = unpack('f*', packet)
            if fields & 0x20:
                obj['blue'], packet = unpack('f*', packet)
            if fields & 0x40:
                packet = packet[4:]
            if fields & 0x80:
                packet = packet[4:]
        else:
            raise ValueError('Unknown object type {}'.format(update_type))
        entries.append(obj)
    return entries

