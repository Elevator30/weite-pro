#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v127 修复脚本 - 修复新建项目按钮点击无反应
修复内容：
1. showNewProject 函数优化：将 openMoModal 移到最前面，用 try-catch 包裹后续初始化代码
2. showEditProject 函数优化：同样将 openMoModal 移到前面，添加空值检查
3. saveSig 函数代码结构优化：修复 v126 引入的缩进问题
4. 给 moNewProject 弹窗添加更高的 z-index 内联样式，确保不被遮挡
"""
import re
import os
import sys

MAIN_FILE = '/app/data/所有对话/主对话/weite-pro-temp/factory-inspection-v2.html'
ENTRY_FILE = '/app/data/所有对话/主对话/weite-pro-temp/威特电梯厂检调试记录单v2.html'

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def fix_showNewProject(content):
    """修复 showNewProject 函数：将 openMoModal 移到最前面，用 try-catch 包裹后续代码"""
    old_func = '''function showNewProject() {
  editingProjectIndex = -1;
  var titleEl = document.getElementById('moNewProjectTitle');
  if (titleEl) titleEl.textContent = '新建项目';
  openMoModal('moNewProject');
  var nameEl = document.getElementById('newProjName');
  if (nameEl) nameEl.value = '';
  var instEl = document.getElementById('newProjInstaller');
  if (instEl) instEl.value = '';
  var mgrEl = document.getElementById('newProjManager');
  if (mgrEl) mgrEl.value = '';
  var addrEl = document.getElementById('newProjAddrDetail');
  if (addrEl) addrEl.value = '';
  var remarkEl = document.getElementById('newProjRemark');
  if (remarkEl) remarkEl.value = '';
  initProvinceSelect('newProjProvince', 'newProjCity', 'newProjDistrict');
}'''

    new_func = '''function showNewProject() {
  editingProjectIndex = -1;
  openMoModal('moNewProject');
  try {
    var titleEl = document.getElementById('moNewProjectTitle');
    if (titleEl) titleEl.textContent = '新建项目';
    var nameEl = document.getElementById('newProjName');
    if (nameEl) nameEl.value = '';
    var instEl = document.getElementById('newProjInstaller');
    if (instEl) instEl.value = '';
    var mgrEl = document.getElementById('newProjManager');
    if (mgrEl) mgrEl.value = '';
    var addrEl = document.getElementById('newProjAddrDetail');
    if (addrEl) addrEl.value = '';
    var remarkEl = document.getElementById('newProjRemark');
    if (remarkEl) remarkEl.value = '';
    initProvinceSelect('newProjProvince', 'newProjCity', 'newProjDistrict');
  } catch(e) {
    console.error('showNewProject init error:', e);
  }
}'''

    if old_func in content:
        content = content.replace(old_func, new_func)
        print("  [OK] 修复 showNewProject 函数")
        return content, True
    else:
        print("  [WARN] 未找到 showNewProject 函数")
        return content, False


def fix_showEditProject(content):
    """修复 showEditProject 函数：将 openMoModal 移到前面，添加空值检查"""
    old_func = '''function showEditProject(index) {
  editingProjectIndex = index;
  var titleEl = document.getElementById('moNewProjectTitle');
  if (titleEl) titleEl.textContent = '编辑项目';
  var proj = projects[index];
  if (!proj) return;
  openMoModal('moNewProject');
  document.getElementById('newProjName').value = proj.name || '';
  document.getElementById('newProjInstaller').value = proj.installer || '';
  document.getElementById('newProjManager').value = proj.projectManagerName || '';
  document.getElementById('newProjRemark').value = proj.remark || '';
  initProvinceSelect('newProjProvince', 'newProjCity', 'newProjDistrict');
  setRegionSelects('newProjProvince', 'newProjCity', 'newProjDistrict', proj.installAddr || '');
  // 提取详细地址（省市区之后的部分）
  var detail = '';
  var addr = proj.installAddr || '';
  var pVal = document.getElementById('newProjProvince').value || '';
  var cVal = document.getElementById('newProjCity').value || '';
  var dVal = document.getElementById('newProjDistrict').value || '';
  var prefix = pVal + cVal + dVal;
  if (addr.indexOf(prefix) === 0) {
    detail = addr.substring(prefix.length);
  }
  document.getElementById('newProjAddrDetail').value = detail;
}'''

    new_func = '''function showEditProject(index) {
  editingProjectIndex = index;
  var proj = projects[index];
  if (!proj) return;
  openMoModal('moNewProject');
  try {
    var titleEl = document.getElementById('moNewProjectTitle');
    if (titleEl) titleEl.textContent = '编辑项目';
    var nameEl = document.getElementById('newProjName');
    if (nameEl) nameEl.value = proj.name || '';
    var instEl = document.getElementById('newProjInstaller');
    if (instEl) instEl.value = proj.installer || '';
    var mgrEl = document.getElementById('newProjManager');
    if (mgrEl) mgrEl.value = proj.projectManagerName || '';
    var remarkEl = document.getElementById('newProjRemark');
    if (remarkEl) remarkEl.value = proj.remark || '';
    initProvinceSelect('newProjProvince', 'newProjCity', 'newProjDistrict');
    setRegionSelects('newProjProvince', 'newProjCity', 'newProjDistrict', proj.installAddr || '');
    // 提取详细地址（省市区之后的部分）
    var detail = '';
    var addr = proj.installAddr || '';
    var pSel = document.getElementById('newProjProvince');
    var cSel = document.getElementById('newProjCity');
    var dSel = document.getElementById('newProjDistrict');
    var pVal = pSel ? pSel.value || '' : '';
    var cVal = cSel ? cSel.value || '' : '';
    var dVal = dSel ? dSel.value || '' : '';
    var prefix = pVal + cVal + dVal;
    if (addr.indexOf(prefix) === 0) {
      detail = addr.substring(prefix.length);
    }
    var addrDetailEl = document.getElementById('newProjAddrDetail');
    if (addrDetailEl) addrDetailEl.value = detail;
  } catch(e) {
    console.error('showEditProject init error:', e);
  }
}'''

    if old_func in content:
        content = content.replace(old_func, new_func)
        print("  [OK] 修复 showEditProject 函数")
        return content, True
    else:
        print("  [WARN] 未找到 showEditProject 函数")
        return content, False


def fix_saveSig_indent(content):
    """修复 saveSig 函数中 v126 引入的缩进问题"""
    old_code = '''  }
  
// 项目管理/安装人员签字（项目级）- 保存到 proj.clientSignature
  if (signZoneTarget === 'client') {'''

    new_code = '''  }
  
  // 项目管理/安装人员签字（项目级）- 保存到 proj.clientSignature
  if (signZoneTarget === 'client') {'''

    if old_code in content:
        content = content.replace(old_code, new_code)
        print("  [OK] 修复 saveSig 函数缩进")
        return content, True
    else:
        print("  [WARN] 未找到 saveSig 缩进问题（可能已修复）")
        return content, False


def fix_moNewProject_zindex(content):
    """给 moNewProject 弹窗添加更高的 z-index，确保不被遮挡"""
    old_html = '<div class="mo" id="moNewProject">'
    new_html = '<div class="mo" id="moNewProject" style="z-index:1000;">'

    if old_html in content:
        content = content.replace(old_html, new_html)
        print("  [OK] 修复 moNewProject z-index")
        return content, True
    else:
        # 可能已经有 style 了
        if 'id="moNewProject"' in content:
            print("  [WARN] moNewProject 已有其他样式，跳过 z-index 修改")
        else:
            print("  [WARN] 未找到 moNewProject 弹窗")
        return content, False


def fix_file(filepath):
    print(f"\n处理文件: {os.path.basename(filepath)}")
    content = read_file(filepath)
    original = content
    fixed_count = 0

    content, fixed = fix_showNewProject(content)
    if fixed: fixed_count += 1

    content, fixed = fix_showEditProject(content)
    if fixed: fixed_count += 1

    content, fixed = fix_saveSig_indent(content)
    if fixed: fixed_count += 1

    content, fixed = fix_moNewProject_zindex(content)
    if fixed: fixed_count += 1

    if content != original:
        write_file(filepath, content)
        print(f"  文件已保存，共修复 {fixed_count} 项")
        return True
    else:
        print("  无修改")
        return False


def main():
    print("=" * 60)
    print("v127 修复脚本 - 修复新建项目按钮点击无反应")
    print("=" * 60)

    fix1 = fix_file(MAIN_FILE)
    fix2 = fix_file(ENTRY_FILE)

    print("\n" + "=" * 60)
    if fix1 or fix2:
        print("修复完成！")
    else:
        print("未执行任何修改")
    print("=" * 60)


if __name__ == '__main__':
    main()
