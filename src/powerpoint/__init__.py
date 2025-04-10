from . import server
import asyncio
import argparse

def main():
    """Main entry point for the package."""
    parser = argparse.ArgumentParser(description='Powerpoint MCP Server')
    parser.add_argument('--folder-path',
                       default="/tmp",
                       help="Folder to store completed decks in.")
    args = parser.parse_args()
    asyncio.run(server.main(args.folder_path))

# Optionally expose other important items at package level
__all__ = ['main', 'server']