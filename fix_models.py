# -*- coding: utf-8 -*-
import re

# Read file
with open('models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all SQL execute statements with tuple parameters
# Pattern: cursor.execute('SQL', (param))
# Fix broken ones

# Fix line-by-line
lines = content.split('\n')
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # If line ends with incomplete tuple like 'ORDER BY x DESC', (var)'
    # and next line starts with some random text
    if line.strip().endswith(")") and 'execute' in line:
        # Check if line has matching parens
        exec_part = line.split("execute('")[1].split("',", 1)[0] if "execute('" in line else ""
        if exec_part and '(' in exec_part:
            # Count parens in execute string
            # Actually simpler: check if line has incomplete tuple
            if line.count('(') > line.count(')'):
                # Incomplete tuple - add closing parens
                # Find the line number and content
                print(f"Fixing line {i+1}: {line[:80]}")
    fixed_lines.append(line)
    i += 1

print(f"Total lines: {len(fixed_lines)}")
print("Sample execute lines with issues:")
for j, line in enumerate(fixed_lines):
    if 'execute' in line and line.count('(') > line.count(')'):
        print(f"  {j+1}: {line.strip()[:100]}")
