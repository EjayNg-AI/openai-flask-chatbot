Unique Session ID: 2254b95a-310c-4379-a7ab-d7b6eef65b7a

Model: gemini-2.5-pro-preview-03-25

**Model:** gemini-2.5-pro-preview-03-25

**Assistant:**

Okay, let's break down the core functionalities and logical flow of this Flask-based chatbot application.

**Overall Purpose:**

The project provides a web-based chat interface (`index.html`) that allows users to interact with various Large Language Models (LLMs) like OpenAI's GPT models, Anthropic's Claude, and Google's Gemini. It includes features for managing conversation history, selecting models, rendering Markdown and MathJax, and crucially, incorporating the content of local files into the chat context via a separate file viewer interface (`index2.html`).

**Core Components:**

1.  **`app.py` (Flask Backend):**

    - **Web Server:** Handles HTTP requests, serves HTML templates, and manages API endpoints.
    - **LLM Interaction:** Initializes and interacts with different LLM clients (OpenAI, Anthropic, Gemini) based on user selection. Handles API key management via environment variables.
    - **Session Management:** Uses Flask-Session (filesystem-based) to maintain some user-specific state, although the primary conversation history is managed globally.
    - **Conversation History Management:**
      - Uses a global list `message_accumulate` to store _all_ conversation turns from _all_ sessions, indexed by a unique session ID (`unique_id`) and a counter. This allows for features like "Reset" (incrementing the counter) and potentially "Consolidate".
      - Generates unique session IDs (`uuid.uuid4`) via the `/get-token` endpoint.
      - Retrieves specific conversation histories (`get_conversation_history`) based on `unique_id` and counter before sending to the LLM.
      - Saves/Loads conversation history (messages only) to/from JSON files (`/save`, `/load`). Saves the full Markdown view as well.
    - **File Handling Logic:**
      - Provides endpoints (`/open_folder`, `/refresh`) to scan local directories (using Tkinter for the dialog) and build a file/folder structure JSON, filtering for specific extensions.
      - Provides an endpoint (`/load_selection`) to receive a list of selected file paths from the file viewer. It reads these files, formats them (`--- FILE: path --- content ---`), concatenates them, and stores the result in the global variable `global_file_contents`.
      - Provides an endpoint (`/get_file_contents`) for the main chat UI to fetch the currently loaded file content.
      - Provides an endpoint (`/clear_loaded_content`) to clear the `global_file_contents`.
    - **State Management:** Manages global flags like `model_name`, `claude_thinking_flag`, `math_render_flag`, `consolidate_conversation_flag`, etc., updated via specific endpoints.
    - **Streaming:** Supports streaming responses from LLMs that offer it, sending chunks back to the frontend via Server-Sent Events (SSE).
    - **Server Management:** Includes shutdown logic (`/shutdown`) and finds an available port to run the Waitress production server.

2.  **`templates/index.html` (Main Chat UI):**

    - **User Interface:** Provides the primary chat window with:
      - Model selection dropdown and controls (Claude Thinking, Math Render).
      - Control panel with input textarea (`query-input`) and action buttons (Submit, Copy Prompt, Clear, Load, Save, Reset, Close, File Viewer, Consolidate, Sanitize, Dark Mode).
      - A split view showing the raw Markdown conversation (`editor`) and the rendered HTML preview (`preview`).
    - **Frontend Logic (JavaScript):**
      - Fetches a unique session token (`uniqueId`) from `/get-token` on load.
      - Handles user input and button clicks.
      - Sends prompts, token, and model name to the `/stream` endpoint.
      - Receives streaming/non-streaming responses from the backend, appends them to the editor textarea.
      - Renders Markdown (using `marked.js`), code blocks (using `highlight.js`), and potentially math formulas (using `MathJax`) in the preview pane.
      - Adds "Copy" buttons to code blocks.
      - Communicates with backend endpoints for actions like saving (`/save`), loading (`/load`), resetting (`/reset`), selecting models (`/select_model`), changing flags (`/update-...`), etc.
      - Opens the file viewer (`/filecontents`) in a new window.
      - Includes a `updateFileContents` function intended to be called by the file viewer window (`window.opener`) to receive concatenated file data (though the "Copy Prompt" button fetches this directly from `/get_file_contents`).
      - Handles sanitizing HTML tags in the editor content.

3.  **`templates/index2.html` (File Viewer UI):**
    - **User Interface:** Provides a separate window/tab with:
      - A left panel containing buttons (Open Folder, Load Selection, Refresh, Clear) and a collapsible directory tree view.
      - A right panel (`output`) to display the concatenated content of selected files.
    - **Frontend Logic (JavaScript):**
      - Handles the "Open Folder" action by calling the `/open_folder` backend endpoint, which uses Tkinter to show a native dialog.
      - Receives the directory structure JSON from the backend and dynamically builds the interactive tree view (`createTree`).
      - Tracks selected files (via checkboxes) in the `selectedFiles` array.
      - Handles the "Load Selection" action by sending the `selectedFiles` array to `/load_selection`.
      - Receives the concatenated file content from `/load_selection`, displays it in the right panel, and attempts to send it back to the main chat window using `window.opener.updateFileContents`.
      - Handles "Refresh" and "Clear Loaded Content" actions, interacting with the corresponding backend endpoints and updating its own UI / calling the opener window.

**Logical Flow:**

1.  **Initialization:**

    - User navigates to the root URL (`/`).
    - `app.py` serves `index.html`.
    - `index.html` JS fetches a unique token and initial model info from `/get-token`. Backend initializes state for this token in `message_accumulate`. UI buttons are enabled.

2.  **Chat Interaction:**

    - User types a query in `index.html`.
    - User clicks "Submit".
    - JS sends the query, token, and model name to `/stream`.
    - Backend (`/stream`) retrieves `global_file_contents`. Appends user query + file contents to `message_accumulate`. Retrieves history for the token.
    - Backend formats the history and calls the selected LLM API.
    - Backend streams/sends the LLM response back to `index.html`.
    - JS receives the response chunks/text, appends it to the editor (`markdown-input`).
    - After the full response, JS renders the updated Markdown in the preview pane.

3.  **Using Local Files:**

    - User clicks "File Viewer" in `index.html`.
    - A new window opens `index2.html`.
    - User clicks "Open Folder" in `index2.html`.
    - Backend (`/open_folder`) shows a dialog, scans the folder, returns the structure.
    - `index2.html` JS builds the directory tree.
    - User selects files via checkboxes.
    - User clicks "Load Selection".
    - `index2.html` JS sends file paths to `/load_selection`.
    - Backend reads files, concatenates content, stores it in `global_file_contents`, returns the content.
    - `index2.html` JS displays content and calls `window.opener.updateFileContents` (though the main window primarily relies on the backend state).
    - The _next_ chat submission from `index.html` will include the content from `global_file_contents` when `/stream` fetches it.

4.  **Session Management:**
    - **Reset:** Clears the UI in `index.html`, calls `/reset`. Backend increments the counter for the current token in `message_accumulate`, effectively starting a new conversation branch linked to the same session ID but ignoring prior turns in that branch.
    - **Save:** Prompts for a name, sends name + editor content + token to `/save`. Backend retrieves the current conversation branch history from `message_accumulate` and saves it to JSON, also saving the full Markdown content.
    - **Load:** Prompts for a name, opens `/load?name=...`. Backend reads the saved JSON history into `loaded_conversation_messages`, sets a flag. `index.html` loads, calls `/get-token`, backend sees the flag/loaded messages and initializes the _new_ token's history in `message_accumulate` with the loaded data.
    - **Consolidate:** Similar to Load, but uses the history of a _previous_ session ID to initialize the new one, often pre-filling the prompt for a specific consolidation task.
    - **Shutdown:** Saves _all_ accumulated messages, clears state, and terminates the server process.

In essence, it's a feature-rich chatbot interface that bridges LLM interaction with local file system access, using a combination of Flask backend logic, global state variables, and JavaScript-driven UIs. The use of a global `message_accumulate` list for all history across sessions is a key architectural choice enabling features like Reset and Consolidate but might have scalability implications.

**Model:** gemini-2.5-pro-preview-03-25

**Assistant:**

