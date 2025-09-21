# ai_interface.py - AI-Powered Natural Language Terminal
import re
import json
from typing import List, Dict, Tuple
from terminal import PythonTerminal

class AITerminalInterface:
    """AI-driven terminal that interprets natural language commands"""
    
    def __init__(self):
        self.terminal = PythonTerminal()
        self.command_patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, List[Dict]]:
        """Initialize natural language patterns and their command mappings"""
        return {
            # File operations
            'create_file': [
                {
                    'patterns': [
                        r'create.*?file.*?(?:named|called)\s+(\S+)',
                        r'make.*?file.*?(\S+)',
                        r'touch.*?(\S+)',
                        r'new file.*?(\S+)'
                    ],
                    'command': 'touch {0}'
                }
            ],
            'create_directory': [
                {
                    'patterns': [
                        r'create.*?(?:directory|folder|dir).*?(?:named|called)\s+(\S+)',
                        r'make.*?(?:directory|folder|dir).*?(\S+)',
                        r'mkdir.*?(\S+)',
                        r'new (?:directory|folder).*?(\S+)'
                    ],
                    'command': 'mkdir {0}'
                }
            ],
            'list_files': [
                {
                    'patterns': [
                        r'list.*?files?',
                        r'show.*?files?',
                        r'what.*?files?.*?here',
                        r'ls',
                        r'dir'
                    ],
                    'command': 'ls'
                }
            ],
            'delete_file': [
                {
                    'patterns': [
                        r'delete.*?file.*?(\S+)',
                        r'remove.*?file.*?(\S+)',
                        r'rm.*?(\S+)',
                        r'del.*?(\S+)'
                    ],
                    'command': 'rm {0}'
                }
            ],
            'copy_file': [
                {
                    'patterns': [
                        r'copy.*?(\S+).*?to.*?(\S+)',
                        r'cp.*?(\S+).*?(\S+)',
                        r'duplicate.*?(\S+).*?as.*?(\S+)'
                    ],
                    'command': 'cp {0} {1}'
                }
            ],
            'move_file': [
                {
                    'patterns': [
                        r'move.*?(\S+).*?to.*?(\S+)',
                        r'mv.*?(\S+).*?(\S+)',
                        r'relocate.*?(\S+).*?to.*?(\S+)'
                    ],
                    'command': 'mv {0} {1}'
                }
            ],
            'change_directory': [
                {
                    'patterns': [
                        r'go.*?to.*?(?:directory|folder).*?(\S+)',
                        r'change.*?(?:directory|folder).*?to.*?(\S+)',
                        r'cd.*?(\S+)',
                        r'navigate.*?to.*?(\S+)'
                    ],
                    'command': 'cd {0}'
                }
            ],
            'show_content': [
                {
                    'patterns': [
                        r'show.*?content.*?(?:of|in).*?(\S+)',
                        r'display.*?(\S+)',
                        r'cat.*?(\S+)',
                        r'read.*?(\S+)',
                        r'view.*?(\S+)'
                    ],
                    'command': 'cat {0}'
                }
            ],
            'find_files': [
                {
                    'patterns': [
                        r'find.*?files?.*?(?:named|called).*?(\S+)',
                        r'search.*?for.*?(\S+)',
                        r'locate.*?(\S+)'
                    ],
                    'command': 'find . -name "{0}"'
                }
            ],
            'system_info': [
                {
                    'patterns': [
                        r'show.*?system.*?info',
                        r'system.*?status',
                        r'resource.*?usage',
                        r'top'
                    ],
                    'command': 'top'
                }
            ],
            'list_processes': [
                {
                    'patterns': [
                        r'list.*?processes?',
                        r'show.*?processes?',
                        r'running.*?programs?',
                        r'ps'
                    ],
                    'command': 'ps'
                }
            ],
            'current_directory': [
                {
                    'patterns': [
                        r'where.*?am.*?i',
                        r'current.*?(?:directory|folder|location)',
                        r'pwd',
                        r'show.*?(?:directory|folder)'
                    ],
                    'command': 'pwd'
                }
            ],
            'disk_usage': [
                {
                    'patterns': [
                        r'disk.*?usage',
                        r'disk.*?space',
                        r'storage.*?info',
                        r'df'
                    ],
                    'command': 'df'
                }
            ],
            'memory_usage': [
                {
                    'patterns': [
                        r'memory.*?usage',
                        r'ram.*?usage',
                        r'memory.*?info',
                        r'free.*?memory',
                        r'free'
                    ],
                    'command': 'free'
                }
            ],
            'clear_screen': [
                {
                    'patterns': [
                        r'clear.*?screen',
                        r'clear.*?terminal',
                        r'cls',
                        r'clear'
                    ],
                    'command': 'clear'
                }
            ],
            'help': [
                {
                    'patterns': [
                        r'help',
                        r'what.*?can.*?do',
                        r'available.*?commands?',
                        r'show.*?commands?'
                    ],
                    'command': 'help'
                }
            ],
            'echo': [
                {
                    'patterns': [
                        r'say.*?"([^"]+)"',
                        r'echo.*?"([^"]+)"',
                        r'print.*?"([^"]+)"',
                        r'display.*?"([^"]+)"'
                    ],
                    'command': 'echo "{0}"'
                }
            ]
        }
    
    def interpret_command(self, natural_language: str) -> Tuple[str, str]:
        """Convert natural language to terminal command"""
        nl_input = natural_language.strip().lower()
        
        # Handle complex multi-step commands
        complex_command = self._handle_complex_commands(nl_input)
        if complex_command:
            return complex_command, "AI interpreted multi-step command"
        
        # Try to match against patterns
        for category, patterns_list in self.command_patterns.items():
            for pattern_dict in patterns_list:
                for pattern in pattern_dict['patterns']:
                    match = re.search(pattern, nl_input, re.IGNORECASE)
                    if match:
                        # Extract parameters from the match
                        params = match.groups()
                        command = pattern_dict['command'].format(*params)
                        return command, f"AI interpreted '{natural_language}' as '{command}'"
        
        # If no pattern matches, try keyword-based interpretation
        keyword_command = self._interpret_by_keywords(nl_input)
        if keyword_command:
            return keyword_command, f"AI interpreted using keywords"
        
        # Return original input if no interpretation found
        return natural_language, "No AI interpretation found, executing as-is"
    
    def _handle_complex_commands(self, nl_input: str) -> str:
        """Handle complex multi-step commands"""
        # Handle "create folder and move file" type commands
        create_and_move = re.search(
            r'create.*?(?:folder|directory).*?(?:called|named)\s+(\S+).*?and.*?move.*?(\S+).*?(?:into|to).*?it',
            nl_input, re.IGNORECASE
        )
        if create_and_move:
            folder_name, file_name = create_and_move.groups()
            return f"mkdir {folder_name} && mv {file_name} {folder_name}/"
        
        # Handle "copy all files with extension" type commands
        copy_by_extension = re.search(
            r'copy.*?all.*?(\.\w+).*?files?.*?to.*?(\S+)',
            nl_input, re.IGNORECASE
        )
        if copy_by_extension:
            extension, destination = copy_by_extension.groups()
            return f"cp *{extension} {destination}/"
        
        # Handle "delete all files in directory" type commands
        delete_all_in_dir = re.search(
            r'delete.*?all.*?files?.*?in.*?(\S+)',
            nl_input, re.IGNORECASE
        )
        if delete_all_in_dir:
            directory = delete_all_in_dir.groups()[0]
            return f"rm {directory}/*"
        
        # Handle "find and delete" type commands
        find_and_delete = re.search(
            r'find.*?and.*?delete.*?files?.*?(?:called|named).*?(\S+)',
            nl_input, re.IGNORECASE
        )
        if find_and_delete:
            filename = find_and_delete.groups()[0]
            return f"find . -name \"{filename}\" -delete"
        
        return None
    
    def _interpret_by_keywords(self, nl_input: str) -> str:
        """Interpret command based on keywords when patterns don't match"""
        keywords = nl_input.split()
        
        # File operations
        if any(word in keywords for word in ['create', 'make', 'new']) and \
           any(word in keywords for word in ['file']):
            # Find filename
            for i, word in enumerate(keywords):
                if word in ['file'] and i + 1 < len(keywords):
                    return f"touch {keywords[i + 1]}"
            return "touch newfile.txt"
        
        if any(word in keywords for word in ['create', 'make', 'new']) and \
           any(word in keywords for word in ['folder', 'directory', 'dir']):
            # Find directory name
            for i, word in enumerate(keywords):
                if word in ['folder', 'directory', 'dir'] and i + 1 < len(keywords):
                    return f"mkdir {keywords[i + 1]}"
            return "mkdir newfolder"
        
        # Navigation
        if any(word in keywords for word in ['go', 'navigate', 'change']) and \
           any(word in keywords for word in ['directory', 'folder', 'to']):
            for i, word in enumerate(keywords):
                if word == 'to' and i + 1 < len(keywords):
                    return f"cd {keywords[i + 1]}"
        
        # List operations
        if any(word in keywords for word in ['list', 'show']) and \
           any(word in keywords for word in ['files', 'contents']):
            return "ls"
        
        # Delete operations
        if any(word in keywords for word in ['delete', 'remove', 'rm']):
            for word in keywords:
                if word not in ['delete', 'remove', 'rm', 'file', 'the']:
                    return f"rm {word}"
        
        return None
    
    def execute_natural_language(self, natural_language: str) -> Tuple[str, int, str]:
        """Execute natural language command and return output, return code, and interpretation"""
        command, interpretation = self.interpret_command(natural_language)
        output, return_code = self.terminal.execute_command(command)
        return output, return_code, interpretation
    
    def get_suggestions(self, partial_input: str) -> List[str]:
        """Get natural language suggestions based on partial input"""
        suggestions = []
        
        # Common command starters
        starters = [
            "create a file named",
            "create a folder named", 
            "list all files",
            "show me the files",
            "delete the file",
            "copy the file",
            "move the file",
            "go to the directory",
            "show me system info",
            "find files named",
            "where am I",
            "clear the screen",
            "help me"
        ]
        
        partial_lower = partial_input.lower()
        
        for starter in starters:
            if starter.startswith(partial_lower) or partial_lower in starter:
                suggestions.append(starter)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def get_help_text(self) -> str:
        """Get help text for AI terminal"""
        return """
AI-Powered Terminal - Natural Language Commands

You can use natural language to interact with the terminal. Here are some examples:

File Operations:
  "create a file named test.txt"
  "make a new folder called documents"
  "delete the file oldfile.txt"
  "copy file1.txt to backup/"
  "move document.pdf to archive/"
  "show me the contents of readme.txt"

Navigation:
  "list all files"
  "go to the documents folder"
  "where am I"
  "show me what's in this directory"

System Information:
  "show me system info"
  "list running processes"
  "check disk usage"
  "show memory usage"

Complex Operations:
  "create a folder called test and move file1.txt into it"
  "find all .txt files"
  "copy all .py files to backup/"
  "find and delete files named temp"

You can also use traditional terminal commands if preferred.
The AI will interpret your natural language and convert it to appropriate commands.
        """

