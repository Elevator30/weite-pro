#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v131版本11项修复脚本 v2
"""

import re
import sys
import subprocess
import tempfile
import os

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def validate_js(content):
    """验证JS语法 - 使用node --check只检查语法，不执行"""
    scripts = re.findall(r'<script[^>]*>([\s\S]*?)</script>', content)
    all_js = '\n'.join(scripts)
    
    # 写入临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(all_js)
        tmp_path = f.name
    
    try:
        result = subprocess.run(
            ['node', '--check', tmp_path],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return True, 'JS语法OK'
        else:
            return False, result.stderr.strip()
    finally:
        os.unlink(tmp_path)

def replace_between_lines(lines, start_marker, end_marker, replacement_lines, include_end=True):
    """
    在行列表中找到start_marker和end_marker之间的内容，替换为replacement_lines
    返回新的行列表和是否成功
    """
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if start_marker in line and start_idx is None:
            start_idx = i
        if start_idx is not None and end_marker in line:
            end_idx = i
            break
    
    if start_idx is None or end_idx is None:
        return lines, False
    
    if include_end:
        new_lines = lines[:start_idx] + replacement_lines + lines[end_idx+1:]
    else:
        new_lines = lines[:start_idx] + replacement_lines + lines[end_idx:]
    
    return new_lines, True

def apply_fixes(content):
    fixes_applied = []
    lines = content.split('\n')
    
    # ============================================================
    # Fix 0: 版本号 v55 → v56
    # ============================================================
    old_count = content.count('v55')
    
    # 替换所有v55为v56（但要小心不要替换其他地方的v55）
    # 只替换标题和版本显示中的v55
    content = content.replace(
        '厂检调试记录单 V2 v55',
        '厂检调试记录单 V2 v56'
    )
    content = content.replace(
        '厂检调试记录单V2 v55',
        '厂检调试记录单V2 v56'
    )
    content = content.replace(
        "task.model ? task.model + ' · v55' : '厂检调试记录单V2 v55'",
        "task.model ? task.model + ' · v56' : '厂检调试记录单V2 v56'"
    )
    
    lines = content.split('\n')
    fixes_applied.append(f'版本号 v55→v56')
    
    # ============================================================
    # Fix 1: 电梯列表页打印按钮层级问题
    # ============================================================
    
    # 添加CSS
    old_css = ".task-card:active{transform:scale(.98);}"
    new_css = ".task-card:active{transform:scale(.98);}\n.task-card.menu-open{z-index:100;}"
    
    if old_css in content:
        content = content.replace(old_css, new_css)
        fixes_applied.append('Fix 1: 添加task-card.menu-open z-index样式')
    else:
        fixes_applied.append('Fix 1: 未找到task-card:active样式')
    
    lines = content.split('\n')
    
    # 修改togglePrintMenu函数
    old_toggle = """function togglePrintMenu(index) {
  var menu = document.getElementById('printMenu_' + index);
  if (!menu) return;
  var isOpen = menu.classList.contains('show');
  closeAllPrintMenus();
  if (!isOpen) menu.classList.add('show');
}"""
    
    new_toggle = """function togglePrintMenu(index) {
  var menu = document.getElementById('printMenu_' + index);
  if (!menu) return;
  var isOpen = menu.classList.contains('show');
  closeAllPrintMenus();
  if (!isOpen) {
    menu.classList.add('show');
    var card = menu.closest('.task-card');
    if (card) card.classList.add('menu-open');
  }
}"""
    
    if old_toggle in content:
        content = content.replace(old_toggle, new_toggle)
        fixes_applied.append('Fix 1: 修改togglePrintMenu')
    else:
        fixes_applied.append('Fix 1: 未找到togglePrintMenu函数')
    
    lines = content.split('\n')
    
    # 修改closeAllPrintMenus函数
    old_close = """function closeAllPrintMenus() {
  var menus = document.querySelectorAll('.print-dropdown-menu');
  for (var i = 0; i < menus.length; i++) {
    menus[i].classList.remove('show');
  }
}"""
    
    new_close = """function closeAllPrintMenus() {
  var menus = document.querySelectorAll('.print-dropdown-menu');
  for (var i = 0; i < menus.length; i++) {
    menus[i].classList.remove('show');
    var card = menus[i].closest('.task-card');
    if (card) card.classList.remove('menu-open');
  }
}"""
    
    if old_close in content:
        content = content.replace(old_close, new_close)
        fixes_applied.append('Fix 1: 修改closeAllPrintMenus')
    else:
        fixes_applied.append('Fix 1: 未找到closeAllPrintMenus函数')
    
    lines = content.split('\n')
    
    # ============================================================
    # Fix 2 & 3: 打印副表按钮 & 按钮联动问题
    # ============================================================
    
    old_menu = """          '<div class="print-dropdown-menu" id="printMenu_' + i + '" onclick="event.stopPropagation();">' +
            '<div onclick="printNotice(' + i + ')">📋 打印通知单</div>' +
            '<div onclick="printCheckSheet(' + i + ')">📝 打印检查表</div>' +
            '<div onclick="printFubiao(' + i + ')">📊 打印副表</div>' +
          '</div>'"""
    
    new_menu = """          '<div class="print-dropdown-menu" id="printMenu_' + i + '" onclick="event.stopPropagation();">' +
            '<div onclick="event.stopPropagation();printNotice(' + i + ')">📋 打印通知单</div>' +
            '<div onclick="event.stopPropagation();printCheckSheet(' + i + ')">📝 打印检查表</div>' +
            '<div onclick="event.stopPropagation();printFubiao(' + i + ')">📊 打印副表</div>' +
          '</div>'"""
    
    if old_menu in content:
        content = content.replace(old_menu, new_menu)
        fixes_applied.append('Fix 2&3: 菜单项添加stopPropagation')
    else:
        fixes_applied.append('Fix 2&3: 未找到菜单项模板（可能已有）')
    
    lines = content.split('\n')
    
    # ============================================================
    # Fix 4: 项目列表页项目卡片上移
    # ============================================================
    
    old_proj = '<div id="projectList" class="task-list"></div>'
    new_proj = '<div id="projectList" class="task-list" style="padding-top:4px;"></div>'
    
    if old_proj in content:
        content = content.replace(old_proj, new_proj)
        fixes_applied.append('Fix 4: 项目列表页顶部padding减小')
    else:
        fixes_applied.append('Fix 4: 未找到projectList元素')
    
    lines = content.split('\n')
    
    # ============================================================
    # Fix 5: 电梯列表页项目信息上移
    # ============================================================
    
    old_task = '<div id="taskList" class="task-list"></div>'
    new_task = '<div id="taskList" class="task-list" style="padding-top:4px;"></div>'
    
    if old_task in content:
        content = content.replace(old_task, new_task)
        fixes_applied.append('Fix 5: 电梯列表页顶部padding减小')
    else:
        fixes_applied.append('Fix 5: 未找到taskList元素')
    
    lines = content.split('\n')
    
    # 减少项目信息卡片间距
    old_proj_info = "html += '<div style=\"background:#f0f7ff;border-radius:12px;padding:14px;margin-bottom:12px;border:1px solid #b3d8ff;\">';\n  html += '<div style=\"font-size:13px;font-weight:600;color:#1a3a6b;margin-bottom:8px;\">📋 项目信息</div>';"
    new_proj_info = "html += '<div style=\"background:#f0f7ff;border-radius:12px;padding:12px 14px;margin-bottom:8px;border:1px solid #b3d8ff;\">';\n  html += '<div style=\"font-size:13px;font-weight:600;color:#1a3a6b;margin-bottom:6px;\">📋 项目信息</div>';"
    
    if old_proj_info in content:
        content = content.replace(old_proj_info, new_proj_info)
        fixes_applied.append('Fix 5: 项目信息卡片间距减小')
    else:
        fixes_applied.append('Fix 5: 未找到项目信息卡片模板')
    
    lines = content.split('\n')
    
    # ============================================================
    # Fix 6: 滑动返回逻辑修正
    # ============================================================
    
    old_swipe = """    // 左滑 → 返回上一级
    var currentPage = getCurrentPage();
    if (currentPage === 'check') {
      // 检验页 → 电梯列表页
      if (typeof saveCurrentTask === 'function') saveCurrentTask();
      if (typeof goPage === 'function') goPage('taskList');
    } else if (currentPage === 'taskList') {
      // 电梯列表页 → 项目列表页
      if (typeof goPage === 'function') goPage('projectList');
    }"""
    
    new_swipe = """    // 左滑 → 返回上一级
    var currentPage = getCurrentPage();
    if (currentPage === 'check') {
      // 检验页：先判断当前检验项索引
      if (typeof currentZoneIndex !== 'undefined' && currentZoneIndex > 0) {
        // 不是第一个检验项 → 切换到上一个检验项
        if (typeof prevZone === 'function') prevZone();
      } else {
        // 第一个检验项 → 返回电梯列表页
        if (typeof saveCurrentTask === 'function') saveCurrentTask();
        if (typeof goPage === 'function') goPage('taskList');
      }
    } else if (currentPage === 'taskList') {
      // 电梯列表页 → 项目列表页
      if (typeof goPage === 'function') goPage('projectList');
    }"""
    
    if old_swipe in content:
        content = content.replace(old_swipe, new_swipe)
        fixes_applied.append('Fix 6: 修改滑动返回逻辑')
    else:
        fixes_applied.append('Fix 6: 未找到滑动返回代码')
    
    lines = content.split('\n')
    
    # ============================================================
    # Fix 7: 滑动切换加过渡动画 - 增强动画效果
    # ============================================================
    
    old_kf = """@keyframes slideInLeft {
  from { transform: translateX(40px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
@keyframes slideInRight {
  from { transform: translateX(-40px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}"""
    
    new_kf = """@keyframes slideInLeft {
  from { transform: translateX(30%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
@keyframes slideInRight {
  from { transform: translateX(-30%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}"""
    
    if old_kf in content:
        content = content.replace(old_kf, new_kf)
        fixes_applied.append('Fix 7: 增强滑动切换动画')
    else:
        fixes_applied.append('Fix 7: 未找到slide关键帧')
    
    lines = content.split('\n')
    
    # ============================================================
    # Fix 8: 副表二轿顶空间加判定结果显示
    # ============================================================
    
    # 用行替换方式
    s5_start_marker = "// ⑤轿顶空间 - 长宽高三个输入"
    s5_end_marker = "// ===== 底坑空间 ====="
    
    s5_replacement = [
        "  // ⑤轿顶空间 - 长宽高三个输入 + 判定结果",
        "  var s5L = parseFloat(att2.顶部空间.s5L) || 0;",
        "  var s5W = parseFloat(att2.顶部空间.s5W) || 0;",
        "  var s5H = parseFloat(att2.顶部空间.s5H) || 0;",
        "  var s5HasData = s5L > 0 && s5W > 0 && s5H > 0;",
        "  var s5Ok = s5HasData && (s5L >= 0.5 && s5W >= 0.6 && s5H >= 0.8);",
        "  var s5Color = s5HasData ? (s5Ok ? '#52c41a' : '#ff4d4f') : '#999';",
        "  var s5Text = s5HasData ? (s5Ok ? '✓合格' : '✕不合格') : '未判定';",
        "  html += '<div style=\"margin-bottom:8px;padding:8px;background:#fafafa;border-radius:6px;\">';",
        "  html += '<div style=\"display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;\">';",
        "  html += '<div style=\"font-size:12px;font-weight:600;color:#333;\">⑤轿顶空间 (≥0.5m×0.6m×0.8m)</div>';",
        "  html += '<div style=\"font-size:12px;font-weight:600;color:' + s5Color + ';\">' + s5Text + '</div>';",
        "  html += '</div>';",
        "  html += '<div style=\"display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;\">';",
        "  html += '<div><div style=\"font-size:10px;color:#666;\">长(m) ≥0.5</div>';",
        "  html += '<input type=\"text\" value=\"' + (att2.顶部空间.s5L||'') + '\" placeholder=\"m\" inputmode=\"decimal\" onfocus=\"cancelAttachRender()\" onblur=\"updateAtt2Top(\\'s5L\\',this.value)\" style=\"width:100%;border:1px solid #ddd;border-radius:4px;padding:5px;font-size:12px;text-align:center;\"></div>';",
        "  html += '<div><div style=\"font-size:10px;color:#666;\">宽(m) ≥0.6</div>';",
        "  html += '<input type=\"text\" value=\"' + (att2.顶部空间.s5W||'') + '\" placeholder=\"m\" inputmode=\"decimal\" onfocus=\"cancelAttachRender()\" onblur=\"updateAtt2Top(\\'s5W\\',this.value)\" style=\"width:100%;border:1px solid #ddd;border-radius:4px;padding:5px;font-size:12px;text-align:center;\"></div>';",
        "  html += '<div><div style=\"font-size:10px;color:#666;\">高(m) ≥0.8</div>';",
        "  html += '<input type=\"text\" value=\"' + (att2.顶部空间.s5H||'') + '\" placeholder=\"m\" inputmode=\"decimal\" onfocus=\"cancelAttachRender()\" onblur=\"updateAtt2Top(\\'s5H\\',this.value)\" style=\"width:100%;border:1px solid #ddd;border-radius:4px;padding:5px;font-size:12px;text-align:center;\"></div>';",
        "  html += '</div>';",
        "  html += '</div>';",
        "  ",
    ]
    
    lines, success = replace_between_lines(lines, s5_start_marker, s5_end_marker, s5_replacement, include_end=False)
    if success:
        fixes_applied.append('Fix 8: 轿顶空间添加判定结果')
    else:
        fixes_applied.append('Fix 8: 未找到轿顶空间代码块')
    
    content = '\n'.join(lines)
    
    # ============================================================
    # Fix 9: 副表二底坑空间简化显示
    # ============================================================
    
    p5_start_marker = "// ⑤底坑空间尺寸"
    p5_end_marker = "// 自动判定"
    
    p5_replacement = [
        "  // ⑤底坑空间尺寸（简化版：长宽高 + 判定结果）",
        "  var p5L = parseFloat(att2.底坑空间.p5L) || 0;",
        "  var p5W = parseFloat(att2.底坑空间.p5W) || 0;",
        "  var p5H = parseFloat(att2.底坑空间.p5H) || 0;",
        "  var p5HasData = p5L > 0 && p5W > 0 && p5H > 0;",
        "  var p5Ok = p5HasData && (p5L >= 0.5 && p5W >= 0.6 && p5H >= 1.0);",
        "  var p5Color = p5HasData ? (p5Ok ? '#52c41a' : '#ff4d4f') : '#999';",
        "  var p5Text = p5HasData ? (p5Ok ? '✓合格' : '✕不合格') : '未判定';",
        "",
        "  html += '<div style=\"margin-bottom:8px;padding:8px;background:#fafafa;border-radius:6px;\">';",
        "  html += '<div style=\"display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;\">';",
        "  html += '<div style=\"font-size:12px;font-weight:600;color:#333;\">⑤底坑空间尺寸 (≥0.5m×0.6m×1.0m)</div>';",
        "  html += '<div style=\"font-size:12px;font-weight:600;color:' + p5Color + ';\">' + p5Text + '</div>';",
        "  html += '</div>';",
        "  html += '<div style=\"display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;\">';",
        "  html += '<div><div style=\"font-size:10px;color:#666;\">长(m) ≥0.5</div>';",
        "  html += '<input type=\"text\" value=\"' + (att2.底坑空间.p5L||'') + '\" placeholder=\"m\" inputmode=\"decimal\" onfocus=\"cancelAttachRender()\" onblur=\"updateAtt2Pit(\\'p5L\\',this.value)\" style=\"width:100%;border:1px solid #ddd;border-radius:4px;padding:5px;font-size:12px;text-align:center;\"></div>';",
        "  html += '<div><div style=\"font-size:10px;color:#666;\">宽(m) ≥0.6</div>';",
        "  html += '<input type=\"text\" value=\"' + (att2.底坑空间.p5W||'') + '\" placeholder=\"m\" inputmode=\"decimal\" onfocus=\"cancelAttachRender()\" onblur=\"updateAtt2Pit(\\'p5W\\',this.value)\" style=\"width:100%;border:1px solid #ddd;border-radius:4px;padding:5px;font-size:12px;text-align:center;\"></div>';",
        "  html += '<div><div style=\"font-size:10px;color:#666;\">高(m) ≥1.0</div>';",
        "  html += '<input type=\"text\" value=\"' + (att2.底坑空间.p5H||'') + '\" placeholder=\"m\" inputmode=\"decimal\" onfocus=\"cancelAttachRender()\" onblur=\"updateAtt2Pit(\\'p5H\\',this.value)\" style=\"width:100%;border:1px solid #ddd;border-radius:4px;padding:5px;font-size:12px;text-align:center;\"></div>';",
        "  html += '</div>';",
        "  html += '</div>';",
        "  ",
    ]
    
    lines, success = replace_between_lines(lines, p5_start_marker, p5_end_marker, p5_replacement, include_end=False)
    if success:
        fixes_applied.append('Fix 9: 底坑空间尺寸简化显示')
    else:
        fixes_applied.append('Fix 9: 未找到底坑空间尺寸代码块')
    
    content = '\n'.join(lines)
    
    # ============================================================
    # Fix 10: 检验页面菜单移除打印功能
    # ============================================================
    
    old_check_menu = """      <div onclick="saveCurrentTask();goPage('taskList');closeHeaderMenu('check')">📋 返回列表</div>
      <div onclick="showNewCheck();closeHeaderMenu('check')">➕ 新建</div>
      <div onclick="printCheckSheet(currentTaskIndex);closeHeaderMenu('check')">📝 打印检查表</div>
      <div onclick="printFubiao(currentTaskIndex);closeHeaderMenu('check')">📊 打印副表</div>"""
    
    new_check_menu = """      <div onclick="saveCurrentTask();goPage('taskList');closeHeaderMenu('check')">📋 返回列表</div>
      <div onclick="showNewCheck();closeHeaderMenu('check')">➕ 新建</div>"""
    
    if old_check_menu in content:
        content = content.replace(old_check_menu, new_check_menu)
        fixes_applied.append('Fix 10: 检验页菜单移除打印选项')
    else:
        fixes_applied.append('Fix 10: 未找到检验页菜单')
    
    lines = content.split('\n')
    
    # ============================================================
    # Fix 11: 确认电梯列表页打印副表是最新版空间尺寸副表
    # ============================================================
    
    if 'exportFubiaoPDF()' in content and 'buildFubiaoPage1' in content and 'buildFubiaoPage2' in content:
        fixes_applied.append('Fix 11: 确认副表使用最新buildFubiaoPage1/2')
    else:
        fixes_applied.append('Fix 11: 警告-未找到新副表生成函数')
    
    return content, fixes_applied

def main():
    file_path = 'factory-inspection-v2.html'
    backup_path = 'factory-inspection-v2.html.bak'
    
    # 读取文件
    content = read_file(file_path)
    print(f'原始文件大小: {len(content)} 字节')
    
    # 备份
    write_file(backup_path, content)
    print(f'已备份到: {backup_path}')
    
    # 应用修复
    content, fixes = apply_fixes(content)
    print('\n===== 修复清单 =====')
    for i, fix in enumerate(fixes, 1):
        print(f'{i}. {fix}')
    
    # 写入文件
    write_file(file_path, content)
    print(f'\n修改后文件大小: {len(content)} 字节')
    
    # 验证JS语法
    print('\n===== JS语法验证 =====')
    valid, msg = validate_js(content)
    if valid:
        print(f'✓ {msg}')
    else:
        print(f'✗ JS语法错误: {msg}')
        # 恢复备份
        write_file(file_path, read_file(backup_path))
        print('已恢复备份文件')
        sys.exit(1)
    
    # 同步到第二个文件
    file2 = '威特电梯厂检调试记录单v2.html'
    write_file(file2, content)
    print(f'\n已同步到: {file2}')
    
    # 验证两个文件一致
    c1 = read_file(file_path)
    c2 = read_file(file2)
    if c1 == c2:
        print('✓ 两个文件完全一致')
    else:
        print('✗ 两个文件不一致！')
    
    print('\n===== 完成 =====')

if __name__ == '__main__':
    main()
