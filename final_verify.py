#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的JS语法验证 - 提取所有script标签并检查
"""

import re
import subprocess
import os

BASE_DIR = '/app/data/所有对话/主对话/weite-pro-temp'

def check_file(filepath):
    fname = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    total = len(scripts)
    passed = 0
    errors = []
    
    for i, script in enumerate(scripts):
        if not script.strip():
            passed += 1
            continue
        if script.strip().startswith('<!--'):
            passed += 1
            continue
        
        tmp = f'/tmp/jscheck_{fname}_{i}.js'
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(script)
        
        try:
            r = subprocess.run(['node', '--check', tmp], 
                             capture_output=True, text=True, timeout=15)
            if r.returncode == 0:
                passed += 1
            else:
                errors.append((i+1, r.stderr[:300]))
        except Exception as e:
            errors.append((i+1, str(e)))
        
        try:
            os.remove(tmp)
        except:
            pass
    
    return total, passed, errors

print('=' * 60)
print('JS语法完整验证')
print('=' * 60)

all_ok = True
for fname in ['weite-service-beta.html', 'weite-service-beta-detail.html']:
    fpath = os.path.join(BASE_DIR, fname)
    total, passed, errors = check_file(fpath)
    status = '✅ 通过' if passed == total else '❌ 失败'
    print(f'\n{fname}: {status} ({passed}/{total})')
    if errors:
        all_ok = False
        for idx, err in errors:
            print(f'  脚本{idx} 错误:')
            for line in err.strip().split('\n')[:5]:
                print(f'    {line}')

print()
print('=' * 60)
if all_ok:
    print('✅ 所有文件JS语法验证通过！')
else:
    print('❌ 存在语法错误，请修复！')
print('=' * 60)

# 数据兼容性检查
print()
print('数据兼容性检查:')
with open(os.path.join(BASE_DIR, 'weite-service-beta-detail.html'), 'r', encoding='utf-8') as f:
    detail = f.read()

data_fields = [
    'initiator', 'serviceCount', 'projectName', 'elevators',
    'province', 'city', 'county', 'detailAddr',
    'siteContact', 'sitePhone', 'servicePerson', 'servicePhone',
    'serviceTime', 'construction', 'preSale', 'during', 'afterSale',
    'visit', 'flowTo', 'impact', 'urgentItems', 'stopDate',
    'sig1', 'sig2', 'records', 'savedAt', 'wtList', 'WeiteKV'
]
missing = []
for field in data_fields:
    if field not in detail:
        missing.append(field)

if missing:
    print(f'  ⚠️  可能缺失的字段: {missing}')
else:
    print(f'  ✅ 全部 {len(data_fields)} 个数据字段兼容')

# 表单ID检查
form_ids = [f'f{i}' for i in range(1, 15)]
missing_ids = []
for fid in form_ids:
    if f'id="{fid}"' not in detail:
        missing_ids.append(fid)

if missing_ids:
    print(f'  ⚠️  可能缺失的表单ID: {missing_ids}')
else:
    print(f'  ✅ 全部 {len(form_ids)} 个表单字段ID保留')

print()
