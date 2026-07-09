#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v129 修复脚本：6项修复
1. 保存按钮改名（暂时保存→保存）
2. 去掉相关人员签名UI
3. 厂检结论页加备注
4. 通知单打印备注
5. 打印副表报错修复（签名容错）
6. 数据备份机制
"""

import sys
import os
import re

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_all(filepath):
    content = read_file(filepath)
    original = content
    fixes_applied = []

    # ============================================================
    # Fix 1: 保存按钮改名 - 搜索"暂时保存"，全部替换为"保存"
    # ============================================================
    count_save = content.count('暂时保存')
    if count_save > 0:
        content = content.replace('暂时保存', '保存')
        fixes_applied.append(f'Fix 1: 保存按钮改名（{count_save}处）')
    else:
        print("  [WARN] Fix 1: 未找到'暂时保存'")

    # ============================================================
    # Fix 2: 去掉相关人员签名UI - 给外层div加display:none
    # ============================================================
    # 找到"相关人员签名"所在的整个区块的外层div
    # 外层div的特征：background:#f8fff8;border-radius:12px;padding:14px;margin-bottom:12px;border:1px solid #e2e8f0;
    old_related_div = "html += '<div style=\"background:#f8fff8;border-radius:12px;padding:14px;margin-bottom:12px;border:1px solid #e2e8f0;\">';\n  // （检验人员全局签名和项目级签名提示框已移除，签名入口在顶部菜单）\n  html += '<div style=\"font-size:13px;font-weight:600;margin-bottom:8px;\">相关人员签名</div>';"
    
    new_related_div = "html += '<div style=\"background:#f8fff8;border-radius:12px;padding:14px;margin-bottom:12px;border:1px solid #e2e8f0;display:none;\">';\n  // （检验人员全局签名和项目级签名提示框已移除，签名入口在顶部菜单）\n  // 【v129】相关人员签名UI已隐藏，JS逻辑保留\n  html += '<div style=\"font-size:13px;font-weight:600;margin-bottom:8px;\">相关人员签名</div>';"
    
    if old_related_div in content:
        content = content.replace(old_related_div, new_related_div)
        fixes_applied.append('Fix 2: 隐藏相关人员签名UI')
    else:
        print("  [WARN] Fix 2: 未找到相关人员签名外层div，尝试其他方式...")
        # 尝试更短的匹配
        old_short = "html += '<div style=\"background:#f8fff8;border-radius:12px;padding:14px;margin-bottom:12px;border:1px solid #e2e8f0;\">';\n  // （检验人员全局签名和项目级签名提示框已移除，签名入口在顶部菜单）"
        new_short = "html += '<div style=\"background:#f8fff8;border-radius:12px;padding:14px;margin-bottom:12px;border:1px solid #e2e8f0;display:none;\">';\n  // （检验人员全局签名和项目级签名提示框已移除，签名入口在顶部菜单）\n  // 【v129】相关人员签名UI已隐藏"
        if old_short in content:
            content = content.replace(old_short, new_short)
            fixes_applied.append('Fix 2: 隐藏相关人员签名UI（短匹配）')
        else:
            print("  [ERROR] Fix 2: 无法匹配相关人员签名区域")

    # ============================================================
    # Fix 3: 厂检结论页加备注
    # 在整改期限区域下方、签名区域上方，添加备注编辑区
    # ============================================================
    old_rectify_end = """  html += '</div></div>';

  // 签字区域 - 合并为一个签字确认面板"""

    new_rectify_end = """  html += '</div></div>';

  // 备注
  html += '<div style="margin-bottom:20px;">';
  html += '<div style="font-size:15px;font-weight:700;margin-bottom:10px;color:#667eea;">备注</div>';
  html += '<textarea id="conclusionRemark" rows="4" placeholder="请输入备注信息..." oninput="setConclusionRemark(this.value)" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;font-size:14px;font-family:inherit;resize:vertical;box-sizing:border-box;line-height:1.5;">' + (task.remark || '') + '</textarea>';
  html += '</div>';

  // 签字区域 - 合并为一个签字确认面板"""

    if old_rectify_end in content:
        content = content.replace(old_rectify_end, new_rectify_end)
        fixes_applied.append('Fix 3a: 厂检结论页添加备注编辑区')
    else:
        print("  [WARN] Fix 3a: 未找到整改期限结束位置")
        # 尝试另一种匹配
        old_rectify_alt = """  html += '<span style="font-size:13px;">前整改完毕</span>';
  html += '</div></div>';

  // 签字区域"""
        new_rectify_alt = """  html += '<span style="font-size:13px;">前整改完毕</span>';
  html += '</div></div>';

  // 备注
  html += '<div style="margin-bottom:20px;">';
  html += '<div style="font-size:15px;font-weight:700;margin-bottom:10px;color:#667eea;">备注</div>';
  html += '<textarea id="conclusionRemark" rows="4" placeholder="请输入备注信息..." oninput="setConclusionRemark(this.value)" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;font-size:14px;font-family:inherit;resize:vertical;box-sizing:border-box;line-height:1.5;">' + (task.remark || '') + '</textarea>';
  html += '</div>';

  // 签字区域"""
        if old_rectify_alt in content:
            content = content.replace(old_rectify_alt, new_rectify_alt)
            fixes_applied.append('Fix 3a: 厂检结论页添加备注编辑区（备选匹配）')
        else:
            print("  [ERROR] Fix 3a: 无法找到备注插入位置")

    # 添加 setConclusionRemark 函数（在 setRectifyDeadline 后面）
    old_set_rectify = """function setRectifyDeadline(val) {
  var task = getCurrentTask();
  if (!task) return;
  task.rectifyDeadline = val;
  saveProjects();
}"""

    new_set_rectify = """function setRectifyDeadline(val) {
  var task = getCurrentTask();
  if (!task) return;
  task.rectifyDeadline = val;
  saveProjects();
}

function setConclusionRemark(val) {
  var task = getCurrentTask();
  if (!task) return;
  task.remark = val;
  saveProjects();
}"""

    if old_set_rectify in content:
        content = content.replace(old_set_rectify, new_set_rectify)
        fixes_applied.append('Fix 3b: 添加setConclusionRemark函数')
    else:
        print("  [WARN] Fix 3b: 未找到setRectifyDeadline函数")

    # ============================================================
    # Fix 4: 通知单打印备注
    # 在通知单打印的HTML模板中添加备注显示
    # ============================================================
    old_notice_remark = """  // 行38：备注（B:G合并，上下都有边）
  h += '<tr>';
  h += '<td style="border:1px solid #000;padding:2px 3px;color:#666;height:50px;" colspan="6">备注：①本通知书一式三联，检验机构、安装单位、项目管理各执一联。②整改完成后，请将本通知书返还检验人员确认。③如有异议，请在收到本通知书之日起5个工作日内提出。</td>';
  h += '</tr>';"""

    new_notice_remark = """  // 行38：备注（含任务备注，B:G合并，上下都有边）
  var taskRemarkStr = '';
  try {
    if (task.remark && typeof task.remark === 'string' && task.remark.trim().length > 0) {
      taskRemarkStr = task.remark.trim();
    }
  } catch(e) { console.warn('读取任务备注失败', e); }
  h += '<tr>';
  if (taskRemarkStr) {
    h += '<td style="border:1px solid #000;padding:4px 6px;color:#333;height:auto;vertical-align:top;" colspan="6">';
    h += '<div style="font-weight:bold;margin-bottom:4px;font-size:9px;">任务备注：</div>';
    h += '<div style="white-space:pre-wrap;line-height:1.6;font-size:9px;">' + escHtml(taskRemarkStr) + '</div>';
    h += '<div style="margin-top:6px;color:#666;font-size:8px;">备注：①本通知书一式三联，检验机构、安装单位、项目管理各执一联。②整改完成后，请将本通知书返还检验人员确认。③如有异议，请在收到本通知书之日起5个工作日内提出。</div>';
    h += '</td>';
  } else {
    h += '<td style="border:1px solid #000;padding:2px 3px;color:#666;height:50px;" colspan="6">备注：①本通知书一式三联，检验机构、安装单位、项目管理各执一联。②整改完成后，请将本通知书返还检验人员确认。③如有异议，请在收到本通知书之日起5个工作日内提出。</td>';
  }
  h += '</tr>';"""

    if old_notice_remark in content:
        content = content.replace(old_notice_remark, new_notice_remark)
        fixes_applied.append('Fix 4: 通知单打印显示任务备注')
    else:
        print("  [WARN] Fix 4: 未找到通知单备注行代码")
        # 尝试部分匹配
        old_partial = '备注：①本通知书一式三联'
        if old_partial in content:
            print("  [INFO] Fix 4: 找到了'备注：①本通知书一式三联'，但完整匹配失败")

    # ============================================================
    # Fix 5: 打印副表报错修复 - 签名校验容错
    # 在buildNoticeFullHTML中增加签名读取的容错处理
    # ============================================================
    # 检验人员签名 - 增加容错
    old_insp_sig = """  // 检验人员签名：优先从localStorage读取全局签名，没有则用任务级签名
  var inspSig = '';
  var inspName = '';
  try {
    var _inspStored = localStorage.getItem(INSPECTOR_SIG_KEY);
    if (_inspStored) {
      var _inspObj = JSON.parse(_inspStored);
      if (_inspObj && _inspObj.sig) {
        inspSig = _inspObj.sig;
        inspName = _inspObj.name || '';
      }
    }
  } catch(e) {}
  if (!inspSig && task.signatures && task.signatures.inspectorSig) {
    inspSig = task.signatures.inspectorSig;
  }
  if (!inspName) inspName = (task.signatures && task.signatures.inspectorName) || manager || '';"""

    new_insp_sig = """  // 检验人员签名：优先从localStorage读取全局签名，没有则用任务级签名
  // 【v129】增加容错：签名数据无效或为空时跳过，不报错
  var inspSig = '';
  var inspName = '';
  try {
    var _inspStored = localStorage.getItem(INSPECTOR_SIG_KEY);
    if (_inspStored && typeof _inspStored === 'string' && _inspStored.length > 0) {
      try {
        var _inspObj = JSON.parse(_inspStored);
        if (_inspObj && typeof _inspObj === 'object' && _inspObj.sig && typeof _inspObj.sig === 'string' && _inspObj.sig.length > 0) {
          inspSig = _inspObj.sig;
          inspName = (_inspObj.name && typeof _inspObj.name === 'string') ? _inspObj.name : '';
        }
      } catch(parseErr) {
        console.warn('解析检验人员签名数据失败', parseErr);
      }
    }
  } catch(e) { console.warn('读取检验人员签名存储失败', e); }
  try {
    if (!inspSig && task.signatures && task.signatures.inspectorSig && typeof task.signatures.inspectorSig === 'string' && task.signatures.inspectorSig.length > 0) {
      inspSig = task.signatures.inspectorSig;
    }
    if (!inspName) {
      if (task.signatures && task.signatures.inspectorName && typeof task.signatures.inspectorName === 'string') {
        inspName = task.signatures.inspectorName;
      } else {
        inspName = manager || '';
      }
    }
  } catch(e) { console.warn('读取任务级检验人员签名失败', e); }"""

    if old_insp_sig in content:
        content = content.replace(old_insp_sig, new_insp_sig)
        fixes_applied.append('Fix 5a: 检验人员签名读取容错')
    else:
        print("  [WARN] Fix 5a: 未找到检验人员签名读取代码")

    # 安装单位代表签名 - 增加容错
    old_pm_sig = """  // 安装单位代表签名：优先从项目级clientSignature读取，没有则用任务级pmSig
  var pmSig = '';
  var pmName = '';
  if (project && project.clientSignature && project.clientSignature.sig) {
    pmSig = project.clientSignature.sig;
    pmName = project.clientSignature.name || '';
  }
  if (!pmSig && task.signatures && task.signatures.pmSig) {
    pmSig = task.signatures.pmSig;
  }
  if (!pmName) pmName = (project && project.projectManagerName) || task.projectManagerName || manager || '';"""

    new_pm_sig = """  // 安装单位代表签名：优先从项目级clientSignature读取，没有则用任务级pmSig
  // 【v129】增加容错：签名数据无效或为空时跳过，不报错
  var pmSig = '';
  var pmName = '';
  try {
    if (project && project.clientSignature && typeof project.clientSignature === 'object' && project.clientSignature.sig && typeof project.clientSignature.sig === 'string' && project.clientSignature.sig.length > 0) {
      pmSig = project.clientSignature.sig;
      pmName = (project.clientSignature.name && typeof project.clientSignature.name === 'string') ? project.clientSignature.name : '';
    }
  } catch(e) { console.warn('读取项目级签名失败', e); }
  try {
    if (!pmSig && task.signatures && task.signatures.pmSig && typeof task.signatures.pmSig === 'string' && task.signatures.pmSig.length > 0) {
      pmSig = task.signatures.pmSig;
    }
    if (!pmName) {
      if (project && project.projectManagerName && typeof project.projectManagerName === 'string') {
        pmName = project.projectManagerName;
      } else if (task.projectManagerName && typeof task.projectManagerName === 'string') {
        pmName = task.projectManagerName;
      } else {
        pmName = manager || '';
      }
    }
  } catch(e) { console.warn('读取任务级pm签名失败', e); }"""

    if old_pm_sig in content:
        content = content.replace(old_pm_sig, new_pm_sig)
        fixes_applied.append('Fix 5b: 安装单位代表签名读取容错')
    else:
        print("  [WARN] Fix 5b: 未找到安装单位代表签名读取代码")

    # ============================================================
    # Fix 6: 数据备份机制
    # ============================================================
    # 修改 saveProjects 函数，增加备份
    old_save_projects = """function saveProjects() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(projects));
  } catch(e) {
    console.error('保存数据失败', e);
  }
}"""

    new_save_projects = """function saveProjects() {
  try {
    var dataStr = JSON.stringify(projects);
    localStorage.setItem(STORAGE_KEY, dataStr);
    // 【v129】自动备份
    try {
      localStorage.setItem(STORAGE_KEY + '_backup', dataStr);
    } catch(be) { console.warn('备份保存失败', be); }
  } catch(e) {
    console.error('保存数据失败', e);
  }
}"""

    if old_save_projects in content:
        content = content.replace(old_save_projects, new_save_projects)
        fixes_applied.append('Fix 6a: saveProjects增加备份')
    else:
        print("  [WARN] Fix 6a: 未找到saveProjects函数")

    # 修改 loadProjects 函数，增加备份恢复
    old_load_projects = """function loadProjects() {
  try {
    var stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      var data = JSON.parse(stored);
      // 判断是旧格式(数组)还是新格式
      if (Array.isArray(data)) {
        // 旧格式: tasks 数组，需要迁移
        migrateOldTasks(data);
        return;
      }
      projects = data;
    }
  } catch(e) {
    console.error('加载数据失败', e);
    projects = [];
  }
}"""

    new_load_projects = """function loadProjects() {
  try {
    var stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      var data = JSON.parse(stored);
      // 判断是旧格式(数组)还是新格式
      if (Array.isArray(data)) {
        // 旧格式: tasks 数组，需要迁移
        migrateOldTasks(data);
        return;
      }
      // 【v129】数据异常检查：projects为空但有备份时，自动恢复
      if (!data || !Array.isArray(data) || data.length === 0) {
        var backupData = tryLoadBackup();
        if (backupData) {
          projects = backupData;
          alert('数据已从备份恢复');
          console.log('主数据为空，已从备份恢复');
          return;
        }
      }
      projects = data;
    } else {
      // 主数据不存在，尝试从备份恢复
      var backupData = tryLoadBackup();
      if (backupData) {
        projects = backupData;
        alert('数据已从备份恢复');
        console.log('主数据不存在，已从备份恢复');
        // 立即写回主存储
        saveProjects();
      }
    }
  } catch(e) {
    console.error('加载数据失败，尝试从备份恢复', e);
    var backupData = tryLoadBackup();
    if (backupData) {
      projects = backupData;
      alert('数据已从备份恢复');
      console.log('加载异常，已从备份恢复');
    } else {
      projects = [];
    }
  }
}

function tryLoadBackup() {
  try {
    var backup = localStorage.getItem(STORAGE_KEY + '_backup');
    if (backup) {
      var data = JSON.parse(backup);
      if (data && Array.isArray(data) && data.length > 0) {
        return data;
      }
    }
  } catch(e) { console.warn('备份读取失败', e); }
  return null;
}"""

    if old_load_projects in content:
        content = content.replace(old_load_projects, new_load_projects)
        fixes_applied.append('Fix 6b: loadProjects增加备份恢复')
    else:
        print("  [WARN] Fix 6b: 未找到loadProjects函数")

    # ============================================================
    # 版本号更新 v54→v55
    # ============================================================
    v54_count_before = content.count('v54')
    if v54_count_before > 0:
        # title
        content = content.replace('威特电梯厂检调试记录单V2 v54', '威特电梯厂检调试记录单V2 v55')
        # header-sub (check page)
        content = content.replace("厂检调试记录单V2 v54", "厂检调试记录单V2 v55")
        # openTask中的版本号
        content = content.replace("' · v54'", "' · v55'")
        # 另一种格式
        content = content.replace('厂检调试记录单 V2 v54', '厂检调试记录单 V2 v55')
        # 剩余的v54（如果有的话）
        content = content.replace('v54', 'v55')
        fixes_applied.append(f'版本号 v54→v55（{v54_count_before}处）')

    v55_count = content.count('v55')
    v54_count = content.count('v54')
    print(f"  [INFO] 版本号: v55出现{v55_count}次, v54出现{v54_count}次")

    # ============================================================
    # 验证结果
    # ============================================================
    print("\n===== 修复汇总 =====")
    for f in fixes_applied:
        print(f"  ✓ {f}")
    print(f"\n共应用 {len(fixes_applied)} 项修复")

    if content == original:
        print("\n  [ERROR] 没有任何修改被应用！")
        return False

    if len(fixes_applied) < 6:
        print(f"\n  [WARN] 只应用了 {len(fixes_applied)} 项修复，少于预期的6+项！")

    write_file(filepath, content)
    print(f"\n文件已保存: {filepath}")
    return True


def main():
    base_path = '/app/data/所有对话/主对话/weite-pro-temp'
    file1 = os.path.join(base_path, 'factory-inspection-v2.html')
    file2 = os.path.join(base_path, '威特电梯厂检调试记录单v2.html')

    print("=" * 60)
    print("v129 修复脚本 - 6项修复")
    print("=" * 60)

    # 修改第一个文件
    print("\n【修改 factory-inspection-v2.html】")
    success = fix_all(file1)
    if not success:
        print("修复失败！")
        sys.exit(1)

    # 同步到第二个文件
    print("\n【同步到 威特电梯厂检调试记录单v2.html】")
    content = read_file(file1)
    write_file(file2, content)
    print("  ✓ 文件已同步")

    # 验证两个文件一致
    content1 = read_file(file1)
    content2 = read_file(file2)
    if content1 == content2:
        print("  ✓ 两个文件内容一致")
    else:
        print("  ✗ 两个文件内容不一致！")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("所有修复完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
