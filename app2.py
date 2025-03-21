from flask import Flask, render_template, jsonify, request
import os
import tkinter as tk
from tkinter import filedialog

app = Flask(__name__)

# Global variable to store the selected folder path.
selected_folder = None

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
    Each file/directory is represented as a dict.
    """
    structure = []
    try:
        for item in os.listdir(rootdir):
            full_path = os.path.join(rootdir, item)
            if os.path.isdir(full_path):
                structure.append({
                    "name": item,
                    "path": full_path,
                    "type": "directory",
                    "children": get_directory_structure(full_path)
                })
            else:
                structure.append({
                    "name": item,
                    "path": full_path,
                    "type": "file"
                })
    except Exception as e:
        print(f"Error reading directory {rootdir}: {e}")
    return structure

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/open_folder', methods=['POST'])
def open_folder():
    global selected_folder
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
    if selected_folder:
        structure = get_directory_structure(selected_folder)
        return jsonify({"folder": selected_folder, "structure": structure})
    else:
        return jsonify({"error": "No folder selected"}), 400

@app.route('/load_selection', methods=['POST'])
def load_selection():
    global selected_folder
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
    return jsonify({"result": result})

if __name__ == '__main__':
    # Run the app on localhost. Debug mode is on for development.
    app.run(debug=True)
