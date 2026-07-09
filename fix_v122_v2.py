#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v122 修复12项问题脚本 - 修复版
"""

import os
import re
import shutil

BASE_DIR = '/app/data/所有对话/主对话/weite-pro-temp'
MAIN_FILE = os.path.join(BASE_DIR, 'factory-inspection-v2.html')
PRINT_FILE = os.path.join(BASE_DIR, 'print-fubiao.html')
CN_FILE = os.path.join(BASE_DIR, '威特电梯厂检调试记录单v2.html')

def read_file(p):
    with open(p, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(p, content):
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)

# Backup first
shutil.copy2(MAIN_FILE, MAIN_FILE + '.bak_v121')
shutil.copy2(PRINT_FILE, PRINT_FILE + '.bak_v121')

content = read_file(MAIN_FILE)
print_content = read_file(PRINT_FILE)

fixes_applied = []

def apply_fix(name, old, new, target='main'):
    global content, print_content
    src = content if target == 'main' else print_content
    if old in src:
        new_src = src.replace(old, new, 1)
        if target == 'main':
            content = new_src
        else:
            print_content = new_src
        fixes_applied.append(f'  [OK] {name}')
        return True
    else:
        fixes_applied.append(f'  [SKIP] {name} - 未找到匹配文本')
        return False

# ============================================================
# Issue 1: 附表1门结构UI调整
# ============================================================
old1 = '''  // 门结构切换 + 门类型选择（同一行）
  var doorStruct = att1.doorStructure || 'center';
  html += '<div style="display:flex;gap:10px;margin-bottom:12px;align-items:stretch;">';
  // 左：中分门/旁开门按钮
  html += '<div style="flex:0 0 auto;display:flex;gap:6px;">';
  html += '<div onclick="setAtt1DoorStructure(&#39;center&#39;)" style="padding:0 16px;display:flex;align-items:center;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;transition:all 0.2s;border:1.5px solid ' + (doorStruct === 'center' ? '#667eea' : '#e2e8f0') + ';background:' + (doorStruct === 'center' ? 'linear-gradient(135deg,#667eea,#764ba2)' : '#fff') + ';color:' + (doorStruct === 'center' ? '#fff' : '#718096') + ';">中分门</div>';
  html += '<div onclick="setAtt1DoorStructure(&#39;side&#39;)" style="padding:0 16px;display:flex;align-items:center;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;transition:all 0.2s;border:1.5px solid ' + (doorStruct === 'side' ? '#667eea' : '#e2e8f0') + ';background:' + (doorStruct === 'side' ? 'linear-gradient(135deg,#667eea,#764ba2)' : '#fff') + ';color:' + (doorStruct === 'side' ? '#fff' : '#718096') + ';">旁开门</div>';
  html += '</div>';
  // 右：门类型下拉
  html += '<div class="fr" style="flex:1;display:flex;align-items:center;"><label style="flex-shrink:0;">门类型</label><select id="att1DoorType" onchange="changeAtt1DoorType(this.value)" style="flex:1;border:1px solid #ddd;border-radius:6px;padding:10px;font-size:14px;min-width:0;">';'''

new1 = '''  // 门类型标签 + 门结构切换 + 门类型下拉（同一行紧凑布局）
  var doorStruct = att1.doorStructure || 'center';
  html += '<div style="display:flex;gap:8px;margin-bottom:12px;align-items:center;">';
  // 门类型文字标签
  html += '<label style="flex-shrink:0;font-size:13px;font-weight:600;color:#333;">门类型</label>';
  // 中分门/旁开门按钮（紧凑样式，高度和下拉框一致）
  html += '<div style="flex:0 0 auto;display:flex;gap:4px;">';
  html += '<div onclick="setAtt1DoorStructure(&#39;center&#39;)" style="padding:0 12px;height:36px;display:flex;align-items:center;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.2s;border:1.5px solid ' + (doorStruct === 'center' ? '#667eea' : '#e2e8f0') + ';background:' + (doorStruct === 'center' ? 'linear-gradient(135deg,#667eea,#764ba2)' : '#fff') + ';color:' + (doorStruct === 'center' ? '#fff' : '#718096') + ';box-sizing:border-box;">中分门</div>';
  html += '<div onclick="setAtt1DoorStructure(&#39;side&#39;)" style="padding:0 12px;height:36px;display:flex;align-items:center;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.2s;border:1.5px solid ' + (doorStruct === 'side' ? '#667eea' : '#e2e8f0') + ';background:' + (doorStruct === 'side' ? 'linear-gradient(135deg,#667eea,#764ba2)' : '#fff') + ';color:' + (doorStruct === 'side' ? '#fff' : '#718096') + ';box-sizing:border-box;">旁开门</div>';
  html += '</div>';
  // 门类型下拉框（和按钮同高）
  html += '<select id="att1DoorType" onchange="changeAtt1DoorType(this.value)" style="flex:1;height:36px;border:1px solid #ddd;border-radius:6px;padding:0 8px;font-size:13px;min-width:0;box-sizing:border-box;">';'''

apply_fix('Issue 1: 附表1门结构UI调整', old1, new1)

# ============================================================
# Issue 2: 附表1弹窗布局 - 确保门结构div正确闭合
# 检查并修复 '</select></div>' 的闭合
# ============================================================
old2 = "  html += '</select></div>';\n  \n  if (currentAtt1Door === 'laygate') {"
new2 = "  html += '</select>';\n  html += '</div>';\n  \n  if (currentAtt1Door === 'laygate') {"

apply_fix('Issue 2: 附表1门类型下拉闭合标签修正', old2, new2)

# ============================================================
# Issue 3: 手风琴滚动偏移量 60 -> 100
# ============================================================
old3 = 'var headerOffset = 60; // 顶部导航栏高度'
new3 = 'var headerOffset = 100; // 顶部导航栏高度'
apply_fix('Issue 3: 手风琴滚动偏移量60->100', old3, new3)

# ============================================================
# Issue 4: 点击符合/不符合时页面抖动 - 保存恢复滚动位置
# ============================================================
old4 = '''function setCheckStatus(id, status) {
  var task = getCurrentTask();
  if (!task) return;
  if (!task.checks[id]) task.checks[id] = {};
  var c = task.checks[id];
  
  // Toggle: if clicking same status, deselect
  if (c.s === status) {
    c.s = '';
  } else {
    c.s = status;
  }
  
  // If switching away from NG, clean up NG fields but keep them in data
  saveCurrentTask();
  renderZoneContent(currentZoneIndex);
  renderZoneTabs();
  updateProgress();
}'''

new4 = '''function setCheckStatus(id, status) {
  // 保存滚动位置，防止重渲染导致页面抖动
  var savedScrollTop = window.pageYOffset || document.documentElement.scrollTop;
  var task = getCurrentTask();
  if (!task) return;
  if (!task.checks[id]) task.checks[id] = {};
  var c = task.checks[id];
  
  // Toggle: if clicking same status, deselect
  if (c.s === status) {
    c.s = '';
  } else {
    c.s = status;
  }
  
  // If switching away from NG, clean up NG fields but keep them in data
  saveCurrentTask();
  renderZoneContent(currentZoneIndex);
  renderZoneTabs();
  updateProgress();
  // 恢复滚动位置，消除抖动
  window.scrollTo(0, savedScrollTop);
}'''

apply_fix('Issue 4: 符合/不符合按钮页面抖动修复', old4, new4)

# ============================================================
# Issue 5: 附表2第⑤项检验结果 (print-fubiao.html)
# ============================================================
# 顶部空间 s5 结果
old5a = '''  // 轿顶空间尺寸
  setFb2Text('top-s5-space', (top.s5L || '') + '×' + (top.s5W || '') + '×' + (top.s5H || ''));
  
  // 底坑空间'''

new5a = '''  // 轿顶空间尺寸
  setFb2Text('top-s5-space', (top.s5L || '') + '×' + (top.s5W || '') + '×' + (top.s5H || ''));
  // 轿顶空间检验结果
  var _s5L = parseFloat(top.s5L) || 0;
  var _s5W = parseFloat(top.s5W) || 0;
  var _s5H = parseFloat(top.s5H) || 0;
  if (_s5L > 0 && _s5W > 0 && _s5H > 0) {
    setFb2Text('top-s5-result', (_s5L >= 0.5 && _s5W >= 0.6 && _s5H >= 0.8) ? '符合' : '不符合');
  }
  
  // 底坑空间'''

apply_fix('Issue 5a: 附表2顶部空间第⑤项检验结果', old5a, new5a, 'print')

# 底坑空间 p5 结果
old5b = '''  // 轿底空间尺寸
  setFb2Text('pit-p5-space', (pit.p5L || '') + '×' + (pit.p5W || '') + '×' + (pit.p5H || ''));
  
  // 计算顶部空间检验结果'''

new5b = '''  // 轿底空间尺寸
  setFb2Text('pit-p5-space', (pit.p5L || '') + '×' + (pit.p5W || '') + '×' + (pit.p5H || ''));
  // 轿底空间检验结果
  var _p5L = parseFloat(pit.p5L) || 0;
  var _p5W = parseFloat(pit.p5W) || 0;
  var _p5H = parseFloat(pit.p5H) || 0;
  if (_p5L > 0 && _p5W > 0 && _p5H > 0) {
    setFb2Text('pit-p5-result', (_p5L >= 0.5 && _p5W >= 0.6 && _p5H >= 1.0) ? '符合' : '不符合');
  }
  
  // 计算顶部空间检验结果'''

apply_fix('Issue 5b: 附表2底坑空间第⑤项检验结果', old5b, new5b, 'print')

# ============================================================
# Issue 6: 附表1层门打印-空楼层不显示楼层号
# ============================================================
old6 = '''  // 填充层门，最多16行（表格共18个数据行-2个轿门=16个层门）
  var maxLaygate = Math.min(laygate.length, 16);
  for (var i = 0; i < maxLaygate; i++) {
    var lg = laygate[i];
    fillFb1Row('laygate' + (i+1), lg.name || ((i+1) + '层'), lg.data || []);
  }
}'''

new6 = '''  // 填充层门，最多16行（表格共18个数据行-2个轿门=16个层门）
  var maxLaygate = Math.min(laygate.length, 16);
  for (var i = 0; i < maxLaygate; i++) {
    var lg = laygate[i];
    var dataArr = lg.data || [];
    var hasData = dataArr.some(function(v){ return v && v.trim(); });
    var floorName = hasData ? (lg.name || ((i+1) + '层')) : '';
    fillFb1Row('laygate' + (i+1), floorName, dataArr);
  }
}'''

apply_fix('Issue 6: 附表1打印空楼层不显示楼层号', old6, new6, 'print')

# ============================================================
# Issue 7: 附表1打印-第16层数字跑到第一列
# rowspan=18 改为 rowspan=19
# ============================================================
old7 = '<th rowspan="18" class="vertical-text">检验位置及测量数据</th>'
new7 = '<th rowspan="19" class="vertical-text">检验位置及测量数据</th>'
apply_fix('Issue 7: 附表1打印 rowspan 18->19', old7, new7, 'print')

# ============================================================
# Issue 8: 附表4最大偏差计算 - 改为最大绝对偏差
# ============================================================
old8 = '''function calcFaceDistMaxDev(rows, ref, key) {
  var refVal = parseFloat(ref) || 0;
  if (refVal <= 0) return { maxDev: '', hasNegative: false, hasData: false };
  
  var maxDev = -Infinity;
  var hasNegative = false;
  var hasData = false;
  
  rows.forEach(function(r) {
    var v = parseFloat(r[key]);
    if (!isNaN(v) && v > 0) {
      hasData = true;
      var dev = v - refVal;
      if (dev < 0) hasNegative = true;
      if (dev > maxDev) maxDev = dev;
    }
  });
  
  return {
    maxDev: hasData ? maxDev.toFixed(2) : '',
    hasNegative: hasNegative,
    hasData: hasData
  };
}'''

new8 = '''function calcFaceDistMaxDev(rows, ref, key) {
  var refVal = parseFloat(ref) || 0;
  if (refVal <= 0) return { maxDev: '', hasNegative: false, hasData: false };
  
  var maxAbsDev = 0;
  var maxPosDev = -Infinity;
  var hasNegative = false;
  var hasData = false;
  
  rows.forEach(function(r) {
    var v = parseFloat(r[key]);
    if (!isNaN(v) && v > 0) {
      hasData = true;
      var dev = v - refVal;
      if (dev < 0) hasNegative = true;
      if (dev > maxPosDev) maxPosDev = dev;
      var absDev = Math.abs(dev);
      if (absDev > maxAbsDev) maxAbsDev = absDev;
    }
  });
  
  return {
    maxDev: hasData ? maxAbsDev.toFixed(2) : '',
    maxPosDev: hasData ? maxPosDev.toFixed(2) : '',
    hasNegative: hasNegative,
    hasData: hasData
  };
}'''

apply_fix('Issue 8: 附表4最大偏差改为最大绝对偏差', old8, new8)

# ============================================================
# Issue 9: 备注新增后自动聚焦
# ============================================================
old9 = '''function addNote() {
  var task = getCurrentTask(); if (!task) return;
  if (!task.notes) task.notes = [];
  task.notes.push({content: ''});
  saveCurrentTask();
  var target = document.getElementById('notesSection');
  if (target) renderNotesSection(target);
  updateProgress();
}'''

new9 = '''function addNote() {
  var task = getCurrentTask(); if (!task) return;
  if (!task.notes) task.notes = [];
  task.notes.push({content: ''});
  saveCurrentTask();
  var target = document.getElementById('notesSection');
  if (target) renderNotesSection(target);
  updateProgress();
  // 新增备注后自动聚焦到新输入框（等待DOM渲染完成）
  setTimeout(function() {
    var noteTextareas = document.querySelectorAll('#notesSection textarea');
    if (noteTextareas && noteTextareas.length > 0) {
      noteTextareas[noteTextareas.length - 1].focus();
    }
  }, 60);
}'''

apply_fix('Issue 9: 备注新增后自动聚焦', old9, new9)

# ============================================================
# Issue 10: 签名体系重构
# ============================================================

# 10.1 全局检验人员签名 - 修改持久化key为WEITE_INSPECTOR_SIGNATURE
# Find the key variable
match10a = re.search(r"var PERSISTENT_SIG_KEY\s*=\s*'([^']+)'", content)
if match10a:
    old10a = match10a.group(0)
    new10a = "var PERSISTENT_SIG_KEY = 'WEITE_INSPECTOR_SIGNATURE'"
    content = content.replace(old10a, new10a, 1)
    fixes_applied.append('  [OK] Issue 10.1: 全局签名key改为WEITE_INSPECTOR_SIGNATURE')
else:
    fixes_applied.append('  [SKIP] Issue 10.1: 全局签名key - 未找到变量')

# 10.2 电梯列表页增加"甲方签字"菜单
old10b = '''      <div onclick="showNewCheck();closeHeaderMenu('task')">➕ 新建检查</div>
    </div>'''
new10b = '''      <div onclick="showNewCheck();closeHeaderMenu('task')">➕ 新建检查</div>
      <div onclick="openClientSignature();closeHeaderMenu('task')">✍️ 甲方签字</div>
    </div>'''
apply_fix('Issue 10.2: 电梯列表页加甲方签字入口', old10b, new10b)

# 10.2 添加 openClientSignature 函数
old10c = '// 签字确认标签页 — 点击签名按钮 → 弹出全屏签名弹窗'
new10c = '''// 甲方签字（项目级）- 从电梯列表菜单调用
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
}

// 签字确认标签页 — 点击签名按钮 → 弹出全屏签名弹窗'''
apply_fix('Issue 10.2: 添加openClientSignature函数', old10c, new10c)

# 10.2 修改 saveSignZone 支持甲方签字模式
old10d = '''function saveSignZone() {
  var task = getCurrentTask();
  if (!task) return;
  if (!task.signatures) task.signatures = {};
  task.signatures.builderName = document.getElementById('signBuilderName').value;
  var inspectorName = document.getElementById('signInspectorName').value;
  task.signatures.inspectorName = inspectorName;
  
  var cBuilder = document.getElementById('sigCanvasBuilder');
  var cInspector = document.getElementById('sigCanvasInspector');
  
  // 保存签名图片
  task.signatures.builderSig = cBuilder.toDataURL('image/png');
  task.signatures.inspectorSig = inspectorSigData;
  
  // 检验人员签名持久化到localStorage（签一次，所有项目复用）
  savePersistentInspectorSig(inspectorName, inspectorSigData);
  
  saveCurrentTask();
  closeMoModal('moSign');
  showToast('签名已保存');
  
  // 刷新签字确认标签页显示
  renderNotesAndSignSection();
}'''

new10d = '''function saveSignZone() {
  // 甲方签字模式：保存到当前项目
  if (window._signMode === 'client') {
    var proj = getCurrentProject();
    if (!proj) return;
    if (!proj.clientSignature) proj.clientSignature = {};
    proj.clientSignature.name = document.getElementById('signBuilderName').value;
    var cBuilder = document.getElementById('sigCanvasBuilder');
    proj.clientSignature.sig = cBuilder.toDataURL('image/png');
    saveProjects();
    closeMoModal('moSign');
    showToast('甲方签字已保存');
    window._signMode = '';
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
  
  // 保存签名图片
  task.signatures.builderSig = cBuilder.toDataURL('image/png');
  task.signatures.inspectorSig = inspectorSigData;
  
  // 检验人员签名持久化到localStorage（签一次，所有项目复用）
  savePersistentInspectorSig(inspectorName, inspectorSigData);
  
  saveCurrentTask();
  closeMoModal('moSign');
  showToast('签名已保存');
  
  // 刷新签字确认标签页显示
  renderNotesAndSignSection();
}'''

apply_fix('Issue 10.2: saveSignZone支持甲方签字模式', old10d, new10d)

# 设置检验人员签名模式
old10e = 'function openInspectorSigSetting() {\n  openMoModal(\'moSign\');'
new10e = '''function openInspectorSigSetting() {
  window._signMode = 'inspector';
  openMoModal('moSign');'''
apply_fix('Issue 10.1: openInspectorSigSetting设置模式', old10e, new10e)

# 设置电梯级签名模式
old10f = 'function openSignZoneModal(target) {\n  openMoModal(\'moSign\');'
new10f = '''function openSignZoneModal(target) {
  window._signMode = 'task';
  openMoModal('moSign');'''
apply_fix('Issue 10: openSignZoneModal设置模式', old10f, new10f)

# ============================================================
# Issue 11: "签字确认"改为"厂检结论"
# ============================================================

# 区域名称
old11a = "{name:'签字确认', color:'#e53e3e', ids:[]} // 签字与结论"
new11a = "{name:'厂检结论', color:'#e53e3e', ids:[]} // 签字与结论"
apply_fix('Issue 11a: 区域名称签字确认->厂检结论', old11a, new11a)

# 弹窗标题
old11b = '<div class="mh"><h3>签字确认</h3><button onclick="closeMoModal(\'moSign\')">×</button></div>'
new11b = '<div class="mh"><h3>厂检结论</h3><button onclick="closeMoModal(\'moSign\')">×</button></div>'
apply_fix('Issue 11b: 弹窗标题签字确认->厂检结论', old11b, new11b)

# 签字区域标题
old11c = 'html += \'<div style="font-size:15px;font-weight:700;margin-bottom:10px;color:#667eea;">签字确认</div>\';'
new11c = 'html += \'<div style="font-size:15px;font-weight:700;margin-bottom:10px;color:#667eea;">厂检结论</div>\';'

count_c = content.count(old11c)
if count_c > 0:
    content = content.replace(old11c, new11c)
    fixes_applied.append(f'  [OK] Issue 11c: 签字区域标题 (替换{count_c}处)')
else:
    fixes_applied.append('  [SKIP] Issue 11c: 签字区域标题 - 未找到')

# 副标题
old11d = 'html += \'<div style="font-size:13px;font-weight:600;margin-bottom:8px;">签字确认（项目管理人员/安装人员）</div>\';'
new11d = 'html += \'<div style="font-size:13px;font-weight:600;margin-bottom:8px;">相关人员签名</div>\';'
apply_fix('Issue 11d: 签字确认副标题', old11d, new11d)

# 检查页菜单中的"检验人员签名"改为"厂检签字"
old11e = '<div onclick="openInspectorSigSetting();closeHeaderMenu(\'check\')">✍️ 检验人员签名</div>'
new11e = '<div onclick="openInspectorSigSetting();closeHeaderMenu(\'check\')">✍️ 厂检签字</div>'
apply_fix('Issue 11e: 检查页菜单检验人员签名->厂检签字', old11e, new11e)

# ============================================================
# Issue 2 补充: 检查附表1测量数据表格是否正确渲染
# 查找renderAtt1LaygateInputs函数确保测量项都在
# ============================================================
# 检查是否有renderAtt1LaygateInputs函数
if 'renderAtt1LaygateInputs' in content:
    fixes_applied.append('  [OK] Issue 2: renderAtt1LaygateInputs函数存在')
else:
    fixes_applied.append('  [WARN] Issue 2: renderAtt1LaygateInputs函数不存在')

# ============================================================
# 保存文件
# ============================================================
write_file(MAIN_FILE, content)
write_file(PRINT_FILE, print_content)

# Issue 12: 复制中文文件名
shutil.copy2(MAIN_FILE, CN_FILE)
fixes_applied.append('  [OK] Issue 12: 中文文件名同步')

# 输出结果
print('=' * 60)
print('修复结果汇总：')
print('=' * 60)
for fix in fixes_applied:
    print(fix)
print('=' * 60)
print(f'主文件: {MAIN_FILE}')
print(f'打印文件: {PRINT_FILE}')
print(f'中文文件: {CN_FILE}')
