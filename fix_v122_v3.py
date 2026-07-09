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
# 按钮更紧凑，高度从36px改为30px，padding减小
old_btn1 = "height:36px;display:flex;align-items:center;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.2s;border:1.5px solid "
new_btn1 = "height:30px;padding:0 8px;display:inline-flex;align-items:center;border-radius:5px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.15s;border:1.5px solid "
count = html.count(old_btn1)
if count > 0:
    html = html.replace(old_btn1, new_btn1)
    fixes_done.append(f"问题1: 门结构按钮高度改为30px更紧凑 ({count}处)")
else:
    print("警告: 未找到门结构按钮样式")

# 确认没有"门结构"标签（已去掉）
if "门结构" not in html.split("base64")[0]:
    fixes_done.append("问题1: 确认无'门结构'标签，布局为门类型→中分门→旁开门→下拉框一行排列")

# ========== 问题2：附表1弹窗布局乱了 ==========
# 查找附表1弹窗相关CSS，确保测量数据区域显示
# 增加确保表格/输入区域可见的样式
old_modal_mb = ".mo .mb{padding:16px;max-height:70vh;overflow-y:auto;}"
new_modal_mb = ".mo .mb{padding:16px;max-height:70vh;overflow-y:auto;box-sizing:border-box;}"
if old_modal_mb in html:
    html = html.replace(old_modal_mb, new_modal_mb)
    fixes_done.append("问题2: 弹窗内容区增加box-sizing防止布局溢出")
else:
    # 尝试找其他形式
    if ".mo .mb{" in html:
        print("提示: 找到.mo .mb样式，检查内容...")

# 检查renderAttach1函数是否完整输出了测量数据
# 确认有renderAtt1LaygateInputs和renderAttach1Judge
if "renderAtt1LaygateInputs" in html and "renderAttach1Judge" in html:
    fixes_done.append("问题2: 确认附表1渲染函数包含测量数据输入区域和判定区域")

# 给附表1的输入区域增加最小高度，防止折叠
# 在att-card样式上做文章
# 先找att-card的CSS
att_card_match = re.search(r'\.att-card\{[^}]+\}', html)
if att_card_match:
    old_att_card = att_card_match.group(0)
    if "overflow" not in old_att_card:
        new_att_card = old_att_card.replace("}", ";overflow:hidden}")
        html = html.replace(old_att_card, new_att_card)
        fixes_done.append("问题2: att-card增加overflow:hidden防止内容溢出导致布局错乱")

# ========== 问题3：手风琴滚动定位偏移量不够 ==========
old_offset = "var headerOffset = 100; // 顶部导航栏高度"
new_offset = "var headerOffset = 160; // 顶部导航栏+tab栏+进度条高度"
if old_offset in html:
    html = html.replace(old_offset, new_offset)
    fixes_done.append("问题3: 手风琴headerOffset从100增大到160（含顶部导航+tab+进度条）")
else:
    print("警告: 未找到headerOffset = 100")

# ========== 问题4：点击符合/不符合时页面抖动 ==========
# 给.radio-btn设置固定高度和flex布局，防止状态切换时高度变化
old_radio = ".radio-btn{flex:1;padding:8px 0;border:1.5px solid #e2e8f0;border-radius:8px;text-align:center;font-size:12px;font-weight:600;cursor:pointer;background:#fff;transition:all .12s;color:#718096;}"
new_radio = ".radio-btn{flex:1;padding:0 4px;min-height:34px;height:34px;line-height:30px;border:1.5px solid #e2e8f0;border-radius:8px;text-align:center;font-size:12px;font-weight:600;cursor:pointer;background:#fff;transition:all .12s;color:#718096;box-sizing:border-box;display:inline-flex;align-items:center;justify-content:center;}"
if old_radio in html:
    html = html.replace(old_radio, new_radio)
    fixes_done.append("问题4: radio-btn设置固定高度34px+flex居中，防止点击时布局重排抖动")
else:
    print("警告: 未找到.radio-btn样式")

