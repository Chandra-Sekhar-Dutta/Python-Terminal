# web_interface.py - Flask Web Interface
from flask import Flask, render_template, request, jsonify, session
import os
import uuid
from terminal import PythonTerminal

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Store terminal instances per session
terminals = {}

def get_terminal(session_id):
    """Get or create terminal instance for session"""
    if session_id not in terminals:
        terminals[session_id] = PythonTerminal()
    return terminals[session_id]

@app.route('/')
def index():
    """Main web terminal page"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    return render_template('terminal.html')

@app.route('/execute', methods=['POST'])
def execute_command():
    """Execute command via AJAX"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({'output': '', 'returnCode': 0})
        
        # Get terminal instance for this session
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'No session found'}), 400
        
        terminal = get_terminal(session_id)
        
        # Execute command
        output, return_code = terminal.execute_command(command)
        
        # Handle exit command
        if output == "EXIT_TERMINAL":
            # Clean up terminal instance
            if session_id in terminals:
                del terminals[session_id]
            return jsonify({'output': 'Terminal session ended.', 'returnCode': 0, 'exit': True})
        
        return jsonify({
            'output': output,
            'returnCode': return_code,
            'prompt': terminal.get_prompt()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    """Provide command and file autocompletion"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        line = data.get('line', '')
        
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'suggestions': []})
        
        terminal = get_terminal(session_id)
        
        suggestions = []
        parts = line.split()
        
        # Command completion (first word)
        if not parts or (len(parts) == 1 and not line.endswith(' ')):
            commands = list(terminal.builtin_commands.keys())
            commands.extend(['python', 'git', 'npm', 'pip', 'node', 'java', 'gcc'])
            
            for cmd in commands:
                if cmd.startswith(text):
                    suggestions.append(cmd)
        
        else:
            # File/directory completion
            try:
                if text.startswith('/'):
                    directory = os.path.dirname(text) or '/'
                    prefix = os.path.basename(text)
                elif text.startswith('~'):
                    expanded = os.path.expanduser(text)
                    directory = os.path.dirname(expanded) or os.path.expanduser('~')
                    prefix = os.path.basename(expanded)
                else:
                    directory = terminal.current_directory
                    if '/' in text:
                        directory = os.path.join(directory, os.path.dirname(text))
                        prefix = os.path.basename(text)
                    else:
                        prefix = text
                
                if os.path.isdir(directory):
                    for item in os.listdir(directory):
                        if item.startswith(prefix):
                            full_path = os.path.join(directory, item)
                            if os.path.isdir(full_path):
                                suggestions.append(item + '/')
                            else:
                                suggestions.append(item)
            
            except (OSError, PermissionError):
                pass
        
        return jsonify({'suggestions': suggestions[:10]})  # Limit to 10 suggestions
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Get command history"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'history': []})
        
        terminal = get_terminal(session_id)
        return jsonify({'history': terminal.command_history[-50:]})  # Last 50 commands
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Template for the web interface
TERMINAL_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Terminal</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background-color: #1e1e1e;
            color: #ffffff;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.4;
        }
        
        .terminal-container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: #2d2d30;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .terminal-header {
            background-color: #3c3c3c;
            padding: 10px 20px;
            border-bottom: 1px solid #555;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .terminal-button {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        
        .close { background-color: #ff5f56; }
        .minimize { background-color: #ffbd2e; }
        .maximize { background-color: #27ca3f; }
        
        .terminal-title {
            margin-left: 10px;
            font-weight: bold;
        }
        
        .terminal-output {
            height: 500px;
            overflow-y: auto;
            padding: 20px;
            background-color: #1e1e1e;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .terminal-input-container {
            display: flex;
            align-items: center;
            padding: 10px 20px;
            background-color: #2d2d30;
            border-top: 1px solid #555;
        }
        
        .prompt {
            color: #4CAF50;
            margin-right: 8px;
            white-space: nowrap;
        }
        
        .terminal-input {
            flex: 1;
            background: transparent;
            border: none;
            color: #ffffff;
            font-family: inherit;
            font-size: inherit;
            outline: none;
            padding: 0;
        }
        
        .autocomplete-suggestions {
            position: absolute;
            bottom: 100%;
            left: 0;
            right: 0;
            background-color: #3c3c3c;
            border: 1px solid #555;
            border-radius: 4px;
            max-height: 200px;
            overflow-y: auto;
            z-index: 1000;
        }
        
        .suggestion-item {
            padding: 8px 12px;
            cursor: pointer;
            border-bottom: 1px solid #555;
        }
        
        .suggestion-item:hover,
        .suggestion-item.selected {
            background-color: #4CAF50;
        }
        
        .suggestion-item:last-child {
            border-bottom: none;
        }
        
        .loading {
            color: #888;
        }
        
        .error {
            color: #ff6b6b;
        }
        
        .success {
            color: #4CAF50;
        }
        
        .info {
            color: #74b9ff;
        }
    </style>
</head>
<body>
    <div class="terminal-container">
        <div class="terminal-header">
            <div class="terminal-button close"></div>
            <div class="terminal-button minimize"></div>
            <div class="terminal-button maximize"></div>
            <div class="terminal-title">Python Terminal</div>
        </div>
        
        <div class="terminal-output" id="output">
            <div class="info">Python Terminal - Type 'help' for available commands</div>
            <div class="info">Use Ctrl+C to interrupt, 'exit' or 'quit' to exit</div>
            <div></div>
        </div>
        
        <div class="terminal-input-container" style="position: relative;">
            <div class="autocomplete-suggestions" id="autocomplete" style="display: none;"></div>
            <span class="prompt" id="prompt">user@localhost:~$ </span>
            <input type="text" class="terminal-input" id="input" autocomplete="off" spellcheck="false">
        </div>
    </div>

    <script>
        const output = document.getElementById('output');
        const input = document.getElementById('input');
        const prompt = document.getElementById('prompt');
        const autocomplete = document.getElementById('autocomplete');
        
        let commandHistory = [];
        let historyIndex = -1;
        let currentSuggestions = [];
        let selectedSuggestion = -1;
        
        // Focus input
        input.focus();
        
        // Load command history
        loadHistory();
        
        // Handle input events
        input.addEventListener('keydown', handleKeyDown);
        input.addEventListener('input', handleInput);
        
        // Auto-scroll output
        function scrollToBottom() {
            output.scrollTop = output.scrollHeight;
        }
        
        // Add content to output
        function addToOutput(content, className = '') {
            const div = document.createElement('div');
            if (className) div.className = className;
            div.textContent = content;
            output.appendChild(div);
            scrollToBottom();
        }
        
        // Execute command
        async function executeCommand(command) {
            if (!command.trim()) return;
            
            // Add command to output
            addToOutput(`${prompt.textContent}${command}`);
            
            // Show loading
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'loading';
            loadingDiv.textContent = 'Executing...';
            output.appendChild(loadingDiv);
            scrollToBottom();
            
            try {
                const response = await fetch('/execute', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ command })
                });
                
                const data = await response.json();
                
                // Remove loading
                output.removeChild(loadingDiv);
                
                if (data.error) {
                    addToOutput(`Error: ${data.error}`, 'error');
                } else {
                    if (data.output) {
                        // Handle special clear command
                        if (data.output.includes('\033[2J\033[H')) {
                            output.innerHTML = '';
                        } else {
                            addToOutput(data.output);
                        }
                    }
                    
                    // Update prompt
                    if (data.prompt) {
                        prompt.textContent = data.prompt;
                    }
                    
                    // Handle exit
                    if (data.exit) {
                        addToOutput('Terminal session ended.', 'info');
                        input.disabled = true;
                        return;
                    }
                }
            } catch (error) {
                output.removeChild(loadingDiv);
                addToOutput(`Network error: ${error.message}`, 'error');
            }
            
            // Add command to history
            if (command.trim()) {
                commandHistory.push(command);
                historyIndex = commandHistory.length;
            }
        }
        
        // Load command history
        async function loadHistory() {
            try {
                const response = await fetch('/history');
                const data = await response.json();
                if (data.history) {
                    commandHistory = data.history;
                    historyIndex = commandHistory.length;
                }
            } catch (error) {
                console.error('Failed to load history:', error);
            }
        }
        
        // Handle key events
        async function handleKeyDown(event) {
            switch (event.key) {
                case 'Enter':
                    event.preventDefault();
                    if (selectedSuggestion >= 0) {
                        // Accept selected suggestion
                        input.value = currentSuggestions[selectedSuggestion];
                        hideSuggestions();
                    } else {
                        const command = input.value;
                        input.value = '';
                        hideSuggestions();
                        await executeCommand(command);
                    }
                    break;
                
                case 'ArrowUp':
                    event.preventDefault();
                    if (autocomplete.style.display === 'block') {
                        // Navigate suggestions
                        selectedSuggestion = Math.max(-1, selectedSuggestion - 1);
                        updateSuggestionSelection();
                    } else {
                        // Command history
                        if (historyIndex > 0) {
                            historyIndex--;
                            input.value = commandHistory[historyIndex];
                        }
                    }
                    break;
                
                case 'ArrowDown':
                    event.preventDefault();
                    if (autocomplete.style.display === 'block') {
                        // Navigate suggestions
                        selectedSuggestion = Math.min(currentSuggestions.length - 1, selectedSuggestion + 1);
                        updateSuggestionSelection();
                    } else {
                        // Command history
                        if (historyIndex < commandHistory.length - 1) {
                            historyIndex++;
                            input.value = commandHistory[historyIndex];
                        } else if (historyIndex === commandHistory.length - 1) {
                            historyIndex = commandHistory.length;
                            input.value = '';
                        }
                    }
                    break;
                
                case 'Tab':
                    event.preventDefault();
                    if (currentSuggestions.length === 1) {
                        input.value = currentSuggestions[0];
                        hideSuggestions();
                    } else if (selectedSuggestion >= 0) {
                        input.value = currentSuggestions[selectedSuggestion];
                        hideSuggestions();
                    }
                    break;
                
                case 'Escape':
                    hideSuggestions();
                    break;
                
                case 'c':
                    if (event.ctrlKey) {
                        event.preventDefault();
                        addToOutput(`${prompt.textContent}${input.value}^C`);
                        input.value = '';
                        hideSuggestions();
                    }
                    break;
            }
        }
        
        // Handle input changes for autocompletion
        async function handleInput(event) {
            const value = input.value;
            const cursorPos = input.selectionStart;
            
            if (value.length > 0) {
                await showSuggestions(value);
            } else {
                hideSuggestions();
            }
        }
        
        // Show autocompletion suggestions
        async function showSuggestions(text) {
            try {
                const response = await fetch('/autocomplete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        text: getLastWord(text),
                        line: text
                    })
                });
                
                const data = await response.json();
                
                if (data.suggestions && data.suggestions.length > 0) {
                    currentSuggestions = data.suggestions;
                    selectedSuggestion = -1;
                    
                    autocomplete.innerHTML = '';
                    data.suggestions.forEach((suggestion, index) => {
                        const div = document.createElement('div');
                        div.className = 'suggestion-item';
                        div.textContent = suggestion;
                        div.addEventListener('click', () => {
                            input.value = replaceLastWord(input.value, suggestion);
                            input.focus();
                            hideSuggestions();
                        });
                        autocomplete.appendChild(div);
                    });
                    
                    autocomplete.style.display = 'block';
                } else {
                    hideSuggestions();
                }
            } catch (error) {
                hideSuggestions();
            }
        }
        
        // Hide suggestions
        function hideSuggestions() {
            autocomplete.style.display = 'none';
            currentSuggestions = [];
            selectedSuggestion = -1;
        }
        
        // Update suggestion selection
        function updateSuggestionSelection() {
            const items = autocomplete.querySelectorAll('.suggestion-item');
            items.forEach((item, index) => {
                if (index === selectedSuggestion) {
                    item.classList.add('selected');
                } else {
                    item.classList.remove('selected');
                }
            });
        }
        
        // Get last word for completion
        function getLastWord(text) {
            const parts = text.split(' ');
            return parts[parts.length - 1];
        }
        
        // Replace last word with completion
        function replaceLastWord(text, replacement) {
            const parts = text.split(' ');
            parts[parts.length - 1] = replacement;
            return parts.join(' ');
        }
        
        // Click outside to hide suggestions
        document.addEventListener('click', (event) => {
            if (!event.target.closest('.terminal-input-container')) {
                hideSuggestions();
            }
        });
        
        // Keep input focused
        document.addEventListener('click', (event) => {
            if (event.target.closest('.terminal-container')) {
                input.focus();
            }
        });
    </script>
</body>
</html>
'''

# Create templates directory and template file
def setup_templates():
    """Create Flask templates"""
    os.makedirs('templates', exist_ok=True)
    with open('templates/terminal.html', 'w') as f:
        f.write(TERMINAL_HTML)

def run_web_server(host='127.0.0.1', port=5000, debug=True):
    """Run the Flask web server"""
    setup_templates()
    print(f"Starting Python Terminal Web Interface...")
    print(f"Open your browser and go to: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    run_web_server()