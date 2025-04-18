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
    return render_template('index.html')


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
    return render_template('index.html')



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
    md_lines = []
    # Header with file name
    md_lines.append(f"**FILE:** {filename}\n\n")

    # Iterate each message and format
    for idx, msg in enumerate(conversation_messages_only, start=1):
        md_lines.append("---\n\n")
        md_lines.append(f"**Dictionary Item {idx:02d}**\n\n")
        md_lines.append(f"**Role:** {msg.get('role','')}\n\n")
        md_lines.append("**Content:**\n\n")
        md_lines.append(f"{msg.get('content','')}\n\n")
        md_lines.append("---\n")

    try:
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.writelines(md_lines)
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
    session['messages'] = []
    session.modified = True
    
    logger.info("Shutting down the server...")
    os._exit(0)  # Forcefully terminate the process
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
        user_input = user_input + "\n" + global_file_contents
        global_file_contents = ""
        message_accumulate.append([unique_id, counter, {"role": "user", "content": user_input}])
        conversation_history = get_conversation_history(unique_id, counter)

        session['messages'].append({"role": "user", "content": user_input})
        session.modified = True  # Ensure session is saved

        @copy_current_request_context
        def generate_response(unique_id: str, counter: int, conversation_history: list[Dict]) -> Generator[str, None, None]:
            global message_accumulate
            global model_name
            global claude_thinking_flag
            collected_chunks = ['\n']

            if "4o" in model_name:

                # Construct full prompt with system message
                full_prompt = []
                full_prompt.append(
                    {"role": "system", 
                     "content": [{"type": "text", "text": SYSTEM_MESSAGE}]
                     }
                )
                for messagedict in conversation_history:
                    if messagedict['role'] == 'user':
                        full_prompt.append(
                            {"role": "user", 
                             "content": [{"type": "text", "text": messagedict['content']}]
                             }
                        )
                    elif messagedict['role'] == 'assistant':
                        full_prompt.append(
                            {"role": "assistant", 
                             "content": [{"type": "text", "text": messagedict['content']}]
                             }
                        )

                try:
                    # Call OpenAI API with conversation history and streaming enabled
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=full_prompt,
                        response_format={"type": "text"},
                        temperature=0,
                        max_completion_tokens=8192,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0,
                        store=False,
                        stream=True,
                    )
             
                    for chunk in response:
                        if chunk.choices[0].delta.content is not None:
                            chunk_message = chunk.choices[0].delta.content
                            collected_chunks.append(chunk_message)
                            ##  chunk_message = chunk_message.replace("\\", "\\\\")
                            yield json.dumps({'content': chunk_message}) + "\n"

                    # After streaming, append the full bot message to the session
                    bot_message = ''.join(collected_chunks)
                    message_accumulate.append([unique_id, counter, {"role": "assistant", "content": bot_message}])

                    # Emit 'done' event to signal completion
                    yield json.dumps({'message': 'Stream complete'}) + "\n"

        
                except Exception as e:
                    logger.error(f"Error in generate_response: {e}", exc_info=True)
                    yield json.dumps({'error': 'An error occurred while processing your request. Please try again.'}) + "\n"


            elif "gpt-4.1" in model_name:

                # Construct full prompt with system message
                full_prompt = []
                full_prompt.append(
                    {"role": "system", 
                     "content": [{"type": "input_text", "text": "You are a helpful assistant. You provide comprehensive, insightful, forward-thinking responses to user queries."}]
                     }
                )
                for messagedict in conversation_history:
                    if messagedict['role'] == 'user':
                        full_prompt.append(
                            {"role": "user", 
                             "content": [{"type": "input_text", "text": messagedict['content']}]
                             }
                        )
                    elif messagedict['role'] == 'assistant':
                        full_prompt.append(
                            {"role": "assistant", 
                             "content": [{"type": "output_text", "text": messagedict['content']}]
                             }
                        )

                try:
                    # Call OpenAI API with conversation history
                    response = client.responses.create(
                        model=model_name,
                        input=full_prompt,
                        temperature=0,
                        max_output_tokens=16384,
                        top_p=1,
                        text={"format": {"type": "text"}},
                        reasoning={},
                        tools=[],
                        store=True,
                    )
                    bot_message = response.output_text
                    yield json.dumps({'content': bot_message}) + "\n"
                    message_accumulate.append([unique_id, counter, {"role": "assistant", "content": bot_message}])
        
                except Exception as e:
                    logger.error(f"Error in generate_response: {e}", exc_info=True)
                    yield json.dumps({'error': 'An error occurred while processing your request. Please try again.'}) + "\n"



            elif "o4-mini" in model_name: 

                # Construct full prompt with system message
                full_prompt = []
                full_prompt.append(
                    {"role": "developer", 
                     "content": [{"type": "input_text", "text": "You are a helpful assistant. You provide comprehensive, insightful, forward-thinking responses to user queries."}]
                     }
                )
                for messagedict in conversation_history:
                    if messagedict['role'] == 'user':
                        full_prompt.append(
                            {"role": "user", 
                             "content": [{"type": "input_text", "text": messagedict['content']}]
                             }
                        )
                    elif messagedict['role'] == 'assistant':
                        full_prompt.append(
                            {"role": "assistant", 
                             "content": [{"type": "output_text", "text": messagedict['content']}]
                             }
                        )

                try:
                    # Call OpenAI API with conversation history
                    response = client.responses.create(
                        model=model_name,
                        input=full_prompt,
                        text={"format": {"type": "text"}},
                        reasoning={"effort": "high"},
                        tools=[],
                        store=True,
                    )
                    bot_message = response.output_text
                    yield json.dumps({'content': bot_message}) + "\n"
                    message_accumulate.append([unique_id, counter, {"role": "assistant", "content": bot_message}])
        
                except Exception as e:
                    logger.error(f"Error in generate_response: {e}", exc_info=True)
                    yield json.dumps({'error': 'An error occurred while processing your request. Please try again.'}) + "\n"





            
            elif "o1-pro" in model_name:

                # Construct full prompt with system message
                full_prompt = []
                full_prompt.append(
                    {"role": "developer", 
                     "content": [{"type": "input_text", "text": "You are a helpful assistant. You provide comprehensive, insightful, forward-thinking responses to user queries."}]
                     }
                )
                for messagedict in conversation_history:
                    if messagedict['role'] == 'user':
                        full_prompt.append(
                            {"role": "user", 
                             "content": [{"type": "input_text", "text": messagedict['content']}]
                             }
                        )
                    elif messagedict['role'] == 'assistant':
                        full_prompt.append(
                            {"role": "assistant", 
                             "content": [{"type": "output_text", "text": messagedict['content']}]
                             }
                        )

                try:
                    # Call OpenAI API with conversation history
                    response = client.responses.create(
                        model=model_name,
                        input=full_prompt,
                        text={"format": {"type": "text"}},
                        reasoning={"effort": "high"},
                        tools=[],
                        store=False,
                    )
                    bot_message = response.output_text
                    yield json.dumps({'content': bot_message}) + "\n"
                    message_accumulate.append([unique_id, counter, {"role": "assistant", "content": bot_message}])
        
                except Exception as e:
                    logger.error(f"Error in generate_response: {e}", exc_info=True)
                    yield json.dumps({'error': 'An error occurred while processing your request. Please try again.'}) + "\n"


            elif ("o1" in model_name or "o3-mini" in model_name):
                
                # Construct full prompt with system message
                full_prompt = []
                full_prompt.append(
                    {"role": "developer", 
                     "content": [{"type": "text", "text": SYSTEM_MESSAGE}]
                     }
                )
                for messagedict in conversation_history:
                    if messagedict['role'] == 'user':
                        full_prompt.append(
                            {"role": "user", 
                             "content": [{"type": "text", "text": messagedict['content']}]
                             }
                        )
                    elif messagedict['role'] == 'assistant':
                        full_prompt.append(
                            {"role": "assistant", 
                             "content": [{"type": "text", "text": messagedict['content']}]
                             }
                        )

                try:
                    # Call OpenAI API with conversation history and streaming enabled
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=full_prompt,
                        response_format={"type": "text"},
                        reasoning_effort="high",
                        store=False,
                        stream=True,
                    )
             
                    for chunk in response:
                        if chunk.choices[0].delta.content is not None:
                            chunk_message = chunk.choices[0].delta.content
                            collected_chunks.append(chunk_message)
                            ##  chunk_message = chunk_message.replace("\\", "\\\\")
                            yield json.dumps({'content': chunk_message}) + "\n"

                    # After streaming, append the full bot message to the session
                    bot_message = ''.join(collected_chunks)
                    message_accumulate.append([unique_id, counter, {"role": "assistant", "content": bot_message}])

                    # Emit 'done' event to signal completion
                    yield json.dumps({'message': 'Stream complete'}) + "\n"

                except Exception as e:
                    logger.error(f"Error in generate_response: {e}", exc_info=True)
                    yield json.dumps({'error': 'An error occurred while processing your request. Please try again.'}) + "\n"


            elif "claude" in model_name:

                # Construct full prompt with system message
                full_prompt = []
                for messagedict in conversation_history:
                    if messagedict['role'] == 'user':
                        full_prompt.append(
                            {"role": "user", 
                             "content": [{"type": "text", "text": messagedict['content']}]
                             }
                        )
                    elif messagedict['role'] == 'assistant':
                        full_prompt.append(
                            {"role": "assistant", 
                             "content": [{"type": "text", "text": messagedict['content']}]
                             }
                        )

                try:
                    if (claude_thinking_flag == True):
                        with anthropic_client.messages.stream(
                            model=model_name,
                            max_tokens=32000,
                            system = SYSTEM_MESSAGE,
                            messages=full_prompt,
                            thinking={"type": "enabled", "budget_tokens": 16000},
                        ) as stream:
                            for chunk_text in stream.text_stream:
                                if chunk_text is not None:
                                    chunk_message = chunk_text
                                    collected_chunks.append(chunk_message)
                                    yield json.dumps({'content': chunk_message}) + "\n"
                    else: 

                        with anthropic_client.messages.stream(
                            model=model_name,
                            max_tokens=32000,
                            system = SYSTEM_MESSAGE,
                            messages=full_prompt,
                        ) as stream:
                            for chunk_text in stream.text_stream:
                                if chunk_text is not None:
                                    chunk_message = chunk_text
                                    collected_chunks.append(chunk_message)
                                    yield json.dumps({'content': chunk_message}) + "\n"

                    # After streaming, append the full bot message to the session
                    bot_message = ''.join(collected_chunks)
                    message_accumulate.append([unique_id, counter, {"role": "assistant", "content": bot_message}])

                    # Emit 'done' event to signal completion
                    yield json.dumps({'message': 'Stream complete'}) + "\n"
                
                except Exception as e:
                    logger.error(f"Error in generate_response: {e}", exc_info=True)
                    yield json.dumps({'error': 'An error occurred while processing your request. Please try again.'}) + "\n"

            
            elif "gemini" in model_name:
                # Construct full prompt with system message
                full_prompt = []
                for messagedict in conversation_history:
                    if messagedict['role'] == 'user':
                        full_prompt.append(
                            types.Content(
                                role="user",
                                parts=[
                                    types.Part.from_text(text=messagedict['content']),
                                ],
                            ),
                        )
                    elif messagedict['role'] == 'assistant':
                        full_prompt.append(
                            types.Content(
                                role="model",
                                parts=[
                                    types.Part.from_text(text=messagedict['content']),
                                ],
                            ),
                        )

                generate_content_config = types.GenerateContentConfig(
                    temperature=0,
                    tools = [types.Tool(google_search=types.GoogleSearch())],
                    safety_settings=[
                        types.SafetySetting(
                            category="HARM_CATEGORY_CIVIC_INTEGRITY",
                            threshold="OFF",  
                        ),
                    ],
                    response_mime_type="text/plain",
                    system_instruction=[
                        types.Part.from_text(text=SYSTEM_MESSAGE),
                    ],
                )

                try:
                    # Call Gemini API with conversation history and streaming enabled
                    stream = gemini_client.models.generate_content_stream(
                        model=model_name,
                        contents=full_prompt,
                        config=generate_content_config,
                    )
             
                    for chunk in stream:
                        if hasattr(chunk, 'text') and chunk.text:
                            chunk_message = chunk.text
                            collected_chunks.append(chunk_message)
                            ##  chunk_message = chunk_message.replace("\\", "\\\\")
                            yield json.dumps({'content': chunk_message}) + "\n"

                    # After streaming, append the full bot message to the session
                    bot_message = ''.join(collected_chunks)
                    message_accumulate.append([unique_id, counter, {"role": "assistant", "content": bot_message}])

                    # Emit 'done' event to signal completion
                    yield json.dumps({'message': 'Stream complete'}) + "\n"

        
                except Exception as e:
                    logger.error(f"Error in generate_response: {e}", exc_info=True)
                    yield json.dumps({'error': 'An error occurred while processing your request. Please try again.'}) + "\n"

            
            
            else:
                logger.error("Invalid Model")
                return jsonify({'error': "Invalid Model"}), 500

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
    counter = determine_counter(unique_id) + 1
    message_accumulate.append([unique_id, counter, {"role": "system", "content": SYSTEM_MESSAGE}])  
    return jsonify({'status': 'Conversation reset successfully'})