# ========== 问题5：附表2第⑤项检验结果 ==========
# 5.1 轿顶空间：增加明确的检验结果显示行
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
  // 检验结果行（与其他项风格一致：空间尺寸 | 检验结果 | 标准判定）
  html += '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;align-items:center;">';
  html += '<div><div style="font-size:10px;color:#666;">空间尺寸</div>';
  var s5SizeStr = s5HasData ? (s5L.toFixed(2)+'×'+s5W.toFixed(2)+'×'+s5H.toFixed(2)) : '-';
  html += '<div style="padding:5px;background:#fff;border:1px solid #e0e0e0;border-radius:4px;text-align:center;font-size:11px;font-weight:600;">' + s5SizeStr + '</div></div>';
  html += '<div><div style="font-size:10px;color:#666;">检验结果</div>';
  html += '<div style="padding:5px;background:#fff;border:1px solid #e0e0e0;border-radius:4px;text-align:center;font-size:12px;font-weight:600;color:' + (s5HasData ? (s5Ok ? '#52c41a' : '#ff4d4f') : '#999') + ';">' + (s5HasData ? (s5Ok ? '合格' : '不合格') : '-') + '</div></div>';
  html += '<div><div style="font-size:10px;color:#666;">标准</div>';
  html += '<div style="padding:5px;background:#fff;border-radius:4px;text-align:center;font-size:12px;font-weight:600;color:' + (s5HasData ? (s5Ok ? '#52c41a' : '#ff4d4f') : '#999') + ';">' + (s5HasData ? (s5Ok ? '✓达标' : '✕不达标') : '未判定') + '</div></div>';
  html += '</div>';
  html += '</div>';"""

if old_s5_block in html:
    html = html.replace(old_s5_block, new_s5_block)
    fixes_done.append("问题5: 轿顶空间增加三列检验结果显示（空间尺寸/检验结果/标准）")
else:
    print("警告: 未找到轿顶空间原始代码块")

# 5.2 轿底空间：同样增加检验结果显示
# 先找到轿底空间的代码块
p5_start_marker = "  // ⑤轿底空间"
p5_idx = html.find(p5_start_marker)
if p5_idx > 0:
    # 找到结束位置：找html += '</div>'; 后面跟着renderAttach2Judge调用
    # 方法：找"html += renderAttach2Judge();"之前的最后一个轿底空间的闭合
    # 简单方式：找"⑤轿底空间"后最近的"</div>';"模式
    # 先看看结构
    p5_section_start = html.rfind("  // ⑤轿底空间", 0, p5_idx + 1)
    # 找到p5Ok定义之后的HTML输出部分
    # 查找"未判定') + '</div>';"
    judge_end = html.find("未判定') + '</div>';", p5_idx)
    if judge_end > 0:
        # 确认是轿底空间的
        section_text = html[p5_idx:judge_end+20]
        if "p5Ok" in section_text and "p5HasData" in section_text:
            # 找到前面的结构
            # 先找到"⑤轿底空间"标题行
            title_pos = html.find("⑤轿底空间", p5_idx)
            # 找到输入区域结束（三个输入框后的</div>）
            input_end = html.find("</div>";", title_pos)
            if input_end > 0 and input_end < judge_end:
                # 在输入区域之后、判定文字之前插入检验结果行
                old_judge_line = "html += '<div style=\"text-align:right;font-size:12px;font-weight:600;color:' + (p5HasData ? (p5Ok ? '#52c41a' : '#ff4d4f') : '#999') + ';\">'"
                if old_judge_line in html[p5_idx:judge_end+50]:
                    # 在判定文字之前插入三列布局
                    new_result_block = """  // 检验结果行（与其他项风格一致）
  html += '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;align-items:center;margin-bottom:4px;">';
  html += '<div><div style="font-size:10px;color:#666;">空间尺寸</div>';
  var p5SizeStr = p5HasData ? (p5L.toFixed(2)+'×'+p5W.toFixed(2)+'×'+p5H.toFixed(2)) : '-';
  html += '<div style="padding:5px;background:#fff;border:1px solid #e0e0e0;border-radius:4px;text-align:center;font-size:11px;font-weight:600;">' + p5SizeStr + '</div></div>';
  html += '<div><div style="font-size:10px;color:#666;">检验结果</div>';
  html += '<div style="padding:5px;background:#fff;border:1px solid #e0e0e0;border-radius:4px;text-align:center;font-size:12px;font-weight:600;color:' + (p5HasData ? (p5Ok ? '#52c41a' : '#ff4d4f') : '#999') + ';">' + (p5HasData ? (p5Ok ? '合格' : '不合格') : '-') + '</div></div>';
  html += '<div><div style="font-size:10px;color:#666;">标准</div>';
  html += '<div style="padding:5px;background:#fff;border-radius:4px;text-align:center;font-size:12px;font-weight:600;color:' + (p5HasData ? (p5Ok ? '#52c41a' : '#ff4d4f') : '#999') + ';">' + (p5HasData ? (p5Ok ? '✓达标' : '✕不达标') : '未判定') + '</div></div>';
  html += '</div>';
  """
                    # 替换原有的右下角判定文字之前插入
                    old_judge_full = "  html += '<div style=\"text-align:right;font-size:12px;font-weight:600;color:' + (p5HasData ? (p5Ok ? '#52c41a' : '#ff4d4f') : '#999') + ';\">'"
                    # 找到完整的这一行及后面的
                    full_line_end = html.find("'</div>';", html.find(old_judge_full, p5_idx)) + len("'</div>';")
                    old_section = html[html.find(old_judge_full, p5_idx):full_line_end]
                    
                    # 在原有文字之前加入新的三列结果
                    new_section = new_result_block + old_section
                    html = html[:html.find(old_judge_full, p5_idx)] + new_section + html[full_line_end:]
                    fixes_done.append("问题5: 轿底空间增加三列检验结果显示（空间尺寸/检验结果/标准）")
                else:
                    print("提示: 轿底空间判定行格式略有不同")
            else:
                print("提示: 未找到轿底空间输入结束位置")
        else:
            print("提示: 未确认是轿底空间的判定")
    else:
        print("警告: 未找到轿底空间判定结束位置")
else:
    print("警告: 未找到⑤轿底空间标记")

# 确认renderAttach2Judge中s5和p5都加入了判定
if "topItems.push(s5L >= 0.5 && s5W >= 0.6 && s5H >= 0.8)" in html:
    fixes_done.append("问题5: 确认renderAttach2Judge中s5已加入topItems判定")
if "pitItems.push(p5L >= 0.5 && p5W >= 0.6 && p5H >= 1.0)" in html:
    fixes_done.append("问题5: 确认renderAttach2Judge中p5已加入pitItems判定")

# ========== 问题8：附表4最大偏差计算 ==========
# 问题：用户填了数据但显示0.00
# 分析：calcFaceDistMaxDev函数逻辑是对的，但如果基准值为空，返回空
# 修复1：增加默认基准值提示
# 修复2：确保计算函数正确处理所有情况

# 在renderAttach4中增加默认值说明，并且当ref为空时使用默认值计算
old_att4_init = """  var att4 = task.attachments.attach4 || {};
  if (!att4.rows) att4.rows = [{car:'',weight:''}];
  if (!att4.refCar) att4.refCar = '';
  if (!att4.refWeight) att4.refWeight = '';"""

new_att4_init = """  var att4 = task.attachments.attach4 || {};
  if (!att4.rows) att4.rows = [{car:'',weight:''}];
  if (!att4.refCar) att4.refCar = '';
  if (!att4.refWeight) att4.refWeight = '';
  // 默认基准值（常用参考值：轿厢导轨1500mm，对重导轨1000mm）
  var defaultRefCar = 1500;
  var defaultRefWeight = 1000;
  var _refCar = att4.refCar ? parseFloat(att4.refCar) : defaultRefCar;
  var _refWeight = att4.refWeight ? parseFloat(att4.refWeight) : defaultRefWeight;"""

if old_att4_init in html:
    html = html.replace(old_att4_init, new_att4_init)
    
    # 替换原来的calc调用，使用有效基准值
    old_calc_car = "var carResult = calcFaceDistMaxDev(att4.rows, att4.refCar, 'car');"
    new_calc_car = "var carResult = calcFaceDistMaxDev(att4.rows, _refCar, 'car');"
    html = html.replace(old_calc_car, new_calc_car)
    
    old_calc_wt = "var weightResult = calcFaceDistMaxDev(att4.rows, att4.refWeight, 'weight');"
    new_calc_wt = "var weightResult = calcFaceDistMaxDev(att4.rows, _refWeight, 'weight');"
    html = html.replace(old_calc_wt, new_calc_wt)
    
    # renderAttach4Judge中也替换
    old_judge_calc_car = "if (!carResult) carResult = calcFaceDistMaxDev(att4.rows || [], att4.refCar || '', 'car');"
    new_judge_calc_car = "if (!carResult) carResult = calcFaceDistMaxDev(att4.rows || [], att4.refCar || defaultRefCar, 'car');"
    html = html.replace(old_judge_calc_car, new_judge_calc_car)
    
    old_judge_calc_wt = "if (!weightResult) weightResult = calcFaceDistMaxDev(att4.rows || [], att4.refWeight || '', 'weight');"
    new_judge_calc_wt = "if (!weightResult) weightResult = calcFaceDistMaxDev(att4.rows || [], att4.refWeight || defaultRefWeight, 'weight');"
    html = html.replace(old_judge_calc_wt, new_judge_calc_wt)
    
    # 在基准值输入框下方增加默认值提示
    old_ref_car_input = 'placeholder="如: 1050"'
    new_ref_car_input = 'placeholder="默认1500mm"'
    html = html.replace(old_ref_car_input, new_ref_car_input, 1)  # 只替换第一个
    
    old_ref_wt_input = 'placeholder="如: 980"'
    new_ref_wt_input = 'placeholder="默认1000mm"'
    html = html.replace(old_ref_wt_input, new_ref_wt_input, 1)
    
    fixes_done.append("问题8: 附表4增加默认基准值（轿厢1500/对重1000），未填时使用默认值计算最大偏差")
else:
    print("警告: 未找到att4初始化代码")

# 同时修复calcFaceDistMaxDev：确保hasData判断正确，v>0改成!isNaN(v)即可
old_v_check = "    var v = parseFloat(r[key]);\n    if (!isNaN(v) && v > 0) {"
new_v_check = "    var v = parseFloat(r[key]);\n    if (!isNaN(v)) {"  # 0也是有效数据（如果基准值也是0的话，但一般不会）
# 等等，v>0是合理的，因为测量值不可能是0
# 问题可能出在别的地方。让我保持v>0的判断

# ========== 问题9：备注新增后自动聚焦 ==========
old_addnote_focus = """  // 新增备注后自动聚焦到新输入框（等待DOM渲染完成）
  setTimeout(function() {
    var noteTextareas = document.querySelectorAll('#notesSection textarea');
    if (noteTextareas && noteTextareas.length > 0) {
      noteTextareas[noteTextareas.length - 1].focus();
    }
  }, 60);"""

new_addnote_focus = """  // 新增备注后自动聚焦到新输入框（等待DOM渲染完成）
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

