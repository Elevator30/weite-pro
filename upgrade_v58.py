# v58 升级脚本
# 修改内容：
# 1. 标题列加宽 (18→28px)，长标题自动分两列竖排，不超出边界
# 2. 技术资料右边列显示设备编号（从checks[id].v读取）
# 3. 调整总宽度，确保打印左右边距对称
# 4. 三栏标题列都加宽，整体表格撑满页面

import re

with open('factory-inspection-v2.html', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('function buildCheckItemsHTML')
end = content.find('\nfunction ', start + 1)
section = content[start:end]

# ========== 1. 修改配置参数 ==========
old_config = """  // ========== 配置参数 ==========
  var rowH = 15;         // 数据行行高
  var titleW = 18;       // 竖排标题列宽
  var seqW = 20;         // 序号列宽
  var resultW = 26;      // 结论列宽
  var headerH = 17;      // 表头行高
  var fontSize = 8;      // 统一字号
  var strokeW = 0.5;     // 统一框线粗细
  var colGap = 0;        // 栏间距（0=紧贴）
  var splitRatio = 0.55; // 技术资料分类内容列分割比例"""

new_config = """  // ========== 配置参数 ==========
  var rowH = 15;         // 数据行行高
  var titleW = 28;       // 竖排标题列宽（加宽，长标题可分两列）
  var seqW = 20;         // 序号列宽
  var resultW = 28;      // 结论列宽
  var headerH = 17;      // 表头行高
  var fontSize = 8;      // 统一字号
  var strokeW = 0.5;     // 统一框线粗细
  var colGap = 0;        // 栏间距（0=紧贴）
  var splitRatio = 0.55; // 技术资料分类内容列分割比例
  var totalW = 780;      // SVG总宽度（A4打印左右边距对称）"""

if old_config in section:
    section = section.replace(old_config, new_config)
    print("✅ 配置参数已更新")
else:
    print("❌ 未找到配置参数区块")
    # 尝试找一下实际的内容
    idx = section.find('配置参数')
    print(section[idx:idx+400])

# ========== 2. 修改verticalText函数，支持多列竖排 ==========
old_vt = """  // 竖排逐字文字（每个字都是正的，从上往下排）
  function verticalText(text, x, startY, fs, spacing) {
    var svg = '';
    for (var i = 0; i < text.length; i++) {
      var ch = text.charAt(i);
      svg += '<text x="' + x + '" y="' + (startY + i * spacing) + '" font-size="' + fs + '" text-anchor="middle" dominant-baseline="middle" fill="#000">' + escHtml(ch) + '</text>';
    }
    return svg;
  }"""

new_vt = """  // 竖排逐字文字（每个字都是正的，从上往下排），支持多列竖排
  function verticalText(text, x, startY, fs, spacing, cols, colWidth) {
    var svg = '';
    cols = cols || 1;
    colWidth = colWidth || 0;
    var charsPerCol = Math.ceil(text.length / cols);
    for (var c = 0; c < cols; c++) {
      var colX = x + (c - (cols - 1) / 2) * colWidth;
      var startIdx = c * charsPerCol;
      var endIdx = Math.min(startIdx + charsPerCol, text.length);
      for (var i = startIdx; i < endIdx; i++) {
        var ch = text.charAt(i);
        var y = startY + (i - startIdx) * spacing;
        svg += '<text x="' + colX + '" y="' + y + '" font-size="' + fs + '" text-anchor="middle" dominant-baseline="middle" fill="#000">' + escHtml(ch) + '</text>';
      }
    }
    return svg;
  }"""

if old_vt in section:
    section = section.replace(old_vt, new_vt)
    print("✅ verticalText函数已更新（支持多列竖排）")
else:
    print("❌ 未找到verticalText函数")

# ========== 3. 修改标题渲染逻辑（自动分栏） ==========
old_title_render = """      // 竖排标题文字（逐字正向）
      var titleCenterX = colX + titleW / 2;
      var letterSpacing = fontSize + 1.5;
      var totalTextH = info.label.length * letterSpacing;
      var titleStartY = groupTop + (groupH - totalTextH) / 2 + letterSpacing / 2 + fontSize / 3;
      svg += verticalText(info.label, titleCenterX, titleStartY, fontSize, letterSpacing);"""

new_title_render = """      // 竖排标题文字（逐字正向，长标题自动分栏）
      var titleCenterX = colX + titleW / 2;
      var letterSpacing = fontSize + 1.5;
      var maxTextH = groupH - 4; // 上下各留2px边距
      var totalTextH = info.label.length * letterSpacing;
      var titleCols = 1;
      if (totalTextH > maxTextH) {
        titleCols = Math.ceil(totalTextH / maxTextH);
        if (titleCols > 3) titleCols = 3; // 最多3列
      }
      var charsPerCol = Math.ceil(info.label.length / titleCols);
      var colTextH = charsPerCol * letterSpacing;
      var titleStartY = groupTop + (groupH - colTextH) / 2 + letterSpacing / 2 + fontSize / 3;
      var titleColW = titleW / (titleCols + 0.5); // 列间距
      svg += verticalText(info.label, titleCenterX, titleStartY, fontSize, letterSpacing, titleCols, titleColW);"""

if old_title_render in section:
    section = section.replace(old_title_render, new_title_render)
    print("✅ 标题渲染逻辑已更新（自动分栏）")
else:
    print("❌ 未找到标题渲染逻辑")
    # 调试：找一下实际内容
    idx = section.find('竖排标题文字')
    if idx >= 0:
        print("找到竖排标题文字 at", idx)
        print(section[idx:idx+500])

# ========== 4. 技术资料右边列显示设备编号 ==========
# 找到技术资料内容渲染的部分，添加右边列的编号显示
# 先找到splitContent相关的渲染代码
old_split = """        if (info.splitContent) {
          // 技术资料分两列：左边项目名，右边留空填编号
          contW = splitX - colX - titleW - seqW - 4;
        }"""

new_split = """        if (info.splitContent) {
          // 技术资料分两列：左边项目名，右边显示设备编号
          contW = splitX - colX - titleW - seqW - 4;
        }"""

if old_split in section:
    section = section.replace(old_split, new_split)
    print("✅ 技术资料分栏注释已更新")
else:
    print("⚠️  未找到splitContent渲染代码（可能变量名不同）")

# 找到结论渲染之前，添加右边列编号显示的代码
old_result = """        // 结论
        var resultVal = getResult(id);
        if (resultVal) {
          svg += '<text x="' + (contentRight + resultW / 2) + '" y="' + itemMidY + '" font-size="' + fontSize + '" text-anchor="middle" dominant-baseline="middle" fill="#000">' + resultVal + '</text>';
        }"""

# 在结论前面，添加技术资料右边列编号显示
new_result = """        // 技术资料右边列：显示设备编号/型号
        if (info.splitContent) {
          var checkData = task.checks && task.checks[id];
          var plateNo = (checkData && checkData.v) ? escHtml(checkData.v) : '';
          if (plateNo) {
            var rightColCenterX = splitX + (contentRight - splitX) / 2;
            svg += '<text x="' + rightColCenterX + '" y="' + itemMidY + '" font-size="' + fontSize + '" text-anchor="middle" dominant-baseline="middle" fill="#000">' + plateNo + '</text>';
          }
        }

        // 结论
        var resultVal = getResult(id, info.splitContent);
        if (resultVal) {
          svg += '<text x="' + (contentRight + resultW / 2) + '" y="' + itemMidY + '" font-size="' + fontSize + '" text-anchor="middle" dominant-baseline="middle" fill="#000">' + resultVal + '</text>';
        }"""

if old_result in section:
    section = section.replace(old_result, new_result)
    print("✅ 技术资料右边列编号显示已添加")
else:
    print("❌ 未找到结论渲染代码")
    # 调试
    idx = section.find('// 结论')
    if idx >= 0:
        print("找到结论 at", idx)
        print(section[idx:idx+400])

# ========== 5. 修改getResult函数，支持splitContent模式 ==========
# 对于技术资料分类，结论列只显示√×/，不显示v值（v值在右边列显示）
old_getresult = """  function getResult(id) {
    var c = task.checks && task.checks[id];
    if (!c) return '';
    if (c.s === 'ok') return '√';
    if (c.s === 'ng') return '×';
    if (c.s === 'na') return '/';
    if (c.v !== undefined && c.v !== '') return escHtml(c.v);
    return '';
  }"""

new_getresult = """  function getResult(id, splitMode) {
    var c = task.checks && task.checks[id];
    if (!c) return '';
    if (c.s === 'ok') return '√';
    if (c.s === 'ng') return '×';
    if (c.s === 'na') return '/';
    // 技术资料分栏模式下，结论列只显示状态符号，v值在右边编号列显示
    if (splitMode) return '';
    if (c.v !== undefined && c.v !== '') return escHtml(c.v);
    return '';
  }"""

if old_getresult in section:
    section = section.replace(old_getresult, new_getresult)
    print("✅ getResult函数已更新（支持splitMode）")
else:
    print("❌ 未找到getResult函数")
    # 调试
    idx = section.find('function getResult')
    if idx >= 0:
        print("找到getResult at", idx)
        print(section[idx:idx+300])

# ========== 6. 调整SVG总宽度和页面布局 ==========
# 找到SVG创建的地方，使用配置的totalW而不是计算的
old_svg_create = """  var svg = '';
  svg += '<svg width="' + totalW + '" height="' + (totalH + 40) + '" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:auto;">';"""

new_svg_create = """  var svg = '';
  svg += '<svg width="' + totalW + '" height="' + (totalH + 40) + '" xmlns="http://www.w3.org/2000/svg" style="display:block;max-width:100%;height:auto;margin:0 auto;">';"""

if old_svg_create in section:
    section = section.replace(old_svg_create, new_svg_create)
    print("✅ SVG创建已更新（居中+最大宽度）")
else:
    print("⚠️  SVG创建代码不同，跳过")
    idx = section.find("var svg = ''")
    if idx >= 0:
        print(section[idx:idx+300])

# ========== 7. 确保每栏宽度是总宽度的1/3 ==========
# 找到colW计算的地方
old_colw = "  var colW = (totalW - 2 * colGap) / 3;"
new_colw = "  var colW = (totalW - 2 * colGap) / 3;  // 每栏均分总宽度"

if old_colw in section:
    section = section.replace(old_colw, new_colw)
    print("✅ 栏宽计算确认")
else:
    print("⚠️  栏宽计算代码不同")
    idx = section.find('colW =')
    if idx >= 0:
        print(section[idx-50:idx+100])

# ========== 写回文件 ==========
content = content[:start] + section + content[end:]

with open('factory-inspection-v2.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ v58升级完成")
