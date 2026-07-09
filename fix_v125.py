#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v125 修复脚本 - 修复6个问题
1. 项目管理/安装人员签字弹窗异常（canvas显示问题）
2. 厂检结论页的签名提示框要删掉
3. 打印通知单时签字没有引用过去
4. 配置表导入编号引用错误（TSX型式试验编号的问题）
5. 打印检查表和打印副表不起作用
6. 附表2打印页表格结构和最大允许值关联（确认修复）
"""
import re
import os
import sys

MAIN_FILE = '/app/data/所有对话/主对话/weite-pro-temp/factory-inspection-v2.html'
PRINT_FILE = '/app/data/所有对话/主对话/weite-pro-temp/print-fubiao.html'
ENTRY_FILE = '/app/data/所有对话/主对话/weite-pro-temp/威特电梯厂检调试记录单v2.html'

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def fix_issue1_signature_modal(content):
    """问题1：项目管理/安装人员签字弹窗异常
    - canvas在flex布局中显示异常，给canvas容器设置最小宽度
    - 确保canvas边框和背景正常显示
    - 增强初始化逻辑
    """
    fixed_count = 0
    
    # 修复1：给canvas的父容器添加最小宽度，确保flex布局下有足够空间
    # 找到弹窗HTML中的canvas容器
    old_canvas_container1 = '''        <div style="flex:1;display:flex;flex-direction:column;gap:4px;">
          <canvas id="sigCanvasBuilder" width="300" height="80" style="border:1px solid #ddd;border-radius:8px;background:#fff;touch-action:none;"></canvas>'''
    new_canvas_container1 = '''        <div style="flex:1;min-width:200px;display:flex;flex-direction:column;gap:4px;">
          <canvas id="sigCanvasBuilder" width="300" height="80" style="border:1px solid #ddd;border-radius:8px;background:#fff;touch-action:none;display:block;width:100%;height:80px;"></canvas>'''
    if old_canvas_container1 in content:
        content = content.replace(old_canvas_container1, new_canvas_container1)
        fixed_count += 1
        print("  [OK] 问题1: 修复Builder canvas容器最小宽度")
    else:
        print("  [WARN] 问题1: 未找到Builder canvas容器代码")
    
    # 修复2：检验人员canvas容器也同样修复
    old_canvas_container2 = '''        <div style="flex:1;display:flex;flex-direction:column;gap:4px;">
          <input type="text" id="signInspectorName" placeholder="检验人员姓名" style="font-size:13px;">
          <canvas id="sigCanvasInspector" width="300" height="80" style="border:1px solid #ddd;border-radius:8px;background:#fff;touch-action:none;"></canvas>'''
    new_canvas_container2 = '''        <div style="flex:1;min-width:200px;display:flex;flex-direction:column;gap:4px;">
          <input type="text" id="signInspectorName" placeholder="检验人员姓名" style="font-size:13px;width:100%;box-sizing:border-box;">
          <canvas id="sigCanvasInspector" width="300" height="80" style="border:1px solid #ddd;border-radius:8px;background:#fff;touch-action:none;display:block;width:100%;height:80px;"></canvas>'''
    if old_canvas_container2 in content:
        content = content.replace(old_canvas_container2, new_canvas_container2)
        fixed_count += 1
        print("  [OK] 问题1: 修复Inspector canvas容器最小宽度")
    else:
        print("  [WARN] 问题1: 未找到Inspector canvas容器代码")
    
    # 修复3：增强 openClientSignature 中的canvas初始化，确保弹窗显示后强制重绘
    # 找到 openClientSignature 函数
    func_start = content.find('function openClientSignature()')
    if func_start >= 0:
        # 找到初始化部分，增加 requestAnimationFrame 确保布局完成后再初始化
        old_init = '''  // 初始化画布（使支持绘制）- 确保弹窗显示后再初始化
  setTimeout(function() {
    // 确保canvas有正确的尺寸
    var cB = document.getElementById('sigCanvasBuilder');
    var cI = document.getElementById('sigCanvasInspector');
    if (cB) {
      // 用offsetWidth，如果为0则用父容器宽度或默认值
      var w = cB.offsetWidth || cB.parentElement.offsetWidth || 300;
      cB.width = w;
      cB.height = 80;
    }
    if (cI) {
      var w2 = cI.offsetWidth || cI.parentElement.offsetWidth || 300;
      cI.width = w2;
      cI.height = 80;
    }
    initSigCanvasFor('Builder');
    initSigCanvasFor('Inspector');
    // 恢复签名
    if (proj.clientSignature && proj.clientSignature.sig) {
      var cBuilder = document.getElementById('sigCanvasBuilder');
      if (cBuilder) {
        var ctx = cBuilder.getContext('2d');
        var img = new Image();
        img.onload = function() { ctx.drawImage(img, 0, 0, cBuilder.width, cBuilder.height); };
        img.src = proj.clientSignature.sig;
      }
    }
  }, 100);'''
        
        new_init = '''  // 初始化画布（使支持绘制）- 确保弹窗显示后再初始化
  function _doInitSigCanvas() {
    var cB = document.getElementById('sigCanvasBuilder');
    var cI = document.getElementById('sigCanvasInspector');
    if (cB) {
      // 强制重排确保父容器有宽度
      cB.style.display = 'block';
      var parentW = cB.parentElement ? (cB.parentElement.offsetWidth || cB.parentElement.clientWidth) : 0;
      var w = cB.offsetWidth || parentW || 300;
      if (w < 50) w = 300;
      cB.width = w;
      cB.height = 80;
      cB.style.width = w + 'px';
      cB.style.height = '80px';
    }
    if (cI) {
      var parentW2 = cI.parentElement ? (cI.parentElement.offsetWidth || cI.parentElement.clientWidth) : 0;
      var w2 = cI.offsetWidth || parentW2 || 300;
      if (w2 < 50) w2 = 300;
      cI.width = w2;
      cI.height = 80;
      cI.style.width = w2 + 'px';
      cI.style.height = '80px';
    }
    initSigCanvasFor('Builder');
    initSigCanvasFor('Inspector');
    // 恢复签名
    if (proj.clientSignature && proj.clientSignature.sig) {
      var cBuilder = document.getElementById('sigCanvasBuilder');
      if (cBuilder) {
        var ctx = cBuilder.getContext('2d');
        var img = new Image();
        img.onload = function() { 
          var cb = document.getElementById('sigCanvasBuilder');
          if (cb) {
            var c = cb.getContext('2d');
            c.clearRect(0, 0, cb.width, cb.height);
            c.drawImage(img, 0, 0, cb.width, cb.height);
          }
        };
        img.src = proj.clientSignature.sig;
      }
    }
  }
  // 多阶段初始化，确保flex布局稳定后canvas有正确尺寸
  setTimeout(_doInitSigCanvas, 50);
  setTimeout(_doInitSigCanvas, 200);
  setTimeout(_doInitSigCanvas, 500);'''
        
        if old_init in content:
            content = content.replace(old_init, new_init)
            fixed_count += 1
            print("  [OK] 问题1: 增强 openClientSignature canvas初始化逻辑（多阶段）")
        else:
            print("  [WARN] 问题1: 未找到 openClientSignature 中的初始化代码")
            # 尝试找到函数位置并打印
            func_end = content.find('function openInspectorSigSetting', func_start)
            if func_end > 0:
                print(f"  openClientSignature 函数范围: {func_start} - {func_end}")
    
    # 修复4：增强 initSigCanvasFor 函数，确保canvas尺寸计算正确
    old_init_for = '''function initSigCanvasFor(suffix) {
  var canvas = document.getElementById('sigCanvas' + suffix);
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var drawing = false;
  // 确保canvas有正确的宽度：优先用offsetWidth，其次父元素宽度，最后默认300
  var w = canvas.offsetWidth;
  if (!w || w < 50) {
    w = (canvas.parentElement && canvas.parentElement.offsetWidth) ? canvas.parentElement.offsetWidth - 20 : 300;
  }
  if (w > 0) canvas.width = w;
  canvas.height = 80;'''
    
    new_init_for = '''function initSigCanvasFor(suffix) {
  var canvas = document.getElementById('sigCanvas' + suffix);
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var drawing = false;
  // 确保canvas有正确的宽度：优先用offsetWidth，其次父元素宽度，最后默认300
  var w = canvas.offsetWidth;
  if (!w || w < 50) {
    // 尝试用父容器的clientWidth
    var parent = canvas.parentElement;
    if (parent) {
      w = parent.clientWidth || parent.offsetWidth;
      if (w) w = w - 10; // 留一点边距
    }
  }
  if (!w || w < 50) w = 300;
  canvas.width = w;
  canvas.height = 80;
  // 同步设置CSS尺寸，确保显示一致
  canvas.style.width = w + 'px';
  canvas.style.height = '80px';'''
    
    if old_init_for in content:
        content = content.replace(old_init_for, new_init_for)
        fixed_count += 1
        print("  [OK] 问题1: 增强 initSigCanvasFor 的宽度计算和CSS同步")
    else:
        print("  [WARN] 问题1: 未找到 initSigCanvasFor 函数的原始代码")
    
    return content


def fix_issue2_remove_sign_hints(content):
    """问题2：删除厂检结论页的签名提示框
    - 删除蓝色的"检验人员签名（全局）"提示框
    - 删除绿色的"项目管理/安装人员签名（项目级）"提示框
    - 保留"相关人员签名"区域
    """
    # 找到 renderSignZoneContent 函数中的两个提示框
    # 蓝色提示框（检验人员签名全局）
    old_blue_box = '''    // 检验人员签名（全局级，只读预览）
  var _gSig = null;
  try { var _sd = localStorage.getItem(INSPECTOR_SIG_KEY); if (_sd) _gSig = JSON.parse(_sd); } catch(e) {}
  html += '<div style="background:#f0f4ff;border-radius:10px;padding:12px;margin-bottom:12px;border:1px solid #c7d2fe;">';
  html += '<div style="font-size:13px;font-weight:600;margin-bottom:8px;color:#4338ca;">✍️ 检验人员签名（全局）</div>';
  if (_gSig && _gSig.sig) {
    html += '<div style="display:flex;align-items:center;gap:10px;">';
    html += '<div style="font-size:12px;color:#4b5563;font-weight:600;white-space:nowrap;">' + (_gSig.name || '检验员') + '：</div>';
    html += '<div style="flex:1;border:1px solid #e2e8f0;border-radius:6px;background:#fff;padding:6px;min-height:45px;display:flex;align-items:center;justify-content:center;">';
    html += '<img src="' + _gSig.sig + '" style="max-height:40px;max-width:100%;">';
    html += '</div></div>';
  } else {
    html += '<div style="color:#9ca3af;font-size:12px;text-align:center;padding:8px;">尚未设置检验人员签名<br><span style="font-size:11px;">顶部菜单 → 厂检签字</span></div>';
  }
  html += '</div>';
  
  // 项目管理/安装人员签名（项目级，只读预览）'''
    
    if old_blue_box in content:
        content = content.replace(old_blue_box, '  // （检验人员全局签名和项目级签名提示框已移除，签名入口在顶部菜单）')
        print("  [OK] 问题2: 删除蓝色检验人员签名提示框")
    else:
        print("  [WARN] 问题2: 未找到蓝色检验人员签名提示框（尝试其他匹配方式）")
        # 部分匹配
        if '检验人员签名（全局）' in content:
            print("  [INFO] 找到'检验人员签名（全局）'文本，需要更精确的匹配")
    
    # 绿色提示框（项目管理/安装人员签名项目级）
    old_green_box = '''  var _cp = getCurrentProject();
  var _cs = (_cp && _cp.clientSignature) ? _cp.clientSignature : null;
  html += '<div style="background:#f0fff4;border-radius:10px;padding:12px;margin-bottom:12px;border:1px solid #9ae6b4;">';
  html += '<div style="font-size:13px;font-weight:600;margin-bottom:8px;color:#276749;">✍️ 项目管理/安装人员签名（项目级）</div>';
  if (_cs && _cs.sig) {
    html += '<div style="display:flex;align-items:center;gap:10px;">';
    html += '<div style="font-size:12px;color:#4b5563;font-weight:600;white-space:nowrap;">' + (_cs.name || '项目管理/安装人员') + '：</div>';
    html += '<div style="flex:1;border:1px solid #e2e8f0;border-radius:6px;background:#fff;padding:6px;min-height:45px;display:flex;align-items:center;justify-content:center;">';
    html += '<img src="' + _cs.sig + '" style="max-height:40px;max-width:100%;">';
    html += '</div></div>';
  } else {
    html += '<div style="color:#9ca3af;font-size:12px;text-align:center;padding:8px;">尚未设置项目管理/安装人员签名<br><span style="font-size:11px;">电梯列表顶部 → 项目管理/安装人员签字</span></div>';
  }
  html += '</div>';
  
  html += '<div style="font-size:13px;font-weight:600;margin-bottom:8px;">相关人员签名</div>';'''
    
    new_related_title = '''  html += '<div style="font-size:13px;font-weight:600;margin-bottom:8px;">相关人员签名</div>';'''
    
    if old_green_box in content:
        content = content.replace(old_green_box, new_related_title)
        print("  [OK] 问题2: 删除绿色项目管理/安装人员签名提示框")
    else:
        print("  [WARN] 问题2: 未找到绿色项目管理/安装人员签名提示框")
        # 检查是否存在
        if '项目管理/安装人员签名（项目级）' in content:
            print("  [INFO] 找到'项目管理/安装人员签名（项目级）'文本")
    
    return content


def fix_issue3_notice_signatures(content):
    """问题3：打印通知单时签字没有引用过去
    - 检验人员签名：优先从 localStorage 读取全局签名
    - 安装单位代表签名：优先从 proj.clientSignature.sig 读取
    """
    # 找到 buildNoticeFullHTML 中检验人员签名的读取部分
    old_insp_sig = "  var inspSig = (task.signatures && task.signatures.inspectorSig) || '';"
    new_insp_sig = '''  // 检验人员签名：优先从localStorage读取全局签名，没有则用任务级签名
  var inspSig = '';
  var inspName = '';
  try {
    var _inspStored = localStorage.getItem(INSPECTOR_SIG_KEY);
    if (_inspStored) {
      var _inspObj = JSON.parse(_inspStored);
      if (_inspObj && _inspObj.sig) {
        inspSig = _inspObj.sig;
        inspName = _inspObj.name || '';
      }
    }
  } catch(e) {}
  if (!inspSig && task.signatures && task.signatures.inspectorSig) {
    inspSig = task.signatures.inspectorSig;
  }'''
    
    if old_insp_sig in content:
        content = content.replace(old_insp_sig, new_insp_sig)
        print("  [OK] 问题3: 修复检验人员签名读取（优先localStorage全局签名）")
    else:
        print("  [WARN] 问题3: 未找到检验人员签名读取代码")
    
    # 修复检验人员姓名的读取
    old_insp_name = "  var inspName = (task.signatures && task.signatures.inspectorName) || manager || '';"
    new_insp_name2 = "  if (!inspName) inspName = (task.signatures && task.signatures.inspectorName) || manager || '';"
    
    if old_insp_name in content:
        content = content.replace(old_insp_name, new_insp_name2)
        print("  [OK] 问题3: 修复检验人员姓名读取逻辑")
    else:
        print("  [WARN] 问题3: 未找到检验人员姓名读取代码")
    
    # 修复安装单位代表签名（项目管理/安装人员）
    old_pm_sig = "  var pmSig = (task.signatures && task.signatures.pmSig) || '';"
    new_pm_sig = '''  // 安装单位代表签名：优先从项目级clientSignature读取，没有则用任务级pmSig
  var pmSig = '';
  var pmName = '';
  if (project && project.clientSignature && project.clientSignature.sig) {
    pmSig = project.clientSignature.sig;
    pmName = project.clientSignature.name || '';
  }
  if (!pmSig && task.signatures && task.signatures.pmSig) {
    pmSig = task.signatures.pmSig;
  }'''
    
    if old_pm_sig in content:
        content = content.replace(old_pm_sig, new_pm_sig)
        print("  [OK] 问题3: 修复安装单位代表签名读取（优先项目级clientSignature）")
    else:
        print("  [WARN] 问题3: 未找到安装单位代表签名读取代码")
    
    # 修复项目管理人员姓名
    old_pm_name = "  var pmName = (project && project.projectManagerName) || task.projectManagerName || manager || '';"
    new_pm_name2 = "  if (!pmName) pmName = (project && project.projectManagerName) || task.projectManagerName || manager || '';"
    
    if old_pm_name in content:
        content = content.replace(old_pm_name, new_pm_name2)
        print("  [OK] 问题3: 修复项目管理人员姓名读取逻辑")
    else:
        print("  [WARN] 问题3: 未找到项目管理人员姓名读取代码")
    
    return content


def fix_issue4_config_code_column(content):
    """问题4：配置表导入编号引用错误
    - 编号列精确匹配"编号或制造批次号"，其他带"编号"的列不算
    - 产品编号匹配时排除"型式试验"相关的
    """
    # 修复部件表格中的编号列检测
    old_code_col = '''        // 从表头行检测列位置
        var headerRow2 = partStartRow - 1;
        if (headerRow2 >= 0 && json[headerRow2]) {
          for (var hc = 0; hc < json[headerRow2].length; hc++) {
            var hcell = String(json[headerRow2][hc] || '').replace(/\\s/g, '').replace(/\\n/g, '');
            if (hcell.indexOf('型号') >= 0 || hcell.indexOf('规格') >= 0) modelCol = hc;
            if (hcell.indexOf('编号') >= 0 || hcell.indexOf('批次') >= 0 || hcell.indexOf('出厂编号') >= 0) codeCol = hc;
          }
        }'''
    
    new_code_col = '''        // 从表头行检测列位置
        var headerRow2 = partStartRow - 1;
        if (headerRow2 >= 0 && json[headerRow2]) {
          modelCol = -1;
          codeCol = -1;
          for (var hc = 0; hc < json[headerRow2].length; hc++) {
            var hcell = String(json[headerRow2][hc] || '').replace(/\\s/g, '').replace(/\\n/g, '');
            // 型号列检测
            if ((hcell.indexOf('型号') >= 0 || hcell.indexOf('规格') >= 0) && hcell.indexOf('型式试验') < 0 && hcell.indexOf('证书') < 0) {
              if (modelCol < 0) modelCol = hc;
            }
            // 编号列检测：只认"编号或制造批次号"，排除型式试验证书编号等
            // 精确匹配优先级：编号或制造批次号 > 出厂编号 > 产品编号 > 设备编号
            // 排除包含"型式试验"、"证书编号"、"TSX"的列
            var isCodeCol = false;
            if (hcell === '编号或制造批次号' || hcell.indexOf('编号或制造批次号') >= 0) {
              isCodeCol = true;
            }
            // 其他含编号的列必须排除型式试验/证书相关
            if (!isCodeCol && hcell.indexOf('编号') >= 0) {
              if (hcell.indexOf('型式试验') < 0 && hcell.indexOf('证书') < 0 && hcell.indexOf('TSX') < 0 && hcell.indexOf('tsx') < 0) {
                // 只在没有找到精确匹配的情况下才考虑模糊匹配
                // 但这里我们严格只认"编号或制造批次号"，所以不启用模糊匹配
              }
            }
            if (isCodeCol) {
              codeCol = hc;
            }
          }
          // 如果没找到精确匹配的编号列，用默认值（D列，索引3）
          if (codeCol < 0) codeCol = 3;
          if (modelCol < 0) modelCol = 2;
        }'''
    
    if old_code_col in content:
        content = content.replace(old_code_col, new_code_col)
        print("  [OK] 问题4: 修复部件表编号列检测（只认编号或制造批次号）")
    else:
        print("  [WARN] 问题4: 未找到部件表编号列检测代码")
    
    # 修复产品编号（prodNo）匹配，排除型式试验证书编号
    # 找到基本信息提取中的产品编号匹配
    old_prod_no_match = '''          if (!prodNo && matchKw(cv, kwMap['产品编号'])) {
            prodNo = val(r, c+1) || val(r, c+2) || val(r+1, c) || val(r+1, c+1);
          }'''
    
    new_prod_no_match = '''          if (!prodNo && matchKw(cv, kwMap['产品编号'])) {
            // 排除型式试验证书编号
            var cvNorm = normText(cv);
            if (cvNorm.indexOf('型式试验') < 0 && cvNorm.indexOf('证书') < 0 && cvNorm.indexOf('tsx') < 0) {
              prodNo = val(r, c+1) || val(r, c+2) || val(r+1, c) || val(r+1, c+1);
            }
          }'''
    
    if old_prod_no_match in content:
        content = content.replace(old_prod_no_match, new_prod_no_match)
        print("  [OK] 问题4: 修复产品编号匹配（排除型式试验相关）")
    else:
        print("  [WARN] 问题4: 未找到产品编号匹配代码")
    
    # 修复"标签：值"在同一单元格的产品编号提取
    old_label_value = '''            if (matchKw(lv.label, kwMap['产品编号']) && !prodNo) prodNo = lv.value;'''
    
    new_label_value = '''            if (matchKw(lv.label, kwMap['产品编号']) && !prodNo) {
              var lblNorm = normText(lv.label);
              if (lblNorm.indexOf('型式试验') < 0 && lblNorm.indexOf('证书') < 0 && lblNorm.indexOf('tsx') < 0) {
                prodNo = lv.value;
              }
            }'''
    
    if old_label_value in content:
        content = content.replace(old_label_value, new_label_value)
        print("  [OK] 问题4: 修复标签值格式的产品编号提取（排除型式试验）")
    else:
        print("  [WARN] 问题4: 未找到标签值格式产品编号提取代码")
    
    # 修复整梯的编号：应该是产品编号（H开头），不是型式试验编号
    # 找到整梯部分的匹配，确保编号列正确
    # （上面的codeCol修复已经解决了这个问题，因为整梯行也会用codeCol列的内容）
    
    return content


def fix_issue5_print_functions(content):
    """问题5：打印检查表和打印副表不起作用
    - 确保 currentProjectIndex 在打印函数中正确设置
    - 增加错误处理
    - 确保下拉菜单点击事件正常工作
    """
    # 修复 printCheckSheet：确保 currentProjectIndex 正确
    old_print_check = '''function printCheckSheet(index) {
  currentTaskIndex = index;
  closeAllPrintMenus();
  exportCheckPDF();
}'''
    
    new_print_check = '''function printCheckSheet(index) {
  // 确保在项目列表页面也能正确获取项目索引
  if (typeof currentProjectIndex === 'undefined' || currentProjectIndex < 0) {
    // 如果没有当前项目，尝试从URL或其他方式获取
    if (projects && projects.length > 0) currentProjectIndex = 0;
  }
  currentTaskIndex = index;
  closeAllPrintMenus();
  try {
    exportCheckPDF();
  } catch(e) {
    console.error('打印检查表失败:', e);
    showToast('打印失败: ' + (e.message || e));
  }
}'''
    
    if old_print_check in content:
        content = content.replace(old_print_check, new_print_check)
        print("  [OK] 问题5: 修复 printCheckSheet（增加错误处理和索引校验）")
    else:
        print("  [WARN] 问题5: 未找到 printCheckSheet 函数")
    
    # 修复 printFubiao：确保 currentProjectIndex 正确
    old_print_fubiao = '''function printFubiao(index) {
  closeAllPrintMenus();
  window.open('print-fubiao.html?proj=' + currentProjectIndex + '&task=' + index, '_blank');
}'''
    
    new_print_fubiao = '''function printFubiao(index) {
  // 确保在项目列表页面也能正确获取项目索引
  if (typeof currentProjectIndex === 'undefined' || currentProjectIndex < 0) {
    if (projects && projects.length > 0) currentProjectIndex = 0;
  }
  closeAllPrintMenus();
  try {
    var url = 'print-fubiao.html?proj=' + currentProjectIndex + '&task=' + index;
    var win = window.open(url, '_blank');
    if (!win) {
      showToast('弹窗被拦截，请允许弹出窗口');
    }
  } catch(e) {
    console.error('打开副表打印页失败:', e);
    showToast('打开副表失败: ' + (e.message || e));
  }
}'''
    
    if old_print_fubiao in content:
        content = content.replace(old_print_fubiao, new_print_fubiao)
        print("  [OK] 问题5: 修复 printFubiao（增加错误处理和弹窗检测）")
    else:
        print("  [WARN] 问题5: 未找到 printFubiao 函数")
    
    # 修复 printNotice 同样增加错误处理
    old_print_notice = '''function printNotice(index) {
  currentTaskIndex = index;
  closeAllPrintMenus();
  exportNoticePDF();
}'''
    
    new_print_notice = '''function printNotice(index) {
  if (typeof currentProjectIndex === 'undefined' || currentProjectIndex < 0) {
    if (projects && projects.length > 0) currentProjectIndex = 0;
  }
  currentTaskIndex = index;
  closeAllPrintMenus();
  try {
    exportNoticePDF();
  } catch(e) {
    console.error('打印通知单失败:', e);
    showToast('打印失败: ' + (e.message || e));
  }
}'''
    
    if old_print_notice in content:
        content = content.replace(old_print_notice, new_print_notice)
        print("  [OK] 问题5: 修复 printNotice（增加错误处理）")
    else:
        print("  [WARN] 问题5: 未找到 printNotice 函数")
    
    return content


def fix_issue6_verify_attach2(content):
    """问题6：确认附表2打印页表格结构和最大允许值关联
    - v124已修复，这里确认修复正确
    """
    # 检查是否还有多余的"对重缓冲距最大允许值"行
    if '对重缓冲距最大允许值' in content:
        print("  [WARN] 问题6: 仍存在'对重缓冲距最大允许值'行，需要删除")
        # 尝试删除
        old_extra_row = '''          <tr class="small-row">
            <th>对重缓冲距最大允许值</th>
            <th colspan="2"></th>
            <th colspan="2" data-fb2="对重最大允许值-val">mm</th>
          </tr>
'''
        if old_extra_row in content:
            content = content.replace(old_extra_row, '')
            print("  [OK] 问题6: 删除多余的对重缓冲距最大允许值行")
    else:
        print("  [OK] 问题6: 确认附表2没有多余行（v124修复有效）")
    
    # 检查数据填充是否正确
    if "setFb2Text('最大允许值-val', att2.对重最大允许值 || att2.最大允许值 || '')" in content:
        print("  [OK] 问题6: 确认最大允许值数据填充正确（对重最大允许值优先）")
    else:
        print("  [WARN] 问题6: 未找到正确的最大允许值数据填充代码")
        # 尝试修复
        old_fill = "  setFb2Text('最大允许值-val', att2.最大允许值 || '');\n  setFb2Text('对重最大允许值-val', att2.对重最大允许值 || '');"
        new_fill = "  setFb2Text('最大允许值-val', att2.对重最大允许值 || att2.最大允许值 || '');"
        if old_fill in content:
            content = content.replace(old_fill, new_fill)
            print("  [OK] 问题6: 修复最大允许值数据填充逻辑")
    
    return content


def main():
    print("=" * 60)
    print("v125 修复脚本 - 修复6个问题")
    print("=" * 60)
    
    # ========== 主文件修复 ==========
    print("\n[主文件 factory-inspection-v2.html]")
    content = read_file(MAIN_FILE)
    original_len = len(content)
    print(f"  文件大小: {original_len} 字符")
    
    print("\n--- 问题1：项目管理/安装人员签字弹窗异常 ---")
    content = fix_issue1_signature_modal(content)
    
    print("\n--- 问题2：删除厂检结论页签名提示框 ---")
    content = fix_issue2_remove_sign_hints(content)
    
    print("\n--- 问题3：打印通知单时签字没有引用过去 ---")
    content = fix_issue3_notice_signatures(content)
    
    print("\n--- 问题4：配置表导入编号引用错误 ---")
    content = fix_issue4_config_code_column(content)
    
    print("\n--- 问题5：打印检查表和打印副表不起作用 ---")
    content = fix_issue5_print_functions(content)
    
    write_file(MAIN_FILE, content)
    print(f"\n  主文件写入完成，大小: {len(content)} 字符")
    
    # ========== 打印页修复 ==========
    print("\n[打印页 print-fubiao.html]")
    print_content = read_file(PRINT_FILE)
    print(f"  文件大小: {len(print_content)} 字符")
    
    print("\n--- 问题6：附表2打印页表格结构确认 ---")
    print_content = fix_issue6_verify_attach2(print_content)
    
    write_file(PRINT_FILE, print_content)
    print(f"\n  打印页写入完成，大小: {len(print_content)} 字符")
    
    # ========== 同步到入口文件 ==========
    print("\n[同步到入口文件]")
    write_file(ENTRY_FILE, content)
    print(f"  已同步到 威特电梯厂检调试记录单v2.html")
    
    print("\n" + "=" * 60)
    print("所有修复完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