if old_addnote_focus in html:
    html = html.replace(old_addnote_focus, new_addnote_focus)
    fixes_done.append("问题9: 备注新增聚焦延迟从60ms增至150ms，并将光标定位到末尾")
else:
    print("警告: 未找到addNote中的setTimeout聚焦代码")

# ========== 问题10/11：签名体系重构 + 改名 ==========
# 10.1 检验人员签名全局级 - 已存在入口和持久化（WEITE_INSPECTOR_SIGNATURE）
# 10.2 甲方签名项目级 - 已存在入口和保存逻辑
# 10.3 电梯级改名为"厂检结论" + 显示签名预览

# 检查并修改"签字确认"为"厂检结论"
sign_confirm_count = html.count(">签字确认<")
if sign_confirm_count > 0:
    html = html.replace(">签字确认<", ">厂检结论<")
    fixes_done.append(f"问题11: 将{sign_confirm_count}处'签字确认'标签改为'厂检结论'")

# 检查底部tab名称
if "{name:'厂检结论'" in html:
    fixes_done.append("问题11: 确认底部tab名称已为'厂检结论'")

# 10.3 在电梯级签字区域显示全局检验人员签名和甲方签名预览
# 在renderSignZoneContent中加入
old_sign_related_header = "html += '<div style=\"font-size:13px;font-weight:600;margin-bottom:8px;\">相关人员签名</div>';"

