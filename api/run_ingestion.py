import os
import shutil
import subprocess
import sys

# Define paths
API_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_STORE_PATH = os.path.join(API_DIR, "chroma_store")
SETUP_CHROMA_SCRIPT = os.path.join(API_DIR, "setup_chroma.py")
INGEST_PDF_SCRIPT = os.path.join(API_DIR, "ingest_pdf.py")
INGEST_WEB_SCRIPT = os.path.join(API_DIR, "ingest_web.py")

def run_script(script_path):
    """Run a Python script and handle errors."""
    try:
        print(f"\n----- Running {os.path.basename(script_path)} -----")
        # Ensure that the script is run with the python executable that is running this script
        result = subprocess.run([sys.executable, script_path], check=True, text=True, capture_output=True)
        print(result.stdout)
        if result.stderr:
            print("----- Errors -----")
            print(result.stderr)
        print(f"----- Finished {os.path.basename(script_path)} -----\n")
    except subprocess.CalledProcessError as e:
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"!!! ERROR running {os.path.basename(script_path)} !!!")
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1) # Exit if any script fails
    except FileNotFoundError:
        print(f"Error: Script not found at {script_path}")
        sys.exit(1)


def main():
    """Main function to run all ingestion scripts."""
    print("[INFO] Starting the full data ingestion process...")

    # 1. Delete existing Chroma store
    if os.path.exists(CHROMA_STORE_PATH):
        print(f"[INFO] Deleting existing Chroma store at: {CHROMA_STORE_PATH}")
        try:
            shutil.rmtree(CHROMA_STORE_PATH)
            print("[SUCCESS] Chroma store deleted successfully.")
        except OSError as e:
            print(f"Error: {e.strerror} - {CHROMA_STORE_PATH}")
            sys.exit(1)
    else:
        print("[INFO] No existing Chroma store found. Starting fresh.")

    # 2. Run Hansard debates ingestion
    run_script(SETUP_CHROMA_SCRIPT)

    # 3. Run PDF ingestion
    run_script(INGEST_PDF_SCRIPT)

    # 4. Run web ingestion
    run_script(INGEST_WEB_SCRIPT)

    print("\n[SUCCESS] All data ingestion scripts have been executed successfully!")
    print("[SUCCESS] The Chroma vector store is now up to date.")

if __name__ == "__main__":
    main()