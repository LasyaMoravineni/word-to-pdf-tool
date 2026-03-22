import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import subprocess
import os
import threading

SOFFICE_PATH = "soffice"
# If needed:
# SOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"


def convert_file(input_file, output_dir):
    filename = os.path.basename(input_file)
    pdf_name = os.path.splitext(filename)[0] + ".pdf"
    output_pdf_path = os.path.join(output_dir, pdf_name)

    if os.path.exists(output_pdf_path):
        return "skipped"

    try:
        subprocess.run([
            SOFFICE_PATH,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            input_file
        ], check=True)

        return "converted"

    except subprocess.CalledProcessError:
        return "failed"


def browse_input():
    folder = filedialog.askdirectory()
    input_entry.delete(0, tk.END)
    input_entry.insert(0, folder)


def browse_output():
    folder = filedialog.askdirectory()
    output_entry.delete(0, tk.END)
    output_entry.insert(0, folder)


def log(message):
    log_area.insert(tk.END, message + "\n")
    log_area.see(tk.END)
    root.update_idletasks()


def start_conversion():
    folder_path = input_entry.get()
    output_dir = output_entry.get() or folder_path

    if not os.path.exists(folder_path):
        messagebox.showerror("Error", "Input folder not found")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = os.listdir(folder_path)
    doc_files = [f for f in files if f.lower().endswith((".doc", ".docx"))]

    total = len(doc_files)

    if total == 0:
        messagebox.showwarning("Warning", "No Word files found")
        return

    # Reset UI
    log_area.delete(1.0, tk.END)
    progress["value"] = 0
    progress["maximum"] = total

    log(f"Found {total} file(s). Starting...\n")

    converted = skipped = failed = 0

    for i, file in enumerate(doc_files, start=1):
        full_path = os.path.join(folder_path, file)
        result = convert_file(full_path, output_dir)

        # percent = (i / total) * 100

        if result == "converted":
            converted += 1
            status = "Converted"
        elif result == "skipped":
            skipped += 1
            status = "Skipped"
        else:
            failed += 1
            status = "Failed"

        log(f"[{i}/{total}]  {status}: {file}")

        # ✅ Update progress bar
        progress["value"] = i
        root.update_idletasks()

    log("\nDone!\n")
    log("Summary:")
    log(f"Converted: {converted}")
    log(f"Skipped: {skipped}")
    log(f"Failed: {failed}")


# ===== GUI SETUP =====
root = tk.Tk()
root.title("Word to PDF Converter")
root.geometry("600x450")

# Input folder
tk.Label(root, text="Input Folder:").pack(anchor="w", padx=10, pady=5)
input_frame = tk.Frame(root)
input_frame.pack(fill="x", padx=10)

input_entry = tk.Entry(input_frame)
input_entry.pack(side="left", fill="x", expand=True)

tk.Button(input_frame, text="Browse", command=browse_input).pack(side="right")

# Output folder
tk.Label(root, text="Output Folder (optional):").pack(anchor="w", padx=10, pady=5)
output_frame = tk.Frame(root)
output_frame.pack(fill="x", padx=10)

output_entry = tk.Entry(output_frame)
output_entry.pack(side="left", fill="x", expand=True)

tk.Button(output_frame, text="Browse", command=browse_output).pack(side="right")

# Convert button
tk.Button(root, text="Start Conversion", command=lambda: threading.Thread(target=start_conversion).start(),
          bg="green", fg="white").pack(pady=10)

# Progress Button
progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress.pack(pady=5)

# Log area
log_area = scrolledtext.ScrolledText(root, height=15)
log_area.pack(fill="both", padx=10, pady=10, expand=True)

root.mainloop()