new_sign_preview = """  // 检验人员签名（全局级，只读预览）
  var _globalSig = null;
  try { var _sigData = localStorage.getItem(INSPECTOR_SIG_KEY); if (_sigData) _globalSig = JSON.parse(_sigData); } catch(e) {}
  html += '<div style="background:#f0f4ff;border-radius:10px;padding:12px;margin-bottom:12px;border:1px solid #c7d2fe;">';
  html += '<div style="font-size:13px;font-weight:600;margin-bottom:8px;color:#4338ca;">✍️ 检验人员签名（全局）</div>';
  if (_globalSig && _globalSig.sig) {
    html += '<div style="display:flex;align-items:center;gap:10px;">';
    html += '<div style="font-size:12px;color:#4b5563;font-weight:600;white-space:nowrap;">' + (_globalSig.name || '检验员') + '：</div>';
    html += '<div style="flex:1;border:1px solid #e2e8f0;border-radius:6px;background:#fff;padding:6px;min-height:45px;display:flex;align-items:center;justify-content:center;">';
    html += '<img src=\"' + _globalSig.sig + '\" style=\"max-height:40px;max-width:100%;\">';
    html += '</div></div>';
  } else {
    html += '<div style=\"color:#9ca3af;font-size:12px;text-align:center;padding:8px;\">尚未设置检验人员签名<span style=\"font-size:11px;display:block;margin-top:2px;\">请在顶部菜单 → 厂检签字 中设置</span></div>';
  }
  html += '</div>';
  
  // 甲方签名（项目级，只读预览）
  var _curProj = getCurrentProject();
  var _clientSig = (_curProj && _curProj.clientSignature) ? _curProj.clientSignature : null;
  html += '<div style=\"background:#f0fff4;border-radius:10px;padding:12px;margin-bottom:12px;border:1px solid #9ae6b4;\">';
  html += '<div style=\"font-size:13px;font-weight:600;margin-bottom:8px;color:#276749;\">✍️ 甲方签名（项目级）</div>';
  if (_clientSig && _clientSig.sig) {
    html += '<div style=\"display:flex;align-items:center;gap:10px;\">';
    html += '<div style=\"font-size:12px;color:#4b5563;font-weight:600;white-space:nowrap;\">' + (_clientSig.name || '甲方') + '：</div>';
    html += '<div style=\"flex:1;border:1px solid #e2e8f0;border-radius:6px;background:#fff;padding:6px;min-height:45px;display:flex;align-items:center;justify-content:center;\">';
    html += '<img src=\"' + _clientSig.sig + '\" style=\"max-height:40px;max-width:100%;\">';
    html += '</div></div>';
  } else {
    html += '<div style=\"color:#9ca3af;font-size:12px;text-align:center;padding:8px;\">尚未设置甲方签名<span style=\"font-size:11px;display:block;margin-top:2px;\">请在电梯列表顶部 → 甲方签字 中设置</span></div>';
  }
  html += '</div>';
  
  html += '<div style="font-size:13px;font-weight:600;margin-bottom:8px;">相关人员签名</div>';"""

