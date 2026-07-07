#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v50.8 全面返工：
1. 检查表三栏布局 float -> flex 修复
2. 附表1-7 全部按Excel模板结构重做
"""

import re

FILE = '威特电梯厂检调试记录单v2.html'
EN_FILE = 'factory-inspection-v2.html'

with open(FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ========== 1. 修复检查表三栏布局 ==========
# 找到三栏布局的行（约6363-6367行），把float改成flex
for i, line in enumerate(lines):
    if 'float:left;width:33.3%;box-sizing:border-box;padding-right:2px;' in line:
        # 外层容器行（上两行）改成flex
        lines[i-1] = lines[i-1].replace(
            '<div style="width:100%;overflow:hidden;">',
            '<div style="display:flex;width:100%;gap:4px;">'
        )
        # 三栏都去掉float，改用flex:1
        lines[i] = lines[i].replace(
            'float:left;width:33.3%;box-sizing:border-box;padding-right:2px;',
            'flex:1;min-width:0;'
        )
        lines[i+1] = lines[i+1].replace(
            'float:left;width:33.3%;box-sizing:border-box;padding:0 2px;',
            'flex:1;min-width:0;'
        )
        lines[i+2] = lines[i+2].replace(
            'float:left;width:33.4%;box-sizing:border-box;padding-left:2px;',
            'flex:1;min-width:0;'
        )
        # 去掉clear:both
        for j in range(i+3, min(i+8, len(lines))):
            if 'clear:both;' in lines[j]:
                lines[j] = lines[j].replace(';clear:both;', ';')
        print(f"  修复三栏布局：第{i+1}行附近")
        break

# ========== 2. 替换 buildSingleAttachHTML 函数 ==========
# 找到函数起始行
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if 'function buildSingleAttachHTML(task, dateStr, attNum)' in line:
        start_idx = i
    if start_idx is not None and i > start_idx + 100:
        # 找函数结束：下一个function之前的 }
        if line.strip() == '}' and i > start_idx + 200:
            # 确认下一行是空行或者注释
            if i+1 < len(lines) and (lines[i+1].strip() == '' or lines[i+1].strip().startswith('//')):
                end_idx = i
                break

print(f"  buildSingleAttachHTML: 第{start_idx+1}行 ~ 第{end_idx+1}行")

# 提取logoBase64（从原函数中）
logo_line = None
for i in range(start_idx, min(start_idx+200, len(lines))):
    if 'var logoBase64' in lines[i]:
        logo_line = i
        break

# 读取logo的完整base64（跨多行，直到 '; 结尾）
logo_lines = []
in_logo = False
for i in range(logo_line, len(lines)):
    if 'var logoBase64' in lines[i]:
        in_logo = True
    if in_logo:
        logo_lines.append(lines[i])
        if lines[i].rstrip().endswith("';") or lines[i].rstrip().endswith("';\n"):
            break
logo_str = ''.join(logo_lines)

# 构建新的buildSingleAttachHTML函数
new_func = '''function buildSingleAttachHTML(task, dateStr, attNum) {
  var att1 = task.attachments.attach1 || {cargate:[Array(15).fill(''),Array(15).fill('')], laygate:[]};
  var att2 = task.attachments.attach2 || {};
  var att3 = task.attachments.attach3 || {rows:[], maxDev:{carL:'',carR:'',weightL:'',weightR:''}};
  var att4 = task.attachments.attach4 || {rows:[], maxDev:{car:'',weight:''}, refCar:'', refWeight:''};
  var att5 = task.attachments.attach5 || {载重:'',电压:{},电流:{},平衡系数:''};
  var att6 = task.attachments.attach6 || {};
  var att7 = task.attachments.attach7 || {};

  // 确保数据完整
  if (!att2.顶部空间) att2.顶部空间 = {s1:'',s2:'',s3:'',s4:'',s5:''};
  if (!att2.底坑空间) att2.底坑空间 = {p1:'',p2:'',p3h1:'',p3v1:'',p3h2:'',p3v2:'',p4:'',p5:''};
  if (!att3.rows || att3.rows.length === 0) att3.rows = Array(10).fill({carL:'',carR:'',weightL:'',weightR:''});
  if (!att3.maxDev) att3.maxDev = {carL:'',carR:'',weightL:'',weightR:''};
  if (!att4.rows || att4.rows.length === 0) att4.rows = Array(10).fill({car:'',weight:''});
  if (!att4.maxDev) att4.maxDev = {car:'',weight:''};

''' + logo_str + '''
  function esc(s) { if (s == null) return ''; return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

  function buildHeader(title, pageLabel) {
    var h = '';
    h += '<div style="position:relative;width:100%;height:100%;padding:0;box-sizing:border-box;font-family:'PingFang SC','Heiti SC','Microsoft YaHei',sans-serif;font-size:8px;line-height:1.3;">';
    // 顶部logo + 标题 + 产品编号
    h += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;border-bottom:1px solid #000;padding-bottom:2px;">';
    h += '<img src="' + logoBase64 + '" style="height:20px;width:auto;">';
    h += '<div style="text-align:center;flex:1;font-weight:bold;font-size:12px;">厂检调试记录单</div>';
    h += '<div style="text-align:right;font-size:7px;">产品编号：' + esc(task.productNo || '') + '</div>';
    h += '</div>';
    // 子标题
    h += '<div style="text-align:center;font-weight:bold;font-size:9px;margin-bottom:4px;">' + title + '</div>';
    return h;
  }

  function buildFooter(label) {
    var h = '';
    h += '<div style="position:absolute;bottom:4px;left:0;right:0;text-align:center;font-size:7px;">— ' + label + ' —</div>';
    h += '</div>';
    return h;
  }

  var h = '';

  // ========== 附表1：电梯门间隙、门锁啮合长度及地坎间距 ==========
  if (attNum === 1) {
    h += buildHeader('附表1  电梯门间隙、门锁啮合长度及地坎间距检验记录', '附表1');
    // 13列表格
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:7px;">';
    h += '<colgroup>';
    h += '<col style="width:7%"><col style="width:8%"><col style="width:6%"><col style="width:6%">'; // 1-4: 检验项目/位置 + 门地坎距离左右
    h += '<col style="width:6%"><col style="width:6%"><col style="width:6%"><col style="width:6%"><col style="width:6%">'; // 5-9: 门间隙(1)的5列
    h += '<col style="width:6%"><col style="width:8%"><col style="width:9%"><col style="width:9%">'; // 10-13: 施力间隙/啮合长度/两项地坎间隙
    h += '</colgroup>';
    // 表头行1
    h += '<tr style="text-align:center;font-weight:bold;background:#f5f5f5;">';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="3">检验项目<br>编号与内容</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">A1.2.7.1</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="6">A1.2.7.2门间隙</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="1" rowspan="3">A1.2.7.8(2)<br>门锁啮合<br>长度</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">A1.2.7.10</td>';
    h += '</tr>';
    // 表头行2
    h += '<tr style="text-align:center;font-weight:bold;background:#f5f5f5;">';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="2">门地坎距离</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="5">A1.2.7.2(1)</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">A1.2.7.2(2)<br>门扇间<br>施力间隙</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">轿门门刀与<br>层门地坎间隙</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">层门门锁滚轮与<br>轿厢地坎间隙</td>';
    h += '</tr>';
    // 表头行3
    h += '<tr style="text-align:center;font-weight:bold;background:#f5f5f5;font-size:6.5px;">';
    h += '<td style="border:1px solid #000;padding:1px;">门扇间<br>间隙</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">门扇与立柱、<br>门楣间隙</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">门扇与<br>地坎间隙</td>';
    h += '</tr>';
    // 判断标准行
    h += '<tr style="text-align:center;font-size:6.5px;background:#fafafa;">';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="2">判断标准</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="2">≤35mm<br>左右偏差<br>小于1/1000</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="5" rowspan="2">乘客电梯：3~6mm<br>载货电梯：3~10mm<br>左右偏差不超过1mm</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">旁开门：≤30<br>中分门：≤45</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">≥7mm</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="2">≥5mm</td>';
    h += '</tr>';
    h += '<tr></tr>'; // 空行（因为rowspan=2）
    // 数据行表头
    h += '<tr style="text-align:center;font-weight:bold;background:#f5f5f5;">';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="19">检验位置<br>及测量<br>数据</td>';
    h += '<td style="border:1px solid #000;padding:1px;">位置</td>';
    h += '<td style="border:1px solid #000;padding:1px;">左</td>';
    h += '<td style="border:1px solid #000;padding:1px;">右</td>';
    h += '<td style="border:1px solid #000;padding:1px;">值</td>';
    h += '<td style="border:1px solid #000;padding:1px;">左</td>';
    h += '<td style="border:1px solid #000;padding:1px;">右</td>';
    h += '<td style="border:1px solid #000;padding:1px;">左</td>';
    h += '<td style="border:1px solid #000;padding:1px;">右</td>';
    h += '<td style="border:1px solid #000;padding:1px;">值</td>';
    h += '<td style="border:1px solid #000;padding:1px;">值</td>';
    h += '<td style="border:1px solid #000;padding:1px;">值</td>';
    h += '<td style="border:1px solid #000;padding:1px;">值</td>';
    h += '</tr>';
    // 轿门1、轿门2 + 15层
    var positions = ['轿门1', '轿门2'];
    for (var f = 1; f <= 15; f++) positions.push(f + '层');
    for (var p = 0; p < positions.length; p++) {
      h += '<tr style="text-align:center;">';
      h += '<td style="border:1px solid #000;padding:1px;">' + positions[p] + '</td>';
      for (var c = 0; c < 11; c++) {
        h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
      }
      h += '</tr>';
    }
    h += '</table>';
    h += buildFooter('附表1');
  }

  // ========== 附表2：缓冲距、顶部空间和底坑空间检测 ==========
  else if (attNum === 2) {
    h += buildHeader('附表2  缓冲距、顶部空间和底坑空间检测记录', '附表2');
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:7px;">';
    h += '<colgroup>';
    h += '<col style="width:8%"><col style="width:34%">'; // 类别 + 项目
    h += '<col style="width:6%"><col style="width:6%">'; // 上端站/下端站 两列
    h += '<col style="width:6%"><col style="width:6%">'; // 完全压缓冲器 两列
    h += '<col style="width:7%"><col style="width:7%">'; // 检验结果 两列？不对
    h += '<col style="width:8%"><col style="width:12%">'; // 调整
    h += '</colgroup>';
    // 行1：轿厢缓冲距区域
    h += '<tr style="text-align:center;font-weight:bold;background:#f5f5f5;">';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="2">轿厢缓冲距</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">mm</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="2">缓冲器压缩行程</td>';
    h += '<td style="border:1px solid #000;padding:1px;">轿厢</td>';
    h += '<td style="border:1px solid #000;padding:1px;">mm</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="2">检验结果</td>';
    h += '</tr>';
    h += '<tr style="text-align:center;font-weight:bold;background:#f5f5f5;">';
    h += '<td style="border:1px solid #000;padding:1px;">对重缓冲距<br>最大允许值</td>';
    h += '<td style="border:1px solid #000;padding:1px;">mm</td>';
    h += '<td style="border:1px solid #000;padding:1px;">对重</td>';
    h += '<td style="border:1px solid #000;padding:1px;">mm</td>';
    h += '</tr>';
    // 空行（轿厢缓冲距数据行）
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    for (var i = 0; i < 8; i++) h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    // 井道顶部空间 表头
    h += '<tr style="text-align:center;font-weight:bold;background:#f5f5f5;">';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="6">井道顶部空间</td>';
    h += '<td style="border:1px solid #000;padding:1px;">项  目        状  态</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">上端站平层时</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">对重完全压在缓冲器上时<br>轿门与层门地坎距离</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="4" rowspan="1">检验结果</td>';
    h += '</tr>';
    // 5个顶部空间项目
    var topItems = [
      '①轿厢导轨进一步制导行程≥0.1+0.035v² (m)',
      '②位于轿厢投影部分的井道顶最低部件的水平面与轿顶最高可站人面积水平面之间的自由垂直距离≥1.0+0.035v (m)',
      '③井道顶最低部件与固定在轿顶部件最高部分之间的自由垂直距离≥0.3+0.035v (m)',
      '④井道顶的最低部件与导靴或滚轮、悬挂装置端接装置附件、垂直滑动门的横梁或者部件的最高部分之间的自由垂直距离≥0.1+0.035v² (m)',
      '⑤轿顶空间（≥0.5m×0.6m×0.8m）'
    ];
    for (var t = 0; t < topItems.length; t++) {
      h += '<tr>';
      h += '<td style="border:1px solid #000;padding:1px;font-size:6.5px;">' + topItems[t] + '</td>';
      if (t < 4) {
        h += '<td style="border:1px solid #000;padding:1px;text-align:center;">m</td>';
        h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
        h += '<td style="border:1px solid #000;padding:1px;text-align:center;">m</td>';
        h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
      } else {
        h += '<td style="border:1px solid #000;padding:1px;text-align:center;" colspan="2">&nbsp;</td>';
        h += '<td style="border:1px solid #000;padding:1px;text-align:center;" colspan="2">&nbsp;</td>';
      }
      h += '<td style="border:1px solid #000;padding:1px;text-align:center;" colspan="4">&nbsp;</td>';
      h += '</tr>';
    }
    // 底坑空间 表头
    h += '<tr style="text-align:center;font-weight:bold;background:#f5f5f5;">';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="7">底坑空间</td>';
    h += '<td style="border:1px solid #000;padding:1px;">项  目        状  态</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">下端站平层时</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">轿厢完全压在缓冲器上时<br>轿门与层门地坎距离</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="4">检验结果</td>';
    h += '</tr>';
    // 底坑项目
    var pitItems = [
      '①底坑底与轿厢最低部件之间的自由垂直距离≥0.5m',
      '②对重导轨进一步制导行程≥0.1+0.035v² (m)',
      null, // 第③项特殊（两行）
      '④底坑中固定的最高部件和轿厢的最低部件之间（b除外）的自由垂直距离≥0.3m',
      '⑤轿底空间（≥0.5m×0.6m×1.0m）'
    ];
    // ①
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;font-size:6.5px;">' + pitItems[0] + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;">m</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;">m</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;" colspan="4">&nbsp;</td>';
    h += '</tr>';
    // ②
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;font-size:6.5px;">' + pitItems[1] + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;">m</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;" colspan="4">&nbsp;</td>';
    h += '</tr>';
    // ③（双行合并）
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;font-size:6.5px;" rowspan="2">③下述水平距离在0.15m之内时，底坑底与轿厢最低部件之间的自由垂直距离≥0.5m</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;font-size:6.5px;">1)<br>水平&nbsp;&nbsp;&nbsp;&nbsp;m<br>&nbsp;<br>垂直&nbsp;&nbsp;&nbsp;&nbsp;m</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;" colspan="4" rowspan="2">&nbsp;</td>';
    h += '</tr>';
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;font-size:6.5px;">2)<br>水平&nbsp;&nbsp;&nbsp;&nbsp;m<br>&nbsp;<br>垂直&nbsp;&nbsp;&nbsp;&nbsp;m</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    // ④
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;font-size:6.5px;">' + pitItems[3] + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;">m</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;" colspan="4">&nbsp;</td>';
    h += '</tr>';
    // ⑤
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;font-size:6.5px;">' + pitItems[4] + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;" colspan="2">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;" colspan="2">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;" colspan="4">&nbsp;</td>';
    h += '</tr>';
    // 备注
    h += '<tr style="font-size:6px;">';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;vertical-align:middle;">备注</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="9">(1)当曳引驱动电梯驱动主机的减速是按照规定被监控时，对于非斜行电梯，0.035可以用按轿厢或者对重触及缓冲器时的速度减小；(2)对于具有补偿绳及补偿绳张紧轮和防跳装置的曳引驱动电梯，0.035v²的值可以用张紧轮可能的移动量再加上轿厢行程的1/500或者二者中较大者</td>';
    h += '</tr>';
    h += '</table>';
    h += buildFooter('附表2');
  }

  // ========== 附表3：导轨工作面铅垂度测量表 ==========
  else if (attNum === 3) {
    h += buildHeader('附表3  导轨工作面铅垂度测量表', '附表3');
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:7px;">';
    h += '<colgroup>';
    h += '<col style="width:5%"><col style="width:9%">'; // 序号 + 导轨类型
    for (var m = 1; m <= 10; m++) h += '<col style="width:7%">'; // 10个测点
    h += '<col style="width:8%">'; // 最大偏差
    h += '</colgroup>';
    // 表头
    h += '<tr style="text-align:center;font-weight:bold;background:#f5f5f5;">';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">序&nbsp;&nbsp;&nbsp;&nbsp;号</td>';
    for (var n = 1; n <= 10; n++) h += '<td style="border:1px solid #000;padding:1px;">' + n + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;">最大偏差</td>';
    h += '</tr>';
    // 轿厢
    var railRows = [
      ['轿厢', '左导轨'],
      ['', '右导轨'],
      ['对重', '左导轨'],
      ['', '右导轨']
    ];
    for (var r = 0; r < railRows.length; r++) {
      h += '<tr style="text-align:center;">';
      if (r % 2 === 0) {
        h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">' + railRows[r][0] + '</td>';
      }
      h += '<td style="border:1px solid #000;padding:1px;">' + railRows[r][1] + '</td>';
      for (var m2 = 0; m2 < 10; m2++) h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
      h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
      h += '</tr>';
    }
    h += '</table>';
    // 标准说明
    h += '<div style="margin-top:4px;font-size:6.5px;border:1px solid #000;padding:2px;">每列导轨工作面每5m铅垂线测量值间的相对最大偏差，轿厢导轨和设有安全钳的T型对重导轨为1.2mm；不设安全钳的T型对重导轨为2mm。</div>';
    h += buildFooter('附表3');
  }

  // ========== 附表4：导轨顶面距离测量 ==========
  else if (attNum === 4) {
    h += buildHeader('附表4  导轨顶面距离测量&nbsp;&nbsp;单位（mm）', '附表4');
    // 左右并排两个表格
    h += '<div style="display:flex;gap:8px;width:100%;">';
    // 左侧：轿厢导轨
    h += '<div style="flex:1;">';
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:7px;">';
    h += '<colgroup><col style="width:20%"><col style="width:40%"><col style="width:40%"></colgroup>';
    h += '<tr style="font-weight:bold;background:#f5f5f5;text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="3">轿厢导轨面距基准：&nbsp;&nbsp;&nbsp;&nbsp;mm（0~+2）</td>';
    h += '</tr>';
    // 10个测点分两行（1-5 / 6-10）
    for (var row = 0; row < 2; row++) {
      h += '<tr style="text-align:center;">';
      for (var col = 0; col < 5; col++) {
        var num = row * 5 + col + 1;
        h += '<td style="border:1px solid #000;padding:1px;">' + num + '</td>';
        if (col === 4 && row === 0) break; // 第一行只有5个序号
      }
      h += '</tr>';
      h += '<tr style="text-align:center;height:16px;">';
      for (var col2 = 0; col2 < 5; col2++) {
        h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
        if (col2 === 4 && row === 0) break;
      }
      h += '</tr>';
    }
    // 最大偏差
    h += '<tr style="text-align:center;font-weight:bold;background:#f5f5f5;">';
    h += '<td style="border:1px solid #000;padding:1px;">最大偏差</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '</tr>';
    h += '</table>';
    h += '</div>';
    // 右侧：对重导轨
    h += '<div style="flex:1;">';
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:7px;">';
    h += '<colgroup><col style="width:20%"><col style="width:40%"><col style="width:40%"></colgroup>';
    h += '<tr style="font-weight:bold;background:#f5f5f5;text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="3">对重导轨面距基准：&nbsp;&nbsp;&nbsp;&nbsp;mm（0~+3）</td>';
    h += '</tr>';
    for (var row2 = 0; row2 < 2; row2++) {
      h += '<tr style="text-align:center;">';
      for (var col3 = 0; col3 < 5; col3++) {
        var num2 = row2 * 5 + col3 + 1;
        h += '<td style="border:1px solid #000;padding:1px;">' + num2 + '</td>';
      }
      h += '</tr>';
      h += '<tr style="text-align:center;height:16px;">';
      for (var col4 = 0; col4 < 5; col4++) {
        h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
      }
      h += '</tr>';
    }
    h += '<tr style="text-align:center;font-weight:bold;background:#f5f5f5;">';
    h += '<td style="border:1px solid #000;padding:1px;">最大偏差</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '</tr>';
    h += '</table>';
    h += '</div>';
    h += '</div>';
    h += '<div style="text-align:right;margin-top:4px;font-size:7px;">— 附表4 —</div>';
    // 手动加底部
    h += '</div>';
  }

  // ========== 附表5：电梯平衡系数检验记录 ==========
  else if (attNum === 5) {
    h += buildHeader('附表5  电梯平衡系数检验记录', '附表5');
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:7px;">';
    h += '<colgroup>';
    h += '<col style="width:12%"><col style="width:8%">'; // 载重量 + 重量
    for (var l = 0; l < 5; l++) { // 5个载荷比，各2列
      h += '<col style="width:8%"><col style="width:8%">';
    }
    h += '</colgroup>';
    // 表头行1 - 载重量
    h += '<tr style="text-align:center;font-weight:bold;background:#f5f5f5;">';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">载重量</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">重量（Kg）<br>额载百分比(%)</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">0.3</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">0.4</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">0.45</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">0.5</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">0.6</td>';
    h += '</tr>';
    // 表头行2 - 运行方向
    h += '<tr style="text-align:center;font-weight:bold;background:#f5f5f5;">';
    for (var d = 0; d < 5; d++) {
      h += '<td style="border:1px solid #000;padding:1px;">上行</td>';
      h += '<td style="border:1px solid #000;padding:1px;">下行</td>';
    }
    h += '</tr>';
    // 电流行
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">电&nbsp;流（A）</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;">&nbsp;</td>';
    for (var c2 = 0; c2 < 10; c++) h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    // 测试结果行 + 平衡系数（合并10列）
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">测试结果</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;">&nbsp;</td>';
    for (var c3 = 0; c3 < 10; c++) h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    // 空行（留作曲线图上方空间？不，电流曲线图在表格下方）
    for (var er = 0; er < 5; er++) {
      h += '<tr>';
      h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
      h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
      for (var c4 = 0; c4 < 10; c4++) h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
      h += '</tr>';
    }
    // 平衡系数行
    h += '<tr style="font-weight:bold;">';
    h += '<td style="border:1px solid #000;padding:1px;text-align:right;" colspan="2">平衡系数：</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;" colspan="10">（0.4~0.5）</td>';
    h += '</tr>';
    h += '</table>';

    // 电流曲线SVG
    var loads = [0.3, 0.4, 0.45, 0.5, 0.6];
    var upData = [];
    var downData = [];
    // 尝试读取att5数据
    try {
      var ratios = [0.3, 0.4, 0.45, 0.5, 0.6];
      for (var ri = 0; ri < ratios.length; ri++) {
        var key = ratios[ri].toString();
        if (att5.电流 && att5.电流[key]) {
          upData.push(parseFloat(att5.电流[key].up) || 0);
          downData.push(parseFloat(att5.电流[key].down) || 0);
        } else {
          upData.push(0);
          downData.push(0);
        }
      }
    } catch(e) { upData = [0,0,0,0,0]; downData = [0,0,0,0,0]; }

    var svgW = 520, svgH = 180;
    var padding = {left: 40, right: 20, top: 20, bottom: 30};
    var chartW = svgW - padding.left - padding.right;
    var chartH = svgH - padding.top - padding.bottom;
    var maxCurrent = 0;
    for (var ui = 0; ui < upData.length; ui++) {
      maxCurrent = Math.max(maxCurrent, upData[ui], downData[ui]);
    }
    if (maxCurrent < 10) maxCurrent = 50;
    maxCurrent = Math.ceil(maxCurrent / 10) * 10;

    function getX(idx) { return padding.left + (idx / (loads.length - 1)) * chartW; }
    function getY(val) { return padding.top + chartH - (val / maxCurrent) * chartH; }

    var svg = '<svg width="' + svgW + '" height="' + svgH + '" style="display:block;margin:4px auto 0;" viewBox="0 0 ' + svgW + ' ' + svgH + '">';
    // 标题
    svg += '<text x="' + (svgW/2) + '" y="14" text-anchor="middle" font-size="10" font-weight="bold">电流曲线示意图</text>';
    // Y轴
    svg += '<line x1="' + padding.left + '" y1="' + padding.top + '" x2="' + padding.left + '" y2="' + (padding.top + chartH) + '" stroke="#000" stroke-width="1"/>';
    // X轴
    svg += '<line x1="' + padding.left + '" y1="' + (padding.top + chartH) + '" x2="' + (padding.left + chartW) + '" y2="' + (padding.top + chartH) + '" stroke="#000" stroke-width="1"/>';
    // Y轴刻度
    var ySteps = 5;
    for (var ys = 0; ys <= ySteps; ys++) {
      var yv = maxCurrent * ys / ySteps;
      var yp = getY(yv);
      svg += '<line x1="' + (padding.left - 3) + '" y1="' + yp + '" x2="' + padding.left + '" y2="' + yp + '" stroke="#000" stroke-width="1"/>';
      svg += '<text x="' + (padding.left - 5) + '" y="' + (yp + 3) + '" text-anchor="end" font-size="7">' + Math.round(yv) + '</text>';
      // 网格线
      svg += '<line x1="' + padding.left + '" y1="' + yp + '" x2="' + (padding.left + chartW) + '" y2="' + yp + '" stroke="#ddd" stroke-width="0.5"/>';
    }
    // Y轴标签
    svg += '<text x="10" y="' + (padding.top + chartH/2) + '" text-anchor="middle" font-size="7" transform="rotate(-90, 10, ' + (padding.top + chartH/2) + ')">电流(A)</text>';
    // X轴刻度和标签
    var loadLabels = ['30%', '40%', '45%', '50%', '60%'];
    for (var xi = 0; xi < loads.length; xi++) {
      var xp = getX(xi);
      svg += '<line x1="' + xp + '" y1="' + (padding.top + chartH) + '" x2="' + xp + '" y2="' + (padding.top + chartH + 3) + '" stroke="#000" stroke-width="1"/>';
      svg += '<text x="' + xp + '" y="' + (padding.top + chartH + 16) + '" text-anchor="middle" font-size="7">' + loadLabels[xi] + '</text>';
    }
    // X轴标签
    svg += '<text x="' + (svgW/2) + '" y="' + (svgH - 4) + '" text-anchor="middle" font-size="7">载荷比</text>';
    // 上行曲线（蓝色）
    var hasUpData = upData.some(function(v){ return v > 0; });
    if (hasUpData) {
      var upPath = 'M';
      for (var ui2 = 0; ui2 < upData.length; ui2++) {
        if (ui2 > 0) upPath += ' L';
        upPath += getX(ui2) + ',' + getY(upData[ui2]);
      }
      svg += '<path d="' + upPath + '" fill="none" stroke="#1e88e5" stroke-width="1.5"/>';
      // 数据点
      for (var ui3 = 0; ui3 < upData.length; ui3++) {
        svg += '<circle cx="' + getX(ui3) + '" cy="' + getY(upData[ui3]) + '" r="2.5" fill="#1e88e5"/>';
      }
    }
    // 下行曲线（红色）
    var hasDownData = downData.some(function(v){ return v > 0; });
    if (hasDownData) {
      var downPath = 'M';
      for (var di = 0; di < downData.length; di++) {
        if (di > 0) downPath += ' L';
        downPath += getX(di) + ',' + getY(downData[di]);
      }
      svg += '<path d="' + downPath + '" fill="none" stroke="#e53935" stroke-width="1.5"/>';
      for (var di2 = 0; di2 < downData.length; di2++) {
        svg += '<circle cx="' + getX(di2) + '" cy="' + getY(downData[di2]) + '" r="2.5" fill="#e53935"/>';
      }
    }
    // 图例
    var legendY = padding.top + 5;
    svg += '<rect x="' + (svgW - 100) + '" y="' + legendY + '" width="10" height="3" fill="#1e88e5"/>';
    svg += '<text x="' + (svgW - 87) + '" y="' + (legendY + 5) + '" font-size="7">—— 上行</text>';
    svg += '<rect x="' + (svgW - 100) + '" y="' + (legendY + 14) + '" width="10" height="3" fill="#e53935"/>';
    svg += '<text x="' + (svgW - 87) + '" y="' + (legendY + 19) + '" font-size="7">—— 下行</text>';

    svg += '</svg>';
    h += svg;

    h += buildFooter('附表5');
  }

  // ========== 附表6：钢丝绳张力测试记录 ==========
  else if (attNum === 6) {
    h += buildHeader('附表6  钢丝绳张力测试记录', '附表6');
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:7px;">';
    h += '<colgroup>';
    h += '<col style="width:12%">'; // 项目
    for (var f = 1; f <= 8; f++) h += '<col style="width:11%">'; // F1-F8
    h += '</colgroup>';
    // 行1 - 钢丝绳序号
    h += '<tr style="text-align:center;font-weight:bold;background:#f5f5f5;">';
    h += '<td style="border:1px solid #000;padding:1px;">钢丝绳序号</td>';
    for (var f2 = 1; f2 <= 8; f2++) h += '<td style="border:1px solid #000;padding:1px;">F' + f2 + '</td>';
    h += '</tr>';
    // 行2 - 张力值
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">张力值（N）</td>';
    for (var f3 = 0; f3 < 8; f3++) h += '<td style="border:1px solid #000;padding:1px;">N</td>';
    h += '</tr>';
    // 张力平均值 + 公式
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">张力平均值</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;font-size:6.5px;" colspan="8">（最大值-最小值）/张力平均值 = 张力偏差</td>';
    h += '</tr>';
    // 张力偏差计算
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">张力偏差计算</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;" colspan="8">张力值偏差：&nbsp;&nbsp;&nbsp;&nbsp;/&nbsp;&nbsp;&nbsp;&nbsp;=&nbsp;&nbsp;&nbsp;&nbsp;%</td>';
    h += '</tr>';
    // 张力判定
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">张力判定</td>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;" colspan="8">张力偏差计算值：&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;结论：□合格 □不合格</td>';
    h += '</tr>';
    h += '</table>';
    h += '<div style="text-align:right;margin-top:4px;font-size:7px;">— 附表6 —</div>';
    h += '</div>';
  }

  // ========== 附表7：噪声测试记录表 ==========
  else if (attNum === 7) {
    h += buildHeader('附表7  乘客电梯噪声测试记录表&nbsp;&nbsp;单位：dB(A)', '附表7');
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:7px;">';
    h += '<colgroup>';
    h += '<col style="width:18%"><col style="width:12%"><col style="width:10%"><col style="width:10%"><col style="width:10%"><col style="width:20%">';
    h += '</colgroup>';
    // 表头
    h += '<tr style="text-align:center;font-weight:bold;background:#f5f5f5;">';
    h += '<td style="border:1px solid #000;padding:1px;">测量项目</td>';
    h += '<td style="border:1px solid #000;padding:1px;">测量位置</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">测量值</td>';
    h += '<td style="border:1px solid #000;padding:1px;">背景</td>';
    h += '<td style="border:1px solid #000;padding:1px;">修正后</td>';
    h += '</tr>';
    // 开关门过程噪声 - 层站
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="4">开关门过程噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">层站</td>';
    h += '<td style="border:1px solid #000;padding:1px;">开门</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="4">最大值：<br>&nbsp;</td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;">关门</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    // 开关门过程噪声 - 轿厢
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">轿厢</td>';
    h += '<td style="border:1px solid #000;padding:1px;">开门</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;">关门</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    // 运行中轿厢内噪声
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">运行中轿厢内噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;">上行</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">最大值：<br>&nbsp;</td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;">下行</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    // 机房噪声
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="3">机房噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;">1</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="3">平均值：<br>&nbsp;</td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;">2</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;">3</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    // 无机房噪声
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;">无机房噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;">层门处</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">最大值：</td>';
    h += '</tr>';
    h += '</table>';

    // 额定速度对比表
    h += '<div style="margin-top:4px;">';
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:6.5px;">';
    h += '<colgroup>';
    h += '<col style="width:18%"><col style="width:16%"><col style="width:16%"><col style="width:16%"><col style="width:17%"><col style="width:17%">';
    h += '</colgroup>';
    h += '<tr style="text-align:center;font-weight:bold;background:#f5f5f5;">';
    h += '<td style="border:1px solid #000;padding:1px;">额定速度υ</td>';
    h += '<td style="border:1px solid #000;padding:1px;">机房噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;">轿厢内噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;">开关门噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">无机房电梯层门处噪声</td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;">υ≤2.5m/s</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤80dB</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤55dB</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤65dB</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">≤65dB</td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;">2.5m/s＜υ≤6.0m/s</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤85dB</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤60dB</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤65dB</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="2">不超过制造单位的允许值。制造单位未规定的，按照额定速度为2.5m/s及以下和6.0m/s及以下分别加5dB。</td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;">υ＞6.0m/s</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="3">不超过制造单位的允许值。制造单位未规定的，按下表规定加5dB。</td>';
    h += '</tr>';
    h += '</table>';
    h += '</div>';
    h += buildFooter('附表7');
  }

  return h;
}
'''

# 替换函数
new_lines = new_func.split('\n')
# 给每行加换行符
new_lines = [line + '\n' for line in new_lines]

# 替换
lines[start_idx:end_idx+1] = new_lines

# 写回文件
with open(FILE, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"✅ {FILE} 已更新")
print(f"   原函数 {start_idx+1}-{end_idx+1} 行（{end_idx-start_idx+1}行）")
print(f"   新函数 {len(new_lines)} 行")

# 同步到英文文件
import shutil
shutil.copy(FILE, EN_FILE)
print(f"✅ 同步到 {EN_FILE}")
