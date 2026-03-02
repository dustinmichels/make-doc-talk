import argparse
import os
import sys
import ollama

# Configuration
LLM_MODEL = "llama3.2:3b"


def clean_text_with_llm(raw_text):
    print("Stage 2: Cleaning text with Ollama...")
    chunk_size = 2000
    cleaned_chunks = []

    total_chunks = (len(raw_text) + chunk_size - 1) // chunk_size

    for i in range(0, len(raw_text), chunk_size):
        chunk = raw_text[i : i + chunk_size]
        current_chunk = (i // chunk_size) + 1
        print(f"  Processing chunk {current_chunk}/{total_chunks}...")

        try:
            response = ollama.chat(
                model=LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional editor. Remove citations, page numbers, and image captions. Join words split by hyphens. Do not change the content. Retain headers. Do not add any text.",
                    },
                    {"role": "user", "content": f"Clean this for TTS: \n\n{chunk}"},
                ],
            )
            cleaned_chunks.append(response["message"]["content"])
        except Exception as e:
            print(f"  Error processing chunk {current_chunk}: {e}")
            # Fallback to original chunk if LLM fails (to avoid data loss)
            cleaned_chunks.append(chunk)

    return " ".join(cleaned_chunks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stage 2: Refine extracted text")
    parser.add_argument(
        "pdf_path",
        help="Path to the original PDF file (used to locate output directory)",
    )

    args = parser.parse_args()

    # Locate the output directory
    pdf_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
    output_dir = os.path.join("out", pdf_name)
    input_path = os.path.join(output_dir, "extracted.txt")

    if not os.path.exists(output_dir):
        print(
            f"Error: Directory '{output_dir}' does not exist. Please run step 1 first."
        )
        sys.exit(1)

    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found. Please run step 1 first.")
        sys.exit(1)

    print(f"Reading from {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        raw_content = f.read()

    refined_content = clean_text_with_llm(raw_content)

    output_path = os.path.join(output_dir, "refined.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(refined_content)

    print(f"Success! Refined text saved to {output_path}")
