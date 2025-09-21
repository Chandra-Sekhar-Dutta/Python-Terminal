# Python-Based Command Terminal

A fully functioning command terminal built in Python that mimics the behavior of a real system terminal. This terminal supports standard file operations, directory navigation, system monitoring, and includes an AI-powered natural language interface.

## Features

### Core Features
- **Complete Terminal Functionality**: Supports all standard terminal commands (ls, cd, pwd, mkdir, rm, etc.)
- **System Monitoring**: Built-in system monitoring tools (CPU, memory, disk usage, process management)
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Command History**: Full command history with navigation
- **Auto-completion**: Tab completion for commands and file paths
- **Error Handling**: Comprehensive error handling for invalid commands

### Interface Options
1. **CLI Interface**: Traditional command-line interface with readline support
2. **Web Interface**: Modern web-based terminal with real-time interaction
3. **AI Interface**: Natural language command interpretation

### AI-Powered Features
- **Natural Language Processing**: Convert plain English to terminal commands
- **Complex Command Interpretation**: Handle multi-step operations
- **Smart Suggestions**: Context-aware command suggestions
- **Learning Capabilities**: Pattern-based command recognition

## Project Structure

```
python-terminal/
├── terminal.py              # Core terminal engine
├── cli_interface.py         # Command-line interface
├── web_interface.py         # Flask web interface
├── ai_interface.py          # AI-powered natural language interface
├── main.py                  # Main launcher
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup configuration
├── run_tests.py             # Basic test runner
├── templates/               # Web interface templates
│   └── terminal.html        # Web terminal HTML template
├── README.md                # This file
└── .terminal_history        # Command history (created at runtime)
```

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Quick Install
```bash
# Clone or download the project files
# Install dependencies
pip install Flask psutil

# Run the terminal
python main.py cli
```

## Usage

### Command Line Interface
```bash
python main.py cli
```

Launch the traditional CLI terminal with readline support, command history, and tab completion.

### Web Interface
```bash
python main.py web
```

Launch the web-based terminal interface. Open your browser and go to `http://127.0.0.1:5000`

**Web Interface Options:**
```bash
python main.py web --host 0.0.0.0 --port 8080 --debug
```

### AI-Powered Interface
```bash
python main.py ai
```

Launch the AI-powered terminal that understands natural language commands.

## Supported Commands

### File Operations
| Command | Description | Example |
|---------|-------------|---------|
| `ls`, `dir` | List directory contents | `ls -l` |
| `cd` | Change directory | `cd /home/user` |
| `pwd` | Print working directory | `pwd` |
| `mkdir` | Create directory | `mkdir newfolder` |
| `rmdir` | Remove empty directory | `rmdir emptyfolder` |
| `rm`, `del` | Remove files/directories | `rm file.txt` |
| `touch` | Create empty file | `touch newfile.txt` |
| `cat`, `type` | Display file contents | `cat readme.txt` |
| `cp`, `copy` | Copy files/directories | `cp file1.txt file2.txt` |
| `mv`, `move` | Move/rename files | `mv oldname.txt newname.txt` |
| `find` | Find files and directories | `find . -name "*.txt"` |
| `grep` | Search text in files | `grep "hello" file.txt` |
| `tree` | Display directory tree | `tree` |

### System Monitoring
| Command | Description | Example |
|---------|-------------|---------|
| `ps` | List running processes | `ps` |
| `kill` | Kill process by PID | `kill 1234` |
| `top` | Display system resource usage | `top` |
| `df` | Display filesystem usage | `df` |
| `free` | Display memory usage | `free` |

### Utilities
| Command | Description | Example |
|---------|-------------|---------|
| `echo` | Echo text | `echo "Hello World"` |
| `whoami` | Display current user | `whoami` |
| `date` | Display current date/time | `date` |
| `history` | Show command history | `history` |
| `clear`, `cls` | Clear screen | `clear` |
| `env` | Show environment variables | `env` |
| `alias` | Create command aliases | `alias ll="ls -l"` |
| `help` | Show help information | `help` |
| `exit`, `quit` | Exit terminal | `exit` |

## AI Natural Language Examples

The AI interface can understand and convert natural language to terminal commands:

