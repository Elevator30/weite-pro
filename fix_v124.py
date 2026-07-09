#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v124 修复脚本 - 修复v123引入的7个问题
"""
import re
import os

MAIN_FILE = '/app/data/所有对话/主对话/weite-pro-temp/factory-inspection-v2.html'
PRINT_FILE = '/app/data/所有对话/主对话/weite-pro-temp/print-fubiao.html'
ENTRY_FILE = '/app/data/所有对话/主对话/weite-pro-temp/威特电梯厂检调试记录单v2.html'

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_issue1_modal_height(content):
    """问题1：所有弹窗内容被截断/变矮
    - .att-card 的 overflow:hidden 导致内部内容被截断
    - 修复：改为 overflow:visible
    """
    old = '.att-card{background:#fff;border-radius:12px;padding:14px;margin-bottom:12px;border:1.5px solid #e2e8f0;;overflow:hidden}'
    new = '.att-card{background:#fff;border-radius:12px;padding:14px;margin-bottom:12px;border:1.5px solid #e2e8f0;overflow:visible}'
    if old in content:
        content = content.replace(old, new)
        print("  [OK] 问题1: 修复 .att-card overflow:hidden -> visible")
    else:
        print("  [WARN] 问题1: 未找到 .att-card 的 overflow:hidden")
    
    # 修复 .mb 的 max-height，确保有足够的滚动空间
    # 同时确保 .mb 有正确的滚动行为
    old_mb = '.mb{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:12px 14px 20px;max-height:calc(90vh - 60px);}'
    new_mb = '.mb{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:12px 14px 20px;max-height:calc(90vh - 60px);min-height:0;}'
    if old_mb in content:
        content = content.replace(old_mb, new_mb)
        print("  [OK] 问题1: 修复 .mb 添加 min-height:0 确保flex子项正确滚动")
    else:
        print("  [WARN] 问题1: 未找到 .mb CSS定义")
    
    return content

def fix_issue2_close_att_modal(content):
    """问题2：附表1关闭后弹出"选择附表"中间层
    - closeAttModal() 里调用了 showAttButtonsModal()，多此一步
    - 修复：删除 closeAttModal 里的 showAttButtonsModal() 调用
    """
    old = """function closeAttModal() {
  var mo = document.getElementById('moAtt');
  if (mo) mo.style.display = 'none';
  closeMoBody();
  // 回到附表按钮列表
  showAttButtonsModal();
}"""
    new = """function closeAttModal() {
  var mo = document.getElementById('moAtt');
  if (mo) mo.style.display = 'none';
  closeMoBody();
}"""
    if old in content:
        content = content.replace(old, new)
        print("  [OK] 问题2: 删除 closeAttModal 中的 showAttButtonsModal() 调用")
    else:
        print("  [WARN] 问题2: 未找到 closeAttModal 函数的原始代码")
        # 尝试另一种匹配方式
        pattern = r'function closeAttModal\(\) \{[^}]+\}'
        match = re.search(pattern, content)
        if match:
            print("  [INFO] 找到 closeAttModal:", match.group()[:100])
    
    return content

def fix_issue3_print_fubiao(content):
    """问题3：附表2打印页表格多加了一行
    - v123给附表2打印页加了"对重缓冲距最大允许值"的行
    - 修复：删除新加的行，保持原始表格结构
    """
    # 新加的行（第三行），需要删除
    old_row = '''          <tr class="small-row">
            <th>对重缓冲距最大允许值</th>
            <th colspan="2"></th>
            <th colspan="2" data-fb2="对重最大允许值-val">mm</th>
          </tr>
'''
    if old_row in content:
        content = content.replace(old_row, '')
        print("  [OK] 问题3: 删除 print-fubiao.html 中多余的对重缓冲距最大允许值行")
    else:
        print("  [WARN] 问题3: 未找到多余的表格行（print-fubiao.html）")
    
    # 修复JS中的数据填充：把对重最大允许值填到原来的"最大允许值-val"位置
    # 原来有两行：
    #   setFb2Text('最大允许值-val', att2.最大允许值 || '');
    #   setFb2Text('对重最大允许值-val', att2.对重最大允许值 || '');
    # 改为：如果 att2.对重最大允许值 有值，优先用它填充最大允许值-val
    old_js = "  setFb2Text('最大允许值-val', att2.最大允许值 || '');\n  setFb2Text('对重最大允许值-val', att2.对重最大允许值 || '');"
    new_js = "  setFb2Text('最大允许值-val', att2.对重最大允许值 || att2.最大允许值 || '');"
    if old_js in content:
        content = content.replace(old_js, new_js)
        print("  [OK] 问题3: 修复JS数据填充，对重最大允许值填到原最大允许值位置")
    else:
        print("  [WARN] 问题3: 未找到JS中的数据填充代码（print-fubiao.html）")
    
    return content

def fix_issue4_signature(content):
    """问题4：所有签字都不行
    - canvas初始化时机问题（display:none时offsetWidth为0）
    - 修复：确保弹窗显示后再初始化canvas，增加延迟，用getBoundingClientRect兜底
    """
    # 修复1：openClientSignature 中增加canvas初始化的可靠性
    # 问题：setTimeout 300ms可能不够，或者弹窗还没完全显示
    old_open_client = '''  // 初始化画布（使支持绘制）
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
  }, 300);'''
    new_open_client = '''  // 初始化画布（使支持绘制）- 确保弹窗显示后再初始化
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
  }, 100);
  // 第二帧再初始化一次，确保尺寸正确
  setTimeout(function() {
    var cB2 = document.getElementById('sigCanvasBuilder');
    var cI2 = document.getElementById('sigCanvasInspector');
    if (cB2 && (cB2.width === 0 || cB2.width === 300)) {
      var w3 = cB2.offsetWidth || cB2.parentElement.offsetWidth || 300;
      if (w3 > 0 && w3 !== cB2.width) {
        cB2.width = w3;
        cB2.height = 80;
        initSigCanvasFor('Builder');
        // 恢复签名
        if (proj.clientSignature && proj.clientSignature.sig) {
          var ctx2 = cB2.getContext('2d');
          var img2 = new Image();
          img2.onload = function() { ctx2.drawImage(img2, 0, 0, cB2.width, cB2.height); };
          img2.src = proj.clientSignature.sig;
        }
      }
    }
    if (cI2 && (cI2.width === 0 || cI2.width === 300)) {
      var w4 = cI2.offsetWidth || cI2.parentElement.offsetWidth || 300;
      if (w4 > 0 && w4 !== cI2.width) {
        cI2.width = w4;
        cI2.height = 80;
        initSigCanvasFor('Inspector');
      }
    }
  }, 400);'''
    if old_open_client in content:
        content = content.replace(old_open_client, new_open_client)
        print("  [OK] 问题4: 修复 openClientSignature 中canvas初始化时机")
    else:
        print("  [WARN] 问题4: 未找到 openClientSignature 中的初始化代码")
    
    # 修复2：initSigCanvasFor 函数增强，确保canvas尺寸正确
    old_init_for = '''function initSigCanvasFor(suffix) {
  var canvas = document.getElementById('sigCanvas' + suffix);
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var drawing = false;
  canvas.width = canvas.offsetWidth || 300;
  canvas.height = 80;'''
    new_init_for = '''function initSigCanvasFor(suffix) {
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
    if old_init_for in content:
        content = content.replace(old_init_for, new_init_for)
        print("  [OK] 问题4: 增强 initSigCanvasFor 的宽度计算")
    else:
        print("  [WARN] 问题4: 未找到 initSigCanvasFor 函数")
    
    # 修复3：全屏签字弹窗 initSigCanvas 也增强
    old_init_sig = '''function initSigCanvas() {
  var canvas = document.getElementById('sigCanvas');
  var container = document.getElementById('sigCanvasC');
  canvas.width = container.offsetWidth;
  canvas.height = container.offsetHeight;'''
    new_init_sig = '''function initSigCanvas() {
  var canvas = document.getElementById('sigCanvas');
  var container = document.getElementById('sigCanvasC');
  // 确保容器有尺寸，用getBoundingClientRect更可靠
  var w = container.offsetWidth;
  var h = container.offsetHeight;
  if (!w || w < 50) {
    var rect = container.getBoundingClientRect();
    w = rect.width || window.innerWidth * 0.9;
    h = rect.height || window.innerHeight * 0.6;
  }
  canvas.width = w || 300;
  canvas.height = h || 200;'''
    if old_init_sig in content:
        content = content.replace(old_init_sig, new_init_sig)
        print("  [OK] 问题4: 增强全屏签字 initSigCanvas 的尺寸计算")
    else:
        print("  [WARN] 问题4: 未找到 initSigCanvas 函数")
    
    # 修复4：openSignZoneModal 中的 initSigCanvas 调用时机
    old_open_zone = '''  document.getElementById('sigModal').style.display = 'flex';
  setTimeout(function() { initSigCanvas(); }, 100);'''
    new_open_zone = '''  document.getElementById('sigModal').style.display = 'flex';
  // 立即初始化 + 延迟再初始化，确保canvas尺寸正确
  setTimeout(function() { initSigCanvas(); }, 50);
  setTimeout(function() { 
    var canvas = document.getElementById('sigCanvas');
    var container = document.getElementById('sigCanvasC');
    if (canvas && container && (canvas.width === 0 || canvas.width < 100)) {
      initSigCanvas();
      // 如果有已保存的签名，重新加载
      if (signZoneTarget && signZoneTarget === 'inspector') {
        var savedSig = localStorage.getItem('inspectorSignature');
        if (savedSig) {
          var ctx = canvas.getContext('2d');
          var img = new Image();
          img.onload = function() { ctx.drawImage(img, 0, 0, canvas.width, canvas.height); };
          img.src = savedSig;
        }
      }
    }
  }, 300);'''
    # 替换两个地方的 openSignZoneModal 和 openInspectorSigSetting
    count = content.count(old_open_zone)
    if count > 0:
        content = content.replace(old_open_zone, new_open_zone)
        print(f"  [OK] 问题4: 修复 {count} 处签字弹窗的初始化时机")
    else:
        print("  [WARN] 问题4: 未找到签字弹窗初始化代码")
    
    # 修复5：openInspectorSigSetting 也需要同样的修复
    old_open_inspector = '''  document.getElementById('sigModal').style.display = 'flex';
  setTimeout(function() { initSigCanvas(); }, 100);
}

function openSignZoneModal(target) {'''
    
    if old_open_inspector in content:
        # 已经在上面替换过了
        pass
    
    return content

def fix_issue5_page_shake(content):
    """问题5：点击符合/不符合/不适用页面还是闪/抖动
    - 真正原因：三个按钮的选中/未选中状态的高度不一致导致重排
    - 修复：给radio-group加固定高度，确保选中和未选中状态高度完全一致
    """
    old = '.radio-group{display:flex;gap:6px;margin-top:4px;}'
    new = '.radio-group{display:flex;gap:6px;margin-top:4px;height:34px;flex-shrink:0;}'
    if old in content:
        content = content.replace(old, new)
        print("  [OK] 问题5: 给 .radio-group 加固定高度 height:34px")
    else:
        print("  [WARN] 问题5: 未找到 .radio-group CSS")
    
    # 同时给 ck-row-top 也加固定高度相关，防止行高变化
    old_row_top = '.ck-row-top{display:flex;align-items:flex-start;gap:8px;}'
    new_row_top = '.ck-row-top{display:flex;align-items:flex-start;gap:8px;min-height:60px;}'
    if old_row_top in content:
        content = content.replace(old_row_top, new_row_top)
        print("  [OK] 问题5: 给 .ck-row-top 加 min-height:60px")
    else:
        print("  [WARN] 问题5: 未找到 .ck-row-top CSS")
    
    # 优化 setCheckStatus：减少重渲染，优先只更新当前行
    # （保留v123的minHeight方案，但优化逻辑）
    return content

def fix_issue6_button_sensitivity(content):
    """问题6：附表1轿前门/轿后门按钮不灵敏
    - 按钮高度太小，点击区域不够
    - 修复：增加按钮高度和点击区域
    """
    # 中分门/旁开门按钮增加高度（从30px增加到36px）
    # 按钮1：中分门
    old_btn_center = '''html += '<div onclick="setAtt1DoorStructure(&#39;center&#39;)" style="padding:0 12px;height:30px;padding:0 8px;display:inline-flex;align-items:center;border-radius:5px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.15s;border:1.5px solid ' + (doorStruct === 'center' ? '#667eea' : '#e2e8f0') + ';background:' + (doorStruct === 'center' ? 'linear-gradient(135deg,#667eea,#764ba2)' : '#fff') + ';color:' + (doorStruct === 'center' ? '#fff' : '#718096') + ';box-sizing:border-box;">中分门</div>';'''
    new_btn_center = '''html += '<div onclick="setAtt1DoorStructure(&#39;center&#39;)" style="padding:0 14px;height:36px;min-width:60px;display:inline-flex;align-items:center;justify-content:center;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;transition:all 0.15s;border:1.5px solid ' + (doorStruct === 'center' ? '#667eea' : '#e2e8f0') + ';background:' + (doorStruct === 'center' ? 'linear-gradient(135deg,#667eea,#764ba2)' : '#fff') + ';color:' + (doorStruct === 'center' ? '#fff' : '#718096') + ';box-sizing:border-box;-webkit-tap-highlight-color:transparent;user-select:none;">中分门</div>';'''
    if old_btn_center in content:
        content = content.replace(old_btn_center, new_btn_center)
        print("  [OK] 问题6: 增大中分门按钮点击区域")
    else:
        print("  [WARN] 问题6: 未找到中分门按钮代码")
    
    # 按钮2：旁开门
    old_btn_side = '''html += '<div onclick="setAtt1DoorStructure(&#39;side&#39;)" style="padding:0 12px;height:30px;padding:0 8px;display:inline-flex;align-items:center;border-radius:5px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.15s;border:1.5px solid ' + (doorStruct === 'side' ? '#667eea' : '#e2e8f0') + ';background:' + (doorStruct === 'side' ? 'linear-gradient(135deg,#667eea,#764ba2)' : '#fff') + ';color:' + (doorStruct === 'side' ? '#fff' : '#718096') + ';box-sizing:border-box;">旁开门</div>';'''
    new_btn_side = '''html += '<div onclick="setAtt1DoorStructure(&#39;side&#39;)" style="padding:0 14px;height:36px;min-width:60px;display:inline-flex;align-items:center;justify-content:center;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;transition:all 0.15s;border:1.5px solid ' + (doorStruct === 'side' ? '#667eea' : '#e2e8f0') + ';background:' + (doorStruct === 'side' ? 'linear-gradient(135deg,#667eea,#764ba2)' : '#fff') + ';color:' + (doorStruct === 'side' ? '#fff' : '#718096') + ';box-sizing:border-box;-webkit-tap-highlight-color:transparent;user-select:none;">旁开门</div>';'''
    if old_btn_side in content:
        content = content.replace(old_btn_side, new_btn_side)
        print("  [OK] 问题6: 增大旁开门按钮点击区域")
    else:
        print("  [WARN] 问题6: 未找到旁开门按钮代码")
    
    # 下拉框也增加高度，保持一致
    old_select = '''html += '<select id="att1DoorType" onchange="changeAtt1DoorType(this.value)" style="flex:1;height:30px;border:1px solid #ddd;border-radius:5px;padding:0 8px;font-size:12px;min-width:0;box-sizing:border-box;">';'''
    new_select = '''html += '<select id="att1DoorType" onchange="changeAtt1DoorType(this.value)" style="flex:1;height:36px;border:1px solid #ddd;border-radius:6px;padding:0 8px;font-size:13px;min-width:0;box-sizing:border-box;">';'''
    if old_select in content:
        content = content.replace(old_select, new_select)
        print("  [OK] 问题6: 增大门类型下拉框高度")
    else:
        print("  [WARN] 问题6: 未找到门类型下拉框代码")
    
    return content

def fix_issue7_config_import(content):
    """问题7：配置表导入功能改进
    - 从固定列名改为关键词模糊匹配
    - 支持的字段：产品型号、产品编号、额定载重、额定速度、提升高度、层站门、
      控制柜型号、控制柜编号、曳引机型号、限速器型号、安全钳型号、缓冲器型号等
    """
    # 找到 handleConfigUpload 函数，替换其中的解析逻辑
    # 我们在函数开头加入一个模糊匹配辅助函数，然后修改匹配逻辑
    
    # 1. 首先添加关键词匹配辅助函数（在函数开头）
    # 2. 修改额定载重量/额定速度的匹配为模糊匹配
    # 3. 修改部件表匹配为模糊匹配
    
    # 找到 handleConfigUpload 函数开始位置
    func_start = content.find('function handleConfigUpload(input) {')
    if func_start < 0:
        print("  [ERROR] 问题7: 未找到 handleConfigUpload 函数")
        return content
    
    # 在函数内部添加关键词匹配工具函数
    insert_point = content.find('configPartsData = {};', func_start)
    if insert_point < 0:
        print("  [WARN] 问题7: 未找到 configPartsData 初始化位置")
        return content
    
    # 插入关键词匹配辅助函数和字段映射配置
    helper_code = '''
      // === 关键词模糊匹配工具 ===
      var kwMap = {
        // 基本信息字段
        '产品编号': ['产品编号', '产品编码', '产品代码', '出厂编号', '设备编号'],
        '产品型号': ['产品型号', '型号', '设备型号', '规格型号'],
        '项目名称': ['项目名称', '项目', '工程名称', '客户名称', '使用单位'],
        '额定载重量': ['额定载重量', '额定载荷', '载重量', '载重', '额定载重', '载荷'],
        '额定速度': ['额定速度', '速度', '运行速度'],
        '提升高度': ['提升高度', '行程', '提升行程'],
        '层站门': ['层/站/门', '层站门', '层数', '站数', '层站', '楼层数'],
        // 部件字段
        '控制柜_型号': ['控制柜'],
        '控制柜_编号': ['控制柜编号', '控制柜编号或'],
        '驱动主机_型号': ['驱动主机', '曳引机', '主机'],
        '驱动主机_编号': ['驱动主机编号', '曳引机编号', '主机编号'],
        '限速器_型号': ['限速器'],
        '限速器_编号': ['限速器编号'],
        '安全钳_型号': ['安全钳'],
        '安全钳_编号': ['安全钳编号'],
        '缓冲器_型号': ['缓冲器'],
        '缓冲器_编号': ['缓冲器编号'],
        '上行超速_型号': ['上行超速', '轿厢上行超速'],
        '上行超速_编号': ['上行超速编号'],
        '意外移动_型号': ['意外移动', '轿厢意外移动'],
        '意外移动_编号': ['意外移动编号'],
        '层门锁_型号': ['层门门锁', '层门锁'],
        '层门锁_编号': ['层门锁编号'],
        '轿门锁_型号': ['轿门门锁', '轿门锁'],
        '轿门锁_编号': ['轿门锁编号'],
        '层门_型号': ['层门'],
        '层门_编号': ['层门编号'],
        '安全电路_型号': ['安全电路', '含有电子元件的安全电路'],
        '安全电路_编号': ['安全电路编号'],
        '整梯_型号': ['乘客电梯', '载货电梯', '曳引驱动', '整梯', '电梯整机'],
        '整梯_编号': ['整梯编号']
      };
      
      // 关键词匹配函数：检查文本是否包含任意关键词
      function matchKw(text, keywords) {
        if (!text) return false;
        var t = String(text).replace(/\\s/g, '').replace(/\\n/g, '');
        for (var ki = 0; ki < keywords.length; ki++) {
          if (t.indexOf(keywords[ki]) >= 0) return true;
        }
        return false;
      }
      
      // 从单元格文本中提取标签和值（支持"标签：值"格式）
      function extractLabelValue(text) {
        if (!text) return null;
        var t = String(text).trim();
        // 处理中文冒号
        var colonIdx = t.indexOf('：');
        if (colonIdx < 0) colonIdx = t.indexOf(':');
        if (colonIdx > 0) {
          return {label: t.substring(0, colonIdx).trim(), value: t.substring(colonIdx + 1).trim()};
        }
        return null;
      }
      
      // 规范化文本：去空格、去换行、统一大小写
      function normText(s) {
        return String(s || '').replace(/\\s/g, '').replace(/\\n/g, '').toLowerCase();
      }

'''
    
    content = content[:insert_point] + helper_code + content[insert_point:]
    print("  [OK] 问题7: 添加关键词模糊匹配工具函数")
    
    # 2. 修改基本信息提取（产品编号、项目名称、产品型号）为模糊匹配
    # 原来的精确匹配改为关键词匹配
    
    old_basic_extract = '''      // === 1. 提取基本信息（前4行） ===
      for (var r = 0; r < 5; r++) {
        for (var c = 0; c < 15; c++) {
          var cv = val(r, c);
          if (!cv) continue;
          // "标签：值"在同一单元格
          if (cv.indexOf('：') > 0) {
            var ci = cv.indexOf('：');
            var label = cv.substring(0, ci).trim();
            var value = cv.substring(ci + 1).trim();
            if (label === '产品编号' && !prodNo) prodNo = value;
            if (label === '项目名称' && !addr) addr = value;
          }
          // "标签：值"在不同单元格
          if (cv === '产品编号' && !prodNo) prodNo = val(r, c+1) || val(r, c+2);
          if (cv === '项目名称' && !addr) addr = val(r, c+1) || val(r, c+2);
          // 产品型号前缀（如TKJ/TKJW）- 检查多个可能的位置
          if ((cv === '产品型号' || cv === '型号') && !modelPrefix) {
            modelPrefix = val(r, c+1) || val(r, c+2) || val(r+1, c) || val(r+1, c+1);
            // 如果提取到的是中文描述而不是型号前缀，跳过
            if (modelPrefix && /[\\u4e00-\\u9fa5]/.test(modelPrefix)) {
              modelPrefix = '';
            }
          }
        }
      }'''
    
    new_basic_extract = '''      // === 1. 提取基本信息（前10行，关键词模糊匹配） ===
      for (var r = 0; r < 10; r++) {
        for (var c = 0; c < 20; c++) {
          var cv = val(r, c);
          if (!cv) continue;
          // "标签：值"在同一单元格
          var lv = extractLabelValue(cv);
          if (lv) {
            if (matchKw(lv.label, kwMap['产品编号']) && !prodNo) prodNo = lv.value;
            if (matchKw(lv.label, kwMap['项目名称']) && !addr) addr = lv.value;
            if (matchKw(lv.label, kwMap['产品型号']) && !modelPrefix) {
              if (!/[\\u4e00-\\u9fa5]/.test(lv.value)) modelPrefix = lv.value;
            }
            if (matchKw(lv.label, kwMap['额定载重量']) && !loadWeight) {
              var lw = lv.value.replace(/[kK][gG]/gi, '').replace(/公斤/g, '').replace(/kg/gi, '').trim();
              if (lw && !isNaN(parseFloat(lw))) loadWeight = lw;
            }
            if (matchKw(lv.label, kwMap['额定速度']) && !speed) {
              var sp = lv.value.replace(/[mM]\\/[sS]/gi, '').replace(/米\\/秒/g, '').replace(/m\\/s/gi, '').trim();
              if (sp && !isNaN(parseFloat(sp))) speed = sp;
            }
            if (matchKw(lv.label, kwMap['提升高度'])) {
              // 先不直接赋值，在参数表中统一处理
            }
          }
          // "标签：值"在不同单元格（标签在左，值在右）
          if (!prodNo && matchKw(cv, kwMap['产品编号'])) {
            prodNo = val(r, c+1) || val(r, c+2) || val(r+1, c) || val(r+1, c+1);
          }
          if (!addr && matchKw(cv, kwMap['项目名称'])) {
            addr = val(r, c+1) || val(r, c+2) || val(r+1, c) || val(r+1, c+1);
          }
          // 产品型号前缀（如TKJ/TKJW）- 关键词匹配
          if (!modelPrefix && matchKw(cv, kwMap['产品型号'])) {
            var mp = val(r, c+1) || val(r, c+2) || val(r+1, c) || val(r+1, c+1);
            // 如果提取到的不是纯中文描述，可能是型号
            if (mp && !/[\\u4e00-\\u9fa5]/.test(mp)) {
              modelPrefix = mp;
            } else if (mp) {
              // 如果是中文，跳过（可能是"主要技术参数"等描述）
            }
          }
        }
      }'''
    
    if old_basic_extract in content:
        content = content.replace(old_basic_extract, new_basic_extract)
        print("  [OK] 问题7: 基本信息提取改为关键词模糊匹配")
    else:
        print("  [WARN] 问题7: 未找到基本信息提取代码块")
    
    # 3. 修改额定载重量和额定速度的表头匹配为模糊匹配
    old_load_speed = '''      var loadCol = -1, speedCol = -1, headerRow = -1;
      for (var r2 = 0; r2 < 15; r2++) {
        for (var c2 = 0; c2 < 20; c2++) {
          var cv2 = val(r2, c2);
          if (cv2 === '额定载重量' || cv2 === '额定载荷') { loadCol = c2; headerRow = r2; }
          if (cv2 === '额定速度') { speedCol = c2; if (headerRow < 0) headerRow = r2; }
        }
      }'''
    
    new_load_speed = '''      var loadCol = -1, speedCol = -1, heightCol = -1, floorsCol = -1, headerRow = -1;
      for (var r2 = 0; r2 < 15; r2++) {
        for (var c2 = 0; c2 < 20; c2++) {
          var cv2 = val(r2, c2);
          if (!cv2) continue;
          if (matchKw(cv2, kwMap['额定载重量'])) { loadCol = c2; headerRow = r2; }
          if (matchKw(cv2, kwMap['额定速度'])) { speedCol = c2; if (headerRow < 0) headerRow = r2; }
          if (matchKw(cv2, kwMap['提升高度'])) { heightCol = c2; if (headerRow < 0) headerRow = r2; }
          if (matchKw(cv2, kwMap['层站门'])) { floorsCol = c2; if (headerRow < 0) headerRow = r2; }
        }
      }'''
    
    if old_load_speed in content:
        content = content.replace(old_load_speed, new_load_speed)
        print("  [OK] 问题7: 额定载重/速度表头匹配改为关键词匹配")
    else:
        print("  [WARN] 问题7: 未找到载重速度表头匹配代码")
    
    # 4. 在数据行提取部分也加入提升高度和层站门
    old_data_row = '''        for (var dr = 1; dr <= 10; dr++) {
          if (loadCol >= 0 && !loadWeight) {
            var lv = val(headerRow + dr, loadCol);
            if (lv && /\\d/.test(lv)) {
              loadWeight = lv.replace(/[kK][gG]/g, '').replace(/公斤/g, '').trim();
            }
          }
          if (speedCol >= 0 && !speed) {
            var sv = val(headerRow + dr, speedCol);
            if (sv && /\\d/.test(sv)) {
              speed = sv.replace(/[mM]\\/[sS]/g, '').replace(/米\\/秒/g, '').replace(/m\\/s/gi, '').trim();
            }
          }
          if (loadWeight && speed) break;
        }'''
    
    new_data_row = '''        for (var dr = 1; dr <= 10; dr++) {
          if (loadCol >= 0 && !loadWeight) {
            var lv = val(headerRow + dr, loadCol);
            if (lv && /\\d/.test(lv)) {
              loadWeight = lv.replace(/[kK][gG]/g, '').replace(/公斤/g, '').trim();
            }
          }
          if (speedCol >= 0 && !speed) {
            var sv = val(headerRow + dr, speedCol);
            if (sv && /\\d/.test(sv)) {
              speed = sv.replace(/[mM]\\/[sS]/g, '').replace(/米\\/秒/g, '').replace(/m\\/s/gi, '').trim();
            }
          }
          if (heightCol >= 0) {
            var hv = val(headerRow + dr, heightCol);
            if (hv && /\\d/.test(hv)) {
              configPartsData['提升高度'] = hv.replace(/mm/g, '').replace(/米/g, '').replace(/m/g, '').trim();
            }
          }
          if (floorsCol >= 0) {
            var fv = val(headerRow + dr, floorsCol);
            if (fv && /\\d/.test(fv)) {
              configPartsData['层站门'] = fv;
            }
          }
          if (loadWeight && speed) break;
        }'''
    
    if old_data_row in content:
        content = content.replace(old_data_row, new_data_row)
        print("  [OK] 问题7: 数据行提取增加提升高度和层站门")
    else:
        print("  [WARN] 问题7: 未找到数据行提取代码")
    
    # 5. 修改部件表匹配为模糊匹配
    old_part_match = '''      if (partStartRow > 0) {
        for (var r4 = partStartRow; r4 < Math.min(partStartRow + 20, json.length); r4++) {
          var partName = String(json[r4] ? (json[r4][0] || '') : '').trim();
          var partModel = String(json[r4] ? (json[r4][2] || '') : '').trim(); // C列=型号
          var partCode = String(json[r4] ? (json[r4][4] || '') : '').trim();  // E列=编号
          if (!partName || partName.indexOf('二、') >= 0 || partName.indexOf('三、') >= 0) break;
          // 存入configPartsData
          if (partName.indexOf('乘客电梯') >= 0 || (partName.indexOf('曳引') >= 0 && partName.indexOf('驱动主机') < 0 && partName.indexOf('曳引机') < 0)) {
            configPartsData['整梯_型号'] = partModel;
            configPartsData['整梯_编号'] = partCode;
            // 整梯编号=控制柜编号，后续匹配控制柜行时会自动填充控制柜型号
          } else if (partName.indexOf('控制柜') >= 0) {
            configPartsData['控制柜_型号'] = partModel;
            configPartsData['控制柜_编号'] = partCode;
          } else if (partName.indexOf('驱动主机') >= 0 || partName.indexOf('主机') >= 0 || partName.indexOf('曳引机') >= 0) {
            configPartsData['驱动主机_型号'] = partModel;
            configPartsData['驱动主机_编号'] = partCode;
          } else if (partName.indexOf('上行超速') >= 0) {
            configPartsData['上行超速_型号'] = partModel;
            configPartsData['上行超速_编号'] = partCode;
          } else if (partName.indexOf('意外移动') >= 0) {
            configPartsData['意外移动_型号'] = partModel;
            configPartsData['意外移动_编号'] = partCode;
          } else if (partName.indexOf('限速器') >= 0) {
            configPartsData['限速器_型号'] = partModel;
            configPartsData['限速器_编号'] = partCode;
          } else if (partName.indexOf('安全钳') >= 0) {
            configPartsData['安全钳_型号'] = partModel;
            configPartsData['安全钳_编号'] = partCode;
          } else if (partName.indexOf('缓冲器') >= 0) {
            configPartsData['缓冲器_型号'] = partModel;
            configPartsData['缓冲器_编号'] = partCode;
          } else if (partName.indexOf('层门门锁') >= 0 || partName.indexOf('层门锁') >= 0) {
            configPartsData['层门锁_型号'] = partModel;
            configPartsData['层门锁_编号'] = partCode;
          } else if (partName.indexOf('轿门门锁') >= 0 || partName.indexOf('轿门锁') >= 0) {
            configPartsData['轿门锁_型号'] = partModel;
            configPartsData['轿门锁_编号'] = partCode;
          } else if (partName.indexOf('层门') >= 0 && partName.indexOf('门锁') < 0) {
            configPartsData['层门_型号'] = partModel;
            configPartsData['层门_编号'] = partCode;
          } else if (partName.indexOf('安全电路') >= 0) {
            configPartsData['安全电路_型号'] = partModel;
            configPartsData['安全电路_编号'] = partCode;
          }
        }
      }'''
    
    new_part_match = '''      if (partStartRow > 0) {
        // 先确定型号列和编号列的位置（不同配置表列可能不同）
        var modelCol = 2; // 默认C列
        var codeCol = 3;  // 默认D列（编号或制造批次号）
        // 从表头行检测列位置
        var headerRow2 = partStartRow - 1;
        if (headerRow2 >= 0 && json[headerRow2]) {
          for (var hc = 0; hc < json[headerRow2].length; hc++) {
            var hcell = String(json[headerRow2][hc] || '').replace(/\\s/g, '').replace(/\\n/g, '');
            if (hcell.indexOf('型号') >= 0 || hcell.indexOf('规格') >= 0) modelCol = hc;
            if (hcell.indexOf('编号') >= 0 || hcell.indexOf('批次') >= 0 || hcell.indexOf('出厂编号') >= 0) codeCol = hc;
          }
        }
        
        for (var r4 = partStartRow; r4 < Math.min(partStartRow + 25, json.length); r4++) {
          var partName = String(json[r4] ? (json[r4][0] || '') : '').trim();
          var partModel = String(json[r4] ? (json[r4][modelCol] || '') : '').trim();
          var partCode = String(json[r4] ? (json[r4][codeCol] || '') : '').trim();
          if (!partName || partName.indexOf('二、') >= 0 || partName.indexOf('三、') >= 0) break;
          
          // 关键词模糊匹配部件类型
          var partKey = null;
          var partNameNorm = normText(partName);
          
          // 按优先级匹配（更具体的优先）
          if (matchKw(partName, ['层门门锁', '层门锁装置', '层门锁'])) {
            partKey = '层门锁';
          } else if (matchKw(partName, ['轿门门锁', '轿门锁装置', '轿门锁'])) {
            partKey = '轿门锁';
          } else if (matchKw(partName, ['上行超速保护装置', '上行超速'])) {
            partKey = '上行超速';
          } else if (matchKw(partName, ['意外移动保护装置', '意外移动'])) {
            partKey = '意外移动';
          } else if (matchKw(partName, ['驱动主机', '曳引机', '主机'])) {
            partKey = '驱动主机';
          } else if (matchKw(partName, ['控制柜'])) {
            partKey = '控制柜';
          } else if (matchKw(partName, ['限速器'])) {
            partKey = '限速器';
          } else if (matchKw(partName, ['安全钳'])) {
            partKey = '安全钳';
          } else if (matchKw(partName, ['缓冲器'])) {
            partKey = '缓冲器';
          } else if (matchKw(partName, ['安全电路', '含有电子元件的安全电路'])) {
            partKey = '安全电路';
          } else if (matchKw(partName, ['层门']) && partNameNorm.indexOf('门锁') < 0) {
            partKey = '层门';
          } else if (matchKw(partName, ['乘客电梯', '载货电梯', '曳引驱动电梯', '观光电梯', '病床电梯'])) {
            partKey = '整梯';
          }
          
          if (partKey) {
            configPartsData[partKey + '_型号'] = partModel;
            configPartsData[partKey + '_编号'] = partCode;
          }
        }
      }'''
    
    if old_part_match in content:
        content = content.replace(old_part_match, new_part_match)
        print("  [OK] 问题7: 部件表匹配改为关键词模糊匹配 + 动态列检测")
    else:
        print("  [WARN] 问题7: 未找到部件表匹配代码")
    
    return content


def main():
    print("=" * 60)
    print("v124 修复脚本 - 修复7个问题")
    print("=" * 60)
    
    # ========== 主文件修复 ==========
    print("\n[主文件 factory-inspection-v2.html]")
    content = read_file(MAIN_FILE)
    original_len = len(content)
    print(f"  文件大小: {original_len} 字符")
    
    print("\n--- 问题1：弹窗内容被截断 ---")
    content = fix_issue1_modal_height(content)
    
    print("\n--- 问题2：附表关闭后弹出中间层 ---")
    content = fix_issue2_close_att_modal(content)
    
    print("\n--- 问题4：签字功能失效 ---")
    content = fix_issue4_signature(content)
    
    print("\n--- 问题5：页面抖动 ---")
    content = fix_issue5_page_shake(content)
    
    print("\n--- 问题6：附表1按钮不灵敏 ---")
    content = fix_issue6_button_sensitivity(content)
    
    print("\n--- 问题7：配置表导入模糊匹配 ---")
    content = fix_issue7_config_import(content)
    
    write_file(MAIN_FILE, content)
    print(f"\n  主文件写入完成，大小: {len(content)} 字符")
    
    # ========== 打印页修复 ==========
    print("\n[打印页 print-fubiao.html]")
    print_content = read_file(PRINT_FILE)
    print(f"  文件大小: {len(print_content)} 字符")
    
    print("\n--- 问题3：附表2打印页表格多加一行 ---")
    print_content = fix_issue3_print_fubiao(print_content)
    
    write_file(PRINT_FILE, print_content)
    print(f"\n  打印页写入完成，大小: {len(print_content)} 字符")
    
    print("\n" + "=" * 60)
    print("所有修复完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
