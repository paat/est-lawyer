#!/usr/bin/env python3
"""
Script to generate a project status report for the est-lawyer project.
This script scans the project directory, parses .gitignore for exclusions,
and generates a Markdown report with file structure and key file contents.
"""

import os
import pathlib
import argparse
import datetime
import fnmatch
import re
import logging

# Configuration
PROJECT_ROOT_PATH = pathlib.Path(".")
DEFAULT_EXCLUDED_DIRS = ['.git', '.venv', 'venv', 'ENV', 'env', '__pycache__', '.vscode', '.idea', 'data']
DEFAULT_EXCLUDED_FILE_PATTERNS = ['*.pyc', '*.pyo', '*.egg-info', '*.dist-info', '*.whl', '*.sqlite', '*.sqlite3', '.DS_Store', 'Thumbs.db', 'generate_project_status.py']
DEFAULT_FILES_FOR_CONTENT_INCLUSION = ['requirements.txt', '.env.example']
DEFAULT_DIRS_FOR_CONTENT_INCLUSION = ['src']
DEFAULT_OUTPUT_FILENAME = "project_status_report.md"

def parse_gitignore(gitignore_path):
    """
    Parse the .gitignore file and return a list of patterns.
    """
    patterns = []
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns

def is_path_excluded(path_to_check, project_root, gitignore_patterns, default_excluded_dirs, default_excluded_file_patterns):
    """
    Check if a path should be excluded based on gitignore patterns and default exclusions.
    """
    # Check if path is in default excluded dirs
    if path_to_check.is_dir():
        path_rel = path_to_check.relative_to(project_root)
        if path_rel.name in default_excluded_dirs:
            return True

    # Check if path matches any gitignore pattern
    try:
        path_rel = path_to_check.relative_to(project_root)
        path_str = str(path_rel)
        for pattern in gitignore_patterns:
            if fnmatch.fnmatch(path_str, pattern):
                return True
    except ValueError:
        # Path is not a child of project_root
        pass

    # Check if path matches any default excluded file pattern
    path_str = str(path_to_check.name)
    for pattern in default_excluded_file_patterns:
        if fnmatch.fnmatch(path_str, pattern):
            return True

    return False

def build_file_tree(current_path, project_root, indent="", exclusions_check_func=None):
    """
    Recursively build a Markdown-formatted file tree.
    """
    result = ""
    try:
        path_rel = current_path.relative_to(project_root)
        result += f"{indent}- {path_rel}/\n"

        if current_path.is_dir():
            items = sorted(current_path.iterdir(),
                          key=lambda p: (p.is_dir(), p.name.lower()))
            for item in items:
                if exclusions_check_func and exclusions_check_func(item):
                    continue
                result += build_file_tree(item, project_root, indent + "  ", exclusions_check_func)
    except Exception as e:
        logging.warning(f"Error processing path {current_path}: {e}")

    return result

def collect_files_for_content(project_root, default_files, default_dirs, additional_content_paths=None, exclusions_check_func=None):
    """
    Collect files whose content should be included in the report.
    """
    files_to_include = set()

    # Add default files
    for file in default_files:
        path = project_root / file
        if path.exists() and not exclusions_check_func(path):
            files_to_include.add(path)

    # Add files from default directories
    for dir_name in default_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists() and dir_path.is_dir():
            for ext in ['.py', '.txt', '.md', '.json', '.yaml', '.yml']:
                for file_path in dir_path.rglob(f"*{ext}"):
                    if not exclusions_check_func(file_path):
                        files_to_include.add(file_path)

    # Add additional content paths if provided
    if additional_content_paths:
        for path_str in additional_content_paths:
            path = project_root / path_str
            if path.exists():
                if path.is_dir():
                    for ext in ['.py', '.txt', '.md', '.json', '.yaml', '.yml']:
                        for file_path in path.rglob(f"*{ext}"):
                            if not exclusions_check_func(file_path):
                                files_to_include.add(file_path)
                else:
                    if not exclusions_check_func(path):
                        files_to_include.add(path)

    return sorted(files_to_include)

