#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v56 全面修复：
1. 三栏合并为单个SVG（彻底解决空隙和边框重复）
2. 标题列内分组之间加横线分隔
3. 跨行合并单元格中间不画横线
4. 长文本自动换行（SVG tspan 多行）
5. 所有检查项名称加上附表标注（13项）
6. 全局连续编号1-229、竖排逐字、框线同粗、字号一致、技术资料分两列
"""

import re
import os

FILE_PATH = '/app/data/所有对话/主对话/weite-pro-temp/威特电梯厂检调试记录单v2.html'

# 附表标注映射（id → 附表标注）
ATTACH_MAP = {
    76: '(附表5)',
    89: '(附表7)',
    113: '(附表1)',
    114: '(附表1)',
    115: '(附表1)',
    116: '(附表1)',
    117: '(附表1)',
    138: '(附表4)',
    140: '(附表3)',
    143: '(附表6)',
    209: '(附表2)',
    211: '(附表2)',
}

def add_attach_labels(content):
    """给检查项名称加上附表标注"""
    def replace_item(match):
        id_str = match.group(1)
        category = match.group(2)
        name = match.group(3)
        item_id = int(id_str)
        if item_id in ATTACH_MAP and ATTACH_MAP[item_id] not in name:
            new_name = name + ATTACH_MAP[item_id]
            return "{" + f"id:{id_str},category:'{category}',name:'{new_name}'"
        return match.group(0)
    
    # 匹配格式: {id:123,category:'xxx',name:'yyy'
    pattern = r"\{id:(\d+),category:'([^']+)',name:'([^']+)'"
    return re.sub(pattern, replace_item, content)


def build_new_buildCheckItemsHTML():
    """生成全新的buildCheckItemsHTML函数 - 单SVG三栏布局"""
    
    new_func = '''function buildCheckItemsHTML(task, project, dateStr, pageNum) {
  // ========== 配置参数 ==========
  var rowH = 15;         // 数据行行高
  var titleW = 18;       // 竖排标题列宽
  var seqW = 20;         // 序号列宽
  var resultW = 26;      // 结论列宽
  var headerH = 17;      // 表头行高
  var fontSize = 8;      // 统一字号
  var strokeW = 0.5;     // 统一框线粗细
  var colGap = 0;        // 栏间距（0=紧贴）
  var splitRatio = 0.55; // 技术资料分类内容列分割比例

  // 页面配置（两页三栏）
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

  // ========== 辅助函数 ==========
  // id->item映射
  var itemMap = {};
  if (typeof checkItems !== 'undefined') {
    checkItems.forEach(function(it) { itemMap[it.id] = it; });
  }

  function escHtml(s) {
    if (!s) return '';
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function getResult(id) {
    var c = task.checks && task.checks[id];
    if (!c) return '';
    if (c.s === 'ok') return '√';
    if (c.s === 'ng') return '×';
    if (c.s === 'na') return '/';
    if (c.v !== undefined && c.v !== '') return escHtml(c.v);
    return '';
  }

  function rangeIds(start, end) {
    var arr = [];
    for (var i = start; i <= end; i++) arr.push(i);
    return arr;
  }

  // 竖排逐字文字（每个字都是正的，从上往下排）
  function verticalText(text, x, startY, fs, spacing) {
    var svg = '';
    for (var i = 0; i < text.length; i++) {
      var ch = text.charAt(i);
      svg += '<text x="' + x + '" y="' + (startY + i * spacing) + '" font-size="' + fs + '" text-anchor="middle" dominant-baseline="middle" fill="#000">' + escHtml(ch) + '</text>';
    }
    return svg;
  }

  // 计算文本按宽度拆分成几行（粗略按字符数估算）
  function wrapText(text, maxWidth, fs) {
    if (!text) return [''];
    var chars = text.split('');
    var lines = [];
    var current = '';
    var charW = fs * 0.9; // 每个字符大概宽度
    for (var i = 0; i < chars.length; i++) {
      var ch = chars[i];
      var testLine = current + ch;
      if (testLine.length * charW > maxWidth && current.length > 0) {
        lines.push(current);
        current = ch;
      } else {
        current = testLine;
      }
    }
    if (current) lines.push(current);
    return lines;
  }

  function getItemName(item) {
    var name = item.name || '';
    // 第23项特殊处理
    if (item.id === 23) {
      var c = task.checks && task.checks[23];
      if (c) {
        if (c.powerType === 'formal') {
          name = name.replace('□正式电', '☑正式电').replace('□临时电', '☐临时电');
        } else if (c.powerType === 'temp') {
          name = name.replace('□正式电', '☐正式电').replace('□临时电', '☑临时电');
        }
        if (c.v) name = name.replace('___V', c.v + 'V');
      }
    }
    return name;
  }

  // ========== 计算每栏的行布局 ==========
  function calcColLayout(groups) {
    var totalRows = 0;
    var groupInfo = [];
    for (var g = 0; g < groups.length; g++) {
      var grp = groups[g];
      var ids = grp.ids;
      var rows = 0;
      var itemRows = [];
      var itemYoffsets = []; // 每个item的起始行偏移
      for (var i = 0; i < ids.length; i++) {
        var span = 1;
        if (grp.rowSpans && grp.rowSpans[ids[i]]) {
          span = grp.rowSpans[ids[i]];
        }
        itemRows.push(span);
        itemYoffsets.push(rows);
        rows += span;
      }
      groupInfo.push({
        label: grp.label,
        ids: ids,
        itemRows: itemRows,
        itemYoffsets: itemYoffsets,
        rows: rows,
        startRow: totalRows,
        splitContent: grp.splitContent || false,
        rowSpans: grp.rowSpans || {}
      });
      totalRows += rows;
    }
    return { groups: groupInfo, totalRows: totalRows };
  }

  // ========== 渲染一栏 ==========
  function renderColumn(svg, groups, colX, colW, layout) {
    var contentW = colW - titleW - seqW - resultW;
    var splitX = colX + titleW + seqW + contentW * splitRatio;
    var totalH = headerH + layout.totalRows * rowH;

    // 外框（左、右、底）
    svg += '<rect x="' + colX + '" y="0" width="' + colW + '" height="' + totalH + '" fill="none" stroke="#000" stroke-width="' + strokeW + '"/>';

    // 竖线：标题列右边界
    svg += '<line x1="' + (colX + titleW) + '" y1="0" x2="' + (colX + titleW) + '" y2="' + totalH + '" stroke="#000" stroke-width="' + strokeW + '"/>';
    // 竖线：序号列右边界
    svg += '<line x1="' + (colX + titleW + seqW) + '" y1="0" x2="' + (colX + titleW + seqW) + '" y2="' + totalH + '" stroke="#000" stroke-width="' + strokeW + '"/>';
    // 竖线：内容列右边界（结论列左边界）
    var contentRight = colX + titleW + seqW + contentW;
    svg += '<line x1="' + contentRight + '" y1="0" x2="' + contentRight + '" y2="' + totalH + '" stroke="#000" stroke-width="' + strokeW + '"/>';

    // 表头分隔线
    svg += '<line x1="' + colX + '" y1="' + headerH + '" x2="' + (colX + colW) + '" y2="' + headerH + '" stroke="#000" stroke-width="' + strokeW + '"/>';

    // 表头文字
    var headerY = headerH / 2 + 3;
    svg += '<text x="' + (colX + titleW + seqW / 2) + '" y="' + headerY + '" font-size="' + fontSize + '" text-anchor="middle" dominant-baseline="middle" fill="#000">序号</text>';
    svg += '<text x="' + (colX + titleW + seqW + contentW / 2) + '" y="' + headerY + '" font-size="' + fontSize + '" text-anchor="middle" dominant-baseline="middle" fill="#000">检查内容</text>';
    svg += '<text x="' + (contentRight + resultW / 2) + '" y="' + headerY + '" font-size="' + fontSize + '" text-anchor="middle" dominant-baseline="middle" fill="#000">结论</text>';

    // 绘制每个分组
    for (var g = 0; g < layout.groups.length; g++) {
      var info = layout.groups[g];
      var groupTop = headerH + info.startRow * rowH;
      var groupH = info.rows * rowH;

      // 分组底部分隔线（标题列内的分组分隔）
      if (g < layout.groups.length - 1) {
        var groupBottomY = groupTop + groupH;
        svg += '<line x1="' + colX + '" y1="' + groupBottomY + '" x2="' + (colX + titleW) + '" y2="' + groupBottomY + '" stroke="#000" stroke-width="' + strokeW + '"/>';
      }

      // 竖排标题文字（逐字正向）
      var titleCenterX = colX + titleW / 2;
      var letterSpacing = fontSize + 1.5;
      var totalTextH = info.label.length * letterSpacing;
      var titleStartY = groupTop + (groupH - totalTextH) / 2 + letterSpacing / 2 + fontSize / 3;
      svg += verticalText(info.label, titleCenterX, titleStartY, fontSize, letterSpacing);

      // 技术资料分类：内容列中间加竖线（分两列）
      if (info.splitContent) {
        svg += '<line x1="' + splitX + '" y1="' + groupTop + '" x2="' + splitX + '" y2="' + (groupTop + groupH) + '" stroke="#000" stroke-width="' + strokeW + '"/>';
      }

      // 数据行横线 + 每个检查项内容
      for (var i = 0; i < info.ids.length; i++) {
        var id = info.ids[i];
        var item = itemMap[id] || {name: '?'};
        var span = info.itemRows[i];
        var itemH = span * rowH;
        var itemTop = groupTop + info.itemYoffsets[i] * rowH;
        var itemMidY = itemTop + itemH / 2;

        // 横线：每个item底部画一条（标题列不画，标题列的分隔由分组分隔线处理）
        // 最后一项底部与外框底重叠，也画上（不影响）
        var lineY = itemTop + itemH;
        svg += '<line x1="' + (colX + titleW) + '" y1="' + lineY + '" x2="' + (colX + colW) + '" y2="' + lineY + '" stroke="#000" stroke-width="' + strokeW + '"/>';

        // 序号
        svg += '<text x="' + (colX + titleW + seqW / 2) + '" y="' + itemMidY + '" font-size="' + fontSize + '" text-anchor="middle" dominant-baseline="middle" fill="#000">' + id + '</text>';

        // 检查内容（支持多行换行）
        var itemName = getItemName(item);
        var contX = colX + titleW + seqW + 2;
        var contW = contentW - 4;
        if (info.splitContent) {
          // 技术资料分两列：左边项目名，右边留空填编号
          contW = splitX - colX - titleW - seqW - 4;
        }

        var lines = wrapText(itemName, contW, fontSize);
        var lineHeight = fontSize + 1.5;
        var totalTextHeight = lines.length * lineHeight;
        var textStartY = itemMidY - totalTextHeight / 2 + lineHeight / 2;

        for (var li = 0; li < lines.length; li++) {
          svg += '<text x="' + contX + '" y="' + (textStartY + li * lineHeight) + '" font-size="' + fontSize + '" text-anchor="start" dominant-baseline="middle" fill="#000">' + escHtml(lines[li]) + '</text>';
        }

        // 结论
        var resultVal = getResult(id);
        if (resultVal) {
          svg += '<text x="' + (contentRight + resultW / 2) + '" y="' + itemMidY + '" font-size="' + fontSize + '" text-anchor="middle" dominant-baseline="middle" fill="#000">' + resultVal + '</text>';
        }
      }
    }
  }

  // ========== 构建SVG ==========
  var layout1 = calcColLayout(pageConfig.col1);
  var layout2 = calcColLayout(pageConfig.col2);
  var layout3 = calcColLayout(pageConfig.col3);

  // 以最高的栏为基准
  var maxRows = Math.max(layout1.totalRows, layout2.totalRows, layout3.totalRows);
  var totalH = headerH + maxRows * rowH;

  // 每栏宽度：均分
  var totalW = 750; // A4横版内宽约750px
  var colW = Math.floor((totalW - 2 * colGap) / 3);
  var col2X = colW + colGap;
  var col3X = 2 * (colW + colGap);

  var svg = '';
  svg += '<svg width="' + totalW + '" height="' + (totalH + 40) + '" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:auto;">';

  // 渲染三栏
  renderColumn(svg, pageConfig.col1, 0, colW, layout1);
  renderColumn(svg, pageConfig.col2, col2X, colW, layout2);
  renderColumn(svg, pageConfig.col3, col3X, colW, layout3);

  svg += '</svg>';

  // ========== 组装HTML ==========
  var projName = (project && project.name) || (task && task.projectName) || '';
  var logoBase64 = 'REPLACE_LOGO_BASE64';

  var html = '';
  html += '<div style="font-family:Arial,sans-serif;font-size:' + fontSize + 'px;position:relative;padding:4px;box-sizing:border-box;width:100%;">';

  // 页眉
  html += '<div style="position:relative;margin-bottom:4px;padding-bottom:3px;border-bottom:1px solid #000;overflow:hidden;">';
  html += '<div style="float:left;width:20%;"><img src="' + logoBase64 + '" style="height:20px;width:auto;"/></div>';
  html += '<div style="float:left;width:60%;text-align:center;font-size:13px;font-weight:bold;line-height:20px;">厂检调试记录单</div>';
  html += '<div style="float:right;width:20%;text-align:right;font-size:8px;line-height:20px;">产品编号：' + escHtml(task.prodNo || task.productNo || '') + '</div>';
  html += '</div>';

  // SVG记录表
  html += '<div style="text-align:center;">' + svg + '</div>';

  // 结论说明
  html += '<div style="margin-top:4px;font-size:7px;color:#333;">结论选项中，符合打"√"，不符合打"×"，不适用打"/"，或写入测量值。</div>';

  // 页码
  html += '<div style="text-align:center;font-size:8px;margin-top:2px;">— ' + pageNum + ' —</div>';

  html += '</div>';

  return html;
}
'''
    return new_func


def main():
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    print('=== v56 升级开始 ===')

    # 1. 给检查项名称加附表标注
    original = content
    content = add_attach_labels(content)
    changed = content != original
    print(f'1. 附表标注: {"已更新" if changed else "无变化"}')

    # 2. 提取logoBase64（从旧函数里拿）
    logo_match = re.search(r"var logoBase64 = '([^']+)';", content)
    if logo_match:
        logo_base64 = logo_match.group(1)
        print(f'2. 提取logoBase64: 成功，长度{len(logo_base64)}')
    else:
        print('2. 提取logoBase64: 失败！')
        return

    # 3. 找到旧的buildCheckItemsHTML函数并替换
    # 找函数起始
    func_start = None
    func_end = None
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'function buildCheckItemsHTML' in line:
            func_start = i
            break
    
    if func_start is None:
        print('3. 未找到buildCheckItemsHTML函数！')
        return
    
    # 找函数结束（匹配大括号）
    depth = 0
    started = False
    for i in range(func_start, len(lines)):
        for ch in lines[i]:
            if ch == '{':
                depth += 1
                started = True
            elif ch == '}':
                depth -= 1
        if started and depth == 0:
            func_end = i
            break
    
    print(f'3. 旧函数范围: L{func_start+1} - L{func_end+1}（共{func_end-func_start+1}行）')

    # 生成新函数并替换logo占位符
    new_func = build_new_buildCheckItemsHTML()
    new_func = new_func.replace('REPLACE_LOGO_BASE64', logo_base64)

    # 替换函数
    new_lines = lines[:func_start] + new_func.strip().split('\n') + lines[func_end+1:]
    content = '\n'.join(new_lines)
    print(f'4. 函数替换完成')

    # 4. 写入文件
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'5. 文件已写入: {FILE_PATH}')

    # 5. 同步英文文件名
    en_path = FILE_PATH.replace('威特电梯厂检调试记录单v2.html', 'factory-inspection-v2.html')
    import shutil
    shutil.copy2(FILE_PATH, en_path)
    print(f'6. 已同步到英文文件名: {os.path.basename(en_path)}')

    # 6. 验证JS语法
    print('7. JS语法验证...')
    # 提取所有script内容验证
    import subprocess
    result = subprocess.run(['node', '--check', FILE_PATH], capture_output=True, text=True)
    if result.returncode == 0:
        print('   ✓ HTML文件语法检查通过（node --check 检测script标签）')
    else:
        print(f'   ⚠ 直接检查失败（正常，因为是HTML），尝试提取script...')
    
    # 用更可靠的方式：提取所有<script>内容单独验证
    script_pattern = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL)
    scripts = script_pattern.findall(content)
    print(f'   找到 {len(scripts)} 个script块')
    all_ok = True
    for idx, script in enumerate(scripts):
        # 跳过外部库
        if script.strip().startswith('//') or len(script.strip()) < 100:
            continue
        temp_file = '/tmp/check_script.js'
        with open(temp_file, 'w') as f:
            f.write(script)
        result = subprocess.run(['node', '--check', temp_file], capture_output=True, text=True)
        if result.returncode != 0:
            print(f'   ✗ script[{idx}] 语法错误: {result.stderr[:200]}')
            all_ok = False
    if all_ok:
        print('   ✓ 所有核心script语法验证通过')

    print()
    print('=== v56 升级完成 ===')


if __name__ == '__main__':
    main()
