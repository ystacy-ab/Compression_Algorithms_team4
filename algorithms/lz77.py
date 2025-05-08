def lz77_compress(input_data: bytes, window_size: int = 100) -> list[tuple[int, int, bytes]]:
    """Compress input data using the LZ77 algorithm."""
    i = 0
    compressed = []
    window = b""
    while i < len(input_data):
        distance = 0
        length = 0
        lookahead_buffer = input_data[i:]
        for j in range(1, len(lookahead_buffer) + 1):
            substring = lookahead_buffer[:j]
            pos = window.rfind(substring)
            if pos != -1:
                distance = len(window) - pos
                length = j
            else:
                break
        if length > 0:
            next_char = lookahead_buffer[length:length+1] if i + length < len(input_data) else b''
        else:
            next_char = input_data[i:i+1]
        compressed.append((distance, length, next_char))
        shift = length + 1
        window += input_data[i:i+shift]
        if len(window) > window_size:
            window = window[-window_size:]
        i += shift
    return compressed

def lz77_decompress(compressed: list[tuple[int, int, bytes]]) -> bytes:
    """Decompress LZ77-compressed data."""
    result = bytearray()
    for distance, length, char_bytes in compressed:
        if distance == 0 and length == 0:
            result.extend(char_bytes)
        else:
            start = len(result) - distance
            for i in range(length):
                result.append(result[start + i])
            result.extend(char_bytes)
    return bytes(result)
