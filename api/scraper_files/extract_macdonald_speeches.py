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
    Split long text into chunks of roughly `chunk_size` words, but respects
    sentence boundaries.
    """
    # A simple sentence splitter. It's not perfect but better than splitting mid-sentence.
    # It splits on '.', '?', '!' followed by a space.
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if not sentences:
        return []

    chunks = []
    current_chunk_sentences = []
    current_chunk_word_count = 0

    for sentence in sentences:
        # Skip empty strings that can result from splitting
        if not sentence:
            continue

        sentence_word_count = len(sentence.split())

        # If the current chunk is empty and the new sentence is already too long,
        # just add it as its own chunk.
        if not current_chunk_sentences and sentence_word_count > chunk_size:
            chunks.append(sentence)
            continue

        # If adding the next sentence would push the chunk over the size limit,
        # finalize the current chunk and start a new one.
        if current_chunk_word_count + sentence_word_count > chunk_size:
            chunks.append(" ".join(current_chunk_sentences))
            current_chunk_sentences = [sentence]
            current_chunk_word_count = sentence_word_count
        else:
            current_chunk_sentences.append(sentence)
            current_chunk_word_count += sentence_word_count

    # Add the last remaining chunk
    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))

    return chunks

def process_pdf_file(pdf_path):
    filename = os.path.basename(pdf_path)

    # --- Improved metadata extraction from filename ---
    parliament, session, year, volume = None, None, None, None

    # Pattern 1: hansard_debate_{parliament}_{session}_{year}[_{volume}].pdf
    pattern1 = r"hansard_debate_(\d{2})_(\d{2})_(\d{4})(?:_(\d{2}))?"
    match1 = re.search(pattern1, filename, re.IGNORECASE)

    # Pattern 2: oop.debates_HOC{parliament}{session}_{part}.pdf
    pattern2 = r"oop\.debates_HOC(\d{2})(\d{2})_(\d{2})"
    match2 = re.search(pattern2, filename, re.IGNORECASE)

    if match1:
        parliament = int(match1.group(1))
        session = int(match1.group(2))
        year = int(match1.group(3))
        volume = int(match1.group(4)) if match1.group(4) else None
    elif match2:
        # This pattern is based on the example PDF and assumes its structure.
        # It seems to lack a year, which is important metadata.
        print(f"⚠️  Filename '{filename}' matches a pattern without a year. Year metadata will be missing.")
        parliament = int(match2.group(1))
        session = int(match2.group(2))
        volume = int(match2.group(3)) # Assuming the last part is a volume/part number
    else:
        # Fallback: try to find any 4-digit year in the filename.
        print(f"⚠️  Filename '{filename}' does not match known patterns. Attempting fallback year extraction.")
        year_match = re.search(r"(\d{4})", filename)
        year = int(year_match.group(1)) if year_match else None
    # --- End of improvement ---

    text_with_pages = extract_text_from_pdf(pdf_path)
    speeches = extract_macdonald_speech_blocks(text_with_pages)

    all_chunks = []
    # Use a single counter for chunk_index across the entire PDF to ensure uniqueness
    # when Macdonald has multiple speeches on the same page.
    chunk_counter = 0
    for speech in speeches:
        chunks = chunk_text(speech["text"])
        for chunk in chunks:
            chunk_metadata = {
                "speaker": "John A. Macdonald",
                "parliament": parliament,
                "session": session,
                "year": year,
                "source": filename,
                "page": speech["page"],
                "chunk_index": chunk_counter, # Use the unique counter
                "content": chunk
            }

            # Only add volume if it exists
            if volume is not None:
                chunk_metadata["volume"] = volume

            all_chunks.append(chunk_metadata)
            chunk_counter += 1 # Increment for the next chunk

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

        print(f"[SUCCESS] Extracted {len(chunks)} chunks from {pdf_file}")

if __name__ == "__main__":
    main()
