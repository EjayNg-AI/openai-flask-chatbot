# Repository Guidelines

## Project Structure & Module Organization
- `app.py` is the Flask entry point that manages LLM routing, streaming, file loading, and session storage; keep server-side changes centralized here.
- `templates/` contains the Jinja2 front-end (`index.html` for the chat UI, `index2.html` for the file viewer); extract shared widgets into partials instead of copying between files.
- `html_files_vibe_coded/` holds experimental static mocks; production assets should remain under `templates/` or a future `static/` folder.
- `requirements.txt`, `.env`, and the auto-created `conversations/` directory (JSON/Markdown transcripts) sit at the repo root.

## Build, Test, and Development Commands
- `python app.py` launches the development server via Waitress with auto-reload; the app picks an open port starting at 5000, so watch the console output.
- `OPENAI_API_KEY=... python app.py --openai` restricts startup to a specific provider; pass `--anthropic` or `--gemini` for vendor-specific debugging.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation; module-level constants (e.g., `SYSTEM_MESSAGE`) stay upper snake case, while helper functions use descriptive snake case.
- Favor cohesive helpers in `app.py` and keep UI changes within the matching Jinja template; mirror element IDs and classes when wiring JS events.
- When adding configuration, load values through `dotenv` and guard them with informative error logs rather than silent defaults.

## Testing Guidelines
- No automated test suite is present; at minimum, start the app (`python app.py`), exercise model selection, file loading, and conversation saving, and check `app.log` for errors.
- For UI changes, verify SSE streaming in a second browser tab and confirm that transcripts appear under `conversations/*.json` and `.md`.
- When adding new endpoints, stub unit tests with `pytest` or Flask’s test client and keep fixtures under `tests/` once introduced.

## Closing the session

- When the user identicates that the codex session can be closed, update README.md file with the changes made and then confirm that session can be safely exited.
