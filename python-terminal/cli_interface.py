# cli_interface.py - Command Line Interface
import readline
import sys
import os
from terminal import PythonTerminal

class CLIInterface:
    """Command Line Interface for the Python Terminal"""
    
    def __init__(self):
        self.terminal = PythonTerminal()
        self.setup_readline()
        
    def setup_readline(self):
        """Setup readline for command history and auto-completion"""
        try:
            # Enable tab completion
            readline.set_completer(self.completer)
            readline.parse_and_bind("tab: complete")
            
            # Load command history
            try:
                readline.read_history_file(".terminal_history")
            except FileNotFoundError:
                pass
            
            # Set history length
            readline.set_history_length(1000)
            
        except ImportError:
            print("Warning: readline not available, no tab completion or history")
    
    def completer(self, text, state):
        """Auto-completion function for commands and files"""
        if state == 0:
            # First call, generate completions
            line = readline.get_line_buffer()
            parts = line.split()
            
            self.completions = []
            
            # Command completion (first word)
            if not parts or (len(parts) == 1 and not line.endswith(' ')):
                # Complete command names
                commands = list(self.terminal.builtin_commands.keys())
                commands.extend(['python', 'git', 'npm', 'pip', 'node', 'java', 'gcc'])
                
                for cmd in commands:
                    if cmd.startswith(text):
                        self.completions.append(cmd)
            
            else:
                # File/directory completion
                try:
                    if text.startswith('/'):
                        # Absolute path
                        directory = os.path.dirname(text) or '/'
                        prefix = os.path.basename(text)
                    elif text.startswith('~'):
                        # Home directory
                        expanded = os.path.expanduser(text)
                        directory = os.path.dirname(expanded) or os.path.expanduser('~')
                        prefix = os.path.basename(expanded)
                    else:
                        # Relative path
                        directory = self.terminal.current_directory
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
                                    self.completions.append(item + '/')
                                else:
                                    self.completions.append(item)
                
                except (OSError, PermissionError):
                    pass
        
        # Return the completion for this state
        try:
            return self.completions[state]
        except IndexError:
            return None
    
    def run(self):
        """Main CLI loop"""
        print("Python Terminal - Type 'help' for available commands")
        print("Use Ctrl+C to interrupt, 'exit' or 'quit' to exit")
        print()
        
        try:
            while True:
                try:
                    # Get command from user
                    prompt = self.terminal.get_prompt()
                    command = input(prompt).strip()
                    
                    if not command:
                        continue
                    
                    # Execute command
                    output, return_code = self.terminal.execute_command(command)
                    
                    # Handle special exit case
                    if output == "EXIT_TERMINAL":
                        break
                    
                    # Print output
                    if output:
                        print(output)
                    
                    # Save command to history
                    try:
                        readline.write_history_file(".terminal_history")
                    except:
                        pass
                
                except KeyboardInterrupt:
                    print("\n^C")
                    continue
                except EOFError:
                    print("\nGoodbye!")
                    break
        
        finally:
            # Save history on exit
            try:
                readline.write_history_file(".terminal_history")
            except:
                pass

def main():
    """Entry point for CLI interface"""
    cli = CLIInterface()
    cli.run()

if __name__ == "__main__":
    main()