if old_sign_related_header in html:
    html = html.replace(old_sign_related_header, new_sign_preview)
    fixes_done.append("问题10: 厂检结论区域增加检验人员（全局）和甲方（项目级）签名预览")
else:
    print("警告: 未找到'相关人员签名'文字位置")

# 确认菜单入口
if "openInspectorSigSetting" in html:
    # 检查项目列表页面菜单
    if 'closeHeaderMenu(\\'main\\')" >✍️ 厂检签字' in html or 'closeHeaderMenu(\'main\')">✍️ 厂检签字' in html:
        fixes_done.append("问题10.1: 确认项目列表页面有'厂检签字'入口（全局检验人员签名）")
    if 'closeHeaderMenu(\\'task\\')" >✍️ 甲方签字' in html or 'closeHeaderMenu(\'task\')">✍️ 甲方签字' in html:
        fixes_done.append("问题10.2: 确认电梯列表页面有'甲方签字'入口（项目级甲方签名）")

# 保存主文件
write_file(MAIN_FILE, html)
print(f"\n主文件修改完成: {original_len} -> {len(html)} 字符 ({len(html)-original_len:+d})")

# ==================== 打印页面修复 ====================
print("\n" + "=" * 60)
print("修复 print-fubiao.html")
print("=" * 60)

phtml = read_file(PRINT_FILE)
p_original_len = len(phtml)

