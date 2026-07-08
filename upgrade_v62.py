#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v62 升级：
1. 技术资料编号改为右对齐，中间竖线隐藏，长编号往左延伸利用项目名侧空间（不溢出结论列）
2. SVG总宽从750调到720，增加打印安全边距，避免右边被切
3. SVG居中显示，左右边距对称
"""

files = [
    '/app/data/所有对话/主对话/weite-pro-temp/factory-inspection-v2.html',
    '/app/data/所有对话/主对话/weite-pro-temp/威特电梯厂检调试记录单v2.html'
]

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        html = f.read()

    # ============================================================
    # 1. totalW 从 750 调到 720
    # ============================================================
    old_totalw = "  var totalW = 750;      // SVG总宽度（A4打印安全宽度，左右边距对称）"
    new_totalw = "  var totalW = 720;      // SVG总宽度（A4打印安全宽度，留足边距避免右边被切）"
    html = html.replace(old_totalw, new_totalw, 1)

    # ============================================================
    # 2. 技术资料内容列：去掉中间竖线，项目名左对齐，编号右对齐
    #    原来：内容列中间画竖线，左边55%放项目名，右边45%放编号（居中）
    #    改为：整列共用空间，项目名左对齐，编号右对齐，中间留间距
    # ============================================================

    # 2a. 去掉中间竖线（技术资料分类的内容列中间竖线）
    old_midline = '''        // 技术资料分类：内容列中间加竖线（分两列）
        if (info.splitContent) {
          svg += '<line x1="' + splitX + '" y1="' + itemTop + '" x2="' + splitX + '" y2="' + itemBottom + '" stroke="#000" stroke-width="' + strokeW + '"/>';
        }'''

    new_midline = '''        // 技术资料分类：中间不画竖线，编号右对齐（长编号往左延伸，不溢出结论列）
        // if (info.splitContent) {
        //   svg += '<line x1="' + splitX + '" y1="' + itemTop + '" x2="' + splitX + '" y2="' + itemBottom + '" stroke="#000" stroke-width="' + strokeW + '"/>';
        // }'''

    html = html.replace(old_midline, new_midline, 1)

    # 2b. 编号列：从居中改为右对齐，并且使用整列宽度（去掉45%的限制）
    old_plate = '''        // 技术资料右边列：显示设备编号（优先读checks.v，为空则从配置表自动取）
        if (info.splitContent) {
          var checkData = task.checks && task.checks[id];
          var plateNo = (checkData && checkData.v) ? escHtml(checkData.v) : '';
          if (!plateNo) {
            var _item = checkItems.find(function(i){return i.id === id;});
            if (_item && _item.category === '技术资料') {
              var _partKey = getConfigPartKey(_item);
              if (_partKey) {
                var _parts = (task && task.configParts) ? task.configParts : configPartsData;
                plateNo = escHtml(_parts[_partKey + '_编号'] || '');
              }
            }
          }
          if (plateNo) {
            var rightColCenterX = splitX + (contentRight - splitX) / 2;
            svg += '<text x="' + rightColCenterX + '" y="' + itemMidY + '" font-size="' + fontSize + '" text-anchor="middle" dominant-baseline="middle" fill="#000">' + plateNo + '</text>';
          }
        }'''

    new_plate = '''        // 技术资料编号：右对齐，利用整列宽度，长编号往左延伸不溢出结论列
        if (info.splitContent) {
          var checkData = task.checks && task.checks[id];
          var plateNo = (checkData && checkData.v) ? escHtml(checkData.v) : '';
          if (!plateNo) {
            var _item = checkItems.find(function(i){return i.id === id;});
            if (_item && _item.category === '技术资料') {
              var _partKey = getConfigPartKey(_item);
              if (_partKey) {
                var _parts = (task && task.configParts) ? task.configParts : configPartsData;
                plateNo = escHtml(_parts[_partKey + '_编号'] || '');
              }
            }
          }
          if (plateNo) {
            // 编号右对齐，右边留2px边距，长了往左延伸（项目名侧有充足空间）
            var plateRightX = contentRight - 2;
            svg += '<text x="' + plateRightX + '" y="' + itemMidY + '" font-size="' + fontSize + '" text-anchor="end" dominant-baseline="middle" fill="#000">' + plateNo + '</text>';
          }
        }'''

    html = html.replace(old_plate, new_plate, 1)

    # 2c. 项目名宽度不再限制在左55%，用整列左边部分（留右边空间给编号右对齐）
    # 实际上项目名很短，原来的contW已经够了，不需要改
    # 但为了统一，把项目名的左边界保持不变，右边界可以延伸但不影响编号（因为编号右对齐在最右边）
    # 这里不需要改项目名的渲染，因为项目名短，不会长到跟编号重叠

    # ============================================================
    # 3. SVG外层容器居中
    # ============================================================
    # 找buildCheckItemsHTML中svg开始标签前的容器div
    import re
    # 匹配包含 <svg width= 的那行及前面的 div 起始行
    pattern = r"(html = '<div style=\\?\"[^>]*\\?\">';\s*\n\s*html \+= '<svg width=)"
    match = re.search(pattern, html)
    if match:
        old_svg_div = match.group(1)
        if 'text-align' not in old_svg_div:
            new_svg_div = old_svg_div.replace(
                'html = \'<div style="',
                'html = \'<div style="text-align:center;'
            )
            html = html.replace(old_svg_div, new_svg_div, 1)

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"{fpath} 已更新为 v62")

print("\nv62 升级完成：")
print("1. 技术资料编号右对齐，中间竖线去掉，长编号往左延伸不顶结论列")
print("2. SVG总宽720px（留足打印边距，避免右边被切）")
print("3. SVG居中显示（左右边距对称）")
