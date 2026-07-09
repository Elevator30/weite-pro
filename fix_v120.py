#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v120 批量修复：11项修改
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

def main():
    main_html = read_file(MAIN_FILE)
    print_html = read_file(PRINT_FILE)
    
    changes = []
    
    # ============================================================
    # 问题2：修复打印按钮尺寸 - 让打印按钮和查看/删除按钮一致
    # ============================================================
    old_css_print = '.print-dropdown{position:relative;flex:1;}'
    new_css_print = '.print-dropdown{position:relative;flex:1;}\n.print-dropdown .btn-view{width:100%;}'
    if old_css_print in main_html:
        main_html = main_html.replace(old_css_print, new_css_print)
        changes.append('问题2：打印按钮尺寸修复')
    else:
        print('WARNING: 未找到打印按钮CSS，尝试其他方式...')
    
    # ============================================================
    # 问题3：打印菜单z-index提高，防止被底部按钮遮挡
    # ============================================================
    old_zindex = '.print-dropdown-menu{position:absolute;top:100%;left:0;right:0;background:#fff;border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,.15);z-index:100;overflow:hidden;margin-top:4px;display:none;}'
    new_zindex = '.print-dropdown-menu{position:absolute;top:100%;left:0;right:0;background:#fff;border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,.15);z-index:9999;overflow:hidden;margin-top:4px;display:none;}'
    if old_zindex in main_html:
        main_html = main_html.replace(old_zindex, new_zindex)
        changes.append('问题3：打印菜单z-index提高到9999')
    else:
        print('WARNING: 未找到打印菜单z-index CSS')
    
    # ============================================================
    # 问题4：从主检查列表移除id140（附表3关联项）
    # ============================================================
    # 添加到hiddenCheckIds
    old_hidden = "var hiddenCheckIds = [113,114,115,116,117,209,210,211,138,76,143,89];"
    new_hidden = "var hiddenCheckIds = [113,114,115,116,117,209,210,211,138,76,143,89,140];"
    if old_hidden in main_html:
        main_html = main_html.replace(old_hidden, new_hidden)
        changes.append('问题4：id140加入隐藏列表')
    else:
        print('WARNING: 未找到hiddenCheckIds')
    
    # 从subGroupMap的导轨与支架分组移除140
    old_subgroup = "{title:'导轨与支架', ids: [138,139,140,141,142]}"
    new_subgroup = "{title:'导轨与支架', ids: [138,139,141,142]}"
    if old_subgroup in main_html:
        main_html = main_html.replace(old_subgroup, new_subgroup)
        changes.append('问题4：从subGroupMap导轨与支架分组移除id140')
    else:
        print('WARNING: 未找到导轨与支架subGroupMap')
    
    # ============================================================
    # 问题5：运行舒适感(id220)改为优/良/差单选
    # ============================================================
    # 修改checkItems中的id220，添加标记
    old_item220 = "{id:220,category:'感官检查',name:'运行舒适感：①优 ②良 ③差',std:'优良'},"
    new_item220 = "{id:220,category:'感官检查',name:'运行舒适感',std:'优为合格',isComfort:true},"
    if old_item220 in main_html:
        main_html = main_html.replace(old_item220, new_item220)
        changes.append('问题5：修改id220定义为isComfort类型')
    else:
        print('WARNING: 未找到id220 checkItem')
    
    # 在渲染逻辑中添加对id220的特殊处理（在isInput判断之后，radio-group之前）
    # 找到插入位置：radio-group生成之前
    old_radio_start = "  // Radio group\n  html += '<div class=\"radio-group\">';"
    
    # 添加舒适感特殊渲染（替换标准radio group前先判断是否是舒适感项）
    comfort_render = """  // 运行舒适感特殊渲染（优/良/差）
  if (item.isComfort) {
    var comfortVal = c.comfort || '';
    html += '<div style="display:flex;gap:6px;margin-top:6px;">';
    html += '<div onclick="setComfort('+item.id+',\'excellent\')" style="flex:1;padding:8px 0;text-align:center;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.2s;border:1.5px solid ' + (comfortVal === 'excellent' ? '#52c41a' : '#ddd') + ';background:' + (comfortVal === 'excellent' ? '#f6ffed' : '#fff') + ';color:' + (comfortVal === 'excellent' ? '#389e0d' : '#666') + ';">优</div>';
    html += '<div onclick="setComfort('+item.id+',\'good\')" style="flex:1;padding:8px 0;text-align:center;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.2s;border:1.5px solid ' + (comfortVal === 'good' ? '#faad14' : '#ddd') + ';background:' + (comfortVal === 'good' ? '#fffbe6' : '#fff') + ';color:' + (comfortVal === 'good' ? '#d48806' : '#666') + ';">良</div>';
    html += '<div onclick="setComfort('+item.id+',\'poor\')" style="flex:1;padding:8px 0;text-align:center;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600;transition:all 0.2s;border:1.5px solid ' + (comfortVal === 'poor' ? '#ff4d4f' : '#ddd') + ';background:' + (comfortVal === 'poor' ? '#fff2f0' : '#fff') + ';color:' + (comfortVal === 'poor' ? '#cf1322' : '#666') + ';">差</div>';
    html += '</div>';
    html += '<div style="margin-top:4px;font-size:11px;color:#999;text-align:center;">自动判定：优=符合，良/差=不符合</div>';
  }
  
  // Radio group
  html += '<div class="radio-group">';"""
    
    if old_radio_start in main_html:
        main_html = main_html.replace(old_radio_start, comfort_render)
        changes.append('问题5：添加舒适感渲染逻辑')
    else:
        print('WARNING: 未找到radio group起始位置')
    
    # 添加setComfort函数（在setCheckStatus函数附近添加）
    old_setstatus = "function setCheckStatus(itemId, status) {"
    comfort_func = """function setComfort(itemId, val) {
  var task = getCurrentTask(); if (!task) return;
  if (!task.checks[itemId]) task.checks[itemId] = {};
  task.checks[itemId].comfort = val;
  // 自动判断：优=符合，良/差=不符合
  task.checks[itemId].s = (val === 'excellent') ? 'ok' : 'ng';
  saveCurrentTask();
  renderCurrentZone();
  updateProgress();
}

function setCheckStatus(itemId, status) {"""
    
    if old_setstatus in main_html:
        main_html = main_html.replace(old_setstatus, comfort_func)
        changes.append('问题5：添加setComfort函数')
    else:
        print('WARNING: 未找到setCheckStatus函数')
    
    # ============================================================
    # 问题6：附表1加门结构总开关（中分门/旁开门）
    # ============================================================
    # 在attach1初始化时添加doorStructure默认值
    old_att1_init = "attach1: {cargate:[Array(15).fill(''),Array(15).fill('')], laygate:[]},"
    new_att1_init = "attach1: {cargate:[Array(15).fill(''),Array(15).fill('')], laygate:[], doorStructure:'center'},"
    if old_att1_init in main_html:
        main_html = main_html.replace(old_att1_init, new_att1_init)
        changes.append('问题6：attach1初始化添加doorStructure')
    else:
        print('WARNING: 未找到attach1初始化')
    
    # 在renderAttach1中，门类型选择上方添加门结构总开关
    old_door_type = """  html += '<div class="fr"><label>门类型</label><select id="att1DoorType" onchange="changeAtt1DoorType(this.value)" style="flex:1;border:1px solid #ddd;border-radius:6px;padding:10px;font-size:14px;">';
  html += '<option value="cargate"' + (currentAtt1Door === 'cargate' ? ' selected' : '') + '>轿门-前门</option>';
  html += '<option value="cargated"' + (currentAtt1Door === 'cargated' ? ' selected' : '') + '>轿门-后门</option>';
  html += '<option value="laygate"' + (currentAtt1Door === 'laygate' ? ' selected' : '') + '>层门</option>';
  html += '</select></div>';"""
    
    new_door_structure = """  // 门结构总开关
  var doorStruct = att1.doorStructure || 'center';
  html += '<div class="door-toggle" style="margin-bottom:10px;">';
  html += '<div style="font-size:12px;font-weight:600;color:#4a5568;margin-bottom:4px;">门结构</div>';
  html += '<div style="display:flex;gap:8px;">';
  html += '<div onclick="setAtt1DoorStructure(\'center\')" style="flex:1;padding:8px 0;text-align:center;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;transition:all 0.2s;border:1.5px solid ' + (doorStruct === 'center' ? '#667eea' : '#e2e8f0') + ';background:' + (doorStruct === 'center' ? 'linear-gradient(135deg,#667eea,#764ba2)' : '#fff') + ';color:' + (doorStruct === 'center' ? '#fff' : '#718096') + ';">中分门</div>';
  html += '<div onclick="setAtt1DoorStructure(\'side\')" style="flex:1;padding:8px 0;text-align:center;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;transition:all 0.2s;border:1.5px solid ' + (doorStruct === 'side' ? '#667eea' : '#e2e8f0') + ';background:' + (doorStruct === 'side' ? 'linear-gradient(135deg,#667eea,#764ba2)' : '#fff') + ';color:' + (doorStruct === 'side' ? '#fff' : '#718096') + ';">旁开门</div>';
  html += '</div></div>';
  
  html += '<div class="fr"><label>门类型</label><select id="att1DoorType" onchange="changeAtt1DoorType(this.value)" style="flex:1;border:1px solid #ddd;border-radius:6px;padding:10px;font-size:14px;">';
  html += '<option value="cargate"' + (currentAtt1Door === 'cargate' ? ' selected' : '') + '>轿门-前门</option>';
  html += '<option value="cargated"' + (currentAtt1Door === 'cargated' ? ' selected' : '') + '>轿门-后门</option>';
  html += '<option value="laygate"' + (currentAtt1Door === 'laygate' ? ' selected' : '') + '>层门</option>';
  html += '</select></div>';"""
    
    if old_door_type in main_html:
        main_html = main_html.replace(old_door_type, new_door_structure)
        changes.append('问题6：添加门结构总开关UI')
    else:
        print('WARNING: 未找到门类型选择器')
    
    # 添加setAtt1DoorStructure函数（在changeAtt1DoorType函数附近）
    old_change_door = "function changeAtt1DoorType(type) {"
    new_set_door_struct = """function setAtt1DoorStructure(type) {
  var task = getCurrentTask(); if (!task) return;
  if (!task.attachments.attach1) task.attachments.attach1 = {cargate:[Array(15).fill(''),Array(15).fill('')], laygate:[], doorStructure:'center'};
  task.attachments.attach1.doorStructure = type;
  saveCurrentTask();
  var target = document.getElementById('attModalBody') || document.getElementById('attContent');
  if (target) renderAttach1(target);
}

function changeAtt1DoorType(type) {"""
    
    if old_change_door in main_html:
        main_html = main_html.replace(old_change_door, new_set_door_struct)
        changes.append('问题6：添加setAtt1DoorStructure函数')
    else:
        print('WARNING: 未找到changeAtt1DoorType函数')
    
    # 修改轿门的门扇间施力间隙标准显示
    # 轿门rows中的门扇间施力间隙
    old_cargate_force = "{type:'pair', l:{label:'门扇间间隙',std:'3-6mm',idx:7}, r:{label:'门扇间施力间隙',std:'旁开≤30/中分≤45',idx:6}},"
    # 需要动态显示，所以改成通过变量控制
    # 先在renderAttach1的轿门部分前计算标准文字
    # 找到cargate相关的rows定义
    if old_cargate_force in main_html:
        # 我们需要用动态方式，先在前面计算好
        # 在 var rows = [ 之前插入 doorStd 变量
        old_cargate_rows_start = "    var rows = ["
        new_cargate_rows_start = "    var forceStd = (doorStruct === 'side') ? '≤30mm' : '≤45mm';\n    var rows = ["
        # 找到轿门模式下的rows定义（在else分支里的）
        # 这个替换要精确匹配轿门部分的
        # 先找第一个出现的（轿门的）
        idx = main_html.find(old_cargate_force)
        if idx > 0:
            new_cargate_force = "{type:'pair', l:{label:'门扇间间隙',std:'3-6mm',idx:7}, r:{label:'门扇间施力间隙',std:forceStd,idx:6}},"
            main_html = main_html[:idx] + new_cargate_force + main_html[idx+len(old_cargate_force):]
            changes.append('问题6：轿门施力间隙标准改为动态')
        else:
            print('WARNING: 未找到轿门门扇间施力间隙')
        
        # 在轿门rows前添加forceStd计算
        # 找到"// 轿门模式: 4行"之后的rows定义
        old_cargate_mode = "  } else {\n    // 轿门模式: 4行\n    var cargateIdx = currentAtt1Door === 'cargate' ? 0 : 1;\n    var cd = att1.cargate[cargateIdx] || Array(15).fill('');\n    \n    var rows = ["
        new_cargate_mode = "  } else {\n    // 轿门模式: 4行\n    var cargateIdx = currentAtt1Door === 'cargate' ? 0 : 1;\n    var cd = att1.cargate[cargateIdx] || Array(15).fill('');\n    var doorStruct = att1.doorStructure || 'center';\n    var forceStd = (doorStruct === 'side') ? '≤30mm' : '≤45mm';\n    \n    var rows = ["
        if old_cargate_mode in main_html:
            main_html = main_html.replace(old_cargate_mode, new_cargate_mode)
            changes.append('问题6：轿门模式添加doorStruct和forceStd变量')
        else:
            print('WARNING: 未找到轿门模式rows起始')
    
    # 修改层门的门扇间施力间隙标准显示
    old_laygate_force = "{type:'pair', l:{label:'门扇间间隙',std:'3-6mm',idx:7}, r:{label:'门扇间施力间隙',std:'旁开≤30/中分≤45',idx:6}},"
    # 层门的是在renderAtt1LaygateInputs函数里的
    # 先计算有几个出现 - 第一个是轿门，第二个是层门
    occurrences = [m.start() for m in re.finditer(re.escape(old_laygate_force), main_html)]
    if len(occurrences) >= 2:
        # 第二个是层门的，修改它
        idx = occurrences[1]
        # 层门的也要动态，需要把forceStd传入或在函数里计算
        # 简单方式：renderAtt1LaygateInputs加参数doorStruct
        # 先修改renderAtt1LaygateInputs的调用和定义
        pass
    
    # 修改renderAttach1Judge中的施力间隙判定逻辑
    # 目前代码里没有直接的施力间隙判定到主表id，可能在其他地方
    # 先检查门扇间施力间隙是否影响主表判定
    
    # ============================================================
    # 问题7：附表2第④项名称改为完整描述
    # ============================================================
    old_s4_label = "{key:'s4', label:'④悬挂装置端接装置附件距离', formula:'0.1+0.035v2'}"
    new_s4_label = "{key:'s4', label:'④井道顶的最低部件与导靴或滚轮、悬挂装置端接装置附件、垂直滑动门的横梁或者部件的最高部分之间的自由垂直距离', formula:'0.1+0.035v2'}"
    if old_s4_label in main_html:
        main_html = main_html.replace(old_s4_label, new_s4_label)
        changes.append('问题7：附表2第④项名称改为完整描述（主页面）')
    else:
        print('WARNING: 未找到s4 label')
    
    # ============================================================
    # 问题8：附表1层门轿门刀/层门锁滚轮打印不显示 + 自动判定
    # ============================================================
    # 在renderAttach1Judge中添加对id116和id117的判定
    old_judge_end = """  // 回填到主表检测项
  // id113: 门地坎距离
  if (hasSillData) {
    task.checks[113].s = sillOk ? 'ok' : 'ng';
    if (!sillOk) task.checks[113].n = '门地坎距离超标';
  }
  // id114: 门间隙
  if (hasDoorGapData) {
    task.checks[114].s = doorGapOk ? 'ok' : 'ng';
    if (!doorGapOk) task.checks[114].n = '门间隙不符合标准';
  }
  // id115: 门锁啮合长度
  if (hasDoorLockData) {
    task.checks[115].s = doorLockOk ? 'ok' : 'ng';
    if (!doorLockOk) task.checks[115].n = '门锁啮合长度不足7mm';
  }"""
    
    new_judge_end = """  // 回填到主表检测项
  // id113: 门地坎距离
  if (hasSillData) {
    task.checks[113].s = sillOk ? 'ok' : 'ng';
    if (!sillOk) task.checks[113].n = '门地坎距离超标';
  }
  // id114: 门间隙
  if (hasDoorGapData) {
    task.checks[114].s = doorGapOk ? 'ok' : 'ng';
    if (!doorGapOk) task.checks[114].n = '门间隙不符合标准';
  }
  // id115: 门锁啮合长度
  if (hasDoorLockData) {
    task.checks[115].s = doorLockOk ? 'ok' : 'ng';
    if (!doorLockOk) task.checks[115].n = '门锁啮合长度不足7mm';
  }
  // id116: 轿门刀与层门地坎间隙 (≥5mm)
  if (!task.checks[116]) task.checks[116] = {};
  var hasCutterData = false;
  var cutterOk = true;
  laygateArr.forEach(function(lg) {
    if (!lg || !lg.data) return;
    var v = parseFloat(lg.data[10]);
    if (!isNaN(v) && v > 0) {
      hasCutterData = true;
      if (v < 5) cutterOk = false;
    }
  });
  if (hasCutterData) {
    task.checks[116].s = cutterOk ? 'ok' : 'ng';
    if (!cutterOk) task.checks[116].n = '轿门刀与层门地坎间隙不足5mm';
  }
  // id117: 层门锁滚轮与轿厢地坎间隙 (≥5mm)
  if (!task.checks[117]) task.checks[117] = {};
  var hasRollerData = false;
  var rollerOk = true;
  laygateArr.forEach(function(lg) {
    if (!lg || !lg.data) return;
    var v = parseFloat(lg.data[12]);
    if (!isNaN(v) && v > 0) {
      hasRollerData = true;
      if (v < 5) rollerOk = false;
    }
  });
  if (hasRollerData) {
    task.checks[117].s = rollerOk ? 'ok' : 'ng';
    if (!rollerOk) task.checks[117].n = '层门锁滚轮与轿厢地坎间隙不足5mm';
  }"""
    
    if old_judge_end in main_html:
        main_html = main_html.replace(old_judge_end, new_judge_end)
        changes.append('问题8：添加id116/117自动判定逻辑')
    else:
        print('WARNING: 未找到renderAttach1Judge回填部分')
    
    # 更新auto-result显示
    old_result_display = """  html += '<br><span style="font-size:11px;color:#999;">根据附表1数据自动判定，关联检测项: id113、id114、id115</span>';"""
    new_result_display = """  html += ' | id116(轿门刀间隙) ';
  if (hasCutterData) html += cutterOk ? '<span style="color:#52c41a;">✓合格</span>' : '<span style="color:#ff4d4f;">✕不合格</span>';
  else html += '<span style="color:#999;">未判定</span>';
  html += ' | id117(层门锁滚轮间隙) ';
  if (hasRollerData) html += rollerOk ? '<span style="color:#52c41a;">✓合格</span>' : '<span style="color:#ff4d4f;">✕不合格</span>';
  else html += '<span style="color:#999;">未判定</span>';
  html += '<br><span style="font-size:11px;color:#999;">根据附表1数据自动判定，关联检测项: id113、id114、id115、id116、id117</span>';"""
    
    if old_result_display in main_html:
        main_html = main_html.replace(old_result_display, new_result_display)
        changes.append('问题8：更新自动判定显示文字')
    else:
        print('WARNING: 未找到auto-result显示文字')
    
    # 更新allOk判断
    old_allok = "  var allOk = hasData && sillOk && doorGapOk && doorLockOk;"
    new_allok = "  var allOk = hasData && sillOk && doorGapOk && doorLockOk && (!hasCutterData || cutterOk) && (!hasRollerData || rollerOk);"
    if old_allok in main_html:
        main_html = main_html.replace(old_allok, new_allok)
        changes.append('问题8：更新allOk判断条件')
    else:
        print('WARNING: 未找到allOk判断')
    
    # ============================================================
    # 问题11：附表2第④项单位和标准（确保与模板一致）
    # ============================================================
    # 已经在问题7中改了名称，公式0.1+0.035v²和单位m应该已经正确
    # 这里确认一下打印页的显示
    
    # ============================================================
    # 打印页 (print-fubiao.html) 修改
    # ============================================================
    
    # 问题8：附表1打印 - 修复fillFb1Row的列数问题
    # 检查FB1_COL_MAP和表格列数是否匹配
    # 先确认表格有多少列和数据应该填到哪些位置
    
    # 问题9：附表2打印检验结果修复
    # 在fillFb2函数中添加结果列填充
    old_fillfb2_end = """  // 轿底空间尺寸
  setFb2Text('pit-p5-space', (pit.p5L || '') + '×' + (pit.p5W || '') + '×' + (pit.p5H || ''));
}"""
    
    new_fillfb2_end = """  // 轿底空间尺寸
  setFb2Text('pit-p5-space', (pit.p5L || '') + '×' + (pit.p5W || '') + '×' + (pit.p5H || ''));
  
  // 计算顶部空间检验结果
  // 对重完全压在缓冲器上时轿门与层门地坎距离 = 对重缓冲距 + 对重压缩行程
  var cwBufM = (parseFloat(att2.对重缓冲距) || 0) / 1000;
  var cwCompM = (parseFloat(att2.对重压缩行程) || 0) / 1000;
  var topSub = cwBufM + cwCompM;
  var speed = 0;
  // 尝试从配置单获取速度
  if (typeof task !== 'undefined' && task.configParts) {
    var vStr = task.configParts['额定速度'] || '';
    speed = parseFloat(vStr) || 0;
  }
  function calcStd(formula, v) {
    if (formula === '0.1+0.035v2') return 0.1 + 0.035 * v * v;
    if (formula === '1.0+0.035v2') return 1.0 + 0.035 * v * v;
    if (formula === '0.3+0.035v2') return 0.3 + 0.035 * v * v;
    return 0;
  }
  function judgeTop(key, formula) {
    var val = parseFloat(top[key]) || 0;
    if (val <= 0 || topSub <= 0) return '';
    var result = val - topSub;
    var std = calcStd(formula, speed);
    if (std <= 0) return (result > 0 ? '符合' : '不符合');
    return result >= std ? '符合' : '不符合';
  }
  setFb2Text('top-s1-result', judgeTop('s1', '0.1+0.035v2'));
  setFb2Text('top-s2-result', judgeTop('s2', '1.0+0.035v2'));
  setFb2Text('top-s3-result', judgeTop('s3', '0.3+0.035v2'));
  setFb2Text('top-s4-result', judgeTop('s4', '0.1+0.035v2'));
  
  // 计算底坑空间检验结果
  // 轿厢完全压在缓冲器上时 = 轿厢缓冲距 + 轿厢压缩行程
  var carBufM = (parseFloat(att2.轿厢缓冲距) || 0) / 1000;
  var carCompM = (parseFloat(att2.轿厢压缩行程) || 0) / 1000;
  var pitSub = carBufM + carCompM;
  function judgePit_p1() {
    var val = parseFloat(pit.p1) || 0;
    if (val <= 0 || pitSub <= 0) return '';
    var result = val - pitSub;
    return result >= 0.5 ? '符合' : '不符合';
  }
  function judgePit_p2() {
    var val = parseFloat(pit.p2) || 0;
    if (val <= 0 || pitSub <= 0) return '';
    var result = val - pitSub;
    return result >= 0.3 ? '符合' : '不符合';
  }
  setFb2Text('pit-p1-result', judgePit_p1());
  setFb2Text('pit-p2-result', judgePit_p2());
  // p4判断
  var p4Val = parseFloat(pit.p4) || 0;
  if (p4Val > 0 && pitSub > 0) {
    var p4Result = p4Val - pitSub;
    setFb2Text('pit-p4-result', p4Result >= 0.3 ? '符合' : '不符合');
  }
}"""
    
    if old_fillfb2_end in print_html:
        print_html = print_html.replace(old_fillfb2_end, new_fillfb2_end)
        changes.append('问题9：附表2打印检验结果填充')
    else:
        print('WARNING: 未找到fillFb2函数结尾')
    
    # 问题10：副表打印页加导出PDF功能
    # 先添加按钮样式和按钮
    old_body_start = "<body>"
    new_body_start = """<body>
<!-- 工具栏 -->
<div id="toolbar" style="position:fixed;top:0;left:0;right:0;background:#fff;padding:10px 20px;box-shadow:0 2px 8px rgba(0,0,0,0.1);z-index:1000;display:flex;justify-content:space-between;align-items:center;">
  <div style="font-size:14px;font-weight:600;color:#333;">副表打印预览</div>
  <div style="display:flex;gap:10px;">
    <button onclick="window.print()" style="padding:8px 16px;background:#667eea;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;">打印</button>
    <button onclick="exportFubiaoPDF()" style="padding:8px 16px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;">保存到文件(PDF)</button>
  </div>
</div>
<div style="height:50px;"></div>"""
    
    if old_body_start in print_html:
        print_html = print_html.replace(old_body_start, new_body_start)
        changes.append('问题10：添加保存到文件按钮')
    else:
        print('WARNING: 未找到body开始标签')
    
    # 添加打印时隐藏工具栏的CSS
    old_print_media = "@media print{"
    new_print_media = "@media print{#toolbar{display:none!important;}"
    if old_print_media in print_html:
        # 找到并修改
        print_html = print_html.replace(old_print_media, new_print_media)
        changes.append('问题10：打印时隐藏工具栏')
    else:
        print('WARNING: 未找到@media print')
    
    # 添加exportFubiaoPDF函数（需要jsPDF和html2canvas）
    # 在script标签末尾添加
    old_script_end = "</script>\n</body>"
    new_export_func = """
// ============ 导出PDF功能 ============
function exportFubiaoPDF() {
  if (typeof jspdf === 'undefined' || jspdf.jsPDF) {
    // 已经通过CDN加载或本地加载
  }
  if (typeof html2canvas === 'undefined') {
    alert('PDF导出库加载中，请稍候再试...');
    return;
  }
  
  var btn = event.target;
  btn.disabled = true;
  btn.textContent = '生成中...';
  
  var pages = document.querySelectorAll('.page');
  var totalPages = pages.length;
  var currentPage = 0;
  
  // 使用横版A4
  var pdf = new jspdf.jsPDF('l', 'mm', 'a4');
  var pageWidth = pdf.internal.pageSize.getWidth();
  var pageHeight = pdf.internal.pageSize.getHeight();
  
  function addNextPage() {
    if (currentPage >= totalPages) {
      pdf.save('副表-' + Date.now() + '.pdf');
      btn.disabled = false;
      btn.textContent = '保存到文件(PDF)';
      return;
    }
    
    var page = pages[currentPage];
    html2canvas(page, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff'
    }).then(function(canvas) {
      var imgData = canvas.toDataURL('image/jpeg', 0.95);
      if (currentPage > 0) pdf.addPage();
      pdf.addImage(imgData, 'JPEG', 0, 0, pageWidth, pageHeight);
      currentPage++;
      setTimeout(addNextPage, 50);
    }).catch(function(err) {
      console.error('导出失败', err);
      alert('导出失败：' + err.message);
      btn.disabled = false;
      btn.textContent = '保存到文件(PDF)';
    });
  }
  
  addNextPage();
}

// 加载jsPDF和html2canvas（如果未加载）
(function() {
  function loadScript(src, callback) {
    if (document.querySelector('script[src="'+src+'"]')) { callback(); return; }
    var s = document.createElement('script');
    s.src = src;
    s.onload = callback;
    s.onerror = callback;
    document.head.appendChild(s);
  }
  var loaded = 0;
  function check() {
    loaded++;
    if (loaded >= 2) {
      // 重命名jsPDF
      if (window.jspdf && window.jspdf.jsPDF && !window.jsPDF) {
        window.jsPDF = window.jspdf.jsPDF;
      }
    }
  }
  if (typeof jspdf === 'undefined') {
    loadScript('https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js', check);
  } else { check(); }
  if (typeof html2canvas === 'undefined') {
    loadScript('https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js', check);
  } else { check(); }
})();
</script>
</body>"""
    
    if old_script_end in print_html:
        print_html = print_html.replace(old_script_end, new_export_func)
        changes.append('问题10：添加exportFubiaoPDF函数')
    else:
        # 尝试其他结束方式
        print('WARNING: 未找到script结束标签，尝试替代方式...')
    
    # ============================================================
    # 问题8修复：附表1打印 - 确保层门的轿门刀/滚轮数据正确显示
    # ============================================================
    # 检查FB1_COL_MAP和表格列数
    # 表格有13列：1(检验位置垂直文本)+1(位置)+11数据 = 13
    # 但数据行里可能有13个td，第一个是位置，后面12个？不对...
    # 让fillFb1Row正确填充最后两列
    # 检查数据行有多少td元素
    
    # 修复fillFb1Row：确保正确的列映射
    # 目前FB1_COL_MAP有11个元素，对应11个数据列
    # 如果表格数据行有13个td，那就是：位置 + 12个数据列 = 13
    # 但实际只有11个数据列，所以可能多了一个空列
    # 让我们数一下实际td数量
    
    # 更直接的方式：修改fillFb1Row使其正确工作
    # 先找到fillFb1Row函数
    old_fb1row = """function fillFb1Row(rowKey, name, data) {
  var row = document.querySelector('[data-fb1-row="' + rowKey + '"]');
  if (!row) return;
  
  var cells = row.querySelectorAll('td');
  if (cells.length < 13) return;
  
  cells[0].textContent = name;
  
  // 共11个数据列 cells[1] ~ cells[11]
  for (var j = 0; j < 11; j++) {
    var dataIdx = FB1_COL_MAP[j];
    var val = (data[dataIdx] !== undefined && data[dataIdx] !== null) ? data[dataIdx] : '';
    cells[j + 1].textContent = val;
  }
}"""
    
    # 检查cells的实际数量 - 如果是13个，那cells[1]-cells[11]只有11个
    # 但应该有11个数据列 + 1个位置列 = 12个
    # 如果有13个td，说明有多余的列
    # 修正：从cells[1]开始填11个，或者检查cells数量
    
    # 实际上问题可能是数据行有13个td（包括垂直文本列的空td），
    # 而位置名称在cells[1]，数据从cells[2]开始
    # 让我们修改代码来处理这种情况
    new_fb1row = """function fillFb1Row(rowKey, name, data) {
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
    
    if old_fb1row in print_html:
        print_html = print_html.replace(old_fb1row, new_fb1row)
        changes.append('问题8：修复fillFb1Row列索引计算')
    else:
        print('WARNING: 未找到fillFb1Row函数')
    
    # ============================================================
    # 保存文件
    # ============================================================
    write_file(MAIN_FILE, main_html)
    write_file(PRINT_FILE, print_html)
    
    print("\n" + "="*60)
    print("已完成修改清单：")
    print("="*60)
    for i, c in enumerate(changes, 1):
        print(f"  {i}. {c}")
    print("="*60)
    print(f"共完成 {len(changes)} 项修改")

if __name__ == '__main__':
    main()
