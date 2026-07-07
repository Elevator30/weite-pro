#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v55 记录表全面修复 - 对照Excel/PDF模板
修复内容：
1. 全局连续编号 1-229
2. 竖排标题逐字正向排列（从上往下，每个字都是正的）
3. 完整框线（所有横线竖线，粗细一致）
4. 三栏紧贴无间隙
5. 技术资料分类内容列分两列（项目名 + 编号）
6. 跨行合并项（page1左栏第15、25项各占2行）
7. 显示所有检查项（不过滤hiddenIds）
8. 所有字号一致
"""

import re
import sys

def upgrade_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到函数起始位置
    func_start = content.find('function buildCheckItemsHTML(')
    if func_start == -1:
        print(f"ERROR: function not found in {filepath}")
        return False
    
    # 找到logoBase64的结束位置
    logo_start = content.find("var logoBase64 = '", func_start)
    logo_end = content.find("';", logo_start) + 2
    logo_line = content[logo_start:logo_end]
    
    # 找到函数结束位置（下一个function之前）
    next_func = content.find('\nfunction ', func_start + 100)
    if next_func == -1:
        next_func = content.find('\n</script>', func_start)
    
    # 构建新函数
    new_func = build_new_function(logo_line)
    
    # 替换
    new_content = content[:func_start] + new_func + content[next_func:]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"OK: {filepath} updated")
    return True

def build_new_function(logo_line):
    return '''function buildCheckItemsHTML(task, project, dateStr, pageNum) {
  // v55 SVG底图方案：竖排逐字标题 + 全局连续编号 + 完整框线 + 三栏紧贴 + 技术资料分两列
  var logoBase64 = ''' + logo_line.split("var logoBase64 = '")[1].rsplit("'", 1)[0] + ''';

  function escHtml(s) {
    if (s == null) return '';
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  // id->item映射
  var itemMap = {};
  if (typeof checkItems !== 'undefined') {
    checkItems.forEach(function(it) { itemMap[it.id] = it; });
  }

  // 获取结论显示
  function getResult(id) {
    var val = task.checkResults ? task.checkResults[id] : '';
    if (val === undefined || val === null || val === '') return '';
    if (val === '符合' || val === '√') return '√';
    if (val === '不符合' || val === '×') return '×';
    if (val === '不适用' || val === '/') return '/';
    return val;
  }

  // 配置
  var rowH = 16;          // 数据行行高
  var titleW = 20;        // 竖排标题列宽
  var seqW = 22;          // 序号列宽
  var resultW = 28;       // 结论列宽
  var headerH = 18;       // 表头行高
  var fontSize = 8;       // 正文字号（所有文字统一）
  var strokeW = 0.5;      // 所有框线粗细一致

  // 生成范围ID数组
  function rangeIds(start, end) {
    var a = [];
    for (var i = start; i <= end; i++) a.push(i);
    return a;
  }

  // 竖排文字：逐字正向排列，从上往下
  function verticalText(text, x, y, fontSize, letterSpacing) {
    var chars = String(text).split('');
    var result = '';
    for (var i = 0; i < chars.length; i++) {
      var cy = y + i * letterSpacing;
      result += '<text x="' + x + '" y="' + cy + '" font-size="' + fontSize + '" text-anchor="middle" dominant-baseline="middle" fill="#000">' + escHtml(chars[i]) + '</text>';
    }
    return result;
  }

  // 构建一栏的SVG
  // groups: [{label, ids, rowSpans?, splitContent?}]
  //   splitContent: true 表示内容列分两列（技术资料分类用）
  //   rowSpans: {itemId: span} 跨行合并的项
  // colWidth: 栏总宽度
  function buildColumnSvg(groups, colWidth) {
    var contentW = colWidth - titleW - seqW - resultW;
    var splitRatio = 0.55;  // 技术资料分类：项目名列占55%，编号列占45%

    // 计算总高度和每个分组的信息（考虑跨行合并）
    var totalRows = 0;
    var groupInfo = [];
    for (var g = 0; g < groups.length; g++) {
      var grp = groups[g];
      var ids = grp.ids; // 显示所有项，不过滤
      var rows = 0;
      var itemRows = []; // 每个item的rowSpan
      for (var i = 0; i < ids.length; i++) {
        var span = 1;
        if (grp.rowSpans && grp.rowSpans[ids[i]]) {
          span = grp.rowSpans[ids[i]];
        }
        itemRows.push(span);
        rows += span;
      }
      groupInfo.push({
        label: grp.label,
        ids: ids,
        itemRows: itemRows,
        rows: rows,
        startRow: totalRows,
        splitContent: grp.splitContent || false
      });
      totalRows += rows;
    }

    var totalH = headerH + totalRows * rowH;

    // SVG底图
    var svg = '';
    svg += '<svg width="' + colWidth + '" height="' + totalH + '" xmlns="http://www.w3.org/2000/svg" style="display:block;">';

    // 外框
    svg += '<rect x="0" y="0" width="' + colWidth + '" height="' + totalH + '" fill="#fff" stroke="#000" stroke-width="' + strokeW + '"/>';

    // 竖线：标题列右边界（贯穿全高）
    svg += '<line x1="' + titleW + '" y1="0" x2="' + titleW + '" y2="' + totalH + '" stroke="#000" stroke-width="' + strokeW + '"/>';
    // 竖线：序号列右边界
    svg += '<line x1="' + (titleW + seqW) + '" y1="0" x2="' + (titleW + seqW) + '" y2="' + totalH + '" stroke="#000" stroke-width="' + strokeW + '"/>';
    // 竖线：内容列右边界（结论列左边界）
    var contentRight = titleW + seqW + contentW;
    svg += '<line x1="' + contentRight + '" y1="0" x2="' + contentRight + '" y2="' + totalH + '" stroke="#000" stroke-width="' + strokeW + '"/>';

    // 表头分隔线
    svg += '<line x1="0" y1="' + headerH + '" x2="' + colWidth + '" y2="' + headerH + '" stroke="#000" stroke-width="' + strokeW + '"/>';

    // 表头文字
    svg += '<text x="' + (titleW + seqW / 2) + '" y="' + (headerH / 2) + '" font-size="' + fontSize + '" text-anchor="middle" dominant-baseline="middle" fill="#000">序号</text>';
    svg += '<text x="' + (titleW + seqW + contentW / 2) + '" y="' + (headerH / 2) + '" font-size="' + fontSize + '" text-anchor="middle" dominant-baseline="middle" fill="#000">检查内容</text>';
    svg += '<text x="' + (contentRight + resultW / 2) + '" y="' + (headerH / 2) + '" font-size="' + fontSize + '" text-anchor="middle" dominant-baseline="middle" fill="#000">结论</text>';

    // 画所有数据行的横线
    for (var r = 1; r <= totalRows; r++) {
      var lineY = headerH + r * rowH;
      svg += '<line x1="' + titleW + '" y1="' + lineY + '" x2="' + colWidth + '" y2="' + lineY + '" stroke="#000" stroke-width="' + strokeW + '"/>';
    }

    // 绘制每个分组
    for (var g = 0; g < groups.length; g++) {
      var info = groupInfo[g];
      var groupTop = headerH + info.startRow * rowH;
      var groupH = info.rows * rowH;

      // 分组分隔横线（标题列内的分组边界已经由横线画了）
      // 竖排标题文字（逐字正向）
      var titleCenterX = titleW / 2;
      var titleText = info.label;
      // 计算标题起始y，让文字在标题区域内垂直居中
      var letterSpacing = fontSize + 1; // 字间距
      var totalTextH = titleText.length * letterSpacing;
      var titleStartY = groupTop + (groupH - totalTextH) / 2 + letterSpacing / 2 + fontSize / 3;
      svg += verticalText(titleText, titleCenterX, titleStartY, fontSize, letterSpacing);

      // 技术资料分类：内容列中间加竖线（分两列）
      var splitX = titleW + seqW + contentW * splitRatio;
      if (info.splitContent) {
        svg += '<line x1="' + splitX + '" y1="' + groupTop + '" x2="' + splitX + '" y2="' + (groupTop + groupH) + '" stroke="#000" stroke-width="' + strokeW + '"/>';
      }

      // 绘制每个检查项
      var currentY = groupTop;
      for (var i = 0; i < info.ids.length; i++) {
        var id = info.ids[i];
        var item = itemMap[id] || {name: '?'};
        var span = info.itemRows[i];
        var itemH = span * rowH;

        // 序号（全局连续编号 = item.id）
        var seqY = currentY + itemH / 2;
        svg += '<text x="' + (titleW + seqW / 2) + '" y="' + seqY + '" font-size="' + fontSize + '" text-anchor="middle" dominant-baseline="middle" fill="#000">' + id + '</text>';

        // 检查内容
        var contentText = item.name || '';
        if (info.splitContent) {
          // 技术资料分类：内容分两列，左边是项目名，右边留空填编号
          var nameX = titleW + seqW + 2;
          var nameW = splitX - titleW - seqW - 4;
          svg += '<text x="' + nameX + '" y="' + seqY + '" font-size="' + fontSize + '" text-anchor="start" dominant-baseline="middle" fill="#000">' + escHtml(contentText) + '</text>';
          // 右边编号列留空，不填文字
        } else {
          // 普通分类：内容占满整列
          var contX = titleW + seqW + 2;
          var contW = contentW - 4;
          // 简单文本（单行）
          svg += '<text x="' + contX + '" y="' + seqY + '" font-size="' + fontSize + '" text-anchor="start" dominant-baseline="middle" fill="#000">' + escHtml(contentText) + '</text>';
        }

        // 结论
        var resultVal = getResult(id);
        if (resultVal) {
          svg += '<text x="' + (contentRight + resultW / 2) + '" y="' + seqY + '" font-size="' + fontSize + '" text-anchor="middle" dominant-baseline="middle" fill="#000">' + resultVal + '</text>';
        }

        currentY += itemH;
      }
    }

    svg += '</svg>';
    return svg;
  }

  // 页面配置
  var pageConfig;
  if (pageNum === 1) {
    pageConfig = {
      col1: [
        {label: '技术资料与铭牌(可识别标志)的一致性检查', ids: rangeIds(1,12), splitContent: true},
        {label: '机器空间及通道', ids: rangeIds(13,21), rowSpans: {15: 2}},
        {label: '机房电气设备与标识', ids: rangeIds(22,36), rowSpans: {25: 2}}
      ],
      col2: [
        {label: '功能检查', ids: rangeIds(37,68)},
        {label: '安全开关', ids: rangeIds(69,74)}
      ],
      col3: [
        {label: '试验', ids: rangeIds(75,99)},
        {label: '驱动主机、承重及导向', ids: rangeIds(100,112)}
      ]
    };
  } else {
    pageConfig = {
      col1: [
        {label: '层门与轿门', ids: rangeIds(113,137)},
        {label: '导轨及固定支架', ids: rangeIds(138,142)},
        {label: '悬挂与补偿装置', ids: rangeIds(143,151)}
      ],
      col2: [
        {label: '轿顶设备', ids: rangeIds(152,166)},
        {label: '轿顶护栏', ids: rangeIds(167,171)},
        {label: '轿厢与对重', ids: rangeIds(172,179)},
        {label: '轿底部件', ids: rangeIds(180,190)}
      ],
      col3: [
        {label: '限速器与夹绳器', ids: rangeIds(191,199)},
        {label: '井道部件及空间', ids: rangeIds(200,211)},
        {label: '底坑设备', ids: rangeIds(212,219)},
        {label: '感官检查', ids: rangeIds(220,229)}
      ]
    };
  }

  // 每栏宽度
  var colWidth = 250;

  // 构建页面
  var h = '';
  h += '<div style="font-family:Arial,sans-serif;font-size:9px;position:relative;padding:8px;box-sizing:border-box;width:100%;">';

  // 页眉
  h += '<div style="position:relative;margin-bottom:6px;padding-bottom:4px;border-bottom:1px solid #000;overflow:hidden;">';
  h += '<div style="float:left;width:20%;"><img src="' + logoBase64 + '" style="height:22px;width:auto;"></div>';
  h += '<div style="float:left;width:60%;text-align:center;font-size:14px;font-weight:bold;line-height:22px;">厂检调试记录单</div>';
  h += '<div style="float:right;width:20%;text-align:right;font-size:9px;line-height:22px;">产品编号：' + escHtml(task.prodNo || task.productNo || '') + '</div>';
  h += '</div>';

  // 三栏布局 - 紧贴无间隙
  h += '<div style="overflow:hidden;">';
  h += '<div style="float:left;width:33.33%;box-sizing:border-box;">' + buildColumnSvg(pageConfig.col1, colWidth) + '</div>';
  h += '<div style="float:left;width:33.33%;box-sizing:border-box;">' + buildColumnSvg(pageConfig.col2, colWidth) + '</div>';
  h += '<div style="float:left;width:33.34%;box-sizing:border-box;">' + buildColumnSvg(pageConfig.col3, colWidth) + '</div>';
  h += '</div>';

  // 结论说明
  h += '<div style="margin-top:6px;font-size:7px;color:#333;">结论选项中，符合打"√"，不符合打"×"，不适用打"/"，或写入测量值。</div>';

  // 页码
  h += '<div style="text-align:center;font-size:8px;margin-top:4px;">— ' + pageNum + ' —</div>';

  h += '</div>';

  return h;
}
'''

if __name__ == '__main__':
    base = '/app/data/所有对话/主对话/weite-pro-temp/'
    ok1 = upgrade_file(base + '威特电梯厂检调试记录单v2.html')
    ok2 = upgrade_file(base + 'factory-inspection-v2.html')
    if ok1 and ok2:
        print("All files upgraded successfully!")
    else:
        print("Some files failed!")
        sys.exit(1)