```python
import sys
import os
import base64
import socket
from flask import copy_current_request_context, json, Flask, render_template, request, session, jsonify, Response, stream_with_context, send_from_directory
from openai import OpenAI
import anthropic
from google import genai
from google.genai import types
from dotenv import load_dotenv
from flask_session import Session
from waitress import serve
import logging
from typing import Generator, Dict
from datetime import datetime, UTC
import uuid
import tkinter as tk
from tkinter import filedialog


# Initial system message for chatbot
SYSTEM_MESSAGE = "You are an expert in coding. " \
"Write code that is clean, efficient, modular, and well-documented. " \
"Ensure all code block are encased with triple backticks."

# Transient global variables
unique_id_1 = None
model_name_1 = None
streaming_flag_1 = False
counter_1 = 0

# Option corresponding to consolidation of conversation
selected_option_consolidate = "fully_updated"

# Flag to indicate if conversation should be consolidated
consolidate_conversation_flag = False

# Global variable to store the loaded conversation messages
loaded_conversation_messages = []

# Contents of selected files
global_file_contents = ""

# Initial model name
model_name = "chatgpt-4o-latest"

# Global variable to store the selected folder path.
selected_folder = None

# Flag to indicate if math rendering is enabled
math_render_flag = False

# Flag to indicate if Claude is thinking
claude_thinking_flag = False

# Flag to indicate if a new file is being loaded
loading_new_file = False

# Get command line arguments
arguments = sys.argv[1:]  # sys.argv[0] is the script name itself.

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# --- DEVELOPMENT SETTING FOR AUTO-RELOAD ---
# When running locally for development, setting debug=True
# enables auto-reloading for Python code AND templates.
# Set the environment variable FLASK_ENV=development or FLASK_DEBUG=1
# OR uncomment the line below:
# app.config['DEBUG'] = True

# Alternatively, Flask automatically enables debug mode if FLASK_ENV is 'development'
# You can set this environment variable before running the app:
# export FLASK_ENV=development (Linux/macOS)
# set FLASK_ENV=development (Windows CMD)
# $env:FLASK_ENV = "development" (Windows PowerShell)

# --- IMPORTANT ---
# Debug mode also enables features not suitable for production, like an
# interactive debugger in the browser. Ensure debug mode is OFF for deployment.
# Using Waitress (as in your original code) implies a production/stable environment
# where auto-reloading is typically disabled.

# Configure with strong secret key
app.secret_key = os.getenv('FLASK_SECRET_KEY') or os.urandom(24)

# Configure server-side session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)
message_accumulate = []

# Configure logging with proper error handling
logging.basicConfig(
    level=logging.DEBUG,
    filename='app.log',
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)
logger = logging.getLogger(__name__)

# Define directories
CONVERSATIONS_DIR = os.path.join(os.getcwd(), 'conversations')

# Ensure directories exist
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

# Initialize OpenAI client with error handling
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    client = OpenAI(api_key=api_key)
except Exception as e:
    if "openai" in arguments or "chatgpt" in arguments:
        logger.critical(f"Failed to initialize OpenAI client: {e}")
        raise
    else:
        logger.info("OpenAI client initialization skipped.")
        client = None  # Explicitly set client to None if initialization fails or skipped

# Initialize Anthropic client with error handling
try:
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
except Exception as e:
    if "anthropic" in arguments or "claude" in arguments:
        logger.critical(f"Failed to initialize Anthropic client: {e}")
        raise
    else:
        logger.info("Anthropic client initialization skipped.")
        anthropic_client = None  # Explicitly set client to None if initialization fails or skipped

# Initialize Gemini client with error handling
try:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    gemini_client = genai.Client(api_key=gemini_api_key)
except Exception as e:
    if "gemini" in arguments or "google" in arguments:
        logger.critical(f"Failed to initialize Gemini client: {e}")
        raise
    else:
        logger.info("Gemini client initialization skipped.")
        gemini_client = None  # Explicitly set client to None if initialization fails or skipped


def save_system_messages(timestamp, filename):
    conversation_data = {
        'messages': session['messages'],
        'last_updated': timestamp
        }
    filename = filename.replace(":","")
    conversation_path = os.path.join(CONVERSATIONS_DIR, f"{filename}.json")
    try:
        with open(conversation_path, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving user prompts: {e}")
        return jsonify({'error': 'Failed to save user prompts.'}), 500


    conversation_path = os.path.join(CONVERSATIONS_DIR, f"{filename+'all'}.json")
    try:
        with open(conversation_path, 'w', encoding='utf-8') as f:
            json.dump(message_accumulate, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving user prompts: {e}")
        return jsonify({'error': 'Failed to save user prompts.'}), 500

    return jsonify({'message': 'User prompts saved successfully.'}), 200



def determine_counter(unique_id):
    global message_accumulate
    counter = 0
    for messages in message_accumulate:
        if messages[0] == unique_id:
            if (int(messages[1]) > counter):
                counter = int(messages[1])
    return counter


def get_conversation_history(unique_id, counter):
    global message_accumulate
    conversation_history = []
    for messages in message_accumulate:
            if (messages[0] == unique_id) and (messages[1] == counter):
                conversation_history.append(messages[2])

    return conversation_history


@app.route('/')
def index() -> str:
    global message_accumulate
    global consolidate_conversation_flag
    if 'messages' not in session:
        session['messages'] = []
    # Avoid re-adding system message if session already exists
    if not any(msg['role'] == 'system' for msg in session['messages']):
        session['messages'].append({
                    "role": "system",
                    "content": SYSTEM_MESSAGE
                    })
        session.modified = True
    return render_template('index.html')


@app.route('/get-token', methods=['GET'])
def get_token():
    global message_accumulate
    global model_name
    global loaded_conversation_messages
    global loading_new_file
    global consolidate_conversation_flag
    global selected_option_consolidate
    global unique_id_1
    global model_name_1
    token = str(uuid.uuid4())
    if loading_new_file:
        for dict_msg in loaded_conversation_messages:
            message_accumulate.append([token, 1, dict_msg])
    elif consolidate_conversation_flag:
        counter_1 = determine_counter(unique_id_1)
        dd = []
        for dict_msg in message_accumulate:
            if (dict_msg[0] == unique_id_1) and (dict_msg[1] == counter_1):
                dd.append(dict_msg[2])
        for msg in dd:
            message_accumulate.append([token, 1, msg])
    else:
        # Check if a system message for this token/counter already exists
        # This check might be redundant if reset logic handles it, but good for safety
        if not any(m[0] == token and m[1] == 1 and m[2]['role'] == 'system' for m in message_accumulate):
             message_accumulate.append([token, 1, {"role": "system", "content": SYSTEM_MESSAGE}])

    loaded_conversation_messages = []
    loading_new_file = False
    c = consolidate_conversation_flag
    consolidate_conversation_flag = False
    return jsonify({'token': token,
                    'model_name': model_name,
                    'consolidate_conversation_flag': c,
                    'consolidate_option': selected_option_consolidate,
                    })  # Send token as JSON response


@app.route('/update-claude-thinking', methods=['POST'])
def update_claude_thought_state():
    global claude_thinking_flag
    data = request.get_json()
    claude_thinking_flag = data.get('claude_thinking_flag')
    return jsonify({'status': 'updated', 'value': claude_thinking_flag}), 200

@app.route('/update-math-render', methods=['POST'])
def update_math_render_state():
    global math_render_flag
    data = request.get_json()
    math_render_flag = data.get('math_render_flag')
    return jsonify({'status': 'updated', 'value': math_render_flag}), 200

# Load Conversation Endpoint
@app.route('/load', methods=['GET'])
def load_conversation():
    global loaded_conversation_messages
    global loading_new_file
    global consolidate_conversation_flag

    filename = request.args.get('name')
    if not filename:
        return jsonify({'error': 'Conversation name is required.'}), 400

    conversation_path = os.path.join(CONVERSATIONS_DIR, f"{filename+'messages'}.json")
    try:
        with open(conversation_path, 'r', encoding='utf-8') as f:
            loaded_conversation_messages = json.load(f)
    except FileNotFoundError:
        return jsonify({'error': 'Conversation not found.'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'Error decoding JSON.'}), 500
    except Exception as e:
        logger.info(f"Error loading conversation: {e}")
        return jsonify({'error': 'Failed to load conversation.'}), 500

    loading_new_file = True
    # Instead of rendering index.html directly, redirect to root
    # This ensures the standard index route logic runs, including token generation
    from flask import redirect, url_for
    return redirect(url_for('index'))


# Consolidate Conversation Endpoint
@app.route('/consolidate', methods=['GET'])
def consolidate_conversation():
    global consolidate_conversation_flag
    global unique_id_1
    global model_name_1
    global streaming_flag_1
    global selected_option_consolidate
    consolidate_conversation_flag = True
    unique_id_1 = request.args.get("uniqueId")
    model_name_1 = request.args.get("model_name")
    streaming_flag_1 = request.args.get("streaming_flag")
    selected_option_consolidate = request.args.get("option", "fully_updated")
    # Redirect to root to start the new consolidated session
    from flask import redirect, url_for
    return redirect(url_for('index'))



# Save Conversation Endpoint
@app.route('/save', methods=['POST'])
def save_conversation():
    global message_accumulate
    data = request.get_json()
    filename = data.get('name')
    content = data.get('content')
    unique_id = data.get('uniqueId')
    counter = determine_counter(unique_id)

    if not filename or not content:
        return jsonify({'error': 'Conversation name and content are required.'}), 400

    conversation_messages_only = get_conversation_history(unique_id, counter)
    conversation_path = os.path.join(CONVERSATIONS_DIR, f"{filename+'messages'}.json")
    try:
        with open(conversation_path, 'w', encoding='utf-8') as f:
            json.dump(conversation_messages_only, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving conversation: {e}")
        return jsonify({'error': 'Failed to save conversation.'}), 500

    markdown_path = os.path.join(CONVERSATIONS_DIR, f"{filename}.md")
    try:
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Error saving markdown: {e}")
        return jsonify({'error': 'Failed to save markdown file.'}), 500

    return jsonify({'message': 'Conversation and markdown saved successfully.'}), 200



@app.route('/shutdown', methods=['POST'])
def shutdown():
    global message_accumulate
    data = request.get_json()
    timestamp = data.get('timestamp', datetime.now(UTC))
    filename = str(timestamp).replace(" ", "")
    _ = save_system_messages(timestamp, filename)
    message_accumulate = []
    session.clear() # Clear the specific user's session

    logger.info("Shutting down the server...")

    # Standard way to request shutdown in development server
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        logger.warning('Not running with the Werkzeug Server or shutdown function not available.')
        # For Waitress or other prod servers, os._exit might be the only way,
        # but it's abrupt. A cleaner shutdown mechanism is preferred if available.
        # os._exit(0) # Use with caution, doesn't allow cleanup
        return jsonify({"message": "Shutdown function not available. Manual stop required."}), 500
    else:
        func()
        return jsonify({"message": "Server is shutting down..."}), 200



@app.route('/stream', methods=['GET'])
def stream():
    global global_file_contents
    global message_accumulate
    global model_name
    global claude_thinking_flag
    try:
        # Get prompt from URL parameters
        user_input = request.args.get('prompt')
        unique_id = request.args.get('uniqueId')
        model_name = request.args.get('modelname')

        if (not user_input) or (len(user_input.strip()) == 0):
            return jsonify({'error': 'No prompt provided'}), 400

        if (not unique_id) or (len(unique_id.strip()) == 0):
            return jsonify({'error': 'No Unique Session ID provided'}), 400

        if (not model_name) or (len(model_name.strip()) == 0):
            return jsonify({'error': 'Invalid Model Name provided'}), 400


        counter = determine_counter(unique_id)

        # Append user message to session
        full_user_input = user_input + "\n" + global_file_contents
        global_file_contents = "" # Clear after use for this turn
        message_accumulate.append([unique_id, counter, {"role": "user", "content": full_user_input}])
        conversation_history = get_conversation_history(unique_id, counter)

        # Note: session['messages'] is less critical now with message_accumulate,
        # but kept for potential future use or if save_system_messages relies on it.
        # Consider if session['messages'] needs updating here.

        @copy_current_request_context
        def generate_response(unique_id: str, counter: int, conversation_history: list[Dict]) -> Generator[str, None, None]:
            global message_accumulate
            global model_name
            global claude_thinking_flag
            collected_chunks = ['\n'] # Start with newline for formatting consistency?

            # --- LLM Interaction Logic (Simplified for Brevity) ---
            # (Keep your existing logic for OpenAI, Anthropic, Gemini here)
            # Example structure:
            if "4o" in model_name or "gpt-4.1" in model_name or "o1" in model_name or "o3-mini" in model_name or "o4-mini" in model_name:
                 # --- OpenAI Logic ---
                is_streaming = not ("gpt-4.1" in model_name or "o4-mini" in model_name or "o1-pro" in model_name) # Determine if model supports streaming based on name
                full_prompt = [] # Build the prompt according to OpenAI's expected format

                # Add system message (ensure it's first and only once)
                system_msg_added = False
                for msg_data in conversation_history:
                    msg = msg_data # Assuming msg_data is the dictionary like {"role": ..., "content": ...}
                    if msg['role'] == 'system' and not system_msg_added:
                         # Adjust format based on specific OpenAI model requirements if needed
                        full_prompt.append({"role": "system", "content": msg['content']})
                        system_msg_added = True
                    elif msg['role'] != 'system':
                        # Adjust format based on specific OpenAI model requirements if needed
                        # e.g., some models might expect content as [{"type": "text", "text": ...}]
                        full_prompt.append({"role": msg['role'], "content": msg['content']})

                # Ensure system message is present if history was empty or didn't have one
                if not system_msg_added:
                    full_prompt.insert(0, {"role": "system", "content": SYSTEM_MESSAGE})


                try:
                    if is_streaming:
                        response = client.chat.completions.create(
                            model=model_name,
                            messages=full_prompt,
                            # ... other params (temp, max_tokens, etc.)
                            stream=True,
                        )
                        for chunk in response:
                             if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content is not None:
                                chunk_message = chunk.choices[0].delta.content
                                collected_chunks.append(chunk_message)
                                yield json.dumps({'content': chunk_message}) + "\n"
                    else: # Non-streaming models like gpt-4.1, o4-mini, o1-pro
                         # Use the appropriate client method (e.g., client.responses.create for some)
                         # Adjust parameters as needed for these models
                         # Example for a hypothetical non-streaming call:
                         response = client.chat.completions.create( # Or client.responses.create(...)
                             model=model_name,
                             messages=full_prompt,
                             # ... other params ...
                             stream=False, # Explicitly False
                         )
                         bot_message = response.choices[0].message.content # Adjust based on actual response structure
                         collected_chunks.append(bot_message)
                         yield json.dumps({'content': bot_message}) + "\n"


                    # Append full response after loop/call
                    bot_message_full = ''.join(collected_chunks).strip() # Join and remove leading/trailing whitespace
                    if bot_message_full: # Avoid adding empty assistant messages
                        message_accumulate.append([unique_id, counter, {"role": "assistant", "content": bot_message_full}])
                    yield json.dumps({'message': 'Stream complete'}) + "\n" # Signal end

                except Exception as e:
                    logger.error(f"Error in OpenAI generate_response: {e}", exc_info=True)
                    yield json.dumps({'error': 'An error occurred (OpenAI). Please try again.'}) + "\n"


            elif "claude" in model_name:
                # --- Anthropic Logic ---
                full_prompt = []
                system_message_content = SYSTEM_MESSAGE # Default
                for msg_data in conversation_history:
                    msg = msg_data
                    if msg['role'] == 'system':
                        system_message_content = msg['content'] # Capture the most recent system message if multiple exist
                    elif msg['role'] in ['user', 'assistant']:
                         # Anthropic expects alternating user/assistant messages
                         # Ensure the format matches [{"role": "user", "content": ...}, {"role": "assistant", "content": ...}]
                         full_prompt.append({"role": msg['role'], "content": msg['content']})

                # Ensure the conversation starts with a user message if needed, or handle history structure issues.
                # Anthropic API might require the first message in `messages` to be 'user'.
                # If full_prompt is empty or starts with 'assistant', you might need to adjust or prepend.

                try:
                    stream_params = {
                        "model": model_name,
                        "max_tokens": 32000, # Adjust as needed
                        "system": system_message_content,
                        "messages": full_prompt,
                    }
                    if claude_thinking_flag:
                         stream_params["thinking"] = {"type": "enabled", "budget_tokens": 16000} # Example

                    with anthropic_client.messages.stream(**stream_params) as stream:
                        for chunk_text in stream.text_stream:
                            if chunk_text is not None:
                                chunk_message = chunk_text
                                collected_chunks.append(chunk_message)
                                yield json.dumps({'content': chunk_message}) + "\n"

                    bot_message_full = ''.join(collected_chunks).strip()
                    if bot_message_full:
                        message_accumulate.append([unique_id, counter, {"role": "assistant", "content": bot_message_full}])
                    yield json.dumps({'message': 'Stream complete'}) + "\n"

                except Exception as e:
                    logger.error(f"Error in Anthropic generate_response: {e}", exc_info=True)
                    yield json.dumps({'error': 'An error occurred (Anthropic). Please try again.'}) + "\n"


            elif "gemini" in model_name:
                # --- Gemini Logic ---
                full_prompt = []
                system_instruction_text = SYSTEM_MESSAGE # Default
                for msg_data in conversation_history:
                     msg = msg_data
                     # Gemini uses 'user' and 'model' roles
                     role = 'model' if msg['role'] == 'assistant' else msg['role']
                     if role == 'system':
                         system_instruction_text = msg['content']
                     elif role in ['user', 'model']:
                         # Ensure content format matches Gemini's expected structure
                         # Example: types.Content(role=role, parts=[types.Part.from_text(text=msg['content'])])
                         full_prompt.append(types.Content(role=role, parts=[types.Part.from_text(text=msg['content'])]))

                # Ensure history structure is valid for Gemini (e.g., alternating roles if required by the API)

                generate_content_config = types.GenerateContentConfig(
                    temperature=0,
                    # tools = [types.Tool(google_search=types.GoogleSearch())], # Optional tools
                    safety_settings=[ # Adjust safety settings as needed
                        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_MEDIUM_AND_ABOVE"),
                        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_MEDIUM_AND_ABOVE"),
                        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_MEDIUM_AND_ABOVE"),
                        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_MEDIUM_AND_ABOVE"),
                    ],
                    response_mime_type="text/plain",
                )
                # System instruction is handled separately in Gemini
                system_instruction = types.Part.from_text(text=system_instruction_text)


                try:
                    stream = gemini_client.generate_content( # Use generate_content for streaming
                        model=model_name,
                        contents=full_prompt,
                        generation_config=generate_content_config,
                        system_instruction=system_instruction,
                        stream=True,
                    )

                    for chunk in stream:
                        if hasattr(chunk, 'text') and chunk.text:
                            chunk_message = chunk.text
                            collected_chunks.append(chunk_message)
                            yield json.dumps({'content': chunk_message}) + "\n"

                    bot_message_full = ''.join(collected_chunks).strip()
                    # Gemini responses might need post-processing (e.g., handling function calls if tools are used)
                    if bot_message_full:
                         message_accumulate.append([unique_id, counter, {"role": "assistant", "content": bot_message_full}]) # Use 'assistant' role internally
                    yield json.dumps({'message': 'Stream complete'}) + "\n"

                except Exception as e:
                    # Handle specific Gemini exceptions if needed (e.g., BlockedPromptError)
                    logger.error(f"Error in Gemini generate_response: {e}", exc_info=True)
                    yield json.dumps({'error': f'An error occurred (Gemini): {e}'}) + "\n"


            else:
                logger.error("Invalid Model")
                yield json.dumps({'error': "Invalid Model Selected"}) + "\n"
            # --- End LLM Interaction Logic ---


        return Response(
            stream_with_context(generate_response(unique_id, counter, conversation_history)),
            mimetype='text/event-stream',
            headers={'Cache-Control': 'no-cache'}
        )


    except Exception as e:
        logger.error(f"Error in stream route: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500



@app.route('/reset', methods=['POST'])
def reset() -> Dict[str, str]:
    global message_accumulate
    data = request.get_json()
    unique_id = data.get('uniqueId')
    if not unique_id:
        return jsonify({'error': 'Unique ID not provided'}), 400
    counter = determine_counter(unique_id) + 1
    # Start the new counter branch with the system message
    message_accumulate.append([unique_id, counter, {"role": "system", "content": SYSTEM_MESSAGE}])
    # Clear the user's Flask session as well if it holds related state
    # session.clear() # Or selectively remove items: session.pop('messages', None)
    return jsonify({'status': 'Conversation reset successfully'})


@app.route('/select_model', methods=['POST'])
def select_model() -> Dict[str, str]:
    global message_accumulate
    global model_name # Ensure we modify the global model_name
    data = request.get_json()
    unique_id = data.get('uniqueId') # Get uniqueId if needed for context
    new_model_name = data.get('selectedModel')

    if not new_model_name:
         return jsonify({'error': 'No model selected'}), 400

    model_name = new_model_name # Update the global model name

    # Optionally, you could add a message to the current conversation branch
    # indicating the model change, but this might clutter the history for the LLM.
    # counter = determine_counter(unique_id)
    # message_accumulate.append([unique_id, counter, {"role": "system", "content": f"Switched model to {model_name}"}])

    logger.info(f"Model changed to: {model_name} for session {unique_id}")
    return jsonify({'status': f'Model set to {model_name}'})


@app.route('/get_file_contents', methods=['GET'])
def get_file_contents():
    global global_file_contents
    return jsonify({"file_contents": global_file_contents})



#####################
# File Contents Viewer
#####################

@app.route('/filecontents')
def filecontents():
    # This route serves the HTML for the file viewer popup/tab
    return render_template('index2.html')

def choose_folder():
    # Use Tkinter on the server thread - BE CAREFUL with GUI libraries in web servers.
    # This might block the server process. Consider running this asynchronously
    # or using a different method for folder selection if it causes issues.
    folder_path = None
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the root window.
        root.attributes('-topmost', True) # Try to bring dialog to front
        folder_path = filedialog.askdirectory(title="Select Folder")
        root.destroy()
    except tk.TclError as e:
        logger.error(f"Tkinter error (maybe no display available?): {e}")
        # Fallback or error handling needed if running in headless environment
        return None
    except Exception as e:
        logger.error(f"Error in choose_folder: {e}")
        return None
    return folder_path


def get_directory_structure(rootdir):
    """
    Recursively builds a directory structure.
    Only includes files with specific extensions.
    Handles potential permission errors.
    """
    # Define allowed extensions (consider making this configurable)
    allowed_extensions = {'.text', '.txt', '.md', '.html', '.htm', '.php', '.js', '.css', '.py', '.json', '.ipynb', '.java', '.c', '.cpp', '.h', '.cs', '.go', '.rb', '.rs', '.swift', '.kt', '.kts', '.yaml', '.yml', '.xml', '.sh', '.bat'}
    structure = []

    try:
        # Check if rootdir exists and is a directory
        if not os.path.isdir(rootdir):
            logger.warning(f"Path is not a directory or does not exist: {rootdir}")
            return [] # Return empty list if path is invalid

        for item in os.listdir(rootdir):
            full_path = os.path.join(rootdir, item)
            try:
                if os.path.isdir(full_path):
                    # Important: Check for recursive symlinks or very deep structures if necessary
                    children = get_directory_structure(full_path)
                    # Only include directories that contain allowed files or subdirs with allowed files
                    if children:
                        structure.append({
                            "name": item,
                            "path": full_path,
                            "type": "directory",
                            "children": children
                        })
                elif os.path.isfile(full_path): # Ensure it's a file
                    _, ext = os.path.splitext(item)
                    if ext.lower() in allowed_extensions:
                        structure.append({
                            "name": item,
                            "path": full_path,
                            "type": "file"
                        })
            except OSError as e:
                 logger.warning(f"Permission error accessing {full_path}: {e}")
                 # Optionally add an entry indicating the error
                 # structure.append({"name": item, "type": "error", "message": str(e)})
                 continue # Skip this item
            except Exception as e:
                 logger.error(f"Unexpected error processing {full_path}: {e}")
                 continue # Skip this item

    except OSError as e:
        logger.error(f"Permission error reading directory {rootdir}: {e}")
        # Return structure found so far, or an empty list, or raise error
        return []
    except Exception as e:
        logger.error(f"Error reading directory {rootdir}: {e}")
        return []

    return structure



@app.route('/open_folder', methods=['POST'])
def open_folder():
    global selected_folder
    global global_file_contents
    global_file_contents = "" # Clear previous content when opening a new folder
    folder = choose_folder()
    if folder:
        selected_folder = folder
        logger.info(f"Folder selected: {selected_folder}")
        structure = get_directory_structure(folder)
        return jsonify({"folder": folder, "structure": structure})
    else:
        logger.warning("No folder was selected by the user.")
        # Check if a folder was previously selected to potentially refresh that
        if selected_folder:
             structure = get_directory_structure(selected_folder)
             return jsonify({"folder": selected_folder, "structure": structure, "message": "No new folder selected, showing previous."})
        else:
             return jsonify({"error": "No folder selected"}), 400

@app.route('/refresh', methods=['GET'])
def refresh():
    global selected_folder
    global global_file_contents
    global_file_contents = "" # Clear content on refresh
    if selected_folder:
        logger.info(f"Refreshing folder: {selected_folder}")
        structure = get_directory_structure(selected_folder)
        return jsonify({"folder": selected_folder, "structure": structure})
    else:
        logger.warning("Refresh requested but no folder is selected.")
        return jsonify({"error": "No folder has been selected yet"}), 400

@app.route('/load_selection', methods=['POST'])
def load_selection():
    global selected_folder
    global global_file_contents
    data = request.get_json()
    selected_files = data.get("files", [])
    result = ""

    if not selected_folder:
        logger.error("Load selection requested but no base folder is set.")
        return jsonify({"error": "No folder context available. Please open a folder first."}), 400

    if not selected_files:
        logger.warning("Load selection called with no files selected.")
        global_file_contents = "" # Clear content if selection is empty
        return jsonify({"result": "", "message": "No files selected."})

    logger.info(f"Loading selection of {len(selected_files)} files from folder: {selected_folder}")

    file_contents_list = [] # Store individual file contents temporarily

    for file_path in selected_files:
        # Security check: Ensure the file path is within the selected_folder directory
        # This helps prevent accessing arbitrary files outside the intended scope
        common_path = os.path.commonpath([selected_folder, file_path])
        if common_path != os.path.normpath(selected_folder):
             logger.warning(f"Attempted to load file outside selected folder: {file_path}")
             # Skip this file or return an error
             file_contents_list.append(f"---\n\nFILE: [ACCESS DENIED - Outside selected folder]\n\n---\n\n")
             continue

        # Compute the relative path for display
        try:
            relative_path = os.path.relpath(file_path, selected_folder)
        except ValueError:
            # Handle cases where paths are on different drives (Windows)
            relative_path = file_path # Fallback to absolute path
        except Exception as e:
            logger.error(f"Error calculating relative path for {file_path}: {e}")
            relative_path = file_path # Fallback

        # Read file contents with error handling for encoding and permissions
        try:
            # Try reading as UTF-8 first, fallback to latin-1 or ignore errors
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                logger.warning(f"File {relative_path} read as latin-1 after UTF-8 decode failed.")
            except Exception as e_fallback:
                content = f"Error reading file (encoding/fallback failed): {e_fallback}"
                logger.error(f"Failed to read file {relative_path} even with fallback: {e_fallback}")
        except OSError as e:
             content = f"Error reading file (OS error): {e}"
             logger.error(f"OS error reading file {relative_path}: {e}")
        except Exception as e:
            content = f"Error reading file: {e}"
            logger.error(f"Generic error reading file {relative_path}: {e}")

        # Append formatted block to the list
        file_contents_list.append(f"---\n\nFILE: {relative_path}\n\n{content}\n\n")

    # Join all file contents with the final delimiter
    result = "".join(file_contents_list) + "---"
    global_file_contents = result # Update the global variable

    logger.info(f"Successfully loaded {len(selected_files)} files into global_file_contents.")
    return jsonify({"result": result}) # Send concatenated content back to file viewer UI

@app.route('/clear_loaded_content', methods=['POST'])
def clear_loaded_content():
    """
    Clears the global file contents stored on the backend.
    """
    global global_file_contents
    global_file_contents = ""
    logger.info("Global file contents cleared.")
    return jsonify({"message": "global_file_contents cleared"}), 200



def find_available_port_iterative(start_port, end_port=65535):
    for port in range(start_port, end_port + 1): # Include end_port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                # Try to bind to the port on localhost
                s.bind(('127.0.0.1', port))
                # If bind succeeds, the port is available
                return port
            except socket.error as e:
                # If bind fails (e.g., address already in use), continue to the next port
                if e.errno == socket.errno.EADDRINUSE:
                    # print(f"Port {port} is in use.") # Optional debug print
                    continue
                else:
                    # Handle other socket errors if necessary
                    logger.error(f"Error checking port {port}: {e}")
                    continue # Or raise error depending on desired behavior
    # If loop completes without finding a port
    raise RuntimeError(f"No available port found between {start_port} and {end_port}.")



if __name__ == '__main__':
    # Determine if running in development mode (e.g., via FLASK_ENV or FLASK_DEBUG)
    # Flask's default is production unless FLASK_ENV=development or FLASK_DEBUG=1
    is_development = os.environ.get('FLASK_ENV') == 'development' or os.environ.get('FLASK_DEBUG') == '1' or app.debug

    try:
        port = find_available_port_iterative(5000)
        print(f"Found available port: {port}")
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1) # Exit if no port found

    if is_development:
        print(f" * Running in development mode (Debug: {app.debug})")
        print(f" * Auto-reloader active for Python code and templates.")
        print(f" * Serving on http://127.0.0.1:{port}")
        # Use Flask's built-in server for development (includes auto-reloader)
        # Pass debug=True explicitly if not set via environment variables or app.config
        app.run(host='127.0.0.1', port=port, debug=True) # debug=True enables reloader and debugger
    else:
        print(" * Running in production mode (Waitress)")
        print(f" * Auto-reloader is OFF.")
        print(f" * Serving on http://127.0.0.1:{port}")
        # Use Waitress for a more stable/production-like environment
        serve(app, host='127.0.0.1', port=port)

```

