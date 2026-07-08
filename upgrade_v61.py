#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v61 升级：从记录单PDF中移除附表1-7，只保留主记录表（检查表1+2）
附表单独做页面，不跟主记录表打在一起
"""

files = [
    '/app/data/所有对话/主对话/weite-pro-temp/factory-inspection-v2.html',
    '/app/data/所有对话/主对话/weite-pro-temp/威特电梯厂检调试记录单v2.html'
]

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 修改 exportCheckPDF 中的 sections 数组，只保留检查表1+2，移除附表1-7
    old_sections = '''  // 渲染：检查表1+2(横版)，附表1-7(每张单独一页竖版)
  // 注意：每张附表单独一页A4竖版，共9页
  var sections = [
    {html: buildCheckItemsHTML(task, proj, dateStr, 1), label: '检查表1', orientation: 'landscape'},
    {html: buildCheckItemsHTML(task, proj, dateStr, 2), label: '检查表2', orientation: 'landscape'},
    {html: buildSingleAttachHTML(task, dateStr, 1), label: '附表1', orientation: 'portrait'},
    {html: buildSingleAttachHTML(task, dateStr, 2), label: '附表2', orientation: 'portrait'},
    {html: buildSingleAttachHTML(task, dateStr, 3), label: '附表3', orientation: 'portrait'},
    {html: buildSingleAttachHTML(task, dateStr, 4), label: '附表4', orientation: 'portrait'},
    {html: buildSingleAttachHTML(task, dateStr, 5), label: '附表5', orientation: 'portrait'},
    {html: buildSingleAttachHTML(task, dateStr, 6), label: '附表6', orientation: 'portrait'},
    {html: buildSingleAttachHTML(task, dateStr, 7), label: '附表7', orientation: 'portrait'}
  ];'''

    new_sections = '''  // 渲染：主记录表两页（横版）
  // 附表已从记录单移除，单独做页面
  var sections = [
    {html: buildCheckItemsHTML(task, proj, dateStr, 1), label: '记录表1', orientation: 'landscape'},
    {html: buildCheckItemsHTML(task, proj, dateStr, 2), label: '记录表2', orientation: 'landscape'}
  ];'''

    html = html.replace(old_sections, new_sections, 1)

    # 同时更新文件名：从"检查表"改为"厂检记录单"更准确
    html = html.replace("var filename = dateForFilename + '_' + projName + '_检查表.pdf';",
                        "var filename = dateForFilename + '_' + projName + '_厂检记录单.pdf';")

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"{fpath} 已更新为 v61")

print("\nv61 升级完成：记录单PDF仅保留主记录表两页，附表已移除")
