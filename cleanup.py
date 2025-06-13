#!/usr/bin/env python3
import os
import shutil
import sys
from pathlib import Path
import logging
from typing import List, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodebaseCleaner:
    def __init__(self, root_dir: str = None):
        """Initialize the cleaner with the root directory."""
        self.root_dir = Path(root_dir) if root_dir else Path(__file__).parent
        self.directories_to_remove: Set[str] = {
            'node_modules',
            'artifacts',
            'coverage',
            'cache',
            '.pytest_cache',
            'venv',
            'crypto_sniping_bot.egg-info',
            'test',  # Only remove the 'test' directory (singular), not 'tests' (plural)
        }
        self.files_to_remove: Set[str] = {
            '.coverage',
            'coverage.json',
            'update.log',
            'sniper_bot.log',
        }
        self.patterns_to_remove: Set[str] = {
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.coverage.*',
        }

    def is_safe_to_delete(self, path: Path) -> bool:
        """Check if it's safe to delete the given path."""
        # Don't delete if it's the root directory
        if path == self.root_dir:
            return False
        
        # Don't delete if it's a git directory
        if '.git' in path.parts:
            return False
        
        # Don't delete if it's a source code directory
        source_dirs = {'bot', 'tests', 'contracts', 'scripts', 'docs', 'abis'}
        if path.name in source_dirs and path.is_dir():
            return False
        
        return True

    def remove_directory(self, dir_path: Path) -> None:
        """Safely remove a directory."""
        if not dir_path.exists():
            return

        if not self.is_safe_to_delete(dir_path):
            logger.warning(f"Skipping protected directory: {dir_path}")
            return

        try:
            shutil.rmtree(dir_path)
            logger.info(f"Removed directory: {dir_path}")
        except Exception as e:
            logger.error(f"Error removing directory {dir_path}: {e}")

    def remove_file(self, file_path: Path) -> None:
        """Safely remove a file."""
        if not file_path.exists():
            return

        if not self.is_safe_to_delete(file_path):
            logger.warning(f"Skipping protected file: {file_path}")
            return

        try:
            file_path.unlink()
            logger.info(f"Removed file: {file_path}")
        except Exception as e:
            logger.error(f"Error removing file {file_path}: {e}")

    def find_pattern_matches(self, pattern: str) -> List[Path]:
        """Find all files/directories matching the given pattern."""
        matches = []
        for root, dirs, files in os.walk(self.root_dir):
            root_path = Path(root)
            
            # Check directories
            if pattern in dirs:
                matches.append(root_path / pattern)
            
            # Check files
            for file in files:
                if file.endswith(pattern.replace('*', '')):
                    matches.append(root_path / file)
        
        return matches

    def cleanup(self) -> None:
        """Perform the cleanup operation."""
        logger.info(f"Starting cleanup in: {self.root_dir}")

        # Remove specific directories
        for dir_name in self.directories_to_remove:
            dir_path = self.root_dir / dir_name
            self.remove_directory(dir_path)

        # Remove specific files
        for file_name in self.files_to_remove:
            file_path = self.root_dir / file_name
            self.remove_file(file_path)

        # Remove files/directories matching patterns
        for pattern in self.patterns_to_remove:
            matches = self.find_pattern_matches(pattern)
            for match in matches:
                if match.is_dir():
                    self.remove_directory(match)
                else:
                    self.remove_file(match)

        logger.info("Cleanup completed!")

def main():
    """Main entry point for the script."""
    # Allow specifying a different root directory
    root_dir = sys.argv[1] if len(sys.argv) > 1 else None
    
    cleaner = CodebaseCleaner(root_dir)
    cleaner.cleanup()

if __name__ == "__main__":
    main() 