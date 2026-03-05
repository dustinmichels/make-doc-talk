# Make-Doc-Talk

## Install

```sh
# install mise (anywhere)
curl https://mise.run | sh
```

Inside this project:

```sh
# install python, uv, bun, and rust
mise use

# install python stuff
uv sync

# change to app directory
cd app

# install frontend stuff
bun install

# run it
bun run tauri dev
```

## Dev

```sh
cd app && bun tauri dev
```

```sh
uv run uvicorn backend.main:app --reload
```

| Command                      | Description                                         |
| ---------------------------- | --------------------------------------------------- |
| `cd app && bun run dev:all`  | Run Vite dev server + Python backend together       |
| `cd app && bun run dev:test` | Same, but injects a fake LLM model name for testing |
| `cd app && bun tauri dev`    | Full Tauri desktop app (uses `beforeDevCommand`)    |

## Environment Variables

The Python backend reads the following environment variables at startup. Copy `.env.template` to `.env` and fill in values as needed.

| Variable    | Default           | Description                                                                                                                                                                                                                                                                   |
| ----------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `LLM_MODEL` | _(auto-detected)_ | Override the Ollama model used for text refinement. If unset, the backend scans installed Ollama models and picks the first match from its known-models list. Set to a fake name (e.g. `llama3.2:3b-fake-for-testing`) to force an error and confirm the override path works. |

### Inline override (no .env file needed)

```sh
LLM_MODEL=llama3.2:3b cd app && bun run dev:all
```

Or use the pre-configured test script:

```sh
cd app && bun run dev:test
```

## Testing the API

```sh
uv run python app/src-python/main.py

# Stage 1 — Extract
curl -X POST http://localhost:8000/jobs/test1/extract \
    -F "pdf=@/Users/dustinmichels/GitRepos/pdf-to-speech/sample-pdfs/just_sustainabilities_pg1.pdf"

# Stage 2 — Refine
curl -X POST http://localhost:8000/jobs/test1/refine

# Stage 3 — TTS
curl -X POST http://localhost:8000/jobs/test1/tts
```

## More

```sh
cd app
bun install
bun run tauri android init
bun run tauri ios init

# For Desktop development, run:
bun run tauri dev

# For Android development, run:
bun run tauri android dev

# For iOS development, run:
bun run tauri ios dev
```

## Install Kokoro TTS

```sh
# Download voice data (bin format is preferred)
wget https://github.com/nazdridoy/kokoro-tts/releases/download/v1.0.0/voices-v1.0.bin

# Download the model
wget https://github.com/nazdridoy/kokoro-tts/releases/download/v1.0.0/kokoro-v1.0.onnx
```
