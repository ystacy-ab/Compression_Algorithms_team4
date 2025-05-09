import os
import pickle
import tkinter
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk, ImageFilter
import math
from algorithms.huffman import compress_file as huffman_compress, decompress_file as huffman_decompress
from algorithms.deflate import deflate_bit_compress as deflate_compress, \
    inflate_bit_decompress as deflate_decompress
from algorithms.lzw import lzw_encode as lzw_compress, lzw_decode as lzw_decompress
from algorithms.lz77 import lz77_compress, lz77_decompress

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def readfile(path):
    """Read the file content"""
    with open(path, "rb") as f:
        data = f.read()
    return data


def get_file_size(path):
    """Get the size of the file"""
    return os.path.getsize(path)


def calc_compression_ratio(original_size, compressed_size):
    """Calculate compression ratio"""
    return round(original_size / compressed_size, 2) if compressed_size else float('inf')


def check_lossless(original_path, decompressed_path):
    """Check if the decompression is lossless"""
    with open(original_path, 'rb') as f1, open(decompressed_path, 'rb') as f2:
        return f1.read() == f2.read()


def save_compressed_file(data, algorithm, original_filepath):
    """Saves the compressed data to a file"""
    original_filename = os.path.splitext(os.path.basename(original_filepath))[0]
    compressed_filename = f"{original_filename}_{algorithm}_compressed.bin"
    with open(compressed_filename, "wb") as f:
        pickle.dump(data, f)
    return compressed_filename


def save_decompressed_file(data, algorithm, original_filepath):
    """Saves the decompressed data to a file with the original extension"""
    original_filename = os.path.splitext(os.path.basename(original_filepath))[0]
    original_extension = os.path.splitext(original_filepath)[1]
    decompressed_filename = f"{original_filename}_{algorithm}_decompressed{original_extension}"
    with open(decompressed_filename, "wb") as f:
        f.write(data)
    return decompressed_filename


