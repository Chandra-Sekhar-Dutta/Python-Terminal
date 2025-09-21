import sys
import argparse
from pathlib import Path

def main():
    """Main launcher for Python Terminal with different interface options"""
    parser = argparse.ArgumentParser(
        description="Python-based Command Terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py cli          # Launch CLI terminal
  python main.py web          # Launch web interface
  python main.py ai           # Launch AI-powered terminal
  python main.py web --port 8080 --host 0.0.0.0  # Custom web server settings
        """
    )
    
    parser.add_argument(
        'interface',
        choices=['cli', 'web', 'ai'],
        help='Interface type to launch'
    )
    
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host for web interface (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port for web interface (default: 5000)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode for web interface'
    )
    
    args = parser.parse_args()
    
    try:
        if args.interface == 'cli':
            print("Launching CLI Terminal...")
            from cli_interface import main as cli_main
            cli_main()
        
        elif args.interface == 'web':
            print("Launching Web Terminal...")
            from web_interface import run_web_server
            run_web_server(host=args.host, port=args.port, debug=args.debug)
        
        elif args.interface == 'ai':
            print("Launching AI-Powered Terminal...")
            from ai_interface import main as ai_main
            ai_main()
    
    except ImportError as e:
        print(f"Error: Missing required module - {e}")
        print("Please install required dependencies:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()