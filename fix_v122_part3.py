#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v122 修复 - 第3部分：完善签名体系重构
"""
import re

FILE = '/app/data/所有对话/主对话/weite-pro-temp/factory-inspection-v2.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)
changes = []

# ============================================================
# Fix 1: openClientSignature() - 添加canvas初始化，使用户可以在甲方签字弹窗中绘制
# ============================================================
old = """// 甲方签字（项目级）- 从电梯列表菜单调用
function openClientSignature() {
  window._signMode = 'client';
  openMoModal('moSign');
  var header = document.querySelector('#moSign .mh h3');
  if (header) header.textContent = '甲方签字';
  var proj = getCurrentProject();
  if (!proj) return;
  if (!proj.clientSignature) proj.clientSignature = {};
  
  // 填充姓名
  document.getElementById('signBuilderName').value = proj.clientSignature.name || '';
  document.getElementById('signInspectorName').value = '';
  
  // 清除画布并恢复签名
  var cBuilder = document.getElementById('sigCanvasBuilder');
  var cInspector = document.getElementById('sigCanvasInspector');
  if (cBuilder) {
    var ctx = cBuilder.getContext('2d');
    ctx.clearRect(0, 0, cBuilder.width, cBuilder.height);
    if (proj.clientSignature.sig) {
      var img = new Image();
      img.onload = function() { ctx.drawImage(img, 0, 0); };
      img.src = proj.clientSignature.sig;
    }
  }
  if (cInspector) {
    var ctx2 = cInspector.getContext('2d');
    ctx2.clearRect(0, 0, cInspector.width, cInspector.height);
  }
}"""

new = """// 甲方签字（项目级）- 从电梯列表菜单调用
function openClientSignature() {
  window._signMode = 'client';
  openMoModal('moSign');
  var header = document.querySelector('#moSign .mh h3');
  if (header) header.textContent = '甲方签字';
  // 修改标签为甲方签字
  var labels = document.querySelectorAll('#moSign label');
  if (labels && labels[0]) labels[0].textContent = '甲方单位签字';
  if (labels && labels[1]) labels[1].style.display = 'none';
  var inspectorRow = document.getElementById('signInspectorName');
  if (inspectorRow) inspectorRow.parentElement.style.display = 'none';
  var proj = getCurrentProject();
  if (!proj) return;
  if (!proj.clientSignature) proj.clientSignature = {};
  
  // 填充姓名
  document.getElementById('signBuilderName').value = proj.clientSignature.name || '';
  document.getElementById('signInspectorName').value = '';
  
  // 初始化画布（使支持绘制）
  setTimeout(function() {
    initSigCanvasFor('Builder');
    initSigCanvasFor('Inspector');
    // 恢复甲方签名
    if (proj.clientSignature.sig) {
      var cBuilder = document.getElementById('sigCanvasBuilder');
      if (cBuilder) {
        var ctx = cBuilder.getContext('2d');
        var img = new Image();
        img.onload = function() { ctx.drawImage(img, 0, 0, cBuilder.width, cBuilder.height); };
        img.src = proj.clientSignature.sig;
      }
    }
  }, 300);
}"""

if old in content:
    content = content.replace(old, new)
    changes.append("Fix 1: openClientSignature() 添加canvas初始化 + 隐藏检验人员行")
else:
    # Try to find with different formatting
    print("WARNING: Fix 1 pattern not found exactly, trying alternative...")
    # Check if already modified
    if 'initSigCanvasFor' in content[content.find('openClientSignature'):content.find('openClientSignature')+1500]:
        changes.append("Fix 1: openClientSignature() - already has canvas init (SKIP)")
    else:
        print("ERROR: Could not find openClientSignature function pattern")

# ============================================================
# Fix 2: saveSignatures() - 支持甲方签字模式，保存到project.clientSignature
# ============================================================
old_save = """function saveSignatures() {
  var task = getCurrentTask();
  if (!task) return;
  if (!task.signatures) task.signatures = {};
  task.signatures.builderName = document.getElementById('signBuilderName').value;
  var inspectorName = document.getElementById('signInspectorName').value;
  task.signatures.inspectorName = inspectorName;
  var cBuilder = document.getElementById('sigCanvasBuilder');
  var cInspector = document.getElementById('sigCanvasInspector');
  task.signatures.builderSig = cBuilder.toDataURL('image/png');
  var inspectorSigData = cInspector.toDataURL('image/png');
  task.signatures.inspectorSig = inspectorSigData;
  // 检验人员签名持久化到localStorage（签一次，所有项目复用）
  if (inspectorName && inspectorSigData) {
    saveInspectorSignature(inspectorName, inspectorSigData);
  }
  saveProjects();
  closeMoModal('moSign');
  showToast('签字已保存');
}"""

new_save = """function saveSignatures() {
  // 甲方签字模式：保存到项目级clientSignature
  if (window._signMode === 'client') {
    var proj = getCurrentProject();
    if (!proj) return;
    if (!proj.clientSignature) proj.clientSignature = {};
    proj.clientSignature.name = document.getElementById('signBuilderName').value || '';
    var cBuilder = document.getElementById('sigCanvasBuilder');
    if (cBuilder) {
      proj.clientSignature.sig = cBuilder.toDataURL('image/png');
    }
    saveProjects();
    closeMoModal('moSign');
    window._signMode = '';
    // 恢复检验人员行显示
    var labels = document.querySelectorAll('#moSign label');
    if (labels && labels[1]) labels[1].style.display = '';
    var inspectorRow = document.getElementById('signInspectorName');
    if (inspectorRow) inspectorRow.parentElement.style.display = '';
    showToast('甲方签字已保存');
    return;
  }
  var task = getCurrentTask();
  if (!task) return;
  if (!task.signatures) task.signatures = {};
  task.signatures.builderName = document.getElementById('signBuilderName').value;
  var inspectorName = document.getElementById('signInspectorName').value;
  task.signatures.inspectorName = inspectorName;
  var cBuilder = document.getElementById('sigCanvasBuilder');
  var cInspector = document.getElementById('sigCanvasInspector');
  task.signatures.builderSig = cBuilder.toDataURL('image/png');
  var inspectorSigData = cInspector.toDataURL('image/png');
  task.signatures.inspectorSig = inspectorSigData;
  // 检验人员签名持久化到localStorage（签一次，所有项目复用）
  if (inspectorName && inspectorSigData) {
    saveInspectorSignature(inspectorName, inspectorSigData);
  }
  saveProjects();
  closeMoModal('moSign');
  showToast('签字已保存');
}"""

if old_save in content:
    content = content.replace(old_save, new_save)
    changes.append("Fix 2: saveSignatures() 添加甲方签字模式（保存到project.clientSignature）")
else:
    if 'window._signMode' in content[content.find('function saveSignatures'):content.find('function saveSignatures')+500]:
        changes.append("Fix 2: saveSignatures() - already has client mode support (SKIP)")
    else:
        print("ERROR: Could not find saveSignatures function pattern")

# ============================================================
# Fix 3: 确保关闭moSign弹窗时重置_signMode和UI状态
# ============================================================
# Find closeMoModal function and add reset
old_close = """function closeMoModal(id) {
  document.getElementById(id).style.display = 'none';
}"""

new_close = """function closeMoModal(id) {
  document.getElementById(id).style.display = 'none';
  // 重置甲方签字模式的UI状态
  if (id === 'moSign' && window._signMode === 'client') {
    window._signMode = '';
    var labels = document.querySelectorAll('#moSign label');
    if (labels && labels[1]) labels[1].style.display = '';
    var inspectorRow = document.getElementById('signInspectorName');
    if (inspectorRow) inspectorRow.parentElement.style.display = '';
  }
}"""

if old_close in content:
    content = content.replace(old_close, new_close)
    changes.append("Fix 3: closeMoModal() 关闭时重置甲方签字模式UI状态")
else:
    # Try alternate pattern
    pattern = r"function closeMoModal\(id\) \{\s*document\.getElementById\(id\)\.style\.display = 'none';\s*\}"
    if re.search(pattern, content):
        content = re.sub(pattern, new_close.replace('\\', '\\\\'), content)
        changes.append("Fix 3: closeMoModal() 关闭时重置甲方签字模式UI状态 (regex)")
    elif '_signMode' in content[content.find('closeMoModal'):content.find('closeMoModal')+300]:
        changes.append("Fix 3: closeMoModal() - already has mode reset (SKIP)")
    else:
        print("WARNING: Could not find closeMoModal function pattern")

# ============================================================
# Fix 4: 项目列表页添加"厂检签字"菜单项（全局检验人员签名设置入口）
# ============================================================
old_menu = """      <div class="header-dropdown" id="headerDropdownMain" style="top:100%;right:0;">
        <div onclick="showNewProject();closeHeaderMenu('main')">➕ 新建项目</div>
      </div>"""

new_menu = """      <div class="header-dropdown" id="headerDropdownMain" style="top:100%;right:0;">
        <div onclick="showNewProject();closeHeaderMenu('main')">➕ 新建项目</div>
        <div onclick="openInspectorSigSetting();closeHeaderMenu('main')">✍️ 厂检签字</div>
      </div>"""

if old_menu in content:
    content = content.replace(old_menu, new_menu)
    changes.append("Fix 4: 项目列表页添加'厂检签字'菜单项")
else:
    if 'openInspectorSigSetting' in content[content.find('headerDropdownMain'):content.find('headerDropdownMain')+500]:
        changes.append("Fix 4: 项目列表页 - 已有厂检签字菜单 (SKIP)")
    else:
        print("WARNING: Could not find project list menu pattern")

# ============================================================
# 写回文件
# ============================================================
with open(FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n===== 修复完成 =====")
print(f"原始长度: {original_len}")
print(f"修改后长度: {len(content)}")
print(f"\n应用的修改:")
for c in changes:
    print(f"  ✓ {c}")
print(f"\n共 {len(changes)} 项修改")
