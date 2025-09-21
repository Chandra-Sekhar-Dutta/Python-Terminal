import unittest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_basic_tests():
    """Run basic functionality tests"""
    print("Running basic terminal tests...")
    
    try:
        # Test terminal import
        from terminal import PythonTerminal
        terminal = PythonTerminal()
        print("✓ Terminal module imported successfully")
        
        # Test basic commands
        test_commands = [
            ('pwd', 'Print working directory'),
            ('echo hello world', 'Echo command'),
            ('help', 'Help command'),
            ('whoami', 'User info command'),
            ('date', 'Date command'),
        ]
        
        for cmd, desc in test_commands:
            try:
                output, code = terminal.execute_command(cmd)
                if output:
                    print(f"✓ {desc}: OK")
                else:
                    print(f"⚠ {desc}: No output")
            except Exception as e:
                print(f"✗ {desc}: Error - {e}")
        
        # Test CLI interface
        try:
            from cli_interface import CLIInterface
            print("✓ CLI interface module imported successfully")
        except Exception as e:
            print(f"✗ CLI interface error: {e}")
        
        # Test web interface
        try:
            from web_interface import app
            print("✓ Web interface module imported successfully")
        except Exception as e:
            print(f"✗ Web interface error: {e}")
        
        # Test AI interface
        try:
            from ai_interface import AITerminalInterface
            ai_terminal = AITerminalInterface()
            
            # Test natural language interpretation
            test_nl_commands = [
                "create a file named test.txt",
                "list all files",
                "show me system info"
            ]
            
            for nl_cmd in test_nl_commands:
                cmd, interpretation = ai_terminal.interpret_command(nl_cmd)
                print(f"✓ AI interpretation: '{nl_cmd}' -> '{cmd}'")
            
            print("✓ AI interface module imported successfully")
        except Exception as e:
            print(f"✗ AI interface error: {e}")
        
        print("\nBasic tests completed!")
        
    except Exception as e:
        print(f"✗ Critical error during testing: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_basic_tests()
    sys.exit(0 if success else 1)