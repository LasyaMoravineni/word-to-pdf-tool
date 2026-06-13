import subprocess
import os

# Change if needed
SOFFICE_PATH = "soffice"
# Example:
# SOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"


def convert_file(input_file, output_dir):
    filename = os.path.basename(input_file)
    pdf_name = os.path.splitext(filename)[0] + ".pdf"
    output_pdf_path = os.path.join(output_dir, pdf_name)

    # ✅ Skip if already exists
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


def convert_folder(folder_path, output_dir=None):
    if not os.path.exists(folder_path):
        print("❌ Input folder not found")
        return

    if output_dir:
        output_dir = os.path.abspath(output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    else:
        output_dir = folder_path

    files = os.listdir(folder_path)

    doc_files = [
        f for f in files
        if f.lower().endswith((".doc", ".docx"))
    ]

    total = len(doc_files)

    if total == 0:
        print("⚠️ No Word files found in folder")
        return

    print(f"\n📂 Found {total} file(s). Starting conversion...\n")

    converted = 0
    skipped = 0
    failed = 0

    for i, file in enumerate(doc_files, start=1):
        full_path = os.path.join(folder_path, file)

        result = convert_file(full_path, output_dir)

        # Progress %
        # percent = (i / total) * 100

        if result == "converted":
            converted += 1
            status = "✅ Converted"
        elif result == "skipped":
            skipped += 1
            status = "⏭ Skipped"
        else:
            failed += 1
            status = "❌ Failed"

        print(f"[{i}/{total}]  {status}: {file}")

    print("\nBatch conversion complete!\n")

    # Summary
    print("Status:")
    print(f"   ✅ Converted: {converted}")
    print(f"   ⏭ Skipped:   {skipped}")
    print(f"   ❌ Failed:    {failed}")


# ===== RUN =====
if __name__ == "__main__":
    folder = input("Enter input folder path: ").strip()

    output = input("Enter output folder (or press Enter to use same folder): ").strip()
    output = output if output else None

    convert_folder(folder, output)