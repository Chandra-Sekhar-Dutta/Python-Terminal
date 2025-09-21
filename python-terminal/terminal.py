# terminal.py - Main Terminal Class
import os
import sys
import shlex
import subprocess
import psutil
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class PythonTerminal:
    """A fully functioning command terminal built in Python"""
    
    def __init__(self):
        self.current_directory = os.getcwd()
        self.command_history = []
        self.aliases = {}
        self.environment_vars = dict(os.environ)
        
        # Built-in commands mapping
        self.builtin_commands = {
            'cd': self.cmd_cd,
            'pwd': self.cmd_pwd,
            'ls': self.cmd_ls,
            'dir': self.cmd_ls,  # Windows alias
            'mkdir': self.cmd_mkdir,
            'rmdir': self.cmd_rmdir,
            'rm': self.cmd_rm,
            'del': self.cmd_rm,  # Windows alias
            'touch': self.cmd_touch,
            'cat': self.cmd_cat,
            'type': self.cmd_cat,  # Windows alias
            'echo': self.cmd_echo,
            'cp': self.cmd_cp,
            'copy': self.cmd_cp,  # Windows alias
            'mv': self.cmd_mv,
            'move': self.cmd_mv,  # Windows alias
            'find': self.cmd_find,
            'grep': self.cmd_grep,
            'ps': self.cmd_ps,
            'kill': self.cmd_kill,
            'top': self.cmd_top,
            'df': self.cmd_df,
            'free': self.cmd_free,
            'whoami': self.cmd_whoami,
            'date': self.cmd_date,
            'history': self.cmd_history,
            'clear': self.cmd_clear,
            'cls': self.cmd_clear,  # Windows alias
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
            'help': self.cmd_help,
            'alias': self.cmd_alias,
            'env': self.cmd_env,
            'set': self.cmd_set,
            'tree': self.cmd_tree,
        }
    
    def get_prompt(self) -> str:
        """Generate command prompt string"""
        user = os.getenv('USER', os.getenv('USERNAME', 'user'))
        hostname = os.getenv('HOSTNAME', os.getenv('COMPUTERNAME', 'localhost'))
        cwd = os.path.basename(self.current_directory) if self.current_directory != '/' else '/'
        return f"{user}@{hostname}:{cwd}$ "
    
    def execute_command(self, command_line: str) -> Tuple[str, int]:
        """Execute a command and return output and return code"""
        if not command_line.strip():
            return "", 0
        
        # Add to history
        self.command_history.append(command_line)
        if len(self.command_history) > 1000:  # Limit history size
            self.command_history = self.command_history[-1000:]
        
        try:
            # Parse command
            parts = shlex.split(command_line)
            if not parts:
                return "", 0
            
            command = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            
            # Check for aliases
            if command in self.aliases:
                command = self.aliases[command]
            
            # Execute built-in command
            if command in self.builtin_commands:
                try:
                    return self.builtin_commands[command](args), 0
                except Exception as e:
                    return f"Error executing {command}: {str(e)}", 1
            
            # Execute external command
            return self.execute_external_command(command, args)
            
        except Exception as e:
            return f"Command parsing error: {str(e)}", 1
    
    def execute_external_command(self, command: str, args: List[str]) -> Tuple[str, int]:
        """Execute external system command"""
        try:
            # Change to current directory for command execution
            result = subprocess.run(
                [command] + args,
                cwd=self.current_directory,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            output = result.stdout
            if result.stderr:
                output += result.stderr
            
            return output, result.returncode
            
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds", 1
        except FileNotFoundError:
            return f"Command not found: {command}", 127
        except Exception as e:
            return f"Error executing external command: {str(e)}", 1
    
    # Built-in Commands Implementation
    
    def cmd_cd(self, args: List[str]) -> str:
        """Change directory command"""
        if not args:
            # Go to home directory
            target = os.path.expanduser("~")
        else:
            target = args[0]
            if target.startswith("~"):
                target = os.path.expanduser(target)
            elif not os.path.isabs(target):
                target = os.path.join(self.current_directory, target)
        
        try:
            target = os.path.abspath(target)
            if os.path.isdir(target):
                self.current_directory = target
                os.chdir(target)
                return f"Changed directory to: {target}"
            else:
                return f"Directory not found: {target}"
        except PermissionError:
            return f"Permission denied: {target}"
        except Exception as e:
            return f"Error changing directory: {str(e)}"
    
    def cmd_pwd(self, args: List[str]) -> str:
        """Print working directory"""
        return self.current_directory
    
    def cmd_ls(self, args: List[str]) -> str:
        """List directory contents"""
        path = args[0] if args else self.current_directory
        show_hidden = '-a' in args or '--all' in args
        long_format = '-l' in args or '--long' in args
        
        try:
            if not os.path.exists(path):
                return f"Path not found: {path}"
            
            if os.path.isfile(path):
                return self.format_file_info(path, long_format)
            
            items = []
            for item in os.listdir(path):
                if not show_hidden and item.startswith('.'):
                    continue
                
                full_path = os.path.join(path, item)
                if long_format:
                    items.append(self.format_file_info(full_path, True))
                else:
                    items.append(item)
            
            return '\n'.join(sorted(items)) if items else "Directory is empty"
            
        except PermissionError:
            return f"Permission denied: {path}"
        except Exception as e:
            return f"Error listing directory: {str(e)}"
    
    def format_file_info(self, path: str, long_format: bool = False) -> str:
        """Format file information for ls command"""
        if not long_format:
            return os.path.basename(path)
        
        try:
            stat = os.stat(path)
            size = stat.st_size
            mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            
            # File type and permissions
            if os.path.isdir(path):
                file_type = 'd'
            elif os.path.islink(path):
                file_type = 'l'
            else:
                file_type = '-'
            
            # Simple permission representation
            perms = oct(stat.st_mode)[-3:]
            
            return f"{file_type}{perms} {size:>8} {mtime} {os.path.basename(path)}"
            
        except Exception:
            return os.path.basename(path)
    
    def cmd_mkdir(self, args: List[str]) -> str:
        """Create directory"""
        if not args:
            return "Usage: mkdir <directory_name>"
        
        results = []
        for dir_name in args:
            try:
                if not os.path.isabs(dir_name):
                    dir_path = os.path.join(self.current_directory, dir_name)
                else:
                    dir_path = dir_name
                
                os.makedirs(dir_path, exist_ok=True)
                results.append(f"Created directory: {dir_name}")
            except Exception as e:
                results.append(f"Error creating {dir_name}: {str(e)}")
        
        return '\n'.join(results)
    
    def cmd_rmdir(self, args: List[str]) -> str:
        """Remove empty directory"""
        if not args:
            return "Usage: rmdir <directory_name>"
        
        results = []
        for dir_name in args:
            try:
                if not os.path.isabs(dir_name):
                    dir_path = os.path.join(self.current_directory, dir_name)
                else:
                    dir_path = dir_name
                
                os.rmdir(dir_path)
                results.append(f"Removed directory: {dir_name}")
            except FileNotFoundError:
                results.append(f"Directory not found: {dir_name}")
            except OSError as e:
                results.append(f"Error removing {dir_name}: {str(e)}")
        
        return '\n'.join(results)
    
    def cmd_rm(self, args: List[str]) -> str:
        """Remove files or directories"""
        if not args:
            return "Usage: rm [-r] <file_or_directory>"
        
        recursive = '-r' in args or '-rf' in args or '--recursive' in args
        force = '-f' in args or '-rf' in args or '--force' in args
        
        # Remove flags from args
        files = [arg for arg in args if not arg.startswith('-')]
        
        if not files:
            return "No files specified"
        
        results = []
        for file_name in files:
            try:
                if not os.path.isabs(file_name):
                    file_path = os.path.join(self.current_directory, file_name)
                else:
                    file_path = file_name
                
                if os.path.isdir(file_path):
                    if recursive:
                        import shutil
                        shutil.rmtree(file_path)
                        results.append(f"Removed directory tree: {file_name}")
                    else:
                        results.append(f"Cannot remove directory {file_name}: use -r flag")
                else:
                    os.remove(file_path)
                    results.append(f"Removed file: {file_name}")
                    
            except FileNotFoundError:
                if not force:
                    results.append(f"File not found: {file_name}")
            except PermissionError:
                results.append(f"Permission denied: {file_name}")
            except Exception as e:
                results.append(f"Error removing {file_name}: {str(e)}")
        
        return '\n'.join(results)
    
    def cmd_touch(self, args: List[str]) -> str:
        """Create empty file or update timestamp"""
        if not args:
            return "Usage: touch <filename>"
        
        results = []
        for filename in args:
            try:
                if not os.path.isabs(filename):
                    file_path = os.path.join(self.current_directory, filename)
                else:
                    file_path = filename
                
                # Create file if it doesn't exist, update timestamp if it does
                Path(file_path).touch()
                results.append(f"Touched: {filename}")
            except Exception as e:
                results.append(f"Error touching {filename}: {str(e)}")
        
        return '\n'.join(results)
    
    def cmd_cat(self, args: List[str]) -> str:
        """Display file contents"""
        if not args:
            return "Usage: cat <filename>"
        
        results = []
        for filename in args:
            try:
                if not os.path.isabs(filename):
                    file_path = os.path.join(self.current_directory, filename)
                else:
                    file_path = filename
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(args) > 1:
                        results.append(f"==> {filename} <==")
                    results.append(content)
            except FileNotFoundError:
                results.append(f"File not found: {filename}")
            except PermissionError:
                results.append(f"Permission denied: {filename}")
            except UnicodeDecodeError:
                results.append(f"Cannot display binary file: {filename}")
            except Exception as e:
                results.append(f"Error reading {filename}: {str(e)}")
        
        return '\n'.join(results)
    
    def cmd_echo(self, args: List[str]) -> str:
        """Echo text to output"""
        return ' '.join(args)
    
    def cmd_cp(self, args: List[str]) -> str:
        """Copy files or directories"""
        if len(args) < 2:
            return "Usage: cp [-r] <source> <destination>"
        
        recursive = '-r' in args or '--recursive' in args
        files = [arg for arg in args if not arg.startswith('-')]
        
        if len(files) < 2:
            return "Source and destination required"
        
        source = files[0]
        dest = files[1]
        
        try:
            if not os.path.isabs(source):
                source = os.path.join(self.current_directory, source)
            if not os.path.isabs(dest):
                dest = os.path.join(self.current_directory, dest)
            
            if os.path.isdir(source):
                if recursive:
                    import shutil
                    shutil.copytree(source, dest)
                    return f"Copied directory tree: {files[0]} -> {files[1]}"
                else:
                    return f"Cannot copy directory {files[0]}: use -r flag"
            else:
                import shutil
                shutil.copy2(source, dest)
                return f"Copied file: {files[0]} -> {files[1]}"
                
        except FileNotFoundError:
            return f"Source not found: {files[0]}"
        except Exception as e:
            return f"Error copying: {str(e)}"
    
    def cmd_mv(self, args: List[str]) -> str:
        """Move/rename files or directories"""
        if len(args) != 2:
            return "Usage: mv <source> <destination>"
        
        source, dest = args
        
        try:
            if not os.path.isabs(source):
                source = os.path.join(self.current_directory, source)
            if not os.path.isabs(dest):
                dest = os.path.join(self.current_directory, dest)
            
            import shutil
            shutil.move(source, dest)
            return f"Moved: {args[0]} -> {args[1]}"
            
        except FileNotFoundError:
            return f"Source not found: {args[0]}"
        except Exception as e:
            return f"Error moving: {str(e)}"
    
    def cmd_find(self, args: List[str]) -> str:
        """Find files and directories"""
        if not args:
            return "Usage: find <path> -name <pattern>"
        
        path = args[0] if args else self.current_directory
        pattern = None
        
        # Simple pattern matching for -name
        if '-name' in args:
            try:
                name_idx = args.index('-name')
                if name_idx + 1 < len(args):
                    pattern = args[name_idx + 1]
            except:
                pass
        
        try:
            if not os.path.isabs(path):
                path = os.path.join(self.current_directory, path)
            
            results = []
            for root, dirs, files in os.walk(path):
                for item in dirs + files:
                    full_path = os.path.join(root, item)
                    if pattern:
                        import fnmatch
                        if fnmatch.fnmatch(item, pattern):
                            results.append(full_path)
                    else:
                        results.append(full_path)
            
            return '\n'.join(results) if results else "No matches found"
            
        except Exception as e:
            return f"Error in find: {str(e)}"
    
    def cmd_grep(self, args: List[str]) -> str:
        """Search text in files"""
        if len(args) < 2:
            return "Usage: grep <pattern> <file>"
        
        pattern = args[0]
        filename = args[1]
        
        try:
            if not os.path.isabs(filename):
                file_path = os.path.join(self.current_directory, filename)
            else:
                file_path = filename
            
            results = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if pattern in line:
                        results.append(f"{line_num}: {line.rstrip()}")
            
            return '\n'.join(results) if results else f"No matches found for '{pattern}'"
            
        except FileNotFoundError:
            return f"File not found: {filename}"
        except Exception as e:
            return f"Error in grep: {str(e)}"
    
    # System Monitoring Commands
    
    def cmd_ps(self, args: List[str]) -> str:
        """List running processes"""
        try:
            results = ["PID   NAME                     CPU%   MEM%"]
            results.append("-" * 45)
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    results.append(f"{info['pid']:<5} {info['name']:<20} {info['cpu_percent']:<6.1f} {info['memory_percent']:<6.1f}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return '\n'.join(results)
        except Exception as e:
            return f"Error listing processes: {str(e)}"
    
    def cmd_kill(self, args: List[str]) -> str:
        """Kill a process by PID"""
        if not args:
            return "Usage: kill <pid>"
        
        try:
            pid = int(args[0])
            proc = psutil.Process(pid)
            proc.terminate()
            return f"Process {pid} terminated"
        except ValueError:
            return "Invalid PID: must be a number"
        except psutil.NoSuchProcess:
            return f"No such process: {args[0]}"
        except psutil.AccessDenied:
            return f"Access denied: cannot kill process {args[0]}"
        except Exception as e:
            return f"Error killing process: {str(e)}"
    
    def cmd_top(self, args: List[str]) -> str:
        """Display system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            results = [
                "System Resource Usage",
                "=" * 30,
                f"CPU Usage: {cpu_percent}%",
                f"Memory Usage: {memory.percent}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)",
                f"Disk Usage: {disk.percent}% ({disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB)",
                "",
                "Top Processes by CPU:",
                "PID   NAME                     CPU%   MEM%",
                "-" * 45
            ]
            
            # Get top CPU processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            for proc in processes[:10]:  # Top 10
                results.append(f"{proc['pid']:<5} {proc['name']:<20} {proc['cpu_percent'] or 0:<6.1f} {proc['memory_percent'] or 0:<6.1f}")
            
            return '\n'.join(results)
        except Exception as e:
            return f"Error getting system info: {str(e)}"
    
    def cmd_df(self, args: List[str]) -> str:
        """Display filesystem disk space usage"""
        try:
            results = ["Filesystem Usage", "=" * 30]
            
            # Get all disk partitions
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    results.append(f"Device: {partition.device}")
                    results.append(f"  Mountpoint: {partition.mountpoint}")
                    results.append(f"  File system: {partition.fstype}")
                    results.append(f"  Total: {usage.total // (1024**3):.1f}GB")
                    results.append(f"  Used: {usage.used // (1024**3):.1f}GB ({usage.percent}%)")
                    results.append(f"  Free: {usage.free // (1024**3):.1f}GB")
                    results.append("")
                except PermissionError:
                    results.append(f"Permission denied: {partition.device}")
                    results.append("")
            
            return '\n'.join(results)
        except Exception as e:
            return f"Error getting disk info: {str(e)}"
    
    def cmd_free(self, args: List[str]) -> str:
        """Display memory usage"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            results = [
                "Memory Usage Information",
                "=" * 30,
                f"Total RAM: {memory.total // (1024**3):.1f}GB",
                f"Available RAM: {memory.available // (1024**3):.1f}GB",
                f"Used RAM: {memory.used // (1024**3):.1f}GB ({memory.percent}%)",
                f"Free RAM: {memory.free // (1024**3):.1f}GB",
                "",
                f"Total Swap: {swap.total // (1024**3):.1f}GB",
                f"Used Swap: {swap.used // (1024**3):.1f}GB ({swap.percent}%)",
                f"Free Swap: {swap.free // (1024**3):.1f}GB"
            ]
            
            return '\n'.join(results)
        except Exception as e:
            return f"Error getting memory info: {str(e)}"
    
    # Utility Commands
    
    def cmd_whoami(self, args: List[str]) -> str:
        """Display current user"""
        return os.getenv('USER', os.getenv('USERNAME', 'unknown'))
    
    def cmd_date(self, args: List[str]) -> str:
        """Display current date and time"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def cmd_history(self, args: List[str]) -> str:
        """Display command history"""
        if not self.command_history:
            return "No command history"
        
        results = []
        for i, cmd in enumerate(self.command_history[-50:], 1):  # Last 50 commands
            results.append(f"{i:3d}  {cmd}")
        
        return '\n'.join(results)
    
    def cmd_clear(self, args: List[str]) -> str:
        """Clear screen"""
        # Return ANSI escape sequence to clear screen
        return "\033[2J\033[H"
    
    def cmd_exit(self, args: List[str]) -> str:
        """Exit terminal"""
        return "EXIT_TERMINAL"
    
    def cmd_help(self, args: List[str]) -> str:
        """Display help information"""
        help_text = """
Python Terminal - Available Commands:

File Operations:
  ls, dir          - List directory contents
  cd               - Change directory
  pwd              - Print working directory
  mkdir            - Create directory
  rmdir            - Remove empty directory
  rm, del          - Remove files/directories
  touch            - Create empty file
  cat, type        - Display file contents
  cp, copy         - Copy files/directories
  mv, move         - Move/rename files/directories
  find             - Find files and directories
  grep             - Search text in files
  tree             - Display directory tree

System Monitoring:
  ps               - List processes
  kill             - Kill process by PID
  top              - Display system resource usage
  df               - Display filesystem usage
  free             - Display memory usage

Utilities:
  echo             - Echo text
  whoami           - Display current user
  date             - Display current date/time
  history          - Show command history
  clear, cls       - Clear screen
  env              - Show environment variables
  alias            - Create command aliases
  help             - Show this help

Navigation:
  exit, quit       - Exit terminal

Use -h or --help with most commands for more options.
        """
        return help_text.strip()
    
    def cmd_alias(self, args: List[str]) -> str:
        """Create or list command aliases"""
        if not args:
            # List all aliases
            if not self.aliases:
                return "No aliases defined"
            
            results = ["Defined aliases:"]
            for alias, command in self.aliases.items():
                results.append(f"  {alias} = {command}")
            return '\n'.join(results)
        
        if '=' in args[0]:
            # Create alias
            alias, command = args[0].split('=', 1)
            self.aliases[alias.strip()] = command.strip()
            return f"Alias created: {alias.strip()} = {command.strip()}"
        else:
            return "Usage: alias name=command"
    
    def cmd_env(self, args: List[str]) -> str:
        """Display environment variables"""
        results = []
        for key, value in sorted(self.environment_vars.items()):
            results.append(f"{key}={value}")
        return '\n'.join(results)
    
    def cmd_set(self, args: List[str]) -> str:
        """Set environment variable"""
        if not args or '=' not in args[0]:
            return "Usage: set VARIABLE=value"
        
        var, value = args[0].split('=', 1)
        self.environment_vars[var] = value
        os.environ[var] = value
        return f"Set {var}={value}"
    
    def cmd_tree(self, args: List[str]) -> str:
        """Display directory tree"""
        path = args[0] if args else self.current_directory
        max_depth = 3  # Limit depth to avoid huge outputs
        
        try:
            if not os.path.isabs(path):
                path = os.path.join(self.current_directory, path)
            
            if not os.path.exists(path):
                return f"Path not found: {path}"
            
            results = [os.path.basename(path) or path]
            self._build_tree(path, "", results, 0, max_depth)
            
            return '\n'.join(results)
        except Exception as e:
            return f"Error building tree: {str(e)}"
    
    def _build_tree(self, path: str, prefix: str, results: List[str], depth: int, max_depth: int):
        """Helper method to build directory tree"""
        if depth >= max_depth:
            return
        
        try:
            items = sorted(os.listdir(path))
            for i, item in enumerate(items):
                if item.startswith('.'):
                    continue
                
                item_path = os.path.join(path, item)
                is_last = i == len(items) - 1
                
                current_prefix = "└── " if is_last else "├── "
                results.append(f"{prefix}{current_prefix}{item}")
                
                if os.path.isdir(item_path):
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    self._build_tree(item_path, next_prefix, results, depth + 1, max_depth)
        except PermissionError:
            results.append(f"{prefix}└── [Permission Denied]")