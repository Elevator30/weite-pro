#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v121 第二批修复 - 修复第一批中未成功替换的部分
"""

import re

MAIN_FILE = '/app/data/所有对话/主对话/weite-pro-temp/factory-inspection-v2.html'

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    content = read_file(MAIN_FILE)
    original_len = len(content)
    
    # ============================================================
    # Issue 5 (fix): id114判定块修复
    # ============================================================
    print("=== Issue 5 修复: id114门间隙判定 ===")
    
    old_id114 = """  // id114: 门间隙
  if (hasDoorGapData) {
    task.checks[114].s = doorGapOk ? 'ok' : 'ng';
    if (!doorGapOk) task.checks[114].n = '门间隙不符合标准';
  }"""
    
    new_id114 = """  // id114: 门间隙（包含门扇间隙和门扇间施力间隙）
  if (hasDoorGapData || hasForceGapData) {
    if (!task.checks[114]) task.checks[114] = {};
    var gapAllOk = doorGapOk && forceGapOk;
    task.checks[114].s = gapAllOk ? 'ok' : 'ng';
    var ngMsgs = [];
    if (!doorGapOk) ngMsgs.push('门间隙不符合标准');
    if (!forceGapOk) ngMsgs.push('门扇间施力间隙超过' + forceGapStd + 'mm');
    if (!gapAllOk) task.checks[114].n = ngMsgs.join('；');
  }"""
    
    if old_id114 in content:
        content = content.replace(old_id114, new_id114, 1)
        print("  - 修复id114门间隙判定逻辑（含施力间隙）")
    else:
        print("  - WARNING: 仍未找到id114判定块，检查上下文...")
        # 用正则搜索
        pattern = r"  // id114: 门间隙\s*\n  if \(hasDoorGapData\) \{\s*\n    task\.checks\[114\]\.s = doorGapOk \? 'ok' : 'ng';\s*\n    if \(!doorGapOk\) task\.checks\[114\]\.n = '门间隙不符合标准';\s*\n  \}"
        match = re.search(pattern, content)
        if match:
            content = content.replace(match.group(0), new_id114, 1)
            print("  - (正则) 修复id114门间隙判定")
    
    # ============================================================
    # Issue 8 (fix): createTask中添加notes初始化
    # ============================================================
    print("\n=== Issue 8 修复: createTask添加notes ===")
    
    # 在task对象的conclusion后添加notes
    old_task_end = """    conclusion: '',
    rectifyDeadline: '',
    projectManagerSign: '',"""
    
    new_task_end = """    conclusion: '',
    notes: [],
    rectifyDeadline: '',
    projectManagerSign: '',"""
    
    if old_task_end in content:
        content = content.replace(old_task_end, new_task_end, 1)
        print("  - 在createTask中添加notes: []")
    else:
        print("  - WARNING: 未找到createTask的conclusion行")
    
    # 同时在copyTask中也添加notes
    old_copy_sig = "  newTask.signatures = {};"
    new_copy_sig = "  newTask.signatures = {};\n  newTask.notes = [];"
    if old_copy_sig in content:
        content = content.replace(old_copy_sig, new_copy_sig, 1)
        print("  - 在copyTask中添加notes初始化")
    
    # ============================================================
    # Issue 8 (fix): renderSignZoneContent调用处添加备注渲染
    # ============================================================
    print("\n=== Issue 8 修复: 签字区域渲染备注 ===")
    
    old_sign_call = """  // 签字确认页
  if (index === 6) {
    renderSignZoneContent(container);
    return;
  }"""
    
    new_sign_call = """  // 签字确认页
  if (index === 6) {
    renderNotesAndSign(container);
    return;
  }"""
    
    if old_sign_call in content:
        content = content.replace(old_sign_call, new_sign_call, 1)
        print("  - 修改签字区域调用为renderNotesAndSign")
    else:
        print("  - WARNING: 未找到签字区域调用")
    
    # 添加renderNotesAndSign函数（在renderSignZoneContent函数之前）
    old_render_sign_func = "function renderSignZoneContent(container) {"
    
    new_render_notes_sign = """function renderNotesAndSign(container) {
  var task = getCurrentTask();
  if (!task) return;
  
  var html = '';
  // 备注区域
  html += '<div class="notes-section">';
  html += '<div class="notes-title">📝 备注 <button class="notes-add-btn" onclick="addNote()">+ 添加备注</button></div>';
  
  if (!task.notes || task.notes.length === 0) {
    html += '<div style="text-align:center;color:#aaa;font-size:12px;padding:20px 0;">暂无备注</div>';
  } else {
    task.notes.forEach(function(note, idx) {
      html += '<div class="note-item">';
      html += '<div class="note-item-header"><span class="note-item-title">备注' + (idx + 1) + '</span><span class="note-item-del" onclick="deleteNote(' + idx + ')">删除</span></div>';
      html += '<textarea placeholder="输入备注内容..." onchange="updateNote(' + idx + ', this.value)">' + (note.content || '') + '</textarea>';
      html += '</div>';
    });
  }
  html += '</div>';
  
  container.innerHTML = html;
  
  // 渲染签字区域（追加）
  var signDiv = document.createElement('div');
  renderSignZoneContent(signDiv);
  container.appendChild(signDiv);
}