**Explanation of Changes:**

1.  **Flask Debug Mode:**

    - Flask has a built-in "debug mode" primarily intended for development.
    - When debug mode is active, Flask's development server automatically monitors your Python files (`.py`) for changes and restarts the server when a change is detected.
    - Crucially for your request, **debug mode also makes Flask check for template file changes** (`.html`, etc., in the `templates` folder) on each request. If a template has changed since it was last loaded, Flask will reload it before rendering.
    - **How to Enable:**
      - **Environment Variable (Recommended):** Set the environment variable `FLASK_ENV` to `development` before running your script.
        - Linux/macOS: `export FLASK_ENV=development`
        - Windows CMD: `set FLASK_ENV=development`
        - Windows PowerShell: `$env:FLASK_ENV = "development"`
        - Then run `python app.py`.
      - **Alternatively (Code):** You could uncomment `app.config['DEBUG'] = True` near the `app = Flask(__name__)` line.
      - **Alternatively (Run Command):** Pass `debug=True` directly to `app.run()`.

2.  **Development Server vs. Production Server (Waitress):**

    - Your original code uses `waitress.serve(app, ...)`. Waitress is a production-grade WSGI server. Production servers are optimized for stability and performance and **do not** typically watch for file changes or automatically reload code/templates. They load the application once at startup.
    - Flask's built-in development server (`app.run()`) **is** designed for this auto-reloading behavior.
    - **Solution:** You need to use the _development server_ when you want auto-reloading.

