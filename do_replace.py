#!/usr/bin/env python3
"""重写PDF生成相关函数，完全按照纸质版PDF模板格式复刻。"""

import sys

INPUT_FILE = '/app/data/所有对话/主对话/weite-pro-temp/威特电梯厂检调试记录单v2.html'
CI_TEMPLATE = '/app/data/所有对话/主对话/weite-pro-temp/buildCheckItemsHTML_template.js'
SA_TEMPLATE = '/app/data/所有对话/主对话/weite-pro-temp/buildSingleAttachHTML_template.js'

# Read the file
with open(INPUT_FILE, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
    lines = content.split('\n')

def find_function_bounds(func_name, lines):
    """Find function start and end line indices (0-indexed)"""
    for i, line in enumerate(lines):
        if func_name in line and line.strip().startswith('function '):
            func_start = i
            brace_count = 0
            started = False
            for j in range(i, len(lines)):
                for ch in lines[j]:
                    if ch == '{':
                        brace_count += 1
                        started = True
                    elif ch == '}':
                        brace_count -= 1
                if started and brace_count == 0:
                    return func_start, j
    return None, None

# Find both functions
ci_start, ci_end = find_function_bounds('buildCheckItemsHTML', lines)
sa_start, sa_end = find_function_bounds('buildSingleAttachHTML', lines)

print(f"buildCheckItemsHTML: lines {ci_start+1}-{ci_end+1}")
print(f"buildSingleAttachHTML: lines {sa_start+1}-{sa_end+1}")

if ci_start is None or sa_start is None:
    print("ERROR: Could not find functions")
    sys.exit(1)

# Extract the logoBase64 line from buildCheckItemsHTML
logo_line = None
for i in range(ci_start, ci_start + 20):
    if 'var logoBase64' in lines[i]:
        logo_line = lines[i].rstrip()
        break

if not logo_line:
    print("ERROR: Could not find logoBase64")
    sys.exit(1)

print(f"Logo line found, length: {len(logo_line)}")

# Read template files and insert logo line
with open(CI_TEMPLATE, 'r', encoding='utf-8') as f:
    ci_func = f.read()
ci_func = ci_func.replace('__LOGO_LINE__', logo_line)

with open(SA_TEMPLATE, 'r', encoding='utf-8') as f:
    sa_func = f.read()
sa_func = sa_func.replace('__LOGO_LINE__', logo_line)

print("Templates prepared")

# ============================================================
# 执行替换 - 先替换后面的函数（行号大的），避免行号偏移
# ============================================================

# 先替换 buildSingleAttachHTML（后面的函数，行号更大）
new_lines = lines[:sa_start] + sa_func.split('\n') + lines[sa_end+1:]
print(f"After replacing buildSingleAttachHTML: {len(new_lines)} lines")

# 重新计算 buildCheckItemsHTML 的位置
lines2 = new_lines
ci_start2, ci_end2 = find_function_bounds('buildCheckItemsHTML', lines2)
print(f"buildCheckItemsHTML now at lines {ci_start2+1}-{ci_end2+1}")

# 再替换 buildCheckItemsHTML
new_lines = lines2[:ci_start2] + ci_func.split('\n') + lines2[ci_end2+1:]
print(f"After replacing buildCheckItemsHTML: {len(new_lines)} lines")

# Write back
new_content = '\n'.join(new_lines)
with open(INPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\nDone!")
print(f"Original lines: {len(lines)}")
print(f"New lines: {len(new_lines)}")
print(f"File size: {len(new_content)} bytes")
