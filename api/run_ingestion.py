import os
import shutil
import subprocess
import sys

# Define paths
API_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_STORE_PATH = os.path.join(API_DIR, "chroma_store")
OUTPUT_PATH = os.path.join(API_DIR, "output") # Path to generated JSON files

# --- Updated script paths for the Macdonald speeches pipeline ---
EXTRACT_SPEECHES_SCRIPT = os.path.join(API_DIR, "scraper_files", "extract_macdonald_speeches.py")
EMBED_CHUNKS_SCRIPT = os.path.join(API_DIR, "scraper_files", "embed_chunks_local.py")


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
    """Main function to run the Hansard debates ingestion pipeline."""
    print("[INFO] Starting the Hansard debates data ingestion process...")

    # 1. Delete existing data directories to ensure a fresh start
    for path in [CHROMA_STORE_PATH, OUTPUT_PATH]:
        if os.path.exists(path):
            print(f"[INFO] Deleting existing data at: {path}")
            try:
                shutil.rmtree(path)
                print(f"[SUCCESS] Directory deleted successfully.")
            except OSError as e:
                print(f"Error: {e.strerror} - {path}")
                sys.exit(1)
        else:
            print(f"[INFO] No existing directory found at {path}. Starting fresh.")

    # 2. Run the script to extract speeches from PDFs into JSON files
    run_script(EXTRACT_SPEECHES_SCRIPT)

    # 3. Run the script to embed the JSON content and store it in Chroma
    run_script(EMBED_CHUNKS_SCRIPT)

    print("\n[SUCCESS] All data ingestion scripts have been executed successfully!")
    print("[SUCCESS] The Chroma vector store is now up to date with Macdonald's speeches.")

if __name__ == "__main__":
    main()