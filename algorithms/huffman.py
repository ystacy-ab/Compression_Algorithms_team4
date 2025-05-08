"""huffman algorithm"""
import os
import pickle

class Node:
    """_summary_
    """
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

def build_frequency_dict(data: bytes) -> dict:
    """Builds a frequency dictionary for all bytes in the input data.
        Parameters:
        data – Bytes object to analyze.
        Returns:
        A dictionary mapping each byte to its frequency in data.
    """
    dct = {}
    for byte in data:
        dct[byte] = dct.get(byte, 0) + 1
    return dct

def build_huffman_tree(freq: dict) -> Node:
    """Builds a Huffman tree based on the given byte frequencies.
        Parameters:
        freq – A dictionary of byte frequencies.
        Returns:
        The root node of the Huffman tree.
    """
    lst = [Node(byte, frq) for byte, frq in freq.items()]
    lst.sort(key=lambda node: node.freq)
    while len(lst) > 1:
        left = lst.pop(0)
        right = lst.pop(0)
        joined = Node(None, left.freq + right.freq)
        joined.left = left
        joined.right = right
        lst.append(joined)
        lst.sort(key=lambda node: node.freq)
    return lst[0] if lst else None

def build_codes(root: Node) -> dict:
    """Generates the binary Huffman codes for each byte by traversing the tree.
        Parameters:
        root – Root node of the Huffman tree.
        Returns:
        A dictionary mapping each byte to its Huffman code as a string of '0's and '1's.
    """
    codes = {}
    stack = [(root, "")]
    while stack:
        node, code = stack.pop()
        if node is not None:
            if node.char is not None:
                codes[node.char] = code
            else:
                stack.append((node.left, code + "0"))
                stack.append((node.right, code + "1"))
    return codes


def compress_file(filepath: str) -> str:
    """Compresses a file using Huffman coding and saves the result to a .huff file.
        Parameters:
        filepath – Path to the file to compress.
        Returns:
        The path to the created compressed .huff file.
    """
    with open(filepath, "rb") as f:
        data = f.read()

    freq_dict = build_frequency_dict(data)
    tree = build_huffman_tree(freq_dict)
    codes = build_codes(tree)

    encoded_bits = ''.join(codes[byte] for byte in data)
    padding = (8 - len(encoded_bits) % 8) % 8
    padded_bits = encoded_bits + '0' * padding
    byte_array = bytearray(int(padded_bits[i:i+8], 2) for i in range(0, len(padded_bits), 8))

    file_name = os.path.basename(filepath)
    output_path = os.path.splitext(filepath)[0] + ".huff"

    with open(output_path, "wb") as out:
        pickle.dump((byte_array, codes, len(encoded_bits), file_name), out)


    return output_path

def decompress_file(filepath: str) -> str:
    """Decompresses a .huff file back to its original binary format.
        Parameters:
        filepath – Path to the .huff file.
        Returns:
        The path to the restored original file.
    """
    with open(filepath, "rb") as f:
        byte_array, codes, bit_length, original_filename = pickle.load(f)

        _, file_ext = os.path.splitext(original_filename)
        output_path = os.path.splitext(filepath)[0] + "_decompressed" + file_ext
    reversed_codes = {v: k for k, v in codes.items()}
    bit_string = ''.join(f"{byte:08b}" for byte in byte_array)
    bit_string = bit_string[:bit_length]
    curr = ""
    result = bytearray()
    for bit in bit_string:
        curr += bit
        if curr in reversed_codes:
            result.append(reversed_codes[curr])
            curr = ""
    output_path = os.path.splitext(filepath)[0] + "_decompressed" + file_ext
    with open(output_path, "wb") as out:
        out.write(result)

    return output_path
