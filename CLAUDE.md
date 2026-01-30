# Claude Code Instructions

This document provides instructions for Claude Code when working on this repository.

## Project Overview

This is a multi-model AI chatbot built with Flask. The project has two parallel versions:

1. **Original files** - Full-featured version supporting multiple LLM providers
2. **New files** (`*_new.*`) - Trimmed version supporting only OpenAI o3 and o1-pro models

## File Structure

### Original Files (DO NOT MODIFY)

| File | Purpose |
|------|---------|
| `app.py` | Original backend with all models (GPT-4o, GPT-4.1, o3, o4-mini, o3-mini, o1-pro, Claude, Gemini) |
| `templates/index.html` | Original frontend with full model selection |
| `templates/index2.html` | Original file viewer |

### New Files (Active Development)

| File | Purpose |
|------|---------|
| `app_new.py` | Trimmed backend - only o3 and o1-pro models |
| `templates/index_new.html` | Trimmed frontend - only o3 and o1-pro in dropdown |
| `templates/index2_new.html` | File viewer for new version |

## Critical Rules

### 1. Preserve Original Files

**NEVER modify the following files:**
- `app.py`
- `templates/index.html`
- `templates/index2.html`

These files serve as reference implementations. All new development should occur in the `*_new.*` files.

### 2. When Making Changes

- All backend changes go in `app_new.py`
- All frontend changes go in `templates/index_new.html` or `templates/index2_new.html`
- If you need to reference original implementation, read from `app.py` or `templates/index.html`

### 3. Running the Application

To run the new trimmed version:
```bash
python app_new.py
```

To run the original full version:
```bash
python app.py
```

## Current State of New Files

### `app_new.py`

- **Supported models**: `o3`, `o1-pro` only
- **API**: OpenAI Responses API (non-streaming)
- **Both models use**: `store=True`, `reasoning={"effort": "high"}`
- **Removed**: Anthropic client, Gemini client, Claude thinking flag
- **Default model**: `o3`

### `templates/index_new.html`

- **Model dropdown**: Only `o3` and `o1-pro` options
- **Removed**: Claude Extended Thinking checkbox
- **Streaming**: Hardcoded to `false` (both models use non-streaming)

## Adding New Features

When adding new functionality:

1. First check if similar functionality exists in the original files
2. Implement changes only in the `*_new.*` files
3. Test thoroughly before considering backporting to original files
4. Document any new endpoints or features in this file

## API Endpoints (New Version)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main chat interface |
| `/get-token` | GET | Generate unique session token |
| `/stream` | GET | Process prompt and return response |
| `/select_model` | POST | Change active model |
| `/save` | POST | Save conversation |
| `/autosave` | POST | Auto-save conversation |
| `/load` | GET | Load previous conversation |
| `/reset` | POST | Reset conversation |
| `/shutdown` | POST | Shutdown server |
| `/filecontents` | GET | File viewer interface |
| `/open_folder` | POST | Open folder picker |
| `/load_selection` | POST | Load selected files |
| `/update-math-render` | POST | Toggle math rendering |

## Notes

- The new version removes all streaming logic since both o3 and o1-pro use the OpenAI Responses API which returns complete responses
- Session management and conversation persistence work identically to the original
- File viewer functionality is preserved unchanged
