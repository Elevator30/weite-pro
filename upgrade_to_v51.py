#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
威特电梯厂检调试记录单 v50.9 -> v51 升级脚本
改动：
1. 版本号 v50.9 -> v51
2. buildCheckItemsHTML: 三栏布局从大table改为float独立布局
3. buildSingleAttachHTML附表1: table改为SVG底图+绝对定位div
"""

import re
import sys

def replace_version(content):
    """替换所有版本号 v50.9 -> v51"""
    # title
    content = content.replace('v50.9', 'v51')
    content = content.replace('V50.9', 'v51')
    # 注释
    content = content.replace(
        '<!-- v50.9: buildCheckItemsHTML和buildSingleAttachHTML改用纯table布局，移除所有flex/float，确保html2canvas正确渲染 -->',
        '<!-- v51: buildCheckItemsHTML三栏独立float布局;附表1SVG底图+绝对定位方案 -->'
    )
    return content


def replace_checkitems_layout(content):
    """
    修改buildCheckItemsHTML中的三栏布局：
    从大table布局改为三个float:left的div
    """
    # 找到要替换的三栏布局部分
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
        print("  ✗ 未找到三栏布局代码，尝试模糊匹配...")
        # 尝试模糊匹配
        pattern = r'  // 三栏布局.*?  h \+= \'</table>\';'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            content = content[:match.start()] + new_layout + content[match.end():]
            print("  ✓ 模糊匹配替换成功")
        else:
            print("  ✗ 模糊匹配也失败，跳过")
    return content


def build_attach1_svg_layout_cn():
    """
    生成附表1的SVG底图 + 绝对定位div方案（中文版）
    结构：
    - SVG绘制所有线条、表头文字、判断标准、灰色背景
    - 绝对定位div放置数据值和位置标签
    """
    return r"""
    // ========== 附表1: SVG底图 + 绝对定位方案 ==========
    h += buildAttachHeader('附表1  电梯门间隙、门锁啮合长度及地坎间距检验记录', '附表1');

    // 配置
    var svgW = 700;
    var rowH = 16;       // 数据行高度
    var headerRowH = [20, 20, 20, 24, 24, 18]; // 6行表头高度
    var leftColW = 60;   // 左侧位置标签列宽
    // 11个数据列宽度 (对应: 门地坎距离左/右, 门扇间隙值, 立柱门楣左/右, 地坎左/右, 门扇间施力间隙, 门刀与层门地坎, 门锁啮合, 滚轮与轿厢地坎)
    var dataColW = [42, 42, 42, 42, 42, 42, 42, 50, 56, 56, 56];

    // 计算列的x坐标
    var colX = [leftColW];
    for (var dc = 0; dc < dataColW.length; dc++) {
      colX.push(colX[colX.length-1] + dataColW[dc]);
    }
    var totalW = colX[colX.length-1];

    // 计算行的y坐标
    var rowY = [0];
    for (var hr = 0; hr < headerRowH.length; hr++) {
      rowY.push(rowY[rowY.length-1] + headerRowH[hr]);
    }
    var dataStartY = rowY[rowY.length-1];
    var dataRows = 17; // 轿门1/2 + 15层
    for (var dr = 0; dr < dataRows; dr++) {
      rowY.push(rowY[rowY.length-1] + rowH);
    }
    var totalH = rowY[rowY.length-1];

    // 生成SVG
    var svg = '<svg width="' + totalW + '" height="' + totalH + '" xmlns="http://www.w3.org/2000/svg" style="display:block;">';

    // === 灰色背景 (表头部分) ===
    // 表头3行灰色
    svg += '<rect x="0" y="0" width="' + totalW + '" height="' + (rowY[3]) + '" fill="#f0f0f0"/>';
    // 判断标准行浅灰
    svg += '<rect x="0" y="' + rowY[3] + '" width="' + totalW + '" height="' + (rowY[5] - rowY[3]) + '" fill="#fafafa"/>';
    // 数据列表头行灰色
    svg += '<rect x="0" y="' + rowY[5] + '" width="' + totalW + '" height="' + (rowY[6] - rowY[5]) + '" fill="#f0f0f0"/>';
    // 第一列(位置列)数据区灰色
    svg += '<rect x="0" y="' + rowY[6] + '" width="' + leftColW + '" height="' + (totalH - rowY[6]) + '" fill="#f0f0f0"/>';

    // === 竖线 ===
    svg += '<line x1="0" y1="0" x2="0" y2="' + totalH + '" stroke="#000" stroke-width="1"/>';
    for (var vx = 0; vx < colX.length; vx++) {
      svg += '<line x1="' + colX[vx] + '" y1="0" x2="' + colX[vx] + '" y2="' + totalH + '" stroke="#000" stroke-width="1"/>';
    }
    svg += '<line x1="' + totalW + '" y1="0" x2="' + totalW + '" y2="' + totalH + '" stroke="#000" stroke-width="1"/>';

    // === 横线 ===
    // 顶线
    svg += '<line x1="0" y1="0" x2="' + totalW + '" y2="0" stroke="#000" stroke-width="1"/>';
    // 所有行底线
    for (var hy = 0; hy < rowY.length; hy++) {
      svg += '<line x1="0" y1="' + rowY[hy] + '" x2="' + totalW + '" y2="' + rowY[hy] + '" stroke="#000" stroke-width="1"/>';
    }
    // 底线
    svg += '<line x1="0" y1="' + totalH + '" x2="' + totalW + '" y2="' + totalH + '" stroke="#000" stroke-width="1"/>';

    // === 表头行1文字 (合并单元格) ===
    var midY1 = rowY[0] + headerRowH[0]/2;
    svg += '<text x="' + (leftColW/2) + '" y="' + (midY1 + 3) + '" text-anchor="middle" font-size="8px" font-weight="bold" font-family="sans-serif">检验项目</text>';
    svg += '<text x="' + (leftColW/2) + '" y="' + (midY1 + 13) + '" text-anchor="middle" font-size="8px" font-weight="bold" font-family="sans-serif">编号与内容</text>';

    // A1.2.7.1 (2列)
    var a1x = colX[0] + (colX[2]-colX[0])/2;
    svg += '<text x="' + a1x + '" y="' + (midY1 + 3) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.1</text>';

    // A1.2.7.2门间隙 (6列: 门扇间隙1列 + 立柱门楣2列 + 地坎2列 + 施力间隙1列 = 6列)
    // 列索引: 2=门扇间间隙, 3-4=立柱门楣, 5-6=地坎, 7=施力间隙
    var gapX = colX[2] + (colX[8]-colX[2])/2;
    svg += '<text x="' + gapX + '" y="' + (midY1 + 3) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.2门间隙</text>';

    // 门锁啮合长度 (第9列)
    var lockX = colX[8] + dataColW[8]/2;
    // 跨3行
    svg += '<text x="' + lockX + '" y="' + (rowY[0] + (rowY[3]-rowY[0])/2 - 3) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.8(2)</text>';
    svg += '<text x="' + lockX + '" y="' + (rowY[0] + (rowY[3]-rowY[0])/2 + 5) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">门锁啮合</text>';
    svg += '<text x="' + lockX + '" y="' + (rowY[0] + (rowY[3]-rowY[0])/2 + 13) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">长度</text>';

    // A1.2.7.10 (2列)
    var a10x = colX[9] + (colX[11]-colX[9])/2;
    svg += '<text x="' + a10x + '" y="' + (midY1 + 3) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.10</text>';

    // === 表头行2 ===
    var midY2 = rowY[1] + headerRowH[1]/2;
    // 门地坎距离 (跨2行: 行1-行2的前2列, 但实际是行2-行3)
    // A1.2.7.2(1) 跨5列 (门扇间隙+立柱门楣2+地坎2 = 5列? 不对，重新看结构)
    // 实际: 门扇间间隙1列 + 立柱门楣2列 + 地坎2列 = 5列 (列索引2-6)
    var a21x = colX[2] + (colX[7]-colX[2])/2;
    svg += '<text x="' + a21x + '" y="' + (midY2 + 3) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.2(1)</text>';

    // A1.2.7.2(2) 门扇间施力间隙 (列7)
    var forceX = colX[7] + dataColW[7]/2;
    svg += '<text x="' + forceX + '" y="' + (rowY[1] + (rowY[3]-rowY[1])/2 - 3) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">A1.2.7.2(2)</text>';
    svg += '<text x="' + forceX + '" y="' + (rowY[1] + (rowY[3]-rowY[1])/2 + 5) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">门扇间</text>';
    svg += '<text x="' + forceX + '" y="' + (rowY[1] + (rowY[3]-rowY[1])/2 + 13) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">施力间隙</text>';

    // 轿门门刀与层门地坎间隙 (列9)
    var knifeX = colX[9] + dataColW[9]/2;
    svg += '<text x="' + knifeX + '" y="' + (rowY[1] + (rowY[3]-rowY[1])/2 - 3) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">轿门门刀与</text>';
    svg += '<text x="' + knifeX + '" y="' + (rowY[1] + (rowY[3]-rowY[1])/2 + 5) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">层门地坎间隙</text>';

    // 层门门锁滚轮与轿厢地坎间隙 (列10)
    var rollerX = colX[10] + dataColW[10]/2;
    svg += '<text x="' + rollerX + '" y="' + (rowY[1] + (rowY[3]-rowY[1])/2 - 3) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">层门门锁滚轮与</text>';
    svg += '<text x="' + rollerX + '" y="' + (rowY[1] + (rowY[3]-rowY[1])/2 + 5) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">轿厢地坎间隙</text>';

    // === 表头行3 (子列标题) ===
    var midY3 = rowY[2] + headerRowH[2]/2 + 2;
    // 左/右 (前2列)
    svg += '<text x="' + (colX[0] + dataColW[0]/2) + '" y="' + midY3 + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">左</text>';
    svg += '<text x="' + (colX[1] + dataColW[1]/2) + '" y="' + midY3 + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">右</text>';
    // 门扇间间隙 (列2)
    svg += '<text x="' + (colX[2] + dataColW[2]/2) + '" y="' + midY3 + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">门扇间</text>';
    svg += '<text x="' + (colX[2] + dataColW[2]/2) + '" y="' + (midY3 + 9) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">间隙</text>';
    // 门扇与立柱、门楣间隙 (列3-4)
    var col34mid = colX[3] + (colX[5]-colX[3])/2;
    svg += '<text x="' + col34mid + '" y="' + (midY3 - 4) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">门扇与立柱、</text>';
    svg += '<text x="' + col34mid + '" y="' + (midY3 + 5) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">门楣间隙</text>';
    svg += '<text x="' + (colX[3] + dataColW[3]/2) + '" y="' + (midY3 + 14) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">左</text>';
    svg += '<text x="' + (colX[4] + dataColW[4]/2) + '" y="' + (midY3 + 14) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">右</text>';
    // 门扇与地坎间隙 (列5-6)
    var col56mid = colX[5] + (colX[7]-colX[5])/2;
    svg += '<text x="' + col56mid + '" y="' + (midY3 - 4) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">门扇与</text>';
    svg += '<text x="' + col56mid + '" y="' + (midY3 + 5) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">地坎间隙</text>';
    svg += '<text x="' + (colX[5] + dataColW[5]/2) + '" y="' + (midY3 + 14) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">左</text>';
    svg += '<text x="' + (colX[6] + dataColW[6]/2) + '" y="' + (midY3 + 14) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">右</text>';

    // === 判断标准行 (2行高) ===
    var judgeMidY = rowY[3] + (rowY[5]-rowY[3])/2;
    // 判断标准标签
    svg += '<text x="' + (leftColW/2) + '" y="' + (judgeMidY + 3) + '" text-anchor="middle" font-size="6.5px" font-family="sans-serif">判断标准</text>';

    // 门地坎距离标准 (≤35mm...)
    var std1x = colX[0] + (colX[2]-colX[0])/2;
    svg += '<text x="' + std1x + '" y="' + (judgeMidY - 8) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">≤35mm</text>';
    svg += '<text x="' + std1x + '" y="' + (judgeMidY) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">左右偏差</text>';
    svg += '<text x="' + std1x + '" y="' + (judgeMidY + 8) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">小于1/1000</text>';

    // 门间隙标准 (乘客电梯3~6mm...)
    var std2x = colX[2] + (colX[7]-colX[2])/2;
    svg += '<text x="' + std2x + '" y="' + (judgeMidY - 8) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">乘客电梯：3~6mm</text>';
    svg += '<text x="' + std2x + '" y="' + (judgeMidY) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">载货电梯：3~10mm</text>';
    svg += '<text x="' + std2x + '" y="' + (judgeMidY + 8) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">左右偏差不超过1mm</text>';

    // 施力间隙标准 (旁开门≤30, 中分门≤45)
    svg += '<text x="' + forceX + '" y="' + (judgeMidY - 4) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">旁开门：≤30</text>';
    svg += '<text x="' + forceX + '" y="' + (judgeMidY + 6) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">中分门：≤45</text>';

    // 门锁啮合标准 (≥7mm)
    svg += '<text x="' + lockX + '" y="' + (judgeMidY + 3) + '" text-anchor="middle" font-size="7px" font-family="sans-serif">≥7mm</text>';

    // A1.2.7.10标准 (≥5mm)
    svg += '<text x="' + a10x + '" y="' + (judgeMidY + 3) + '" text-anchor="middle" font-size="7px" font-family="sans-serif">≥5mm</text>';

    // === 数据列表头行 ===
    var dataHdrY = rowY[5] + headerRowH[5]/2 + 2;
    svg += '<text x="' + (leftColW/2) + '" y="' + dataHdrY + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">位置</text>';
    var hdrLabels = ['左','右','值','左','右','左','右','值','值','值','值'];
    // 实际: 门地坎距离有左/右，然后是门扇间隙值，立柱门楣左/右，地坎左/右，施力间隙值，啮合值，门刀值，滚轮值
    // 共11列
    for (var hl = 0; hl < hdrLabels.length && hl < dataColW.length; hl++) {
      svg += '<text x="' + (colX[hl] + dataColW[hl]/2) + '" y="' + dataHdrY + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">' + hdrLabels[hl] + '</text>';
    }

    // "检验位置及测量数据" 竖排文字（左侧）
    var vertTextY = rowY[6] + (totalH - rowY[6])/2;
    svg += '<text x="' + (leftColW/2) + '" y="' + (vertTextY - 15) + '" text-anchor="middle" font-size="8px" font-weight="bold" font-family="sans-serif">检验位置</text>';
    svg += '<text x="' + (leftColW/2) + '" y="' + (vertTextY - 3) + '" text-anchor="middle" font-size="8px" font-weight="bold" font-family="sans-serif">及测量</text>';
    svg += '<text x="' + (leftColW/2) + '" y="' + (vertTextY + 9) + '" text-anchor="middle" font-size="8px" font-weight="bold" font-family="sans-serif">数据</text>';

    svg += '</svg>';

    // 外容器：相对定位
    h += '<div style="position:relative;width:' + totalW + 'px;font-size:7px;font-family:sans-serif;">';
    // SVG底图
    h += svg;

    // 位置标签 + 数据单元格（绝对定位div）
    var posList = ['轿门1', '轿门2'];
    for (var fl = 1; fl <= 15; fl++) posList.push(fl + '层');

    for (var ri = 0; ri < posList.length; ri++) {
      var rowTop = dataStartY + ri * rowH;
      // 位置标签
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


def replace_attach1_cn(content):
    """替换中文版附表1的table布局为SVG方案"""
    # 找到if (attNum === 1)块并替换
    pattern = r'  if \(attNum === 1\) \{.*?    h \+= buildAttachFooter\(\'附表1\'\);\n  \}'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        new_block = build_attach1_svg_layout_cn()
        content = content[:match.start()] + new_block + content[match.end():]
        print("  ✓ 附表1 SVG方案替换成功（中文版）")
    else:
        print("  ✗ 未找到附表1代码块（中文版）")
    return content


def build_attach1_svg_layout_en():
    """
    生成附表1的SVG底图 + 绝对定位div方案（英文版）
    """
    return r"""
    // ========== Attach 1: SVG background + absolute positioning ==========
    h += buildAttachHeader('Appendix 1  Elevator Door Gap, Door Lock Engagement Length & Sill Distance Inspection Record', 'Appendix 1');

    // Configuration
    var svgW = 700;
    var rowH = 16;
    var headerRowH = [20, 20, 20, 24, 24, 18];
    var leftColW = 60;
    var dataColW = [42, 42, 42, 42, 42, 42, 42, 50, 56, 56, 56];

    // Calculate column X positions
    var colX = [leftColW];
    for (var dc = 0; dc < dataColW.length; dc++) {
      colX.push(colX[colX.length-1] + dataColW[dc]);
    }
    var totalW = colX[colX.length-1];

    // Calculate row Y positions
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

    // Generate SVG
    var svg = '<svg width="' + totalW + '" height="' + totalH + '" xmlns="http://www.w3.org/2000/svg" style="display:block;">';

    // Gray backgrounds
    svg += '<rect x="0" y="0" width="' + totalW + '" height="' + (rowY[3]) + '" fill="#f0f0f0"/>';
    svg += '<rect x="0" y="' + rowY[3] + '" width="' + totalW + '" height="' + (rowY[5] - rowY[3]) + '" fill="#fafafa"/>';
    svg += '<rect x="0" y="' + rowY[5] + '" width="' + totalW + '" height="' + (rowY[6] - rowY[5]) + '" fill="#f0f0f0"/>';
    svg += '<rect x="0" y="' + rowY[6] + '" width="' + leftColW + '" height="' + (totalH - rowY[6]) + '" fill="#f0f0f0"/>';

    // Vertical lines
    svg += '<line x1="0" y1="0" x2="0" y2="' + totalH + '" stroke="#000" stroke-width="1"/>';
    for (var vx = 0; vx < colX.length; vx++) {
      svg += '<line x1="' + colX[vx] + '" y1="0" x2="' + colX[vx] + '" y2="' + totalH + '" stroke="#000" stroke-width="1"/>';
    }
    svg += '<line x1="' + totalW + '" y1="0" x2="' + totalW + '" y2="' + totalH + '" stroke="#000" stroke-width="1"/>';

    // Horizontal lines
    svg += '<line x1="0" y1="0" x2="' + totalW + '" y2="0" stroke="#000" stroke-width="1"/>';
    for (var hy = 0; hy < rowY.length; hy++) {
      svg += '<line x1="0" y1="' + rowY[hy] + '" x2="' + totalW + '" y2="' + rowY[hy] + '" stroke="#000" stroke-width="1"/>';
    }
    svg += '<line x1="0" y1="' + totalH + '" x2="' + totalW + '" y2="' + totalH + '" stroke="#000" stroke-width="1"/>';

    // === Header Row 1 ===
    var midY1 = rowY[0] + headerRowH[0]/2;
    svg += '<text x="' + (leftColW/2) + '" y="' + (midY1 + 3) + '" text-anchor="middle" font-size="8px" font-weight="bold" font-family="sans-serif">Inspection Item</text>';
    svg += '<text x="' + (leftColW/2) + '" y="' + (midY1 + 13) + '" text-anchor="middle" font-size="8px" font-weight="bold" font-family="sans-serif">No. &amp; Content</text>';

    // A1.2.7.1 (2 cols)
    var a1x = colX[0] + (colX[2]-colX[0])/2;
    svg += '<text x="' + a1x + '" y="' + (midY1 + 3) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.1</text>';

    // A1.2.7.2 Door Gap (6 cols)
    var gapX = colX[2] + (colX[8]-colX[2])/2;
    svg += '<text x="' + gapX + '" y="' + (midY1 + 3) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.2 Door Gap</text>';

    // Door lock engagement length (col 8)
    var lockX = colX[8] + dataColW[8]/2;
    svg += '<text x="' + lockX + '" y="' + (rowY[0] + (rowY[3]-rowY[0])/2 - 3) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.8(2)</text>';
    svg += '<text x="' + lockX + '" y="' + (rowY[0] + (rowY[3]-rowY[0])/2 + 5) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">Door Lock</text>';
    svg += '<text x="' + lockX + '" y="' + (rowY[0] + (rowY[3]-rowY[0])/2 + 13) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">Engagement</text>';

    // A1.2.7.10 (2 cols)
    var a10x = colX[9] + (colX[11]-colX[9])/2;
    svg += '<text x="' + a10x + '" y="' + (midY1 + 3) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.10</text>';

    // === Header Row 2 ===
    var midY2 = rowY[1] + headerRowH[1]/2;
    // Door sill distance label (rows 1-2 merged for first 2 cols, but text is on row 2 spanning cols 0-1)
    // Actually: "门地坎距离" spans rows 1-2 of the first 2 cols in the original
    // But we have A1.2.7.1 on row1, and 门地坎距离 on rows 2-3
    // Let me restructure: row1 has A1.2.7.1, rows 2-3 have "门地坎距离"

    // A1.2.7.2(1) spans 5 cols
    var a21x = colX[2] + (colX[7]-colX[2])/2;
    svg += '<text x="' + a21x + '" y="' + (midY2 + 3) + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">A1.2.7.2(1)</text>';

    // A1.2.7.2(2) Force gap (col 7)
    var forceX = colX[7] + dataColW[7]/2;
    svg += '<text x="' + forceX + '" y="' + (rowY[1] + (rowY[3]-rowY[1])/2 - 3) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">A1.2.7.2(2)</text>';
    svg += '<text x="' + forceX + '" y="' + (rowY[1] + (rowY[3]-rowY[1])/2 + 5) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">Door Panel</text>';
    svg += '<text x="' + forceX + '" y="' + (rowY[1] + (rowY[3]-rowY[1])/2 + 13) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">Force Gap</text>';

    // Door vane &amp; landing sill gap (col 9)
    var knifeX = colX[9] + dataColW[9]/2;
    svg += '<text x="' + knifeX + '" y="' + (rowY[1] + (rowY[3]-rowY[1])/2 - 3) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">Door Vane &amp;</text>';
    svg += '<text x="' + knifeX + '" y="' + (rowY[1] + (rowY[3]-rowY[1])/2 + 5) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">Landing Sill</text>';

    // Door lock roller &amp; car sill gap (col 10)
    var rollerX = colX[10] + dataColW[10]/2;
    svg += '<text x="' + rollerX + '" y="' + (rowY[1] + (rowY[3]-rowY[1])/2 - 3) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">Lock Roller &amp;</text>';
    svg += '<text x="' + rollerX + '" y="' + (rowY[1] + (rowY[3]-rowY[1])/2 + 5) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">Car Sill Gap</text>';

    // === Header Row 3 (sub-labels) ===
    var midY3 = rowY[2] + headerRowH[2]/2 + 2;
    // Left/Right (first 2 cols)
    svg += '<text x="' + (colX[0] + dataColW[0]/2) + '" y="' + midY3 + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">L</text>';
    svg += '<text x="' + (colX[1] + dataColW[1]/2) + '" y="' + midY3 + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">R</text>';
    // Door panel gap (col 2)
    svg += '<text x="' + (colX[2] + dataColW[2]/2) + '" y="' + (midY3 - 4) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">Panel</text>';
    svg += '<text x="' + (colX[2] + dataColW[2]/2) + '" y="' + (midY3 + 5) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">Gap</text>';
    // Panel &amp; jamb/header gap (cols 3-4)
    var col34mid = colX[3] + (colX[5]-colX[3])/2;
    svg += '<text x="' + col34mid + '" y="' + (midY3 - 4) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">Jamb/Header</text>';
    svg += '<text x="' + col34mid + '" y="' + (midY3 + 5) + '" text-anchor="middle" font-size="6px" font-weight="bold" font-family="sans-serif">Gap</text>';
    svg += '<text x="' + (colX[3] + dataColW[3]/2) + '" y="' + (midY3 + 14) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">L</text>';
    svg += '<text x="' + (colX[4] + dataColW[4]/2) + '" y="' + (midY3 + 14) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">R</text>';
    // Panel &amp; sill gap (cols 5-6)
    var col56mid = colX[5] + (colX[7]-colX[5])/2;
    svg += '<text x="' + col56mid + '" y="' + (midY3 - 4) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">Sill Gap</text>';
    svg += '<text x="' + (colX[5] + dataColW[5]/2) + '" y="' + (midY3 + 14) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">L</text>';
    svg += '<text x="' + (colX[6] + dataColW[6]/2) + '" y="' + (midY3 + 14) + '" text-anchor="middle" font-size="6.5px" font-weight="bold" font-family="sans-serif">R</text>';

    // === Judgment Standard Rows ===
    var judgeMidY = rowY[3] + (rowY[5]-rowY[3])/2;
    svg += '<text x="' + (leftColW/2) + '" y="' + (judgeMidY + 3) + '" text-anchor="middle" font-size="6.5px" font-family="sans-serif">Standard</text>';

    // Door sill distance standard
    var std1x = colX[0] + (colX[2]-colX[0])/2;
    svg += '<text x="' + std1x + '" y="' + (judgeMidY - 8) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">≤35mm</text>';
    svg += '<text x="' + std1x + '" y="' + (judgeMidY) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">L/R dev</text>';
    svg += '<text x="' + std1x + '" y="' + (judgeMidY + 8) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">&lt; 1/1000</text>';

    // Door gap standard
    var std2x = colX[2] + (colX[7]-colX[2])/2;
    svg += '<text x="' + std2x + '" y="' + (judgeMidY - 8) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">Passenger: 3~6mm</text>';
    svg += '<text x="' + std2x + '" y="' + (judgeMidY) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">Freight: 3~10mm</text>';
    svg += '<text x="' + std2x + '" y="' + (judgeMidY + 8) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">L/R dev ≤1mm</text>';

    // Force gap standard
    svg += '<text x="' + forceX + '" y="' + (judgeMidY - 4) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">Side: ≤30</text>';
    svg += '<text x="' + forceX + '" y="' + (judgeMidY + 6) + '" text-anchor="middle" font-size="6px" font-family="sans-serif">Center: ≤45</text>';

    // Lock engagement standard
    svg += '<text x="' + lockX + '" y="' + (judgeMidY + 3) + '" text-anchor="middle" font-size="7px" font-family="sans-serif">≥7mm</text>';

    // A1.2.7.10 standard
    svg += '<text x="' + a10x + '" y="' + (judgeMidY + 3) + '" text-anchor="middle" font-size="7px" font-family="sans-serif">≥5mm</text>';

    // === Data header row ===
    var dataHdrY = rowY[5] + headerRowH[5]/2 + 2;
    svg += '<text x="' + (leftColW/2) + '" y="' + dataHdrY + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">Pos</text>';
    var hdrLabels = ['L','R','Val','L','R','L','R','Val','Val','Val','Val'];
    for (var hl = 0; hl < hdrLabels.length && hl < dataColW.length; hl++) {
      svg += '<text x="' + (colX[hl] + dataColW[hl]/2) + '" y="' + dataHdrY + '" text-anchor="middle" font-size="7px" font-weight="bold" font-family="sans-serif">' + hdrLabels[hl] + '</text>';
    }

    // Vertical text for inspection position
    var vertTextY = rowY[6] + (totalH - rowY[6])/2;
    svg += '<text x="' + (leftColW/2) + '" y="' + (vertTextY - 15) + '" text-anchor="middle" font-size="8px" font-weight="bold" font-family="sans-serif">Position</text>';
    svg += '<text x="' + (leftColW/2) + '" y="' + (vertTextY - 3) + '" text-anchor="middle" font-size="8px" font-weight="bold" font-family="sans-serif">&amp;</text>';
    svg += '<text x="' + (leftColW/2) + '" y="' + (vertTextY + 9) + '" text-anchor="middle" font-size="8px" font-weight="bold" font-family="sans-serif">Data</text>';

    svg += '</svg>';

    // Container: relative positioning
    h += '<div style="position:relative;width:' + totalW + 'px;font-size:7px;font-family:sans-serif;">';
    h += svg;

    // Position labels + data cells (absolute positioned divs)
    var posList = ['Car Door 1', 'Car Door 2'];
    for (var fl = 1; fl <= 15; fl++) posList.push('F' + fl);

    for (var ri = 0; ri < posList.length; ri++) {
      var rowTop = dataStartY + ri * rowH;
      // Position label
      h += '<div style="position:absolute;left:0;top:' + rowTop + 'px;width:' + leftColW + 'px;height:' + rowH + 'px;line-height:' + rowH + 'px;text-align:center;font-size:7px;overflow:hidden;">';
      h += posList[ri];
      h += '</div>';

      // 11 data cells
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


def replace_attach1_en(content):
    """替换英文版附表1的table布局为SVG方案"""
    pattern = r'  if \(attNum === 1\) \{.*?    h \+= buildAttachFooter\([^\)]+\);\n  \}'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        # 检查是否是附表1的块
        block = content[match.start():match.end()]
        if 'Appendix 1' in block or '附表1' in block or 'Door Gap' in block or '门间隙' in block:
            new_block = build_attach1_svg_layout_en()
            content = content[:match.start()] + new_block + content[match.end():]
            print("  ✓ 附表1 SVG方案替换成功（英文版）")
        else:
            print("  ✗ 找到的不是附表1的块")
    else:
        print("  ✗ 未找到附表1代码块（英文版）")
    return content


def replace_checkitems_layout_en(content):
    """修改英文版buildCheckItemsHTML的三栏布局"""
    # 英文版的布局代码和中文版一样，只是内容不同
    return replace_checkitems_layout(content)


def process_file(filepath, is_cn=True):
    """处理单个文件"""
    print(f"\n处理文件: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"  原始大小: {len(content)} 字符")

    # 1. 版本号替换
    content = replace_version(content)
    print("  ✓ 版本号替换完成")

    # 2. 记录表三栏布局修改
    content = replace_checkitems_layout(content)

    # 3. 附表1 SVG方案
    if is_cn:
        content = replace_attach1_cn(content)
    else:
        content = replace_attach1_en(content)

    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  最终大小: {len(content)} 字符")
    print(f"  ✓ 文件已保存")
    return content


def verify_file(filepath):
    """验证文件"""
    print(f"\n验证文件: {filepath}")

    # 检查文件可读且非空
    import subprocess
    result = subprocess.run(
        ['node', '-e', f"const fs = require('fs'); const c = fs.readFileSync('{filepath}','utf8'); console.log('文件大小:', c.length, '字节'); console.log('包含v51:', c.includes('v51')); console.log('包含v50.9:', c.includes('v50.9'));"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"  ✓ {result.stdout.strip()}")
    else:
        print(f"  ✗ node读取失败: {result.stderr}")
        return False

    # 检查大括号配对
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 只检查<script>标签内的JS
    script_matches = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    total_open = 0
    total_close = 0
    for s in script_matches:
        total_open += s.count('{')
        total_close += s.count('}')

    print(f"  大括号统计: {{ {total_open} 个, }} {total_close} 个")
    if total_open == total_close:
        print("  ✓ 大括号配对正确")
    else:
        print(f"  ✗ 大括号不配对: 相差 {abs(total_open - total_close)} 个")

    return total_open == total_close


def main():
    base_dir = '/app/data/所有对话/主对话/weite-pro-temp/'
    cn_file = base_dir + '威特电梯厂检调试记录单v2.html'
    en_file = base_dir + 'factory-inspection-v2.html'

    # 先备份
    import shutil
    shutil.copy(cn_file, cn_file + '.v509_backup')
    shutil.copy(en_file, en_file + '.v509_backup')
    print("已创建v50.9备份")

    # 处理中文文件
    process_file(cn_file, is_cn=True)

    # 处理英文文件
    process_file(en_file, is_cn=False)

    # 验证
    cn_ok = verify_file(cn_file)
    en_ok = verify_file(en_file)

    print("\n" + "="*60)
    if cn_ok and en_ok:
        print("✓ 所有文件验证通过！")
    else:
        print("✗ 存在验证失败的文件")
    print("="*60)


if __name__ == '__main__':
    main()
