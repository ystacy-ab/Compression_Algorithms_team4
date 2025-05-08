"""argparse module"""
import argparse
import os
import tempfile
import pickle
from algorithms.huffman import compress_file as huffman_compress, \
decompress_file as huffman_decompress
from algorithms.deflate import deflate_bit_compress as deflate_compress, \
inflate_bit_decompress as deflate_decompress
from algorithms.lzw import lzw_encode as lzw_compress, lzw_decode as lzw_decompress
from algorithms.lz77 import lz77_compress, lz77_decompress
def readfile(path):
    """_summary_"""
    with open(path, "rb") as f:
        data = f.read()
    return data

def get_file_size(path):
    """summary"""
    return os.path.getsize(path)

def calc_compression_ratio(original_size, compressed_size):
    """summary"""
    return round(original_size / compressed_size, 2) if compressed_size else float('inf')

def check_lossless(original_path, decompressed_path):
    """summary"""
    with open(original_path, 'rb') as f1, open(decompressed_path, 'rb') as f2:
        return f1.read() == f2.read()

def main():
    """main"""
    parser = argparse.ArgumentParser(description="Compress files using different algorithms.")
    parser.add_argument("filepath", help="Path to the input file")
    parser.add_argument("algorithm", choices=["huffman", "deflate", "lzw", "lz77"], \
                    help="Compression algorithm to use")
    args = parser.parse_args()

    original_size = get_file_size(args.filepath)
    data = readfile(args.filepath)

    if args.algorithm == "huffman":
        compressed_path = huffman_compress(args.filepath)
        decompressed_path = huffman_decompress(compressed_path)

    elif args.algorithm == "deflate":
        compressed_data = deflate_compress(args.filepath)
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(compressed_data)
            compressed_path = f.name
        decompressed_data = deflate_decompress(compressed_data)
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(decompressed_data)
            decompressed_path = f.name

    elif args.algorithm == "lzw":
        compressed_data = lzw_compress(data)
        with tempfile.NamedTemporaryFile(delete=False) as f:
            pickle.dump(compressed_data, f)
            compressed_path = f.name
        decompressed_data = lzw_decompress(compressed_data)
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(decompressed_data)
            decompressed_path = f.name

    elif args.algorithm == "lz77":
        compressed_data = lz77_compress(data)
        with tempfile.NamedTemporaryFile(delete=False) as f:
            pickle.dump(compressed_data, f)
            compressed_path = f.name
        decompressed_data = lz77_decompress(compressed_data)
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(decompressed_data)
            decompressed_path = f.name

    else:
        print('Invalid algorithm')
        return

    compressed_size = get_file_size(compressed_path)
    compression_ratio = calc_compression_ratio(original_size, compressed_size)
    is_lossless = check_lossless(args.filepath, decompressed_path)

    print(f"Original file size     : {original_size} bytes")
    print(f"Compressed file size   : {compressed_size} bytes")
    print(f"Compression ratio      : {compression_ratio}")
    print(f"Lossless compression?  : {'Yes' if is_lossless else 'No'}")
if __name__ == "__main__":
    main()