class AITerminalCLI:
    """CLI interface for AI-powered terminal"""
    
    def __init__(self):
        self.ai_terminal = AITerminalInterface()
        self.use_ai = True
    
    def run(self):
        """Main CLI loop for AI terminal"""
        print("AI-Powered Python Terminal")
        print("Type natural language commands or traditional terminal commands")
        print("Type 'help' for examples, 'toggle ai' to switch modes, 'exit' to quit")
        print()
        
        while True:
            try:
                # Get input
                prompt = self.ai_terminal.terminal.get_prompt()
                if self.use_ai:
                    prompt = f"AI {prompt}"
                
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() == 'toggle ai':
                    self.use_ai = not self.use_ai
                    mode = "enabled" if self.use_ai else "disabled"
                    print(f"AI interpretation {mode}")
                    continue
                
                if user_input.lower() in ['exit', 'quit']:
                    break
                
                if user_input.lower() == 'ai help':
                    print(self.ai_terminal.get_help_text())
                    continue
                
                # Execute command
                if self.use_ai:
                    output, return_code, interpretation = self.ai_terminal.execute_natural_language(user_input)
                    if interpretation != "No AI interpretation found, executing as-is":
                        print(f"✓ {interpretation}")
                    if output and output != "EXIT_TERMINAL":
                        print(output)
                    if output == "EXIT_TERMINAL":
                        break
                else:
                    output, return_code = self.ai_terminal.terminal.execute_command(user_input)
                    if output and output != "EXIT_TERMINAL":
                        print(output)
                    if output == "EXIT_TERMINAL":
                        break
            
            except KeyboardInterrupt:
                print("\n^C")
                continue
            except EOFError:
                print("\nGoodbye!")
                break

def main():
    """Entry point for AI terminal CLI"""
    ai_cli = AITerminalCLI()
    ai_cli.run()

if __name__ == "__main__":
    main()