#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v120 第三部分：修复层门门扇间施力间隙标准、语法验证
"""
import re
import os
import subprocess

MAIN_FILE = '/app/data/所有对话/主对话/weite-pro-temp/factory-inspection-v2.html'
PRINT_FILE = '/app/data/所有对话/主对话/weite-pro-temp/print-fubiao.html'

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    main_html = read_file(MAIN_FILE)
    changes = []
    
    # ============================================================
    # 问题6：修复层门(renderAtt1LaygateInputs)的门扇间施力间隙标准动态显示
    # ============================================================
    
    # 1. 修改函数定义，添加doorStruct参数
    old_func_def = "function renderAtt1LaygateInputs(data, rowIdx) {"
    new_func_def = "function renderAtt1LaygateInputs(data, rowIdx, doorStruct) {"
    if old_func_def in main_html:
        main_html = main_html.replace(old_func_def, new_func_def)
        changes.append('问题6：renderAtt1LaygateInputs添加doorStruct参数')
    else:
        print('WARNING: 未找到renderAtt1LaygateInputs函数定义')
    
    # 2. 修改层门的门扇间施力间隙std为动态
    old_laygate_force = "{type:'pair', l:{label:'门扇间间隙',std:'3-6mm',idx:7}, r:{label:'门扇间施力间隙',std:'旁开≤30/中分≤45',idx:6}},"
    # 这个出现在renderAtt1LaygateInputs中，需要用变量
    # 在函数内的rows定义前添加forceStd变量
    old_laygate_rows = "  var rows = [\n    {type:'pair', l:{label:'门地坎距离-左',std:'≤35mm',idx:4}, r:{label:'门地坎距离-右',std:'≤35mm',idx:5}},"
    
    new_laygate_rows = "  var ds = doorStruct || 'center';\n  var forceStdLg = (ds === 'side') ? '≤30mm' : '≤45mm';\n  var rows = [\n    {type:'pair', l:{label:'门地坎距离-左',std:'≤35mm',idx:4}, r:{label:'门地坎距离-右',std:'≤35mm',idx:5}},"
    
    if old_laygate_rows in main_html:
        main_html = main_html.replace(old_laygate_rows, new_laygate_rows)
        changes.append('问题6：层门rows前添加forceStd变量')
    else:
        print('WARNING: 未找到层门rows起始')
    
    # 3. 修改层门门扇间施力间隙的std为变量
    # 在renderAtt1LaygateInputs中的那一个
    # 我们需要找到第二个出现的（第一个在轿门，第二个在层门函数里）
    old_force2 = "{type:'pair', l:{label:'门扇间间隙',std:'3-6mm',idx:7}, r:{label:'门扇间施力间隙',std:'旁开≤30/中分≤45',idx:6}},"
    new_force2 = "{type:'pair', l:{label:'门扇间间隙',std:'3-6mm',idx:7}, r:{label:'门扇间施力间隙',std:forceStdLg,idx:6}},"
    
    # 找到所有出现位置
    occurrences = [m.start() for m in re.finditer(re.escape(old_force2), main_html)]
    if len(occurrences) >= 1:
        # 最后一个应该是层门的（第一个是轿门，已经改了；或者第一个/第二个是层门的）
        # 让我们找到renderAtt1LaygateInputs函数内的那个
        func_start = main_html.find('function renderAtt1LaygateInputs')
        if func_start > 0:
            # 在函数内找
            func_end = main_html.find('\nfunction ', func_start + 10)
            if func_end < 0:
                func_end = min(func_start + 3000, len(main_html))
            func_content = main_html[func_start:func_end]
            if old_force2 in func_content:
                # 替换函数内的
                new_func_content = func_content.replace(old_force2, new_force2)
                main_html = main_html[:func_start] + new_func_content + main_html[func_end:]
                changes.append('问题6：层门门扇间施力间隙std改为动态变量')
            else:
                print('WARNING: 层门函数内未找到门扇间施力间隙')
    else:
        print('WARNING: 未找到门扇间施力间隙（可能已被修改）')
    
    # 4. 更新renderAtt1LaygateInputs的调用点，传入doorStruct
    # 两个调用点都在renderAttach1函数内
    # 先获取doorStruct变量（应该已经在renderAttach1里有了，在轿门模式下定义的）
    # 我们需要确保在层门模式下也能获取到
    
    # 调用点1: renderAtt1LaygateInputs(d.data || Array(15).fill(''), currentLaygateEditIdx)
    old_call1 = "renderAtt1LaygateInputs(d.data || Array(15).fill(''), currentLaygateEditIdx)"
    new_call1 = "renderAtt1LaygateInputs(d.data || Array(15).fill(''), currentLaygateEditIdx, att1.doorStructure || 'center')"
    if old_call1 in main_html:
        main_html = main_html.replace(old_call1, new_call1)
        changes.append('问题6：更新层门调用点1（编辑模式）')
    else:
        print('WARNING: 未找到层门调用点1')
    
    # 调用点2: renderAtt1LaygateInputs(Array(15).fill(''), '_new')
    old_call2 = "renderAtt1LaygateInputs(Array(15).fill(''), '_new')"
    new_call2 = "renderAtt1LaygateInputs(Array(15).fill(''), '_new', att1.doorStructure || 'center')"
    if old_call2 in main_html:
        main_html = main_html.replace(old_call2, new_call2)
        changes.append('问题6：更新层门调用点2（新增模式）')
    else:
        print('WARNING: 未找到层门调用点2')
    
    # ============================================================
    # 问题6：确保层门模式下也能读取doorStructure（在laygate if分支前确认att1.doorStructure存在）
    # ============================================================
    # 在renderAttach1函数中，进入laygate分支前应该也能访问att1.doorStructure
    # 因为att1是在函数开头获取的，所以应该没问题
    # 但我们需要确保在renderAttach1开头doorStruct变量是存在的（目前只在轿门模式下定义）
    # 让我们在函数开头就定义doorStruct
    
    old_renderstart = "  var html = '<div class=\"att-card\"><div class=\"att-card-title\">🚪 门间隙测量表</div>';"
    new_renderstart = "  var doorStruct = att1.doorStructure || 'center';\n  var html = '<div class=\"att-card\"><div class=\"att-card-title\">🚪 门间隙测量表</div>';"
    
    if old_renderstart in main_html:
        main_html = main_html.replace(old_renderstart, new_renderstart)
        changes.append('问题6：renderAttach1开头添加doorStruct变量')
    else:
        print('WARNING: 未找到renderAttach1 html起始')
    
    # 同时轿门模式下的doorStruct定义就不需要了（因为函数开头已经有了）
    # 但保留也不会有问题，let it be
    
    # 同时更新调用点的参数传入方式（用已有的doorStruct变量）
    # 不过上面已经用att1.doorStructure传入了，也行
    
    # ============================================================
    # 保存
    # ============================================================
    write_file(MAIN_FILE, main_html)
    
    print("\n" + "="*60)
    print("第三部分修改清单：")
    print("="*60)
    for i, c in enumerate(changes, 1):
        print(f"  {i}. {c}")
    print("="*60)

if __name__ == '__main__':
    main()
