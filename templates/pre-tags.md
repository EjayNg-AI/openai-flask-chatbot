**FILE:** /home/ngejay3046/api/openai-flask-chatbot/templates/pre-tags.md

---

**Dictionary Item 01**

**Role:** system

**Content:**

You are an expert in coding. Write code that is clean, efficient, modular, and well-documented. Ensure all code block are encased with triple backticks.

---
---

**Dictionary Item 02**

**Role:** user

**Content:**

Please refer to the attached project files which form part of a full stack web application.

When sanitizing HTML tags, one issue is unresolved. The frontend places <pre> ... </pre> tags upon opening a new page. In particular, if a file is being loaded, the markdown contents retrieved from local storage is placed within those tags. This behavior is *intentional*.

However, upon subsequent conversation turns, sanitization turns those <pre> ... </pre> tags into &lt;pre&gt; ... &lt;/pre&gt; -- and this behavior does not align with the original intent of the pre tags.

I wish the sanization behavior to be retain, but also want to resolve this remaining issue. Please suggest solutions.
---

FILE: templates/index.html

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Chatbot powered by State of the Art LLMs</title>

    <script>
      window.MathJax = {
        tex: {
          inlineMath: [
            ["$", "$"],
            ["\\(", "\\)"],
          ],
          displayMath: [
            ["$$", "$$"],
            ["\\[", "\\]"],
          ],
        },
        options: {
          skipHtmlTags: ["script", "noscript", "style", "textarea", "pre"],
        },
      };
    </script>

    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link
      rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/default.min.css"
    />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
    <link
      href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap"
      rel="stylesheet"
    />

    <style>
      body {
        font-family: "Roboto", sans-serif;
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        height: 100vh;
        overflow: hidden;
      }

      .control-panel {
        display: flex;
        gap: 10px;
        padding: 20px;
        background-color: #f0f0f0;
        border-bottom: 1px solid #ddd;
      }

      .query-input {
        font-size: 16px;
        flex: 1;
        resize: none;
        line-height: 1.2;
        min-height: 10px;
        max-height: 70vh;
        overflow-y: auto;
        transition: height 0.2s ease;
        padding: 2.3px;
        border: 1px solid #ddd;
        border-radius: 4px;
      }

      .button {
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
        width: 80px;
        /* Fixed width */
        height: 60px;
        /* Fixed height */
        flex-shrink: 0;
        /* Prevent buttons from shrinking */
      }

      .toggle-dark-mode {
        background-color: #008080;
        color: white;
      }

      .toggle-dark-mode:hover {
        background-color: #005f5f;
      }

      .sanitize-btn {
        background-color: #0066cc;
        color: white;
      }

      .sanitize-btn:hover {
        background-color: #004999;
      }

      .copy-prompt-btn:hover {
        background-color: #ff9800;
        color: white;
      }

      .copy-prompt-btn {
        background-color: #f57c00;
        color: white;
      }

      .load-btn {
        background-color: #aa4444;
        color: white;
      }

      .load-btn:hover {
        background-color: #dd7777;
        color: white;
      }

      .save-btn {
        background-color: #444444;
        color: white;
      }

      .save-btn:hover {
        background-color: #777777;
        color: white;
      }

      .submit-btn {
        background-color: #4caf50;
        color: white;
      }

      .submit-btn:hover {
        background-color: #45df49;
        color: white;
      }

      .clearscreen-btn {
        background-color: #550055;
        color: white;
      }

      .clearscreen-btn:hover {
        background-color: #990099;
        color: white;
      }

      .close-btn {
        background-color: #0000aa;
        color: white;
      }

      .close-btn:hover {
        background-color: #0055ff;
        color: white;
      }

      .file-viewer-btn {
        background-color: #aa0044;
        color: white;
      }

      .file-viewer-btn:hover {
        background-color: #cc0066;
        color: white;
      }

      .consolidate-btn {
        background-color: #444444;
        color: white;
      }

      .consolidate-btn:hover {
        background-color: #777777;
        color: white;
      }

      .reset-btn {
        background-color: #f44336;
        color: white;
      }

      .reset-btn:hover {
        background-color: #ff0099;
        color: white;
      }

      .conversation-turn {
        margin-bottom: 20px;
        padding-bottom: 20px;
        border-bottom: 1px solid #eee;
      }

      .query-container {
        padding: 20px;
        background-color: #f0f0f0;
        border-bottom: 1px solid #ddd;
      }

      .container {
        display: flex;
        flex: 1;
        overflow: hidden;
      }

      .editor,
      .preview {
        width: 50%;
        padding: 20px;
        box-sizing: border-box;
        overflow: auto;
        min-width: 0;
      }

      .editor {
        border-right: 1px solid #ddd;
        background-color: #f9f9f9;
      }

      #markdown-input {
        width: 100%;
        height: 100%;
        resize: none;
        border: none;
        outline: none;
        font-size: 16px;
        font-family: "Courier New", Courier, monospace;
      }

      .preview {
        background-color: #fff;
      }

      pre {
        position: relative;
        background-color: #f0f0f0;
        padding: 15px;
        overflow: auto;
        border-radius: 5px;
      }

      pre button.copy-btn {
        position: absolute;
        top: 10px;
        right: 10px;
        background-color: #4caf50;
        border: none;
        color: white;
        padding: 5px 10px;
        cursor: pointer;
        border-radius: 3px;
        font-size: 12px;
      }

      blockquote {
        border-left: 5px solid #ccc;
        padding-left: 15px;
        color: #666;
        margin: 1em 0;
      }

      .model-controls {
        display: flex;
        align-items: center;
        gap: 5px;
        padding: 5px;
        background-color: #ffffff;
        border-bottom: 1px solid #000000;
      }

      .model-controls .drop-down-menu {
        display: flex;
        align-items: center;
        gap: 5px;
      }

      /* ─── Light‑mode fixes for the left “file‑browser” panel ─── */
      body:not(.dark-mode) #file-browser {
        background-color: #fafafa;
        color: #111;
      }

      body:not(.dark-mode) #directory-tree .directory-entry,
      body:not(.dark-mode) #directory-tree .toggle-triangle {
        color: #222;
      }

      body:not(.dark-mode) #directory-tree a.file-link {
        color: #007bff;
      }

      body:not(.dark-mode) #directory-tree a.file-link:hover {
        color: #0056b3;
      }

      #markdown-input {
        white-space: pre-wrap;
        word-break: break-word;
        overflow-wrap: anywhere;
      }

      #chat-panel,
      .container,
      .editor,
      .preview {
        min-width: 0;
      }

      .preview pre {
        overflow-x: auto;
      }

      /* ---------------- Dark Mode Styles ---------------- */
      /* When the body receives the "dark-mode" class the following rules apply */
      body.dark-mode {
        background-color: #121212;
        color: white;
        /* General text color */
      }

      /* Override background and text for control panels & header areas */
      body.dark-mode .control-panel,
      body.dark-mode .model-controls {
        background-color: #181818;
        color: white;
      }

      /* Editor and preview areas use near‑black backgrounds with white text */
      body.dark-mode .editor,
      body.dark-mode .preview,
      body.dark-mode textarea {
        background-color: #121212;
        color: white;
      }

      /* Code blocks use a different dark background for contrast */
      body.dark-mode pre {
        background-color: #2e2e2e;
        color: white;
      }

      /* ---------------- End Dark Mode Styles ---------------- */

      /* ———— new two‐pane layout ———— */
      #content-wrapper {
        display: flex;
        flex: 1;
        overflow: hidden;
      }

      #file-browser {
        flex: 0 0 240px;
        height: 100%;
        min-width: 120px;
        border-right: 1px solid #ccc;
        padding: 8px;
        box-sizing: border-box;
        overflow-y: auto;
      }

      #file-browser button {
        margin: 3px 0;
        width: 100%;
        padding: 6px 8px;
        font-size: 0.85em;
      }

      #directory-tree .node {
        margin-left: 20px;
      }

      #directory-tree .toggle-triangle {
        display: inline-block;
        width: 1em;
        text-align: center;
        cursor: pointer;
        user-select: none;
        margin-right: 5px;
      }

      #directory-tree .directory-entry {
        font-weight: bold;
      }

      #directory-tree a.file-link {
        display: block;
        color: #00cc00;
        text-decoration: none;
        margin: 2px 0;
      }

      #directory-tree a.file-link:hover {
        text-decoration: underline;
        color: #00ff00;
      }

      /* pull your old .container into the right pane */
      #chat-panel {
        flex: 1;
        display: flex;
        flex-direction: column;
      }
    </style>
  </head>

  <body>
    <!-- … your model‐controls & control‐panel … -->

    <div id="content-wrapper">
      <!-- LEFT: file‐browser -->
      <div id="file-browser">
        <button id="open-folder">Open Directory</button>
        <button id="refresh">Refresh</button>
        <div id="directory-tree"></div>
      </div>

      <!-- RIGHT: your existing chat UI -->
      <div id="chat-panel">
        <div class="model-controls">
          <div class="drop-down-menu">
            <form>
              <label for="language-model">Select Language Model:</label>
              <select id="language-model">
                <option value="chatgpt-4o-latest">chatgpt-4o-latest</option>
                <option value="gpt-4o">gpt-4o</option>
                <option value="gpt-4.1">gpt-4.1</option>
                <option value="o1-pro">o1-pro</option>
                <option value="o3">o3</option>
                <option value="o4-mini">o4-mini</option>
                <option value="o3-mini">o3-mini</option>
                <option value="claude-3-7-sonnet-20250219">
                  claude-3-7-sonnet-20250219
                </option>
                <option value="gemini-2.5-flash-preview-04-17">
                  gemini-2.5-flash-preview-04-17
                </option>
                <option value="gemini-2.5-pro-preview-03-25">
                  gemini-2.5-pro-preview-03-25
                </option>
              </select>
            </form>
            <button id="model_choice">Select Model</button>
          </div>
          <div>
            <label style="margin-left: 10px">
              <input type="checkbox" id="claude-thinking" />
              Claude Extended Thinking
            </label>
          </div>
          <div>
            <label style="margin-left: 10px">
              <input type="checkbox" id="math-render" />
              Escape Output & Render Math
            </label>
          </div>
          <div>
            <button id="file-viewer-btn" class="file-viewer-btn">
              File Viewer
            </button>
          </div>
          <div style="display: flex; align-items: center; gap: 5px">
            <button id="consolidate-btn" class="consolidate-btn">
              Consolidate
            </button>
            <select id="consolidate-option">
              <option value="fully_updated">Fully Updated Files</option>
              <option value="refactor">Refactor Code</option>
              <option value="critique">Critique Code</option>
              <option value="synopsis">Synopsis of Project</option>
            </select>
          </div>
          <div>
            <button id="sanitize-btn" class="sanitize-btn">
              Sanitize Scripts
            </button>
          </div>
          <div>
            <button id="toggle-dark-mode" class="toggle-dark-mode">
              Toggle Dark Mode
            </button>
          </div>
        </div>

        <div class="control-panel">
          <textarea
            type="text"
            id="query-input"
            class="query-input"
            placeholder="Enter your question..."
          ></textarea>
          <button id="copy-prompt-btn" class="button copy-prompt-btn">
            Copy Prompt
          </button>
          <button id="submit-btn" class="button submit-btn">Submit</button>
          <button id="clearscreen-btn" class="button clearscreen-btn">
            Clear Screen
          </button>
          <button id="load-btn" class="button load-btn">Load</button>
          <button id="save-btn" class="button save-btn">Save</button>
          <button id="reset-btn" class="button reset-btn">Reset</button>
          <button id="shutdown-btn" class="button close-btn">Close</button>
        </div>
        <div class="container">
          <div class="editor">
            <textarea id="markdown-input"></textarea>
          </div>
          <div class="preview" id="preview"></div>
        </div>
      </div>
    </div>

    <script>
      hljs.highlightAll();

      const dropdown_menu = document.getElementById("language-model");
      const queryInput = document.getElementById("query-input");
      const copyPromptBtn = document.getElementById("copy-prompt-btn");
      const submitBtn = document.getElementById("submit-btn");
      const clear_scr = document.getElementById("clearscreen-btn");
      const loadBtn = document.getElementById("load-btn");
      const SaveBtn = document.getElementById("save-btn");
      const closeBtn = document.getElementById("shutdown-btn");
      const resetBtn = document.getElementById("reset-btn");
      const markdownInput = document.getElementById("markdown-input");
      const preview = document.getElementById("preview");
      const choose_model = document.getElementById("model_choice");
      const claudeThinking = document.getElementById("claude-thinking");
      const MathRender = document.getElementById("math-render");

      submitBtn.disabled = true;
      SaveBtn.disabled = true;
      choose_model.disabled = true;
      clear_scr.disabled = true;

      let uniqueId;
      let model_name;
      let streaming_flag = true;
      let claude_thinking_flag = false;
      let math_render_flag = false;
      let consolidate_flag = false;
      let currentFileContents = "";
      let consolidate_option = "fully_updated";
      let prompt_consolidate =
        "In this conversation, I initially provided project code files. Based on all the feedback, suggestions, and revisions discussed so far, please output the full, updated set of project files, organized and ready to copy into my development environment. Reflect all code, structural, and dependency updates. Ensure that the final output is fully integrated, consistent, and ready for use.";

      let refactoringPrompt = `Objective: Refactor and clean up the existing codebase to improve its readability, maintainability, and modularity **without altering any existing functionality or user experience**.

Strict Constraints:
1. Do not introduce any changes in logic, business rules, or user-facing behavior.
2. Preserve exact input/output behavior, side-effects, UI layout/flow, and performance characteristics (within a negligible margin).
3. Do not remove or simplify code that appears redundant unless it has *zero* effect on behavior and is *provably unreachable or unnecessary*.

Goals of Refactoring:
- Improve structure, clarity, and cohesion of the codebase.
- Reduce deeply nested logic, excessive coupling, and repetition.
- Apply standard best practices (e.g., DRY, SRP, consistent naming, modularization).
- Introduce helper functions, configuration files, or abstractions only if they increase clarity.
- Document public interfaces, key functions, and assumptions where lacking.

Code Coverage & Testing:
- All changes must be accompanied by unit or integration tests where possible.
- Validate that test results remain unchanged post-refactor. If no test suite exists, assist in generating regression tests from current behavior.

Deliverables:
- Refactored code with in-line comments on major changes or restructuring decisions.
- A summary of the changes, including files touched, functions moved/extracted, patterns replaced, and any identified anti-patterns.
- (Optional) A cleanup roadmap for future maintainability and architectural improvements.

Output:
- Output one refactored file at a time, including the original file name and a summary of changes, recommendations and other notes.
- Prompt the user to confirm the changes before proceeding to the next file.
`;

      let synopsisPrompt = `# Provide structured metadata of codebase

**You are a senior software engineer and architect.** You have been provided with multiple source files in your current context. For **each** file, please extract and summarize the following metadata. Then, provide an **overall, high-level summary** of the entire codebase at the end.

---

## I. Codebase-Level Information

1. **Directory Structure**
   - Provide a tree-style or indented list of file and folder paths relative to the project root.

2. **Programming Languages & Key Technologies**
   - List the programming languages, frameworks, libraries, and technologies used across the codebase.

3. **Entry Points & Execution Flow**
   - Identify main entry points.
   - Briefly describe how control flows through the application from start to finish.

4. **High-Level Architecture Overview**
   - Summarize the architectural style (e.g., monolithic, microservices, event-driven).
   - Describe major components or modules and how they interact.

---

## II. File-Level Information (Repeat for Each File)

For each **source code file**, provide the following metadata:

1. **File Path**  
   - The full path (or best estimate if partial paths are given).  

2. **File Type/Language**  
   - Explicitly state the language or file type (e.g., Python, JavaScript, CSS, HTML, JSON).  

3. **High-Level Summary/Purpose**  
   - A concise (1–3 sentence) natural language description of what the file does or which feature/component it represents.  

4. **Key Entities Defined**  
   - A list of major classes, functions, methods, constants, variables, interfaces, or components.  

5. **Dependencies (Imports/Requires)**  
   - A list of other modules/files (from **within** this codebase) that this file imports or requires.  

6. **Exports/Public Interface**  
   - A list of entities (classes, functions, constants, etc.) that are publicly exposed and can be used by other files.  

7. **Docstrings for Python Modules**  
   - For *python modules*, provide docstrings for each class and function therein.

---

## Output Format

- Format your final answer as a **Markdown document** with clear headings and subheadings.
- First, provide a **"Codebase-Level Information"** section.
- Then, list all **file-level** metadata (in whichever order the files appear or by directory order).
- If any of the elements do not apply to a particular file, please omit them or mark them as “N/A.”  
- Make sure to keep your headings and structure consistent.
- Be **concise** but **complete**. Avoid repeating boilerplate. Capture purpose, semantics, and relationships, not just syntax.

---

`;

      /**
       * sanitizeText scans the given markdown text and escapes any HTML tags
       * (e.g. <img>, <a>, <p> etc.) that appear outside of code blocks and
       * that are not already escaped.
       *
       * This version recognizes code blocks fenced with either three or four backticks.
       *
       * @param {string} text - The markdown text to sanitize.
       * @returns {string} - The sanitized text.
       */
      function sanitizeText(text) {
        /**
         * sanitizeInline processes a given text segment (outside fenced code blocks)
         * and escapes any HTML tags found outside inline code blocks.
         *
         * @param {string} segment - A portion of text that might include inline code.
         * @returns {string} - The segment with HTML tags normalized and escaped.
         */
        function sanitizeInline(segment) {
          // Split the segment by inline code blocks wrapped in single backticks.
          var inlineParts = segment.split(/(`[^`]*`)/g);
          for (var i = 0; i < inlineParts.length; i++) {
            // Process only parts that are not inline code.
            if (!/^`[^`]*`$/.test(inlineParts[i])) {
              inlineParts[i] = inlineParts[i].replace(
                /<\s*(\/?)\s*(["']?)([a-zA-Z][a-zA-Z0-9-]*)(["']?)([^>]*)>/g,
                function (match, slash, openQuote, tagName, closeQuote, rest) {
                  var trimmedRest = rest.trim();
                  var normalizedTag =
                    "&lt;" +
                    (slash ? slash : "") +
                    (openQuote ? openQuote : "") +
                    tagName +
                    (closeQuote ? closeQuote : "");
                  if (trimmedRest === "/") {
                    normalizedTag += trimmedRest + "&gt;";
                  } else if (trimmedRest) {
                    normalizedTag += " " + trimmedRest + "&gt;";
                  } else {
                    normalizedTag += "&gt;";
                  }
                  return normalizedTag;
                }
              );
            }
          }
          return inlineParts.join("");
        }

        // Updated regex to recognize code blocks with either 3 or 4 backticks.
        var parts = text.split(/((?:`{3,4})[\s\S]*?(?:`{3,4}))/g);
        for (var j = 0; j < parts.length; j++) {
          // Only sanitize parts that are not identified as code blocks.
          if (!/^(?:`{3,4})/.test(parts[j])) {
            parts[j] = sanitizeInline(parts[j]);
          }
        }
        return parts.join("");
      }

      /**
       * Unescapes HTML entities (&lt; and &gt;) inside fenced code blocks.
       * This version uses a regex that captures the entire block, ensures that
       * the fence markers are the same (by using a backreference), and then unescapes
       * the content between the markers.
       *
       * @param {string} text - The input markdown text.
       * @returns {string} - The text with HTML entities unescaped inside fenced code blocks.
       */
      function unescapeHtmlEntitiesInFencedCodeBlocks(text) {
        // This regex matches a fence (3 or more backticks), followed by any content,
        // and then the same fence again (the backreference \1 ensures that the closing
        // fence is exactly the same as the opening fence).
        const codeBlockRegex = /(^`{3,})([\s\S]*?)(^\1$)/gm;

        return text.replace(
          codeBlockRegex,
          (match, fence, codeContent, closingFence) => {
            // Unescape HTML entities only in the content of the code block.
            const unescapedContent = codeContent
              .replace(/&lt;/g, "<")
              .replace(/&gt;/g, ">");
            return fence + unescapedContent + closingFence;
          }
        );
      }

      /*
  // Example usage:
  const originalMarkdown = "Normal text <p>with tag</p>\n\n````\n// Some code: &lt;div&gt;should be unescaped&lt;/div&gt;\n// More code: &lt;span&gt;should not be escaped by sanitizeText&lt;/span&gt;\n````\n\nMore text with <a href='#'>link</a>.";
  
  // First, sanitize tags outside code blocks:
  const sanitized = sanitizeText(originalMarkdown);
  const finalText = unescapeHtmlEntitiesInFencedCodeBlocks(sanitized);
  // finalText is now: "Normal text &lt;p&gt;with tag&lt;/p&gt;\n\n````\n// Some code: &lt;div&gt;should be unescaped&lt;/div&gt;\n// More code: &lt;span&gt;should not be escaped by sanitizeText&lt;/span&gt;\n````\n\nMore text with &lt;a href='#'&gt;link&lt;/a&gt;."
  
  console.log("Original:\n", originalMarkdown);
  console.log("\nSanitized:\n", sanitized);
  console.log("\nFinal Text (Restored inside code):\n", finalText);
  */

      /**
       * sanitizeLeftPanel retrieves the current contents of the editor (left panel),
       * sanitizes it (escaping any tags that are not already inside code blocks),
       * updates the editor with the sanitized content, and then re-renders the preview.
       */
      function sanitizeLeftPanel() {
        var editor = document.getElementById("markdown-input");
        if (!editor) {
          console.error("Editor element (#markdown-input) not found.");
          return;
        }
        var originalText = editor.value;
        var sanitizedText = sanitizeText(originalText);
        if (sanitizedText !== originalText) {
          editor.value = sanitizedText;
          // Re-render the preview; the renderMarkdown function is defined elsewhere.
          renderMarkdown(true);
          alert(
            "Sanitization complete. Tags outside code blocks have been escaped."
          );
        } else {
          alert("No unsanitized tags found outside code blocks.");
        }
      }

      // Attach the sanitizeLeftPanel function to the new button's click event.
      document
        .getElementById("sanitize-btn")
        .addEventListener("click", sanitizeLeftPanel);

      // When the 'Toggle Dark Mode' button is clicked, toggle the "dark-mode" class on the body element
      document
        .getElementById("toggle-dark-mode")
        .addEventListener("click", function () {
          document.body.classList.toggle("dark-mode");
        });

      MathRender.addEventListener("change", async () => {
        math_render_flag = MathRender.checked;
        // Send to backend
        try {
          await fetch("/update-math-render", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              math_render_flag: math_render_flag,
            }),
          });
          if (markdownInput) {
            markdownInput.value += `\n Math Rendering: ${math_render_flag} \n`;
          }
        } catch (err) {
          console.error("Failed to update backend:", err);
        }
      });

      claudeThinking.addEventListener("change", async () => {
        claude_thinking_flag = claudeThinking.checked;
        // Send to backend
        try {
          await fetch("/update-claude-thinking", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              claude_thinking_flag: claude_thinking_flag,
            }),
          });
          if (markdownInput) {
            markdownInput.value += `\n Claude Extended Thinking: ${claude_thinking_flag} \n`;
          }
        } catch (err) {
          console.error("Failed to update backend:", err);
        }
      });

      document
        .getElementById("file-viewer-btn")
        .addEventListener("click", () => {
          window.open("/filecontents", "_blank");
        });

      document.getElementById("load-btn").addEventListener("click", () => {
        // this will cause the Flask handler to pop up a native file chooser
        window.open("/load", "_blank");
      });

      document
        .getElementById("consolidate-btn")
        .addEventListener("click", () => {
          const consolidateOption =
            document.getElementById("consolidate-option").value;

          if (!uniqueId || !model_name || streaming_flag === undefined) {
            alert("Missing required data.");
            return;
          }

          const params = new URLSearchParams({
            uniqueId: uniqueId,
            model_name: model_name,
            streaming_flag: streaming_flag,
            option: consolidateOption,
          });

          const url = `/consolidate?${params.toString()}`;
          window.open(url, "_blank");
        });

      function updateFileContents(contents) {
        currentFileContents = contents;
        console.log("File contents updated in main window.");
      }

      // Fetch token from the Flask backend
      fetch("/get-token")
        .then((response) => response.json())
        .then((data) => {
          // Set the global uniqueId
          uniqueId = data.token;
          model_name = data.model_name;
          streaming_flag = !["o1-pro"].includes(model_name);
          consolidate_flag = data.consolidate_conversation_flag;
          consolidate_option = data.consolidate_option;
          const initialMarkdown = data.markdown_content || "";
          setTimeout(() => {
            if (markdownInput) {
              let sanitizedMarkdown = sanitizeText(initialMarkdown);
              markdownInput.value =
                "<pre> \n" + sanitizedMarkdown + "\n </pre>";
              markdownInput.scrollTop = markdownInput.scrollHeight;
              markdownInput.value += `\n\n Unique Session ID: ${uniqueId} \n`;
              markdownInput.value += `\n Model: ${model_name} \n`;
              markdownInput.value += `\n Streaming: ${streaming_flag} \n`;
              renderMarkdown(true);
              submitBtn.disabled = false;
              SaveBtn.disabled = false;
              choose_model.disabled = false;
              clear_scr.disabled = false;
            }
          }, 0);
          if (consolidate_flag) {
            if (consolidate_option === "fully_updated") {
              queryInput.value =
                "In this conversation, I initially provided project code files. Based on all the feedback, suggestions, and revisions discussed so far, please output the full, updated set of project files, organized and ready to copy into my development environment. Reflect all code, structural, and dependency updates. Ensure that the final output is fully integrated, consistent, and ready for use.";
            } else if (consolidate_option === "refactor") {
              queryInput.value = refactoringPrompt;
            } else if (consolidate_option === "critique") {
              queryInput.value =
                "Examine the attached project code files and provide a detailed critique of the code, including suggestions for improvements, potential issues, and best practices. Focus on code quality, readability, and maintainability.";
            } else if (consolidate_option === "synopsis") {
              queryInput.value = synopsisPrompt;
            }

            consolidate_flag = false;
          }
        })
        .catch((error) => {
          console.error("Error fetching token:", error);
        });

      copyPromptBtn.addEventListener("click", async () => {
        const currentQuery = queryInput.value;

        // Fetch the latest file contents from the backend
        let fileContents = "";
        try {
          const response = await fetch("/get_file_contents");
          if (response.ok) {
            const data = await response.json();
            fileContents = data.file_contents || "";
          } else {
            console.warn("Failed to fetch file contents from backend.");
          }
        } catch (err) {
          console.error("Error fetching file contents from backend:", err);
        }

        const fullPrompt = fileContents
          ? currentQuery + " \n  \n " + fileContents
          : currentQuery;

        if (fullPrompt.trim() === "") {
          alert("Nothing to copy (input and file contents are empty).");
          return;
        }

        navigator.clipboard
          .writeText(fullPrompt)
          .then(() => {
            const originalText = copyPromptBtn.innerText;
            copyPromptBtn.innerText = "Copied!";
            copyPromptBtn.disabled = true; // Briefly disable
            console.log("Prompt copied to clipboard.");
            setTimeout(() => {
              copyPromptBtn.innerText = originalText;
              copyPromptBtn.disabled = false;
            }, 2000); // Reset after 2 seconds
          })
          .catch((err) => {
            console.error("Failed to copy prompt: ", err);
            alert(
              "Failed to copy prompt to clipboard. See console for details."
            );
          });
      });

      clear_scr.addEventListener("click", async () => {
        queryInput.value = "";
        autoResize();
        preview.innerHTML = "";
        markdownInput.value = "";
      });

      choose_model.addEventListener("click", async () => {
        let selectedModel;
        selectedModel = dropdown_menu.value;
        model_name = selectedModel;
        try {
          const response = await fetch("/select_model", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              uniqueId: uniqueId,
              selectedModel: selectedModel,
            }),
          });

          if (response.ok) {
            streaming_flag = !["o1-pro"].includes(model_name);
            markdownInput.value += `\n\n Unique Session ID: ${uniqueId} \n`;
            markdownInput.value += `\n Model: ${model_name} \n`;
            markdownInput.value += `\n Streaming: ${streaming_flag} \n`;
            renderMarkdown(true);
            autoResize();
          } else {
            console.error("Failed to choose model");
          }
        } catch (error) {
          console.error("Error choosing model:", error);
        }
      });

      // Auto-resize Function
      function autoResize() {
        queryInput.style.height = "auto"; // Reset height
        const scrollHeight = queryInput.scrollHeight;
        const maxHeight = 350;
        if (scrollHeight < maxHeight) {
          queryInput.style.height = scrollHeight + "px";
        } else {
          queryInput.style.height = maxHeight + "px";
        }
      }

      // Initial Resize
      autoResize();

      // Event Listener for Input
      queryInput.addEventListener("input", autoResize);

      SaveBtn.addEventListener("click", async () => {
        queryInput.value = "";
        autoResize();

        try {
          const response = await fetch("/choose_save_path");
          const data = await response.json();

          if (response.ok && data.path) {
            await saveConversation(data.path); // Pass the full path
          } else if (data.error) {
            // Handle cancellation or error from the dialog endpoint
            console.log("Save cancelled or failed:", data.error);
          } else {
            console.log("Save cancelled by user.");
          }
        } catch (error) {
          console.error("Error getting save path:", error);
          alert("An error occurred while trying to open the save dialog.");
        }
      });

      async function saveConversation(fullPath) {
        try {
          // Collect the markdown content from the editor
          const markdownContent = markdownInput.value;

          // Send POST request to the backend /save endpoint
          const response = await fetch("/save", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              uniqueId: uniqueId,
              full_path: fullPath,
              content: markdownContent,
            }),
          });

          const result = await response.json();

          if (response.ok) {
            alert(`Conversation saved successfully to ${fullPath}!`);
          } else {
            alert(
              `Failed to save conversation: ${result.error || "Unknown error"}`
            );
          }
        } catch (error) {
          console.error("Error saving conversation:", error);
          alert("An error occurred while saving the conversation.");
        }
      }

      closeBtn.addEventListener("click", async () => {
        queryInput.value = "";
        autoResize();
        currentFileContents = "";
        preview.innerHTML = "";
        markdownInput.value = "";

        fetch("/shutdown", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            timestamp: new Date().toISOString(),
          }),
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.message) {
              alert(data.message);
            } else if (data.error) {
              alert(`Error: ${data.error}`);
            }
          })
          .catch((error) => {
            console.error("Error:", error);
          });
      });

      let renderTimeout;

      function renderMarkdown(renderMath = false) {
        clearTimeout(renderTimeout);

        let markdownText = markdownInput.value;

        marked.setOptions({
          breaks: true,
          highlight: function (code, lang) {
            if (lang && hljs.getLanguage(lang)) {
              return hljs.highlight(code, { language: lang }).value;
            } else {
              return hljs.highlightAuto(code).value;
            }
          },
        });
        let html = marked.parse(markdownText);
        preview.innerHTML = html;
        addCopyButtons();

        if (renderMath) {
          renderTimeout = setTimeout(() => {
            renderMathJax();
          }, 500); // 500ms delay
        }
      }

      function addCopyButtons() {
        const codeBlocks = preview.querySelectorAll("pre");
        codeBlocks.forEach((pre) => {
          if (!pre.querySelector("button.copy-btn")) {
            const button = document.createElement("button");
            button.className = "copy-btn";
            button.innerText = "Copy";
            button.onclick = () => {
              const code = pre.querySelector("code").innerText;
              navigator.clipboard
                .writeText(code)
                .then(() => {
                  button.innerText = "Copied!";
                  setTimeout(() => {
                    button.innerText = "Copy";
                  }, 2000);
                })
                .catch((err) => {
                  console.error("Failed to copy: ", err);
                });
            };
            pre.appendChild(button);
          }
        });
      }

      function renderMathJax() {
        if (window.MathJax) {
          MathJax.typesetPromise([preview]).catch(function (err) {
            console.error("MathJax typeset failed: " + err.message);
          });
        }
      }

      function appendConversationTurn(userQuery) {
        markdownInput.value += `\n\n**Model:** ${model_name} \n\n**Assistant:** \n\n`;
        renderMarkdown(true);
      }

      submitBtn.addEventListener("click", async () => {
        const query = queryInput.value.trim();
        if (!query) return;

        queryInput.value = "";
        autoResize();
        submitBtn.disabled = true;
        appendConversationTurn(query);
        currentFileContents = "";

        let isMathRendered = false;

        const url = `/stream?prompt=${encodeURIComponent(
          query
        )}&uniqueId=${encodeURIComponent(
          uniqueId
        )}&modelname=${encodeURIComponent(model_name)}`;

        if (streaming_flag) {
          try {
            const response = await fetch(url);
            if (!response.ok) {
              throw new Error(`Network error: ${response.statusText}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = "";
            let done = false;

            while (!done) {
              const { value, done: doneReading } = await reader.read();
              done = doneReading;
              // Accumulate the stream text
              buffer += decoder.decode(value, { stream: true });

              // Split into lines (each line should be a complete JSON string)
              let lines = buffer.split("\n");
              // Keep any incomplete line in the buffer
              buffer = lines.pop();

              for (const line of lines) {
                if (line.trim()) {
                  try {
                    // Parse the JSON object from the line
                    const parsed = JSON.parse(line);
                    let escapedContent;
                    if (parsed.content) {
                      if (math_render_flag) {
                        // Escape backslashes: replace "\" with "\\"
                        escapedContent = parsed.content.replace(/\\/g, "\\\\");
                      } else {
                        escapedContent = parsed.content;
                      }
                      // Append only the escaped content to the Editor
                      markdownInput.value += escapedContent;
                    }
                  } catch (err) {
                    console.error("Error parsing JSON:", err);
                  }
                }
              }
              // Scroll the Editor to the bottom for the latest content
              markdownInput.scrollTop = markdownInput.scrollHeight;
            }

            // Once the stream is complete, update the Preview pane.
            if (!isMathRendered) {
              // Render the final markdown content to update the preview.
              let sanitized = sanitizeText(markdownInput.value);
              //  markdownInput.value = unescapeHtmlEntitiesInFencedCodeBlocks(sanitized);
              markdownInput.value = sanitized;
              renderMarkdown(true);
              isMathRendered = true;
            }
            submitBtn.disabled = false;
          } catch (error) {
            console.error("Streaming error:", error);
            submitBtn.disabled = false;
            alert(
              "An error occurred while streaming the response. Please try again."
            );
          }
        } else {
          try {
            const response = await fetch(url);
            if (!response.ok) {
              throw new Error(`Network error: ${response.statusText}`);
            }
            const result = await response.json();
            if (result.content) {
              markdownInput.value += result.content;
            } else {
              alert(result.error || "Unexpected error");
            }
            // Scroll the Editor to the bottom for the latest content
            markdownInput.scrollTop = markdownInput.scrollHeight;
            if (!isMathRendered) {
              // Render the final markdown content to update the preview.
              let sanitized = sanitizeText(markdownInput.value);
              //  markdownInput.value = unescapeHtmlEntitiesInFencedCodeBlocks(sanitized);
              markdownInput.value = sanitized;
              renderMarkdown(true);
              isMathRendered = true;
            }
            submitBtn.disabled = false;
          } catch (error) {
            console.error("Non-streaming error:", error);
            submitBtn.disabled = false;
            alert("An error occurred. Please try again.");
          }
        }
      });

      resetBtn.addEventListener("click", async () => {
        try {
          const response = await fetch("/reset", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              uniqueId: uniqueId,
            }),
          });

          if (response.ok) {
            currentFileContents = "";
            markdownInput.value = "";
            preview.innerHTML = "";
            queryInput.value = "";
            markdownInput.value += `\n Unique Session ID: ${uniqueId} \n`;
            markdownInput.value += `\n Model: ${model_name} \n`;
            renderMarkdown();
            autoResize();
          } else {
            console.error("Failed to reset conversation");
          }
        } catch (error) {
          console.error("Error resetting conversation:", error);
        }
      });

      queryInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          if (e.ctrlKey) {
            // Ctrl + Enter: Submit the message
            e.preventDefault(); // Prevent newline insertion
            if (submitBtn && !submitBtn.disabled) {
              submitBtn.click(); // Trigger send button if it's enabled
            }
          }
          // Else: Allow newline insertion
        }
      });

      // ———— file‐browser logic (adapted from index2.html) ————

      let selectedFolder = null;

      // recursively build tree
      function createTree(node, container) {
        if (Array.isArray(node)) {
          node.forEach((n) => createTree(n, container));
          return;
        }
        const wrapper = document.createElement("div");
        wrapper.className = "node";

        if (node.type === "directory") {
          // collapse/expand
          const toggle = document.createElement("span");
          toggle.className = "toggle-triangle";
          toggle.textContent = "▼";
          wrapper.appendChild(toggle);

          const label = document.createElement("span");
          label.className = "directory-entry";
          label.textContent = node.name;
          wrapper.appendChild(label);

          container.appendChild(wrapper);

          if (node.children && node.children.length) {
            const childContainer = document.createElement("div");
            wrapper.appendChild(childContainer);
            createTree(node.children, childContainer);

            toggle.onclick = () => {
              if (childContainer.style.display === "none") {
                childContainer.style.display = "";
                toggle.textContent = "▼";
              } else {
                childContainer.style.display = "none";
                toggle.textContent = "▶";
              }
            };
          } else {
            toggle.style.visibility = "hidden";
          }
        } else if (node.type === "file") {
          const link = document.createElement("a");
          link.href = "#";
          link.className = "file-link";
          link.textContent = node.name;

          link.onclick = (e) => {
            e.preventDefault();
            if (!selectedFolder) {
              alert("Open a folder first.");
              return;
            }
            // relative path keeps the URL short & avoids leaking absolute paths
            const relPath = node.path.substring(selectedFolder.length + 1);
            window.open(
              `/load_chat?rel=${encodeURIComponent(relPath)}`,
              "_blank"
            );
          };

          wrapper.appendChild(link);
          container.appendChild(wrapper);
        }
      }

      function loadDirectoryTree(tree) {
        const div = document.getElementById("directory-tree");
        div.innerHTML = "";
        createTree(tree, div);
      }

      // “Open Directory” exactly as index2.html does:
      document.getElementById("open-folder").onclick = async () => {
        try {
          const resp = await fetch("/open_folder_chat", { method: "POST" });
          const data = await resp.json();
          if (data.error) {
            alert(data.error);
          } else {
            selectedFolder = data.folder;
            loadDirectoryTree(data.structure);
          }
        } catch (err) {
          console.error(err);
          alert("Failed to open folder");
        }
      };

      // “Refresh” exactly as index2.html does:
      document.getElementById("refresh").onclick = async () => {
        if (!selectedFolder) {
          alert("No folder selected");
          return;
        }
        try {
          const resp = await fetch("/refresh_chat");
          const data = await resp.json();
          if (data.error) {
            alert(data.error);
          } else {
            loadDirectoryTree(data.structure);
          }
        } catch (err) {
          console.error(err);
          alert("Failed to refresh");
        }
      };
    </script>
  </body>
</html>


---

FILE: app.py

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

# Global variable to store markdown content
loaded_markdown_content: str = ""

# Global variable to store the selected folder path for chat
selected_folder_chat = None 

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
#— enable debug + auto‑reload of code & templates —
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
#— disable caching of static files so changed JS/CSS/html always reloads —
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

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


def get_markdown_for_conversation(path):
    """
    Given a .json or .md path, return the corresponding .md file's contents (if exists).
    """
    stem, ext = os.path.splitext(path)
    if ext.lower() == ".json" and stem.endswith("messages"):
        md_path = stem[:-len("messages")] + ".md"
    elif ext.lower() in (".md", ".txt"):
        md_path = stem + ".md"
    else:
        return None, None
    if os.path.isfile(md_path):
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                return md_path, f.read()
        except Exception as e:
            return md_path, f"Error reading markdown file: {e}"
    return md_path, ""


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
    global loaded_markdown_content
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
    markdown_to_send = loaded_markdown_content or ""
    loaded_markdown_content = ""   
    return jsonify({'token': token, 
                    'model_name': model_name,
                    'consolidate_conversation_flag': c,  
                    'consolidate_option': selected_option_consolidate,
                    'markdown_content': markdown_to_send,
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
    global loaded_markdown_content

    # 1) Ask the user to pick any file
    selected = choose_file()
    if not selected:
        return jsonify({'error': 'No file selected.'}), 400

    _, loaded_markdown_content = get_markdown_for_conversation(selected)
    # 2) Compute your “conversation key” exactly as the tree‑view does
    base = os.path.basename(selected)   # e.g. "123.md" or "foo.messages.json"
    stem, ext = os.path.splitext(base)  # ("123", ".md") or ("foo.messages", ".json")
    if ext.lower() == '.json' and stem.lower().endswith('messages'):
        conv = stem[:-len('messages')]  # strip off trailing "messages"
    else:
        conv = stem                     # otherwise just the name before the last “.”
    conv = conv.rstrip('.')             # guard against an accidental trailing dot

    # 3) Build the full path in the same folder the file lived in
    folder = os.path.dirname(selected)  # e.g. "/home/bin"
    target = os.path.join(folder, f'{conv}messages.json')
    
    # 4) Load it
    try:
        with open(target, 'r', encoding='utf-8') as f:
            loaded_conversation_messages = json.load(f)
    except FileNotFoundError:
        return jsonify({'error': f'Conversation not found at {target}'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'Error decoding JSON.'}), 500
    except Exception as e:
        logger.error(f"Error loading {target}: {e}", exc_info=True)
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

# Endpoint to trigger the native "Save As" dialog
@app.route('/choose_save_path', methods=['GET'])
def choose_save_path():
    """
    Opens a native 'Save As' dialog using Tkinter on the server side.
    Returns the chosen file path to the client.
    """
    root = None
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the main Tkinter window
        # Pop up the "Save As" dialog
        file_path = filedialog.asksaveasfilename(
            title="Save Conversation As...",
            defaultextension=".md", # Default extension
            filetypes=[("Markdown files", "*.md"), # File type filter
                       ("Text files", "*.txt"),
                       ("JSON files", "*.json")]
        )
        root.destroy() # Clean up the Tkinter root window

        if file_path:
            # User selected a path
            return jsonify({'path': file_path})
        else:
            # User cancelled the dialog
            return jsonify({'error': 'No path selected'}), 400
    except Exception as e:
        logger.error(f"Error opening save dialog: {e}", exc_info=True)
        if root:
            try:
                root.destroy()
            except: # nosec # Ignore errors during cleanup
                pass
        return jsonify({'error': 'Failed to open save dialog.'}), 500
    

# Save Conversation Endpoint
@app.route('/save', methods=['POST'])
def save_conversation():
    global message_accumulate
    data = request.get_json()
    full_path = data.get('full_path')
    content = data.get('content')
    unique_id = data.get('uniqueId')
    counter = determine_counter(unique_id)

    # Validate the received full path
    if not full_path or not content:
        return jsonify({'error': 'Full path and content are required.'}), 400

    # Determine the directory and base filename from the full path
    try:
        save_directory = os.path.dirname(full_path)
        base_filename = os.path.basename(full_path)
        filename_stem, _ = os.path.splitext(base_filename) # Get name without extension

        # Ensure the target directory exists (optional, but good practice)
        os.makedirs(save_directory, exist_ok=True)

        # Construct the paths using the chosen directory and derived names
        markdown_path = os.path.join(save_directory, f"{filename_stem}.md")
        json_path = os.path.join(save_directory, f"{filename_stem}messages.json")

    except Exception as e:
        logger.error(f"Error processing save path '{full_path}': {e}", exc_info=True)
        return jsonify({'error': f'Invalid save path provided: {e}'}), 400

    
    conversation_messages_only = get_conversation_history(unique_id, counter)

    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(conversation_messages_only, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving conversation: {e}")
        return jsonify({'error': 'Failed to save conversation.'}), 500

    md_lines = []
    # Header with file name
    md_lines.append(f"**FILE:** {markdown_path}\n\n")

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



            elif "o4-mini" in model_name or "o3" in model_name: 

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


            elif ("o3-mini" in model_name):
                
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



def choose_file():
    """Pop up a standard file‑open dialog and return the chosen path (or '' if cancelled)."""
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="Select a conversation base file",
        filetypes=[("All files","*.*")]
    )
    root.destroy()
    return path


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
    global loaded_markdown_content
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




# -----------------------------------
# Dedicated state for index.html
# -----------------------------------


@app.route('/open_folder_chat', methods=['POST'])          # <‑‑ NEW ❷
def open_folder_chat():
    """
    Folder picker used ONLY by templates/index.html
    """
    global selected_folder_chat, global_file_contents
    global_file_contents = ""
    folder = choose_folder()
    if folder:
        selected_folder_chat = folder
        return jsonify({
            "folder": folder,
            "structure": get_directory_structure(folder)
        })
    return jsonify({"error": "No folder selected"}), 400


@app.route('/refresh_chat', methods=['GET'])               # <‑‑ NEW ❸
def refresh_chat():
    """
    Refresh directory tree shown in templates/index.html
    """
    global selected_folder_chat, global_file_contents
    global_file_contents = ""
    if selected_folder_chat:
        return jsonify({
            "folder": selected_folder_chat,
            "structure": get_directory_structure(selected_folder_chat)
        })
    return jsonify({"error": "No folder selected"}), 400

@app.route('/load_chat', methods=['GET'])
def load_chat():
    """
    Called when the user clicks a file in the left‑hand browser that
    is rendered inside templates/index.html.
    """

    global selected_folder_chat
    global loaded_conversation_messages
    global loading_new_file
    global loaded_markdown_content

    # ---------- 1. figure out which path the client sent ----------
    rel = request.args.get("rel")        # relative path (recommended)
    abs_path = request.args.get("abs")   # absolute path (fallback)

    if rel:
        if not selected_folder_chat:
            return jsonify({"error": "No folder was opened in this session."}), 400
        path = os.path.abspath(os.path.join(selected_folder_chat, rel))
    elif abs_path:
        path = os.path.abspath(abs_path)
    else:
        return jsonify({"error": "Missing file path."}), 400

    _, loaded_markdown_content = get_markdown_for_conversation(path)

    # (optional) sanity‑check that the path is inside the chosen folder
    if selected_folder_chat and not path.startswith(os.path.abspath(selected_folder_chat)):
        return jsonify({"error": "Path outside selected folder."}), 400

    # ---------- 2. decide which JSON to open ----------
    stem, ext = os.path.splitext(path)
    if ext.lower() == ".md":
        conv_path = f"{stem}messages.json"
    elif ext.lower() == ".txt":
        conv_path = f"{stem}messages.json"
    elif ext.lower() == ".json":
        conv_path = path
    else:
        return jsonify({"error": "Click a .md or .json file to load a conversation."}), 400

    if not os.path.isfile(conv_path):
        return jsonify({"error": f"Conversation file not found: {conv_path}"}), 404

    # ---------- 3. load it ----------
    try:
        with open(conv_path, "r", encoding="utf-8") as fh:
            loaded_conversation_messages = json.load(fh)
    except Exception as exc:  # noqa: BLE001  (keep traceback in log)
        logger.error("Failed to load %s: %s", conv_path, exc, exc_info=True)
        return jsonify({"error": "Failed to read conversation file."}), 500

    loading_new_file = True
    return render_template("index.html")



def find_free(base=5000):
    for p in range(base, 65536):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)):
                return p

if __name__ == "__main__":
    # decide the port only once, pass via env var
    port = int(os.environ.get("DEV_PORT", find_free()))
    os.environ["DEV_PORT"] = str(port)

    print(f"Serving on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1",
            port=port,
            debug=True,
            use_reloader=True)      




---

---
---

**Dictionary Item 03**

**Role:** assistant

**Content:**

Below are three practical ways to get rid of the “&lt;pre&gt; … &lt;/pre&gt;” problem without giving up the rest of your tag–escaping logic.  
Pick the one that best matches your threat‑model and the amount of code you want to touch.

────────────────────────────────────────
1.  Stop using real HTML and switch to Markdown fences (easiest / safest)
────────────────────────────────────────
You only wrap the loaded file in a `<pre>` block so that **its whole
content is shown literally** in the preview.  
Markdown already has the perfect construct for that – a fenced code
block.

Replace the line in the *get‑token* callback …

```javascript
markdownInput.value = "<pre>\n" + sanitizedMarkdown + "\n</pre>";
```

with

```javascript
// pick a fence length that is longer than any run of back‑ticks
const fence = "````";          // 4 ticks because your sanitizer already
                               // understands both 3 and 4 ticks
markdownInput.value =
  fence + "markdown\n" +
  sanitizedMarkdown +
  "\n" + fence;
```

Because

* `sanitizeText()` already skips everything that sits between
  three‑or‑four back‑ticks,  
* and `marked` converts the fence to a proper `<pre><code>` block,

the `<pre>` tag never appears in the source, so nothing gets escaped.

────────────────────────────────────────
2.  Allowlist the <pre> tag inside sanitizeText (one‑liner change)
────────────────────────────────────────
If you really want literal `<pre>` tags to survive, teach the sanitiser
to leave them alone.

Add an allow‑list just before you transform a found tag:

```javascript
// inside sanitizeInline …
inlineParts[i] = inlineParts[i].replace(
  /<\s*(\/?)\s*([a-zA-Z][\w-]*)([^>]*)>/g,
  function (match, slash, tagName, rest) {

    // ①  ———  allow “pre” and “/pre” unconditionally  ———
    const tag = (slash ? "/" : "") + tagName.toLowerCase();
    if (tag === "pre" || tag === "/pre") {
      return match;               // keep the tag exactly as it is
    }

    // ②  ———  normal escaping for everything else  ———
    …
});
```

Nothing else in the algorithm changes – you are just short‑circuiting
the replacement when the tag is `<pre>` or `</pre>`.

────────────────────────────────────────
3.  Preserve the whole <pre>…</pre> block with a placeholder (robust)
────────────────────────────────────────
If you later decide to protect more HTML fragments
(e.g. `<table>`, `<video>` …) you can wrap them with placeholders before
sanitising and restore them afterwards:

```javascript
function sanitizeText(text) {

  // A. protect every <pre …> … </pre> first
  const PRE_RE   = /<pre\b[^>]*>[\s\S]*?<\/pre>/gi;
  const store    = [];
  text = text.replace(PRE_RE, m => {
      const key = `___PRESERVE_PRE_${store.length}___`;
      store.push(m);
      return key;                  // leave a stub in the text
  });

  // B. run your existing algorithm (unchanged) on the stubbed text
  text = coreSanitize(text);       // <‑‑ move your old code into here

  // C. put the untouched <pre …> blocks back
  store.forEach((block, i) => {
      text = text.replace(`___PRESERVE_PRE_${i}___`, block);
  });

  return text;
}
```

This pattern lets you keep your escape‑all‑HTML default while still
whitelisting whole fragments whenever you need to.

────────────────────────────────────────
What the author of this project normally does
────────────────────────────────────────
In production code we almost always pick option 1 (Markdown code fences)
and run a real HTML sanitizer such as **DOMPurify** or **sanitize‑html**
as a final guard before injecting anything into the DOM.  
That keeps XSS risk low and the code base small.

But if you are happy with your current regex‑based approach, option 2 is
literally a two‑line edit and solves the immediate problem.

Choose whichever solution fits best – they are all compatible with the
rest of your stack.

---
