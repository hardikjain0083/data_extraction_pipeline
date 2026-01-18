import os
import urllib.request
import zipfile
import shutil
import subprocess
import sys

POPPLER_URL = "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.08.0-0/Release-24.08.0-0.zip"
INSTALL_DIR = os.path.expanduser(r"~\AppData\Local\Programs\poppler")
ZIP_PATH = "poppler.zip"

def install_poppler():
    print(f"Downloading Poppler from {POPPLER_URL}...")
    try:
        urllib.request.urlretrieve(POPPLER_URL, ZIP_PATH)
        print("Download complete.")
    except Exception as e:
        print(f"Failed to download: {e}")
        return

    print(f"Extracting to {INSTALL_DIR}...")
    if os.path.exists(INSTALL_DIR):
        shutil.rmtree(INSTALL_DIR)
    
    try:
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(INSTALL_DIR)
        print("Extraction complete.")
    except Exception as e:
        print(f"Failed to extract: {e}")
        return
    finally:
        if os.path.exists(ZIP_PATH):
            os.remove(ZIP_PATH)

    # Find the bin directory
    # The structure usually is Poppler/Library/bin or similar.
    # We walk to find 'pdftoppm.exe'
    bin_path = None
    for root, dirs, files in os.walk(INSTALL_DIR):
        if "pdftoppm.exe" in files:
            bin_path = root
            break
    
    if not bin_path:
        print("Error: Could not find 'bin' directory with pdftoppm.exe in extracted files.")
        return

    print(f"Found bin directory: {bin_path}")

    # Add to PATH
    current_path = os.environ.get('PATH', '')
    if bin_path in current_path:
        print("Poppler is already in your PATH (current session).")
    else:
        print("Adding Poppler to PATH...")
        # Add to current process path so we can survive this session
        os.environ['PATH'] += os.pathsep + bin_path
        
        # Persist to User PATH registry
        try:
            command = f'[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";{bin_path}", "User")'
            subprocess.run(["powershell", "-Command", command], check=True)
            print("Successfully updated User PATH registry.")
            print("NOTE: You may need to restart your terminal or application for the changes to take effect globally.")
        except Exception as e:
            print(f"Failed to update registry PATH: {e}")
            print("You can assume it works for this script, but for future use, add it manually.")

    print("\nPoppler installation setup complete!")
    print(f"Location: {bin_path}")

if __name__ == "__main__":
    install_poppler()