### File Operations
- "create a file named test.txt" → `touch test.txt`
- "make a new folder called documents" → `mkdir documents`
- "delete the file oldfile.txt" → `rm oldfile.txt`
- "copy file1.txt to backup folder" → `cp file1.txt backup/`
- "move document.pdf to archive" → `mv document.pdf archive/`

### Navigation & Information
- "list all files" → `ls`
- "show me what's in this directory" → `ls -l`
- "go to the documents folder" → `cd documents`
- "where am I" → `pwd`
- "show me system info" → `top`

### Complex Operations
- "create a folder called test and move file1.txt into it" → `mkdir test && mv file1.txt test/`
- "find all .txt files" → `find . -name "*.txt"`
- "copy all .py files to backup" → `cp *.py backup/`

## Web Interface Features

The web interface provides:
- **Real-time Command Execution**: Execute commands with immediate feedback
- **Modern UI**: Clean, terminal-like interface with syntax highlighting
- **Auto-completion**: Tab completion for commands and file paths
- **Command History**: Navigate through command history with arrow keys
- **Session Management**: Maintains separate terminal sessions per browser session
- **Responsive Design**: Works on desktop and mobile devices

## Configuration

### Environment Variables
The terminal respects standard environment variables:
- `HOME` / `USERPROFILE`: User home directory
- `USER` / `USERNAME`: Current username
- `PATH`: Command search path
- `HOSTNAME` / `COMPUTERNAME`: System hostname

### Customization
You can customize the terminal by modifying:
- **Prompt**: Edit `get_prompt()` method in `terminal.py`
- **Commands**: Add new built-in commands to `builtin_commands` dictionary
- **AI Patterns**: Extend natural language patterns in `ai_interface.py`

## Testing

Run basic functionality tests:
```bash
python run_tests.py
```

This will test:
- Core terminal functionality
- Command execution
- Interface imports
- AI interpretation capabilities

## API Reference

### PythonTerminal Class

Main terminal engine class:

```python
from terminal import PythonTerminal

terminal = PythonTerminal()
output, return_code = terminal.execute_command("ls -l")
print(output)
```

### AITerminalInterface Class

AI-powered terminal interface:

```python
from ai_interface import AITerminalInterface

ai_terminal = AITerminalInterface()
command, interpretation = ai_terminal.interpret_command("create a file named test.txt")
output, return_code, interpretation = ai_terminal.execute_natural_language("list all files")
```

## Development

### Adding New Commands
To add a new built-in command:

1. Add the command to `builtin_commands` dictionary in `terminal.py`
2. Implement the command method (e.g., `cmd_newcommand`)
3. Add help text to the `cmd_help` method

### Extending AI Capabilities
To add new natural language patterns:

1. Add patterns to `command_patterns` in `ai_interface.py`
2. Test with various natural language inputs
3. Add complex command handlers to `_handle_complex_commands`

### Web Interface Customization
- Modify `templates/terminal.html` for UI changes
- Extend Flask routes in `web_interface.py` for new functionality
- Add CSS styling in the HTML template

## Security Considerations

- **Command Execution**: The terminal can execute system commands - use with caution
- **File Access**: Respects system permissions but can access any readable file
- **Web Interface**: Runs locally by default - be careful when exposing to network
- **AI Commands**: Natural language commands are converted to system commands

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
pip install -r requirements.txt
```

**Permission Denied:**
- Check file/directory permissions
- Run with appropriate user privileges

**Web Interface Not Loading:**
- Check if port 5000 is available
- Try different port: `python main.py web --port 8080`

**Command Not Found:**
- Ensure the command exists on your system
- Check PATH environment variable
- Use absolute paths for executables

### Debug Mode
Enable debug output:
```bash
python main.py web --debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Changelog

### Version 1.0.0
- Initial release
- Core terminal functionality
- CLI, Web, and AI interfaces
- System monitoring tools
- Natural language processing
- Cross-platform support

## Support

For issues, questions, or contributions:
1. Check the troubleshooting section
2. Run the test suite: `python run_tests.py`
3. Review the code documentation
4. Create an issue with detailed information

---

**Note**: This terminal executes real system commands. Always be cautious when running commands, especially with elevated privileges or on production systems.