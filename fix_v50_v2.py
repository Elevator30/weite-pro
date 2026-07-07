#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v50.8 全面返工 v2：
1. 检查表三栏布局 float -> flex 修复
2. 附表1-7 全部按Excel模板结构重做
"""

import shutil

FILE = '威特电梯厂检调试记录单v2.html'
EN_FILE = 'factory-inspection-v2.html'

with open(FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ========== 1. 修复检查表三栏布局 ==========
for i, line in enumerate(lines):
    if 'float:left;width:33.3%;box-sizing:border-box;padding-right:2px;' in line:
        # 外层容器改flex
        lines[i-1] = lines[i-1].replace(
            '<div style="width:100%;overflow:hidden;">',
            '<div style="display:flex;width:100%;gap:4px;">'
        )
        # 三栏去掉float，改用flex
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
        print(f"✅ 修复三栏布局：第{i+1}行附近")
        break

# ========== 2. 提取原函数中的logoBase64 ==========
start_line = 6637  # 0-indexed: 第6638行
# 找到logoBase64行
logo_start = None
logo_end = None
for i in range(start_line, start_line + 100):
    if 'var logoBase64' in lines[i]:
        logo_start = i
        # 找到以 '; 结尾的行
        for j in range(i, i + 600):
            if lines[j].rstrip().endswith("';") or lines[j].rstrip().endswith("';\n"):
                logo_end = j
                break
        break

logo_lines = lines[logo_start:logo_end + 1]
logo_str = ''.join(logo_lines)
print(f"✅ 提取logoBase64：第{logo_start+1}~{logo_end+1}行")

# ========== 3. 构建新的buildSingleAttachHTML函数 ==========
new_func_start = '''function buildSingleAttachHTML(task, dateStr, attNum) {
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
  function esc(s) { if (s == null) return ''; return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

  function buildAttachHeader(title, label) {
    var h = '';
    h += '<div style="position:relative;width:100%;height:100%;padding:10px 15px;box-sizing:border-box;font-family:Arial,sans-serif;font-size:8px;line-height:1.3;">';
    // 顶部：logo + 标题 + 产品编号
    h += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;border-bottom:1px solid #000;padding-bottom:3px;">';
    h += '<img src="' + logoBase64 + '" style="height:18px;width:auto;">';
    h += '<div style="text-align:center;flex:1;font-weight:bold;font-size:11px;">厂检调试记录单</div>';
    h += '<div style="text-align:right;font-size:7px;">产品编号：' + esc(task.productNo || '') + '</div>';
    h += '</div>';
    // 子标题
    h += '<div style="text-align:center;font-weight:bold;font-size:9px;margin-bottom:6px;">' + title + '</div>';
    return h;
  }

  function buildAttachFooter(label) {
    var h = '';
    h += '<div style="position:absolute;bottom:6px;left:0;right:0;text-align:center;font-size:7px;">— ' + label + ' —</div>';
    h += '</div>';
    return h;
  }

  var h = '';

  // ========== 附表1 ==========
  if (attNum === 1) {
    h += buildAttachHeader('附表1  电梯门间隙、门锁啮合长度及地坎间距检验记录', '附表1');
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:7px;text-align:center;">';
    h += '<colgroup>';
    h += '<col style="width:6%"><col style="width:7%"><col style="width:6%"><col style="width:6%">'; // 1-4
    h += '<col style="width:6%"><col style="width:6%"><col style="width:6%"><col style="width:6%"><col style="width:6%">'; // 5-9
    h += '<col style="width:6%"><col style="width:8%"><col style="width:9%"><col style="width:9%">'; // 10-13
    h += '</colgroup>';
    // 表头行1
    h += '<tr style="font-weight:bold;background:#f0f0f0;">';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="3">检验项目<br>编号与内容</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">A1.2.7.1</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="6">A1.2.7.2门间隙</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="3">A1.2.7.8(2)<br>门锁啮合<br>长度</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">A1.2.7.10</td>';
    h += '</tr>';
    // 表头行2
    h += '<tr style="font-weight:bold;background:#f0f0f0;">';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="2">门地坎距离</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="5">A1.2.7.2(1)</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">A1.2.7.2(2)<br>门扇间<br>施力间隙</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">轿门门刀与<br>层门地坎间隙</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">层门门锁滚轮与<br>轿厢地坎间隙</td>';
    h += '</tr>';
    // 表头行3
    h += '<tr style="font-weight:bold;background:#f0f0f0;font-size:6.5px;">';
    h += '<td style="border:1px solid #000;padding:1px;">门扇间<br>间隙</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">门扇与立柱、<br>门楣间隙</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">门扇与<br>地坎间隙</td>';
    h += '</tr>';
    // 判断标准（2行）
    h += '<tr style="font-size:6.5px;background:#fafafa;">';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="2">判断标准</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="2">≤35mm<br>左右偏差<br>小于1/1000</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="5" rowspan="2">乘客电梯：3~6mm<br>载货电梯：3~10mm<br>左右偏差不超过1mm</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">旁开门：≤30<br>中分门：≤45</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">≥7mm</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="2">≥5mm</td>';
    h += '</tr>';
    h += '<tr style="font-size:6.5px;background:#fafafa;"></tr>';
    // 数据行表头
    h += '<tr style="font-weight:bold;background:#f0f0f0;">';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="17">检验位置<br>及测量<br>数据</td>';
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
    // 数据行：轿门1/2 + 15层
    var posList = ['轿门1', '轿门2'];
    for (var fl = 1; fl <= 15; fl++) posList.push(fl + '层');
    for (var pi = 0; pi < posList.length; pi++) {
      h += '<tr>';
      h += '<td style="border:1px solid #000;padding:1px;">' + posList[pi] + '</td>';
      for (var ci = 0; ci < 11; ci++) {
        h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
      }
      h += '</tr>';
    }
    h += '</table>';
    h += buildAttachFooter('附表1');
  }

  // ========== 附表2 ==========
  else if (attNum === 2) {
    h += buildAttachHeader('附表2  缓冲距、顶部空间和底坑空间检测记录', '附表2');
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:7px;text-align:center;">';
    h += '<colgroup>';
    h += '<col style="width:8%"><col style="width:32%">'; // 类别+项目
    h += '<col style="width:6%"><col style="width:6%">'; // 上端站2列
    h += '<col style="width:6%"><col style="width:6%">'; // 压缓冲2列
    h += '<col style="width:6%"><col style="width:6%"><col style="width:6%"><col style="width:8%">'; // 检验结果等
    h += '</colgroup>';
    // 轿厢缓冲距（2行表头+1空行）
    h += '<tr style="font-weight:bold;background:#f0f0f0;">';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="2">轿厢缓冲距</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">mm</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="2">缓冲器压缩行程</td>';
    h += '<td style="border:1px solid #000;padding:1px;">轿厢</td>';
    h += '<td style="border:1px solid #000;padding:1px;">mm</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="2">检验结果</td>';
    h += '</tr>';
    h += '<tr style="font-weight:bold;background:#f0f0f0;">';
    h += '<td style="border:1px solid #000;padding:1px;">对重缓冲距<br>最大允许值</td>';
    h += '<td style="border:1px solid #000;padding:1px;">mm</td>';
    h += '<td style="border:1px solid #000;padding:1px;">对重</td>';
    h += '<td style="border:1px solid #000;padding:1px;">mm</td>';
    h += '</tr>';
    // 轿厢缓冲距数据行
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    for (var bi = 0; bi < 8; bi++) h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    // 井道顶部空间 表头
    h += '<tr style="font-weight:bold;background:#f0f0f0;">';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="6">井道顶部空间</td>';
    h += '<td style="border:1px solid #000;padding:1px;">项  目        状  态</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">上端站平层时</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">对重完全压在缓冲器上时<br>轿门与层门地坎距离</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="4">检验结果</td>';
    h += '</tr>';
    var top5 = [
      '①轿厢导轨进一步制导行程≥0.1+0.035v² (m)',
      '②位于轿厢投影部分的井道顶最低部件的水平面与轿顶最高可站人面积水平面之间的自由垂直距离≥1.0+0.035v (m)',
      '③井道顶最低部件与固定在轿顶部件最高部分之间的自由垂直距离≥0.3+0.035v (m)',
      '④井道顶的最低部件与导靴或滚轮、悬挂装置端接装置附件、垂直滑动门的横梁或部件的最高部分之间的自由垂直距离≥0.1+0.035v² (m)',
      '⑤轿顶空间（≥0.5m×0.6m×0.8m）'
    ];
    for (var ti = 0; ti < 5; ti++) {
      h += '<tr>';
      h += '<td style="border:1px solid #000;padding:1px;text-align:left;font-size:6.5px;">' + top5[ti] + '</td>';
      if (ti < 4) {
        h += '<td style="border:1px solid #000;padding:1px;">m</td>';
        h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
        h += '<td style="border:1px solid #000;padding:1px;">m</td>';
        h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
      } else {
        h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
        h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
      }
      h += '<td style="border:1px solid #000;padding:1px;" colspan="4">&nbsp;</td>';
      h += '</tr>';
    }
    // 底坑空间 表头
    h += '<tr style="font-weight:bold;background:#f0f0f0;">';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="7">底坑空间</td>';
    h += '<td style="border:1px solid #000;padding:1px;">项  目        状  态</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">下端站平层时</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">轿厢完全压在缓冲器上时<br>轿门与层门地坎距离</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="4">检验结果</td>';
    h += '</tr>';
    var pitItems = [
      '①底坑底与轿厢最低部件之间的自由垂直距离≥0.5m',
      '②对重导轨进一步制导行程≥0.1+0.035v² (m)',
      '③-双行',
      '④底坑中固定的最高部件和轿厢的最低部件之间（b除外）的自由垂直距离≥0.3m',
      '⑤轿底空间（≥0.5m×0.6m×1.0m）'
    ];
    // ①
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:left;font-size:6.5px;">' + pitItems[0] + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;">m</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">m</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="4">&nbsp;</td>';
    h += '</tr>';
    // ②
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:left;font-size:6.5px;">' + pitItems[1] + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;">m</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="4">&nbsp;</td>';
    h += '</tr>';
    // ③（双行合并）
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:left;font-size:6.5px;" rowspan="2">③下述水平距离在0.15m之内时，底坑底与轿厢最低部件之间的自由垂直距离≥0.5m</td>';
    h += '<td style="border:1px solid #000;padding:1px;font-size:6.5px;">1)<br>水平&nbsp;&nbsp;&nbsp;&nbsp;m<br>&nbsp;<br>垂直&nbsp;&nbsp;&nbsp;&nbsp;m</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="4" rowspan="2">&nbsp;</td>';
    h += '</tr>';
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;font-size:6.5px;">2)<br>水平&nbsp;&nbsp;&nbsp;&nbsp;m<br>&nbsp;<br>垂直&nbsp;&nbsp;&nbsp;&nbsp;m</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    // ④
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:left;font-size:6.5px;">' + pitItems[3] + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;">m</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="4">&nbsp;</td>';
    h += '</tr>';
    // ⑤
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;text-align:left;font-size:6.5px;">' + pitItems[4] + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="4">&nbsp;</td>';
    h += '</tr>';
    // 备注
    h += '<tr style="font-size:6px;text-align:left;">';
    h += '<td style="border:1px solid #000;padding:1px;text-align:center;vertical-align:top;">备注</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="9">(1)当曳引驱动电梯驱动主机的减速是按照规定被监控时，对于非斜行电梯，0.035可以用按轿厢或者对重触及缓冲器时的速度减小；(2)对于具有补偿绳及补偿绳张紧轮和防跳装置的曳引驱动电梯，0.035v²的值可以用张紧轮可能的移动量再加上轿厢行程的1/500或者二者中较大者</td>';
    h += '</tr>';
    h += '</table>';
    h += buildAttachFooter('附表2');
  }

  // ========== 附表3 ==========
  else if (attNum === 3) {
    h += buildAttachHeader('附表3  导轨工作面铅垂度测量表', '附表3');
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:7px;text-align:center;">';
    h += '<colgroup>';
    h += '<col style="width:5%"><col style="width:9%">';
    for (var mi = 1; mi <= 10; mi++) h += '<col style="width:7%">';
    h += '<col style="width:8%">';
    h += '</colgroup>';
    // 表头
    h += '<tr style="font-weight:bold;background:#f0f0f0;">';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">序&nbsp;&nbsp;&nbsp;&nbsp;号</td>';
    for (var ni = 1; ni <= 10; ni++) h += '<td style="border:1px solid #000;padding:1px;">' + ni + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;">最大偏差</td>';
    h += '</tr>';
    // 4行数据
    var railData = [['轿厢', '左导轨'], ['', '右导轨'], ['对重', '左导轨'], ['', '右导轨']];
    for (var ri = 0; ri < 4; ri++) {
      h += '<tr>';
      if (ri % 2 === 0) {
        h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">' + railData[ri][0] + '</td>';
      }
      h += '<td style="border:1px solid #000;padding:1px;">' + railData[ri][1] + '</td>';
      for (var ci2 = 0; ci2 < 10; ci2++) h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
      h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
      h += '</tr>';
    }
    h += '</table>';
    // 标准说明
    h += '<div style="margin-top:4px;font-size:6.5px;border:1px solid #000;padding:2px;">每列导轨工作面每5m铅垂线测量值间的相对最大偏差，轿厢导轨和设有安全钳的T型对重导轨为1.2mm；不设安全钳的T型对重导轨为2mm。</div>';
    h += buildAttachFooter('附表3');
  }

  // ========== 附表4 ==========
  else if (attNum === 4) {
    h += buildAttachHeader('附表4  导轨顶面距离测量&nbsp;&nbsp;单位（mm）', '附表4');
    // 左右两表并排
    h += '<div style="display:flex;gap:10px;width:100%;">';
    // 左：轿厢
    h += '<div style="flex:1;">';
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:7px;text-align:center;">';
    h += '<colgroup><col style="width:20%"><col style="width:40%"><col style="width:40%"></colgroup>';
    h += '<tr style="font-weight:bold;background:#f0f0f0;">';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="3">轿厢导轨面距基准：&nbsp;&nbsp;&nbsp;&nbsp;mm（0~+2）</td>';
    h += '</tr>';
    // 10个测点分两行显示
    for (var r4 = 0; r4 < 2; r4++) {
      h += '<tr>';
      for (var c4 = 0; c4 < 5; c4++) {
        var n4 = r4 * 5 + c4 + 1;
        h += '<td style="border:1px solid #000;padding:1px;">' + n4 + '</td>';
      }
      h += '</tr>';
      h += '<tr style="height:16px;">';
      for (var c4b = 0; c4b < 5; c4b++) {
        h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
      }
      h += '</tr>';
    }
    // 最大偏差
    h += '<tr style="font-weight:bold;background:#f0f0f0;">';
    h += '<td style="border:1px solid #000;padding:1px;">最大偏差</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '</tr>';
    h += '</table>';
    h += '</div>';
    // 右：对重
    h += '<div style="flex:1;">';
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:7px;text-align:center;">';
    h += '<colgroup><col style="width:20%"><col style="width:40%"><col style="width:40%"></colgroup>';
    h += '<tr style="font-weight:bold;background:#f0f0f0;">';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="3">对重导轨面距基准：&nbsp;&nbsp;&nbsp;&nbsp;mm（0~+3）</td>';
    h += '</tr>';
    for (var r42 = 0; r42 < 2; r42++) {
      h += '<tr>';
      for (var c42 = 0; c42 < 5; c42++) {
        h += '<td style="border:1px solid #000;padding:1px;">' + (r42 * 5 + c42 + 1) + '</td>';
      }
      h += '</tr>';
      h += '<tr style="height:16px;">';
      for (var c43 = 0; c43 < 5; c43++) {
        h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
      }
      h += '</tr>';
    }
    h += '<tr style="font-weight:bold;background:#f0f0f0;">';
    h += '<td style="border:1px solid #000;padding:1px;">最大偏差</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '</tr>';
    h += '</table>';
    h += '</div>';
    h += '</div>';
    h += '<div style="text-align:right;margin-top:6px;font-size:7px;">— 附表4 —</div>';
    h += '</div>'; // 闭合最外层div
  }

  // ========== 附表5 ==========
  else if (attNum === 5) {
    h += buildAttachHeader('附表5  电梯平衡系数检验记录', '附表5');
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:7px;text-align:center;">';
    h += '<colgroup>';
    h += '<col style="width:12%"><col style="width:8%">';
    for (var li = 0; li < 5; li++) h += '<col style="width:8%"><col style="width:8%">';
    h += '</colgroup>';
    // 表头行1
    h += '<tr style="font-weight:bold;background:#f0f0f0;">';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">载重量</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">重量（Kg）<br>额载百分比(%)</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">0.3</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">0.4</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">0.45</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">0.5</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">0.6</td>';
    h += '</tr>';
    // 表头行2
    h += '<tr style="font-weight:bold;background:#f0f0f0;">';
    for (var di = 0; di < 5; di++) {
      h += '<td style="border:1px solid #000;padding:1px;">上行</td>';
      h += '<td style="border:1px solid #000;padding:1px;">下行</td>';
    }
    h += '</tr>';
    // 电流行
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">电&nbsp;流（A）</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    for (var ci5 = 0; ci5 < 10; ci5++) h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    // 测试结果行
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">测试结果</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    for (var ci6 = 0; ci6 < 10; ci6++) h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    // 空行（6行）
    for (var er = 0; er < 6; er++) {
      h += '<tr>';
      h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
      h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
      for (var ci7 = 0; ci7 < 10; ci7++) h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
      h += '</tr>';
    }
    // 平衡系数
    h += '<tr style="font-weight:bold;">';
    h += '<td style="border:1px solid #000;padding:1px;text-align:right;" colspan="2">平衡系数：</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="10">（0.4~0.5）</td>';
    h += '</tr>';
    h += '</table>';

    // 电流曲线SVG
    var loadRatios = [0.3, 0.4, 0.45, 0.5, 0.6];
    var upArr = [], downArr = [];
    try {
      for (var ri = 0; ri < loadRatios.length; ri++) {
        var k = loadRatios[ri].toString();
        var cu = (att5.电流 && att5.电流[k]) ? (parseFloat(att5.电流[k].up) || 0) : 0;
        var cd = (att5.电流 && att5.电流[k]) ? (parseFloat(att5.电流[k].down) || 0) : 0;
        upArr.push(cu);
        downArr.push(cd);
      }
    } catch(e) { upArr = [0,0,0,0,0]; downArr = [0,0,0,0,0]; }

    var svgW = 500, svgH = 170;
    var pad = {l: 36, r: 16, t: 18, b: 28};
    var cw = svgW - pad.l - pad.r;
    var ch = svgH - pad.t - pad.b;
    var maxC = 0;
    for (var uii = 0; uii < upArr.length; uii++) maxC = Math.max(maxC, upArr[uii], downArr[uii]);
    if (maxC < 10) maxC = 50;
    maxC = Math.ceil(maxC / 10) * 10;

    function gx(idx) { return pad.l + (idx / (loadRatios.length - 1)) * cw; }
    function gy(val) { return pad.t + ch - (val / maxC) * ch; }

    var svgStr = '<svg width="' + svgW + '" height="' + svgH + '" style="display:block;margin:6px auto 0;" viewBox="0 0 ' + svgW + ' ' + svgH + '">';
    svgStr += '<text x="' + (svgW/2) + '" y="12" text-anchor="middle" font-size="9" font-weight="bold">电流曲线示意图</text>';
    svgStr += '<line x1="' + pad.l + '" y1="' + pad.t + '" x2="' + pad.l + '" y2="' + (pad.t + ch) + '" stroke="#000" stroke-width="1"/>';
    svgStr += '<line x1="' + pad.l + '" y1="' + (pad.t + ch) + '" x2="' + (pad.l + cw) + '" y2="' + (pad.t + ch) + '" stroke="#000" stroke-width="1"/>';
    // Y刻度
    var ySteps = 5;
    for (var ys = 0; ys <= ySteps; ys++) {
      var yv = maxC * ys / ySteps;
      var yp = gy(yv);
      svgStr += '<line x1="' + (pad.l - 3) + '" y1="' + yp + '" x2="' + pad.l + '" y2="' + yp + '" stroke="#000" stroke-width="1"/>';
      svgStr += '<text x="' + (pad.l - 5) + '" y="' + (yp + 3) + '" text-anchor="end" font-size="6.5">' + Math.round(yv) + '</text>';
      svgStr += '<line x1="' + pad.l + '" y1="' + yp + '" x2="' + (pad.l + cw) + '" y2="' + yp + '" stroke="#ddd" stroke-width="0.5"/>';
    }
    svgStr += '<text x="10" y="' + (pad.t + ch/2) + '" text-anchor="middle" font-size="6.5" transform="rotate(-90,10,' + (pad.t + ch/2) + ')">电流(A)</text>';
    // X刻度
    var xLabels = ['30%', '40%', '45%', '50%', '60%'];
    for (var xi = 0; xi < loadRatios.length; xi++) {
      var xp = gx(xi);
      svgStr += '<line x1="' + xp + '" y1="' + (pad.t + ch) + '" x2="' + xp + '" y2="' + (pad.t + ch + 3) + '" stroke="#000" stroke-width="1"/>';
      svgStr += '<text x="' + xp + '" y="' + (pad.t + ch + 14) + '" text-anchor="middle" font-size="6.5">' + xLabels[xi] + '</text>';
    }
    svgStr += '<text x="' + (svgW/2) + '" y="' + (svgH - 4) + '" text-anchor="middle" font-size="6.5">载荷比</text>';
    // 上行曲线（蓝）
    var hasUp = upArr.some(function(v){ return v > 0; });
    if (hasUp) {
      var upPath = 'M';
      for (var ui = 0; ui < upArr.length; ui++) {
        if (ui > 0) upPath += ' L';
        upPath += gx(ui) + ',' + gy(upArr[ui]);
      }
      svgStr += '<path d="' + upPath + '" fill="none" stroke="#1e88e5" stroke-width="1.5"/>';
      for (var uj = 0; uj < upArr.length; uj++) {
        svgStr += '<circle cx="' + gx(uj) + '" cy="' + gy(upArr[uj]) + '" r="2.5" fill="#1e88e5"/>';
      }
    }
    // 下行曲线（红）
    var hasDown = downArr.some(function(v){ return v > 0; });
    if (hasDown) {
      var dnPath = 'M';
      for (var di2 = 0; di2 < downArr.length; di2++) {
        if (di2 > 0) dnPath += ' L';
        dnPath += gx(di2) + ',' + gy(downArr[di2]);
      }
      svgStr += '<path d="' + dnPath + '" fill="none" stroke="#e53935" stroke-width="1.5"/>';
      for (var dj = 0; dj < downArr.length; dj++) {
        svgStr += '<circle cx="' + gx(dj) + '" cy="' + gy(downArr[dj]) + '" r="2.5" fill="#e53935"/>';
      }
    }
    // 图例
    var ly = pad.t + 4;
    svgStr += '<rect x="' + (svgW - 90) + '" y="' + ly + '" width="10" height="3" fill="#1e88e5"/>';
    svgStr += '<text x="' + (svgW - 77) + '" y="' + (ly + 5) + '" font-size="6.5">—— 上行</text>';
    svgStr += '<rect x="' + (svgW - 90) + '" y="' + (ly + 13) + '" width="10" height="3" fill="#e53935"/>';
    svgStr += '<text x="' + (svgW - 77) + '" y="' + (ly + 18) + '" font-size="6.5">—— 下行</text>';
    svgStr += '</svg>';

    h += svgStr;
    h += buildAttachFooter('附表5');
  }

  // ========== 附表6 ==========
  else if (attNum === 6) {
    h += buildAttachHeader('附表6  钢丝绳张力测试记录', '附表6');
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:7px;text-align:center;">';
    h += '<colgroup>';
    h += '<col style="width:12%">';
    for (var fi = 1; fi <= 8; fi++) h += '<col style="width:11%">';
    h += '</colgroup>';
    // 行1：序号
    h += '<tr style="font-weight:bold;background:#f0f0f0;">';
    h += '<td style="border:1px solid #000;padding:1px;">钢丝绳序号</td>';
    for (var fi2 = 1; fi2 <= 8; fi2++) h += '<td style="border:1px solid #000;padding:1px;">F' + fi2 + '</td>';
    h += '</tr>';
    // 行2：张力值
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">张力值（N）</td>';
    for (var fi3 = 0; fi3 < 8; fi3++) h += '<td style="border:1px solid #000;padding:1px;">N</td>';
    h += '</tr>';
    // 张力平均值 + 公式
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">张力平均值</td>';
    h += '<td style="border:1px solid #000;padding:1px;font-size:6.5px;" colspan="8">（最大值-最小值）/张力平均值 = 张力偏差</td>';
    h += '</tr>';
    // 张力偏差计算
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">张力偏差计算</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="8">张力值偏差：&nbsp;&nbsp;&nbsp;&nbsp;/&nbsp;&nbsp;&nbsp;&nbsp;=&nbsp;&nbsp;&nbsp;&nbsp;%</td>';
    h += '</tr>';
    // 张力判定
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">张力判定</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="8">张力偏差计算值：&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;结论：□合格 □不合格</td>';
    h += '</tr>';
    h += '</table>';
    h += '<div style="text-align:right;margin-top:6px;font-size:7px;">— 附表6 —</div>';
    h += '</div>'; // 闭合最外层div
  }

  // ========== 附表7 ==========
  else if (attNum === 7) {
    h += buildAttachHeader('附表7  乘客电梯噪声测试记录表&nbsp;&nbsp;单位：dB(A)', '附表7');
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:7px;text-align:center;">';
    h += '<colgroup>';
    h += '<col style="width:18%"><col style="width:12%"><col style="width:10%"><col style="width:10%"><col style="width:10%"><col style="width:20%">';
    h += '</colgroup>';
    // 表头
    h += '<tr style="font-weight:bold;background:#f0f0f0;">';
    h += '<td style="border:1px solid #000;padding:1px;">测量项目</td>';
    h += '<td style="border:1px solid #000;padding:1px;">测量位置</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">测量值</td>';
    h += '<td style="border:1px solid #000;padding:1px;">背景</td>';
    h += '<td style="border:1px solid #000;padding:1px;">修正后</td>';
    h += '</tr>';
    // 开关门 - 层站（开+关）
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="4">开关门过程噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">层站</td>';
    h += '<td style="border:1px solid #000;padding:1px;">开门</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="4">最大值：<br>&nbsp;</td>';
    h += '</tr>';
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;">关门</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    // 开关门 - 轿厢
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">轿厢</td>';
    h += '<td style="border:1px solid #000;padding:1px;">开门</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;">关门</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    // 运行中轿厢内噪声
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">运行中轿厢内噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;">上行</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">最大值：<br>&nbsp;</td>';
    h += '</tr>';
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;">下行</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    // 机房噪声
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="3">机房噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;">1</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="3">平均值：<br>&nbsp;</td>';
    h += '</tr>';
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;">2</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;">3</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '</tr>';
    // 无机房噪声
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;">无机房噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;">层门处</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">&nbsp;</td>';
    h += '<td style="border:1px solid #000;padding:1px;">最大值：</td>';
    h += '</tr>';
    h += '</table>';

    // 额定速度对比表
    h += '<div style="margin-top:6px;">';
    h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:6.5px;text-align:center;">';
    h += '<colgroup>';
    h += '<col style="width:18%"><col style="width:16%"><col style="width:16%"><col style="width:16%"><col style="width:17%"><col style="width:17%">';
    h += '</colgroup>';
    h += '<tr style="font-weight:bold;background:#f0f0f0;">';
    h += '<td style="border:1px solid #000;padding:1px;">额定速度υ</td>';
    h += '<td style="border:1px solid #000;padding:1px;">机房噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;">轿厢内噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;">开关门噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">无机房电梯层门处噪声</td>';
    h += '</tr>';
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;">υ≤2.5m/s</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤80dB</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤55dB</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤65dB</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">≤65dB</td>';
    h += '</tr>';
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;">2.5m/s＜υ≤6.0m/s</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤85dB</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤60dB</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤65dB</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2" rowspan="2">不超过制造单位的允许值。制造单位未规定的，按照额定速度为2.5m/s及以下和6.0m/s及以下分别加5dB。</td>';
    h += '</tr>';
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:1px;">υ＞6.0m/s</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="3">不超过制造单位的允许值。制造单位未规定的，按下表规定加5dB。</td>';
    h += '</tr>';
    h += '</table>';
    h += '</div>';
    h += buildAttachFooter('附表7');
  }

  return h;
}
'''

# 执行替换
end_line = 7272  # 0-indexed: 第7273行

new_func_lines = new_func_start.split('\n')
new_func_lines = [line + '\n' for line in new_func_lines]

lines[start_line:end_line + 1] = new_func_lines

with open(FILE, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"✅ 替换buildSingleAttachHTML函数")
print(f"   原函数：{start_line+1}-{end_line+1}行（{end_line-start_line+1}行）")
print(f"   新函数：{len(new_func_lines)}行")

# 同步英文文件
shutil.copy(FILE, EN_FILE)
print(f"✅ 同步到 {EN_FILE}")
