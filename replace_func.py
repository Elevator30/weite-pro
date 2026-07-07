#!/usr/bin/env python3
"""Replace buildCheckItemsHTML function with new layout matching paper-PDF-style layout."""

import sys

INPUT_FILE = '/app/data/所有对话/主对话/weite-pro-temp/威特电梯厂检调试记录单v2.html'

# Read the file
with open(INPUT_FILE, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
    lines = content.split('\n')

# Find the function start line (0-indexed)
func_start = None
func_end = None

for i, line in enumerate(lines):
    if line.strip() == 'function buildCheckItemsHTML(task, project, dateStr, pageNum) {':
        func_start = i
        # Find the matching closing brace
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
                func_end = j
                break
        break

print(f"Function found at lines {func_start+1}-{func_end+1}")
if func_start is None or func_end is None:
    print("ERROR: Could not find function")
    sys.exit(1)

# Extract the logoBase64 line
logo_line = None
for i in range(func_start, func_start + 20):
    if 'var logoBase64' in lines[i]:
        logo_line = lines[i]
        break

if not logo_line:
    print("ERROR: Could not find logoBase64")
    sys.exit(1)

print(f"Logo line found, length: {len(logo_line)}")

# Now build the new function
# The layout: single table with 3 column groups, each group has: 大类(竖排) | 序 | 检查内容 | 结论
# Page 1: col1(A,B,C) col2(D,E) col3(F,G)
# Page 2: col1(H,I,J) col2(K,L,M,N) col3(O,P,Q,R)

new_func = '''// 检查项三列HTML生成（pageNum=1或2，按纸质版PDF布局）
function buildCheckItemsHTML(task, project, dateStr, pageNum) {
  // 纸质版PDF布局：每页三栏，每栏结构：大类(竖排标题) + 序 + 检查内容 + 结论
  // Page 1: A.技术资料与铭牌 B.机器空间及通道 C.机房电气设备与标识 | D.功能检查 E.安全开关 | F.试验 G.驱动主机承重及导向
  // Page 2: H.层门与轿门 I.导轨及固定支架 J.悬挂与补偿装置 | K.轿顶设备 L.轿顶护栏 M.轿厢与对重 N.轿底部件 | O.限速器与夹绳器 P.井道部件及空间 Q.底坑设备 R.感官检查

  ''' + logo_line + '''

  // 构建id到item的映射
  var itemMap = {};
  checkItems.forEach(function(it) { itemMap[it.id] = it; });

  // 每页三列的大类配置
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

  // 构建每列的扁平化item列表（带大类信息）
  function buildColItems(groups) {
    var items = [];
    var groupRanges = []; // {startIdx, count, label, special}
    var idx = 0;
    groups.forEach(function(g) {
      var start = idx;
      var cnt = 0;
      g.ids.forEach(function(id) {
        if (itemMap[id]) {
          var it = itemMap[id];
          var c = task.checks[id] || {};
          var displayName = getPDFDisplayItemName(it, c);
          if (appendixMap[id]) displayName += appendixMap[id];
          var res = c.s === 'ok' ? '\\u221a' : (c.s === 'ng' ? '\\u00d7' : (c.s === 'na' ? '/' : (c.v || '')));
          items.push({id: id, name: displayName, result: res, note: c.n || ''});
          idx++;
          cnt++;
        }
      });
      if (cnt > 0) {
        groupRanges.push({startIdx: start, count: cnt, label: g.label, special: g.special || ''});
      }
    });
    return {items: items, groups: groupRanges, total: idx};
  }

  var col1 = buildColItems(pageConfig.col1);
  var col2 = buildColItems(pageConfig.col2);
  var col3 = buildColItems(pageConfig.col3);
  var maxRows = Math.max(col1.total, col2.total, col3.total);

  // 查找某行在某列中所属的大类及相对位置
  function findGroup(colData, rowIdx) {
    for (var gi = 0; gi < colData.groups.length; gi++) {
      var g = colData.groups[gi];
      if (rowIdx >= g.startIdx && rowIdx < g.startIdx + g.count) {
        return {group: g, relIdx: rowIdx - g.startIdx, isFirst: rowIdx === g.startIdx, remain: g.count - (rowIdx - g.startIdx)};
      }
    }
    return null;
  }

  var h = '<div style="font-family:\\'PingFang SC\\',\\'Heiti SC\\',sans-serif;font-size:8px;position:relative;">';
  // 页眉
  h += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">';
  h += '<img src="' + logoBase64 + '" style="height:20px;width:auto;">';
  h += '<span style="font-size:12px;font-weight:bold;">厂检调试记录单</span>';
  h += '<span>产品编号：' + escHtml(task.prodNo||'') + '</span>';
  h += '</div>';

  // 主表：12列 = 3组 x (大类|序|检查内容|结论)
  h += '<table style="width:100%;border-collapse:collapse;font-size:8px;table-layout:fixed;">';

  // 表头行
  h += '<tr style="background:#f0f0f0;font-weight:bold;text-align:center;">';
  for (var ci = 0; ci < 3; ci++) {
    h += '<td style="border:1px solid #000;padding:1px 2px;width:3%;">大类</td>';
    h += '<td style="border:1px solid #000;padding:1px 2px;width:3%;">序</td>';
    h += '<td style="border:1px solid #000;padding:1px 2px;width:24%;">检查内容</td>';
    h += '<td style="border:1px solid #000;padding:1px 2px;width:4%;">结论</td>';
  }
  h += '</tr>';

  // 数据行
  for (var rowIdx = 0; rowIdx < maxRows; rowIdx++) {
    h += '<tr>';

    var colsData = [col1, col2, col3];
    for (var ci = 0; ci < 3; ci++) {
      var colData = colsData[ci];
      var info = findGroup(colData, rowIdx);

      if (rowIdx < colData.items.length) {
        var item = colData.items[rowIdx];
        var grp = info.group;

        // 大类列（竖排，仅在大类第一行输出，rowspan覆盖整组）
        if (info.isFirst) {
          h += '<td style="border:1px solid #000;padding:1px 2px;text-align:center;writing-mode:vertical-lr;letter-spacing:1px;font-weight:bold;background:#f5f5f5;" rowspan="' + info.remain + '">' + escHtml(grp.label) + '</td>';
        }

        // 序号列
        h += '<td style="border:1px solid #000;padding:1px 2px;text-align:center;">' + item.id + '</td>';

        // 检查内容列
        if (grp.special === 'techdata') {
          // 技术资料特殊两列布局：项目名 | 型号编号
          h += '<td style="border:1px solid #000;padding:1px 2px;">';
          h += '<table style="width:100%;border-collapse:collapse;font-size:7px;table-layout:fixed;"><tr>';
          h += '<td style="border-right:1px solid #999;padding:1px 2px;width:62%;">' + escHtml(item.name) + '</td>';
          h += '<td style="padding:1px 2px;width:38%;"></td>';
          h += '</tr></table>';
          h += '</td>';
        } else {
          h += '<td style="border:1px solid #000;padding:1px 2px;">' + escHtml(item.name) + (item.note ? '<br><span style="color:red;font-size:7px;">备注:'+escHtml(item.note)+'</span>' : '') + '</td>';
        }

        // 结论列
        h += '<td style="border:1px solid #000;padding:1px 2px;text-align:center;">' + item.result + '</td>';
      } else {
        // 空行（该列已无数据）
        h += '<td style="border:1px solid #000;padding:1px;"></td>';
        h += '<td style="border:1px solid #000;padding:1px;"></td>';
        h += '<td style="border:1px solid #000;padding:1px;"></td>';
        h += '<td style="border:1px solid #000;padding:1px;"></td>';
      }
    }

    h += '</tr>';
  }

  h += '</table>';

  // 结论说明 + 页脚
  h += '<div style="margin-top:2px;font-size:7px;color:#666;">结论选项：\\u221a符合 \\u00d7不符合 /不适用，或写入测量值。</div>';
  h += '<div style="position:absolute;bottom:0;left:0;right:0;text-align:center;font-size:8px;">— ' + pageNum + ' —</div>';
  h += '</div>';

  return h;
}'''

# Now replace the function in the file
new_lines = lines[:func_start] + [new_func] + lines[func_end+1:]
new_content = '\n'.join(new_lines)

with open(INPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Done. Replaced function at lines {func_start+1}-{func_end+1}")
print(f"Original lines: {len(lines)}, New lines: {len(new_lines)}")
