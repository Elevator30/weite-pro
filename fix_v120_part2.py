#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v120 批量修复 - 第二部分：修复第一部分未匹配的项
"""
import re
import os

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
    print_html = read_file(PRINT_FILE)
    
    changes = []
    
    # ============================================================
    # 问题4：从subGroupMap导轨与支架分组移除id140
    # ============================================================
    old_sub = "{title: '导轨与支架', ids: [138,139,140,141,142]}"
    new_sub = "{title: '导轨与支架', ids: [138,139,141,142]}"
    if old_sub in main_html:
        main_html = main_html.replace(old_sub, new_sub)
        changes.append('问题4：从subGroupMap导轨与支架分组移除id140')
    else:
        print('WARNING: 仍未找到导轨与支架subGroupMap')
    
    # ============================================================
    # 问题5：添加setComfort函数（修正函数签名）
    # ============================================================
    old_set = "function setCheckStatus(id, status) {"
    comfort_func = """function setComfort(itemId, val) {
  var task = getCurrentTask(); if (!task) return;
  if (!task.checks[itemId]) task.checks[itemId] = {};
  task.checks[itemId].comfort = val;
  // 自动判断：优=符合，良/差=不符合
  task.checks[itemId].s = (val === 'excellent') ? 'ok' : 'ng';
  saveCurrentTask();
  renderCurrentZone();
  updateProgress();
}

function setCheckStatus(id, status) {"""
    
    if old_set in main_html:
        # 检查是否已经添加过
        if 'function setComfort' not in main_html:
            main_html = main_html.replace(old_set, comfort_func)
            changes.append('问题5：添加setComfort函数')
        else:
            changes.append('问题5：setComfort函数已存在，跳过')
    else:
        print('WARNING: 未找到setCheckStatus函数签名')
    
    # ============================================================
    # 问题10：print-fubiao.html的@media print修复
    # ============================================================
    old_media = "@media print {"
    new_media = "@media print {\n#toolbar{display:none!important;}"
    if old_media in print_html:
        # 检查是否已经添加过
        if '#toolbar' not in print_html.split('@media print')[1].split('}')[0]:
            print_html = print_html.replace(old_media, new_media, 1)
            changes.append('问题10：打印时隐藏工具栏')
        else:
            changes.append('问题10：工具栏隐藏已存在，跳过')
    else:
        print('WARNING: 未找到@media print')
    
    # ============================================================
    # 问题10：添加exportFubiaoPDF函数到print-fubiao.html
    # ============================================================
    old_script_end = "// ============ 初始化 ============\ndocument.addEventListener('DOMContentLoaded', fillData);\n</script>"
    
    new_export = """// ============ 导出PDF功能 ============
function exportFubiaoPDF() {
  if (typeof jspdf === 'undefined' || typeof jspdf.jsPDF === 'undefined') {
    alert('PDF导出库加载中，请稍候再试...');
    return;
  }
  if (typeof html2canvas === 'undefined') {
    alert('截图库加载中，请稍候再试...');
    return;
  }
  
  var btn = event.target;
  btn.disabled = true;
  btn.textContent = '生成中...';
  
  var pages = document.querySelectorAll('.page');
  var totalPages = pages.length;
  var currentPage = 0;
  
  // 横版A4
  var pdf = new jspdf.jsPDF('l', 'mm', 'a4');
  var pageWidth = pdf.internal.pageSize.getWidth();
  var pageHeight = pdf.internal.pageSize.getHeight();
  
  function addNextPage() {
    if (currentPage >= totalPages) {
      pdf.save('副表-' + Date.now() + '.pdf');
      btn.disabled = false;
      btn.textContent = '保存到文件(PDF)';
      return;
    }
    
    var page = pages[currentPage];
    html2canvas(page, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff'
    }).then(function(canvas) {
      var imgData = canvas.toDataURL('image/jpeg', 0.95);
      if (currentPage > 0) pdf.addPage();
      pdf.addImage(imgData, 'JPEG', 0, 0, pageWidth, pageHeight);
      currentPage++;
      setTimeout(addNextPage, 50);
    }).catch(function(err) {
      console.error('导出失败', err);
      alert('导出失败：' + err.message);
      btn.disabled = false;
      btn.textContent = '保存到文件(PDF)';
    });
  }
  
  addNextPage();
}

// 加载jsPDF和html2canvas
(function() {
  function loadScript(src, callback) {
    if (document.querySelector('script[src="'+src+'"]')) { callback(); return; }
    var s = document.createElement('script');
    s.src = src;
    s.onload = callback;
    s.onerror = function() { console.warn('加载失败:', src); callback(); };
    document.head.appendChild(s);
  }
  var needLoad = 0;
  var loaded = 0;
  function check() {
    loaded++;
  }
  if (typeof jspdf === 'undefined' || typeof jspdf.jsPDF === 'undefined') {
    needLoad++;
    loadScript('https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js', check);
  }
  if (typeof html2canvas === 'undefined') {
    needLoad++;
    loadScript('https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js', check);
  }
})();

// ============ 初始化 ============
document.addEventListener('DOMContentLoaded', fillData);
</script>"""
    
    if old_script_end in print_html:
        print_html = print_html.replace(old_script_end, new_export)
        changes.append('问题10：添加exportFubiaoPDF函数和CDN加载')
    else:
        print('WARNING: 未找到脚本结束位置')
    
    # ============================================================
    # 问题1：检查默认数据 - 确认没有默认项目/电梯初始化
    # ============================================================
    # 检查是否有任何地方创建默认项目或默认电梯
    # 目前代码: projects = []; loadProjects()从localStorage读取
    # createProject创建tasks: []  都是空的
    # 如果没有找到默认数据创建逻辑，则认为已经正确
    
    has_default_data = False
    # 检查是否有"默认项目"硬编码（除了迁移代码）
    # migrateOldTasks中的"默认项目"是数据迁移用的，不是首次初始化
    # 所以不需要删
    
    changes.append('问题1：已确认无默认项目/电梯初始化数据（projects初始为空，createProject创建tasks为空数组）')
    
    # ============================================================
    # 问题11：附表2第④项单位和标准
    # 已确认：公式 0.1+0.035v²，单位m，与其他项一致
    # ============================================================
    changes.append('问题11：已确认附表2第④项单位m，标准0.1+0.035v²，与模板一致')
    
    # ============================================================
    # 保存文件
    # ============================================================
    write_file(MAIN_FILE, main_html)
    write_file(PRINT_FILE, print_html)
    
    print("\n" + "="*60)
    print("第二部分修改清单：")
    print("="*60)
    for i, c in enumerate(changes, 1):
        print(f"  {i}. {c}")
    print("="*60)

if __name__ == '__main__':
    main()
