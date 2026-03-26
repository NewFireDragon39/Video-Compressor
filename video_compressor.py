import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
import subprocess

root = tk.Tk()
root.title("Video Compressor")
root.geometry("500x420")

input_file = tk.StringVar()
output_dir = tk.StringVar()
last_auto_name = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
output_name = tk.StringVar(value=last_auto_name)

RESOLUTION_OPTIONS = (
    "1080 (Best Quality, Big File Size)",
    "720 (High Quality, Medium-High File Size)",
    "480 (Standard Quality, Medium File Size)",
    "360 (Low Quality, Small File Size)",
    "240 (Very Low Quality, Very Small File Size)",
    "144 (Terrible Quality, Super Duper Small File Size)",
    "20 (Just for fun ;) )"
)

FPS_OPTIONS = (
    "60 (Smooth, Big File Size)",
    "30 (Balanced)",
    "24 (Optimized, Recommended)",
    "15 (Choppy, Small File Size)",
    "1 (Just for fun ;) )"
)

def browse_file():
    global last_auto_name

    previous_input = input_file.get().strip()
    file = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mkv *.mov")])
    if not file:
        return

    input_file.set(file)

    previous_dir = str(Path(previous_input).parent) if previous_input else ""
    if not output_dir.get().strip() or output_dir.get().strip() == previous_dir:
        output_dir.set(str(Path(file).parent))

    if not output_name.get().strip() or output_name.get().strip() == last_auto_name:
        last_auto_name = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        output_name.set(last_auto_name)


def browse_output_dir():
    initial_dir = output_dir.get().strip()
    if not initial_dir and input_file.get().strip():
        initial_dir = str(Path(input_file.get().strip()).parent)

    folder = filedialog.askdirectory(initialdir=initial_dir)
    if folder:
        output_dir.set(folder)


tk.Label(root, text="Input File:").pack()
tk.Entry(root, textvariable=input_file, width=40).pack()
tk.Button(root, text="Browse", command=browse_file).pack()

tk.Label(root, text="Output Folder:").pack()
tk.Entry(root, textvariable=output_dir, width=50).pack()
tk.Button(root, text="Choose Folder", command=browse_output_dir).pack()

tk.Label(root, text="Output Name:").pack()
tk.Entry(root, textvariable=output_name, width=50).pack()

tk.Label(root, text="Resolution (height):").pack()

res_var = tk.StringVar()
res_combo = ttk.Combobox(root, textvariable=res_var, state="readonly")
res_combo["values"] = RESOLUTION_OPTIONS
res_combo.set("480 (Standard Quality, Medium File Size)")
res_combo.pack()

tk.Label(root, text="Custom Resolution (optional):").pack()
res_entry = tk.Entry(root)
res_entry.pack()

tk.Label(root, text="Framerate (FPS):").pack()

fps_var = tk.StringVar()
fps_combo = ttk.Combobox(root, textvariable=fps_var, state="readonly")
fps_combo["values"] = FPS_OPTIONS
fps_combo.set("30 (Balanced)")
fps_combo.pack()

tk.Label(root, text="Custom FPS (optional):").pack()
fps_entry = tk.Entry(root)
fps_entry.pack()

def get_numeric_value(entry_widget, selected_value, field_name):
    custom_value = entry_widget.get().strip()
    if custom_value:
        if not custom_value.isdigit():
            raise ValueError(f"{field_name} must be a whole number.")
        return custom_value
    return selected_value.split()[0]


def get_output_path(infile):
    global last_auto_name

    current_name = output_name.get().strip()
    if not current_name or current_name == last_auto_name:
        last_auto_name = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        output_name.set(last_auto_name)
        current_name = last_auto_name

    if any(char in current_name for char in '<>:"/\\|?*'):
        raise ValueError("Output name contains invalid filename characters.")

    target_dir = output_dir.get().strip() or str(Path(infile).parent)
    if not Path(target_dir).exists():
        raise ValueError("Output folder does not exist.")

    suffix = Path(current_name).suffix
    filename = current_name if suffix else f"{current_name}.mp4"
    return str(Path(target_dir) / filename)


def compress():
    infile = input_file.get().strip()

    if not infile:
        messagebox.showerror("Missing input", "Choose a video file first.")
        return

    try:
        res_str = res_combo.get()
        fps_str = fps_combo.get()

        if res_str == "64 (Just for fun ;) )":
            res = 20
        else:
            res = int(get_numeric_value(res_entry, res_str, "Resolution"))
            if res < 20:
                messagebox.showerror("Invalid Resolution", "Resolution too low!")
                return

        if fps_str == "1 (Just for fun ;) )":
            fps = 1
        else:
            fps = int(get_numeric_value(fps_entry, fps_str, "FPS"))
            if fps < 1:
                messagebox.showerror("Invalid FPS", "FPS must be at least 1.")
                return

        outfile = get_output_path(infile)
    except ValueError as error:
        messagebox.showerror("Invalid setting", str(error))
        return

    command = [
        "ffmpeg",
        "-y",
        "-i", infile,
        "-vf", f"scale=-2:{res},fps={fps}",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "fast",
        outfile
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True)
    except FileNotFoundError:
        messagebox.showerror("ffmpeg not found", "Install ffmpeg and make sure it is on your PATH.")
        return

    if result.returncode != 0:
        messagebox.showerror("Compression failed", result.stderr.strip() or "ffmpeg returned an error.")
        return

    messagebox.showinfo("Done", f"Compressed video saved as {outfile}.")

tk.Button(root, text="Compress", command=compress).pack(pady=10)

root.mainloop()