class CircularGradient(ctk.CTkFrame):
    def __init__(self, master, width=300, height=300, color1="#FF4D00", color2="#0D0D0D", blur_radius=20, **kwargs):
        super().__init__(master, width=width, height=height, fg_color="transparent", **kwargs)

        self.width = width
        self.height = height
        self.color1 = color1
        self.color2 = color2
        self.blur_radius = blur_radius

        self.canvas = ctk.CTkCanvas(
            self,
            width=width,
            height=height,
            bg="#0D0D0D",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.draw_gradient()

    def draw_gradient(self):
        center_x = self.width // 2
        center_y = self.height // 2
        radius = min(center_x, center_y)

        for r in range(radius, 0, -1):
            ratio = r / radius
            r_color = int(int(self.color1[1:3], 16) * ratio + int(self.color2[1:3], 16) * (1 - ratio))
            g_color = int(int(self.color1[3:5], 16) * ratio + int(self.color2[3:5], 16) * (1 - ratio))
            b_color = int(int(self.color1[5:7], 16) * ratio + int(self.color2[5:7], 16) * (1 - ratio))

            color = f"#{r_color:02x}{g_color:02x}{b_color:02x}"

            self.canvas.create_oval(
                center_x - r, center_y - r,
                center_x + r, center_y + r,
                fill=color, outline=color
            )

        blur_height = self.height // 3
        self.canvas.create_rectangle(
            0, 0, self.width, blur_height,
            fill="#0D0D0D", outline="#0D0D0D",
            stipple="gray50"
        )

class FileConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ApexConvert")
        self.geometry("650x650")
        self.configure(fg_color="#0D0D0D")

        self.file_path = tkinter.StringVar()
        self.algorithm = tkinter.StringVar(value="huffman")
        self.mode = tkinter.StringVar(value="compress")
        self.total_files = tkinter.StringVar(value="0")
        self.ratio = tkinter.StringVar(value="0.0x")
        self.total_saved = tkinter.StringVar(value="0.0 KB")

        self.create_background()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.create_header()
        self.create_main_content()

    def create_background(self):
        self.gradient_frame = ctk.CTkFrame(self, fg_color="transparent", width=650, height=650)
        self.gradient_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.gradient = CircularGradient(
            self.gradient_frame,
            width=650,
            height=650,
            color1="#FF4D00",
            color2="#0D0D0D",
            blur_radius=30
        )
        self.gradient.pack()

        self.blur_frame = ctk.CTkFrame(self, fg_color="transparent", width=650, height=300)
        self.blur_frame.place(relx=0.5, rely=0.3, anchor="center")

        self.blur_canvas = ctk.CTkCanvas(
            self.blur_frame,
            width=650,
            height=300,
            bg="#0D0D0D",
            highlightthickness=0
        )
        self.blur_canvas.pack(fill="both", expand=True)

        for i in range(100):
            opacity = 100 - i
            y_pos = i * 3

            stipple_pattern = "gray25" if opacity > 75 else "gray50" if opacity > 50 else "gray75" if opacity > 25 else ""

            if stipple_pattern:
                self.blur_canvas.create_rectangle(
                    0, y_pos, 650, y_pos + 3,
                    fill="#0D0D0D", outline="#0D0D0D",
                    stipple=stipple_pattern
                )

    def create_header(self):
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent", height=40)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=1)

        self.logo_frame = ctk.CTkFrame(self.header_frame, fg_color="#171717", corner_radius=10)
        self.logo_frame.grid(row=0, column=0, sticky="w", padx=15, pady=10)

        self.logo_label = ctk.CTkLabel(
            self.logo_frame,
            text="⚡ ApexConvert",
            font=ctk.CTkFont(size=14, weight="bold"),
            padx=10,
            pady=5
        )
        self.logo_label.pack()

        self.date_frame = ctk.CTkFrame(self.header_frame, fg_color="#171717", corner_radius=10)
        self.date_frame.grid(row=0, column=1, sticky="e", padx=15, pady=10)

        import datetime
        today = datetime.datetime.now().strftime("%A %b %d, %Y")

        self.date_label = ctk.CTkLabel(
            self.date_frame,
            text=today,
            font=ctk.CTkFont(size=12),
            padx=10,
            pady=5
        )
        self.date_label.pack()

    def create_main_content(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=0)
        self.main_frame.grid_rowconfigure(1, weight=0)
        self.main_frame.grid_rowconfigure(2, weight=0)
        self.main_frame.grid_rowconfigure(3, weight=0)
        self.main_frame.grid_rowconfigure(4, weight=1)

        self.stats_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.stats_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)
        self.stats_frame.grid_columnconfigure(0, weight=1)
        self.stats_frame.grid_columnconfigure(1, weight=1)
        self.stats_frame.grid_columnconfigure(2, weight=1)
        self.stats_frame.grid_columnconfigure(3, weight=1)

        self.files_label = ctk.CTkLabel(
            self.stats_frame,
            textvariable=self.total_files,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.files_label.grid(row=0, column=0, sticky="w", padx=10)

        self.files_desc = ctk.CTkLabel(
            self.stats_frame,
            text="Files processed",
            text_color=("gray70", "gray30"),
            font=ctk.CTkFont(size=12)
        )
        self.files_desc.grid(row=1, column=0, sticky="w", padx=10)

        self.size_label = ctk.CTkLabel(
            self.stats_frame,
            text="3.2b",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.size_label.grid(row=0, column=1, sticky="w", padx=10)

        self.size_desc = ctk.CTkLabel(
            self.stats_frame,
            text="Bytes processed",
            text_color=("gray70", "gray30"),
            font=ctk.CTkFont(size=12)
        )
        self.size_desc.grid(row=1, column=1, sticky="w", padx=10)

        self.awards_label = ctk.CTkLabel(
            self.stats_frame,
            text="1k+",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.awards_label.grid(row=0, column=2, sticky="e", padx=10)

        self.awards_desc = ctk.CTkLabel(
            self.stats_frame,
            text="Happy users",
            text_color=("gray70", "gray30"),
            font=ctk.CTkFont(size=12)
        )
        self.awards_desc.grid(row=1, column=2, sticky="e", padx=10)

        self.transactions_label = ctk.CTkLabel(
            self.stats_frame,
            textvariable=self.ratio,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.transactions_label.grid(row=0, column=3, sticky="e", padx=10)

        self.transactions_desc = ctk.CTkLabel(
            self.stats_frame,
            text="Compression ratio",
            text_color=("gray70", "gray30"),
            font=ctk.CTkFont(size=12)
        )
        self.transactions_desc.grid(row=1, column=3, sticky="e", padx=10)

        self.headline_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.headline_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.headline_label = ctk.CTkLabel(
            self.headline_frame,
            text="Next level of compression and decompression",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=24, weight="bold"),
            justify="center"
        )
        self.headline_label.pack()

        self.file_card = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="#1A1A1A")
        self.file_card.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10, padx=10)
        self.file_card.grid_columnconfigure(0, weight=1)
        self.file_card.grid_columnconfigure(1, weight=0)

        self.file_title = ctk.CTkLabel(
            self.file_card,
            text="Select File",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.file_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 5))

        self.file_entry = ctk.CTkEntry(
            self.file_card,
            textvariable=self.file_path,
            placeholder_text="No file selected",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.file_entry.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))

        self.browse_button = ctk.CTkButton(
            self.file_card,
            text="Browse",
            command=self.browse_file,
            width=100,
            height=35,
            fg_color="#FF4D00",
            hover_color="#FF6A29",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8
        )
        self.browse_button.grid(row=1, column=1, sticky="e", padx=15, pady=(0, 15))

        self.settings_card = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="#1A1A1A")
        self.settings_card.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10, padx=10)
        self.settings_card.grid_columnconfigure(0, weight=1)
        self.settings_card.grid_columnconfigure(1, weight=1)

        self.settings_title = ctk.CTkLabel(
            self.settings_card,
            text="Conversion Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.settings_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 5))

        self.algo_label = ctk.CTkLabel(
            self.settings_card,
            text="Algorithm:",
            font=ctk.CTkFont(size=12)
        )
        self.algo_label.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 5))

        self.algo_menu = ctk.CTkOptionMenu(
            self.settings_card,
            values=["huffman", "deflate", "lzw", "lz77"],
            variable=self.algorithm,
            width=180,
            height=35,
            fg_color="#171717",
            button_color="#FF4D00",
            button_hover_color="#FF6A29",
            font=ctk.CTkFont(size=12),
            corner_radius=8
        )
        self.algo_menu.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 15))

        self.mode_label = ctk.CTkLabel(
            self.settings_card,
            text="Mode:",
            font=ctk.CTkFont(size=12)
        )
        self.mode_label.grid(row=1, column=1, sticky="w", padx=15, pady=(0, 5))

        self.mode_menu = ctk.CTkOptionMenu(
            self.settings_card,
            values=["compress", "decompress"],
            variable=self.mode,
            width=180,
            height=35,
            fg_color="#171717",
            button_color="#FF4D00",
            button_hover_color="#FF6A29",
            font=ctk.CTkFont(size=12),
            corner_radius=8
        )
        self.mode_menu.grid(row=2, column=1, sticky="w", padx=15, pady=(0, 15))

        self.start_button = ctk.CTkButton(
            self.main_frame,
            text="START CONVERSION",
            command=self.compress_decompress_file,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#FF4D00",
            hover_color="#FF6A29",
            corner_radius=10
        )
        self.start_button.grid(row=4, column=0, columnspan=2, sticky="n", pady=10, padx=10)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select File",
            filetypes=(("All Files", "*.*"),)
        )
        if filename:
            self.file_path.set(filename)

    def update_stats(self, original_size, compressed_size, compression_ratio):
        """Update compression statistics"""
        try:
            self.total_files.set(str(int(self.total_files.get()) + 1))
            self.total_saved.set(f"{(original_size - compressed_size) / 1024:.1f} KB")

            self.ratio.set(f"{compression_ratio:.1f}x")
        except:
            pass

    def compress_decompress_file(self):
        filepath = self.file_path.get()
        algorithm = self.algorithm.get()
        mode = self.mode.get()

        if not filepath:
            messagebox.showerror("Input Error", "Please select a file.")
            return
        if not os.path.exists(filepath):
            messagebox.showerror("File Error", f"File not found: {filepath}")
            return

        try:
            original_size = get_file_size(filepath)
            original_filename = os.path.splitext(os.path.basename(filepath))[0]
            original_extension = os.path.splitext(filepath)[1]

            if mode == "compress":
                if algorithm == "huffman":
                    compressed_path = huffman_compress(filepath)

                elif algorithm == "deflate":
                    compressed_data = deflate_compress(filepath)
                    compressed_path = f"{original_filename}_deflate_compressed.bin"
                    with open(compressed_path, "wb") as f:
                        f.write(compressed_data)

                elif algorithm == "lzw":
                    data = readfile(filepath)
                    compressed_data = lzw_compress(data)
                    compressed_path = save_compressed_file(compressed_data, 'lzw', filepath)

                elif algorithm == "lz77":
                    data = readfile(filepath)
                    compressed_data = lz77_compress(data)
                    compressed_path = save_compressed_file(compressed_data, 'lz77', filepath)

                compressed_size = get_file_size(compressed_path)
                compression_ratio = calc_compression_ratio(original_size, compressed_size)

                self.update_stats(original_size, compressed_size, compression_ratio)

                messagebox.showinfo("Success",
                                    f"Compressed: {compressed_path}\n"
                                    f"Original size: {original_size} bytes\n"
                                    f"Compressed size: {compressed_size} bytes\n"
                                    f"Compression ratio: {compression_ratio}")

            elif mode == "decompress":
                if algorithm == "huffman":
                    decompressed_path = huffman_decompress(filepath)

                elif algorithm == "deflate":
                    with open(filepath, "rb") as f:
                        compressed_data = f.read()
                    decompressed_data = deflate_decompress(compressed_data)
                    decompressed_path = f"{original_filename}_deflate_decompressed{original_extension}"
                    with open(decompressed_path, "wb") as f:
                        f.write(decompressed_data)

                elif algorithm == "lzw":
                    with open(filepath, "rb") as f:
                        compressed_data = pickle.load(f)
                    decompressed_data = lzw_decompress(compressed_data)
                    decompressed_path = save_decompressed_file(decompressed_data, 'lzw', filepath)

                elif algorithm == "lz77":
                    with open(filepath, "rb") as f:
                        compressed_data = pickle.load(f)
                    decompressed_data = lz77_decompress(compressed_data)
                    decompressed_path = save_decompressed_file(decompressed_data, 'lz77', filepath)

                original_file_guess = filepath.replace("_compressed.bin", "").replace(f"_{algorithm}", "")
                is_lossless = "Unknown"
                if os.path.exists(original_file_guess):
                    is_lossless = "Yes" if check_lossless(original_file_guess, decompressed_path) else "No"

                messagebox.showinfo("Success",
                                    f"Decompressed: {decompressed_path}\n"
                                    f"Lossless: {is_lossless}")

        except Exception as e:
            messagebox.showerror("Error", f"Operation failed for {algorithm.upper()}:\n{str(e)}")


if __name__ == "__main__":
    app = FileConverterApp()
    app.mainloop()
