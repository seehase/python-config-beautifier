#!/usr/bin/env python3
"""
Config file beautifier for Python config files in dictionary format.

This script lints and beautifies configuration files with sections, subsections,
and key-value pairs, ensuring proper indentation and formatting.

Format specifications:
- Sections: [section_name]
- Subsections: [[subsection_name]], [[[nested_subsection]]], etc.
- Key-value pairs: key = value
- Comments: # comment
- Indentation: 4 spaces per level
- Maximum 1 blank line between sections
"""

import argparse
import re
import sys
from typing import List, Tuple, Optional


class ConfigLine:
    """Represents a line in the config file with its type and content."""
    
    def __init__(self, content: str, line_type: str, indent_level: int = 0):
        self.content = content.strip()
        self.line_type = line_type  # 'section', 'key_value', 'comment', 'blank'
        self.indent_level = indent_level
        self.original_line = content


class ConfigBeautifier:
    """Main class for beautifying config files."""
    
    def __init__(self):
        self.lines: List[ConfigLine] = []
        self.section_stack: List[int] = []
        
    def parse_line(self, line: str) -> ConfigLine:
        """Parse a single line and determine its type and indentation level."""
        stripped = line.strip()
        
        if not stripped:
            return ConfigLine(line, 'blank')
        
        if stripped.startswith('#'):
            indent = len(self.section_stack)
            return ConfigLine(stripped, 'comment', indent)
        
        section_match = re.match(r'^(\[+)([^\]]+)(\]+)$', stripped)
        if section_match:
            bracket_count = len(section_match.group(1))
            section_name = section_match.group(2)
            
            if len(section_match.group(3)) != bracket_count:
                raise ValueError(f"Mismatched brackets in section: {stripped}")
            
            level = bracket_count - 1
            
            while self.section_stack and self.section_stack[-1] >= level:
                self.section_stack.pop()
            
            self.section_stack.append(level)
            
            return ConfigLine(stripped, 'section', level)
        
        if '=' in stripped:
            parts = stripped.split('=', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                formatted_kv = f"{key} = {value}"
                indent = len(self.section_stack)
                return ConfigLine(formatted_kv, 'key_value', indent)
        
        return ConfigLine(stripped, 'content', len(self.section_stack))
    
    def parse_file(self, content: str) -> List[ConfigLine]:
        """Parse the entire file content into ConfigLine objects."""
        self.lines = []
        self.section_stack = []
        
        for line_num, line in enumerate(content.splitlines(), 1):
            try:
                parsed_line = self.parse_line(line)
                self.lines.append(parsed_line)
            except ValueError as e:
                print(f"Error on line {line_num}: {e}", file=sys.stderr)
                sys.exit(1)
        
        return self.lines

    def adjust_header_comments(self, lines: List[ConfigLine]) -> List[ConfigLine]:
        """Fix indentation of comments that are headers for sections."""
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.line_type == 'comment':
                # Look ahead to see if this is a header for a section
                next_section_idx = -1
                is_header = False
                for j in range(i + 1, len(lines)):
                    if lines[j].line_type == 'section':
                        next_section_idx = j
                        is_header = True
                        break
                    if lines[j].line_type not in ['comment', 'blank']:
                        is_header = False
                        break
                
                if is_header and next_section_idx != -1:
                    # This is a header block. Adjust all comments in it.
                    for k in range(i, next_section_idx):
                        if lines[k].line_type == 'comment':
                            lines[k].indent_level = lines[next_section_idx].indent_level
                    i = next_section_idx # skip to the section
                    continue
            i += 1
        return lines

    def remove_excessive_blank_lines_from_list(self, lines: List[ConfigLine]) -> List[ConfigLine]:
        """Remove excessive blank lines and handle section spacing properly."""
        if not lines:
            return []
        
        result = []
        i = 0
        
        while i < len(lines):
            current_line = lines[i]
            
            if current_line.line_type == 'blank':
                # Skip consecutive blank lines, keep max 1
                consecutive_blanks = 0
                j = i
                while j < len(lines) and lines[j].line_type == 'blank':
                    consecutive_blanks += 1
                    j += 1
                
                # Check what comes after blanks
                next_non_blank = None
                if j < len(lines):
                    next_non_blank = lines[j]
                
                # Check if we should remove these blank lines
                should_remove_blanks = False

                # Case 1: Blank lines are directly before a top-level section
                if (next_non_blank and next_non_blank.line_type == 'section' and next_non_blank.indent_level == 0):
                    should_remove_blanks = True

                # Case 2: Blank lines are before a comment that precedes a top-level section
                elif (next_non_blank and next_non_blank.line_type == 'comment'):
                    for k in range(j + 1, len(lines)):
                        if lines[k].line_type == 'section' and lines[k].indent_level == 0:
                            should_remove_blanks = True
                            break
                        elif lines[k].line_type not in ['blank', 'comment']:
                            break

                # Case 3: Blank lines are between a comment and the section it describes
                elif (i > 0 and lines[i-1].line_type == 'comment' and
                      next_non_blank and next_non_blank.line_type == 'section'):
                    should_remove_blanks = True

                if should_remove_blanks:
                    # Skip all blank lines
                    i = j
                    continue

                # Keep max 1 blank line in other cases (only if not before a top-level section comment)
                if consecutive_blanks > 0 and next_non_blank:
                    result.append(ConfigLine('', 'blank', 0))
                
                i = j
            else:
                result.append(current_line)
                i += 1
        
        # Remove trailing blank lines
        while result and result[-1].line_type == 'blank':
            result.pop()
        
        # Now add proper spacing after sections
        return self.add_section_end_spacing(result)
    
    def add_section_end_spacing(self, lines: List[ConfigLine]) -> List[ConfigLine]:
        """Add blank lines after sections end."""
        if not lines:
            return []
        
        result = []
        
        for i, line in enumerate(lines):
            result.append(line)
            
            # Check if we need to add spacing after this line
            if i < len(lines) - 1:  # Not the last line
                next_line = lines[i + 1]
                
                # Add blank line before top-level sections or the first comment that precedes a top-level section
                should_add_blank = False

                # Case 1: Next line is directly a top-level section
                if (next_line.line_type == 'section' and next_line.indent_level == 0):
                    # Don't add blank line if current line is a comment that describes the section
                    if not (line.line_type == 'comment' and line.indent_level == 0):
                        should_add_blank = True

                # Case 2: Next line is the first comment in a block that precedes a top-level section
                elif (next_line.line_type == 'comment' and
                      self.comment_precedes_toplevel_section(lines, i + 1) and
                      line.line_type != 'comment'):  # Only if current line is not a comment
                    should_add_blank = True

                if (should_add_blank and
                    line.line_type in ['key_value', 'section', 'comment'] and
                    line.indent_level >= 0):

                    # Don't add if there's already a blank line
                    if not (result and result[-1].line_type == 'blank'):
                        result.append(ConfigLine('', 'blank', 0))
        
        return result
    
    def comment_precedes_toplevel_section(self, lines: List[ConfigLine], comment_index: int) -> bool:
        """Check if a comment at given index precedes a top-level section."""
        for i in range(comment_index + 1, len(lines)):
            if lines[i].line_type == 'section' and lines[i].indent_level == 0:
                return True
            elif lines[i].line_type not in ['blank', 'comment']:
                return False
        return False

    def format_line(self, line: ConfigLine) -> str:
        """Format a single line with proper indentation."""
        if line.line_type == 'blank':
            return ''
        
        indent = '    ' * line.indent_level
        
        return f"{indent}{line.content}"
    
    def add_section_spacing(self, lines: List[ConfigLine]) -> List[ConfigLine]:
        """Add proper spacing between sections and remove unwanted blank lines."""
        result = []
        
        for i, line in enumerate(lines):
            # Skip blank lines before comments that precede sections
            if (line.line_type == 'blank' and 
                i + 1 < len(lines) and 
                lines[i + 1].line_type == 'comment' and
                self.is_comment_before_section(lines, i + 1)):
                continue
                
            result.append(line)
            
            # Add blank line after section content ends (before next section)
            if (i < len(lines) - 1 and 
                line.line_type == 'key_value' and
                self.next_line_is_section_or_section_comment(lines, i + 1) and
                not (result and result[-1].line_type == 'blank')):
                result.append(ConfigLine('', 'blank'))
        
        return result
    
    def next_line_is_section_or_section_comment(self, lines: List[ConfigLine], start_idx: int) -> bool:
        """Check if the next non-blank line is a section or comment before section."""
        for i in range(start_idx, len(lines)):
            line = lines[i]
            if line.line_type == 'blank':
                continue
            elif line.line_type == 'section' and line.indent_level == 0:
                return True
            elif line.line_type == 'comment':
                # Check if this comment is followed by a top-level section
                return self.is_comment_before_section(lines, i) and self.get_next_section_level(lines, i) == 0
            else:
                return False
        return False
    
    def is_comment_before_section(self, lines: List[ConfigLine], comment_index: int) -> bool:
        """Check if a comment is immediately before a section."""
        if comment_index >= len(lines) or lines[comment_index].line_type != 'comment':
            return False
        
        # Look for the next non-blank line after the comment
        for j in range(comment_index + 1, len(lines)):
            next_line = lines[j]
            if next_line.line_type == 'blank':
                continue
            elif next_line.line_type == 'section':
                return True
            else:
                return False
        
        return False
    
    def get_next_section_level(self, lines: List[ConfigLine], comment_index: int) -> Optional[int]:
        """Get the indent level of the next section after a comment."""
        for j in range(comment_index + 1, len(lines)):
            line = lines[j]
            if line.line_type == 'blank':
                continue
            elif line.line_type == 'section':
                return line.indent_level
            else:
                break
        return None

    def validate_config(self, lines: List[ConfigLine]) -> bool:
        """Validate the configuration for duplicates and structure."""
        sections = {}
        current_path = []
        
        for line in lines:
            if line.line_type == 'section':
                # Update current path based on indentation level
                level = line.indent_level
                if level < len(current_path):
                    current_path = current_path[:level]
                
                section_name = re.match(r'\[+([^\]]+)\]+', line.content).group(1)
                current_path.append(section_name)
                
                # Check for duplicate sections at the same level
                path_key = '/'.join(current_path)
                if path_key in sections:
                    print(f"Warning: Duplicate section found: {path_key}", file=sys.stderr)
                    return False
                sections[path_key] = True
        
        return True
    
    def beautify(self, content: str) -> str:
        """Main method to beautify the config file content."""
        # Parse the file
        lines = self.parse_file(content)
        
        # Adjust comment indentation for headers
        lines = self.adjust_header_comments(lines)
        
        # Add proper section spacing
        lines = self.add_section_spacing(lines)
        
        # Remove excessive blank lines (after spacing is added)
        lines = self.remove_excessive_blank_lines_from_list(lines)
        
        # Validate configuration
        self.validate_config(lines)
        
        # Format all lines
        formatted_lines = [self.format_line(line) for line in lines]
        
        # Join lines and ensure single trailing newline
        result = '\n'.join(formatted_lines)
        if result and not result.endswith('\n'):
            result += '\n'
        
        return result


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Beautify Python config files in dictionary format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python config_beautifier.py input.conf
    python config_beautifier.py input.conf --output output.conf
    python config_beautifier.py input.conf -o beautified.conf
        """
    )
    
    parser.add_argument('source', help='Source config file to beautify')
    parser.add_argument('-o', '--output', help='Output file (default: overwrite source)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without writing')
    
    args = parser.parse_args()
    
    # Read source file
    try:
        with open(args.source, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.source}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{args.source}': {e}", file=sys.stderr)
        sys.exit(1)
    
    # Beautify content
    beautifier = ConfigBeautifier()
    try:
        beautified_content = beautifier.beautify(content)
    except Exception as e:
        print(f"Error beautifying file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Determine output file
    output_file = args.output if args.output else args.source
    
    # Dry run mode
    if args.dry_run:
        print("Dry run mode - showing beautified content:")
        print("-" * 50)
        print(beautified_content)
        print("-" * 50)
        print(f"Would write to: {output_file}")
        return
    
    # Write output
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(beautified_content)
        print(f"Successfully beautified '{args.source}' -> '{output_file}'")
    except Exception as e:
        print(f"Error writing to '{output_file}': {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