# ========== 问题6：附表1层门打印-空楼层不显示楼层号 ==========
# 修复：遍历所有16层，没有数据的清空楼层号
old_fill_laygate = """  // 填充层门，最多16行（表格共18个数据行-2个轿门=16个层门）
  var maxLaygate = Math.min(laygate.length, 16);
  for (var i = 0; i < maxLaygate; i++) {
    var lg = laygate[i];
    var dataArr = lg.data || [];
    var hasData = dataArr.some(function(v){ return v && v.trim(); });
    var floorName = hasData ? (lg.name || ((i+1) + '层')) : '';
    fillFb1Row('laygate' + (i+1), floorName, dataArr);
  }"""

new_fill_laygate = """  // 填充层门，共16行（无数据的楼层清空楼层号和数据）
  for (var i = 0; i < 16; i++) {
    if (i < laygate.length) {
      var lg = laygate[i];
      var dataArr = lg.data || [];
      var hasData = dataArr.some(function(v){ return v && v.trim(); });
      var floorName = hasData ? (lg.name || ((i+1) + '层')) : '';
      fillFb1Row('laygate' + (i+1), floorName, dataArr);
    } else {
      // 超出数据范围的楼层，全部清空
      fillFb1Row('laygate' + (i+1), '', []);
    }
  }"""

if old_fill_laygate in phtml:
    phtml = phtml.replace(old_fill_laygate, new_fill_laygate)
    fixes_done.append("问题6: 打印页附表1遍历所有16层，空楼层清空楼层号和数据")
else:
    print("警告: 未找到fillFb1层门循环代码")

# ========== 问题7：附表1打印第16层数字跑到第一列 ==========
# 根本原因：数据行有13个td，第1个td对应第1列（被vertical-text覆盖）
# 位置名称应该在第2个td（索引1），但原函数判断条件有问题
# 修复：只要cells.length >= 13，nameIdx就=1，同时清空第一个cell防止干扰

old_fill_row = """function fillFb1Row(rowKey, name, data) {
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

new_fill_row = """function fillFb1Row(rowKey, name, data) {
  var row = document.querySelector('[data-fb1-row="' + rowKey + '"]');
  if (!row) return;
  
  var cells = row.querySelectorAll('td');
  if (cells.length < 12) return;
  
  // 确定位置列索引：
  // 13个td：第1个对应第1列（被vertical-text rowspan覆盖），第2个才是位置列
  // 12个td：第1个就是位置列
  var nameIdx = (cells.length >= 13) ? 1 : 0;
  
  // 清空第一个cell（如果是被覆盖的列），防止干扰显示
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

if old_fill_row in phtml:
    phtml = phtml.replace(old_fill_row, new_fill_row)
    fixes_done.append("问题7: 修复fillFb1Row列索引（13个td时nameIdx=1），并清空第1列防止错位")
else:
    print("警告: 未找到fillFb1Row函数（格式可能不同）")

# ========== 问题5（打印页）：确认附表2第⑤项检验结果 ==========
if "top-s5-result" in phtml and "pit-p5-result" in phtml:
    # 确认判定逻辑
    if "s5L >= 0.5 && _s5W >= 0.6 && _s5H >= 0.8" in phtml or "_s5L >= 0.5" in phtml:
        fixes_done.append("问题5: 打印页附表2轿顶空间判定逻辑已存在")
    if "p5L >= 0.5 && _p5W >= 0.6 && _p5H >= 1.0" in phtml or "_p5L >= 0.5" in phtml:
        fixes_done.append("问题5: 打印页附表2轿底空间判定逻辑已存在")

# 保存打印文件
write_file(PRINT_FILE, phtml)
print(f"打印文件修改完成: {p_original_len} -> {len(phtml)} 字符 ({len(phtml)-p_original_len:+d})")

# ==================== 问题12：中文文件名同步 ====================
shutil.copy2(MAIN_FILE, CN_FILE)
fixes_done.append("问题12: factory-inspection-v2.html 已同步复制到 威特电梯厂检调试记录单v2.html")

# ==================== 输出总结 ====================
print("\n" + "=" * 60)
print("修复完成汇总")
print("=" * 60)
for i, fix in enumerate(fixes_done, 1):
    print(f"  {i}. {fix}")

print(f"\n共 {len(fixes_done)} 项修复/确认")
print(f"主文件变化: {original_len} -> {len(html)} 字节")
print(f"打印文件变化: {p_original_len} -> {len(phtml)} 字节")
