import tkinter as tk
from tkinter import filedialog
from flask import Flask, request, render_template_string

app = Flask(__name__)

def select_files_via_dialog():
    # Create a hidden Tkinter root window.
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    # Open a dialog allowing the user to select multiple files.
    # Note: This dialog typically allows selecting multiple files from a single directory.
    file_paths = filedialog.askopenfilenames(title="Select Files")
    root.destroy()  # Clean up the Tkinter instance
    return list(file_paths)

@app.route('/')
def index():
    # A simple HTML page with a button to trigger file selection.
    html_content = '''
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Python File Dialog</title>
      </head>
      <body>
        <h1>Select Files via Python File Dialog</h1>
        <form action="/select" method="post">
          <button type="submit">Select Files</button>
        </form>
      </body>
    </html>
    '''
    return render_template_string(html_content)

@app.route('/select', methods=['POST'])
def select():
    # This function is triggered when the button is clicked.
    file_paths = select_files_via_dialog()
    # Return the list of selected file paths to the user.
    return f"Selected file paths: {file_paths}"

if __name__ == '__main__':
    app.run(debug=True)

