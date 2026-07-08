#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v60 升级：记录表技术资料编号列从配置表自动读取
复用已有的 getConfigPartKey 函数，与资料审查页用同一数据源
"""

files = [
    '/app/data/所有对话/主对话/weite-pro-temp/factory-inspection-v2.html',
    '/app/data/所有对话/主对话/weite-pro-temp/威特电梯厂检调试记录单v2.html'
]

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        html = f.read()

    # ============================================================
    # 修改SVG渲染中技术资料编号列的读取逻辑
    # 当前：只从 task.checks[id].v 读
    # 修改：优先读 task.checks[id].v，为空则从 configParts 自动取编号
    # 复用 getConfigPartKey 函数，与资料审查页逻辑一致
    # ============================================================
    old_render = '''        // 技术资料右边列：显示设备编号/型号
        if (info.splitContent) {
          var checkData = task.checks && task.checks[id];
          var plateNo = (checkData && checkData.v) ? escHtml(checkData.v) : '';
          if (plateNo) {'''

    new_render = '''        // 技术资料右边列：显示设备编号（优先读checks.v，为空则从配置表自动取）
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
          if (plateNo) {'''

    html = html.replace(old_render, new_render, 1)

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"{fpath} 已更新为 v60")

print("\nv60 升级完成：记录表技术资料编号列从配置表自动读取")
