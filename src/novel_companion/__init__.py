"""
Novel Companion AI - AI-driven reading assistant
"""

__version__ = "0.1.0"
__author__ = "chogerlate"

def main():
    """Main entry point for the application"""
    import argparse
    from novel_companion.api.main import run_server
    
    parser = argparse.ArgumentParser(
        description="Novel Companion AI - AI-driven reading assistant",
        prog="novel-companion"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"Novel Companion AI {__version__}"
    )
    
    parser.add_argument(
        "--host", 
        default=None,
        help="Host to bind the server to"
    )
    
    parser.add_argument(
        "--port", 
        type=int,
        default=None,
        help="Port to bind the server to"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--no-reload", 
        action="store_true",
        help="Disable auto-reload in development"
    )
    
    args = parser.parse_args()
    
    # Start the server with optional overrides
    run_server(
        host_override=args.host,
        port_override=args.port,
        debug_override=args.debug,
        reload_override=not args.no_reload
    )
