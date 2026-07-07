#!/usr/bin/env python3
"""重写PDF生成相关函数，完全按照纸质版PDF模板格式复刻。"""

import sys

INPUT_FILE = '/app/data/所有对话/主对话/weite-pro-temp/威特电梯厂检调试记录单v2.html'

# Read the file
with open(INPUT_FILE, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
    lines = content.split('\n')

def find_function_bounds(func_name, lines):
    """Find function start and end line indices (0-indexed)"""
    for i, line in enumerate(lines):
        if func_name in line and line.strip().startswith('function '):
            func_start = i
            brace_count = 0
            started = False
            for j in range(i, len(lines)):
                for ch in lines[j]:
                    if ch == '{':
                        brace_count += 1
                        started = True
                    elif ch == '}':
                        brace_count -= 1
                if started and brace_count == 0:
                    return func_start, j
    return None, None

# Find both functions
ci_start, ci_end = find_function_bounds('buildCheckItemsHTML', lines)
sa_start, sa_end = find_function_bounds('buildSingleAttachHTML', lines)

print(f"buildCheckItemsHTML: lines {ci_start+1}-{ci_end+1}")
print(f"buildSingleAttachHTML: lines {sa_start+1}-{sa_end+1}")

if ci_start is None or sa_start is None:
    print("ERROR: Could not find functions")
    sys.exit(1)

# Extract the logoBase64 line from buildCheckItemsHTML
logo_line = None
for i in range(ci_start, ci_start + 20):
    if 'var logoBase64' in lines[i]:
        logo_line = lines[i].strip()
        break

if not logo_line:
    print("ERROR: Could not find logoBase64")
    sys.exit(1)

print(f"Logo line found, length: {len(logo_line)}")

# ============================================================
# 新的 buildCheckItemsHTML 函数
# 三栏独立布局（float:left），水平大类标题
# ============================================================
new_buildCheckItemsHTML = r'''// 检查表主表HTML生成（三栏独立布局，水平大类标题）- 按纸质版PDF格式
function buildCheckItemsHTML(task, project, dateStr, pageNum) {
  // 纸质版PDF布局：每页三栏独立div(float:left)，每栏内多个大类表格
  // 每栏大类结构：水平标题行(背景色) + 序|检查内容|结论 三列表格
  // Page 1: 左栏(A,B,C) 中栏(D,E) 右栏(F,G)
  // Page 2: 左栏(H,I,J) 中栏(K,L,M,N) 右栏(O,P,Q,R)

  ''' + logo_line + '''

  // 构建id到item的映射
  var itemMap = {};
  checkItems.forEach(function(it) { itemMap[it.id] = it; });

  // 每页三栏的大类配置
  var pageConfig;
  if (pageNum === 1) {
    pageConfig = {
      col1: [
        {label: '技术资料与铭牌(可识别标志)的一致性检查', ids: [1,2,3,4,5,6,7,8,9,10,11,12], special: 'techdata'},
        {label: '机器空间及通道', ids: [13,14,15,16,17,18,19,20,21]},
        {label: '机房电气设备与标识', ids: [22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]}
      ],
      col2: [
        {label: '功能检查', ids: (function(){var a=[];for(var i=37;i<=68;i++)a.push(i);return a;})()},
        {label: '安全开关', ids: [69,70,71,72,73,74]}
      ],
      col3: [
        {label: '试验', ids: (function(){var a=[];for(var i=75;i<=99;i++)a.push(i);return a;})()},
        {label: '驱动主机承重及导向', ids: [100,101,102,103,104,105,106,107,108,109,110,111,112]}
      ]
    };
  } else {
    pageConfig = {
      col1: [
        {label: '层门与轿门', ids: (function(){var a=[];for(var i=113;i<=137;i++)a.push(i);return a;})()},
        {label: '导轨及固定支架', ids: [138,139,140,141,142]},
        {label: '悬挂与补偿装置', ids: [143,144,145,146,147,148,149,150,151]}
      ],
      col2: [
        {label: '轿顶设备', ids: (function(){var a=[];for(var i=152;i<=166;i++)a.push(i);return a;})()},
        {label: '轿顶护栏', ids: [167,168,169,170,171]},
        {label: '轿厢与对重', ids: [172,173,174,175,176,177,178,179]},
        {label: '轿底部件', ids: [180,181,182,183,184,185,186,187,188,189,190]}
      ],
      col3: [
        {label: '限速器与夹绳器', ids: [191,192,193,194,195,196,197,198,199]},
        {label: '井道部件及空间', ids: [200,201,202,203,204,205,206,207,208,209,210,211]},
        {label: '底坑设备', ids: [212,213,214,215,216,217,218,219]},
        {label: '感官检查', ids: [220,221,222,223,224,225,226,227,228,229]}
      ]
    };
  }

  // 附表引用标注映射
  var appendixMap = {
    113: '(附表1)', 114: '(附表1)', 115: '(附表1)', 116: '(附表1)', 117: '(附表1)',
    138: '(附表4)', 140: '(附表3)',
    143: '(附表6)',
    76: '(附表5)', 89: '(附表7)',
    209: '(附表2)', 210: '(附表2)', 211: '(附表2)'
  };

  // 生成一栏内的所有大类表格HTML
  function buildColumnHTML(groups) {
    var html = '';
    groups.forEach(function(g) {
      var items = [];
      g.ids.forEach(function(id) {
        if (itemMap[id]) {
          var it = itemMap[id];
          var c = task.checks[id] || {};
          var displayName = getPDFDisplayItemName(it, c);
          if (appendixMap[id]) displayName += appendixMap[id];
          var res = c.s === 'ok' ? '\\u221a' : (c.s === 'ng' ? '\\u00d7' : (c.s === 'na' ? '/' : (c.v || '')));
          items.push({id: id, name: displayName, result: res, note: c.n || ''});
        }
      });

      if (items.length === 0) return;

      // 大类标题行（水平，占满整栏宽度，背景色）
      html += '<table style="width:100%;border-collapse:collapse;font-size:8px;table-layout:fixed;margin-bottom:0;">';
      html += '<tr style="background:#e8e8e8;font-weight:bold;text-align:center;">';
      if (g.special === 'techdata') {
        html += '<td style="border:1px solid #000;padding:2px 3px;" colspan="2">' + escHtml(g.label) + '</td>';
      } else {
        html += '<td style="border:1px solid #000;padding:2px 3px;" colspan="3">' + escHtml(g.label) + '</td>';
      }
      html += '</tr>';

      // 表头行：序|检查内容|结论
      if (g.special === 'techdata') {
        html += '<tr style="background:#f5f5f5;text-align:center;font-weight:bold;">';
        html += '<td style="border:1px solid #000;padding:1px 2px;width:55%;">项目</td>';
        html += '<td style="border:1px solid #000;padding:1px 2px;width:45%;">型号编号/结论</td>';
        html += '</tr>';
      } else {
        html += '<tr style="background:#f5f5f5;text-align:center;font-weight:bold;">';
        html += '<td style="border:1px solid #000;padding:1px 2px;width:12%;">序</td>';
        html += '<td style="border:1px solid #000;padding:1px 2px;width:70%;">检查内容</td>';
        html += '<td style="border:1px solid #000;padding:1px 2px;width:18%;">结论</td>';
        html += '</tr>';
      }

      // 数据行
      items.forEach(function(item) {
        html += '<tr>';
        if (g.special === 'techdata') {
          html += '<td style="border:1px solid #000;padding:1px 2px;">' + escHtml(item.name) + '</td>';
          html += '<td style="border:1px solid #000;padding:1px 2px;text-align:center;">' + item.result + '</td>';
        } else {
          html += '<td style="border:1px solid #000;padding:1px 2px;text-align:center;">' + item.id + '</td>';
          html += '<td style="border:1px solid #000;padding:1px 2px;">' + escHtml(item.name) + (item.note ? '<br><span style="color:red;font-size:7px;">备注:'+escHtml(item.note)+'</span>' : '') + '</td>';
          html += '<td style="border:1px solid #000;padding:1px 2px;text-align:center;">' + item.result + '</td>';
        }
        html += '</tr>';
      });

      html += '</table>';
    });
    return html;
  }

  var h = '<div style="font-family:\\'PingFang SC\\',\\'Heiti SC\\',sans-serif;font-size:8px;position:relative;width:100%;">';
  // 页眉
  h += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">';
  h += '<img src="' + logoBase64 + '" style="height:20px;width:auto;">';
  h += '<span style="font-size:12px;font-weight:bold;">厂检调试记录单</span>';
  h += '<span>产品编号：' + escHtml(task.prodNo||'') + '</span>';
  h += '</div>';

  // 三栏独立布局
  h += '<div style="width:100%;overflow:hidden;">';
  // 左栏
  h += '<div style="float:left;width:33.33%;box-sizing:border-box;padding-right:2px;">';
  h += buildColumnHTML(pageConfig.col1);
  h += '</div>';
  // 中栏
  h += '<div style="float:left;width:33.33%;box-sizing:border-box;padding:0 1px;">';
  h += buildColumnHTML(pageConfig.col2);
  h += '</div>';
  // 右栏
  h += '<div style="float:left;width:33.33%;box-sizing:border-box;padding-left:2px;">';
  h += buildColumnHTML(pageConfig.col3);
  h += '</div>';
  h += '</div>';

  // 清除浮动
  h += '<div style="clear:both;"></div>';

  // 结论说明 + 页脚
  h += '<div style="margin-top:4px;font-size:7px;color:#666;">结论选项：\\u221a符合 \\u00d7不符合 /不适用，或写入测量值。</div>';
  h += '<div style="position:absolute;bottom:0;left:0;right:0;text-align:center;font-size:8px;">— ' + pageNum + ' —</div>';
  h += '</div>';

  return h;
}'''

print("buildCheckItemsHTML function prepared")

# ============================================================
# 新的 buildSingleAttachHTML 函数
# 完全按照纸质版PDF模板格式复刻
# ============================================================
new_buildSingleAttachHTML = r'''// 附表HTML生成（每个附表单独一页A4竖版）- 按纸质版PDF格式复刻
function buildSingleAttachHTML(task, dateStr, attNum) {
  var att1 = task.attachments.attach1 || {cargate:[Array(15).fill(''),Array(15).fill('')], laygate:[]};
  var att2 = task.attachments.attach2 || {};
  var att3 = task.attachments.attach3 || {rows:[], maxDev:{carL:'',carR:'',weightL:'',weightR:''}};
  var att4 = task.attachments.attach4 || {rows:[], maxDev:{car:'',weight:''}, refCar:'', refWeight:''};
  var att5 = task.attachments.attach5 || {载重:'',电压:{},电流:{},平衡系数:''};
  var att6 = task.attachments.attach6 || {};
  var att7 = task.attachments.attach7 || {};

  // 确保数据完整
  if (!att2.顶部空间) att2.顶部空间 = {s1:'',s2:'',s3:'',s4:'',s5:''};
  if (!att2.底坑空间) att2.底坑空间 = {p1:'',p2:'',p3h:'',p3v1:'',p3v2:'',p4:'',p5:''};
  if (!att3.rows || att3.rows.length === 0) att3.rows = [{carL:'',carR:'',weightL:'',weightR:''}];
  if (!att3.maxDev) att3.maxDev = {carL:'',carR:'',weightL:'',weightR:''};
  if (!att4.rows || att4.rows.length === 0) att4.rows = [{car:'',weight:''}];
  if (!att4.maxDev) att4.maxDev = {car:'',weight:''};

  ''' + logo_line + '''

  var h = '<div style="font-family:\\'PingFang SC\\',\\'Heiti SC\\',sans-serif;font-size:9px;position:relative;">';
  // 页眉
  h += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">';
  h += '<img src="' + logoBase64 + '" style="height:20px;width:auto;">';
  h += '<span style="font-size:12px;font-weight:bold;">厂检调试记录单</span>';
  h += '<span>产品编号：' + escHtml(task.prodNo||'') + '</span>';
  h += '</div>';

  // 根据attNum生成对应附表
  if (attNum === 1) {
    // === 附表1: 电梯门间隙、门锁啮合长度及地坎间距检验存在问题记录 ===
    h += '<div style="font-size:10px;font-weight:bold;text-align:center;margin-bottom:4px;">附表1 电梯门间隙、门锁啮合长度及地坎间距检验记录</div>';

    // 主表格 - 多层表头
    h += '<table style="width:100%;border-collapse:collapse;font-size:7.5px;table-layout:fixed;">';

    // 第一层表头：大项
    h += '<tr style="background:#f0f0f0;font-weight:bold;text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;width:6%;" rowspan="3">检验项目<br>编号与内容</td>';
    h += '<td style="border:1px solid #000;padding:1px;width:8%;" rowspan="3">A1.2.7.1<br>门地坎距离</td>';
    h += '<td style="border:1px solid #000;padding:1px;width:24%;" colspan="5">A1.2.7.2 门间隙</td>';
    h += '<td style="border:1px solid #000;padding:1px;width:8%;" rowspan="3">A1.2.7.8(2)<br>门锁啮合长度</td>';
    h += '<td style="border:1px solid #000;padding:1px;width:9%;" rowspan="3">A1.2.7.10<br>轿门门刀与层门地坎间隙</td>';
    h += '<td style="border:1px solid #000;padding:1px;width:9%;" rowspan="3">层门门锁滚轮与轿厢地坎间隙</td>';
    h += '</tr>';

    // 第二层表头
    h += '<tr style="background:#f5f5f5;font-weight:bold;text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="4">A1.2.7.2(1)</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">A1.2.7.2(2)<br>门扇间施力间隙</td>';
    h += '</tr>';

    // 第三层表头
    h += '<tr style="background:#fafafa;font-weight:bold;text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;width:6%;">门扇间间隙</td>';
    h += '<td style="border:1px solid #000;padding:1px;width:6%;" colspan="2">门扇与立柱、门楣间隙</td>';
    h += '<td style="border:1px solid #000;padding:1px;width:6%;">门扇与地坎间隙</td>';
    h += '</tr>';

    // 判断标准行
    h += '<tr style="text-align:center;font-size:7px;">';
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">判断标准</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤35mm<br>左右偏差小于1/1000</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="2">乘客电梯:3-6mm<br>载货电梯:3-10mm<br>左右偏差不超过1mm</td>';
    h += '<td style="border:1px solid #000;padding:1px;">/</td>';
    h += '<td style="border:1px solid #000;padding:1px;">旁开门:<30mm<br>中分门:≤45mm</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≥7mm</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≥5mm</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≥5mm</td>';
    h += '</tr>';

    // 位置行（轿门1、轿门2、各楼层）
    // 构建数据行
    var dataRows = [];
    // 轿门1
    var carDoor1 = {label: '轿门1', isCar: true, idx: 0};
    var carDoor2 = {label: '轿门2', isCar: true, idx: 1};
    dataRows.push(carDoor1);
    dataRows.push(carDoor2);
    // 层门（从laygate获取，最多12层）
    var laygateList = att1.laygate || [];
    for (var li = 0; li < Math.max(laygateList.length, 8); li++) {
      dataRows.push({label: (li+1) + '层', isCar: false, idx: li});
    }

    // 获取数据的辅助函数
    function getAtt1Val(isCar, rowIdx, colIdx) {
      if (isCar) {
        var carArr = att1.cargate && att1.cargate[rowIdx] ? att1.cargate[rowIdx] : [];
        return carArr[colIdx] || '';
      } else {
        if (laygateList[rowIdx] && laygateList[rowIdx].data) {
          return laygateList[rowIdx].data[colIdx] || '';
        }
        return '';
      }
    }

    // 位置标签行
    h += '<tr style="background:#f5f5f5;font-weight:bold;text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;">位置</td>';
    h += '<td style="border:1px solid #000;padding:1px;">左/右</td>';
    h += '<td style="border:1px solid #000;padding:1px;">左</td>';
    h += '<td style="border:1px solid #000;padding:1px;">右</td>';
    h += '<td style="border:1px solid #000;padding:1px;">左</td>';
    h += '<td style="border:1px solid #000;padding:1px;">右</td>';
    h += '<td style="border:1px solid #000;padding:1px;">/</td>';
    h += '<td style="border:1px solid #000;padding:1px;">/</td>';
    h += '<td style="border:1px solid #000;padding:1px;">/</td>';
    h += '<td style="border:1px solid #000;padding:1px;">/</td>';
    h += '</tr>';

    // 数据行
    dataRows.forEach(function(row, ri) {
      var lbl = row.label;
      var isCar = row.isCar;
      var idx = row.idx;
      h += '<tr style="text-align:center;">';
      // 检验位置列（第一列合并显示检验位置及测量数据）
      if (ri === 0) {
        h += '<td style="border:1px solid #000;padding:1px;" rowspan="' + dataRows.length + '">检验位置及测量数据</td>';
      }
      // 位置名称
      h += '<td style="border:1px solid #000;padding:1px;background:#fafafa;">' + escHtml(lbl) + '</td>';
      // 门地坎距离（左）
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(getAtt1Val(isCar, idx, 0)) + '</td>';
      // 门扇间间隙 - 左/右合并显示
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(getAtt1Val(isCar, idx, 1)) + '</td>';
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(getAtt1Val(isCar, idx, 2)) + '</td>';
      // 门扇与立柱门楣间隙 - 左
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(getAtt1Val(isCar, idx, 3)) + '</td>';
      // 门扇与地坎间隙 - 右
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(getAtt1Val(isCar, idx, 4)) + '</td>';
      // 门扇间施力间隙
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(getAtt1Val(isCar, idx, 5)) + '</td>';
      // 门锁啮合长度
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(getAtt1Val(isCar, idx, 6)) + '</td>';
      // 轿门门刀与层门地坎间隙
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(getAtt1Val(isCar, idx, 7)) + '</td>';
      // 层门门锁滚轮与轿厢地坎间隙
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(getAtt1Val(isCar, idx, 8)) + '</td>';
      h += '</tr>';
    });

    h += '</table>';

  } else if (attNum === 2) {
    // === 附表2: 缓冲距、顶部空间和底坑空间检测记录 ===
    h += '<div style="font-size:10px;font-weight:bold;text-align:center;margin-bottom:4px;">附表2 缓冲距、顶部空间和底坑空间检测记录</div>';

    // 顶部基础参数行
    h += '<table style="width:100%;border-collapse:collapse;font-size:8px;table-layout:fixed;margin-bottom:4px;">';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;width:25%;background:#f0f0f0;font-weight:bold;">轿厢缓冲距</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:10%;">' + escHtml(att2.轿厢缓冲距||'') + ' mm</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:25%;background:#f0f0f0;font-weight:bold;">对重缓冲距<br>最大允许值</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:10%;">' + escHtml(att2.对重缓冲距||'') + ' mm</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:15%;background:#f0f0f0;font-weight:bold;">缓冲器压缩行程</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:15%;">轿厢: ' + escHtml(att2.轿厢压缩行程||'') + ' mm<br>对重: ' + escHtml(att2.对重压缩行程||'') + ' mm</td>';
    h += '</tr>';
    h += '</table>';

    // 井道顶部空间检测表
    h += '<div style="font-size:8.5px;font-weight:bold;margin-bottom:2px;">井道顶部空间检测：</div>';
    h += '<table style="width:100%;border-collapse:collapse;font-size:7.5px;table-layout:fixed;margin-bottom:6px;">';
    h += '<tr style="background:#f0f0f0;font-weight:bold;text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;width:6%;" rowspan="6">井道<br>顶部<br>空间</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:8%;">项目</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:6%;">状态</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:15%;">上端站平层时</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:15%;">对重完全压在缓冲器上时</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:10%;">检验结果</td>';
    h += '</tr>';

    var topItems = [
      {key:'s1', label:'①轿厢导轨进一步制导行程≥0.1+0.035v²(m)'},
      {key:'s2', label:'②位于轿厢投影部分的井道顶最低部件的水平面与轿顶最高可站人面积水平面之间的自由垂直距离≥1.0+0.035v(m)'},
      {key:'s3', label:'③井道顶最低部件与固定在轿顶部件最高部分之间的自由垂直距离≥0.3+0.035v(m)'},
      {key:'s4', label:'④井道顶的最低部件与导靴或滚轮、悬挂装置端接装置附件、垂直滑动门的横梁或者部件的最高部分之间的自由垂直距离≥0.1+0.035v²(m)'},
      {key:'s5', label:'⑤轿顶空间 (≥0.5m×0.6m×0.8m)'}
    ];

    topItems.forEach(function(item) {
      h += '<tr>';
      h += '<td style="border:1px solid #000;padding:1px 2px;">' + escHtml(item.label) + '</td>';
      h += '<td style="border:1px solid #000;padding:1px;text-align:center;"></td>';
      h += '<td style="border:1px solid #000;padding:1px;text-align:center;">' + escHtml(att2.顶部空间[item.key]||'') + '</td>';
      h += '<td style="border:1px solid #000;padding:1px;text-align:center;"></td>';
      h += '<td style="border:1px solid #000;padding:1px;text-align:center;"></td>';
      h += '</tr>';
    });
    h += '</table>';

    // 底坑空间检测表
    h += '<div style="font-size:8.5px;font-weight:bold;margin-bottom:2px;">底坑空间检测：</div>';
    h += '<table style="width:100%;border-collapse:collapse;font-size:7.5px;table-layout:fixed;">';
    h += '<tr style="background:#f0f0f0;font-weight:bold;text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;width:6%;" rowspan="6">底坑<br>空间</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:8%;">项目</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:6%;">状态</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:15%;">下端站平层时</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:15%;">轿厢完全压在缓冲器上时</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:10%;">检验结果</td>';
    h += '</tr>';

    var pitItems = [
      {key:'p1', label:'①底坑底与轿厢最低部件之间的自由垂直距离≥0.5m'},
      {key:'p2', label:'②对重导轨进一步制导行程≥0.1+0.035v²(m)'},
      {key:'p3', label:'③水平距离在0.15m之内时，底坑底与轿厢最低部件之间的自由垂直距离≥0.1m'},
      {key:'p4', label:'④底坑中固定的最高部件和轿厢的最低部件之间的自由垂直距离≥0.3m'},
      {key:'p5', label:'⑤轿底空间 (≥0.5m×0.6m×1.0m)'}
    ];

    pitItems.forEach(function(item) {
      h += '<tr>';
      h += '<td style="border:1px solid #000;padding:1px 2px;">' + escHtml(item.label) + '</td>';
      h += '<td style="border:1px solid #000;padding:1px;text-align:center;"></td>';
      h += '<td style="border:1px solid #000;padding:1px;text-align:center;">' + escHtml(att2.底坑空间[item.key]||'') + '</td>';
      h += '<td style="border:1px solid #000;padding:1px;text-align:center;"></td>';
      h += '<td style="border:1px solid #000;padding:1px;text-align:center;"></td>';
      h += '</tr>';
    });
    h += '</table>';

    // 备注
    h += '<div style="margin-top:4px;font-size:7px;color:#666;">备注：(1)当曳引驱动电梯驱动主机的减速是按照规定被监控时，对于非斜行电梯，0.035可以用按轿厢或者对重触及缓冲器时的速度减小来代替；(2)对于具有补偿绳及补偿绳张紧轮和防跳装置的曳引驱动电梯，0.035v²的值可以用张紧轮可能的移动量再加上轿厢行程的1/500或者0.20m(取二者中的较大者)来代替。</div>';

  } else if (attNum === 3) {
    // === 附表3: 导轨工作面铅垂度测量表 ===
    h += '<div style="font-size:10px;font-weight:bold;text-align:center;margin-bottom:4px;">附表3 导轨工作面铅垂度测量表</div>';

    h += '<table style="width:100%;border-collapse:collapse;font-size:8px;table-layout:fixed;">';
    // 表头
    h += '<tr style="background:#f0f0f0;font-weight:bold;text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;width:10%;" colspan="2">序号</td>';
    for (var mi = 1; mi <= 10; mi++) {
      h += '<td style="border:1px solid #000;padding:2px;width:7%;">' + mi + '</td>';
    }
    h += '<td style="border:1px solid #000;padding:2px;width:10%;">最大偏差</td>';
    h += '</tr>';

    // 轿厢左导轨
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;width:5%;" rowspan="2">轿厢</td>';
    h += '<td style="border:1px solid #000;padding:2px;background:#fafafa;">左导轨</td>';
    for (var c3l = 0; c3l < 10; c3l++) {
      var rowL = att3.rows[c3l] || {carL:''};
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(rowL.carL||'') + '</td>';
    }
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">' + escHtml(att3.maxDev.carL||'') + '</td>';
    h += '</tr>';

    // 轿厢右导轨
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;background:#fafafa;">右导轨</td>';
    for (var c3r = 0; c3r < 10; c3r++) {
      var rowR = att3.rows[c3r] || {carR:''};
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(rowR.carR||'') + '</td>';
    }
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">' + escHtml(att3.maxDev.carR||'') + '</td>';
    h += '</tr>';

    // 对重左导轨
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;" rowspan="2">对重</td>';
    h += '<td style="border:1px solid #000;padding:2px;background:#fafafa;">左(前)导轨</td>';
    for (var w3l = 0; w3l < 10; w3l++) {
      var rowWL = att3.rows[w3l] || {weightL:''};
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(rowWL.weightL||'') + '</td>';
    }
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">' + escHtml(att3.maxDev.weightL||'') + '</td>';
    h += '</tr>';

    // 对重右导轨
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;background:#fafafa;">右(后)导轨</td>';
    for (var w3r = 0; w3r < 10; w3r++) {
      var rowWR = att3.rows[w3r] || {weightR:''};
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(rowWR.weightR||'') + '</td>';
    }
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">' + escHtml(att3.maxDev.weightR||'') + '</td>';
    h += '</tr>';

    h += '</table>';

  } else if (attNum === 4) {
    // === 附表4: 导轨顶面距离测量表 ===
    h += '<div style="font-size:10px;font-weight:bold;text-align:center;margin-bottom:4px;">附表4 导轨顶面距离测量表</div>';

    // 左右两个表格并排
    h += '<div style="width:100%;overflow:hidden;">';
    // 左：轿厢导轨面距
    h += '<div style="float:left;width:48%;">';
    h += '<div style="font-size:8px;font-weight:bold;margin-bottom:2px;">轿厢导轨面距：基准 ' + escHtml(att4.refCar||'') + ' mm (0~+2)</div>';
    h += '<table style="width:100%;border-collapse:collapse;font-size:8px;table-layout:fixed;">';
    h += '<tr style="background:#f0f0f0;font-weight:bold;text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;width:15%;">测点</td>';
    for (var c4 = 1; c4 <= 10; c4++) {
      h += '<td style="border:1px solid #000;padding:2px;width:7.5%;">' + c4 + '</td>';
    }
    h += '<td style="border:1px solid #000;padding:2px;width:10%;">最大偏差</td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;background:#fafafa;">数值</td>';
    var att4rows = att4.rows || [];
    for (var c4i = 0; c4i < 10; c4i++) {
      var row4c = att4rows[c4i] || {car:''};
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(row4c.car||'') + '</td>';
    }
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">' + escHtml(att4.maxDev.car||'') + '</td>';
    h += '</tr>';
    h += '</table>';
    h += '</div>';

    // 右：对重导轨面距
    h += '<div style="float:right;width:48%;">';
    h += '<div style="font-size:8px;font-weight:bold;margin-bottom:2px;">对重导轨面距：基准 ' + escHtml(att4.refWeight||'') + ' mm</div>';
    h += '<table style="width:100%;border-collapse:collapse;font-size:8px;table-layout:fixed;">';
    h += '<tr style="background:#f0f0f0;font-weight:bold;text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;width:15%;">测点</td>';
    for (var w4 = 1; w4 <= 10; w4++) {
      h += '<td style="border:1px solid #000;padding:2px;width:7.5%;">' + w4 + '</td>';
    }
    h += '<td style="border:1px solid #000;padding:2px;width:10%;">最大偏差</td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;background:#fafafa;">数值</td>';
    for (var w4i = 0; w4i < 10; w4i++) {
      var row4w = att4rows[w4i] || {weight:''};
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(row4w.weight||'') + '</td>';
    }
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">' + escHtml(att4.maxDev.weight||'') + '</td>';
    h += '</tr>';
    h += '</table>';
    h += '</div>';
    h += '</div>';
    h += '<div style="clear:both;"></div>';

  } else if (attNum === 5) {
    // === 附表5: 电梯平衡系数检验记录 ===
    h += '<div style="font-size:10px;font-weight:bold;text-align:center;margin-bottom:4px;">附表5 电梯平衡系数检验记录</div>';

    // 额定载重
    h += '<div style="font-size:8px;margin-bottom:4px;">额定载重量：' + escHtml(att5.载重||'') + ' Kg</div>';

    h += '<table style="width:100%;border-collapse:collapse;font-size:8px;table-layout:fixed;">';
    // 表头第一层
    h += '<tr style="background:#f0f0f0;font-weight:bold;text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;width:12%;" rowspan="4">重量(Kg)<br>额定载重量的百分比(%)</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:10%;">载重量</td>';
    for (var p5 = 0; p5 < 5; p5++) {
      h += '<td style="border:1px solid #000;padding:2px;width:15.6%;" colspan="2">' + ['30%','40%','45%','50%','60%'][p5] + '</td>';
    }
    h += '</tr>';
    // 电压行
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;background:#fafafa;">电压(V)</td>';
    var volts = att5.电压 || {};
    for (var vi = 0; vi < 5; vi++) {
      var vKey = ['30%','40%','45%','50%','60%'][vi];
      h += '<td style="border:1px solid #000;padding:1px;" colspan="2">' + escHtml(volts[vKey]||'') + '</td>';
    }
    h += '</tr>';
    // 运行方向行
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;background:#fafafa;">运行方向</td>';
    for (var d5 = 0; d5 < 5; d5++) {
      h += '<td style="border:1px solid #000;padding:1px;width:7.8%;">上行</td>';
      h += '<td style="border:1px solid #000;padding:1px;width:7.8%;">下行</td>';
    }
    h += '</tr>';
    // 电流行
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;background:#fafafa;">电流(A)</td>';
    var upCurrents = att5.电流['电流上行'] || ['','','','',''];
    var downCurrents = att5.电流['电流下行'] || ['','','','',''];
    for (var ci5 = 0; ci5 < 5; ci5++) {
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(upCurrents[ci5]||'') + '</td>';
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(downCurrents[ci5]||'') + '</td>';
    }
    h += '</tr>';
    // 备注行 - 平衡系数结果
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:2px;font-weight:bold;">备注</td>';
    h += '<td style="border:1px solid #000;padding:2px;" colspan="11">测试平衡系数：<b>' + escHtml(att5.平衡系数||'') + '</b>（标准:40%-50%）</td>';
    h += '</tr>';
    h += '</table>';

    // 电流曲线示意图区域
    h += '<div style="margin-top:6px;border:1px solid #000;padding:6px;height:130px;position:relative;">';
    h += '<div style="font-size:8px;font-weight:bold;margin-bottom:4px;">电流曲线示意图：</div>';
    h += '<div style="position:relative;width:100%;height:90px;border-left:1px solid #999;border-bottom:1px solid #999;">';
    // X轴标签
    h += '<div style="position:absolute;left:5%;bottom:-16px;font-size:7px;color:#666;">30%</div>';
    h += '<div style="position:absolute;left:25%;bottom:-16px;font-size:7px;color:#666;">40%</div>';
    h += '<div style="position:absolute;left:50%;bottom:-16px;font-size:7px;color:#666;">45%</div>';
    h += '<div style="position:absolute;left:75%;bottom:-16px;font-size:7px;color:#666;">50%</div>';
    h += '<div style="position:absolute;right:2%;bottom:-16px;font-size:7px;color:#666;">60%</div>';
    // 电流
    h += '<div style="position:absolute;left:-30px;top:45%;font-size:7px;color:#666;">电流</div>';
    // 示意曲线（简单表示）
    h += '<svg width="100%" height="100%" style="position:absolute;top:0;left:0;">';
    // 上行曲线（蓝色）
    h += '<polyline points="5%,70% 25%,55% 50%,45% 75%,35% 95%,25%" fill="none" stroke="#3182ce" stroke-width="1.5"/>';
    // 下行曲线（红色）
    h += '<polyline points="5%,30% 25%,40% 50%,50% 75%,60% 95%,70%" fill="none" stroke="#e53e3e" stroke-width="1.5"/>';
    h += '</svg>';
    // 图例
    h += '<div style="position:absolute;top:5px;right:10px;font-size:7px;">';
    h += '<span style="color:#3182ce;">—— 上行</span>&nbsp;&nbsp;';
    h += '<span style="color:#e53e3e;">—— 下行</span>';
    h += '</div>';
    h += '</div>';
    h += '</div>';

  } else if (attNum === 6) {
    // === 附表6: 钢丝绳张力测试记录 ===
    h += '<div style="font-size:10px;font-weight:bold;text-align:center;margin-bottom:4px;">附表6 钢丝绳张力测试记录</div>';

    h += '<table style="width:100%;border-collapse:collapse;font-size:8px;table-layout:fixed;">';
    // 表头
    h += '<tr style="background:#f0f0f0;font-weight:bold;text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;width:12%;">钢丝绳序号</td>';
    for (var f6 = 1; f6 <= 8; f6++) {
      h += '<td style="border:1px solid #000;padding:2px;width:9%;">F' + f6 + '</td>';
    }
    h += '<td style="border:1px solid #000;padding:2px;width:8%;">平均值</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:8%;">张力偏差</td>';
    h += '</tr>';

    // 张力值行
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;background:#fafafa;">张力值(N)</td>';
    for (var fj = 1; fj <= 8; fj++) {
      h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(att6['F'+fj]||'') + '</td>';
    }
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;">' + escHtml(att6.平均值||'') + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;font-weight:bold;color:#dc3545;">' + escHtml(att6.偏差||'') + '</td>';
    h += '</tr>';

    // 张力平均值说明行
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:2px;font-weight:bold;">张力平均值</td>';
    h += '<td style="border:1px solid #000;padding:2px;" colspan="9">(最大值-最小值)/张力平均值=张力偏差</td>';
    h += '</tr>';

    // 张力偏差计算及判定
    h += '<tr>';
    h += '<td style="border:1px solid #000;padding:2px;font-weight:bold;">张力偏差计算及判定</td>';
    h += '<td style="border:1px solid #000;padding:2px;" colspan="9">';
    h += '张力值偏差: <b>' + escHtml(att6.偏差||'') + '</b> % (张力偏差≤5%为合格)<br>';
    h += '张力偏差计算值: ' + escHtml(att6.偏差||'') + ' %<br>';
    h += '结论: ' + (att6.结论 ? '☑合格 ☐不合格' : '☐合格 ☐不合格');
    h += '</td>';
    h += '</tr>';

    h += '</table>';

  } else if (attNum === 7) {
    // === 附表7: 噪声测试 dB(A) ===
    h += '<div style="font-size:10px;font-weight:bold;text-align:center;margin-bottom:4px;">附表7 噪声测试 dB(A)</div>';

    h += '<table style="width:100%;border-collapse:collapse;font-size:8px;table-layout:fixed;">';
    // 表头
    h += '<tr style="background:#f0f0f0;font-weight:bold;text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;width:18%;">测量项目</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:15%;">测量位置</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:15%;">测量值</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:12%;">背景</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:12%;">修正后</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:28%;">备注</td>';
    h += '</tr>';

    // 开关门过程噪声
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;" rowspan="4">开关门过程噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;background:#fafafa;">层站-开门</td>';
    h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(att7.开门层站||'') + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="4">最大值: <b>' + escHtml(att7.开关门最大值||'') + '</b></td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;background:#fafafa;">层站-关门</td>';
    h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(att7.关门层站||'') + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;background:#fafafa;">轿厢-开门</td>';
    h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(att7.开门轿厢||'') + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;background:#fafafa;">轿厢-关门</td>';
    h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(att7.关门轿厢||'') + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '</tr>';

    // 运行中轿厢内噪声
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;" rowspan="2">运行中轿厢内噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;background:#fafafa;">上行</td>';
    h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(att7.上行轿厢||'') + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="2">最大值: <b>' + escHtml(att7.轿厢内最大值||'') + '</b></td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;background:#fafafa;">下行</td>';
    h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(att7.下行轿厢||'') + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '</tr>';

    // 机房噪声
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;" rowspan="3">机房噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;background:#fafafa;">测点1</td>';
    h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(att7.机房1||'') + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="3">平均值: <b>' + escHtml(att7.机房平均值||'') + '</b></td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;background:#fafafa;">测点2</td>';
    h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(att7.机房2||'') + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;background:#fafafa;">测点3</td>';
    h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(att7.机房3||'') + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '</tr>';

    // 无机房噪声
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;">无机房噪声</td>';
    h += '<td style="border:1px solid #000;padding:1px;background:#fafafa;">层门处</td>';
    h += '<td style="border:1px solid #000;padding:1px;">' + escHtml(att7.无机房层门||'') + '</td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '<td style="border:1px solid #000;padding:1px;"></td>';
    h += '<td style="border:1px solid #000;padding:1px;">最大值: <b>' + escHtml(att7.无机房最大值||'') + '</b></td>';
    h += '</tr>';

    h += '</table>';

    // 底部标准参考
    h += '<div style="margin-top:6px;">';
    h += '<table style="width:100%;border-collapse:collapse;font-size:7px;table-layout:fixed;">';
    h += '<tr style="background:#f0f0f0;font-weight:bold;text-align:center;">';
    h += '<td style="border:1px solid #000;padding:2px;width:18%;">额定速度v</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:18%;">机房噪声</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:18%;">轿厢内噪声</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:18%;">开关门噪声</td>';
    h += '<td style="border:1px solid #000;padding:2px;width:28%;">无机房电梯层门处噪声</td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;">v≤2.5m/s</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤80dB</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤55dB</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤65dB</td>';
    h += '<td style="border:1px solid #000;padding:1px;" rowspan="3">不超过制造单位的允许值。制造单位未规定的，按照额定速度为2.5m/s的电梯限值指标判定</td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;">2.5m/s＜v≤6.0m/s</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤85dB</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤60dB</td>';
    h += '<td style="border:1px solid #000;padding:1px;">≤65dB</td>';
    h += '</tr>';
    h += '<tr style="text-align:center;">';
    h += '<td style="border:1px solid #000;padding:1px;">v＞6.0m/s</td>';
    h += '<td style="border:1px solid #000;padding:1px;" colspan="3">不超过制造单位的允许值。制造单位未规定的，按照额定速度为6.0m/s的电梯限值指标判定</td>';
    h += '</tr>';
    h += '</table>';
    h += '</div>';
  }

  // 页脚
  h += '<div style="position:absolute;bottom:0;left:0;right:0;text-align:center;font-size:8px;">— 附表' + attNum + ' —</div>';
  h += '</div>';

  return h;
}'''

print("buildSingleAttachHTML function prepared")

# ============================================================
# 执行替换
# ============================================================

# 注意：buildCheckItemsHTML 在前面（行号小），buildSingleAttachHTML 在后面
# 所以先替换后面的函数，再替换前面的，避免行号偏移

# 先替换 buildSingleAttachHTML（后面的函数）
new_lines = lines[:sa_start] + [new_buildSingleAttachHTML] + lines[sa_end+1:]

# 重新计算 buildCheckItemsHTML 的位置（因为前面替换了后面的函数，前面的行号不变）
# 实际上由于sa_start > ci_end，替换后面的函数不会影响前面函数的行号
# 但为了安全，我们重新基于new_lines计算
lines = new_lines
ci_start2, ci_end2 = find_function_bounds('buildCheckItemsHTML', lines)
print(f"After first replace, buildCheckItemsHTML at lines {ci_start2+1}-{ci_end2+1}")

# 再替换 buildCheckItemsHTML
new_lines = lines[:ci_start2] + [new_buildCheckItemsHTML] + lines[ci_end2+1:]

# Write back
new_content = '\n'.join(new_lines)
with open(INPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\nDone!")
print(f"Original file had {len(lines)} lines")
print(f"New file has {len(new_lines)} lines")
print(f"File size: {len(new_content)} bytes")
'''
