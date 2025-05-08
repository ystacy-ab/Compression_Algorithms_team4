def lzw_encode(data: bytes) -> list[int]:
    table = {bytes([i]): i for i in range(256)}
    next_code = 256
    P = bytes([data[0]])
    result = []

    for byte in data[1:]:
        C = bytes([byte])
        if P + C in table:
            P = P + C
        else:
            result.append(table[P])
            table[P + C] = next_code
            next_code += 1
            P = C

    result.append(table[P])
    return result


def lzw_decode(codes: list[int]) -> bytes:
    table = {i: bytes([i]) for i in range(256)}
    next_code = 256
    OLD = codes[0]
    S = table[OLD]
    result = bytearray(S)
    C = S[:1]

    for NEW in codes[1:]:
        if NEW not in table:
            S = table[OLD] + C
        else:
            S = table[NEW]
        result += S
        C = S[:1]
        table[next_code] = table[OLD] + C
        next_code += 1
        OLD = NEW

    return bytes(result)
