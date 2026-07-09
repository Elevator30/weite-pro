#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v129 综合修复脚本：7项修复
1. 打印副表报错 - 签名名称校验容错
2. 厂检结论页备注 - 添加备注编辑区域
3. 备注打印到通知单 - 通知单显示备注
4. 去掉相关人员签名UI
5. 暂时保存改保存
6. 数据自动备份机制
7. 数据丢失排查修复
"""

import sys
import os

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
    # Fix 5: 暂时保存改保存 (先做简单的)
    # ============================================================
    old_save_btn = '<button class="btm-save" onclick="saveCurrentTask();showToast(\'已保存\')" style="flex:1.5;">暂时保存</button>'
    new_save_btn = '<button class="btm-save" onclick="saveCurrentTask();showToast(\'已保存\')" style="flex:1.5;">保存</button>'
    if old_save_btn in content:
        content = content.replace(old_save_btn, new_save_btn)
        fixes_applied.append('Fix 5: 暂时保存→保存')
    else:
        print("  [WARN] Fix 5: 未找到暂时保存按钮")

    # ============================================================
    # Fix 6: 数据自动备份机制
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
    // 自动备份
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
      // 数据异常检查：projects为空但有备份时，自动恢复
      if (!data || !Array.isArray(data) || data.length === 0) {
        var backupData = tryLoadBackup();
        if (backupData) {
          projects = backupData;
          showToast('检测到主数据异常，已从备份恢复');
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
        showToast('检测到主数据丢失，已从备份恢复');
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
      showToast('数据加载失败，已从备份恢复');
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
    # Fix 1: 打印副表报错 - 签名名称校验容错
    # 在 buildNoticeFullHTML 函数中增加签名相关的容错处理
    # ============================================================
    # 修改检验人员签名读取部分，增加try-catch容错
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
  var inspSig = '';
  var inspName = '';
  try {
    var _inspStored = localStorage.getItem(INSPECTOR_SIG_KEY);
    if (_inspStored && typeof _inspStored === 'string' && _inspStored.length > 0) {
      var _inspObj = JSON.parse(_inspStored);
      if (_inspObj && typeof _inspObj === 'object' && _inspObj.sig && typeof _inspObj.sig === 'string' && _inspObj.sig.length > 0) {
        inspSig = _inspObj.sig;
        inspName = (_inspObj.name && typeof _inspObj.name === 'string') ? _inspObj.name : '';
      }
    }
  } catch(e) { console.warn('读取全局检验人员签名失败', e); }
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
  } catch(e) { console.warn('读取任务级签名失败', e); }"""

    if old_insp_sig in content:
        content = content.replace(old_insp_sig, new_insp_sig)
        fixes_applied.append('Fix 1a: 检验人员签名读取容错')
    else:
        print("  [WARN] Fix 1a: 未找到检验人员签名读取代码")

    # 修改安装单位代表签名读取部分，增加容错
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
        fixes_applied.append('Fix 1b: 安装单位代表签名读取容错')
    else:
        print("  [WARN] Fix 1b: 未找到安装单位代表签名读取代码")

    # ============================================================
    # Fix 4: 去掉相关人员签名UI
    # ============================================================
    # 隐藏相关人员签名区域（保留代码但UI不显示）
    old_related_sign = """  // 项目管理人员/安装人员 - 姓名输入 + 点击弹窗签名
  var pmSigData = task.signatures.pmSig || '';
  var installerSigData = task.signatures.installerSig || '';
  html += '<div style="background:#f8fff8;border-radius:12px;padding:14px;margin-bottom:12px;border:1px solid #e2e8f0;">';
  // （检验人员全局签名和项目级签名提示框已移除，签名入口在顶部菜单）
  html += '<div style="font-size:13px;font-weight:600;margin-bottom:8px;">相关人员签名</div>';
  // 安装人员姓名输入
  html += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">';
  // 安装人员姓名（从项目读取，不显示输入框）
  var _proj = getCurrentProject(); var _installerName = (_proj && _proj.installer) || task.installerName || "";
  // 项目管理人员姓名输入
  html += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">';
  // 项目管理人员姓名（从项目读取，不显示输入框）
  var _pmName = (_proj && _proj.projectManagerName) || task.projectManagerName || '';
  if (pmSigData) {
    html += '<div style="border:1px solid #e2e8f0;border-radius:8px;background:#fff;padding:10px;margin-bottom:10px;min-height:100px;display:flex;align-items:center;justify-content:center;">';
    html += '<img src="' + pmSigData + '" style="max-height:90px;max-width:100%;">';
    html += '</div>';
  } else {
    html += '<div style="border:1px dashed #ccc;border-radius:8px;background:#fafafa;padding:20px;text-align:center;color:#aaa;font-size:12px;margin-bottom:8px;">暂无签名</div>';
  }
  html += '<button onclick="openSignZoneModal(\\'pm\\')" style="width:100%;padding:10px;background:#38a169;color:#fff;border:none;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;">✍️ ' + (pmSigData ? '重新签名' : '点击签名') + '</button>';
  html += '</div>';


  html += '</div>';"""

    new_related_sign = """  // 项目管理人员/安装人员 - 姓名输入 + 点击弹窗签名
  // 【v129】相关人员签名区域UI已隐藏，代码保留便于后续恢复
  var pmSigData = task.signatures.pmSig || '';
  var installerSigData = task.signatures.installerSig || '';
  html += '<div style="background:#f8fff8;border-radius:12px;padding:14px;margin-bottom:12px;border:1px solid #e2e8f0;display:none;">';
  // （检验人员全局签名和项目级签名提示框已移除，签名入口在顶部菜单）
  html += '<div style="font-size:13px;font-weight:600;margin-bottom:8px;">相关人员签名</div>';
  // 安装人员姓名输入
  html += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">';
  // 安装人员姓名（从项目读取，不显示输入框）
  var _proj = getCurrentProject(); var _installerName = (_proj && _proj.installer) || task.installerName || "";
  // 项目管理人员姓名输入
  html += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">';
  // 项目管理人员姓名（从项目读取，不显示输入框）
  var _pmName = (_proj && _proj.projectManagerName) || task.projectManagerName || '';
  if (pmSigData) {
    html += '<div style="border:1px solid #e2e8f0;border-radius:8px;background:#fff;padding:10px;margin-bottom:10px;min-height:100px;display:flex;align-items:center;justify-content:center;">';
    html += '<img src="' + pmSigData + '" style="max-height:90px;max-width:100%;">';
    html += '</div>';
  } else {
    html += '<div style="border:1px dashed #ccc;border-radius:8px;background:#fafafa;padding:20px;text-align:center;color:#aaa;font-size:12px;margin-bottom:8px;">暂无签名</div>';
  }
  html += '<button onclick="openSignZoneModal(\\'pm\\')" style="width:100%;padding:10px;background:#38a169;color:#fff;border:none;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;">✍️ ' + (pmSigData ? '重新签名' : '点击签名') + '</button>';
  html += '</div>';


  html += '</div>';"""

    if old_related_sign in content:
        content = content.replace(old_related_sign, new_related_sign)
        fixes_applied.append('Fix 4: 隐藏相关人员签名UI')
    else:
        print("  [WARN] Fix 4: 未找到相关人员签名区域代码")
        # 尝试更短的匹配
        print("  [INFO] 尝试部分匹配...")

    # ============================================================
    # Fix 2: 厂检结论页添加备注编辑区域
    # 在厂检结论区域（整改期限下方）添加备注编辑框
    # ============================================================
    old_rectify_section = """  // 整改期限
  html += '<div style="margin-bottom:20px;" id="rectifySection">';
  html += '<div style="font-size:15px;font-weight:700;margin-bottom:10px;color:#d69e2e;">整改期限</div>';
  html += '<div style="display:flex;align-items:center;gap:8px;">';
  html += '<span style="font-size:13px;">以上问题请于</span>';
  html += '<input type="date" id="signRectifyDeadline" value="' + (task.rectifyDeadline||'') + '" onchange="setRectifyDeadline(this.value)" style="font-size:14px;padding:8px 10px;border:1px solid #ddd;border-radius:8px;flex:1;">';
  html += '<span style="font-size:13px;">前整改完毕</span>';
  html += '</div></div>';

  // 签字区域"""

    new_rectify_section = """  // 整改期限
  html += '<div style="margin-bottom:20px;" id="rectifySection">';
  html += '<div style="font-size:15px;font-weight:700;margin-bottom:10px;color:#d69e2e;">整改期限</div>';
  html += '<div style="display:flex;align-items:center;gap:8px;">';
  html += '<span style="font-size:13px;">以上问题请于</span>';
  html += '<input type="date" id="signRectifyDeadline" value="' + (task.rectifyDeadline||'') + '" onchange="setRectifyDeadline(this.value)" style="font-size:14px;padding:8px 10px;border:1px solid #ddd;border-radius:8px;flex:1;">';
  html += '<span style="font-size:13px;">前整改完毕</span>';
  html += '</div></div>';

  // 备注
  html += '<div style="margin-bottom:20px;">';
  html += '<div style="font-size:15px;font-weight:700;margin-bottom:10px;color:#667eea;">备注</div>';
  html += '<textarea id="taskRemark" rows="4" placeholder="请输入备注信息..." oninput="setTaskRemark(this.value)" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;font-size:14px;font-family:inherit;resize:vertical;box-sizing:border-box;line-height:1.5;">' + (task.remark || '') + '</textarea>';
  html += '</div>';

  // 签字区域"""

    if old_rectify_section in content:
        content = content.replace(old_rectify_section, new_rectify_section)
        fixes_applied.append('Fix 2a: 厂检结论页添加备注编辑区')
    else:
        print("  [WARN] Fix 2a: 未找到整改期限区域代码")

    # 添加 setTaskRemark 函数（在 setRectifyDeadline 函数后面）
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

