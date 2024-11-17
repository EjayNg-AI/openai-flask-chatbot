import os
from flask import copy_current_request_context, json, Flask, render_template, request, session, jsonify, Response, stream_with_context, send_from_directory
from openai import OpenAI
from dotenv import load_dotenv
from flask_session import Session
from waitress import serve 
import logging
from typing import Generator, Dict
from datetime import datetime, UTC
import uuid

SYSTEM_MESSAGE = "You are a helpful assistant.\n\nProvide Python code that is well-documented with clear docstrings and type hints for all functions. Ensure that the code, comments and docstrings are concise, avoids unnecessary line spaces, and adheres to PEP 8 (Python Enhancement Proposal 8) guidelines.\n\nMake sure the code is easy to understand, even for readers unfamiliar with the logic or purpose of each function.\n\n## Steps\n\n1. **Add Type Hints**: \n   - Use Python type hints to specify the types of all function inputs and outputs. This enhances code readability and helps other developers understand the code better.\n\n2. **Write Concise Docstrings**:\n   - Add informative docstrings to every function. Each docstring should include:\n     - The function’s purpose.\n     - A description of the parameters, including their types and roles.\n     - A description of the return value, including its type and content.\n     - Any exceptions the function might raise.\n\n3. **Ensure Clean Code**:\n   - Use consistent, meaningful variable names.\n   - Avoid redundancy and keep functions simple.\n\n4. **Provide Example Usage**:\n   - If a function’s behavior isn’t immediately obvious, include a simple example in the docstring to demonstrate its use and expected output.\n\n## Output Format\n\n- Provide a complete Python script with functions that include type hints and docstrings.\n- Each function’s docstring should use triple double-quotes (`\"\"\"`) and include the following sections:\n  1. **Function Description**\n  2. **Args**: (if applicable)\n  3. **Returns**: (if applicable)\n  4. **Raises**: (if applicable)\n  5. **Example**: (optional, if the function’s behavior may not be obvious)\n\n## Example\n\n ```python \nfrom typing import List, Optional\n\ndef calculate_average(numbers: List[float]) -> Optional[float]:\n    \"\"\"\n    Calculate the average of a list of numbers.\n\n    Args:\n        numbers (List[float]): A list of floating-point numbers.\n\n    Returns:\n        Optional[float]: The average of the numbers, or None if the list is empty.\n\n    Raises:\n        ValueError: If any element in the list is not a valid number.\n\n    Example:\n        >>> calculate_average([1.0, 2.0, 3.0])\n        2.0\n    \"\"\"\n    if not numbers:\n        return None\n    for num in numbers:\n        if not isinstance(num, (int, float)):\n            raise ValueError(\"All elements must be numbers.\")\n    return sum(numbers) / len(numbers)\n ``` \n\n## Notes\n\n- Consider edge cases, such as:\n  - Handling an empty list.\n  - Managing incorrect data types.\n- Ensure consistent formatting for all docstrings.\n- Where applicable, include both value types (e.g., `int`, `float`) and value descriptions to provide extra clarity in type hints and docstrings."

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure with strong secret key - avoid regenerating on each restart
app.secret_key = os.getenv('FLASK_SECRET_KEY') or os.urandom(24)

# Configure server-side session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
#  Permanent Session Lifetime is not applicable for temporary sessions
#  app.config['PERMANENT_SESSION_LIFETIME'] = 36000  # Session timeout in seconds

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
    logger.critical(f"Failed to initialize OpenAI client: {e}")
    raise



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
    token = str(uuid.uuid4()) + '-system-generated'
    message_accumulate.append([token, 1, {"role": "system", "content": SYSTEM_MESSAGE}])
    return jsonify({'token': token})  # Send token as JSON response



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
    try:
        # Get prompt from URL parameters
        user_input = request.args.get('prompt')
        unique_id = request.args.get('uniqueId')

        if (not user_input) or (len(user_input.strip()) == 0):
            return jsonify({'error': 'No prompt provided'}), 400

        if (not unique_id) or (len(unique_id.strip()) == 0):
            return jsonify({'error': 'No Unique Session ID provided'}), 400
        
        counter = determine_counter(unique_id)

        # Append user message to session
        message_accumulate.append([unique_id, counter, {"role": "user", "content": user_input}])
        conversation_history = get_conversation_history(unique_id, counter)

        session['messages'].append({"role": "user", "content": user_input})
        session.modified = True  # Ensure session is saved

        @copy_current_request_context
        def generate_response(unique_id: str, counter: int, conversation_history: list[Dict]) -> Generator[str, None, None]:
            global message_accumulate
            try:
                # Send message indicating new response is starting
                # yield f"data: {json.dumps({'newResponse': True})}\n\n"

                # Call OpenAI API with conversation history and streaming enabled
                response = client.chat.completions.create(
                    model="chatgpt-4o-latest",   
                    messages=conversation_history,
                    temperature=0.25,  # Added some randomness for more natural responses
                    max_tokens=12000,  # Reduced token limit to prevent timeouts
                    stream=True
                )

                collected_chunks = ['\n']
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        chunk_message = chunk.choices[0].delta.content
                        collected_chunks.append(chunk_message)
                        chunk_message = chunk_message.replace("\\", "\\\\")
                        yield f"data: {json.dumps({'content': chunk_message})}\n\n"

                # After streaming, append the full bot message to the session
                bot_message = ''.join(collected_chunks)
                message_accumulate.append([unique_id, counter, {"role": "assistant", "content": bot_message}])

                # Emit 'done' event to signal completion
                yield f"event: done\ndata: {json.dumps({'message': 'Stream complete'})}\n\n"
        
            except Exception as e:
                logger.error(f"Error in generate_response: {e}", exc_info=True)
                yield f"data: Error: An error occurred while processing your request. Please try again.\n\n"
        
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



if __name__ == '__main__':
    serve(app, host='127.0.0.1', port=5000)