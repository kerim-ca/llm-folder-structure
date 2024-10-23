import os
import json
from typing import List, Set

class ProjectDocumenter:
    def __init__(self, root_dir: str, ignore_dirs: Set[str] = None, ignore_files: Set[str] = None):
        self.root_dir = root_dir
        self.ignore_dirs = ignore_dirs or {'.git', 'node_modules', '__pycache__', 'dist', 'build', 'venv'}
        self.ignore_files = ignore_files or {'.DS_Store', '.env'}
        self.language_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'jsx',
            '.tsx': 'tsx',
            '.css': 'css',
            '.scss': 'scss',
            '.html': 'html',
            '.json': 'json',
            '.md': 'markdown',
            '.sql': 'sql',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
            '.ejs': 'html'
        }

    def generate_tree(self, startpath: str = None) -> str:
        """Generate a directory tree structure."""
        if startpath is None:
            startpath = self.root_dir

        tree = []
        for root, dirs, files in os.walk(startpath):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            level = root.replace(startpath, '').count(os.sep)
            indent = '│   ' * level
            
            # Add directory name
            if level > 0:
                tree.append(f'{indent[:-4]}├── {os.path.basename(root)}/')
            
            # Add files
            for file in sorted(files):
                if file not in self.ignore_files:
                    tree.append(f'{indent}├── {file}')

        return '\n'.join(tree)

    def get_file_language(self, filename: str) -> str:
        """Determine the language/syntax highlighting to use based on file extension."""
        _, ext = os.path.splitext(filename)
        return self.language_extensions.get(ext, '')

    def read_file_content(self, filepath: str) -> str:
        """Read and return file content, handling different encodings."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception:
                return "<<Binary file or encoding not supported>>"
        except Exception as e:
            return f"<<Error reading file: {str(e)}>>"

    def get_header_level(self, path: str) -> int:
        """
        Calculate header level based on directory depth.
        Root is h1, each subdirectory adds one level (h2, h3, etc.)
        Maximum level is h6 (HTML standard)
        """
        if path == '.':
            return 1
        depth = path.count(os.sep) + 2  # +2 because root is h1 and first level starts at h2
        return min(depth, 6)  # Cap at h6

    def generate_documentation(self) -> str:
        """Generate complete documentation including tree and file contents."""
        # Start with h1 header for project name
        documentation = [
            f"# {os.path.basename(self.root_dir)}\n",
            "## Directory Structure\n",
            "```",
            self.generate_tree(),
            "```\n",
            "## File Contents\n"
        ]

        for root, dirs, files in os.walk(self.root_dir):
            # Skip ignored directories
            if any(ignore_dir in root.split(os.sep) for ignore_dir in self.ignore_dirs):
                continue

            relative_path = os.path.relpath(root, self.root_dir)
            if relative_path != '.':
                # Calculate header level based on directory depth
                header_level = self.get_header_level(relative_path)
                header = '#' * header_level
                documentation.append(f"{header} {relative_path}\n")

            for file in sorted(files):
                if file in self.ignore_files:
                    continue

                filepath = os.path.join(root, file)
                language = self.get_file_language(file)
                
                documentation.extend([
                    f"**{file}:**",
                    "```" + language,
                    self.read_file_content(filepath),
                    "```\n"
                ])

        return '\n'.join(documentation)

    def save_documentation(self, output_file: str = 'project_documentation.md'):
        """Generate and save documentation to a file."""
        documentation = self.generate_documentation()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(documentation)
        print(f"Documentation saved to {output_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate project documentation')
    parser.add_argument('project_path', help='Path to the project directory')
    parser.add_argument('--output', '-o', default='project_documentation.md',
                       help='Output markdown file path')
    parser.add_argument('--ignore-dirs', '-d', nargs='*',
                       help='Additional directories to ignore')
    parser.add_argument('--ignore-files', '-f', nargs='*',
                       help='Additional files to ignore')

    args = parser.parse_args()

    # Create custom ignore sets
    ignore_dirs = {'.git', 'node_modules', '__pycache__', 'dist', 'build', 'venv', 'images'}
    ignore_files = {'.DS_Store', 'README.md', 'package-lock.json'}

    if args.ignore_dirs:
        ignore_dirs.update(args.ignore_dirs)
    if args.ignore_files:
        ignore_files.update(args.ignore_files)

    # Generate documentation
    documenter = ProjectDocumenter(
        args.project_path,
        ignore_dirs=ignore_dirs,
        ignore_files=ignore_files
    )
    documenter.save_documentation(args.output)

if __name__ == '__main__':
    main()
