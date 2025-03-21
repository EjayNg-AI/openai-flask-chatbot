import sys
import os
import copy
from flask import copy_current_request_context, json, Flask, render_template, request, session, jsonify, Response, stream_with_context, send_from_directory
from openai import OpenAI
import anthropic
from dotenv import load_dotenv
from flask_session import Session
from waitress import serve 
import logging
from typing import Generator, Dict
from datetime import datetime, UTC
import uuid

SYSTEM_MESSAGE = "You are an expert in coding. " \
"Write code that is clean, efficient, modular, and well-documented. " \
"Ensure all code block are encased with triple backticks"

model_name = "chatgpt-4o-latest"

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
    token = str(uuid.uuid4())
    message_accumulate.append([token, 1, {"role": "system", "content": SYSTEM_MESSAGE}])
    return jsonify({'token': token, 'model_name': model_name})  # Send token as JSON response



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
    session['messages'] = []
    session.modified = True
    
    logger.info("Shutting down the server...")
    os._exit(0)  # Forcefully terminate the process
    return jsonify({"message": "Server is shutting down..."}), 200



@app.route('/stream', methods=['GET'])
def stream():
    global message_accumulate
    global model_name
    try:
        # Get prompt from URL parameters
        user_input = request.args.get('prompt')
        unique_id = request.args.get('uniqueId')
        model_name = request.args.get('modelmame')

        if (not user_input) or (len(user_input.strip()) == 0):
            return jsonify({'error': 'No prompt provided'}), 400

        if (not unique_id) or (len(unique_id.strip()) == 0):
            return jsonify({'error': 'No Unique Session ID provided'}), 400
        
        if (not model_name) or (len(model_name.strip()) == 0):
            return jsonify({'error': 'Invalid Model Name provided'}), 400
        
        
        counter = determine_counter(unique_id)

        # Append user message to session
        message_accumulate.append([unique_id, counter, {"role": "user", "content": user_input}])
        conversation_history = get_conversation_history(unique_id, counter)

        session['messages'].append({"role": "user", "content": user_input})
        session.modified = True  # Ensure session is saved

        @copy_current_request_context
        def generate_response(unique_id: str, counter: int, conversation_history: list[Dict]) -> Generator[str, None, None]:
            global message_accumulate
            global model_name
            collected_chunks = ['\n']
            cc = copy.deepcopy(conversation_history)
            sys_message = cc.pop(0)
            sys_anthropic = sys_message['content']

            if "gpt" in model_name:

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
            
            elif "o1-pro" in model_name:

                # Construct full prompt with system message
                full_prompt = []
                full_prompt.append(
                    {"role": "developer", 
                     "content": [{"type": "input_text", "text": SYSTEM_MESSAGE}]
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
                    # Call OpenAI API with conversation history and streaming enabled
                    response = client.responses.create(
                        model=model_name,
                        input=full_prompt,
                        text={"format": {"type": "text"}},
                        reasoning={"effort": "high"},
                        tools=[],
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
                try:
                    with anthropic_client.messages.stream(
                        model=model_name,
                        max_tokens=5000,
                        temperature=0,
                        system = sys_anthropic,
                        messages=cc,
                    ) as stream:
                        for chunk_text in stream.text_stream:
                            if chunk_text is not None:
                                chunk_message = chunk_text
                                collected_chunks.append(chunk_message)
                                chunk_message = chunk_message.replace("\\", "\\\\")
                                yield f"data: {json.dumps({'content': chunk_message})}\n\n"

                    # After streaming, append the full bot message to the session
                    bot_message = ''.join(collected_chunks)
                    message_accumulate.append([unique_id, counter, {"role": "assistant", "content": bot_message}])

                    # Emit 'done' event to signal completion
                    yield f"event: done\ndata: {json.dumps({'message': 'Anthropic Stream complete'})}\n\n"
                
                except anthropic.APIError as e:
                    yield f"data: Error in generating Anthropic API output: {str(e)}\n\n"
                except Exception as e:
                    yield f"data: Unexpected error: {str(e)}\n\n"

            else:
                logger.error("Invalid Model")
                return jsonify({'error': "Invalid Model"}), 500

        return Response(
            stream_with_context(generate_response(unique_id, counter, conversation_history)),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                # 'Transfer-Encoding': 'chunked' # This line is not applicable for waitress
            }
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


if __name__ == '__main__':
    serve(app, host='127.0.0.1', port=5000)