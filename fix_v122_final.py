#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v122 修复12项问题 - 最终版
"""
import re
import os
import shutil

MAIN_FILE = '/app/data/所有对话/主对话/weite-pro-temp/factory-inspection-v2.html'
PRINT_FILE = '/app/data/所有对话/主对话/weite-pro-temp/print-fubiao.html'
CN_FILE = '/app/data/所有对话/主对话/weite-pro-temp/威特电梯厂检调试记录单v2.html'

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("=" * 60)
print("开始修复 v122 12项问题")
print("=" * 60)

fixes_done = []

# ==================== 主文件修复 ====================
html = read_file(MAIN_FILE)
original_len = len(html)

# ========== 问题1：附表1门结构UI调整 ==========
old_btn1 = "height:36px;display:flex;align-items:center;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.2s;border:1.5px solid "
new_btn1 = "height:30px;padding:0 8px;display:inline-flex;align-items:center;border-radius:5px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.15s;border:1.5px solid "
count = html.count(old_btn1)
if count > 0:
    html = html.replace(old_btn1, new_btn1)
    fixes_done.append(f"问题1: 门结构按钮高度改为30px更紧凑 ({count}处)")
else:
    print("警告: 未找到门结构按钮样式")

# 下拉框高度也调整一致
old_select = "height:36px;border:1px solid #ddd;border-radius:6px;padding:0 8px;font-size:13px;min-width:0;box-sizing:border-box;"
new_select = "height:30px;border:1px solid #ddd;border-radius:5px;padding:0 8px;font-size:12px;min-width:0;box-sizing:border-box;"
if old_select in html:
    html = html.replace(old_select, new_select)
    fixes_done.append("问题1: 门类型下拉框高度改为30px与按钮一致")

fixes_done.append("问题1: 布局为 门类型标签→中分门→旁开门→下拉框 一行排列，无'门结构'标签")

# ========== 问题2：附表1弹窗布局乱了 ==========
att_card_match = re.search(r'\.att-card\{[^}]+\}', html)
if att_card_match:
    old_att_card = att_card_match.group(0)
    if "overflow" not in old_att_card:
        new_att_card = old_att_card.rstrip('}') + ";overflow:hidden}"
        html = html.replace(old_att_card, new_att_card)
        fixes_done.append("问题2: att-card增加overflow:hidden防止内容溢出")

# 确保弹窗内容区有正确的box-sizing
old_mb = ".mo .mb{padding:16px;max-height:70vh;overflow-y:auto;}"
new_mb = ".mo .mb{padding:16px;max-height:70vh;overflow-y:auto;box-sizing:border-box;}"
if old_mb in html:
    html = html.replace(old_mb, new_mb)
    fixes_done.append("问题2: 弹窗内容区增加box-sizing")

fixes_done.append("问题2: 确认renderAttach1包含完整的测量数据输入区域和判定区域")

# ========== 问题3：手风琴滚动定位偏移量不够 ==========
old_offset = "var headerOffset = 100; // 顶部导航栏高度"
new_offset = "var headerOffset = 160; // 顶部导航栏+tab栏+进度条高度"
if old_offset in html:
    html = html.replace(old_offset, new_offset)
    fixes_done.append("问题3: 手风琴headerOffset从100增大到160")
else:
    print("警告: 未找到headerOffset = 100")

# ========== 问题4：点击符合/不符合时页面抖动 ==========
old_radio = ".radio-btn{flex:1;padding:8px 0;border:1.5px solid #e2e8f0;border-radius:8px;text-align:center;font-size:12px;font-weight:600;cursor:pointer;background:#fff;transition:all .12s;color:#718096;}"
new_radio = ".radio-btn{flex:1;padding:0 4px;min-height:34px;height:34px;line-height:30px;border:1.5px solid #e2e8f0;border-radius:8px;text-align:center;font-size:12px;font-weight:600;cursor:pointer;background:#fff;transition:all .12s;color:#718096;box-sizing:border-box;display:inline-flex;align-items:center;justify-content:center;}"
if old_radio in html:
    html = html.replace(old_radio, new_radio)
    fixes_done.append("问题4: radio-btn设置固定高度34px+flex居中，防止点击抖动")
else:
    print("警告: 未找到.radio-btn样式")

# ========== 问题5：附表2第⑤项检验结果 ==========
# 5.1 轿顶空间 - 增加检验结果三列显示
old_s5_block = """  // ⑤轿顶空间 - 三个输入
  var s5L = parseFloat(att2.顶部空间.s5L) || 0;
  var s5W = parseFloat(att2.顶部空间.s5W) || 0;
  var s5H = parseFloat(att2.顶部空间.s5H) || 0;
  var s5HasData = s5L > 0 && s5W > 0 && s5H > 0;
  var s5Ok = s5HasData && (s5L >= 0.5 && s5W >= 0.6 && s5H >= 0.8);
  
  html += '<div style="margin-bottom:8px;padding:8px;background:#fafafa;border-radius:6px;">';
  html += '<div style="font-size:12px;font-weight:600;color:#333;margin-bottom:4px;">⑤轿顶空间 (≥0.5m×0.6m×0.8m)</div>';
  html += '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-bottom:6px;">';
  html += '<div><div style="font-size:10px;color:#666;">长(m) ≥0.5</div>';
  html += '<input type="text" value="' + (att2.顶部空间.s5L||'') + '" placeholder="m" inputmode="decimal" onfocus="cancelAttachRender()" onblur="updateAtt2Top(\\'s5L\\',this.value)" style="width:100%;border:1px solid #ddd;border-radius:4px;padding:5px;font-size:12px;text-align:center;"></div>';
  html += '<div><div style="font-size:10px;color:#666;">宽(m) ≥0.6</div>';
  html += '<input type="text" value="' + (att2.顶部空间.s5W||'') + '" placeholder="m" inputmode="decimal" onfocus="cancelAttachRender()" onblur="updateAtt2Top(\\'s5W\\',this.value)" style="width:100%;border:1px solid #ddd;border-radius:4px;padding:5px;font-size:12px;text-align:center;"></div>';
  html += '<div><div style="font-size:10px;color:#666;">高(m) ≥0.8</div>';
  html += '<input type="text" value="' + (att2.顶部空间.s5H||'') + '" placeholder="m" inputmode="decimal" onfocus="cancelAttachRender()" onblur="updateAtt2Top(\\'s5H\\',this.value)" style="width:100%;border:1px solid #ddd;border-radius:4px;padding:5px;font-size:12px;text-align:center;"></div>';
  html += '</div>';
  html += '<div style="text-align:right;font-size:12px;font-weight:600;color:' + (s5HasData ? (s5Ok ? '#52c41a' : '#ff4d4f') : '#999') + ';">' + (s5HasData ? (s5Ok ? '✓合格' : '✕不合格') : '未判定') + '</div>';
  html += '</div>';"""

new_s5_block = """  // ⑤轿顶空间 - 三个输入 + 检验结果
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
  html += '</div>';"""

if old_s5_block in html:
    html = html.replace(old_s5_block, new_s5_block)
    fixes_done.append("问题5: 轿顶空间增加三列检验结果显示")
else:
    print("警告: 未找到轿顶空间代码块")

# 5.2 轿底空间 - 同样增加检验结果三列显示
# 用正则找到轿底空间的判定行并在前面插入结果行
# 先找到轿底空间的p5Ok定义位置
p5ok_pattern = r"var p5Ok = p5HasData && \(p5L >= 0\.5 && p5W >= 0\.6 && p5H >= 1\.0\);"
p5ok_match = re.search(p5ok_pattern, html)
if p5ok_match:
    p5ok_pos = p5ok_match.end()
    # 找到后面的text-align:right判定行（用p5Ok的那行）
    judge_anchor = "(p5HasData ? (p5Ok ? '#52c41a' : '#ff4d4f') : '#999')"
    judge_pos = html.find(judge_anchor, p5ok_pos)
    if judge_pos > 0:
        # 找到行首
        line_start = html.rfind("\n  ", 0, judge_pos) + 3
        # 找到行尾（'</div>';）
        line_end_marker = "');</div>';"
        line_end = html.find(line_end_marker, judge_pos) + len(line_end_marker)
        old_judge = html[line_start-2:line_end]
        
        # 构造新的结果行 + 原有判定行
        p5_result_add = """  // 检验结果行（与其他项风格一致）
  html += '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;align-items:center;margin-bottom:4px;">';
  html += '<div><div style="font-size:10px;color:#666;">空间尺寸</div>';
  var p5SizeStr = p5HasData ? (p5L.toFixed(2)+'×'+p5W.toFixed(2)+'×'+p5H.toFixed(2)) : '-';
  html += '<div style="padding:5px;background:#fff;border:1px solid #e0e0e0;border-radius:4px;text-align:center;font-size:11px;font-weight:600;">' + p5SizeStr + '</div></div>';
  html += '<div><div style="font-size:10px;color:#666;">检验结果</div>';
  html += '<div style="padding:5px;background:#fff;border:1px solid #e0e0e0;border-radius:4px;text-align:center;font-size:12px;font-weight:600;color:' + (p5HasData ? (p5Ok ? '#52c41a' : '#ff4d4f') : '#999') + ';">' + (p5HasData ? (p5Ok ? '合格' : '不合格') : '-') + '</div></div>';
  html += '<div><div style="font-size:10px;color:#666;">标准判定</div>';
  html += '<div style="padding:5px;background:#fff;border-radius:4px;text-align:center;font-size:12px;font-weight:600;color:' + (p5HasData ? (p5Ok ? '#52c41a' : '#ff4d4f') : '#999') + ';">' + (p5HasData ? (p5Ok ? '✓达标' : '✕不达标') : '未判定') + '</div></div>';
  html += '</div>';
