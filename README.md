# Multi-Model AI Chatbot with Streaming, File Handling, and Flask Backend

A versatile web-based chatbot application supporting multiple Large Language Models (LLMs) including OpenAI (GPT, O1), Anthropic (Claude), and Google (Gemini). It features real-time streaming responses (where available), conversation management (save, load, reset), Markdown rendering with code highlighting and MathJax support, and a unique integrated file viewer to load local file contents directly into the chat context.

## Table of Contents

- [Features](#features)
- [Demo](#demo)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
  - [Updating Requirements](#updating-requirements)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Accessing the Chatbot](#accessing-the-chatbot)
  - [Selecting a Model](#selecting-a-model)
  - [Interacting with the Chatbot](#interacting-with-the-chatbot)
  - [Using the File Viewer](#using-the-file-viewer)
  - [Using Conversation Consolidation](#using-conversation-consolidation)
  - [Managing Conversations](#managing-conversations)
  - [Server Shutdown](#server-shutdown)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
  - [Backend (Flask)](#backend-flask)
  - [Frontend (Main Chat)](#frontend-main-chat)
  - [Frontend (File Viewer)](#frontend-file-viewer)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Features

-   **Multi-Model Support:** Interact with various LLMs:
    -   OpenAI: `gpt-4o-latest`, `gpt-4o`, `gpt-4.5-preview`, `o1-pro`, `o1`, `o3-mini`
    -   Anthropic: `claude-3-7-sonnet-20250219`
    -   Google: `gemini-2.0-flash-thinking-exp-01-21`, `gemini-2.5-pro-exp-03-25`
-   **Real-Time Streaming:** Receive responses as they are generated for supported models (most GPT, Claude, Gemini models).
-   **File Viewer & Loader:** Browse local directories (via a server-side dialog), select relevant code/text files (`.py`, `.js`, `.html`, `.css`, `.md`, `.txt`, etc.), and load their concatenated content directly into the chat context for analysis or modification.
-   **Conversation Management:**
    -   Save conversations (both message history in JSON and full chat log in Markdown).
    -   Load previous conversations into a new session.
    -   Reset the current conversation branch while preserving history.
-   **Conversation Consolidation:** Start a new chat session pre-filled with a prompt to consolidate, refactor, critique, or summarize the previous conversation, especially useful after loading project files.
-   **Rich Text Rendering:** Displays responses with Markdown formatting, syntax highlighting for code blocks (via Highlight.js), and mathematical equations (via MathJax).
-   **Model-Specific Features:** Toggle Anthropic's "Extended Thinking" feature.
-   **Convenient UI:**
    -   Editor/Preview split view.
    -   Auto-resizing input text area.
    -   "Copy" buttons for the user prompt (including loaded file content) and individual code blocks in the response.
    -   Model selection dropdown.
-   **Server-Side Sessions:** Manages conversation history per browser tab/session using unique IDs.
-   **Configurable System Prompt:** Easily modify the initial system message in `app.py`.
-   **Graceful Shutdown:** Option to terminate the server from the UI.

## Demo

![Chatbot Interface](scrennshot.png)

## Installation

### Prerequisites

-   **Python 3.7 or higher**
-   **pip** (Python package installer)
-   **Git** (for cloning the repository)
-   **(Optional) Tkinter:** Required by the backend for the "Open Folder" dialog. This is usually included with standard Python installations, but might need separate installation on some minimal Linux environments (`sudo apt-get install python3-tk`).

### Setup

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/EjayNg-AI/openai-flask-chatbot.git
    cd openai-flask-chatbot
    ```

2.  **Create a Virtual Environment**

    It's highly recommended to use a virtual environment.

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\\Scripts\\activate
    ```

3.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables**

    Create a `.env` file in the project root directory. Add the necessary API keys for the models you intend to use and a Flask secret key.

    ```env
    FLASK_SECRET_KEY=your_strong_random_flask_secret_key
    OPENAI_API_KEY=your_openai_api_key_here
    ANTHROPIC_API_KEY=your_anthropic_api_key_here
    GEMINI_API_KEY=your_google_gemini_api_key_here
    ```

    -   `FLASK_SECRET_KEY`: A long, random string for securing Flask sessions. Generate one if needed.
    -   You only need to provide API keys for the services you plan to use. The application will skip initialization for services without a key.

5.  **Run the Application**

    ```bash
    python app.py
    ```

    The server will start using Waitress on `http://127.0.0.1:5000/`.

### Updating Requirements

```text
anthropic==0.49.0
Flask==3.1.0
flask-cors==5.0.1
Flask-Session==0.8.0
google==3.0.0
google-auth==2.38.0
google-genai==1.8.0
openai==1.68.2
python-dotenv==1.0.1
waitress==3.0.2
```
## Configuration

-   **API Keys & Secret Key:** Configure in the `.env` file as described in the Installation section.
-   **System Prompt:** The initial instruction given to the chatbot can be modified by changing the `SYSTEM_MESSAGE` constant at the top of `app.py`.
-   **Conversation Storage:** Conversations are saved in the `conversations/` directory, which is created automatically. Saved files include:
    -   `[name]messages.json`: Only the user/assistant messages (used for loading).
    -   `[name].md`: The full chat log rendered as Markdown.
    -   `[name]all.json`: Internal representation of all messages including system prompts and history branches (used for debugging/internal state).
-   **Allowed File Extensions:** The file types displayed in the File Viewer are controlled by the `allowed_extensions` set within the `get_directory_structure` function in `app.py`.

## Usage

### Accessing the Chatbot

Navigate to `http://127.0.0.1:5000/` in your web browser. Each browser tab will maintain its own independent session and conversation history.

### Selecting a Model

-   Use the dropdown menu at the top-left to choose the desired LLM.
-   Click the **"Select Model"** button to apply the change to the current session. The selected model and streaming status will be logged in the editor pane.
-   For Claude models, you can check/uncheck the **"Claude Extended Thinking"** checkbox to enable/disable the thinking feature (sends the change to the backend).

### Interacting with the Chatbot

1.  **Enter Your Query:** Type your question or prompt in the text area below the control panel. The area will auto-resize as you type.
2.  **Add File Context (Optional):** Use the [File Viewer](#using-the-file-viewer) to load content from local files. This content will be appended to your *next* prompt when you click "Submit". Use the "Copy" button next to the input area to verify the full prompt (including file content) that will be sent.
3.  **Submit:** Click the **"Submit"** button or press `Ctrl + Enter`.
4.  **View Response:** The response will appear in the editor (raw text) and preview (rendered Markdown/code/math) panes. For streaming models, the response appears token by token.
5.  **Copy Code:** Use the "Copy" button that appears on code blocks in the preview pane.

### Using the File Viewer

1.  Click the **"File Viewer"** button in the top controls. This opens a new browser window/tab (`/filecontents`).
2.  In the new window, click **"Open Folder"**. A *native OS folder selection dialog* will appear (triggered by the backend via Tkinter). Select the project folder you want to browse.
3.  The left panel will populate with a directory tree, showing only files with allowed extensions (e.g., `.py`, `.js`, `.html`, `.css`, `.md`, `.txt`).
4.  Check the boxes next to the files whose content you want to load.
5.  Click **"Load Selection"**. The concatenated content of the selected files (with separators indicating file paths) will appear in the right panel of the File Viewer window.
6.  Simultaneously, this concatenated content is sent back to the *main chat window* and stored internally. It will be automatically appended to the *next* prompt you submit in the main chat window.
7.  You can use the **"Refresh"** button in the File Viewer to reload the directory structure if files have changed.
8.  Close the File Viewer window when done. The loaded content remains available in the main chat window until you submit the next prompt or refresh the main page.

### Using Conversation Consolidation

1.  After having a conversation (potentially involving loaded files), select a task from the **Consolidate dropdown** (e.g., "Fully Updated Files", "Refactor Code", "Critique Code", "Synopsis of Project").
2.  Click the **"Consolidate"** button.
3.  A *new chat tab/window* will open. It inherits the *entire conversation history* from the previous tab.
4.  The query input in the new tab will be pre-filled with a detailed prompt corresponding to the selected consolidation task.
5.  You can edit the prompt if needed, then click **"Submit"** to have the AI perform the consolidation task based on the conversation history.

### Managing Conversations

-   **Save:** Click **"Save"**. Enter a name when prompted. Saves the current conversation state (`messages.json`, `all.json`) and a Markdown log (`.md`) to the `conversations/` directory.
-   **Load:** Click **"Load"**. Enter the name of a previously saved conversation. A *new browser tab* will open, loading the message history from the corresponding `[name]messages.json` file.
-   **Reset:** Click **"Reset"**. Clears the current editor/preview panes and starts a new conversation branch within the *same session*. The previous turns are still stored in the backend history for this session ID but won't be sent in subsequent requests unless loaded again.
-   **Clear Screen:** Click **"Clear Screen"**. Clears the editor and preview panes *visually* but does not affect the backend conversation history like "Reset" does.

### Server Shutdown

-   Click the **"Close"** button. This sends a request to the `/shutdown` endpoint.
-   The backend saves the final state of all active sessions' message history to timestamped files in `conversations/` and then terminates the Python process.
-   **Warning:** Use this primarily in development. Exposing a shutdown endpoint like this is generally unsafe in production.

## Project Structure

```
openai-flask-chatbot/
├── app.py              # Main Flask application, API logic, LLM clients
├── templates/
│   ├── index.html      # Main chat interface HTML/CSS/JS
│   └── index2.html     # File Viewer interface HTML/CSS/JS
├── conversations/      # Directory to store saved conversations (.json, .md)
├── .env                # Environment variables (API keys, Flask secret) - Gitignored
├── requirements.txt    # Python dependencies
├── app.log             # Log file (created automatically)
└── README.md           # This file
```

## How It Works

### Backend (Flask)

-   **Web Server:** Uses Flask and Waitress to serve HTML pages and handle API requests.
-   **API Clients:** Initializes clients for OpenAI, Anthropic, and Google GenAI based on provided API keys.
-   **Routing:** Defines endpoints for the main page (`/`), streaming (`/stream`), saving (`/save`), loading (`/load`), resetting (`/reset`), model selection (`/select_model`), Claude thinking toggle (`/update-claude-thinking`), file viewer (`/filecontents`), folder opening (`/open_folder`), file loading (`/load_selection`), refreshing (`/refresh`), consolidation (`/consolidate`), and shutdown (`/shutdown`).
-   **Streaming:** Uses Server-Sent Events (SSE) via `stream_with_context` to send chunks of data from the LLM APIs to the frontend in real-time. Handles different streaming mechanisms for each provider.
-   **Session Management:** Uses Flask-Session with a filesystem backend to manage unique session IDs (`uniqueId`) and store conversation history per session. A global list `message_accumulate` stores messages tagged with `(uniqueId, counter)`.
-   **Conversation State:** Tracks conversation turns using a `counter`. Resetting increments the counter to branch the history.
-   **File Handling:**
    -   Uses `tkinter.filedialog.askdirectory` (server-side) to allow users to select a local folder securely.
    -   Recursively scans the selected directory, filtering for allowed file extensions.
    -   Reads selected files and concatenates their content.
-   **Logging:** Basic logging configured to `app.log`.

### Frontend (Main Chat - `index.html`)

-   **Structure:** HTML defines the layout (model controls, input panel, editor/preview panes). CSS provides styling.
-   **JavaScript Logic:**
    -   Fetches a unique session ID (`uniqueId`) on load.
    -   Handles user input (query text area, button clicks).
    -   Manages model selection and feature toggles (e.g., Claude thinking).
    -   Initiates SSE connection to `/stream` for receiving responses.
    -   Updates the editor pane with raw text and the preview pane with rendered HTML (using Marked.js, Highlight.js, MathJax).
    -   Communicates with the backend for save, load, reset, shutdown actions.
    -   Opens the File Viewer (`/filecontents`) in a new window.
    -   Includes an `updateFileContents` function callable by the File Viewer window (`window.opener`) to receive concatenated file content.
    -   Handles the "Consolidate" workflow by opening a new tab with inherited history and a pre-filled prompt.

### Frontend (File Viewer - `index2.html`)

-   **Structure:** Simple two-panel layout (directory tree/controls, content preview).
-   **JavaScript Logic:**
    -   Communicates with backend endpoints (`/open_folder`, `/refresh`, `/load_selection`).
    -   Dynamically builds the directory tree view based on data from the backend.
    -   Tracks selected files.
    -   Displays concatenated file content received from `/load_selection`.
    -   Uses `window.opener.updateFileContents(data.result)` to send the loaded content back to the main chat window that opened it.

## Troubleshooting

-   **API Errors:** Ensure the correct API keys are in the `.env` file and that they are valid and have necessary permissions/credits with the respective providers (OpenAI, Anthropic, Google). Check `app.log` for specific error messages from the API clients.
-   **Tkinter/Folder Dialog Issues:** The "Open Folder" button relies on Tkinter running on the *server*. This may fail in headless environments (like some Docker containers or SSH sessions without X11 forwarding). Ensure Tkinter is installed and accessible in the server environment.
-   **File Viewer Doesn't Update Main Window:** Ensure the main chat window (`index.html`) remains open while using the File Viewer (`index2.html`). Browser security might prevent communication if the opener window is closed or navigated away. Check the browser's developer console in both windows for errors related to `window.opener`.
-   **Dependencies:** Make sure all dependencies in the updated `requirements.txt` are installed correctly in your virtual environment.
-   **Port Conflicts:** If port `5000` is already in use, modify the `serve(app, host='127.0.0.1', port=5000)` line at the bottom of `app.py` to use a different port.
-   **Permissions:** The application needs write permissions in the project directory to create the `conversations/` folder and save files, and to write to `app.log`.

## License

This project is licensed under the MIT License. See the LICENSE file for details (if one exists, otherwise assume standard MIT terms).

---

**Disclaimer:** This application interacts with external APIs and local files. Ensure you understand the security implications. Handle API keys securely and be cautious when allowing applications to access local file system data, even indirectly via server-side dialogs. The shutdown feature is intended for development convenience and should be removed or secured in production.