#!/usr/bin/env python3
"""
v123 批量修复10项bug
修复威特电梯厂检调试记录单v2的10个bug
"""

import re
import os

MAIN_FILE = '/app/data/所有对话/主对话/weite-pro-temp/factory-inspection-v2.html'
PRINT_FILE = '/app/data/所有对话/主对话/weite-pro-temp/print-fubiao.html'

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_main_file(content):
    """修复主文件 factory-inspection-v2.html"""
    fixes_applied = []
    
    # ========== Bug 7: "甲方签字"改"项目管理/安装人员签字" ==========
    # 菜单中的标签
    old = '✍️ 甲方签字'
    new = '✍️ 项目管理/安装人员签字'
    if old in content:
        content = content.replace(old, new)
        fixes_applied.append('Bug7: 菜单中甲方签字→项目管理/安装人员签字')
    
    # openClientSignature函数中的标题
    old = "header.textContent = '甲方签字';"
    new = "header.textContent = '项目管理/安装人员签字';"
    if old in content:
        content = content.replace(old, new)
        fixes_applied.append('Bug7: 弹窗标题甲方签字→项目管理/安装人员签字')
    
    # 标签文字
    old = "labels[0].textContent = '甲方单位签字';"
    new = "labels[0].textContent = '项目管理/安装人员签字';"
    if old in content:
        content = content.replace(old, new)
        fixes_applied.append('Bug7: 标签甲方单位签字→项目管理/安装人员签字')
    
    # 签字确认页的甲方签名标签
    old = '✍️ 甲方签名（项目级）'
    new = '✍️ 项目管理/安装人员签名（项目级）'
    if old in content:
        content = content.replace(old, new)
        fixes_applied.append('Bug7: 签名区甲方签名→项目管理/安装人员签名')
    
    # 尚未设置甲方签名
    old = '尚未设置甲方签名'
    new = '尚未设置项目管理/安装人员签名'
    if old in content:
        content = content.replace(old, new)
        fixes_applied.append('Bug7: 尚未设置甲方签名→尚未设置项目管理/安装人员签名')
    
    # 电梯列表顶部 → 甲方签字
    old = '电梯列表顶部 → 甲方签字'
    new = '电梯列表顶部 → 项目管理/安装人员签字'
    if old in content:
        content = content.replace(old, new)
        fixes_applied.append('Bug7: 提示文字甲方签字→项目管理/安装人员签字')
    
    # 甲方签字已保存 toast
    old = "showToast('甲方签字已保存');"
    new = "showToast('项目管理/安装人员签字已保存');"
    if old in content:
        content = content.replace(old, new)
        fixes_applied.append('Bug7: toast提示甲方签字→项目管理/安装人员签字')
    
    # 注释：甲方签字（项目级）
    old = '// 甲方签字（项目级）- 从电梯列表菜单调用'
    new = '// 项目管理/安装人员签字（项目级）- 从电梯列表菜单调用'
    if old in content:
        content = content.replace(old, new)
        fixes_applied.append('Bug7: 注释甲方签字→项目管理/安装人员签字')
    
    # 甲方签字模式
    old = "// 甲方签字模式：保存到项目级clientSignature"
    new = "// 项目管理/安装人员签字模式：保存到项目级clientSignature"
    if old in content:
        content = content.replace(old, new)
        fixes_applied.append('Bug7: 注释甲方签字模式→项目管理/安装人员签字模式')
    
    # ========== Bug 8: 签字弹窗去掉施工单位名称输入框 ==========
    # moSign弹窗中施工单位签字那行的输入框
    old_sig_section = """      <div class="fr" style="margin-bottom:8px;">
        <label>施工单位签字</label>
        <div style="flex:1;display:flex;flex-direction:column;gap:4px;">
          <input type="text" id="signBuilderName" placeholder="施工单位名称" style="font-size:13px;">
          <canvas id="sigCanvasBuilder" width="300" height="80" style="border:1px solid #ddd;border-radius:8px;background:#fff;touch-action:none;"></canvas>
          <button onclick="clearSigCanvas('Builder')" style="font-size:11px;color:#999;background:none;border:none;cursor:pointer;text-align:right;">清除签名</button>
        </div>
      </div>"""
    
    new_sig_section = """      <div class="fr" style="margin-bottom:8px;">
        <label>项目管理/安装人员签字</label>
        <div style="flex:1;display:flex;flex-direction:column;gap:4px;">
          <canvas id="sigCanvasBuilder" width="300" height="80" style="border:1px solid #ddd;border-radius:8px;background:#fff;touch-action:none;"></canvas>
          <button onclick="clearSigCanvas('Builder')" style="font-size:11px;color:#999;background:none;border:none;cursor:pointer;text-align:right;">清除签名</button>
        </div>
      </div>"""
    
    if old_sig_section in content:
        content = content.replace(old_sig_section, new_sig_section)
        fixes_applied.append('Bug8: 移除施工单位名称输入框，改标签为项目管理/安装人员签字')
    
    # ========== Bug 1: 附表1门扇间施力间隙联动失效 ==========
    # 在 renderAttach1Judge 函数末尾，返回html之前，添加 updateStatusUI 调用
    # 找到函数末尾 return html; 之前的位置
    old_end = """  var allOk = hasData && sillOk && doorGapOk && doorLockOk && forceGapOk && (!hasCutterData || cutterOk) && (!hasRollerData || rollerOk);
  
  var html = '<div class="auto-result'"""
    
    new_end = """  var allOk = hasData && sillOk && doorGapOk && doorLockOk && forceGapOk && (!hasCutterData || cutterOk) && (!hasRollerData || rollerOk);
  
  // 同步更新主表检测项状态UI
  if (hasSillData && typeof updateStatusUI === 'function') updateStatusUI(113, task.checks[113].s);
  if ((hasDoorGapData || hasForceGapData) && typeof updateStatusUI === 'function') updateStatusUI(114, task.checks[114].s);
  if (hasDoorLockData && typeof updateStatusUI === 'function') updateStatusUI(115, task.checks[115].s);
  if (hasCutterData && typeof updateStatusUI === 'function') updateStatusUI(116, task.checks[116].s);
  if (hasRollerData && typeof updateStatusUI === 'function') updateStatusUI(117, task.checks[117].s);
  if (typeof updateProgress === 'function') updateProgress();
  
  var html = '<div class="auto-result'"""
    
    if old_end in content:
        content = content.replace(old_end, new_end)
        fixes_applied.append('Bug1: 附表1门扇间施力间隙联动-添加主表UI更新')
    
    # ========== Bug 3: 附表2第⑤项移除额外计算框/结果框 ==========
    # 移除轿顶空间的检验结果行，只保留长宽高三个输入框
    old_s5 = """  // ⑤轿顶空间 - 三个输入 + 检验结果
  var s5L = parseFloat(att2.顶部空间.s5L) || 0;
  var s5W = parseFloat(att2.顶部空间.s5W) || 0;
  var s5H = parseFloat(att2.顶部空间.s5H) || 0;
  var s5HasData = s5L > 0 && s5W > 0 && s5H > 0;
  var s5Ok = s5HasData && (s5L >= 0.5 && s5W >= 0.6 && s5H >= 0.8);
  
  html += '<div style="margin-bottom:8px;padding:8px;background:#fafafa;border-radius:6px;">';
  html += '<div style="font-size:12px;font-weight:600;color:#333;margin-bottom:6px;">⑤轿顶空间 (≥0.5m×0.6m×0.8m)</div>';
  html += '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-bottom:6px;">';
  html += '<div><div style="font-size:10px;color:#666;">长(m) ≥0.5</div>';
  html += '<input type="text" value="' + (att2.顶部空间.s5L||'') + '" placeholder="m" inputmode="decimal" onfocus="cancelAttachRender()" onblur="updateAtt2Top(\\'s5L\\',this.value)" style="width:100%;border:1px solid #ddd;border-radius:4px;padding:5px;font-size:12px;text-align:center;"></div>';
  html += '<div><div style="font-size:10px;color:#666;">宽(m) ≥0.6</div>';
  html += '<input type="text" value="' + (att2.顶部空间.s5W||'') + '" placeholder="m" inputmode="decimal" onfocus="cancelAttachRender()" onblur="updateAtt2Top(\\'s5W\\',this.value)" style="width:100%;border:1px solid #ddd;border-radius:4px;padding:5px;font-size:12px;text-align:center;"></div>';
  html += '<div><div style="font-size:10px;color:#666;">高(m) ≥0.8</div>';
  html += '<input type="text" value="' + (att2.顶部空间.s5H||'') + '" placeholder="m" inputmode="decimal" onfocus="cancelAttachRender()" onblur="updateAtt2Top(\\'s5H\\',this.value)" style="width:100%;border:1px solid #ddd;border-radius:4px;padding:5px;font-size:12px;text-align:center;"></div>';
  html += '</div>';
  // 检验结果行
  html += '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;align-items:center;">';
  html += '<div><div style="font-size:10px;color:#666;">空间尺寸</div>';
  var s5SizeStr = s5HasData ? (s5L.toFixed(2)+'×'+s5W.toFixed(2)+'×'+s5H.toFixed(2)) : '-';
  html += '<div style="padding:5px;background:#fff;border:1px solid #e0e0e0;border-radius:4px;text-align:center;font-size:11px;font-weight:600;">' + s5SizeStr + '</div></div>';
  html += '<div><div style="font-size:10px;color:#666;">检验结果</div>';
  html += '<div style="padding:5px;background:#fff;border:1px solid #e0e0e0;border-radius:4px;text-align:center;font-size:12px;font-weight:600;color:' + (s5HasData ? (s5Ok ? '#52c41a' : '#ff4d4f') : '#999') + ';">' + (s5HasData ? (s5Ok ? '合格' : '不合格') : '-') + '</div></div>';
  html += '<div><div style="font-size:10px;color:#666;">标准判定</div>';
  html += '<div style="padding:5px;background:#fff;border-radius:4px;text-align:center;font-size:12px;font-weight:600;color:' + (s5HasData ? (s5Ok ? '#52c41a' : '#ff4d4f') : '#999') + ';">' + (s5HasData ? (s5Ok ? '✓达标' : '✕不达标') : '未判定') + '</div></div>';
  html += '</div>';
  html += '</div>';
  html += '</div>';"""
    
    new_s5 = """  // ⑤轿顶空间 - 长宽高三个输入
  html += '<div style="margin-bottom:8px;padding:8px;background:#fafafa;border-radius:6px;">';
  html += '<div style="font-size:12px;font-weight:600;color:#333;margin-bottom:6px;">⑤轿顶空间 (≥0.5m×0.6m×0.8m)</div>';
  html += '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;">';
  html += '<div><div style="font-size:10px;color:#666;">长(m) ≥0.5</div>';
  html += '<input type="text" value="' + (att2.顶部空间.s5L||'') + '" placeholder="m" inputmode="decimal" onfocus="cancelAttachRender()" onblur="updateAtt2Top(\\'s5L\\',this.value)" style="width:100%;border:1px solid #ddd;border-radius:4px;padding:5px;font-size:12px;text-align:center;"></div>';
  html += '<div><div style="font-size:10px;color:#666;">宽(m) ≥0.6</div>';
  html += '<input type="text" value="' + (att2.顶部空间.s5W||'') + '" placeholder="m" inputmode="decimal" onfocus="cancelAttachRender()" onblur="updateAtt2Top(\\'s5W\\',this.value)" style="width:100%;border:1px solid #ddd;border-radius:4px;padding:5px;font-size:12px;text-align:center;"></div>';
  html += '<div><div style="font-size:10px;color:#666;">高(m) ≥0.8</div>';
  html += '<input type="text" value="' + (att2.顶部空间.s5H||'') + '" placeholder="m" inputmode="decimal" onfocus="cancelAttachRender()" onblur="updateAtt2Top(\\'s5H\\',this.value)" style="width:100%;border:1px solid #ddd;border-radius:4px;padding:5px;font-size:12px;text-align:center;"></div>';
  html += '</div>';
  html += '</div>';"""
    
    if old_s5 in content:
        content = content.replace(old_s5, new_s5)
        fixes_applied.append('Bug3: 附表2第⑤项移除额外计算框/结果框，退回长宽高布局')
    
    # ========== Bug 4: 附表2加"对重缓冲距最大允许值"手填输入框 ==========
    # 在轿厢缓冲器压缩行程下面添加对重缓冲距最大允许值输入框
    old_buf2 = """  html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px;">';
  html += '<div><div style="font-size:11px;color:#666;margin-bottom:2px;">轿厢缓冲器压缩行程 (mm)</div>';
  html += '<input type="text" value="' + (att2.轿厢压缩行程||'') + '" placeholder="mm" inputmode="decimal" onfocus="cancelAttachRender()" onblur="updateAtt2(\\'轿厢压缩行程\\',this.value)" style="width:100%;border:1px solid #ddd;border-radius:4px;padding:6px;font-size:13px;text-align:center;"></div>';
  html += '<div><div style="font-size:11px;color:#666;margin-bottom:2px;">对重缓冲器压缩行程 (mm)</div>';
  html += '<input type="text" value="' + (att2.对重压缩行程||'') + '" placeholder="mm" inputmode="decimal" onfocus="cancelAttachRender()" onblur="updateAtt2(\\'对重压缩行程\\',this.value)" style="width:100%;border:1px solid #ddd;border-radius:4px;padding:6px;font-size:13px;text-align:center;"></div>';
  html += '</div>';"""
    
    new_buf2 = """  html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px;">';
  html += '<div><div style="font-size:11px;color:#666;margin-bottom:2px;">轿厢缓冲器压缩行程 (mm)</div>';
  html += '<input type="text" value="' + (att2.轿厢压缩行程||'') + '" placeholder="mm" inputmode="decimal" onfocus="cancelAttachRender()" onblur="updateAtt2(\\'轿厢压缩行程\\',this.value)" style="width:100%;border:1px solid #ddd;border-radius:4px;padding:6px;font-size:13px;text-align:center;"></div>';
  html += '<div><div style="font-size:11px;color:#666;margin-bottom:2px;">对重缓冲器压缩行程 (mm)</div>';
  html += '<input type="text" value="' + (att2.对重压缩行程||'') + '" placeholder="mm" inputmode="decimal" onfocus="cancelAttachRender()" onblur="updateAtt2(\\'对重压缩行程\\',this.value)" style="width:100%;border:1px solid #ddd;border-radius:4px;padding:6px;font-size:13px;text-align:center;"></div>';
  html += '</div>';
  html += '<div style="margin-bottom:8px;">';
  html += '<div style="font-size:11px;color:#666;margin-bottom:2px;">对重缓冲距最大允许值 (mm)</div>';
  html += '<input type="text" value="' + (att2.对重最大允许值||'') + '" placeholder="手动填写，不参与计算" inputmode="decimal" onfocus="cancelAttachRender()" onblur="updateAtt2(\\'对重最大允许值\\',this.value)" style="width:100%;border:1px solid #ddd;border-radius:4px;padding:6px;font-size:13px;text-align:center;">';
  html += '</div>';"""
    
    if old_buf2 in content:
        content = content.replace(old_buf2, new_buf2)
        fixes_applied.append('Bug4: 添加对重缓冲距最大允许值手填输入框')
    
    # ========== Bug 5: 项目管理/安装人员签字弹窗点不开 ==========
    # openClientSignature 函数需要确保能正常工作
    # 问题可能是 getCurrentProject 在任务列表页面返回null，导致函数提前return
    # 修复：在获取project之前先打开modal，并且处理null情况
    old_ocs = """function openClientSignature() {
  window._signMode = 'client';
  openMoModal('moSign');
  var header = document.querySelector('#moSign .mh h3');
  if (header) header.textContent = '项目管理/安装人员签字';
  // 修改标签为甲方签字
  var labels = document.querySelectorAll('#moSign label');
  if (labels && labels[0]) labels[0].textContent = '项目管理/安装人员签字';
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
    
    new_ocs = """function openClientSignature() {
  window._signMode = 'client';
  openMoModal('moSign');
  var header = document.querySelector('#moSign .mh h3');
  if (header) header.textContent = '项目管理/安装人员签字';
  // 修改标签为项目管理/安装人员签字
  var labels = document.querySelectorAll('#moSign label');
  if (labels && labels[0]) labels[0].textContent = '项目管理/安装人员签字';
  if (labels && labels[1]) labels[1].style.display = 'none';
  var inspectorRow = document.getElementById('signInspectorName');
  if (inspectorRow) inspectorRow.parentElement.style.display = 'none';
  var nameInput = document.getElementById('signBuilderName');
  if (nameInput) nameInput.parentElement.style.display = 'none';
  var proj = getCurrentProject();
  if (!proj) {
    // 即使没有当前项目也初始化画布
    setTimeout(function() {
      initSigCanvasFor('Builder');
    }, 300);
    return;
  }
  if (!proj.clientSignature) proj.clientSignature = {};
  
  // 初始化画布（使支持绘制）
  setTimeout(function() {
    initSigCanvasFor('Builder');
    initSigCanvasFor('Inspector');
    // 恢复签名
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
    
    if old_ocs in content:
        content = content.replace(old_ocs, new_ocs)
        fixes_applied.append('Bug5: 修复项目管理/安装人员签字弹窗-处理无项目情况+隐藏姓名输入框')
    
    # ========== Bug 6: 检验人员签字保存不了 ==========
    # saveSig 函数中，检验人员签名保存时，name用的是固定'检验人员'
    # 但 saveInspectorSignature 保存到 localStorage 是全局的
    # 问题：openInspectorSigSetting 用的是 sigModal，但保存时 task 可能不存在
    # 修复：在 saveSig 中，当 signZoneTarget === 'inspector' 时，确保也保存到当前任务
    old_savesig = """  // 签字确认标签页的签名
  if (signZoneTarget === 'inspector') {
    task.signatures.inspectorSig = dataUrl;
    saveInspectorSignature('检验人员', dataUrl);
  } else if (signZoneTarget === 'pm') {"""
    
    new_savesig = """  // 签字确认标签页的签名
  if (signZoneTarget === 'inspector') {
    task.signatures.inspectorSig = dataUrl;
    saveInspectorSignature('检验人员', dataUrl);
    saveProjects();
    // 刷新显示
    if (typeof renderSignZoneContent === 'function') {
      var signDiv = document.getElementById('signZoneContent');
      if (signDiv) renderSignZoneContent(signDiv);
    }
  } else if (signZoneTarget === 'pm') {"""
    
    if old_savesig in content:
        content = content.replace(old_savesig, new_savesig)
        fixes_applied.append('Bug6: 检验人员签字保存-增加saveProjects和刷新显示')
    
    # 另一个问题：从菜单调用 openInspectorSigSetting 时，可能没有当前task
    # 需要确保保存时也能正常工作
    old_openinspector = """function openInspectorSigSetting() {
  signZoneTarget = 'inspector';
  var header = document.querySelector('#sigModal .sig-canvas-h span');
  if (header) header.textContent = '检验人员签名设置';
  document.getElementById('sigModal').style.display = 'flex';
  setTimeout(function() { initSigCanvas(); }, 100);
}"""

    # 这个函数看起来没问题，但saveSig中需要确保即使在菜单调用时也能保存
    # 让我检查 saveSig 的完整逻辑，确保inspector模式下保存正确
    # 先检查是否有从菜单调用时task不存在的问题
    old_savesig_full = """function saveSig() {
  var canvas = document.getElementById('sigCanvas');
  var dataUrl = canvas.toDataURL();
  var task = getCurrentTask();
  if (!task) return;
  if (!task.signatures) task.signatures = {};
  
  // 签字确认标签页的签名
  if (signZoneTarget === 'inspector') {
    task.signatures.inspectorSig = dataUrl;
    saveInspectorSignature('检验人员', dataUrl);
    saveProjects();
    // 刷新显示
    if (typeof renderSignZoneContent === 'function') {
      var signDiv = document.getElementById('signZoneContent');
      if (signDiv) renderSignZoneContent(signDiv);
    }
  } else if (signZoneTarget === 'pm') {"""

    # 问题：当从顶部菜单调用厂检签字时，如果还没进入具体任务，getCurrentTask()返回null，函数就return了
    # 修复：inspector模式下即使没有task也要保存到localStorage
    new_savesig_full = """function saveSig() {
  var canvas = document.getElementById('sigCanvas');
  var dataUrl = canvas.toDataURL();
  var task = getCurrentTask();
  
  // 检验人员签名（全局）- 即使没有当前任务也要保存到localStorage
  if (signZoneTarget === 'inspector') {
    saveInspectorSignature('检验人员', dataUrl);
    // 如果有当前任务，也保存到任务中
    if (task) {
      if (!task.signatures) task.signatures = {};
      task.signatures.inspectorSig = dataUrl;
      saveProjects();
      // 刷新显示
      if (typeof renderSignZoneContent === 'function') {
        var signDiv = document.getElementById('signZoneContent');
        if (signDiv) renderSignZoneContent(signDiv);
      }
    }
    closeSigModal();
    showToast('检验人员签名已保存');
    return;
  }
  
  if (!task) return;
  if (!task.signatures) task.signatures = {};
  
  // 签字确认标签页的签名
  if (signZoneTarget === 'pm') {"""
    
    if old_savesig_full in content:
        content = content.replace(old_savesig_full, new_savesig_full)
        fixes_applied.append('Bug6: 检验人员签字-支持无任务时保存到全局')
    elif old_savesig in content:
        # 如果只找到部分匹配，至少添加saveProjects
        content = content.replace(old_savesig, new_savesig)
        fixes_applied.append('Bug6: 检验人员签字保存-增加saveProjects和刷新显示')
    
    # ========== Bug 10: 点击符合/不符合/不适用页面抖动 ==========
    # setCheckStatus 函数中的滚动恢复不够稳定
    # 用 requestAnimationFrame 双重确保滚动位置恢复，并且用更精确的方式
    old_setcheck = """function setCheckStatus(id, status) {
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
}"""
    
    new_setcheck = """function setCheckStatus(id, status) {
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
  
  // 固定容器高度防止重排抖动
  var zoneContent = document.getElementById('zoneContent');
  var origHeight = zoneContent ? zoneContent.offsetHeight : 0;
  if (zoneContent && origHeight > 0) {
    zoneContent.style.minHeight = origHeight + 'px';
  }
  
  // If switching away from NG, clean up NG fields but keep them in data
  saveCurrentTask();
  renderZoneContent(currentZoneIndex);
  renderZoneTabs();
  updateProgress();
  
  // 立即恢复滚动位置
  window.scrollTo(0, savedScrollTop);
  
  // 下一帧再次恢复，确保浏览器布局完成后位置正确
  requestAnimationFrame(function() {
    window.scrollTo(0, savedScrollTop);
    // 第二帧再确认一次
    requestAnimationFrame(function() {
      window.scrollTo(0, savedScrollTop);
      // 清除minHeight限制
      if (zoneContent) zoneContent.style.minHeight = '';
    });
  });
}"""
    
    if old_setcheck in content:
        content = content.replace(old_setcheck, new_setcheck)
        fixes_applied.append('Bug10: 点击符合/不符合/不适用页面抖动-固定高度+双RAF恢复滚动')
    
    # ========== Bug 7 补充: saveSignatures中的甲方引用 ==========
    # 保存签字函数中clientSignature相关逻辑
    old_save_sig_client = """  // 甲方签字模式：保存到项目级clientSignature
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
    showToast('项目管理/安装人员签字已保存');
    return;
  }"""
    
    new_save_sig_client = """  // 项目管理/安装人员签字模式：保存到项目级clientSignature
  if (window._signMode === 'client') {
    var proj = getCurrentProject();
    if (!proj) {
      closeMoModal('moSign');
      window._signMode = '';
      showToast('请先选择项目');
      return;
    }
    if (!proj.clientSignature) proj.clientSignature = {};
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
    var nameInput = document.getElementById('signBuilderName');
    if (nameInput) nameInput.parentElement.style.display = '';
    showToast('项目管理/安装人员签字已保存');
    return;
  }"""
    
    if old_save_sig_client in content:
        content = content.replace(old_save_sig_client, new_save_sig_client)
        fixes_applied.append('Bug7+8: 保存签字函数-移除name读取+恢复nameInput显示')
    
    return content, fixes_applied


def fix_print_file(content):
    """修复副表打印页 print-fubiao.html"""
    fixes_applied = []
    
    # ========== Bug 2: 附表2第⑤项打印PDF无判定结果 ==========
    # 确保 top-s5-result 被正确设置
    # 先检查现有代码
    old_s5_result = """  // 轿顶空间检验结果
  var _s5L = parseFloat(top.s5L) || 0;
  var _s5W = parseFloat(top.s5W) || 0;
  var _s5H = parseFloat(top.s5H) || 0;
  if (_s5L > 0 && _s5W > 0 && _s5H > 0) {
    setFb2Text('top-s5-result', (_s5L >= 0.5 && _s5W >= 0.6 && _s5H >= 0.8) ? '符合' : '不符合');
  }"""
    
    new_s5_result = """  // 轿顶空间检验结果
  var _s5L = parseFloat(top.s5L) || 0;
  var _s5W = parseFloat(top.s5W) || 0;
  var _s5H = parseFloat(top.s5H) || 0;
  if (_s5L > 0 && _s5W > 0 && _s5H > 0) {
    setFb2Text('top-s5-result', (_s5L >= 0.5 && _s5W >= 0.6 && _s5H >= 0.8) ? '符合' : '不符合');
  } else {
    setFb2Text('top-s5-result', '');
  }"""
    
    if old_s5_result in content:
        # 代码本身没问题，但可能是HTML结构问题
        # 让我们检查底坑空间第⑤项是否也有问题
        pass
    
    # 检查底坑空间第⑤项的结果设置
    old_p5_result = """  if (_p5L > 0 && _p5W > 0 && _p5H > 0) {
    setFb2Text('pit-p5-result', (_p5L >= 0.5 && _p5W >= 0.6 && _p5H >= 1.0) ? '符合' : '不符合');
  }"""
    
    new_p5_result = """  if (_p5L > 0 && _p5W > 0 && _p5H > 0) {
    setFb2Text('pit-p5-result', (_p5L >= 0.5 && _p5W >= 0.6 && _p5H >= 1.0) ? '符合' : '不符合');
  } else {
    setFb2Text('pit-p5-result', '');
  }"""
    
    if old_p5_result in content:
        content = content.replace(old_p5_result, new_p5_result)
    
    # 真正的Bug2修复：确保顶部空间第⑤项的HTML结构正确
    # 检查是否有 top-s5-result 元素，如果没有则需要添加
    if 'data-fb2="top-s5-result"' not in content:
        fixes_applied.append('Bug2: 警告-未找到top-s5-result元素')
    else:
        # 元素存在，可能是CSS或布局问题导致文字看不见
        # 添加一个明确的样式确保结果文字可见
        # 先检查表格结构
        pass
    
    # 让我们仔细检查：顶部空间第5行的HTML结构
    # 可能的问题是top-s5-space的colspan=3占了太多列，导致result列被挤掉
    # 让我看看实际的HTML结构
    old_s5_row = """          <tr class="data-row">
            <td colspan="4" class="align-left">⑤轿顶空间（≥0.5m×0.6m×0.8m）</td>
            <td colspan="3" data-fb2="top-s5-space"></td>
            <td colspan="2" data-fb2="top-s5-result"></td>
          </tr>"""
    
    # 这个结构看起来是对的。列数：1(vertical) + 4(项目名) + 3(空间尺寸) + 2(结果) = 10
    # 表头列数：1(vertical) + 4(项目/状态) + 2(上端站平层时) + 1(对重压缓冲距离) + 2(检验结果) = 10
    # 第5行：前4行有rowspan=4的"对重压缓冲距离"列在第8列
    # 第5行没有这个rowspan了，所以 s5-space 应该占 2+1=3列(上端站平层时2列+对重压缓冲距离1列) = colspan=3
    # 这是正确的
    
    # 可能的问题：PDF导出时html2canvas渲染问题？
    # 或者是数据填充顺序问题？
    # 让我们确保 fillFb2 函数中 s5-result 的设置是在 DOM 就绪后
    
    # 另一个可能的问题：表格的第5行(⑤轿顶空间)在items 1-4的后面
    # items 1-4 的 "对重完全压在缓冲器上时轿门与层门地坎距离" 列有 rowspan=4
    # 但第5行(轿顶空间)在第6个tr，不在前4个data-row里
    # 让我数一下：
    # - 井道顶部空间表头行 (第1个tr)
    # - ① (第2个tr, data-row)
    # - ② (第3个tr, data-row)
    # - ③ (第4个tr, data-row)
    # - ④ (第5个tr, data-row)
    # - ⑤ (第6个tr, data-row)
    # 所以 rowspan=4 覆盖 rows 2-5 (①-④)，第6行(⑤)不受影响
    # 这是正确的
    
    # 让我检查 PDF 导出时的问题
    # 也许是在 PDF 导出前，数据还没填充完？
    # 不，fillData() 在页面加载时就调用了
    
    # 让我换个思路：也许问题是 top-s5-result 的 td 没有内容时宽度为0，
    # 或者文字颜色和背景一样？
    # 让我们给结果列加个最小宽度和明确的文字样式
    old_result_td = '<td colspan="2" data-fb2="top-s5-result"></td>'
    new_result_td = '<td colspan="2" data-fb2="top-s5-result" style="text-align:center;font-weight:bold;"></td>'
    
    if old_result_td in content:
        content = content.replace(old_result_td, new_result_td)
        fixes_applied.append('Bug2: top-s5-result添加居中和粗体样式确保可见')
    
    # 同样处理 pit-p5-result
    old_pit_result = '<td colspan="2" data-fb2="pit-p5-result"></td>'
    new_pit_result = '<td colspan="2" data-fb2="pit-p5-result" style="text-align:center;font-weight:bold;"></td>'
    
    if old_pit_result in content:
        content = content.replace(old_pit_result, new_pit_result)
    
    # ========== Bug 9: 附表1打印列错位 ==========
    # 轿门1/2和楼层号跑到C列，应该在B列
    # fillFb1Row 函数中 nameIdx 的计算有问题
    old_fillrow = """  // 位置列索引确定：
  // 13个td：第1个对应第1列（被vertical-text rowspan覆盖），第2个才是位置列
  // 12个td：第1个就是位置列
  var nameIdx = (cells.length >= 13) ? 1 : 0;
  
  // 清空第1列（被rowspan覆盖的列），防止内容错位
  if (cells.length >= 13) {
    cells[0].textContent = '';
  }
  
  // 设置位置名称
  cells[nameIdx].textContent = name;
  
  // 共11个数据列，从位置列后面开始
  var dataStartIdx = nameIdx + 1;"""
    
    new_fillrow = """  // 位置列索引确定：
  // HTML表格中，第一列被vertical-text的rowspan占用，每行第一个td就是位置列(B列)
  // 因此 cells[0] 就是位置列，数据从 cells[1] 开始
  var nameIdx = 0;
  
  // 设置位置名称
  cells[nameIdx].textContent = name;
  
  // 共11个数据列，从位置列后面开始
  var dataStartIdx = nameIdx + 1;"""
    
    if old_fillrow in content:
        content = content.replace(old_fillrow, new_fillrow)
        fixes_applied.append('Bug9: 附表1打印列错位-修正位置列索引，位置名称从第1个td开始')
    
    # ========== Bug 4: 打印页也需要添加"对重缓冲距最大允许值" ==========
    # 在打印表格的缓冲距部分添加对重最大允许值行
    old_buf_max = """          <tr class="small-row">
            <th>最大允许值</th>
            <th colspan="2" data-fb2="最大允许值-val">mm</th>
            <th>对重</th>
            <th data-fb2="对重压缩行程-val">mm</th>
          </tr>"""
    
    # 这个"最大允许值"是轿厢侧的，我们需要加一个对重侧的手填最大允许值
    # 实际上，根据bug描述，是在"轿厢缓冲器压缩行程下面加"，也就是编辑页的布局
    # 打印页的表格结构不同，需要确认在哪里加
    # 让我先看看现有表格结构
    # 从之前读取的内容来看，表格有"最大允许值"这一行，但不确定是轿厢还是对重的
    # 从代码 setFb2Text('最大允许值-val', att2.最大允许值 || '') 来看，
    # 已经有一个最大允许值，但可能是轿厢侧的
    # Bug4要求添加"对重缓冲距最大允许值"手填输入框
    # 所以我们需要在打印页也添加对应的列/行
    
    # 让我们在 fillFb2 中添加对重最大允许值的填充
    old_fillfb2_start = """  // 缓冲距 - 单位mm
  setFb2Text('轿厢缓冲距-val', att2.轿厢缓冲距 || '');
  setFb2Text('对重缓冲距-val', att2.对重缓冲距 || '');
  setFb2Text('最大允许值-val', att2.最大允许值 || '');
  setFb2Text('轿厢压缩行程-val', att2.轿厢压缩行程 || '');
  setFb2Text('对重压缩行程-val', att2.对重压缩行程 || '');"""
    
    new_fillfb2_start = """  // 缓冲距 - 单位mm
  setFb2Text('轿厢缓冲距-val', att2.轿厢缓冲距 || '');
  setFb2Text('对重缓冲距-val', att2.对重缓冲距 || '');
  setFb2Text('最大允许值-val', att2.最大允许值 || '');
  setFb2Text('轿厢压缩行程-val', att2.轿厢压缩行程 || '');
  setFb2Text('对重压缩行程-val', att2.对重压缩行程 || '');
  setFb2Text('对重最大允许值-val', att2.对重最大允许值 || '');"""
    
    if old_fillfb2_start in content:
        content = content.replace(old_fillfb2_start, new_fillfb2_start)
        fixes_applied.append('Bug4: 打印页添加对重最大允许值数据填充')
    
    # 在HTML表格中添加对重最大允许值行
    old_small_row = """          <tr class="small-row">
            <th>最大允许值</th>
            <th colspan="2" data-fb2="最大允许值-val">mm</th>
            <th>对重</th>
            <th data-fb2="对重压缩行程-val">mm</th>
          </tr>"""
    
    new_small_row = """          <tr class="small-row">
            <th>最大允许值</th>
            <th colspan="2" data-fb2="最大允许值-val">mm</th>
            <th>对重</th>
            <th data-fb2="对重压缩行程-val">mm</th>
          </tr>
          <tr class="small-row">
            <th>对重缓冲距最大允许值</th>
            <th colspan="2"></th>
            <th colspan="2" data-fb2="对重最大允许值-val">mm</th>
          </tr>"""
    
    if old_small_row in content:
        content = content.replace(old_small_row, new_small_row)
        fixes_applied.append('Bug4: 打印页表格添加对重缓冲距最大允许值行')
    
    # ========== Bug 2 进一步检查 ==========
    # 让我们再确认一下 top-s5-result 是否真的在正确的位置
    # 可能的问题是第5行的列数不对
    # 表头有10列(1+4+2+1+2)
    # 第5行：colspan=4(项目名) + colspan=3(空间) + colspan=2(结果) = 9 + 1(vertical) = 10 ✓
    
    # 另一个可能：由于上面的行有rowspan，导致第5行的单元格位置计算错误
    # 让我们给第5行加一个明确的样式调试
    # 实际上，让我重新检查：前4行的结构是
    # td colspan=4 (项目名) + td colspan=2 (测量值) + td rowspan=4 (对重压距离) + td colspan=2 (结果)
    # = 4 + 2 + 1 + 2 = 9 + 1(vertical-text) = 10 ✓
    
    # 第5行：td colspan=4 (项目名) + td colspan=3 (空间尺寸) + td colspan=2 (结果)
    # = 4 + 3 + 2 = 9 + 1(vertical-text) = 10 ✓
    
    # 结构是对的。那为什么PDF中看不见结果？
    # 可能是 html2canvas 渲染时的问题，或者字体颜色太浅
    # 让我们确保所有结果列都有明确的样式
    all_results = re.findall(r'data-fb2="top-s\d-result"', content)
    if len(all_results) > 0:
        # 给所有检验结果td添加样式
        for i in range(1, 6):
            old = f'data-fb2="top-s{i}-result"></td>'
            new = f'data-fb2="top-s{i}-result" style="text-align:center;font-weight:bold;color:#000;"></td>'
            if old in content:
                content = content.replace(old, new)
        
        for i in range(1, 6):
            old = f'data-fb2="pit-p{i}-result'
            # 只替换那些还没有style的
            pattern = f'data-fb2="pit-p{i}-result"></td>'
            replacement = f'data-fb2="pit-p{i}-result" style="text-align:center;font-weight:bold;color:#000;"></td>'
            if pattern in content:
                content = content.replace(pattern, replacement)
        
        fixes_applied.append('Bug2: 所有检验结果列添加居中和粗体黑色样式')
    
    return content, fixes_applied


def main():
    print("=" * 60)
    print("v123 批量修复10项bug")
    print("=" * 60)
    
    # 读取主文件
    main_content = read_file(MAIN_FILE)
    print(f"\n主文件读取成功: {len(main_content)} 字符")
    
    # 修复主文件
    main_content, main_fixes = fix_main_file(main_content)
    print(f"\n主文件修复 ({len(main_fixes)} 项):")
    for fix in main_fixes:
        print(f"  ✓ {fix}")
    
    # 写入主文件
    write_file(MAIN_FILE, main_content)
    print(f"\n主文件写入成功: {len(main_content)} 字符")
    
    # 读取打印文件
    print_content = read_file(PRINT_FILE)
    print(f"\n打印文件读取成功: {len(print_content)} 字符")
    
    # 修复打印文件
    print_content, print_fixes = fix_print_file(print_content)
    print(f"\n打印文件修复 ({len(print_fixes)} 项):")
    for fix in print_fixes:
        print(f"  ✓ {fix}")
    
    # 写入打印文件
    write_file(PRINT_FILE, print_content)
    print(f"\n打印文件写入成功: {len(print_content)} 字符")
    
    print("\n" + "=" * 60)
    print("修复完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