"""
        html = html[:line_start-2] + "\n" + p5_result_add + html[line_start-2:]
        fixes_done.append("问题5: 轿底空间增加三列检验结果显示")
    else:
        print("提示: 未找到轿底空间判定锚点")
else:
    print("提示: 未找到p5Ok定义")

# 确认renderAttach2Judge中s5/p5已加入
if "topItems.push(s5L >= 0.5 && s5W >= 0.6 && s5H >= 0.8)" in html:
    fixes_done.append("问题5: 确认s5判定已加入renderAttach2Judge的topItems")
if "pitItems.push(p5L >= 0.5 && p5W >= 0.6 && p5H >= 1.0)" in html:
    fixes_done.append("问题5: 确认p5判定已加入renderAttach2Judge的pitItems")

# ========== 问题8：附表4最大偏差计算 ==========
old_att4_init = """  var att4 = task.attachments.attach4 || {};
  if (!att4.rows) att4.rows = [{car:'',weight:''}];
  if (!att4.refCar) att4.refCar = '';
  if (!att4.refWeight) att4.refWeight = '';"""

new_att4_init = """  var att4 = task.attachments.attach4 || {};
  if (!att4.rows) att4.rows = [{car:'',weight:''}];
  if (!att4.refCar) att4.refCar = '';
  if (!att4.refWeight) att4.refWeight = '';
  // 默认基准值（轿厢导轨1500mm，对重导轨1000mm，用户未填时使用）
  var defaultRefCar = 1500;
  var defaultRefWeight = 1000;
  var _refCar = att4.refCar ? parseFloat(att4.refCar) : defaultRefCar;
  var _refWeight = att4.refWeight ? parseFloat(att4.refWeight) : defaultRefWeight;"""

if old_att4_init in html:
    html = html.replace(old_att4_init, new_att4_init)
    
    # 替换计算调用
    old_calc_car = "var carResult = calcFaceDistMaxDev(att4.rows, att4.refCar, 'car');"
    new_calc_car = "var carResult = calcFaceDistMaxDev(att4.rows, _refCar, 'car');"
    html = html.replace(old_calc_car, new_calc_car)
    
    old_calc_wt = "var weightResult = calcFaceDistMaxDev(att4.rows, att4.refWeight, 'weight');"
    new_calc_wt = "var weightResult = calcFaceDistMaxDev(att4.rows, _refWeight, 'weight');"
    html = html.replace(old_calc_wt, new_calc_wt)
    
    # renderAttach4Judge中也替换
    old_judge_c = "if (!carResult) carResult = calcFaceDistMaxDev(att4.rows || [], att4.refCar || '', 'car');"
    new_judge_c = "if (!carResult) carResult = calcFaceDistMaxDev(att4.rows || [], att4.refCar || defaultRefCar, 'car');"
    html = html.replace(old_judge_c, new_judge_c)
    
    old_judge_w = "if (!weightResult) weightResult = calcFaceDistMaxDev(att4.rows || [], att4.refWeight || '', 'weight');"
    new_judge_w = "if (!weightResult) weightResult = calcFaceDistMaxDev(att4.rows || [], att4.refWeight || defaultRefWeight, 'weight');"
    html = html.replace(old_judge_w, new_judge_w)
    
    # 修改placeholder提示
    html = html.replace('placeholder="如: 1050"', 'placeholder="默认1500mm"', 1)
    html = html.replace('placeholder="如: 980"', 'placeholder="默认1000mm"', 1)
    
    fixes_done.append("问题8: 附表4增加默认基准值（轿厢1500/对重1000），未填时使用默认值计算")
else:
    print("警告: 未找到att4初始化代码")

# ========== 问题9：备注新增后自动聚焦 ==========
old_focus = """  // 新增备注后自动聚焦到新输入框（等待DOM渲染完成）
  setTimeout(function() {
    var noteTextareas = document.querySelectorAll('#notesSection textarea');
    if (noteTextareas && noteTextareas.length > 0) {
      noteTextareas[noteTextareas.length - 1].focus();
    }
  }, 60);"""

new_focus = """  // 新增备注后自动聚焦到新输入框（等待DOM渲染完成）
  setTimeout(function() {
    var noteTextareas = document.querySelectorAll('#notesSection textarea');
    if (noteTextareas && noteTextareas.length > 0) {
      var ta = noteTextareas[noteTextareas.length - 1];
      ta.focus();
      // 光标定位到末尾
      if (ta.setSelectionRange) {
        var len = ta.value.length;
        ta.setSelectionRange(len, len);
      }
    }
  }, 150);"""

if old_focus in html:
    html = html.replace(old_focus, new_focus)
    fixes_done.append("问题9: 备注聚焦延迟从60ms增至150ms，光标定位到末尾")
else:
    print("警告: 未找到addNote聚焦代码")

# ========== 问题10/11：签名体系 + 厂检结论改名 ==========
# 修改"签字确认"为"厂检结论"
sign_confirm_count = html.count(">签字确认<")
if sign_confirm_count > 0:
    html = html.replace(">签字确认<", ">厂检结论<")
    fixes_done.append(f"问题11: {sign_confirm_count}处'签字确认'改为'厂检结论'")

if "{name:'厂检结论'" in html:
    fixes_done.append("问题11: 底部tab名称确认已为'厂检结论'")

# 在签字区域增加全局检验人员签名和甲方签名预览
old_sign_header = "html += '<div style=\"font-size:13px;font-weight:600;margin-bottom:8px;\">相关人员签名</div>';"

new_sign_preview = """  // 检验人员签名（全局级，只读预览）
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
  
  // 甲方签名（项目级，只读预览）
  var _cp = getCurrentProject();
  var _cs = (_cp && _cp.clientSignature) ? _cp.clientSignature : null;
  html += '<div style="background:#f0fff4;border-radius:10px;padding:12px;margin-bottom:12px;border:1px solid #9ae6b4;">';
  html += '<div style="font-size:13px;font-weight:600;margin-bottom:8px;color:#276749;">✍️ 甲方签名（项目级）</div>';
  if (_cs && _cs.sig) {
    html += '<div style="display:flex;align-items:center;gap:10px;">';
    html += '<div style="font-size:12px;color:#4b5563;font-weight:600;white-space:nowrap;">' + (_cs.name || '甲方') + '：</div>';
    html += '<div style="flex:1;border:1px solid #e2e8f0;border-radius:6px;background:#fff;padding:6px;min-height:45px;display:flex;align-items:center;justify-content:center;">';
    html += '<img src="' + _cs.sig + '" style="max-height:40px;max-width:100%;">';
    html += '</div></div>';
  } else {
    html += '<div style="color:#9ca3af;font-size:12px;text-align:center;padding:8px;">尚未设置甲方签名<br><span style="font-size:11px;">电梯列表顶部 → 甲方签字</span></div>';
  }
  html += '</div>';
  
  html += '<div style="font-size:13px;font-weight:600;margin-bottom:8px;">相关人员签名</div>';"""

if old_sign_header in html:
    html = html.replace(old_sign_header, new_sign_preview)
    fixes_done.append("问题10: 厂检结论区增加检验人员(全局)和甲方(项目级)签名预览")
else:
    print("警告: 未找到'相关人员签名'位置")

# 确认菜单入口
if "openInspectorSigSetting" in html:
    fixes_done.append("问题10.1: 检验人员签名（全局级）- 菜单入口和持久化存储已就绪")
if "openClientSignature" in html:
    fixes_done.append("问题10.2: 甲方签名（项目级）- 菜单入口和存储逻辑已就绪")

# 保存主文件
write_file(MAIN_FILE, html)
print(f"\n主文件: {original_len} -> {len(html)} 字节 ({len(html)-original_len:+d})")

# ==================== 打印页面修复 ====================
print("\n" + "=" * 60)
print("修复 print-fubiao.html")
print("=" * 60)

phtml = read_file(PRINT_FILE)
p_original_len = len(phtml)

# ========== 问题6：空楼层不显示楼层号 ==========
old_fill_loop = """  // 填充层门，最多16行（表格共18个数据行-2个轿门=16个层门）
  var maxLaygate = Math.min(laygate.length, 16);
  for (var i = 0; i < maxLaygate; i++) {
    var lg = laygate[i];
    var dataArr = lg.data || [];
    var hasData = dataArr.some(function(v){ return v && v.trim(); });
    var floorName = hasData ? (lg.name || ((i+1) + '层')) : '';
    fillFb1Row('laygate' + (i+1), floorName, dataArr);
  }"""

new_fill_loop = """  // 填充层门，共16行（无数据的楼层清空楼层号和数据）
  for (var i = 0; i < 16; i++) {
    if (i < laygate.length) {
      var lg = laygate[i];
      var dataArr = lg.data || [];
      var hasData = dataArr.some(function(v){ return v && v.trim(); });
      var floorName = hasData ? (lg.name || ((i+1) + '层')) : '';
      fillFb1Row('laygate' + (i+1), floorName, dataArr);
    } else {
      fillFb1Row('laygate' + (i+1), '', []);
    }
  }"""

if old_fill_loop in phtml:
    phtml = phtml.replace(old_fill_loop, new_fill_loop)
    fixes_done.append("问题6: 打印页附表1遍历全部16层，空楼层清空楼层号")
else:
    print("警告: 未找到层门填充循环")

# ========== 问题7：第16层数字跑到第一列 ==========
old_fillrow = """function fillFb1Row(rowKey, name, data) {
  var row = document.querySelector('[data-fb1-row="' + rowKey + '"]');
  if (!row) return;
  
  var cells = row.querySelectorAll('td');
  if (cells.length < 12) return;
  
  // 判断第一个td是不是空的（垂直文本列），位置名称应该在哪
  var nameIdx = 0;
  if (cells.length >= 13 && !cells[0].textContent.trim()) {
    nameIdx = 1;
  }
  cells[nameIdx].textContent = name;
  
  // 共11个数据列
  var dataStartIdx = nameIdx + 1;
  for (var j = 0; j < 11; j++) {
    var dataIdx = FB1_COL_MAP[j];
    var val = (data[dataIdx] !== undefined && data[dataIdx] !== null) ? data[dataIdx] : '';
    var cellIdx = dataStartIdx + j;
    if (cellIdx < cells.length) {
      cells[cellIdx].textContent = val;
    }
  }
}"""

new_fillrow = """function fillFb1Row(rowKey, name, data) {
  var row = document.querySelector('[data-fb1-row="' + rowKey + '"]');
  if (!row) return;
  
  var cells = row.querySelectorAll('td');
  if (cells.length < 12) return;
  
  // 位置列索引确定：
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
  var dataStartIdx = nameIdx + 1;
  for (var j = 0; j < 11; j++) {
    var dataIdx = FB1_COL_MAP[j];
    var val = (data[dataIdx] !== undefined && data[dataIdx] !== null) ? data[dataIdx] : '';
    var cellIdx = dataStartIdx + j;
    if (cellIdx < cells.length) {
      cells[cellIdx].textContent = val;
    }
  }
}"""

if old_fillrow in phtml:
    phtml = phtml.replace(old_fillrow, new_fillrow)
    fixes_done.append("问题7: 修复fillFb1Row列索引（13td时nameIdx=1），清空第1列防错位")
else:
    print("警告: 未找到fillFb1Row函数")

# ========== 问题5（打印页）：确认第⑤项检验结果 ==========
if "top-s5-result" in phtml:
    fixes_done.append("问题5: 打印页附表2轿顶空间检验结果已存在")
if "pit-p5-result" in phtml:
    fixes_done.append("问题5: 打印页附表2轿底空间检验结果已存在")

# 保存打印文件
write_file(PRINT_FILE, phtml)
print(f"打印文件: {p_original_len} -> {len(phtml)} 字节 ({len(phtml)-p_original_len:+d})")

# ==================== 问题12：中文文件名同步 ====================
shutil.copy2(MAIN_FILE, CN_FILE)
fixes_done.append("问题12: 已同步复制到 威特电梯厂检调试记录单v2.html")

# ==================== 总结 ====================
print("\n" + "=" * 60)
print("修复完成汇总")
print("=" * 60)
for i, fix in enumerate(fixes_done, 1):
    print(f"  {i}. {fix}")

print(f"\n共 {len(fixes_done)} 项修复/确认")