function setTaskRemark(val) {
  var task = getCurrentTask();
  if (!task) return;
  task.remark = val;
  saveProjects();
}"""

    if old_set_rectify in content:
        content = content.replace(old_set_rectify, new_set_rectify)
        fixes_applied.append('Fix 2b: 添加setTaskRemark函数')
    else:
        print("  [WARN] Fix 2b: 未找到setRectifyDeadline函数")

    # ============================================================
    # Fix 3: 备注打印到通知单
    # 在通知单底部备注区域显示任务备注
    # ============================================================
    # 修改 buildNoticeFullHTML 中的备注行，增加任务备注显示
    old_remark_row = """  // 行38：备注（B:G合并，上下都有边）
  h += '<tr>';
  h += '<td style="border:1px solid #000;padding:2px 3px;color:#666;height:50px;" colspan="6">备注：①本通知书一式三联，检验机构、安装单位、项目管理各执一联。②整改完成后，请将本通知书返还检验人员确认。③如有异议，请在收到本通知书之日起5个工作日内提出。</td>';
  h += '</tr>';"""

    new_remark_row = """  // 行38：备注（含任务备注，B:G合并，上下都有边）
  var taskRemarkText = '';
  try {
    if (task.remark && typeof task.remark === 'string' && task.remark.trim().length > 0) {
      taskRemarkText = task.remark;
    }
  } catch(e) { console.warn('读取任务备注失败', e); }
  h += '<tr>';
  if (taskRemarkText) {
    h += '<td style="border:1px solid #000;padding:4px 6px;color:#333;height:auto;vertical-align:top;" colspan="6">';
    h += '<div style="font-weight:bold;margin-bottom:4px;">任务备注：</div>';
    h += '<div style="white-space:pre-wrap;line-height:1.6;">' + escHtml(taskRemarkText) + '</div>';
    h += '<div style="margin-top:6px;color:#666;font-size:8px;">备注：①本通知书一式三联，检验机构、安装单位、项目管理各执一联。②整改完成后，请将本通知书返还检验人员确认。③如有异议，请在收到本通知书之日起5个工作日内提出。</div>';
    h += '</td>';
  } else {
    h += '<td style="border:1px solid #000;padding:2px 3px;color:#666;height:50px;" colspan="6">备注：①本通知书一式三联，检验机构、安装单位、项目管理各执一联。②整改完成后，请将本通知书返还检验人员确认。③如有异议，请在收到本通知书之日起5个工作日内提出。</td>';
  }
  h += '</tr>';"""

    if old_remark_row in content:
        content = content.replace(old_remark_row, new_remark_row)
        fixes_applied.append('Fix 3a: 通知单PDF显示任务备注')
    else:
        print("  [WARN] Fix 3a: 未找到通知单备注行代码")

    # 同时修改 Excel 导出中的备注（在 exportNoticeExcel 中）
    # 在填完C35后增加备注填写
    old_excel_installer = """      // 填安装单位代表 (C35)
      var installerName = task.installerName || (proj && proj.installer) || task.installerSign || '';
      ws.getCell('C35').value = installerName;

      // 签收日期 (G35)"""

    new_excel_installer = """      // 填安装单位代表 (C35)
      var installerName = task.installerName || (proj && proj.installer) || task.installerSign || '';
      ws.getCell('C35').value = installerName;

      // 填任务备注 (B37开始，在签收日期下方)
      if (task.remark && task.remark.trim().length > 0) {
        ws.getCell('B37').value = '任务备注：' + task.remark;
        ws.getCell('B37').alignment = { wrapText: true, vertical: 'top' };
      }

      // 签收日期 (G35)"""

    if old_excel_installer in content:
        content = content.replace(old_excel_installer, new_excel_installer)
        fixes_applied.append('Fix 3b: 通知单Excel显示任务备注')
    else:
        print("  [WARN] Fix 3b: 未找到Excel安装单位代表代码")

    # ============================================================
    # Fix 7: 数据丢失排查修复
    # ============================================================
    # 7a: 确保新建任务时项目基本信息完整写入
    old_create_task_info = """  var task = {
    id: Date.now(),
    prodNo: prodNo,
    addr: proj.name, // 项目名称从项目读取
    model: document.getElementById('newModel').value.trim(),
    load: document.getElementById('newLoad').value.trim(),
    speed: document.getElementById('newSpeed').value.trim(),
    liftNo: document.getElementById('newLiftNo').value.trim(),
    installer: proj.installer, // 从项目读取
    installAddr: proj.installAddr, // 从项目读取
    manager: proj.projectManagerName, // 从项目读取
    checkDate: document.getElementById('newCheckDate').value,"""

    new_create_task_info = """  var task = {
    id: Date.now(),
    prodNo: prodNo,
    addr: proj.name || '', // 项目名称从项目读取
    projectName: proj.name || '', // 冗余存储项目名，防止项目信息丢失
    model: document.getElementById('newModel').value.trim(),
    load: document.getElementById('newLoad').value.trim(),
    speed: document.getElementById('newSpeed').value.trim(),
    liftNo: document.getElementById('newLiftNo').value.trim(),
    elevatorNo: document.getElementById('newLiftNo').value.trim(), // 冗余：电梯编号
    installer: proj.installer || '', // 从项目读取
    installAddr: proj.installAddr || '', // 从项目读取
    projectManagerName: proj.projectManagerName || '', // 从项目读取
    manager: proj.projectManagerName || '', // 从项目读取
    checkDate: document.getElementById('newCheckDate').value,"""

    if old_create_task_info in content:
        content = content.replace(old_create_task_info, new_create_task_info)
        fixes_applied.append('Fix 7a: 新建任务时完整保存项目信息')
    else:
        print("  [WARN] Fix 7a: 未找到新建任务信息代码")

    # 7b: 确保保存任务时配置数据完整
    # 在 saveCurrentTask 中确保 configParts 和电梯配置数据被保存
    old_save_current = """function saveCurrentTask() {
  saveProjects();
  renderRegionGrid();
  updateProgress();
}"""

    new_save_current = """function saveCurrentTask() {
  // 保存前确保任务配置数据完整
  var task = getCurrentTask();
  var proj = getCurrentProject();
  if (task && proj) {
    // 确保项目基本信息冗余存储在任务中（防止项目信息丢失）
    if (!task.projectName && proj.name) task.projectName = proj.name;
    if (!task.installer && proj.installer) task.installer = proj.installer;
    if (!task.installAddr && proj.installAddr) task.installAddr = proj.installAddr;
    if (!task.projectManagerName && proj.projectManagerName) task.projectManagerName = proj.projectManagerName;
    if (!task.manager && proj.projectManagerName) task.manager = proj.projectManagerName;
    // 确保电梯配置表数据保存
    if (typeof configPartsData !== 'undefined' && configPartsData && Object.keys(configPartsData).length > 0) {
      task.configParts = JSON.parse(JSON.stringify(configPartsData));
    }
    // 确保elevatorNo字段存在
    if (!task.elevatorNo && task.liftNo) task.elevatorNo = task.liftNo;
    if (!task.liftNo && task.elevatorNo) task.liftNo = task.elevatorNo;
    // 确保备注字段存在
    if (task.remark === undefined) task.remark = '';
  }
  saveProjects();
  renderRegionGrid();
  updateProgress();
}"""

    if old_save_current in content:
        content = content.replace(old_save_current, new_save_current)
        fixes_applied.append('Fix 7b: saveCurrentTask确保数据完整')
    else:
        print("  [WARN] Fix 7b: 未找到saveCurrentTask函数")

    # 7c: 确保打开任务时配置数据正确加载
    old_open_task = """function openTask(index) {
  currentTaskIndex = index;
  var task = getCurrentTask();
  if (!task) return;
  // 恢复配置单数据
  if (task.configParts) {
    configPartsData = task.configParts;
  }
  document.getElementById('checkProdNo').textContent = task.prodNo || '未编号';
  document.getElementById('checkHeaderSub').textContent = (task.model ? task.model + ' · v54' : '厂检调试记录单V2 v54');
  goPage('check');
  renderZoneTabs();
  switchZone(0);
  updateProgress();
}"""

    new_open_task = """function openTask(index) {
  currentTaskIndex = index;
  var task = getCurrentTask();
  if (!task) return;
  var proj = getCurrentProject();
  // 恢复配置单数据
  if (task.configParts) {
    configPartsData = JSON.parse(JSON.stringify(task.configParts));
  } else {
    configPartsData = {};
  }
  // 确保任务有完整的项目信息（从项目补全）
  if (proj) {
    if (!task.projectName && proj.name) task.projectName = proj.name;
    if (!task.installer && proj.installer) task.installer = proj.installer;
    if (!task.installAddr && proj.installAddr) task.installAddr = proj.installAddr;
    if (!task.projectManagerName && proj.projectManagerName) task.projectManagerName = proj.projectManagerName;
    if (!task.manager && proj.projectManagerName) task.manager = proj.projectManagerName;
  }
  // 确保elevatorNo和liftNo同步
  if (!task.elevatorNo && task.liftNo) task.elevatorNo = task.liftNo;
  if (!task.liftNo && task.elevatorNo) task.liftNo = task.elevatorNo;
  // 确保remark字段存在
  if (task.remark === undefined) task.remark = '';
  document.getElementById('checkProdNo').textContent = task.prodNo || '未编号';
  document.getElementById('checkHeaderSub').textContent = (task.model ? task.model + ' · v55' : '厂检调试记录单V2 v55');
  goPage('check');
  renderZoneTabs();
  switchZone(0);
  updateProgress();
}"""

    if old_open_task in content:
        content = content.replace(old_open_task, new_open_task)
        fixes_applied.append('Fix 7c: openTask确保数据完整')
    else:
        print("  [WARN] Fix 7c: 未找到openTask函数")

    # 7d: 确保项目名称不会变成"默认项目"
    # 检查 migrateOldTasks 中的默认项目名
    old_migrate_name = "    name: first.addr || '默认项目',"
    new_migrate_name = "    name: first.addr || first.projectName || first.project_name || '默认项目',"
    if old_migrate_name in content:
        content = content.replace(old_migrate_name, new_migrate_name)
        fixes_applied.append('Fix 7d: 迁移时优先使用项目名')
    else:
        print("  [WARN] Fix 7d: 未找到迁移时的默认项目名代码")

    # 7e: 确保导入配置单后数据保存
    # 在 handleConfigUpload 的保存逻辑中确保数据完整
    old_config_save = """  // 如果配置单有载重，自动填入附表5"""
    new_config_save = """  // 保存配置单数据到configPartsData（已在解析时设置）
  // 确保当前任务也保存配置单数据
  var _curTask = getCurrentTask();
  if (_curTask && Object.keys(configPartsData).length > 0) {
    _curTask.configParts = JSON.parse(JSON.stringify(configPartsData));
    // 从配置单提取基本信息
    if (configPartsData['产品编号'] && !_curTask.prodNo) _curTask.prodNo = configPartsData['产品编号'];
    if (configPartsData['产品型号'] && !_curTask.model) _curTask.model = configPartsData['产品型号'];
    if (configPartsData['项目名称'] && !_curTask.projectName) _curTask.projectName = configPartsData['项目名称'];
    saveProjects();
  }

  // 如果配置单有载重，自动填入附表5"""

    if old_config_save in content:
        content = content.replace(old_config_save, new_config_save)
        fixes_applied.append('Fix 7e: 导入配置单后保存数据')
    else:
        print("  [WARN] Fix 7e: 未找到配置单载重填入代码")

    # ============================================================
    # 版本号更新 v54→v55
    # ============================================================
    version_fixes = 0
    # title
    if 'v54' in content and '厂检调试记录单V2 v54' in content:
        content = content.replace('威特电梯厂检调试记录单V2 v54', '威特电梯厂检调试记录单V2 v55')
        version_fixes += 1
    # header-sub (check page)
    content = content.replace("厂检调试记录单V2 v54", "厂检调试记录单V2 v55")
    # openTask中的版本号（已经在上面的Fix 7c中改了，这里再确认其他地方）
    content = content.replace("' · v54'", "' · v55'")
    # 另一个header位置
    content = content.replace('厂检调试记录单 V2 v54', '厂检调试记录单 V2 v55')

    # 统计版本号修改
    v55_count = content.count('v55')
    v54_count = content.count('v54')
    print(f"  [INFO] 版本号: v55出现{v55_count}次, v54出现{v54_count}次")

    if v55_count > 0:
        fixes_applied.append('版本号 v54→v55')

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

    write_file(filepath, content)
    print(f"\n文件已保存: {filepath}")
    return True

def main():
    base_path = '/app/data/所有对话/主对话/weite-pro-temp'
    file1 = os.path.join(base_path, 'factory-inspection-v2.html')
    file2 = os.path.join(base_path, '威特电梯厂检调试记录单v2.html')

    print("=" * 60)
    print("v129 综合修复 - 7项修复")
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