""" + old_render_sign_func
    
    if old_render_sign_func in content:
        content = content.replace(old_render_sign_func, new_render_notes_sign, 1)
        print("  - 添加renderNotesAndSign函数")
    else:
        print("  - WARNING: 未找到renderSignZoneContent函数定义")
    
    # ============================================================
    # Issue 9 (fix): sub-accordion添加id
    # ============================================================
    print("\n=== Issue 9 修复: sub-accordion添加id ===")
    
    old_sub_acc = """      html += '<div class="sub-accordion">';
      html += '<div class="sub-header-sticky" style="background:' + region.color + ';" onclick="toggleSubGroup(' + index + ',' + gi + ')">';"""
    
    new_sub_acc = """      html += '<div class="sub-accordion" id="subGroup_' + index + '_' + gi + '">';
      html += '<div class="sub-header-sticky" style="background:' + region.color + ';" onclick="toggleSubGroup(' + index + ',' + gi + ')">';"""
    
    if old_sub_acc in content:
        content = content.replace(old_sub_acc, new_sub_acc, 1)
        print("  - 为sub-accordion添加id属性")
    else:
        print("  - WARNING: 仍未找到sub-accordion渲染位置")
        # 用正则搜索
        pattern = r"html \+= '<div class=\"sub-accordion\">';\s*\n\s*html \+= '<div class=\"sub-header-sticky\""
        match = re.search(pattern, content)
        if match:
            # 用更精确的替换
            content = re.sub(
                r"(html \+= '<div class=\"sub-accordion\">')(\s*\n\s*html \+= '<div class=\"sub-header-sticky\" onclick=\"toggleSubGroup\()",
                r"html += '<div class=\"sub-accordion\" id=\"subGroup_' + index + '_' + gi + '\">'\2",
                content,
                count=1
            )
            print("  - (正则) 为sub-accordion添加id")
    
    # ============================================================
    # 额外修复：确保toggleSubGroup中的变量名正确
    # ============================================================
    print("\n=== 额外检查: toggleSubGroup函数 ===")
    
    # 检查toggleSubGroup中是否有isCurrentlyExpanded变量
    if "isCurrentlyExpanded" in content and "toggleSubGroup" in content:
        print("  - isCurrentlyExpanded变量存在 ✓")
    
    # 检查subGroup_前缀是否一致
    if "subGroup_" in content and "getElementById('subGroup_'" in content:
        print("  - subGroup_ id前缀一致 ✓")
    
    # ============================================================
    # 保存
    # ============================================================
    write_file(MAIN_FILE, content)
    
    print(f"\n=== 完成 ===")
    print(f"主文件: {original_len} -> {len(content)} 字节 (变化: {len(content)-original_len:+d})")

if __name__ == '__main__':
    main()
