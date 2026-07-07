#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 buildCheckItemsHTML 和 buildSingleAttachHTML 中的 flex/float 布局
全部替换为纯 table 布局，确保 html2canvas 正确渲染。
"""

import re
import sys

def find_func_end(lines, start_idx):
    """从start_idx开始，找到函数结束的右花括号行号（0-indexed）"""
    depth = 0
    started = False
    for i in range(start_idx, len(lines)):
        for ch in lines[i]:
            if ch == '{':
                depth += 1
                started = True
            elif ch == '}':
                depth -= 1
        if started and depth == 0:
            return i
    return None

def replace_buildCheckItemsHTML(lines):
    """替换 buildCheckItemsHTML 中的 flex 布局为 table 布局"""
    
    # 找到函数起始行
    func_start = None
    for i, line in enumerate(lines):
        if 'function buildCheckItemsHTML(' in line:
            func_start = i
            break
    if func_start is None:
        print("ERROR: buildCheckItemsHTML not found")
        return False
    
    func_end = find_func_end(lines, func_start)
    print(f"buildCheckItemsHTML: line {func_start+1} - {func_end+1}")
    
    # 提取函数内容
    func_lines = lines[func_start:func_end+1]
    
    new_func_lines = []
    
    # 逐行扫描，找到需要替换的部分
    i = 0
    while i < len(func_lines):
        line = func_lines[i]
        
        # === 替换1: 页眉 flex 布局 ===
        # 原代码: h += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">';
        # ... 3行内容 ...
        # h += '</div>';
        if 'display:flex;justify-content:space-between;align-items:center' in line and 'margin-bottom:4px' in line and 'h +=' in line:
            print(f"  替换页眉flex布局 (函数内第{i+1}行)")
            # 跳过这行和后续3行内容 + 闭合div，替换为table布局
            # 先收集后续内容直到闭合div
            j = i + 1
            while j < len(func_lines):
                if "h += '</div>'" in func_lines[j]:
                    break
                j += 1
            
            # 新的table布局页眉
            new_lines = [
                "  // 页眉 - table三列布局（左logo/中标题/右产品编号）\n",
                "  h += '<table style=\"width:100%;border-collapse:collapse;table-layout:fixed;margin-bottom:4px;\">';\n",
                "  h += '<colgroup><col style=\"width:20%\"><col style=\"width:60%\"><col style=\"width:20%\"></colgroup>';\n",
                "  h += '<tr>';\n",
                "  h += '<td style=\"padding:0;text-align:left;vertical-align:middle;\"><img src=\"' + logoBase64 + '\" style=\"height:24px;width:auto;\"></td>';\n",
                "  h += '<td style=\"padding:0;text-align:center;vertical-align:middle;font-size:14px;font-weight:bold;\">厂检调试记录单</td>';\n",
                "  h += '<td style=\"padding:0;text-align:right;vertical-align:middle;font-size:9px;\">产品编号：' + escHtml(task.prodNo||'') + '</td>';\n",
                "  h += '</tr>';\n",
                "  h += '</table>';\n",
            ]
            new_func_lines.extend(new_lines)
            i = j + 1  # 跳过闭合div行
            continue
        
        # === 替换2: 三栏 flex 布局 ===
        # 原代码: h += '<div style="display:flex;width:100%;gap:4px;">';
        # ... 3个div列 ...
        # h += '</div>';
        if 'display:flex;width:100%' in line and 'gap' in line and 'h +=' in line:
            print(f"  替换三栏flex布局 (函数内第{i+1}行)")
            # 找到三栏内容结束的闭合div
            j = i + 1
            col_end_count = 0
            while j < len(func_lines):
                if "h += '</div>'" in func_lines[j]:
                    col_end_count += 1
                    if col_end_count == 4:  # 3个列div + 1个外层div
                        break
                j += 1
            
            # 新的table三栏布局
            new_lines = [
                "  // 三栏布局 - table三列\n",
                "  h += '<table style=\"width:100%;border-collapse:collapse;table-layout:fixed;\">';\n",
                "  h += '<colgroup><col style=\"width:33.33%\"><col style=\"width:33.33%\"><col style=\"width:33.34%\"></colgroup>';\n",
                "  h += '<tr>';\n",
                "  h += '<td style=\"padding:0 2px 0 0;vertical-align:top;\">' + buildColumn(pageConfig.col1) + '</td>';\n",
                "  h += '<td style=\"padding:0 2px;vertical-align:top;\">' + buildColumn(pageConfig.col2) + '</td>';\n",
                "  h += '<td style=\"padding:0 0 0 2px;vertical-align:top;\">' + buildColumn(pageConfig.col3) + '</td>';\n",
                "  h += '</tr>';\n",
                "  h += '</table>';\n",
            ]
            new_func_lines.extend(new_lines)
            i = j + 1
            continue
        
        new_func_lines.append(line)
        i += 1
    
    # 替换原函数
    lines[func_start:func_end+1] = new_func_lines
    print(f"  替换后函数行数: {len(new_func_lines)}")
    return True

def replace_buildSingleAttachHTML(lines):
    """替换 buildSingleAttachHTML 中的 flex 布局为 table 布局"""
    
    # 找到函数起始行
    func_start = None
    for i, line in enumerate(lines):
        if 'function buildSingleAttachHTML(' in line:
            func_start = i
            break
    if func_start is None:
        print("ERROR: buildSingleAttachHTML not found")
        return False
    
    func_end = find_func_end(lines, func_start)
    print(f"buildSingleAttachHTML: line {func_start+1} - {func_end+1}")
    
    func_lines = lines[func_start:func_end+1]
    new_func_lines = []
    
    i = 0
    while i < len(func_lines):
        line = func_lines[i]
        
        # === 替换3: buildAttachHeader 内的 flex 布局 ===
        # h += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;border-bottom:1px solid #000;padding-bottom:3px;">';
        if ('display:flex;justify-content:space-between;align-items:center' in line 
            and 'border-bottom' in line and 'buildAttachHeader' not in line):
            # 确认是在buildAttachHeader内部
            # 往前找几行确认
            is_in_header = False
            for k in range(max(0, i-20), i):
                if 'function buildAttachHeader(' in func_lines[k]:
                    is_in_header = True
                    break
            if is_in_header:
                print(f"  替换buildAttachHeader内的flex布局 (函数内第{i+1}行)")
                # 找到闭合div
                j = i + 1
                while j < len(func_lines):
                    if "h += '</div>'" in func_lines[j]:
                        break
                    j += 1
                
                new_lines = [
                    "    // 顶部 - table三列布局\n",
                    "    h += '<table style=\"width:100%;border-collapse:collapse;table-layout:fixed;margin-bottom:4px;border-bottom:1px solid #000;padding-bottom:3px;\">';\n",
                    "    h += '<colgroup><col style=\"width:20%\"><col style=\"width:60%\"><col style=\"width:20%\"></colgroup>';\n",
                    "    h += '<tr>';\n",
                    "    h += '<td style=\"padding:0;text-align:left;vertical-align:middle;\"><img src=\"' + logoBase64 + '\" style=\"height:18px;width:auto;\"></td>';\n",
                    "    h += '<td style=\"padding:0;text-align:center;vertical-align:middle;font-weight:bold;font-size:11px;\">厂检调试记录单</td>';\n",
                    "    h += '<td style=\"padding:0;text-align:right;vertical-align:middle;font-size:7px;\">产品编号：' + esc(task.productNo || '') + '</td>';\n",
                    "    h += '</tr>';\n",
                    "    h += '</table>';\n",
                ]
                new_func_lines.extend(new_lines)
                i = j + 1
                continue
        
        # === 替换4: 附表4 左右两表 flex 布局 ===
        # h += '<div style="display:flex;gap:10px;width:100%;">';
        if 'display:flex;gap:10px;width:100%' in line and 'h +=' in line:
            print(f"  替换附表4左右flex布局 (函数内第{i+1}行)")
            
            # 找到整个flex块的结束（包括左右两个div和外层闭合）
            j = i + 1
            div_depth = 1  # 已经有一个外层div
            while j < len(func_lines) and div_depth > 0:
                if 'h += \'<div' in func_lines[j] or ('<div style=' in func_lines[j] and 'h +=' in func_lines[j]):
                    div_depth += 1
                if "h += '</div>'" in func_lines[j]:
                    div_depth -= 1
                j += 1
            
            # 现在我们需要提取左右两个表格的内容，重新包装为table两列
            # 先收集整个块的内容
            block_lines = func_lines[i:j]
            
            # 找到左表内容 (从第一个 <table 到 </table>)
            left_table_start = None
            left_table_end = None
            right_table_start = None
            right_table_end = None
            
            for k, bl in enumerate(block_lines):
                if '<table' in bl and left_table_start is None:
                    left_table_start = k
                if left_table_start is not None and '</table>' in bl and left_table_end is None:
                    left_table_end = k
                if left_table_end is not None and '<table' in bl and right_table_start is None:
                    right_table_start = k
                if right_table_start is not None and '</table>' in bl and right_table_end is None:
                    right_table_end = k
                    break
            
            if left_table_start and left_table_end and right_table_start and right_table_end:
                # 提取左右表的h +=行
                left_table_lines = block_lines[left_table_start:left_table_end+1]
                right_table_lines = block_lines[right_table_start:right_table_end+1]
                
                new_lines = [
                    "    // 左右两表并排 - table两列布局\n",
                    "    h += '<table style=\"width:100%;border-collapse:collapse;table-layout:fixed;\">';\n",
                    "    h += '<colgroup><col style=\"width:50%\"><col style=\"width:50%\"></colgroup>';\n",
                    "    h += '<tr>';\n",
                    "    h += '<td style=\"padding:0 5px 0 0;vertical-align:top;\">';\n",
                ]
                new_lines.extend(left_table_lines)
                new_lines.append("    h += '</td>';\n")
                new_lines.append("    h += '<td style=\"padding:0 0 0 5px;vertical-align:top;\">';\n")
                new_lines.extend(right_table_lines)
                new_lines.append("    h += '</td>';\n")
                new_lines.append("    h += '</tr>';\n")
                new_lines.append("    h += '</table>';\n")
                
                new_func_lines.extend(new_lines)
                i = j
                continue
            else:
                print(f"  WARNING: 未能找到附表4的左右表格")
        
        new_func_lines.append(line)
        i += 1
    
    lines[func_start:func_end+1] = new_func_lines
    print(f"  替换后函数行数: {len(new_func_lines)}")
    return True

def process_file(filepath):
    print(f"\n处理文件: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    original_len = len(lines)
    print(f"  原始行数: {original_len}")
    
    r1 = replace_buildCheckItemsHTML(lines)
    r2 = replace_buildSingleAttachHTML(lines)
    
    if not r1 or not r2:
        print("  ERROR: 替换失败，未写入文件")
        return False
    
    print(f"  替换后行数: {len(lines)}")
    
    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"  已写入: {filepath}")
    return True

if __name__ == '__main__':
    base_dir = '/app/data/所有对话/主对话/weite-pro-temp'
    
    files = [
        f'{base_dir}/威特电梯厂检调试记录单v2.html',
        f'{base_dir}/factory-inspection-v2.html',
    ]
    
    for f in files:
        process_file(f)
    
    print("\n全部完成！")
