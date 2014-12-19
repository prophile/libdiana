import struct

ENCODERS = {}

def struct_encoder_for(char):
    format_expr = "<{}".format(char)
    def st_encode(fmt, data):
        if not data:
            raise ValueError("Not enough data")
        return (struct.pack(format_expr, data[0]) +
                encode(fmt[1:], data[1:]))
    return st_encode

for base_format in 'bBiIf':
    ENCODERS[base_format] = struct_encoder_for(base_format)
ENCODERS['s'] = struct_encoder_for('h')
ENCODERS['S'] = struct_encoder_for('H')

def encode_unicode_string(fmt, data):
    subject = data[0]
    block = subject.encode('utf-16le')
    output = struct.pack('<I', 1 + len(block)//2) + block + b'\x00\x00'
    return output + encode(fmt[1:], data[1:])
ENCODERS['u'] = encode_unicode_string

def encode_array(fmt, data):
    array_elements = data[0]
    stack_depth = 0
    for index, element in enumerate(fmt):
        if element == '[':
            stack_depth += 1
        elif element == ']':
            stack_depth -= 1
        if stack_depth == 0:
            end_index = index
            break
    else:
        raise ValueError('Bad format; unbalanced brackets')
    remainder_fmt = fmt[(end_index+1):]
    remaining_data = data[1:]
    remainder = encode(fmt[(end_index+1):], data[1:])
    this_fmt = fmt[1:end_index]
    return b''.join(encode(this_fmt, x) for x in array_elements) + remainder
ENCODERS['['] = encode_array

def encode(fmt, data):
    if not fmt:
        if data:
            raise ValueError('Too much data')
        return b''
    return ENCODERS[fmt[0]](fmt, data)

DECODERS = {}
def struct_decoder_for(char):
    format_expr = "<{}".format(char)
    expected_size = struct.calcsize(format_expr)
    def st_decode(fmt, data, handle_trail):
        if len(data) < expected_size:
            raise ValueError("Truncated data")
        decoded, = struct.unpack(format_expr, data[:expected_size])
        rest = decode(fmt[1:], data[expected_size:], handle_trail)
        return (decoded,) + rest
    return st_decode

for base_format in 'bBiIf':
    DECODERS[base_format] = struct_decoder_for(base_format)
DECODERS['s'] = struct_decoder_for('h')
DECODERS['S'] = struct_decoder_for('H')

def decode_unicode_string(fmt, data, handle_trail):
    if len(data) < 4:
        raise ValueError('Truncated data')
    str_len_padded, = struct.unpack('<I', data[:4])
    if str_len_padded == 0:
        raise ValueError('Zero-length string (no nul trailer?)')
    data = data[4:]
    if len(data) < (str_len_padded * 2):
        raise ValueError('Truncated data')
    str_len = str_len_padded - 1
    str_data = data[:(str_len * 2)].decode('utf-16le')
    data = data[(str_len*2):]
    if data[0] != 0 or data[1] != 0:
        raise ValueError('NUL trailer missing')
    return (str_data,) + decode(fmt[1:], data[2:], handle_trail)
DECODERS['u'] = decode_unicode_string

def decode_array(fmt, data, handle_trail):
    stack_depth = 0
    for index, element in enumerate(fmt):
        if element == '[':
            stack_depth += 1
        elif element == ']':
            stack_depth -= 1
        if stack_depth == 0:
            end_index = index
            break
    else:
        raise ValueError('Bad format; unbalanced brackets')
    remainder_fmt = fmt[(end_index+1):]
    this_fmt = fmt[1:end_index]
    print('Matching as many {0!r}'.format(this_fmt))
    matches = []
    try:
        def internal_handle_trail(trail):
            nonlocal data
            data = trail
            return ()
        while True:
            inner_decode = decode(this_fmt, data, handle_trail=internal_handle_trail)
            matches.append(inner_decode)
    except ValueError:
        pass
    return (matches,) + decode(remainder_fmt, data, handle_trail)
DECODERS['['] = decode_array

def handle_trail_error(trailer):
    if not trailer:
        return ()
    raise ValueError('Trailing bytes')

def decode(fmt, data, handle_trail=handle_trail_error):
    if fmt == '':
        return handle_trail(data)
    return DECODERS[fmt[0]](fmt, data, handle_trail)

