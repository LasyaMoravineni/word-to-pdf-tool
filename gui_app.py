import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import subprocess
import os
import threading
import fitz  # PyMuPDF

SOFFICE_PATH = "soffice"
# If needed:
# SOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"


# =====================================================
# WORD TO PDF FUNCTIONS
# =====================================================

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
    output_dir = output_entry.get().strip() or folder_path

    if not os.path.exists(folder_path):
        messagebox.showerror("Error", "Input folder not found")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = os.listdir(folder_path)

    doc_files = [
        f for f in files
        if f.lower().endswith((".doc", ".docx"))
    ]

    total = len(doc_files)

    if total == 0:
        messagebox.showwarning(
            "Warning",
            "No Word files found"
        )
        return

    log_area.delete(1.0, tk.END)

    progress["value"] = 0
    progress["maximum"] = total

    log(f"Found {total} file(s). Starting...\n")

    converted = skipped = failed = 0

    for i, file in enumerate(doc_files, start=1):

        full_path = os.path.join(folder_path, file)

        result = convert_file(
            full_path,
            output_dir
        )

        if result == "converted":
            converted += 1
            status = "Converted"

        elif result == "skipped":
            skipped += 1
            status = "Skipped"

        else:
            failed += 1
            status = "Failed"

        log(f"[{i}/{total}] {status}: {file}")

        progress["value"] = i
        root.update_idletasks()

    log("\nDone!\n")
    log("Summary:")
    log(f"Converted: {converted}")
    log(f"Skipped: {skipped}")
    log(f"Failed: {failed}")


# =====================================================
# PDF TO JPG FUNCTIONS
# =====================================================

def browse_pdf_folder():

    folder = filedialog.askdirectory()

    pdf_input_entry.delete(0, tk.END)
    pdf_input_entry.insert(0, folder)


def browse_pdf_output():

    folder = filedialog.askdirectory()

    pdf_output_entry.delete(0, tk.END)
    pdf_output_entry.insert(0, folder)


def pdf_log(message):

    pdf_log_area.insert(tk.END, message + "\n")
    pdf_log_area.see(tk.END)

    root.update_idletasks()


def convert_pdfs_to_jpg():

    folder_path = pdf_input_entry.get().strip()

    output_folder = pdf_output_entry.get().strip()

    if output_folder == "":
        output_folder = folder_path

    if not os.path.exists(folder_path):

        messagebox.showerror(
            "Error",
            "PDF folder not found"
        )

        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(".pdf")
    ]

    total = len(pdf_files)

    if total == 0:

        messagebox.showwarning(
            "Warning",
            "No PDF files found"
        )

        return

    pdf_log_area.delete(1.0, tk.END)

    pdf_progress["value"] = 0
    pdf_progress["maximum"] = total

    total_images = 0

    pdf_log(f"Found {total} PDF(s). Starting...\n")

    for index, pdf_file in enumerate(pdf_files, start=1):

        pdf_path = os.path.join(
            folder_path,
            pdf_file
        )

        pdf_name = os.path.splitext(
            pdf_file
        )[0]

        try:

            pdf_document = fitz.open(pdf_path)

            for page_num in range(len(pdf_document)):

                page = pdf_document[page_num]

                # Better quality output
                pix = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2)
                )

                output_file = os.path.join(
                    output_folder,
                    f"{pdf_name}_page{page_num + 1}.jpg"
                )

                pix.save(output_file)

                total_images += 1

            pdf_document.close()

            pdf_log(
                f"[{index}/{total}] Converted: {pdf_file}"
            )

        except Exception as e:

            pdf_log(
                f"[{index}/{total}] Failed: {pdf_file}"
            )

            pdf_log(str(e))

        pdf_progress["value"] = index

        root.update_idletasks()

    pdf_log("")
    pdf_log("Completed")
    pdf_log(f"PDFs Processed: {total}")
    pdf_log(f"Images Created: {total_images}")
    pdf_log(f"Output Folder: {output_folder}")




# =====================================================
# MERGE PDFs
# =====================================================


def browse_merge_folder():

    folder = filedialog.askdirectory()

    merge_input_entry.delete(0, tk.END)
    merge_input_entry.insert(0, folder)


def browse_merge_output():

    folder = filedialog.askdirectory()

    merge_output_entry.delete(0, tk.END)
    merge_output_entry.insert(0, folder)


def merge_log(message):

    merge_log_area.insert(tk.END, message + "\n")
    merge_log_area.see(tk.END)

    root.update_idletasks()


def merge_pdfs():

    folder_path = merge_input_entry.get().strip()

    output_folder = merge_output_entry.get().strip()

    if not os.path.exists(folder_path):

        messagebox.showerror(
            "Error",
            "Input folder not found"
        )

        return

    if output_folder == "":
        output_folder = folder_path

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_file = os.path.join(
        output_folder,
        "Merged_PDF.pdf"
    )

    pdf_files = sorted([
        f for f in os.listdir(folder_path)
        if f.lower().endswith(".pdf")
    ])

    total = len(pdf_files)

    if total == 0:

        messagebox.showwarning(
            "Warning",
            "No PDF files found"
        )

        return

    merge_log_area.delete(1.0, tk.END)

    merge_progress["value"] = 0
    merge_progress["maximum"] = total

    merge_log(
        f"Found {total} PDF(s). Starting...\n"
    )

    merged_pdf = fitz.open()

    try:

        for index, pdf_file in enumerate(
            pdf_files,
            start=1
        ):

            pdf_path = os.path.join(
                folder_path,
                pdf_file
            )

            current_pdf = fitz.open(
                pdf_path
            )

            merged_pdf.insert_pdf(
                current_pdf
            )

            current_pdf.close()

            merge_log(
                f"[{index}/{total}] Added: {pdf_file}"
            )

            merge_progress["value"] = index

            root.update_idletasks()

        merged_pdf.save(output_file)

        merge_log("")
        merge_log("Merge Completed")
        merge_log(
            f"Saved to: {output_file}"
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            str(e)
        )

    finally:

        merged_pdf.close()



