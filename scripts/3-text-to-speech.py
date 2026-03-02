import argparse
import os
import sys
import soundfile as sf
from kokoro_onnx import Kokoro
from pydub import AudioSegment
import re

# Configuration
VOICE_NAME = "af_sky"
KOKORO_MODEL = "models/kokoro-v1.0.onnx"
VOICES_BIN = "models/voices-v1.0.bin"


def generate_tts(text, output_file):
    print("Stage 3: Generating audio with Kokoro...")

    # Validation
    if not os.path.exists(KOKORO_MODEL):
        print(f"Error: Kokoro model not found at '{KOKORO_MODEL}'")
        sys.exit(1)
    if not os.path.exists(VOICES_BIN):
        print(f"Error: Voices bin not found at '{VOICES_BIN}'")
        sys.exit(1)

    try:
        kokoro = Kokoro(KOKORO_MODEL, VOICES_BIN)
    except Exception as e:
        print(f"Error initializing Kokoro: {e}")
        sys.exit(1)

    # Smart text splitting to ensure chunks are < 510 phonemes (using ~400 characters as a safe limit)
    def split_text_smart(text, max_len=400):
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        # 1. Split by major punctuation (. ? !)
        # re.split includes the separators in the list if captured
        parts = re.split(r"([.!?]+)", text)
        sentences = []
        current = ""

        for part in parts:
            if re.match(r"^[.!?]+$", part):
                current += part
                sentences.append(current.strip())
                current = ""
            else:
                current += part

        if current.strip():
            sentences.append(current.strip())

        # 2. Process chunks that are still too long
        final_chunks = []
        for sent in sentences:
            if not sent.strip():
                continue

            if len(sent) <= max_len:
                final_chunks.append(sent)
            else:
                # Split by commas and semicolons if too long
                sub_parts = re.split(r"([,;:]+)", sent)
                current_sub = ""
                for sub in sub_parts:
                    if len(current_sub) + len(sub) <= max_len:
                        current_sub += sub
                    else:
                        if current_sub.strip():
                            final_chunks.append(current_sub.strip())
                        current_sub = sub
                if current_sub.strip():
                    final_chunks.append(current_sub.strip())

        # 3. Last resort: split by words
        really_final_chunks = []
        for chunk in final_chunks:
            if len(chunk) <= max_len:
                really_final_chunks.append(chunk)
            else:
                words = chunk.split(" ")
                current_word_chunk = ""
                for word in words:
                    if len(current_word_chunk) + len(word) + 1 <= max_len:
                        current_word_chunk += word + " "
                    else:
                        if current_word_chunk.strip():
                            really_final_chunks.append(current_word_chunk.strip())
                        current_word_chunk = word + " "
                if current_word_chunk.strip():
                    really_final_chunks.append(current_word_chunk.strip())

        return really_final_chunks

    sentences = split_text_smart(text)
    combined_audio = AudioSegment.empty()
    total_sentences = len(sentences)

    print(f"  Processing {total_sentences} chunks/sentences...")

    for i, sentence in enumerate(sentences):
        if not sentence.strip():
            continue

        # Helper logging
        if (i + 1) % 10 == 0:
            print(f"  Chunk {i + 1}/{total_sentences}...")

        try:
            # Add punctuation if missing (helps TTS prosody)
            text_to_process = sentence
            if not text_to_process.endswith((".", "!", "?", ";", ":")):
                text_to_process += "."

            samples, sample_rate = kokoro.create(
                text_to_process, voice=VOICE_NAME, speed=1.0
            )

            temp_chunk = f"temp_{i}.wav"
            sf.write(temp_chunk, samples, sample_rate)
            combined_audio += AudioSegment.from_wav(temp_chunk)
            os.remove(temp_chunk)
        except Exception as e:
            print(
                f"  Warning: Error generating audio for chunk '{sentence[:20]}...': {e}"
            )

    combined_audio.export(output_file, format="wav")
    print(f"Success! Audio saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stage 3: Convert text to speech")
    parser.add_argument(
        "pdf_path",
        help="Path to the original PDF file (used to locate output directory)",
    )
    args = parser.parse_args()

    # Locate the output directory
    pdf_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
    output_dir = os.path.join("out", pdf_name)
    input_path = os.path.join(output_dir, "refined.txt")

    if not os.path.exists(output_dir):
        print(
            f"Error: Directory '{output_dir}' does not exist. Please run steps 1 and 2."
        )
        sys.exit(1)

    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found. Please run step 2 first.")
        sys.exit(1)

    print(f"Reading from {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    output_path = os.path.join(output_dir, "audiobook.wav")
    generate_tts(text, output_path)