@app.route('/select_model', methods=['POST'])
def select_model() -> Dict[str, str]:
    global message_accumulate
    global model_name
    data = request.get_json()
    unique_id = data.get('uniqueId')
    model_name = data.get('selectedModel')
    return jsonify({'status': 'Model reset successfully'})


@app.route('/get_file_contents', methods=['GET'])
def get_file_contents():
    global global_file_contents
    return jsonify({"file_contents": global_file_contents})



#####################
# File Contents Viewer
#####################

@app.route('/filecontents')
def filecontents():
    return render_template('index2.html')

def choose_folder():
    # Use Tkinter to open a native folder selection dialog.
    root = tk.Tk()
    root.withdraw()  # Hide the root window.
    folder_path = filedialog.askdirectory(title="Select Folder")
    root.destroy()
    return folder_path


def get_directory_structure(rootdir):
    """
    Recursively builds a directory structure.
    Only includes files with specific extensions.
    """
    allowed_extensions = {'.text', '.txt', '.md', '.html', '.htm', '.php', '.js', '.css', '.py', '.json', '.ipynb'}
    structure = []

    try:
        for item in os.listdir(rootdir):
            full_path = os.path.join(rootdir, item)
            if os.path.isdir(full_path):
                children = get_directory_structure(full_path)
                if children:  # Only include directories that have valid children
                    structure.append({
                        "name": item,
                        "path": full_path,
                        "type": "directory",
                        "children": children
                    })
            else:
                _, ext = os.path.splitext(item)
                if ext.lower() in allowed_extensions:
                    structure.append({
                        "name": item,
                        "path": full_path,
                        "type": "file"
                    })
    except Exception as e:
        print(f"Error reading directory {rootdir}: {e}")

    return structure



