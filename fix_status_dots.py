#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复进度条状态点缺失问题
"""

BASE_DIR = '/app/data/所有对话/主对话/weite-pro-temp'
DETAIL_FILE = BASE_DIR + '/weite-service-beta-detail.html'

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

html = read_file(DETAIL_FILE)

# ===== 修复1：在服务说明区块添加st_impact状态点 =====
old_impact_title = '''      <h4>⚠️ 服务说明</h4>'''

new_impact_title = '''      <h4 style="display:flex;align-items:center;justify-content:space-between;">
        <span>⚠️ 服务说明</span>
        <span class="card-status" id="st_impact"></span>
      </h4>'''

html = html.replace(old_impact_title, new_impact_title)

# ===== 修复2：在header-dropdown中添加隐藏的st_history和st_data =====
# 它们需要存在于DOM中以便updateBtnStatus能找到
old_header_dropdown = '''  <div class="header-dropdown" id="headerDropdown">
    <div onclick="closeHeaderMenu();openMo('historyMo')"><span class="menu-icon">📂</span>已保存记录</div>
    <div onclick="closeHeaderMenu();openMo('dataMo')"><span class="menu-icon">📦</span>数据迁移</div>
  </div>'''

new_header_dropdown = '''  <div class="header-dropdown" id="headerDropdown">
    <div onclick="closeHeaderMenu();openMo('historyMo')" style="display:flex;align-items:center;justify-content:space-between;">
      <span><span class="menu-icon">📂</span>已保存记录</span>
      <span class="card-count" id="st_history" style="font-size:10px;padding:1px 6px;">0条</span>
    </div>
    <div onclick="closeHeaderMenu();openMo('dataMo')"><span class="menu-icon">📦</span>数据迁移<span class="card-status" id="st_data" style="float:right;margin-top:4px;"></span></div>
  </div>'''

html = html.replace(old_header_dropdown, new_header_dropdown)

# ===== 修复3：确保进度条total数量正确 =====
# 原来total=11，现在检查一下有多少个filled项
# 基本信息tab: st_basic(申请人), st_project(项目信息), st_contact(联系方式), st_build(施工类别) = 4
# 服务详情tab: st_service(服务类别), st_flow(服务节点), st_record(服务记录), st_impact(服务说明) = 4
# 签字确认tab: st_sign(签字), st_history(已保存), st_data(数据迁移) = 3
# 总共 4+4+3 = 11，和原来一样

write_file(DETAIL_FILE, html)
print('✅ 状态点修复完成')

import subprocess, re
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
passed = 0
for i, script in enumerate(scripts):
    if not script.strip() or script.strip().startswith('<!--'):
        passed += 1
        continue
    tmp = f'/tmp/fix_status_{i}.js'
    with open(tmp, 'w') as f:
        f.write(script)
    r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
    if r.returncode == 0:
        passed += 1
    else:
        print(f'  ❌ 脚本{i+1} 错误: {r.stderr[:200]}')
    import os
    os.remove(tmp)
print(f'   JS语法: {passed}/{len(scripts)} 通过')

# 验证状态点
print()
print('=== 状态点验证 ===')
for sid in ['st_basic', 'st_project', 'st_contact', 'st_build', 
            'st_service', 'st_flow', 'st_record', 'st_impact',
            'st_sign', 'st_history', 'st_data']:
    count = html.count(f'id="{sid}"')
    status = '✅' if count >= 1 else '❌'
    print(f'  {status} {sid}: {count} 个')
