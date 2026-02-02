import os
import zipfile


def create_zip(source_dir, output_filename):
    # Items to exclude
    EXCLUDE_DIRS = {
        ".git",
        ".vscode",
        "node_modules",
        "__pycache__",
        ".idea",
        "dist",
        "coverage",
        ".pytest_cache",
        ".claude",
        ".gemini",
    }

    EXCLUDE_EXTENSIONS = {".pyc", ".zip", ".rar", ".7z"}

    EXCLUDE_FILES = {".env", ".DS_Store"}

    print(f"Creating backup ZIP: {output_filename}...")

    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                if file in EXCLUDE_FILES:
                    continue

                _, ext = os.path.splitext(file)
                if ext in EXCLUDE_EXTENSIONS:
                    continue

                # Full path
                file_path = os.path.join(root, file)

                # Relative path for the zip
                rel_path = os.path.relpath(file_path, source_dir)

                # Add to zip
                print(f"Adding: {rel_path}")
                zipf.write(file_path, rel_path)

    print(f"\n[OK] ZIP Created successfully: {output_filename}")


if __name__ == "__main__":
    source = r"c:\Users\Transporte-02\Desktop\teste_mateus"
    output = os.path.join(source, "Teste_mateus.zip")
    create_zip(source, output)
