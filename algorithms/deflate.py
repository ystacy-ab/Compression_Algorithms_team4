"""
DEFLATE.PY
"""

import heapq
import pickle
from datetime import datetime

#COMPRESS

def compress_lz77(data: bytes, window_size: int =4096, lookahead: int =15) -> list[int | tuple[int, int]]:
    """
    Compresses using lz77.
    """
    compressed = []
    i = 0
    n = len(data)
    hash_table = {}

    while i < n:
        best_len = 0
        best_dist = 0
        max_len = min(lookahead, n - i)
        if i + 2 < n:
            key = (data[i], data[i+1])
            for j in hash_table.get(key, []):
                if i - j > window_size:
                    continue
                length = 0
                while length < max_len and data[j + length] == data[i + length]:
                    length += 1
                if length > best_len:
                    best_len = length
                    best_dist = i - j
            hash_table.setdefault(key, []).append(i)

        if best_len >= 3:
            compressed.append((best_dist, best_len))
            i += best_len
        else:
            compressed.append(data[i])
            i += 1
    return compressed

def lz77_to_bytes(compressed: list[tuple[int, int] | int]) -> bytearray:
    """
    converts lz77 to bytes.
    """
    output = bytearray()
    for item in compressed:
        if isinstance(item, tuple):
            output.append(0)
            output.append((item[0] >> 8) & 0xFF)
            output.append(item[0] & 0xFF)
            output.append(item[1])
        else:
            output.append(1)
            output.append(item)
    return output

class Node:
    """
    Node for Huffman tree.
    """
    def __init__(self, symbol=None, freq=0):
        self.symbol = symbol
        self.freq = freq
        self.left = None
        self.right = None
    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(data: bytes) -> Node:
    """
    builds huffman tree.
    """
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    heap = [Node(sym, f) for sym, f in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        l = heapq.heappop(heap)
        r = heapq.heappop(heap)
        m = Node(freq=l.freq + r.freq)
        m.left = l
        m.right = r
        heapq.heappush(heap, m)
    return heap[0]

def make_codes(node: Node, prefix: str = "", table: dict | None = None) -> dict[int, str]:
    """
    Creates Huffman code tablet.
    """
    if table is None:
        table = {}
    if node.symbol is not None:
        table[node.symbol] = prefix
    else:
        make_codes(node.left, prefix + "0", table)
        make_codes(node.right, prefix + "1", table)
    return table

def huffman_compress(data: bytes) -> str:
    """
    Codes data using Huffman tablet.
    """
    tree = build_huffman_tree(data)
    codes = make_codes(tree)
    encoded = ''.join(codes[b] for b in data)
    return encoded

def bitstring_to_bytes(s: str) -> bytearray:
    """
    Converts bytestring to bytes.
    """
    return bytearray(int(s[i:i+8], 2) for i in range(0, len(s), 8))

def deflate_bit_compress(filename: str, data: bool = False) -> bytes | tuple[bytes, dict]:
    """
    Makes pseudodeflate compression.
    """
    with open(filename, 'rb') as file:
        info = file.read()
    start = datetime.now()
    lz77 = compress_lz77(info)
    lz_bytes = lz77_to_bytes(lz77)
    tree = build_huffman_tree(lz_bytes)
    codes = make_codes(tree)
    encoded_bits = ''.join(codes[b] for b in lz_bytes)
    compressed_bytes = bitstring_to_bytes(encoded_bits)
    codes_serialized = pickle.dumps(codes)
    header_size = len(codes_serialized).to_bytes(4, 'big')
    final_data = header_size + codes_serialized + compressed_bytes

    end = datetime.now()
    print("Original size:", len(info), "bytes")
    print("Compressed size:", len(final_data), "bytes")
    if data:
        return final_data, {
            'Original size': len(info),
            'Compressed size': len(final_data),
            'Time': end - start
        }

    return final_data

#DECOMPRESS

def bytes_to_bitstring(data: bytes) -> str:
    """
    Converts bytes into string.
    """
    return ''.join(f'{byte:08b}' for byte in data)

def rebuild_tree_from_codes(codes: dict[int, str]) -> Node:
    """
    Rebuilds Huffman tree
    """
    root = Node()
    for symbol, code in codes.items():
        node = root
        for bit in code:
            if bit == '0':
                if not node.left:
                    node.left = Node()
                node = node.left
            else:
                if not node.right:
                    node.right = Node()
                node = node.right
        node.symbol = symbol
    return root

def huffman_decompress(bitstring: str, codes: dict[int, str]) -> bytearray:
    """
    Decompresses the string using Huffman tablet.
    """
    root = rebuild_tree_from_codes(codes)
    result = bytearray()
    node = root
    for bit in bitstring:
        node = node.left if bit == '0' else node.right
        if node.symbol is not None:
            result.append(node.symbol)
            node = root
    return result

def bytes_to_lz77(decoded_bytes: bytearray) -> list[tuple[int, int] | int]:
    """
    Converts bytes in LZ77 list again.
    """
    i = 0
    result = []
    while i < len(decoded_bytes):
        marker = decoded_bytes[i]

        if marker == 0:
            if i + 3 >= len(decoded_bytes):
                break
            dist = (decoded_bytes[i + 1] << 8) | decoded_bytes[i + 2]
            length = decoded_bytes[i + 3]
            result.append((dist, length))
            i += 4

        elif marker == 1:
            if i + 1 >= len(decoded_bytes):
                break
            result.append(decoded_bytes[i + 1])
            i += 2

        else:
            i += 1

    return result

def decompress_lz77(compressed: list[tuple[int, int] | int]) -> bytes:
    """
    Decompresses the LZ77 tuple
    """
    result = bytearray()
    for item in compressed:
        if isinstance(item, tuple):
            dist, length = item
            start = len(result) - dist
            for _ in range(length):
                result.append(result[start])
                start += 1
        else:
            result.append(item)
    return bytes(result)

def inflate_bit_decompress(compressed_data: bytes, info: bool=False) -> bytes | tuple[bytes, dict[str, int]]:
    """
    Decompresses the data by pseudodeflate code.
    """
    start = datetime.now()
    header_size = int.from_bytes(compressed_data[:4], 'big')
    codes_serialized = compressed_data[4:4+header_size]
    codes = pickle.loads(codes_serialized)
    compressed_bytes = compressed_data[4+header_size:]
    bitstring = bytes_to_bitstring(compressed_bytes)
    decoded_bytes = huffman_decompress(bitstring, codes)
    lz77_data = bytes_to_lz77(decoded_bytes)
    result = decompress_lz77(lz77_data)
    end = datetime.now()
    if info:
        return result, {
            "Decompressed size": len(result),
            "Time:": end - start
        }
    return result
