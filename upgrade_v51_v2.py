#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
威特电梯厂检调试记录单 v50.9 -> v51 升级脚本 v2
用大括号深度计算精确替换，避免正则吞块问题
"""

import re
import sys

def find_matching_brace(s, start):
    """从start位置的{开始，找到匹配的}，返回其位置"""
    depth = 0
    for i in range(start, len(s)):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return i
    return -1

def find_if_block(s, if_pattern):
    """找到if块的起止位置，返回(start, end)，end是闭合}的位置"""
    idx = s.find(if_pattern)
    if idx < 0:
        return -1, -1
    # 找第一个{
    brace_start = s.find('{', idx)
    if brace_start < 0:
        return -1, -1
    brace_end = find_matching_brace(s, brace_start)
    return idx, brace_end

def replace_version(content):
    """替换所有版本号 v50.9 -> v51"""
    content = content.replace('v50.9', 'v51')
    content = content.replace('V50.9', 'v51')
    content = content.replace(
        '<!-- v50.9: buildCheckItemsHTML和buildSingleAttachHTML改用纯table布局，移除所有flex/float，确保html2canvas正确渲染 -->',
        '<!-- v51: buildCheckItemsHTML三栏独立float布局;附表1SVG底图+绝对定位方案 -->'
    )
    return content

def replace_checkitems_layout(content):
    """修改buildCheckItemsHTML中的三栏布局：大table -> float div"""
    old_layout = """  // 三栏布局
  // 三栏布局 - table三列
  h += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;">';
  h += '<colgroup><col style="width:33.33%"><col style="width:33.33%"><col style="width:33.34%"></colgroup>';
  h += '<tr>';
  h += '<td style="padding:0 2px 0 0;vertical-align:top;">' + buildColumn(pageConfig.col1) + '</td>';
  h += '<td style="padding:0 2px;vertical-align:top;">' + buildColumn(pageConfig.col2) + '</td>';
  h += '<td style="padding:0 0 0 2px;vertical-align:top;">' + buildColumn(pageConfig.col3) + '</td>';
  h += '</tr>';
  h += '</table>';"""

    new_layout = """  // 三栏布局 - float独立布局，每栏高度由内容决定，不对齐行
  h += '<div style="overflow:hidden;zoom:1;">';
  h += '<div style="float:left;width:33.33%;padding:0 3px 0 0;box-sizing:border-box;">' + buildColumn(pageConfig.col1) + '</div>';
  h += '<div style="float:left;width:33.33%;padding:0 3px;box-sizing:border-box;">' + buildColumn(pageConfig.col2) + '</div>';
  h += '<div style="float:left;width:33.34%;padding:0 0 0 3px;box-sizing:border-box;">' + buildColumn(pageConfig.col3) + '</div>';
  h += '</div>';"""

    if old_layout in content:
        content = content.replace(old_layout, new_layout)
        print("  ✓ 三栏布局替换成功")
    else:
        print("  ✗ 精确匹配失败，尝试模糊搜索...")
        # 在buildCheckItemsHTML函数内找
        func_start = content.find('function buildCheckItemsHTML')
        func_end = content.find('function buildSingleAttachHTML', func_start)
        if func_end < 0:
            func_end = len(content)
        func_content = content[func_start:func_end]
        
        # 找三栏布局table
        table_start = func_content.find("h += '<table")
        table_end = func_content.find("h += '</table>';", table_start) + len("h += '</table>';")
        if table_start > 0 and table_end > table_start:
            old_block = func_content[table_start:table_end]
            # 找前面的注释行
            comment_start = func_content.rfind('// 三栏', 0, table_start)
            if comment_start > 0:
                # 往上找行首
                line_start = func_content.rfind('\n', 0, comment_start) + 1
                old_block = func_content[line_start:table_end]
            
            new_block = new_layout
            new_func = func_content[:table_start - (table_start - comment_start - 0)] + new_layout + func_content[table_end:]
            # 更简单的方式：直接替换table那段
            new_func = func_content.replace(old_block, new_layout)
            content = content[:func_start] + new_func + content[func_end:]
            print("  ✓ 模糊匹配替换成功")
        else:
            print("  ✗ 模糊匹配也失败")
    return content

def build_attach1_svg_cn():
    """中文版附表1 SVG方案"""
    return """  // ========== 附表1: SVG底图 + 绝对定位方案 ==========
  if (attNum === 1) {
    h += buildAttachHeader('附表1  电梯门间隙、门锁啮合长度及地坎间距检验记录', '附表1');

    // 配置
    var rowH = 16;
    var headerRowH = [22, 22, 24, 26, 26, 20]; // 6行表头高度
    var leftColW = 64;
    var dataColW = [44, 44, 44, 44, 44, 44, 44, 52, 56, 56, 56];
    var totalW = leftColW + dataColW.reduce(function(a,b){return a+b;}, 0);

    // 计算列x坐标
    var colX = [leftColW];
    for (var dc = 0; dc < dataColW.length; dc++) {
      colX.push(colX[colX.length-1] + dataColW[dc]);
    }

    // 计算行y坐标
    var rowY = [0];
    for (var hr = 0; hr < headerRowH.length; hr++) {
      rowY.push(rowY[rowY.length-1] + headerRowH[hr]);
    }
    var dataStartY = rowY[rowY.length-1];
    var dataRows = 17;
    for (var dr = 0; dr < dataRows; dr++) {
      rowY.push(rowY[rowY.length-1] + rowH);
    }
    var totalH = rowY[rowY.length-1];

    // 生成SVG
    var svg = '<svg width="' + totalW + '" height="' + totalH + '" xmlns="http://www.w3.org/2000/svg" style="display:block;">';

    // === 灰色背景 ===
    svg += '<rect x="0" y="0" width="' + totalW + '" height="' + rowY[3] + '" fill="#f0f0f0"/>';
    svg += '<rect x="0" y="' + rowY[3] + '" width="' + totalW + '" height="' + (rowY[5]-rowY[3]) + '" fill="#fafafa"/>';
    svg += '<rect x="0" y="' + rowY[5] + '" width="' + totalW + '" height="' + (rowY[6]-rowY[5]) + '" fill="#f0f0f0"/>';
    svg += '<rect x="0" y="' + rowY[6] + '" width="' + leftColW + '" height="' + (totalH-rowY[6]) + '" fill="#f0f0f0"/>';

    // === 竖线 ===
    svg += '<line x1="0" y1="0" x2="0" y2="' + totalH + '" stroke="#000" stroke-width="1"/>';
    for (var vx = 0; vx < colX.length; vx++) {
      svg += '<line x1="' + colX[vx] + '" y1="0" x2="' + colX[vx] + '" y2="' + totalH + '" stroke="#000" stroke-width="1"/>';
    }
    svg += '<line x1="' + totalW + '" y1="0" x2="' + totalW + '" y2="' + totalH + '" stroke="#000" stroke-width="1"/>';

    // === 横线 ===
    for (var hy = 0; hy < rowY.length; hy++) {
      svg += '<line x1="0" y1="' + rowY[hy] + '" x2="' + totalW + '" y2="' + rowY[hy] + '" stroke="#000" stroke-width="1"/>';
    }

    // === 表头第1行文字 ===
    var midY1 = rowY[0] + headerRowH[0]/2 + 3;
    // 第1列: 检验项目编号与内容 (跨3行)
    svg += '<text x="' + (leftColW/2) + '" y="' + (rowY[0] + (rowY[3]-rowY[0])/2 - 4) + '" text-anchor="middle" font-size="8px" font-weight="bold" font-family="sans-serif">检验项目</text>';
    svg += '<text x="' + (leftColW/2) + '" y="' + (rowY[0] + (rowY[3]-rowY[0])/2 + 8) + '" text-anchor="middle" font-size="8px" font-weight="bold" font-family="sans-serif">编号与内容</text>';

    // A1.2.7.1 (跨2列第1行)
    var a1x = colX[0] + (colX[2]-colX[0])/2;
    svg += '<text x="' + a1x + '" y="' + midY1 + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.1</text>';

    // A1.2.7.2门间隙 (跨6列第1行)
    var gapX = colX[2] + (colX[8]-colX[2])/2;
    svg += '<text x="' + gapX + '" y="' + midY1 + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.2门间隙</text>';

    // 门锁啮合长度 (第9列, 跨3行)
    var lockX = colX[8] + dataColW[8]/2;
    var lockMidY = rowY[0] + (rowY[3]-rowY[0])/2;
    svg += '<text x="' + lockX + '" y="' + (lockMidY - 10) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.8(2)</text>';
    svg += '<text x="' + lockX + '" y="' + (lockMidY) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">门锁啮合</text>';
    svg += '<text x="' + lockX + '" y="' + (lockMidY + 10) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">长度</text>';

    // A1.2.7.10 (跨2列第1行)
    var a10x = colX[9] + (colX[11]-colX[9])/2;
    svg += '<text x="' + a10x + '" y="' + midY1 + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.10</text>';

    // === 表头第2行文字 ===
    var midY2 = rowY[1] + headerRowH[1]/2 + 3;
    // 门地坎距离 (跨2列, 跨2-3行)
    var sillX = colX[0] + (colX[2]-colX[0])/2;
    svg += '<text x="' + sillX + '" y="' + (rowY[1] + (rowY[3]-rowY[1])/2 + 3) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">门地坎距离</text>';

    // A1.2.7.2(1) (跨5列第2行)
    var a21x = colX[2] + (colX[7]-colX[2])/2;
    svg += '<text x="' + a21x + '" y="' + midY2 + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.2(1)</text>';

    // A1.2.7.2(2)门扇间施力间隙 (第8列, 跨2-3行)
    var forceX = colX[7] + dataColW[7]/2;
    var forceMidY = rowY[1] + (rowY[3]-rowY[1])/2;
    svg += '<text x="' + forceX + '" y="' + (forceMidY - 8) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">A1.2.7.2(2)</text>';
    svg += '<text x="' + forceX + '" y="' + (forceMidY) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">门扇间</text>';
    svg += '<text x="' + forceX + '" y="' + (forceMidY + 8) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">施力间隙</text>';

    // 轿门门刀与层门地坎间隙 (第10列, 跨2-3行)
    var knifeX = colX[9] + dataColW[9]/2;
    var knifeMidY = rowY[1] + (rowY[3]-rowY[1])/2;
    svg += '<text x="' + knifeX + '" y="' + (knifeMidY - 8) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">轿门门刀与</text>';
    svg += '<text x="' + knifeX + '" y="' + (knifeMidY + 2) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">层门地坎间隙</text>';

    // 层门门锁滚轮与轿厢地坎间隙 (第11列, 跨2-3行)
    var rollerX = colX[10] + dataColW[10]/2;
    var rollerMidY = rowY[1] + (rowY[3]-rowY[1])/2;
    svg += '<text x="' + rollerX + '" y="' + (rollerMidY - 8) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">层门门锁滚轮与</text>';
    svg += '<text x="' + rollerX + '" y="' + (rollerMidY + 2) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">轿厢地坎间隙</text>';

    // === 表头第3行文字 ===
    var midY3 = rowY[2] + headerRowH[2]/2 + 2;
    // 门扇间间隙 (第3列)
    svg += '<text x="' + (colX[2]+dataColW[2]/2) + '" y="' + (midY3 - 4) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">门扇间</text>';
    svg += '<text x="' + (colX[2]+dataColW[2]/2) + '" y="' + (midY3 + 6) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">间隙</text>';

    // 门扇与立柱、门楣间隙 (跨2列: 第4-5列)
    var frameMidX = colX[3] + (colX[5]-colX[3])/2;
    svg += '<text x="' + frameMidX + '" y="' + (midY3 - 4) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">门扇与立柱、</text>';
    svg += '<text x="' + frameMidX + '" y="' + (midY3 + 6) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">门楣间隙</text>';
    // 左/右小字
    svg += '<text x="' + (colX[3]+dataColW[3]/2) + '" y="' + (midY3 + 16) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">左</text>';
    svg += '<text x="' + (colX[4]+dataColW[4]/2) + '" y="' + (midY3 + 16) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">右</text>';

    // 门扇与地坎间隙 (跨2列: 第6-7列)
    var sillMidX = colX[5] + (colX[7]-colX[5])/2;
    svg += '<text x="' + sillMidX + '" y="' + (midY3 + 2) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">门扇与地坎间隙</text>';
    svg += '<text x="' + (colX[5]+dataColW[5]/2) + '" y="' + (midY3 + 16) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">左</text>';
    svg += '<text x="' + (colX[6]+dataColW[6]/2) + '" y="' + (midY3 + 16) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">右</text>';

    // === 判断标准行 ===
    var judgeMidY = rowY[3] + (rowY[5]-rowY[3])/2 + 2;
    // 判断标准 (第1列, 跨2行)
    svg += '<text x="' + (leftColW/2) + '" y="' + judgeMidY + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">判断标准</text>';

    // 门地坎距离标准
    svg += '<text x="' + sillX + '" y="' + (judgeMidY - 10) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">≤35mm</text>';
    svg += '<text x="' + sillX + '" y="' + (judgeMidY) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">左右偏差</text>';
    svg += '<text x="' + sillX + '" y="' + (judgeMidY + 10) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">小于1/1000</text>';

    // 门间隙标准
    var stdGapX = colX[2] + (colX[7]-colX[2])/2;
    svg += '<text x="' + stdGapX + '" y="' + (judgeMidY - 10) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">乘客电梯：3~6mm</text>';
    svg += '<text x="' + stdGapX + '" y="' + (judgeMidY) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">载货电梯：3~10mm</text>';
    svg += '<text x="' + stdGapX + '" y="' + (judgeMidY + 10) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">左右偏差不超过1mm</text>';

    // 施力间隙标准
    svg += '<text x="' + forceX + '" y="' + (judgeMidY - 5) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">旁开门：≤30</text>';
    svg += '<text x="' + forceX + '" y="' + (judgeMidY + 7) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">中分门：≤45</text>';

    // 啮合长度标准
    svg += '<text x="' + lockX + '" y="' + judgeMidY + '" text-anchor="middle" font-size="7px" font-family="sans-serif">≥7mm</text>';

    // A1.2.7.10标准
    svg += '<text x="' + a10x + '" y="' + judgeMidY + '" text-anchor="middle" font-size="7px" font-family="sans-serif">≥5mm</text>';

    // === 数据列表头行 ===
    var dataHdrY = rowY[5] + headerRowH[5]/2 + 3;
    svg += '<text x="' + (leftColW/2) + '" y="' + dataHdrY + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">位置</text>';
    var hdrLabels = ['左','右','值','左','右','左','右','值','值','值','值'];
    for (var hl = 0; hl < hdrLabels.length; hl++) {
      svg += '<text x="' + (colX[hl]+dataColW[hl]/2) + '" y="' + dataHdrY + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">' + hdrLabels[hl] + '</text>';
    }

    // 左侧竖排文字：检验位置及测量数据
    var vertMidY = rowY[6] + (totalH-rowY[6])/2;
    svg += '<text x="' + (leftColW/2) + '" y="' + (vertMidY - 14) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">检验位置</text>';
    svg += '<text x="' + (leftColW/2) + '" y="' + (vertMidY - 2) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">及测量</text>';
    svg += '<text x="' + (leftColW/2) + '" y="' + (vertMidY + 10) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">数据</text>';

    svg += '</svg>';

    // 容器 + 数据单元格
    h += '<div style="position:relative;width:' + totalW + 'px;margin:0 auto;font-size:7px;font-family:sans-serif;">';
    h += svg;

    var posList = ['轿门1', '轿门2'];
    for (var fl = 1; fl <= 15; fl++) posList.push(fl + '层');

    for (var ri = 0; ri < posList.length; ri++) {
      var rowTop = dataStartY + ri * rowH;
      // 位置标签（在第2列，左起第1数据列）
      h += '<div style="position:absolute;left:0;top:' + rowTop + 'px;width:' + leftColW + 'px;height:' + rowH + 'px;line-height:' + rowH + 'px;text-align:center;font-size:7px;overflow:hidden;">';
      h += posList[ri];
      h += '</div>';

      // 11个数据单元格
      for (var ci = 0; ci < dataColW.length; ci++) {
        h += '<div style="position:absolute;left:' + colX[ci] + 'px;top:' + rowTop + 'px;width:' + dataColW[ci] + 'px;height:' + rowH + 'px;line-height:' + rowH + 'px;text-align:center;font-size:7px;overflow:hidden;">';
        h += '&nbsp;';
        h += '</div>';
      }
    }

    h += '</div>';
    h += buildAttachFooter('附表1');
  }
