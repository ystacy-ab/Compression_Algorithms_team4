import tkinter as tk
from tkinter import filedialog, messagebox
import pickle
from algorithms.huffman import compress_file as huffman_compress, decompress_file as huffman_decompress
from algorithms.deflate import deflate_bit_compress as deflate_compress, inflate_bit_decompress as deflate_decompress
from algorithms.lzw import lzw_encode as lzw_compress, lzw_decode as lzw_decompress
from algorithms.lz77 import lz77_compress, lz77_decompress

def browse_file():
    filename = filedialog.askopenfilename(title="Select a File", filetypes=(("All Files", "*.*"),))
    file_entry.delete(0, tk.END)
    file_entry.insert(0, filename)

def compress_decompress_file():
    filepath = file_entry.get()
    algorithm = algorithm_var.get()
    mode = mode_var.get()

    if not filepath:
        messagebox.showerror("Error", "Please select a file")
        return

    try:
        if mode == "compress":
            if algorithm == "huffman":
                compressed_path = huffman_compress(filepath)
            elif algorithm == "deflate":
                compressed_path = deflate_compress(filepath)
            elif algorithm == "lzw":
                with open(filepath, "rb") as f:
                    data = f.read()
                compressed_data = lzw_compress(data)
                compressed_path = save_compressed_file(compressed_data, 'lzw', filepath)
            elif algorithm == "lz77":
                with open(filepath, "rb") as f:
                    data = f.read()
                compressed_data = lz77_compress(data)
                compressed_path = save_compressed_file(compressed_data, 'lz77', filepath)

            messagebox.showinfo("Success", f"File compressed successfully:\n{compressed_path}")

        elif mode == "decompress":
            if algorithm == "huffman":
                decompressed_path = huffman_decompress(filepath)
            elif algorithm == "deflate":
                decompressed_path = deflate_decompress(filepath)
            elif algorithm == "lzw":
                decompressed_data = lzw_decompress(filepath)
                decompressed_path = save_decompressed_file(decompressed_data, 'lzw', filepath)
            elif algorithm == "lz77":
                decompressed_data = lz77_decompress(filepath)
                decompressed_path = save_decompressed_file(decompressed_data, 'lz77', filepath)

            messagebox.showinfo("Success", f"File decompressed successfully:\n{decompressed_path}")
        else:
            messagebox.showerror("Error", "Invalid mode selected")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def save_compressed_file(data, algorithm, original_filename):
    compressed_filename = f"{original_filename}_{algorithm}_compressed.bin"
    with open(compressed_filename, "wb") as f:
        pickle.dump(data, f)
    return compressed_filename

def save_decompressed_file(data, algorithm, original_filename):
    decompressed_filename = f"{original_filename}_{algorithm}_decompressed.bin"
    with open(decompressed_filename, "wb") as f:
        f.write(data)
    return decompressed_filename

root = tk.Tk()
root.title("File Compression/Decompression")
root.configure(bg="#f8f9fa")
root.geometry("600x250")
root.resizable(False, False)

label_font = ("Arial", 12)
entry_font = ("Arial", 12)
button_font = ("Arial", 12, "bold")
primary_color = "#A9B5E1"
secondary_color = "#A9B5E1"
text_color = "#343a40"

file_frame = tk.Frame(root, bg="#122D93", padx=20, pady=10)
file_frame.pack(fill="x")

file_label = tk.Label(file_frame, text="Select File:", font=label_font, bg="#f8f9fa", fg=text_color)
file_label.pack(side="left")

file_entry = tk.Entry(file_frame, width=40, font=entry_font)
file_entry.pack(side="left", padx=10, fill="x", expand=True)

browse_button = tk.Button(file_frame, text="Browse", command=browse_file, font=button_font,
                          bg=secondary_color, fg="black")
browse_button.pack(side="left")
settings_frame = tk.Frame(root, bg="#A9B5E1", padx=20, pady=10)
settings_frame.pack(fill="x")
algorithm_label = tk.Label(settings_frame, text="Algorithm:", font=label_font, bg="#f8f9fa", fg=text_color)
algorithm_label.pack(side="left", padx=(0, 5))

algorithm_var = tk.StringVar(value="huffman")
algorithm_options = ["huffman", "deflate", "lzw", "lz77"]
algorithm_menu = tk.OptionMenu(settings_frame, algorithm_var, *algorithm_options)
algorithm_menu.config(font=entry_font, bg="white", fg=text_color)
algorithm_menu.pack(side="left", padx=(0, 20))

mode_label = tk.Label(settings_frame, text="Mode:", font=label_font, bg="#f8f9fa", fg=text_color)
mode_label.pack(side="left", padx=(0, 5))

mode_var = tk.StringVar(value="compress")
mode_options = ["compress", "decompress"]
mode_menu = tk.OptionMenu(settings_frame, mode_var, *mode_options)
mode_menu.config(font=entry_font, bg="white", fg=text_color)
mode_menu.pack(side="left")

process_button = tk.Button(root, text="Process", command=compress_decompress_file, font=button_font,
                           bg=primary_color, fg="white", pady=8, padx=20)
process_button.pack(pady=20)

root.mainloop()