#!/usr/bin/env python3
"""
Extract JS from HTML <script> tags and validate with node --check
"""
import re
import subprocess
import os
import sys

def extract_and_check(html_path, label):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract all script tag contents
    # Handle both <script> and <script ...>
    pattern = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
    matches = pattern.findall(content)
    
    print(f"\n{'='*60}")
    print(f"Checking: {label}")
    print(f"Found {len(matches)} script block(s)")
    print(f"{'='*60}")
    
    all_ok = True
    for i, js_code in enumerate(matches):
        # Skip empty scripts
        if not js_code.strip():
            continue
        
        # Skip scripts that load external files (no content)
        if len(js_code.strip()) < 10:
            continue
            
        tmp_path = f"/tmp/check_{label}_{i}.js"
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(js_code)
        
        result = subprocess.run(
            ['node', '--check', tmp_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"  Script block {i+1}: ✓ OK ({len(js_code)} chars)")
        else:
            print(f"  Script block {i+1}: ✗ FAILED ({len(js_code)} chars)")
            print(f"    {result.stderr}")
            all_ok = False
        
        os.remove(tmp_path)
    
    return all_ok

# Check both files
print_ok = extract_and_check(
    "/app/data/所有对话/主对话/weite-pro-temp/print-fubiao.html",
    "print-fubiao"
)

main_ok = extract_and_check(
    "/app/data/所有对话/主对话/weite-pro-temp/factory-inspection-v2.html",
    "factory-inspection-v2"
)

print(f"\n{'='*60}")
print("SUMMARY:")
print(f"  print-fubiao.html:         {'✓ PASS' if print_ok else '✗ FAIL'}")
print(f"  factory-inspection-v2.html: {'✓ PASS' if main_ok else '✗ FAIL'}")
print(f"{'='*60}")

if not (print_ok and main_ok):
    sys.exit(1)
