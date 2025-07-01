import fitz  # PyMuPDF
import os
import re
import json
from tqdm import tqdm

# Settings
INPUT_FOLDER = "./pdfs"        # Folder containing Hansard PDFs
OUTPUT_FOLDER = "./output"     # Where to save JSON files
CHUNK_WORDS = 500              # Approximate chunk size

def extract_text_from_pdf(filepath):
    doc = fitz.open(filepath)
    full_text = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        full_text.append((page_num + 1, text))
    return full_text

def extract_macdonald_speech_blocks(text_with_pages):
    """
    Find all speech blocks attributed to John A. Macdonald.
    """
    speech_blocks = []
    # More flexible patterns
    patterns = [
      re.compile(r"(Right\s+)?Hon(\.|ourable)?\s+Sir\s+John\s+A\.?\s+Macdonald.*?(rose|said|moved|addressed|spoke)", re.IGNORECASE),
      re.compile(r"Sir\s+John\s+A\.?\s+Macdonald.*?(rose|said|moved|addressed|spoke)", re.IGNORECASE),
      re.compile(r"Mr\.?\s+Macdonald.*?(rose|said|moved|addressed|spoke)", re.IGNORECASE)
    ]


    current_speaker = None
    buffer = []
    current_page = None

    for page_num, text in text_with_pages:
        lines = text.split("\n")
        for line in lines:
            for p in patterns:
              if p.search(line.strip()):
                  current_speaker = "Macdonald"
                  current_page = page_num
                  cleaned_line = p.sub("", line).strip()  # ✅ safely remove the speaker intro
                  buffer = [cleaned_line] if cleaned_line else []
                  break

              elif re.match(r"^[A-Z][\w\s.'-]+:", line):  # New speaker
                  if current_speaker == "Macdonald" and buffer:
                      speech_blocks.append({
                          "page": current_page,
                          "text": " ".join(buffer)
                      })
                  buffer = []
                  current_speaker = None
              elif current_speaker == "Macdonald":
                  buffer.append(line.strip())

    # Final flush
    if current_speaker == "Macdonald" and buffer:
        speech_blocks.append({
            "page": current_page,
            "text": " ".join(buffer)
        })

    return speech_blocks

def chunk_text(text, chunk_size=CHUNK_WORDS):
    """
    Split long text into ~chunk_size word chunks.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def process_pdf_file(pdf_path):
    filename = os.path.basename(pdf_path)

    # Parse filename: hansard_debate_{parliament}_{session}_{year}[_{volume}].pdf
    filename_match = re.search(r"hansard_debate_(\d{2})_(\d{2})_(\d{4})(?:_(\d{2}))?", filename)

    if filename_match:
        parliament = int(filename_match.group(1))
        session = int(filename_match.group(2))
        year = int(filename_match.group(3))
        volume = int(filename_match.group(4)) if filename_match.group(4) else None
    else:
        # Fallback for files that don't match the expected pattern
        parliament = None
        session = None
        year_match = re.search(r"(\d{4})", filename)
        year = int(year_match.group(1)) if year_match else None
        volume = None

    text_with_pages = extract_text_from_pdf(pdf_path)
    speeches = extract_macdonald_speech_blocks(text_with_pages)

    all_chunks = []
    for speech in speeches:
        chunks = chunk_text(speech["text"])
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                "speaker": "John A. Macdonald",
                "parliament": parliament,
                "session": session,
                "year": year,
                "source": filename,
                "page": speech["page"],
                "chunk_index": i,
                "content": chunk
            }

            # Only add volume if it exists
            if volume is not None:
                chunk_metadata["volume"] = volume

            all_chunks.append(chunk_metadata)

    return all_chunks

def main():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    pdf_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(".pdf")]

    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        pdf_path = os.path.join(INPUT_FOLDER, pdf_file)
        chunks = process_pdf_file(pdf_path)

        out_file = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(pdf_file)[0]}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2)

        print(f"✔ Extracted {len(chunks)} chunks from {pdf_file}")

if __name__ == "__main__":
    main()
