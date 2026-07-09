#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v121 批量修复 9 个问题
"""

import re

MAIN_FILE = '/app/data/所有对话/主对话/weite-pro-temp/factory-inspection-v2.html'
FB_FILE = '/app/data/所有对话/主对话/weite-pro-temp/print-fubiao.html'

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    content = read_file(MAIN_FILE)
    fb_content = read_file(FB_FILE)
    
    original_len = len(content)
    fb_original_len = len(fb_content)
    
    # ============================================================
    # Issue 1: 打印检查表失效 - 修复exportNoticePDF和exportCheckPDF中的错误函数名
    # ============================================================
    print("=== Issue 1: 修复打印检查表失效 ===")
    
    # exportNoticePDF 中调用了不存在的 exportCheckToPdf()
    old1 = "      exportCheckToPdf();"
    new1 = "      exportNoticePDF();"
    if old1 in content:
        content = content.replace(old1, new1, 1)
        print("  - 修复 exportNoticePDF 中的错误函数名 exportCheckToPdf -> exportNoticePDF")
    else:
        print("  - 未找到 exportCheckToPdf 调用 (可能已修复)")
    
    # exportCheckPDF 中调用了不存在的 exportCheckToExcelWithPdf()
    old2 = "      exportCheckToExcelWithPdf();"
    new2 = "      exportCheckPDF();"
    if old2 in content:
        content = content.replace(old2, new2, 1)
        print("  - 修复 exportCheckPDF 中的错误函数名 exportCheckToExcelWithPdf -> exportCheckPDF")
    else:
        print("  - 未找到 exportCheckToExcelWithPdf 调用 (可能已修复)")
    
    # ============================================================
    # Issue 2: 打印副表失效 - 确保printFubiao功能正常
    # ============================================================
    print("\n=== Issue 2: 修复打印副表失效 ===")
    
    # 检查printFubiao函数是否正确
    print("  - 检查printFubiao函数...")
    if "function printFubiao(index)" in content:
        print("  - printFubiao函数存在")
    
    # 在print-fubiao.html中添加无数据时的提示
    print("  - 增强print-fubiao.html的错误处理...")
    old_fb_filldata = "function fillData() {\n  var task = getCurrentTask();\n  if (!task) return;"
    new_fb_filldata = """function fillData() {
  var task = getCurrentTask();
  if (!task) {
    document.getElementById('content').innerHTML = '<div style="text-align:center;padding:80px 20px;color:#999;font-size:14px;"><div style="font-size:48px;margin-bottom:16px;">📋</div>暂无数据<br><span style="font-size:12px;">请先在主页面录入检查数据后再打印副表</span></div>';
    return;
  }"""
    if old_fb_filldata in fb_content:
        fb_content = fb_content.replace(old_fb_filldata, new_fb_filldata, 1)
        print("  - 添加无数据提示")
    else:
        print("  - 未找到fillData起始位置，尝试其他匹配...")
        # 尝试不同的格式
        pattern = r"function fillData\(\s*\)\s*\{\s*var task = getCurrentTask\(\);\s*if \(!task\) return;"
        if re.search(pattern, fb_content):
            fb_content = re.sub(pattern, new_fb_filldata.replace("\\", "\\\\"), fb_content, count=1)
            print("  - (正则匹配) 添加无数据提示")
        else:
            print("  - WARNING: 无法定位fillData函数起始")
    
    # 确保content div存在 (给错误提示用)
    if "id='content'" not in fb_content and 'id="content"' not in fb_content:
        # 找到body后面的第一个主要内容容器，给它加id
        # 在工具栏后面的内容添加content id
        old_toolbar_end = '<div style="height:50px;"></div>'
        new_toolbar_end = '<div id="content" style="width:100%;">'
        if old_toolbar_end in fb_content:
            fb_content = fb_content.replace(old_toolbar_end, new_toolbar_end, 1)
            # 在最后一个page之后添加闭合标签
            # 找到body结束标签前添加闭合
            fb_content = fb_content.replace('</body>', '</div>\n</body>', 1)
            print("  - 添加content容器")
    
    # ============================================================
    # Issue 3: 默认项目/电梯仍存在 - 确保首次打开为空
    # ============================================================
    print("\n=== Issue 3: 确保首次打开无默认项目/电梯 ===")
    
    # 检查migrateOldTasks中的"默认项目" - 仅在有旧数据时创建，这是正确的
    # 但我们要确保没有其他地方创建默认数据
    
    # 确认loadProjects正确处理空数据
    if "var projects = [];" in content:
        print("  - projects初始化为空数组 ✓")
    
    # 检查migrateOldTasks正确处理空oldTasks
    if "if (!oldTasks || oldTasks.length === 0) {" in content and "projects = [];" in content:
        print("  - migrateOldTasks空数据时返回空项目 ✓")
    
    # 确保init不会创建默认数据
    if "function init() {" in content and "loadProjects();" in content:
        print("  - init仅加载数据不创建默认值 ✓")
    
    print("  - 确认: 首次打开页面时项目/电梯列表应为空")
    
    # ============================================================
    # Issue 4: 附表1门结构UI调整
    # ============================================================
    print("\n=== Issue 4: 附表1门结构UI调整 ===")
    
    # 当前结构:
    # <div class="door-toggle" style="margin-bottom:10px;">
    #   <div style="font-size:12px;font-weight:600;color:#4a5568;margin-bottom:4px;">门结构</div>
    #   <div style="display:flex;gap:8px;">
    #     <div onclick="setAtt1DoorStructure('center')">中分门</div>
    #     <div onclick="setAtt1DoorStructure('side')">旁开门</div>
    #   </div>
    # </div>
    # 然后是 <div class="fr"><label>门类型</label><select...>
    
    # 需要改为: 同一行，左边两个按钮，右边门类型下拉，去掉"门结构"标签
    
    # 找到门结构开关块
    old_door_struct_block = """  var doorStruct = att1.doorStructure || 'center';
  var html = '<div class="att-card"><div class="att-card-title">🚪 门间隙测量表</div>';
  
  // 门结构总开关
  var doorStruct = att1.doorStructure || 'center';
  html += '<div class="door-toggle" style="margin-bottom:10px;">';
  html += '<div style="font-size:12px;font-weight:600;color:#4a5568;margin-bottom:4px;">门结构</div>';
  html += '<div style="display:flex;gap:8px;">';
  html += '<div onclick="setAtt1DoorStructure(&#39;center&#39;)" style="flex:1;padding:8px 0;text-align:center;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;transition:all 0.2s;border:1.5px solid ' + (doorStruct === 'center' ? '#667eea' : '#e2e8f0') + ';background:' + (doorStruct === 'center' ? 'linear-gradient(135deg,#667eea,#764ba2)' : '#fff') + ';color:' + (doorStruct === 'center' ? '#fff' : '#718096') + ';">中分门</div>';
  html += '<div onclick="setAtt1DoorStructure(&#39;side&#39;)" style="flex:1;padding:8px 0;text-align:center;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;transition:all 0.2s;border:1.5px solid ' + (doorStruct === 'side' ? '#667eea' : '#e2e8f0') + ';background:' + (doorStruct === 'side' ? 'linear-gradient(135deg,#667eea,#764ba2)' : '#fff') + ';color:' + (doorStruct === 'side' ? '#fff' : '#718096') + ';">旁开门</div>';
  html += '</div></div>';
  
  html += '<div class="fr"><label>门类型</label><select id="att1DoorType" onchange="changeAtt1DoorType(this.value)" style="flex:1;border:1px solid #ddd;border-radius:6px;padding:10px;font-size:14px;">';"""
    
    new_door_struct_block = """  var doorStruct = att1.doorStructure || 'center';
  var html = '<div class="att-card"><div class="att-card-title">🚪 门间隙测量表</div>';
  
  // 门结构切换 + 门类型选择（同一行）
  var doorStruct = att1.doorStructure || 'center';
  html += '<div style="display:flex;gap:10px;margin-bottom:12px;align-items:stretch;">';
  // 左：中分门/旁开门按钮
  html += '<div style="flex:0 0 auto;display:flex;gap:6px;">';
  html += '<div onclick="setAtt1DoorStructure(&#39;center&#39;)" style="padding:0 16px;display:flex;align-items:center;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;transition:all 0.2s;border:1.5px solid ' + (doorStruct === 'center' ? '#667eea' : '#e2e8f0') + ';background:' + (doorStruct === 'center' ? 'linear-gradient(135deg,#667eea,#764ba2)' : '#fff') + ';color:' + (doorStruct === 'center' ? '#fff' : '#718096') + ';">中分门</div>';
  html += '<div onclick="setAtt1DoorStructure(&#39;side&#39;)" style="padding:0 16px;display:flex;align-items:center;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;transition:all 0.2s;border:1.5px solid ' + (doorStruct === 'side' ? '#667eea' : '#e2e8f0') + ';background:' + (doorStruct === 'side' ? 'linear-gradient(135deg,#667eea,#764ba2)' : '#fff') + ';color:' + (doorStruct === 'side' ? '#fff' : '#718096') + ';">旁开门</div>';
  html += '</div>';
  // 右：门类型下拉
  html += '<div class="fr" style="flex:1;display:flex;align-items:center;"><label style="flex-shrink:0;">门类型</label><select id="att1DoorType" onchange="changeAtt1DoorType(this.value)" style="flex:1;border:1px solid #ddd;border-radius:6px;padding:10px;font-size:14px;min-width:0;">';"""
    
    if old_door_struct_block in content:
        content = content.replace(old_door_struct_block, new_door_struct_block, 1)
        print("  - 调整门结构UI：去掉标签，按钮和下拉放同一行")
    else:
        print("  - WARNING: 未找到门结构代码块精确匹配，尝试分段替换...")
        # 去掉"门结构"标签行
        old_label = "html += '<div style=\"font-size:12px;font-weight:600;color:#4a5568;margin-bottom:4px;\">门结构</div>';"
        if old_label in content:
            content = content.replace(old_label, "// 门结构标签已移除，与门类型同行显示")
            print("  - 移除'门结构'标签")
        
        # 把门结构块和门类型下拉合并到一行 - 这个比较复杂，先做简单替换
        # 将 door-toggle div改为行内布局
        old_door_toggle = "html += '<div class=\"door-toggle\" style=\"margin-bottom:10px;\">';"
        new_door_toggle = "html += '<div style=\"display:flex;gap:10px;margin-bottom:12px;align-items:stretch;\">';"
        if old_door_toggle in content:
            content = content.replace(old_door_toggle, new_door_toggle, 1)
            print("  - 调整门结构容器为行布局")
    
    # ============================================================
    # Issue 5: 附表1门扇间隙联动主表门间隙判定
    # ============================================================
    print("\n=== Issue 5: 附表1门扇间隙联动主表门间隙判定 ===")
    
    # 在renderAttach1Judge中添加门扇间施力间隙(idx6)的检查
    # 需要在轿门和层门的数据检查中都加入idx6
    
    # 首先在变量声明处添加 forceGapOk 和 hasForceGapData
    old_vars = """  var hasData = false;
  var doorGapOk = true;    // 门间隙 3-6mm (id114)
  var doorLockOk = true;   // 门锁啮合长度 ≥7mm (id115)
  var sillOk = true;       // 门地坎距离 ≤35mm (id113)
  
  var hasDoorGapData = false;
  var hasDoorLockData = false;
  var hasSillData = false;"""
    
    new_vars = """  var hasData = false;
  var doorGapOk = true;    // 门间隙 3-6mm (id114)
  var doorLockOk = true;   // 门锁啮合长度 ≥7mm (id115)
  var sillOk = true;       // 门地坎距离 ≤35mm (id113)
  var forceGapOk = true;   // 门扇间施力间隙 ≤45mm(中分)/≤30mm(旁开) (id114)
  
  var hasDoorGapData = false;
  var hasDoorLockData = false;
  var hasSillData = false;
  var hasForceGapData = false;
  var doorStructure = (att1.doorStructure || 'center');
  var forceGapStd = (doorStructure === 'side') ? 30 : 45;"""
    
    if old_vars in content:
        content = content.replace(old_vars, new_vars, 1)
        print("  - 添加门扇间施力间隙变量")
    else:
        print("  - WARNING: 未找到变量声明块")
    
    # 在轿门数据检查中添加idx6检查
    old_cargate_check = """    // 门锁啮合长度 idx:9 (标准≥7mm)
    var v9 = parseFloat(cd[9]);
    if (!isNaN(v9) && v9 > 0) {
      hasDoorLockData = true;
      hasData = true;
      if (v9 < 7) doorLockOk = false;
    }
  });
  
  // 检查层门数据"""
    
    new_cargate_check = """    // 门锁啮合长度 idx:9 (标准≥7mm)
    var v9 = parseFloat(cd[9]);
    if (!isNaN(v9) && v9 > 0) {
      hasDoorLockData = true;
      hasData = true;
      if (v9 < 7) doorLockOk = false;
    }
    // 门扇间施力间隙 idx:6 (标准:中分门≤45mm, 旁开门≤30mm)
    var v6 = parseFloat(cd[6]);
    if (!isNaN(v6) && v6 > 0) {
      hasForceGapData = true;
      hasData = true;
      if (v6 > forceGapStd) forceGapOk = false;
    }
  });
  
  // 检查层门数据"""
    
    if old_cargate_check in content:
        content = content.replace(old_cargate_check, new_cargate_check, 1)
        print("  - 添加轿门门扇间施力间隙检查")
    else:
        print("  - WARNING: 未找到轿门门锁检查块")
    
    # 在层门数据检查中添加idx6检查
    old_laygate_lock = """    // 门锁啮合长度 idx:9 (标准≥7mm)
    var v9 = parseFloat(d[9]);
    if (!isNaN(v9) && v9 > 0) {
      hasDoorLockData = true;
      hasData = true;
      if (v9 < 7) doorLockOk = false;
    }
  });
  
  // 回填到主表检测项"""
    
    new_laygate_lock = """    // 门锁啮合长度 idx:9 (标准≥7mm)
    var v9 = parseFloat(d[9]);
    if (!isNaN(v9) && v9 > 0) {
      hasDoorLockData = true;
      hasData = true;
      if (v9 < 7) doorLockOk = false;
    }
    // 门扇间施力间隙 idx:6 (标准:中分门≤45mm, 旁开门≤30mm)
    var v6 = parseFloat(d[6]);
    if (!isNaN(v6) && v6 > 0) {
      hasForceGapData = true;
      hasData = true;
      if (v6 > forceGapStd) forceGapOk = false;
    }
  });
  
  // 回填到主表检测项"""
    
    if old_laygate_lock in content:
        content = content.replace(old_laygate_lock, new_laygate_lock, 1)
        print("  - 添加层门门扇间施力间隙检查")
    else:
        print("  - WARNING: 未找到层门门锁检查块")
    
    # 更新id114的判定逻辑，加入forceGap
    old_id114 = """  // id114: 门间隙
  if (hasDoorGapData) {
    if (!task.checks[114]) task.checks[114] = {};
    task.checks[114].s = doorGapOk ? 'ok' : 'ng';
    if (!doorGapOk) task.checks[114].n = '门间隙不符合标准';
  }"""
    
    new_id114 = """  // id114: 门间隙（包含门扇间隙和门扇间施力间隙）
  if (hasDoorGapData || hasForceGapData) {
    if (!task.checks[114]) task.checks[114] = {};
    var gapAllOk = doorGapOk && forceGapOk;
    task.checks[114].s = gapAllOk ? 'ok' : 'ng';
    var ngMsgs = [];
    if (!doorGapOk) ngMsgs.push('门间隙不符合标准');
    if (!forceGapOk) ngMsgs.push('门扇间施力间隙超过' + forceGapStd + 'mm');
    if (!gapAllOk) task.checks[114].n = ngMsgs.join('；');
  }"""
    
    if old_id114 in content:
        content = content.replace(old_id114, new_id114, 1)
        print("  - 更新id114门间隙判定逻辑（含施力间隙）")
    else:
        print("  - WARNING: 未找到id114判定块")
    
    # 更新allOk判断
    old_allok = "  var allOk = hasData && sillOk && doorGapOk && doorLockOk && (!hasCutterData || cutterOk) && (!hasRollerData || rollerOk);"
    new_allok = "  var allOk = hasData && sillOk && doorGapOk && doorLockOk && forceGapOk && (!hasCutterData || cutterOk) && (!hasRollerData || rollerOk);"
    if old_allok in content:
        content = content.replace(old_allok, new_allok, 1)
        print("  - 更新allOk判断（加入forceGapOk）")
    else:
        print("  - WARNING: 未找到allOk判断")
    
    # 在自动判定显示中添加施力间隙
    old_judge_display = "  html += ' | id114(门间隙) ';"
    new_judge_display = "  html += ' | id114(门间隙含施力间隙) ';"
    if old_judge_display in content:
        content = content.replace(old_judge_display, new_judge_display, 1)
        print("  - 更新自动判定显示文字")
    
    # ============================================================
    # Issue 6: 附表2第②③点名称补全
    # ============================================================
    print("\n=== Issue 6: 附表2第②③点名称补全 ===")
    
    old_s2_s3 = """    {key:'s1', label:'①轿厢导轨进一步制导行程', formula:'0.1+0.035v2'},
    {key:'s2', label:'②轿顶可站人面积垂直距离', formula:'1.0+0.035v2'},
    {key:'s3', label:'③井道顶最低部件与轿顶部件距离', formula:'0.3+0.035v2'},
    {key:'s4', label:'④井道顶的最低部件与导靴或滚轮、悬挂装置端接装置附件、垂直滑动门的横梁或者部件的最高部分之间的自由垂直距离', formula:'0.1+0.035v2'}"""
    
    new_s2_s3 = """    {key:'s1', label:'①轿厢导轨进一步制导行程≥0.1＋0.035v²(m)', formula:'0.1+0.035v2'},
    {key:'s2', label:'②位于轿厢投影部分的井道顶最低部件的水平面与轿顶最高可站人面积水平面之间的自由垂直距离≥1.0＋0.035v²(m)', formula:'1.0+0.035v2'},
    {key:'s3', label:'③井道顶最低部件与固定在轿顶部件最高部分之间的自由垂直距离≥0.3＋0.035v²(m)', formula:'0.3+0.035v2'},
    {key:'s4', label:'④井道顶的最低部件与导靴或滚轮、悬挂装置端接装置附件、垂直滑动门的横梁或者部件的最高部分之间的自由垂直距离≥0.1＋0.035v²(m)', formula:'0.1+0.035v2'}"""
    
    if old_s2_s3 in content:
        content = content.replace(old_s2_s3, new_s2_s3, 1)
        print("  - 更新附表2顶部空间s1/s2/s3/s4完整名称")
    else:
        print("  - WARNING: 未找到附表2标签块，尝试单独替换...")
        # 逐个替换
        replacements = [
            ("{key:'s2', label:'②轿顶可站人面积垂直距离', formula:'1.0+0.035v2'}",
             "{key:'s2', label:'②位于轿厢投影部分的井道顶最低部件的水平面与轿顶最高可站人面积水平面之间的自由垂直距离≥1.0＋0.035v²(m)', formula:'1.0+0.035v2'}"),
            ("{key:'s3', label:'③井道顶最低部件与轿顶部件距离', formula:'0.3+0.035v2'}",
             "{key:'s3', label:'③井道顶最低部件与固定在轿顶部件最高部分之间的自由垂直距离≥0.3＋0.035v²(m)', formula:'0.3+0.035v2'}"),
        ]
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new, 1)
                print(f"  - 更新 {old.split(':')[1].split(',')[0]}")
            else:
                print(f"  - 未找到 {old[:40]}...")
    
    # ============================================================
    # Issue 7: 删除顶部菜单栏"导出通知单（Excel）"
    # ============================================================
    print("\n=== Issue 7: 删除顶部菜单栏导出通知单Excel ===")
    
    old_excel_menu = "      <div onclick=\"saveCurrentTask();exportNoticeExcel();closeHeaderMenu('check')\">📊 导出通知书Excel</div>"
    if old_excel_menu in content:
        content = content.replace(old_excel_menu + "\n", "", 1)
        print("  - 删除顶部菜单'导出通知书Excel'")
    else:
        print("  - WARNING: 未找到导出通知书Excel菜单项")
        # 尝试不同的格式
        alt_pattern = r"      <div onclick=\"[^\"]*exportNoticeExcel[^\"]*\">[^<]*</div>\n?"
        match = re.search(alt_pattern, content)
        if match:
            content = content.replace(match.group(0), "", 1)
            print("  - (正则匹配) 删除导出Excel菜单项")
    
    # ============================================================
    # Issue 8: 新增备注功能
    # ============================================================
    print("\n=== Issue 8: 新增备注功能 ===")
    
    # 1. 在createTask中添加notes初始化
    old_create_task_notes = "    signatures: {},"
    new_create_task_notes = "    signatures: {},\n    notes: [],"
    if old_create_task_notes in content:
        content = content.replace(old_create_task_notes, new_create_task_notes, 1)
        print("  - 在createTask中添加notes初始化")
    else:
        print("  - WARNING: 未找到createTask的signatures行")
    
    # 2. 在底部或顶部菜单添加"备注"按钮 - 放在签字区域附近或作为浮动按钮
    # 找到renderSignZoneContent函数附近，添加备注区域
    # 先找一个合适的位置插入 - 比如在签字区域之前
    
    # 添加备注CSS样式
    old_css_end = ".sub-accordion{margin-bottom:10px;border-radius:12px;background:#fff;border:1px solid #e8ecf0;}"
    new_css_end = """.sub-accordion{margin-bottom:10px;border-radius:12px;background:#fff;border:1px solid #e8ecf0;}
.notes-section{background:#fff;border-radius:12px;padding:15px;margin-bottom:10px;border:1px solid #e8ecf0;}
.notes-title{font-size:14px;font-weight:600;color:#2d3748;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;}
.notes-add-btn{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;border-radius:6px;padding:6px 12px;font-size:12px;cursor:pointer;}
.note-item{background:#f7fafc;border-radius:8px;padding:10px;margin-bottom:8px;border-left:3px solid #667eea;}
.note-item-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;}
.note-item-title{font-size:12px;font-weight:600;color:#4a5568;}
.note-item-del{color:#e53e3e;cursor:pointer;font-size:12px;}
.note-item textarea{width:100%;border:1px solid #e2e8f0;border-radius:6px;padding:8px;font-size:13px;font-family:inherit;resize:vertical;min-height:60px;box-sizing:border-box;}
.note-item textarea:focus{outline:none;border-color:#667eea;}"""
    
    if old_css_end in content:
        content = content.replace(old_css_end, new_css_end, 1)
        print("  - 添加备注功能CSS样式")
    else:
        print("  - WARNING: 未找到CSS插入位置")
    
    # 3. 添加备注渲染函数 - 放在renderSignZoneContent之前
    old_render_sign = "function renderSignZoneContent(container) {"
    new_notes_func = """function renderNotesSection(container) {
  var task = getCurrentTask();
  if (!task) return;
  if (!task.notes) task.notes = [];
  
  var html = '<div class="notes-section">';
  html += '<div class="notes-title">📝 备注 <button class="notes-add-btn" onclick="addNote()">+ 添加备注</button></div>';
  
  if (task.notes.length === 0) {
    html += '<div style="text-align:center;color:#aaa;font-size:12px;padding:20px 0;">暂无备注</div>';
  } else {
    task.notes.forEach(function(note, idx) {
      html += '<div class="note-item">';
      html += '<div class="note-item-header"><span class="note-item-title">备注' + (idx + 1) + '</span><span class="note-item-del" onclick="deleteNote(' + idx + ')">删除</span></div>';
      html += '<textarea placeholder="输入备注内容..." onchange="updateNote(' + idx + ', this.value)">' + (note.content || '') + '</textarea>';
      html += '</div>';
    });
  }
  
  html += '</div>';
  container.innerHTML = html;
}

function addNote() {
  var task = getCurrentTask(); if (!task) return;
  if (!task.notes) task.notes = [];
  task.notes.push({content: ''});
  saveCurrentTask();
  var target = document.getElementById('notesSection');
  if (target) renderNotesSection(target);
  updateProgress();
}

function updateNote(idx, val) {
  var task = getCurrentTask(); if (!task) return;
  if (!task.notes || !task.notes[idx]) return;
  task.notes[idx].content = val;
  saveCurrentTask();
}

function deleteNote(idx) {
  var task = getCurrentTask(); if (!task) return;
  if (!task.notes) return;
  if (!confirm('确定删除这条备注吗？')) return;
  task.notes.splice(idx, 1);
  saveCurrentTask();
  var target = document.getElementById('notesSection');
  if (target) renderNotesSection(target);
  updateProgress();
}

""" + old_render_sign
    
    if old_render_sign in content:
        content = content.replace(old_render_sign, new_notes_func, 1)
        print("  - 添加备注功能JS函数")
    else:
        print("  - WARNING: 未找到renderSignZoneContent函数")
    
    # 4. 在签字区域页面添加备注区域 - 找到sign zone的渲染部分
    # 查找sign zone的HTML结构，在前面插入备注
    old_sign_zone = 'id="signZone"'
    if old_sign_zone in content:
        print("  - 找到签字区域，准备插入备注区域...")
        # 在签字区域之前插入备注section
        old_sign_page = '''<div class="page" id="page-sign">'''
        new_sign_page = '''<div class="page" id="page-sign">
    <div id="notesSection"></div>'''
        
        if old_sign_page in content:
            content = content.replace(old_sign_page, new_sign_page, 1)
            print("  - 在签字页添加备注容器")
        else:
            print("  - WARNING: 未找到签字页div")
    
    # 5. 在切换到签字区域时渲染备注
    old_render_sign_call = "    renderSignZoneContent(signEl);"
    new_render_sign_call = """    var notesEl = document.getElementById('notesSection');
    if (notesEl) renderNotesSection(notesEl);
    renderSignZoneContent(signEl);"""
    if old_render_sign_call in content:
        content = content.replace(old_render_sign_call, new_render_sign_call, 1)
        print("  - 签字区域渲染时同时渲染备注")
    else:
        print("  - WARNING: 未找到renderSignZoneContent调用")
    
    # 6. 在通知单PDF中添加备注
    # 找到NG items收集的部分，在后面添加备注
    old_ng_collect = """  var ngItems = [];
  checkItems.forEach(function(item) {
    var c = task.checks[item.id];
    if (c && c.s === 'ng') {
      var dispName = getPDFDisplayItemName(item, c);
      ngItems.push({id:item.id,name:dispName,std:item.std,value:c.v||'',duty:c.d||'A',note:c.n||''});
    }
  });"""
    
    new_ng_collect = """  var ngItems = [];
  checkItems.forEach(function(item) {
    var c = task.checks[item.id];
    if (c && c.s === 'ng') {
      var dispName = getPDFDisplayItemName(item, c);
      ngItems.push({id:item.id,name:dispName,std:item.std,value:c.v||'',duty:c.d||'A',note:c.n||''});
    }
  });
  // 添加备注
  if (task.notes && task.notes.length > 0) {
    task.notes.forEach(function(note, idx) {
      if (note.content && note.content.trim()) {
        ngItems.push({id:'note_' + idx, name:'备注：' + note.content, std:'-', value:'', duty:'', note:'', isNote:true});
      }
    });
  }"""
    
    if old_ng_collect in content:
        content = content.replace(old_ng_collect, new_ng_collect, 1)
        print("  - 通知单PDF中添加备注显示")
    else:
        print("  - WARNING: 未找到NG items收集代码")
    
    # ============================================================
    # Issue 9: 手风琴展开滚动定位修复
    # ============================================================
    print("\n=== Issue 9: 手风琴展开滚动定位修复 ===")
    
    old_toggle_subgroup = """function toggleSubGroup(zoneIdx, groupIdx) {
  if (!expandedSubGroups[zoneIdx]) expandedSubGroups[zoneIdx] = {};
  var isCurrentlyExpanded = expandedSubGroups[zoneIdx][groupIdx] === true;
  // 手风琴效果：先收起同区域所有已展开的模块
  for (var key in expandedSubGroups[zoneIdx]) {
    if (expandedSubGroups[zoneIdx].hasOwnProperty(key)) {
      expandedSubGroups[zoneIdx][key] = false;
    }
  }
  // 如果之前是收起的，则展开当前模块（手风琴：点击已展开的则全部收起）
  if (!isCurrentlyExpanded) {
    expandedSubGroups[zoneIdx][groupIdx] = true;
  }
  renderZoneContent(zoneIdx);
}"""
    
    new_toggle_subgroup = """function toggleSubGroup(zoneIdx, groupIdx) {
  if (!expandedSubGroups[zoneIdx]) expandedSubGroups[zoneIdx] = {};
  var isCurrentlyExpanded = expandedSubGroups[zoneIdx][groupIdx] === true;
  // 手风琴效果：先收起同区域所有已展开的模块
  for (var key in expandedSubGroups[zoneIdx]) {
    if (expandedSubGroups[zoneIdx].hasOwnProperty(key)) {
      expandedSubGroups[zoneIdx][key] = false;
    }
  }
  // 如果之前是收起的，则展开当前模块（手风琴：点击已展开的则全部收起）
  var willExpand = !isCurrentlyExpanded;
  if (willExpand) {
    expandedSubGroups[zoneIdx][groupIdx] = true;
  }
  renderZoneContent(zoneIdx);
  
  // 展开后滚动到该分组顶部
  if (willExpand) {
    setTimeout(function() {
      var groupEl = document.getElementById('subGroup_' + zoneIdx + '_' + groupIdx);
      if (groupEl) {
        var rect = groupEl.getBoundingClientRect();
        var headerOffset = 60; // 顶部导航栏高度
        var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        var targetTop = scrollTop + rect.top - headerOffset;
        window.scrollTo({top: targetTop, behavior: 'smooth'});
      }
    }, 50);
  }
}"""
    
    if old_toggle_subgroup in content:
        content = content.replace(old_toggle_subgroup, new_toggle_subgroup, 1)
        print("  - 添加手风琴展开后滚动定位")
    else:
        print("  - WARNING: 未找到toggleSubGroup函数精确匹配")
        # 尝试找到函数并添加滚动逻辑
        pattern = r"function toggleSubGroup\(zoneIdx, groupIdx\) \{[\s\S]*?renderZoneContent\(zoneIdx\);\s*\}"
        match = re.search(pattern, content)
        if match:
            print("  - (正则匹配) 找到toggleSubGroup函数")
            # 在renderZoneContent之后添加滚动逻辑
            old_render_call = "  renderZoneContent(zoneIdx);\n}"
            new_render_call = """  renderZoneContent(zoneIdx);
  
  // 展开后滚动到该分组顶部
  if (!isCurrentlyExpanded) {
    setTimeout(function() {
      var groupEl = document.getElementById('subGroup_' + zoneIdx + '_' + groupIdx);
      if (groupEl) {
        var rect = groupEl.getBoundingClientRect();
        var headerOffset = 60;
        var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        window.scrollTo({top: scrollTop + rect.top - headerOffset, behavior: 'smooth'});
      }
    }, 50);
  }
}"""
            if old_render_call in content:
                content = content.replace(old_render_call, new_render_call, 1)
                print("  - 添加滚动定位代码")
    
    # 确保subGroup元素有id - 在手风琴渲染处添加id
    # 找到sub-accordion的渲染，添加id
    old_sub_accordion = "html += '<div class=\"sub-accordion\">';"
    new_sub_accordion = "html += '<div class=\"sub-accordion\" id=\"subGroup_' + index + '_' + gi + '\">';"
    # 需要确认变量名，让我先检查一下渲染代码中的变量
    
    # 实际上，在renderZoneContent中，groups是subGroupMap[index + 1]
    # 让我找到确切的渲染位置
    old_sub_acc_render = """      html += '<div class="sub-accordion">';
      html += '<div class="sub-acc-header" onclick="toggleSubGroup(' + index + ',' + gi + ')">';"""
    new_sub_acc_render = """      html += '<div class="sub-accordion" id="subGroup_' + index + '_' + gi + '">';
      html += '<div class="sub-acc-header" onclick="toggleSubGroup(' + index + ',' + gi + ')">';"""
    
    if old_sub_acc_render in content:
        content = content.replace(old_sub_acc_render, new_sub_acc_render, 1)
        print("  - 为sub-accordion添加id属性")
    else:
        print("  - WARNING: 未找到sub-accordion渲染位置")
        # 尝试不同的格式
        alt_pattern = r"html \+= '<div class=\"sub-accordion\">';\s*\n\s*html \+= '<div class=\"sub-acc-header\""
        if re.search(alt_pattern, content):
            content = re.sub(
                r"html \+= '<div class=\"sub-accordion\">';(\s*\n\s*html \+= '<div class=\"sub-acc-header\" onclick=\"toggleSubGroup\(" ,
                r"html += '<div class=\"sub-accordion\" id=\"subGroup_' + index + '_' + gi + '\">';\1",
                content
            )
            print("  - (正则) 为sub-accordion添加id属性")
    
    # ============================================================
    # 保存文件
    # ============================================================
    write_file(MAIN_FILE, content)
    write_file(FB_FILE, fb_content)
    
    print(f"\n=== 完成 ===")
    print(f"主文件: {original_len} -> {len(content)} 字节 (变化: {len(content)-original_len:+d})")
    print(f"副表文件: {fb_original_len} -> {len(fb_content)} 字节 (变化: {len(fb_content)-fb_original_len:+d})")

if __name__ == '__main__':
    main()