# =====================================================
# GUI
# =====================================================

root = tk.Tk()
root.title("Document Utility Tool")
root.geometry("750x600")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# =====================================================
# WORD TO PDF TAB
# =====================================================

word_tab = tk.Frame(notebook)
notebook.add(word_tab, text="Word to PDF")

tk.Label(
    word_tab,
    text="Input Folder:"
).pack(anchor="w", padx=10, pady=5)

input_frame = tk.Frame(word_tab)
input_frame.pack(fill="x", padx=10)

input_entry = tk.Entry(input_frame)

input_entry.pack(
    side="left",
    fill="x",
    expand=True
)

tk.Button(
    input_frame,
    text="Browse",
    command=browse_input
).pack(side="right")

tk.Label(
    word_tab,
    text="Output Folder (optional):"
).pack(anchor="w", padx=10, pady=5)

output_frame = tk.Frame(word_tab)
output_frame.pack(fill="x", padx=10)

output_entry = tk.Entry(output_frame)

output_entry.pack(
    side="left",
    fill="x",
    expand=True
)

tk.Button(
    output_frame,
    text="Browse",
    command=browse_output
).pack(side="right")

tk.Button(
    word_tab,
    text="Start Conversion",
    bg="green",
    fg="white",
    command=lambda:
        threading.Thread(
            target=start_conversion
        ).start()
).pack(pady=10)

progress = ttk.Progressbar(
    word_tab,
    orient="horizontal",
    length=500,
    mode="determinate"
)

progress.pack(pady=5)

log_area = scrolledtext.ScrolledText(
    word_tab,
    height=18
)

log_area.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

# =====================================================
# PDF TO JPG TAB
# =====================================================

pdf_tab = tk.Frame(notebook)
notebook.add(pdf_tab, text="PDF to JPG")

merge_tab = tk.Frame(notebook)
notebook.add(merge_tab, text="Merge PDFs")

tk.Label(
    pdf_tab,
    text="Input Folder:"
).pack(anchor="w", padx=10, pady=5)

pdf_frame = tk.Frame(pdf_tab)
pdf_frame.pack(fill="x", padx=10)

pdf_input_entry = tk.Entry(pdf_frame)

pdf_input_entry.pack(
    side="left",
    fill="x",
    expand=True
)

tk.Button(
    pdf_frame,
    text="Browse",
    command=browse_pdf_folder
).pack(side="right")

# PDF OUTPUT FOLDER

tk.Label(
    pdf_tab,
    text="Output Folder (optional):"
).pack(anchor="w", padx=10, pady=5)

pdf_output_frame = tk.Frame(pdf_tab)
pdf_output_frame.pack(fill="x", padx=10)

pdf_output_entry = tk.Entry(pdf_output_frame)

pdf_output_entry.pack(
    side="left",
    fill="x",
    expand=True
)

tk.Button(
    pdf_output_frame,
    text="Browse",
    command=browse_pdf_output
).pack(side="right")

tk.Button(
    pdf_tab,
    text="Convert PDFs to JPG",
    bg="blue",
    fg="white",
    command=lambda:
        threading.Thread(
            target=convert_pdfs_to_jpg
        ).start()
).pack(pady=10)

pdf_progress = ttk.Progressbar(
    pdf_tab,
    orient="horizontal",
    length=500,
    mode="determinate"
)

pdf_progress.pack(pady=5)

pdf_log_area = scrolledtext.ScrolledText(
    pdf_tab,
    height=18
)

pdf_log_area.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)


# =====================================================
# MERGE PDF TAB
# =====================================================

tk.Label(
    merge_tab,
    text="Input Folder:"
).pack(anchor="w", padx=10, pady=5)

merge_input_frame = tk.Frame(
    merge_tab
)

merge_input_frame.pack(
    fill="x",
    padx=10
)

merge_input_entry = tk.Entry(
    merge_input_frame
)

merge_input_entry.pack(
    side="left",
    fill="x",
    expand=True
)

tk.Button(
    merge_input_frame,
    text="Browse",
    command=browse_merge_folder
).pack(side="right")


tk.Label(
    merge_tab,
    text="Output Folder (optional):"
).pack(anchor="w", padx=10, pady=5)

merge_output_frame = tk.Frame(
    merge_tab
)

merge_output_frame.pack(
    fill="x",
    padx=10
)

merge_output_entry = tk.Entry(
    merge_output_frame
)

merge_output_entry.pack(
    side="left",
    fill="x",
    expand=True
)

tk.Button(
    merge_output_frame,
    text="Browse",
    command=browse_merge_output
).pack(side="right")


tk.Button(
    merge_tab,
    text="Merge PDFs",
    bg="purple",
    fg="white",
    command=lambda:
        threading.Thread(
            target=merge_pdfs
        ).start()
).pack(pady=10)


merge_progress = ttk.Progressbar(
    merge_tab,
    orient="horizontal",
    length=500,
    mode="determinate"
)

merge_progress.pack(pady=5)


merge_log_area = scrolledtext.ScrolledText(
    merge_tab,
    height=18
)

merge_log_area.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

root.mainloop()