def get_file_content(filepath):
    """
    Read and return the content of a file.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Error reading {filepath}: {e}")
        return None

def generate_report_markdown(project_name, file_tree, content_files, gitignore_used, exclusions, inclusions):
    """
    Generate the Markdown report.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines = []

    # Title and timestamp
    report_lines.append(f"# {project_name} Project Status Report")
    report_lines.append(f"Generated on: {timestamp}\n")

    # Configuration summary
    report_lines.append("## Configuration Summary\n")
    report_lines.append(f"- Project root: {PROJECT_ROOT_PATH}\n")
    report_lines.append(f"- Gitignore used: {'Yes' if gitignore_used else 'No'}\n")
    report_lines.append("- Default exclusions applied:\n")
    for dir_name in DEFAULT_EXCLUDED_DIRS:
        report_lines.append(f"  - Directory: {dir_name}\n")
    for pattern in DEFAULT_EXCLUDED_FILE_PATTERNS:
        report_lines.append(f"  - File pattern: {pattern}\n")
    report_lines.append("- Additional exclusions from .gitignore:\n")
    if gitignore_used:
        for pattern in exclusions['gitignore_patterns']:
            report_lines.append(f"  - {pattern}\n")
    else:
        report_lines.append("  - None (no .gitignore found)\n")
    report_lines.append("- Files/directories with content included:\n")
    for file in inclusions['default_files']:
        report_lines.append(f"  - Default file: {file}\n")
    for dir_name in inclusions['default_dirs']:
        report_lines.append(f"  - Default directory: {dir_name}\n")
    if inclusions['additional_paths']:
        for path in inclusions['additional_paths']:
            report_lines.append(f"  - Additional path: {path}\n")
    else:
        report_lines.append("  - No additional paths\n")

    # Project file structure
    report_lines.append("\n## Project File Structure\n")
    report_lines.append(file_tree)

    # Key file contents
    report_lines.append("\n## Key File Contents\n")
    for content_file in content_files:
        filepath = content_file['filepath']
        content = content_file['content']

        if not content:
            continue

        # Determine language for syntax highlighting
        ext = pathlib.Path(filepath).suffix.lower()
        language = ""
        if ext == '.py':
            language = "python"
        elif ext == '.md':
            language = "markdown"
        elif ext in ['.json', '.yaml', '.yml']:
            language = "json" if ext == '.json' else "yaml"
        elif ext == '.txt':
            language = "text"

        # Add file content with syntax highlighting
        report_lines.append(f"\n### {filepath}\n")
        if language:
            report_lines.append(f"```{language}\n{content}\n```")
        else:
            report_lines.append(f"```\n{content}\n```")

    return "\n".join(report_lines)

def main():
    """
    Main execution logic.
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate a project status report in Markdown format.")
    parser.add_argument("-o", "--output", type=str, default=DEFAULT_OUTPUT_FILENAME,
                        help=f"Output file name (default: {DEFAULT_OUTPUT_FILENAME})")
    parser.add_argument("--include-content", action="append",
                        help="Path to a specific file or directory whose textual content should be included")
    parser.add_argument("--no-default-content", action="store_true",
                        help="Disable inclusion of default files/dirs content")
    args = parser.parse_args()

    # Load .gitignore patterns
    gitignore_path = PROJECT_ROOT_PATH / '.gitignore'
    gitignore_patterns = parse_gitignore(gitignore_path)
    gitignore_used = len(gitignore_patterns) > 0

    # Define exclusions check function
    def is_excluded(path):
        return is_path_excluded(path, PROJECT_ROOT_PATH, gitignore_patterns,
                                DEFAULT_EXCLUDED_DIRS, DEFAULT_EXCLUDED_FILE_PATTERNS)

    # Build file tree
    file_tree = build_file_tree(PROJECT_ROOT_PATH, PROJECT_ROOT_PATH, exclusions_check_func=is_excluded)

    # Collect files for content inclusion
    default_files = DEFAULT_FILES_FOR_CONTENT_INCLUSION if not args.no_default_content else []
    default_dirs = DEFAULT_DIRS_FOR_CONTENT_INCLUSION if not args.no_default_content else []

    content_paths = collect_files_for_content(
        PROJECT_ROOT_PATH,
        default_files,
        default_dirs,
        args.include_content,
        exclusions_check_func=is_excluded
    )

    # Get content for each file
    content_files = []
    for path in content_paths:
        content = get_file_content(path)
        content_files.append({'filepath': str(path.relative_to(PROJECT_ROOT_PATH)), 'content': content})

    # Generate report
    inclusions = {
        'default_files': DEFAULT_FILES_FOR_CONTENT_INCLUSION if not args.no_default_content else [],
        'default_dirs': DEFAULT_DIRS_FOR_CONTENT_INCLUSION if not args.no_default_content else [],
        'additional_paths': args.include_content or []
    }

    exclusions = {
        'gitignore_patterns': gitignore_patterns
    }

    report_content = generate_report_markdown(
        "est-lawyer",
        file_tree,
        content_files,
        gitignore_used,
        exclusions,
        inclusions
    )

    # Write report to output file
    output_path = PROJECT_ROOT_PATH / args.output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    logging.info(f"Project status report generated: {output_path}")

if __name__ == "__main__":
    main()