3.  **Conditional Server Start (`if __name__ == '__main__':`)**
    - The code block at the end of `app.py` is modified.
    - It now checks if Flask is likely running in development mode (based on environment variables or `app.debug`).
    - If `is_development` is true, it calls `app.run(host='127.0.0.1', port=port, debug=True)`. Passing `debug=True` here explicitly enables the debugger and the reloader.
    - If `is_development` is false (i.e., you haven't set `FLASK_ENV=development`), it falls back to using `waitress.serve(...)` as before, suitable for a more stable or production-like deployment.

**How to Use:**

1.  **Save** the modified `app.py` code above.
2.  **Open your terminal** in the project directory.
3.  **Set the environment variable:**
    - `export FLASK_ENV=development` (Linux/macOS)
    - `set FLASK_ENV=development` (Windows CMD)
    - `$env:FLASK_ENV = "development"` (Windows PowerShell)
4.  **Run the backend:**
    - `python app.py`
5.  You should see output indicating it's running in development mode with the reloader active.
6.  Now, open the web interface in your browser.
7.  Make changes to `templates/index.html` or `templates/index2.html` and save the file.
8.  **Refresh the page in your browser.** You should see the changes reflected without needing to stop and restart the `python app.py` process.

**Important Considerations:**

- **Browser Cache:** Sometimes, even if Flask serves the new file, your browser might show a cached version. Do a hard refresh (Ctrl+Shift+R or Cmd+Shift+R) if you don't see changes immediately.
- **Python Code Changes:** Debug mode also reloads the server when you change `.py` files, which is very useful during development.
- **Production:** Remember to switch back to using Waitress (or another production server like Gunicorn) and ensure debug mode is **OFF** (`FLASK_ENV=production` or remove the debug setting) when deploying your application for others to use. Debug mode exposes security risks and is less performant.

---

Unique Session ID: 2254b95a-310c-4379-a7ab-d7b6eef65b7a

Model: gemini-2.5-flash-preview-04-17

Unique Session ID: 2254b95a-310c-4379-a7ab-d7b6eef65b7a

Model: gemini-2.5-pro-preview-03-25

Streaming: true

**Model:** gemini-2.5-pro-preview-03-25

**Assistant:**

Okay, here is a Python program using the Pygame library to simulate a ball bouncing inside a spinning hexagon with a central circle, incorporating gravity and friction.

This program demonstrates:

1.  **Modular Design:** Uses classes for `Ball`, `Hexagon`, and `Circle`.
2.  **Physics Simulation:** Implements gravity, elastic collisions, and kinetic friction.
3.  **Vector Math:** Leverages `pygame.math.Vector2` for position, velocity, and normal calculations.
4.  **Rotation:** The hexagon rotates at a constant angular velocity.
5.  **Collision Detection:** Detects collisions between the ball and the hexagon edges, and the ball and the circle.
6.  **Collision Response:** Calculates the reflection vector based on the surface normal and applies friction tangentially.
7.  **Configuration:** Parameters like gravity, friction, sizes, and speeds are easily configurable.

**Prerequisites:**
You need to have Pygame installed. If not, install it using pip:
`pip install pygame`

```python
import pygame
import math
import sys

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Physics Parameters
GRAVITY_STRENGTH = 250.0  # Pixels per second squared (positive is downwards)
COEFF_STATIC_FRICTION = 0.6  # For future use
COEFF_KINETIC_FRICTION = 0.15 # Affects tangential velocity during bounce
BALL_MASS = 1.0 # kg (used in friction calculation logic)
# Coefficient of Restitution (1.0 = perfectly elastic)
# We simulate elasticity directly, friction handles energy loss tangentially
COEFF_RESTITUTION = 1.0

# Object Parameters
HEXAGON_CENTER = pygame.math.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
HEXAGON_SIZE = 250  # Distance from center to vertex
HEXAGON_ANGULAR_VELOCITY = math.radians(30)  # Radians per second
HEXAGON_COLOR = BLUE
HEXAGON_LINE_WIDTH = 3

CIRCLE_CENTER = pygame.math.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
CIRCLE_RADIUS = 80
CIRCLE_COLOR = GREEN
CIRCLE_LINE_WIDTH = 3

BALL_RADIUS = 15
BALL_COLOR = RED
# Ensure ball starts inside hexagon but outside circle
INITIAL_BALL_POS = pygame.math.Vector2(HEXAGON_CENTER.x + CIRCLE_RADIUS + BALL_RADIUS + 20, HEXAGON_CENTER.y)
INITIAL_BALL_VEL = pygame.math.Vector2(0, -150) # Initial velocity (pixels/sec)

# --- Helper Functions ---
def clamp(value, min_val, max_val):
    """Clamps a value between a minimum and maximum."""
    return max(min_val, min(value, max_val))

# --- Classes ---

class Ball:
    """Represents the bouncing ball."""
    def __init__(self, pos, vel, radius, mass, color):
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(vel)
        self.radius = radius
        self.mass = mass
        self.color = color

    def update(self, dt, gravity_vec):
        """Updates the ball's position and velocity based on time step and gravity."""
        # Apply gravity
        self.vel += gravity_vec * dt
        # Update position
        self.pos += self.vel * dt

    def draw(self, surface):
        """Draws the ball on the given surface."""
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)

class Hexagon:
    """Represents the spinning hexagon boundary."""
    def __init__(self, center, size, initial_angle, angular_velocity, color, line_width):
        self.center = pygame.math.Vector2(center)
        self.size = size
        self.angle = initial_angle # Radians
        self.angular_velocity = angular_velocity # Radians per second
        self.color = color
        self.line_width = line_width
        self.vertices = []
        self.edges = [] # List of tuples: (start_point, end_point, normal_vector)
        self._calculate_geometry()

    def update(self, dt):
        """Updates the hexagon's rotation angle."""
        self.angle += self.angular_velocity * dt
        self._calculate_geometry()

    def _calculate_geometry(self):
        """Calculates vertices, edges, and normals based on the current angle."""
        self.vertices = []
        for i in range(6):
            angle_rad = self.angle + math.pi / 3 * i
            x = self.center.x + self.size * math.cos(angle_rad)
            y = self.center.y + self.size * math.sin(angle_rad) # Pygame y increases downwards
            self.vertices.append(pygame.math.Vector2(x, y))

        self.edges = []
        for i in range(6):
            p1 = self.vertices[i]
            p2 = self.vertices[(i + 1) % 6]
            edge_vec = p2 - p1
            # Normal vector pointing inwards (rotate edge vector -90 degrees)
            normal = edge_vec.rotate(-90).normalize()
            self.edges.append((p1, p2, normal))

    def draw(self, surface):
        """Draws the hexagon on the given surface."""
        pygame.draw.polygon(surface, self.color, [(int(v.x), int(v.y)) for v in self.vertices], self.line_width)

class Circle:
    """Represents the stationary inner circle obstacle."""
    def __init__(self, center, radius, color, line_width):
        self.center = pygame.math.Vector2(center)
        self.radius = radius
        self.color = color
        self.line_width = line_width

    def draw(self, surface):
        """Draws the circle on the given surface."""
        pygame.draw.circle(surface, self.color, (int(self.center.x), int(self.center.y)), self.radius, self.line_width)

# --- Collision Logic ---

def handle_collision(ball, normal, penetration_depth, mu_k):
    """
    Handles the physics response to a collision.
    Updates ball velocity for elastic bounce and applies kinetic friction.

    Args:
        ball (Ball): The ball object.
        normal (Vector2): The surface normal at the point of collision (pointing away from the surface).
        penetration_depth (float): How far the ball has penetrated the surface.
        mu_k (float): Coefficient of kinetic friction.
    """
    # 1. Resolve Penetration: Move ball slightly out of the surface
    # This prevents sticking. Add a small buffer (e.g., 0.1 pixels).
    correction = normal * max(0, penetration_depth + 0.1)
    ball.pos += correction

    # 2. Calculate relative velocity component along the normal
    # For stationary surfaces, this is just ball.vel.dot(normal)
    v_normal_scalar = ball.vel.dot(normal)

    # If ball is moving away from surface already, do nothing (can happen due to float errors or multiple collisions)
    if v_normal_scalar >= 0:
        return

    # 3. Calculate impulse for elastic collision (normal direction)
    # For elastic collision (COR=1), the normal velocity reverses.
    # Impulse J_normal = delta_p_normal = m * (v_normal_final - v_normal_initial)
    # v_normal_final = -v_normal_initial
    # J_normal = m * (-v_normal_initial - v_normal_initial) = -2 * m * v_normal_initial
    # We work with velocity change directly: delta_v_normal = -2 * v_normal_initial
    # Note: v_normal_scalar is ball.vel.dot(normal), which is the component *along* the normal.
    v_normal_vec = v_normal_scalar * normal
    delta_v_normal = - (1 + COEFF_RESTITUTION) * v_normal_vec # More general form using COR

    # 4. Calculate tangential velocity
    v_tangent_vec = ball.vel - v_normal_vec

    # 5. Calculate friction impulse (tangential direction)
    # Friction opposes tangential motion.
    # Max friction impulse magnitude: J_friction_max = mu_k * |J_normal|
    # J_normal_mag = abs(- (1 + COEFF_RESTITUTION) * ball.mass * v_normal_scalar)
    # J_friction_max = mu_k * (1 + COEFF_RESTITUTION) * ball.mass * abs(v_normal_scalar)
    # Change in tangential velocity due to friction: delta_v_tangent = J_friction / mass
    # delta_v_tangent_max = mu_k * (1 + COEFF_RESTITUTION) * abs(v_normal_scalar)

    tangent_speed = v_tangent_vec.length()
    if tangent_speed > 1e-6: # Avoid division by zero and tiny speeds
        tangent_dir = v_tangent_vec.normalize()
        delta_v_tangent_max = mu_k * (1 + COEFF_RESTITUTION) * abs(v_normal_scalar)

        # Friction impulse cannot exceed what's needed to stop tangential motion
        delta_v_tangent_mag = min(delta_v_tangent_max, tangent_speed)

        # Friction acts opposite to the tangential velocity vector
        delta_v_tangent = -delta_v_tangent_mag * tangent_dir
    else:
        delta_v_tangent = pygame.math.Vector2(0, 0)

    # 6. Apply velocity changes
    ball.vel += delta_v_normal + delta_v_tangent


def check_ball_hexagon_collision(ball, hexagon, mu_k):
    """Checks and handles collisions between the ball and hexagon edges."""
    collided = False
    for p1, p2, normal in hexagon.edges:
        # Vector from edge start to ball center
        vec_p1_to_ball = ball.pos - p1
        edge_vec = p2 - p1
        edge_len_sq = edge_vec.length_squared()

        if edge_len_sq < 1e-9: # Avoid division by zero for very short edges (shouldn't happen)
            continue

        # Project ball center onto the edge line
        # Parameter t represents the projection along the normalized edge vector
        t = vec_p1_to_ball.dot(edge_vec) / edge_len_sq

        # Find the closest point on the infinite line defined by the edge
        if t < 0:
            closest_point = p1
        elif t > 1:
            closest_point = p2
        else:
            closest_point = p1 + t * edge_vec

        # Vector from closest point to ball center
        vec_closest_to_ball = ball.pos - closest_point
        dist_sq = vec_closest_to_ball.length_squared()

        # Check for collision (distance < radius)
        if dist_sq < ball.radius * ball.radius:
            dist = math.sqrt(dist_sq)
            penetration = ball.radius - dist

            # The normal for collision response is from the closest point to the ball center,
            # unless the closest point is a vertex, then use the edge normal (or average).
            # For simplicity here, we use the pre-calculated edge normal if the closest
            # point is on the segment itself (0 <= t <= 1). If it's a vertex (t<0 or t>1),
            # the normal should ideally be handled differently (e.g., average of adjacent edge normals),
            # but using the edge normal is often sufficient.
            # A simpler approach: use the vector from closest point to ball as normal if dist > 0
            if dist > 1e-6:
                 collision_normal = vec_closest_to_ball.normalize()
                 # Ensure normal points away from wall (towards ball)
                 # Our pre-calculated normals point inwards, so we need to flip it
                 # Let's stick to the pre-calculated inward normal and flip it for the handler
                 collision_normal_for_handler = -normal # Normal pointing OUT from hexagon wall
            else:
                 # If distance is near zero (center exactly on line), use edge normal
                 collision_normal_for_handler = -normal

            # Check if ball is moving towards this edge segment
            # Use the edge normal for this check
            if ball.vel.dot(collision_normal_for_handler) < 0:
                 handle_collision(ball, collision_normal_for_handler, penetration, mu_k)
                 collided = True
                 # Optional: break after first collision detected per frame for simplicity,
                 # though multiple collisions are possible. Handling one is usually stable enough.
                 # break

    return collided


def check_ball_circle_collision(ball, circle, mu_k):
    """Checks and handles collisions between the ball and the inner circle."""
    vec_circle_to_ball = ball.pos - circle.center
    dist_sq = vec_circle_to_ball.length_squared()
    min_dist = ball.radius + circle.radius

    if dist_sq < min_dist * min_dist:
        dist = math.sqrt(dist_sq)
        penetration = min_dist - dist

        if dist > 1e-6:
            # Normal points from circle center towards ball center (away from circle surface)
            normal = vec_circle_to_ball.normalize()
        else:
            # Ball center is exactly at circle center - push outwards arbitrarily (e.g., upwards)
            normal = pygame.math.Vector2(0, -1)

        # Check if ball is moving towards the circle center (or away from the surface normal)
        if ball.vel.dot(normal) < 0:
            handle_collision(ball, normal, penetration, mu_k)
            return True
    return False

# --- Main Game ---
def main():
    """Main game function."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bouncing Ball in Spinning Hexagon")
    clock = pygame.time.Clock()

    # Create objects
    gravity_vector = pygame.math.Vector2(0, GRAVITY_STRENGTH) # Pointing downwards
    ball = Ball(INITIAL_BALL_POS, INITIAL_BALL_VEL, BALL_RADIUS, BALL_MASS, BALL_COLOR)
    hexagon = Hexagon(HEXAGON_CENTER, HEXAGON_SIZE, 0, HEXAGON_ANGULAR_VELOCITY, HEXAGON_COLOR, HEXAGON_LINE_WIDTH)
    circle = Circle(CIRCLE_CENTER, CIRCLE_RADIUS, CIRCLE_COLOR, CIRCLE_LINE_WIDTH)

    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # --- Time Step ---
        # dt is time elapsed since last frame in seconds
        dt = clock.tick(FPS) / 1000.0
        # Avoid large dt spikes if debugging or pausing
        dt = min(dt, 1.0 / 20.0) # Cap dt to avoid instability

        # --- Updates ---
        hexagon.update(dt)
        ball.update(dt, gravity_vector)

        # --- Collision Detection & Response ---
        # Order matters: Check outer boundary (hexagon) first, then inner (circle).
        # It's possible to collide with both in one frame near corners/intersections.
        # Handling one collision per frame is usually sufficient for stability.
        collided_hex = check_ball_hexagon_collision(ball, hexagon, COEFF_KINETIC_FRICTION)
        # Only check circle collision if not already handled by hexagon collision in this frame
        if not collided_hex:
            check_ball_circle_collision(ball, circle, COEFF_KINETIC_FRICTION)

        # Optional: Screen boundary check (if needed, though hexagon should contain it)
        # if ball.pos.x < ball.radius or ball.pos.x > SCREEN_WIDTH - ball.radius:
        #     ball.vel.x *= -1 # Reflect horizontally
        #     ball.pos.x = clamp(ball.pos.x, ball.radius, SCREEN_WIDTH - ball.radius)
        # if ball.pos.y < ball.radius or ball.pos.y > SCREEN_HEIGHT - ball.radius:
        #     ball.vel.y *= -1 # Reflect vertically
        #     ball.pos.y = clamp(ball.pos.y, ball.radius, SCREEN_HEIGHT - ball.radius)


        # --- Drawing ---
        screen.fill(BLACK)
        hexagon.draw(screen)
        circle.draw(screen)
        ball.draw(screen)

        # Display FPS (optional)
        font = pygame.font.SysFont(None, 24)
        fps_text = font.render(f"FPS: {clock.get_fps():.1f}", True, YELLOW)
        screen.blit(fps_text, (10, 10))

        pygame.display.flip() # Update the full screen

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
```

**Explanation:**

1.  **Configuration:** All tunable parameters (screen size, colors, physics constants, object properties) are at the top for easy modification.
2.  **Classes:**
    - `Ball`: Stores position (`pos`), velocity (`vel`), radius, mass, and color. `update` applies gravity and integrates position. `draw` renders it.
    - `Hexagon`: Stores center, size, current rotation `angle`, `angular_velocity`, color, and line width. `update` increments the angle. `_calculate_geometry` computes the current vertex positions and edge data (start point, end point, inward normal vector) based on the angle. `draw` renders the polygon.
    - `Circle`: Stores center, radius, color, and line width. `draw` renders it.
3.  **Collision Logic:**
    - `handle_collision`: This is the core physics response function.
      - It first resolves penetration by pushing the ball out along the collision `normal`.
      - It calculates the velocity component perpendicular to the surface (`v_normal_vec`).
      - It calculates the change in normal velocity for an elastic bounce (`delta_v_normal`).
      - It calculates the tangential velocity (`v_tangent_vec`).
      - It calculates the maximum possible change in tangential velocity due to kinetic friction, based on the normal impulse and `mu_k`.
      - It applies a change in tangential velocity (`delta_v_tangent`) that opposes the current tangential motion, capped by the friction limit and ensuring it doesn't exceed the tangential speed itself.
      - Finally, it updates the ball's velocity by adding the normal and tangential velocity changes.
    - `check_ball_hexagon_collision`: Iterates through the hexagon's current edges. For each edge, it finds the closest point on the edge segment to the ball's center. If the distance is less than the ball's radius, it calculates the penetration depth and the appropriate collision normal (pointing _out_ of the wall). It checks if the ball is moving _towards_ the wall before calling `handle_collision`.
    - `check_ball_circle_collision`: Calculates the distance between the ball and circle centers. If less than the sum of their radii, it calculates penetration and the normal (vector from circle center to ball center). It checks if the ball is moving towards the circle before calling `handle_collision`.
4.  **Main Loop (`main` function):**
    - Initializes Pygame, screen, and clock.
    - Creates instances of `Ball`, `Hexagon`, and `Circle`.
    - Enters the main game loop.
    - Handles events (quitting).
    - Calculates `dt` (delta time) using `clock.tick()`. Capping `dt` prevents physics instability if the frame rate drops significantly.
    - Updates the hexagon's rotation and the ball's position/velocity due to gravity.
    - Calls the collision detection functions. The order (hexagon then circle) is chosen somewhat arbitrarily but ensures the outer boundary is checked first.
    - Clears the screen (`screen.fill`).
    - Draws all objects (`hexagon.draw`, `circle.draw`, `ball.draw`).
    - Optionally displays the FPS.
    - Updates the display (`pygame.display.flip`).
    - Cleans up Pygame on exit.

This code provides a robust simulation with the requested features. You can adjust the parameters in the "Configuration" section to see how they affect the simulation.

---

Unique Session ID: be59d89f-5893-4285-8046-d1a77350d102

Model: chatgpt-4o-latest

Streaming: true

Unique Session ID: be59d89f-5893-4285-8046-d1a77350d102

Model: o4-mini

Streaming: true

**Model:** o4-mini

**Assistant:**

Here’s a self‑contained Python script using Tkinter. Save it as, say, `financial_calculator.py` and run with Python 3. It provides

• A scientific‑style calculator (arithmetic, ^, ln, log, exp, factorial, nCr)  
• Financial functions: FV, PV, Rate, Annuity PV, Annuity FV, Perpetuity  
• Robust error handling

```python
import tkinter as tk
from tkinter import messagebox
import math

# fallback comb if math.comb not available
def comb(n, k):
    if not (isinstance(n, int) and isinstance(k, int)):
        raise ValueError("nCr requires integer arguments")
    if k < 0 or n < 0 or k > n:
        raise ValueError("Invalid nCr parameters")
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

# allowed names for safe eval
allowed_names = {
    'ln': math.log,
    'log': math.log,
    'exp': math.exp,
    'factorial': math.factorial,
    'nCr': comb,
    'pi': math.pi,
    'e': math.e
}

def safe_eval(expr):
    expr = expr.replace('^', '**')
    try:
        code = compile(expr, "<string>", "eval")
        for name in code.co_names:
            if name not in allowed_names:
                raise NameError(f"use of '{name}' not allowed")
        return eval(code, {"__builtins__": None}, allowed_names)
    except Exception as e:
        raise

class CalculatorApp:
    def __init__(self, root):
        self.root = root
        root.title("Financial Calculator")

        self.entry = tk.Entry(root, font=("Arial", 18), bd=4, relief=tk.RIDGE, justify='right')
        self.entry.grid(row=0, column=0, columnspan=5, pady=8, padx=8, sticky="we")
        self._build_buttons()

    def _build_buttons(self):
        btns = [
            ['7','8','9','/','ln'],
            ['4','5','6','*','log'],
            ['1','2','3','-','exp'],
            ['0','.','^','+','factorial'],
            ['(',')','nCr','Del','Clear'],
        ]
        for i, row in enumerate(btns):
            for j, txt in enumerate(row):
                cmd = lambda x=txt: self._on_button(x)
                if txt == '=': cmd = self.calculate
                elif txt == 'Clear': cmd = self.clear
                elif txt == 'Del': cmd = self.backspace
                tk.Button(self.root, text=txt, width=6, height=2, command=cmd)\
                  .grid(row=i+1, column=j, padx=2, pady=2)

        # financial buttons
        fin_ops = [
            ('=', self.calculate),
            ('FV', self.open_fv), ('PV', self.open_pv), ('Rate', self.open_rate),
            ('Annuity PV', self.open_annuity_pv), ('Annuity FV', self.open_annuity_fv),
            ('Perpetuity', self.open_perpetuity)
        ]
        # place '=' in the UI as well
        tk.Button(self.root, text='=', width=6, height=2, command=self.calculate)\
          .grid(row=6, column=0, padx=2, pady=2)
        tk.Button(self.root, text='FV', width=6, height=2, command=self.open_fv)\
          .grid(row=6, column=1, padx=2, pady=2)
        tk.Button(self.root, text='PV', width=6, height=2, command=self.open_pv)\
          .grid(row=6, column=2, padx=2, pady=2)
        tk.Button(self.root, text='Rate', width=6, height=2, command=self.open_rate)\
          .grid(row=6, column=3, padx=2, pady=2)
        tk.Button(self.root, text='Annuity PV', width=12, height=2, command=self.open_annuity_pv)\
          .grid(row=7, column=0, columnspan=2, padx=2, pady=2)
        tk.Button(self.root, text='Annuity FV', width=12, height=2, command=self.open_annuity_fv)\
          .grid(row=7, column=2, columnspan=2, padx=2, pady=2)
        tk.Button(self.root, text='Perpetuity', width=6, height=2, command=self.open_perpetuity)\
          .grid(row=6, column=4, rowspan=2, padx=2, pady=2)

    def _on_button(self, char):
        if char in ('ln','log','exp','factorial','nCr'):
            self.entry.insert(tk.END, char + '(')
        else:
            self.entry.insert(tk.END, char)

    def clear(self):
        self.entry.delete(0, tk.END)

    def backspace(self):
        self.entry.delete(len(self.entry.get())-1, tk.END)

    def calculate(self):
        expr = self.entry.get()
        try:
            result = safe_eval(expr)
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, str(result))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # helper to build financial popups
    def _financial_window(self, title, fields, compute_fn):
        win = tk.Toplevel(self.root)
        win.title(title)
        entries = {}
        for i,(label, default) in enumerate(fields):
            tk.Label(win, text=label).grid(row=i, column=0, sticky='e', padx=4, pady=4)
            ent = tk.Entry(win)
            ent.grid(row=i, column=1, padx=4, pady=4)
            if default is not None:
                ent.insert(0, str(default))
            entries[label] = ent

        # frequency dropdown
        tk.Label(win, text="Compounding").grid(row=len(fields), column=0, sticky='e', padx=4, pady=4)
        freq_var = tk.StringVar(win)
        freq_var.set("Yearly")
        options = {"Yearly":1,"Half-Yearly":2,"Quarterly":4,"Monthly":12,"Daily":365,"Continuous":0}
        opt = tk.OptionMenu(win, freq_var, *options.keys())
        opt.grid(row=len(fields), column=1, padx=4, pady=4)

        result_label = tk.Label(win, text="", fg="blue")
        result_label.grid(row=len(fields)+2, column=0, columnspan=2, pady=4)

        def on_compute():
            try:
                vals = {label: float(ent.get()) for label,ent in entries.items()}
                m = options[freq_var.get()]
                res = compute_fn(vals, m)
                result_label.config(text=title+" = "+str(res))
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Compute", command=on_compute).grid(row=len(fields)+1, column=0, columnspan=2, pady=4)

    def open_fv(self):
        def fv_fn(v,m):
            PV, Rate, Years = v['PV'], v['Rate (%)']/100, v['Years']
            if m==0: return PV*math.exp(Rate*Years)
            return PV*(1+Rate/m)**(Years*m)
        self._financial_window("FV", [("PV",0),("Rate (%)",0),("Years",0)], fv_fn)

    def open_pv(self):
        def pv_fn(v,m):
            FV, Rate, Years = v['FV'], v['Rate (%)']/100, v['Years']
            if m==0: return FV*math.exp(-Rate*Years)
            return FV*(1+Rate/m)**(-Years*m)
        self._financial_window("PV", [("FV",0),("Rate (%)",0),("Years",0)], pv_fn)

    def open_rate(self):
        def rate_fn(v,m):
            PV, FV, Years = v['PV'], v['FV'], v['Years']
            if PV==0: raise ZeroDivisionError("PV cannot be zero")
            if m==0:
                return (1/Years)*math.log(FV/PV)
            return m*((FV/PV)**(1/(Years*m)) - 1)
        self._financial_window("Rate", [("PV",0),("FV",0),("Years",0)], rate_fn)

    def open_annuity_pv(self):
        def annpv_fn(v,m):
            PMT, Rate, Years = v['PMT'], v['Rate (%)']/100, v['Years']
            if m==0:
                if Rate==0: return PMT*Years
                return PMT*(1-math.exp(-Rate*Years))/Rate
            if Rate==0: return PMT*Years*m
            return PMT*(1-(1+Rate/m)**(-Years*m))/(Rate/m)
        self._financial_window("Annuity PV", [("PMT",0),("Rate (%)",0),("Years",0)], annpv_fn)

    def open_annuity_fv(self):
        def annfv_fn(v,m):
            PMT, Rate, Years = v['PMT'], v['Rate (%)']/100, v['Years']
            if m==0:
                if Rate==0: return PMT*Years
                return PMT*(math.exp(Rate*Years)-1)/Rate
            if Rate==0: return PMT*Years*m
            return PMT*((1+Rate/m)**(Years*m)-1)/(Rate/m)
        self._financial_window("Annuity FV", [("PMT",0),("Rate (%)",0),("Years",0)], annfv_fn)

    def open_perpetuity(self):
        def perp_fn(v,m):
            PMT, Rate = v['PMT'], v['Rate (%)']/100
            if Rate==0: raise ZeroDivisionError("Rate must be non-zero")
            if m==0: return PMT/Rate
            return PMT/(Rate/m)
        self._financial_window("Perpetuity", [("PMT",0),("Rate (%)",0)], perp_fn)

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()
```

How it works  
• Type any expression in the top entry (e.g. `2^3+ln(5)`, `factorial(6)+nCr(10,3)`) and press “=”  
• Financial buttons open dialogs for FV, PV, Rate, Annuity and Perpetuity calculations, with compounding choices including continuous.  
• All inputs are validated; errors show a pop‑up.