@app.route('/open_folder', methods=['POST'])
def open_folder():
    global selected_folder
    global global_file_contents
    global_file_contents = ""
    folder = choose_folder()
    if folder:
        selected_folder = folder
        structure = get_directory_structure(folder)
        return jsonify({"folder": folder, "structure": structure})
    else:
        return jsonify({"error": "No folder selected"}), 400

@app.route('/refresh', methods=['GET'])
def refresh():
    global selected_folder
    global global_file_contents
    global_file_contents = ""
    if selected_folder:
        structure = get_directory_structure(selected_folder)
        return jsonify({"folder": selected_folder, "structure": structure})
    else:
        return jsonify({"error": "No folder selected"}), 400

@app.route('/load_selection', methods=['POST'])
def load_selection():
    global selected_folder
    global global_file_contents
    data = request.get_json()
    selected_files = data.get("files", [])
    result = ""
    if not selected_folder:
        return jsonify({"error": "No folder selected"}), 400

    for file in selected_files:
        # Compute the relative path to the selected folder.
        try:
            relative_path = os.path.relpath(file, selected_folder)
        except Exception as e:
            relative_path = file  # Fallback to the full path if error occurs.
        # Read file contents.
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading file: {e}"
        # Append formatted block.
        result += f"---\n\nFILE: {relative_path}\n\n{content}\n\n"
    result += "---"
    global_file_contents = result
    return jsonify({"result": result})

@app.route('/clear_loaded_content', methods=['POST'])
def clear_loaded_content():
    """
    Clears the global file contents stored on the backend.
    """
    global global_file_contents
    global_file_contents = ""
    return jsonify({"message": "global_file_contents cleared"}), 200



def find_available_port_iterative(start_port, end_port=65535):
    for port in range(start_port, end_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)):
                return port
    raise RuntimeError("No available port found.")



if __name__ == '__main__':
    print("Please wait while we find an available port for use.")
    port = find_available_port_iterative(5000)
    print(f"Serving on port {port}")
    serve(app, host='127.0.0.1', port=port)