"""

def replace_attach1(content, is_cn=True):
    """用大括号深度计算精确替换附表1"""
    # 找到buildSingleAttachHTML函数
    func_match = re.search(r'(function buildSingleAttachHTML\(task, dateStr, attNum\) \{)', content)
    if not func_match:
        print("  ✗ 未找到buildSingleAttachHTML函数")
        return content
    
    func_start = func_match.start()
    brace_start = func_match.end() - 1  # 指向{
    func_end = find_matching_brace(content, brace_start)
    
    func_content = content[func_start:func_end+1]
    
    # 找到附表1的if块
    if is_cn:
        if_pattern = 'if (attNum === 1) {'
    else:
        if_pattern = 'if (attNum === 1) {'  # 英文版也是一样的pattern
    
    if_idx = func_content.find(if_pattern)
    if if_idx < 0:
        print("  ✗ 未找到附表1 if块")
        return content
    
    # 找到if块的{和匹配的}
    if_brace_start = func_content.find('{', if_idx)
    if_brace_end = find_matching_brace(func_content, if_brace_start)
    
    print(f"  附表1 if块位置: {if_idx} - {if_brace_end}")
    print(f"  块长度: {if_brace_end - if_idx + 1} 字符")
    
    # 生成新块
    new_block = build_attach1_svg_cn() if is_cn else build_attach1_svg_en()
    
    # 替换
    new_func = func_content[:if_idx] + new_block + func_content[if_brace_end+1:]
    new_content = content[:func_start] + new_func + content[func_end+1:]
    
    print(f"  ✓ 附表1替换成功（{'中文' if is_cn else '英文'}版）")
    return new_content

def build_attach1_svg_en():
    """英文版附表1 SVG方案"""
    return """  // ========== Attach 1: SVG background + absolute positioning ==========
  if (attNum === 1) {
    h += buildAttachHeader('Appendix 1  Elevator Door Gap, Door Lock Engagement Length & Sill Distance Inspection Record', 'Appendix 1');

    var rowH = 16;
    var headerRowH = [22, 22, 24, 26, 26, 20];
    var leftColW = 64;
    var dataColW = [44, 44, 44, 44, 44, 44, 44, 52, 56, 56, 56];
    var totalW = leftColW + dataColW.reduce(function(a,b){return a+b;}, 0);

    var colX = [leftColW];
    for (var dc = 0; dc < dataColW.length; dc++) {
      colX.push(colX[colX.length-1] + dataColW[dc]);
    }

    var rowY = [0];
    for (var hr = 0; hr < headerRowH.length; hr++) {
      rowY.push(rowY[rowY.length-1] + headerRowH[hr]);
    }
    var dataStartY = rowY[rowY.length-1];
    var dataRows = 17;
    for (var dr = 0; dr < dataRows; dr++) {
      rowY.push(rowY[rowY.length-1] + rowH);
    }
    var totalH = rowY[rowY.length-1];

    var svg = '<svg width="' + totalW + '" height="' + totalH + '" xmlns="http://www.w3.org/2000/svg" style="display:block;">';

    // Gray backgrounds
    svg += '<rect x="0" y="0" width="' + totalW + '" height="' + rowY[3] + '" fill="#f0f0f0"/>';
    svg += '<rect x="0" y="' + rowY[3] + '" width="' + totalW + '" height="' + (rowY[5]-rowY[3]) + '" fill="#fafafa"/>';
    svg += '<rect x="0" y="' + rowY[5] + '" width="' + totalW + '" height="' + (rowY[6]-rowY[5]) + '" fill="#f0f0f0"/>';
    svg += '<rect x="0" y="' + rowY[6] + '" width="' + leftColW + '" height="' + (totalH-rowY[6]) + '" fill="#f0f0f0"/>';

    // Vertical lines
    svg += '<line x1="0" y1="0" x2="0" y2="' + totalH + '" stroke="#000" stroke-width="1"/>';
    for (var vx = 0; vx < colX.length; vx++) {
      svg += '<line x1="' + colX[vx] + '" y1="0" x2="' + colX[vx] + '" y2="' + totalH + '" stroke="#000" stroke-width="1"/>';
    }
    svg += '<line x1="' + totalW + '" y1="0" x2="' + totalW + '" y2="' + totalH + '" stroke="#000" stroke-width="1"/>';

    // Horizontal lines
    for (var hy = 0; hy < rowY.length; hy++) {
      svg += '<line x1="0" y1="' + rowY[hy] + '" x2="' + totalW + '" y2="' + rowY[hy] + '" stroke="#000" stroke-width="1"/>';
    }

    // Header Row 1
    var midY1 = rowY[0] + headerRowH[0]/2 + 3;
    svg += '<text x="' + (leftColW/2) + '" y="' + (rowY[0] + (rowY[3]-rowY[0])/2 - 4) + '" text-anchor="middle" font-size="8px" font-weight="bold" font-family="sans-serif">Inspection Item</text>';
    svg += '<text x="' + (leftColW/2) + '" y="' + (rowY[0] + (rowY[3]-rowY[0])/2 + 8) + '" text-anchor="middle" font-size="8px" font-weight="bold" font-family="sans-serif">No. &amp; Content</text>';

    var a1x = colX[0] + (colX[2]-colX[0])/2;
    svg += '<text x="' + a1x + '" y="' + midY1 + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.1</text>';

    var gapX = colX[2] + (colX[8]-colX[2])/2;
    svg += '<text x="' + gapX + '" y="' + midY1 + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.2 Door Gap</text>';

    var lockX = colX[8] + dataColW[8]/2;
    var lockMidY = rowY[0] + (rowY[3]-rowY[0])/2;
    svg += '<text x="' + lockX + '" y="' + (lockMidY - 10) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.8(2)</text>';
    svg += '<text x="' + lockX + '" y="' + (lockMidY) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">Door Lock</text>';
    svg += '<text x="' + lockX + '" y="' + (lockMidY + 10) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">Engagement</text>';

    var a10x = colX[9] + (colX[11]-colX[9])/2;
    svg += '<text x="' + a10x + '" y="' + midY1 + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.10</text>';

    // Header Row 2
    var midY2 = rowY[1] + headerRowH[1]/2 + 3;
    var sillX = colX[0] + (colX[2]-colX[0])/2;
    svg += '<text x="' + sillX + '" y="' + (rowY[1] + (rowY[3]-rowY[1])/2 + 3) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">Door Sill Dist.</text>';

    var a21x = colX[2] + (colX[7]-colX[2])/2;
    svg += '<text x="' + a21x + '" y="' + midY2 + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.2(1)</text>';

    var forceX = colX[7] + dataColW[7]/2;
    var forceMidY = rowY[1] + (rowY[3]-rowY[1])/2;
    svg += '<text x="' + forceX + '" y="' + (forceMidY - 8) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">A1.2.7.2(2)</text>';
    svg += '<text x="' + forceX + '" y="' + (forceMidY) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">Panel Force</text>';
    svg += '<text x="' + forceX + '" y="' + (forceMidY + 8) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">Gap</text>';

    var knifeX = colX[9] + dataColW[9]/2;
    var knifeMidY = rowY[1] + (rowY[3]-rowY[1])/2;
    svg += '<text x="' + knifeX + '" y="' + (knifeMidY - 8) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">Door Vane &amp;</text>';
    svg += '<text x="' + knifeX + '" y="' + (knifeMidY + 2) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">Landing Sill</text>';

    var rollerX = colX[10] + dataColW[10]/2;
    var rollerMidY = rowY[1] + (rowY[3]-rowY[1])/2;
    svg += '<text x="' + rollerX + '" y="' + (rollerMidY - 8) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">Lock Roller &amp;</text>';
    svg += '<text x="' + rollerX + '" y="' + (rollerMidY + 2) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">Car Sill Gap</text>';

    // Header Row 3
    var midY3 = rowY[2] + headerRowH[2]/2 + 2;
    svg += '<text x="' + (colX[2]+dataColW[2]/2) + '" y="' + (midY3 + 2) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">Panel Gap</text>';

    var frameMidX = colX[3] + (colX[5]-colX[3])/2;
    svg += '<text x="' + frameMidX + '" y="' + (midY3 - 4) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">Jamb/Header</text>';
    svg += '<text x="' + frameMidX + '" y="' + (midY3 + 6) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">Gap</text>';
    svg += '<text x="' + (colX[3]+dataColW[3]/2) + '" y="' + (midY3 + 16) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">L</text>';
    svg += '<text x="' + (colX[4]+dataColW[4]/2) + '" y="' + (midY3 + 16) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">R</text>';

    var sillMidX = colX[5] + (colX[7]-colX[5])/2;
    svg += '<text x="' + sillMidX + '" y="' + (midY3 + 2) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">Sill Gap</text>';
    svg += '<text x="' + (colX[5]+dataColW[5]/2) + '" y="' + (midY3 + 16) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">L</text>';
    svg += '<text x="' + (colX[6]+dataColW[6]/2) + '" y="' + (midY3 + 16) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">R</text>';

    // Judgment Standard rows
    var judgeMidY = rowY[3] + (rowY[5]-rowY[3])/2 + 2;
    svg += '<text x="' + (leftColW/2) + '" y="' + judgeMidY + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">Standard</text>';

    svg += '<text x="' + sillX + '" y="' + (judgeMidY - 10) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">≤35mm</text>';
    svg += '<text x="' + sillX + '" y="' + (judgeMidY) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">L/R Dev.</text>';
    svg += '<text x="' + sillX + '" y="' + (judgeMidY + 10) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">&lt; 1/1000</text>';

    var stdGapX = colX[2] + (colX[7]-colX[2])/2;
    svg += '<text x="' + stdGapX + '" y="' + (judgeMidY - 10) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">Passenger: 3~6mm</text>';
    svg += '<text x="' + stdGapX + '" y="' + (judgeMidY) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">Freight: 3~10mm</text>';
    svg += '<text x="' + stdGapX + '" y="' + (judgeMidY + 10) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">L/R Dev ≤1mm</text>';

    svg += '<text x="' + forceX + '" y="' + (judgeMidY - 5) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">Side: ≤30</text>';
    svg += '<text x="' + forceX + '" y="' + (judgeMidY + 7) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">Center: ≤45</text>';

    svg += '<text x="' + lockX + '" y="' + judgeMidY + '" text-anchor="middle" font-size="7px" font-family="sans-serif">≥7mm</text>';

    svg += '<text x="' + a10x + '" y="' + judgeMidY + '" text-anchor="middle" font-size="7px" font-family="sans-serif">≥5mm</text>';

    // Data header row
    var dataHdrY = rowY[5] + headerRowH[5]/2 + 3;
    svg += '<text x="' + (leftColW/2) + '" y="' + dataHdrY + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">Pos</text>';
    var hdrLabels = ['L','R','Val','L','R','L','R','Val','Val','Val','Val'];
    for (var hl = 0; hl < hdrLabels.length; hl++) {
      svg += '<text x="' + (colX[hl]+dataColW[hl]/2) + '" y="' + dataHdrY + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">' + hdrLabels[hl] + '</text>';
    }

    // Vertical text: Position & Data
    var vertMidY = rowY[6] + (totalH-rowY[6])/2;
    svg += '<text x="' + (leftColW/2) + '" y="' + (vertMidY - 14) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">Position</text>';
    svg += '<text x="' + (leftColW/2) + '" y="' + (vertMidY - 2) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">&amp;</text>';
    svg += '<text x="' + (leftColW/2) + '" y="' + (vertMidY + 10) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">Measured</text>';

    svg += '</svg>';

    h += '<div style="position:relative;width:' + totalW + 'px;margin:0 auto;font-size:7px;font-family:sans-serif;">';
    h += svg;

    var posList = ['Car Door 1', 'Car Door 2'];
    for (var fl = 1; fl <= 15; fl++) posList.push('F' + fl);

    for (var ri = 0; ri < posList.length; ri++) {
      var rowTop = dataStartY + ri * rowH;
      h += '<div style="position:absolute;left:0;top:' + rowTop + 'px;width:' + leftColW + 'px;height:' + rowH + 'px;line-height:' + rowH + 'px;text-align:center;font-size:7px;overflow:hidden;">';
      h += posList[ri];
      h += '</div>';

      for (var ci = 0; ci < dataColW.length; ci++) {
        h += '<div style="position:absolute;left:' + colX[ci] + 'px;top:' + rowTop + 'px;width:' + dataColW[ci] + 'px;height:' + rowH + 'px;line-height:' + rowH + 'px;text-align:center;font-size:7px;overflow:hidden;">';
        h += '&nbsp;';
        h += '</div>';
      }
    }

    h += '</div>';
    h += buildAttachFooter('Appendix 1');
  }
"""

def process_file(filepath, is_cn=True):
    """处理单个文件"""
    print(f"\n处理文件: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"  原始大小: {len(content)} 字符")
    
    # 1. 版本号
    content = replace_version(content)
    print("  ✓ 版本号替换完成")
    
    # 2. 记录表三栏布局
    content = replace_checkitems_layout(content)
    
    # 3. 附表1 SVG方案
    content = replace_attach1(content, is_cn=is_cn)
    
    # 写回
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  最终大小: {len(content)} 字符")
    return content

def verify_file(filepath):
    """验证文件"""
    print(f"\n验证文件: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"  文件大小: {len(content)} 字符")
    print(f"  包含v51: {'v51' in content}")
    print(f"  包含v50.9: {'v50.9' in content}")
    
    # 统计<script>内的大括号
    script_matches = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    total_open = 0
    total_close = 0
    for s in script_matches:
        total_open += s.count('{')
        total_close += s.count('}')
    
    print(f"  大括号: {{ {total_open}, }} {total_close}")
    if total_open == total_close:
        print("  ✓ 大括号配对正确")
    else:
        print(f"  ✗ 大括号不配对，相差 {abs(total_open - total_close)} 个")
    
    # 检查附表数量
    func_match = re.search(r'function buildSingleAttachHTML\(task, dateStr, attNum\) \{', content)
    if func_match:
        func_start = func_match.start()
        depth = 0
        pos = func_match.end() - 1
        for i in range(pos, len(content)):
            if content[i] == '{':
                depth += 1
            elif content[i] == '}':
                depth -= 1
                if depth == 0:
                    func_end = i
                    break
        
        func = content[func_start:func_end+1]
        att_count = len(re.findall(r'attNum === \d+', func))
        print(f"  附表数量: {att_count} 个")
        if att_count == 7:
            print("  ✓ 附表数量正确（7个）")
        else:
            print(f"  ✗ 附表数量不对，应为7个")
    
    return total_open == total_close

def main():
    base_dir = '/app/data/所有对话/主对话/weite-pro-temp/'
    cn_file = base_dir + '威特电梯厂检调试记录单v2.html'
    en_file = base_dir + 'factory-inspection-v2.html'
    
    # 处理中文文件
    process_file(cn_file, is_cn=True)
    
    # 处理英文文件
    process_file(en_file, is_cn=False)
    
    # 验证
    cn_ok = verify_file(cn_file)
    en_ok = verify_file(en_file)
    
    print("\n" + "="*60)
    if cn_ok and en_ok:
        print("✓ v51 升级完成，所有验证通过！")
    else:
        print("✗ 存在验证失败")
    print("="*60)

if __name__ == '__main__':
    main()
