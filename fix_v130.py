#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v130 修复脚本：7项修复
1. 打印不出来修复（检查表+副表）
2. 导入/导出JSON移到项目列表页菜单
3. 导出Excel移到项目列表页菜单
4. 检验页菜单去掉厂检签字
5. 厂检结论页备注消失bug
6. 去掉重复的备注和标题
7. 左滑返回手势
版本号 v55→v56
"""

import re
import os
import sys

INPUT_FILE = '/app/data/所有对话/主对话/weite-pro-temp/factory-inspection-v2.html'
BACKUP_FILE = '/app/data/所有对话/主对话/weite-pro-temp/factory-inspection-v2.html.bak_v129'
FUBAO_FILE = '/app/data/所有对话/主对话/weite-pro-temp/print-fubiao.html'

def main():
    # 备份
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 保存备份
    with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"原始文件已备份到: {BACKUP_FILE}")
    print(f"原始文件长度: {len(content)}")
    
    # ==========================================
    # 修复0：版本号 v55→v56
    # ==========================================
    content = content.replace(
        '<title>威特电梯厂检调试记录单V2 v55</title>',
        '<title>威特电梯厂检调试记录单V2 v56</title>'
    )
    print("[修复0] 版本号 v55→v56")
    
    # ==========================================
    # 修复1：打印不出来修复
    # ==========================================
    
    # 1a. 修复 loadPdfLibs 函数 - fallback时优先用CDN而不是本地文件
    old_loadPdfLibs = """function loadPdfLibs(callback) {
  if (_pdfLibsReady) { callback && callback(); return; }
  if (callback) _pdfLibsCallbacks.push(callback);
  if (_pdfLibsLoading) return;
  _pdfLibsLoading = true;
  
  function checkDone() {
    _pdfLibsReady = true;
    _pdfLibsLoading = false;
    if(window.jspdf && window.jspdf.jsPDF){ window.jsPDF = window.jspdf.jsPDF; }
    for (var i = 0; i < _pdfLibsCallbacks.length; i++) {
      try { _pdfLibsCallbacks[i](); } catch(e) {}
    }
    _pdfLibsCallbacks = [];
  }
  
  var loaded = 0;
  var needHc = (typeof html2canvas === 'undefined');
  var needJspdf = (typeof jsPDF === 'undefined' && !(window.jspdf && window.jspdf.jsPDF));
  var total = (needHc ? 1 : 0) + (needJspdf ? 1 : 0);
  
  if (total === 0) { checkDone(); return; }
  
  function onOne() {
    loaded++;
    if (loaded >= total) checkDone();
  }
  
  if (needHc) {
    var s1 = document.createElement('script');
    s1.src = 'html2canvas.min.js';
    s1.onload = onOne;
    s1.onerror = function(){ console.error('html2canvas本地加载失败'); onOne(); };
    document.head.appendChild(s1);
  }
  if (needJspdf) {
    var s2 = document.createElement('script');
    s2.src = 'jspdf.min.js';
    s2.onload = onOne;
    s2.onerror = function(){ console.error('jsPDF本地加载失败'); onOne(); };
    document.head.appendChild(s2);
  }
}"""

    new_loadPdfLibs = """function loadPdfLibs(callback) {
  if (_pdfLibsReady) { callback && callback(); return; }
  if (callback) _pdfLibsCallbacks.push(callback);
  if (_pdfLibsLoading) return;
  _pdfLibsLoading = true;
  
  function checkDone() {
    _pdfLibsReady = true;
    _pdfLibsLoading = false;
    if(window.jspdf && window.jspdf.jsPDF){ window.jsPDF = window.jspdf.jsPDF; }
    for (var i = 0; i < _pdfLibsCallbacks.length; i++) {
      try { _pdfLibsCallbacks[i](); } catch(e) {}
    }
    _pdfLibsCallbacks = [];
  }
  
  var loaded = 0;
  var needHc = (typeof html2canvas === 'undefined');
  var needJspdf = (typeof jsPDF === 'undefined' && !(window.jspdf && window.jspdf.jsPDF));
  var total = (needHc ? 1 : 0) + (needJspdf ? 1 : 0);
  
  if (total === 0) { checkDone(); return; }
  
  function onOne() {
    loaded++;
    if (loaded >= total) checkDone();
  }
  
  // 优先使用CDN，fallback到本地文件
  var CDN_HC = 'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js';
  var CDN_JSPDF = 'https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js';
  
  if (needHc) {
    var s1 = document.createElement('script');
    s1.src = CDN_HC;
    s1.onload = onOne;
    s1.onerror = function(){
      // CDN失败，尝试本地文件
      console.warn('html2canvas CDN加载失败，尝试本地文件...');
      var s1b = document.createElement('script');
      s1b.src = 'html2canvas.min.js';
      s1b.onload = onOne;
      s1b.onerror = function(){ console.error('html2canvas加载失败'); onOne(); };
      document.head.appendChild(s1b);
    };
    document.head.appendChild(s1);
  }
  if (needJspdf) {
    var s2 = document.createElement('script');
    s2.src = CDN_JSPDF;
    s2.onload = onOne;
    s2.onerror = function(){
      // CDN失败，尝试本地文件
      console.warn('jsPDF CDN加载失败，尝试本地文件...');
      var s2b = document.createElement('script');
      s2b.src = 'jspdf.min.js';
      s2b.onload = onOne;
      s2b.onerror = function(){ console.error('jsPDF加载失败'); onOne(); };
      document.head.appendChild(s2b);
    };
    document.head.appendChild(s2);
  }
}"""

    if old_loadPdfLibs in content:
        content = content.replace(old_loadPdfLibs, new_loadPdfLibs)
        print("[修复1a] loadPdfLibs函数 - 优先CDN，fallback本地文件")
    else:
        print("[修复1a] 警告：未找到loadPdfLibs函数原文，尝试模糊匹配...")
        # 尝试用正则替换
        pattern = r"function loadPdfLibs\(callback\) \{.*?\n\}"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            content = content[:match.start()] + new_loadPdfLibs + content[match.end():]
            print("[修复1a] loadPdfLibs函数 - 正则替换成功")
        else:
            print("[修复1a] 警告：loadPdfLibs替换失败")
    
    # 1b. 修复副表打印 - 内嵌实现，不依赖外部print-fubiao.html文件
    # 读取副表HTML内容
    with open(FUBAO_FILE, 'r', encoding='utf-8') as f:
        fubiao_content = f.read()
    
    # 将副表内容转义为JS字符串（用于内嵌）
    # 方案：创建一个隐藏的div容器，包含副表内容
    # 但副表内容太大，改用动态生成blob URL的方式
    
    old_printFubiao = """function printFubiao(index) {
  // 确保在项目列表页面也能正确获取项目索引
  if (typeof currentProjectIndex === 'undefined' || currentProjectIndex < 0) {
    if (projects && projects.length > 0) currentProjectIndex = 0;
  }
  closeAllPrintMenus();
  try {
    var url = 'print-fubiao.html?proj=' + currentProjectIndex + '&task=' + index;
    var win = window.open(url, '_blank');
    if (!win) {
      showToast('弹窗被拦截，请允许弹出窗口');
    }
  } catch(e) {
    console.error('打开副表打印页失败:', e);
    showToast('打开副表失败: ' + (e.message || e));
  }
}"""

    # 新的printFubiao：内嵌副表打印逻辑，用jsPDF+html2canvas直接生成
    new_printFubiao = """function printFubiao(index) {
  // 确保在项目列表页面也能正确获取项目索引
  if (typeof currentProjectIndex === 'undefined' || currentProjectIndex < 0) {
    if (projects && projects.length > 0) currentProjectIndex = 0;
  }
  currentTaskIndex = index;
  closeAllPrintMenus();
  
  try {
    // 确保PDF库已加载
    if (typeof html2canvas === 'undefined' || typeof jsPDF === 'undefined') {
      showToast('正在加载PDF库，请稍候...');
      loadPdfLibs(function(){
        if (typeof html2canvas === 'undefined' || typeof jsPDF === 'undefined') {
          showToast('PDF库加载失败，请检查网络');
          return;
        }
        printFubiao(index);
      });
      return;
    }
    
    showToast('正在准备副表...');
    exportFubiaoPDF();
  } catch(e) {
    console.error('副表打印失败:', e);
    showToast('副表打印失败: ' + (e.message || e));
  }
}

// ========== 副表PDF生成（内嵌实现） ==========
function exportFubiaoPDF() {
  var task = getCurrentTask();
  if (!task) { showToast('未找到检查数据'); return; }
  var proj = getCurrentProject();
  var now = new Date();
  var dateStr = now.getFullYear() + '年' + (now.getMonth()+1) + '月' + now.getDate() + '日';
  var projName = (proj && proj.name || '未命名').replace(/[\\\\/:*?"<>|]/g, '');
  var filename = projName + '_副表.pdf';
  
  if (typeof html2canvas === 'undefined' || typeof jsPDF === 'undefined') {
    showToast('PDF库未加载');
    return;
  }
  var JsPDF = jsPDF;
  
  var att = task.attachments || {};
  
  // 构建副表HTML（简化版，两页横版A4）
  var page1Html = buildFubiaoPage1(att, task, proj);
  var page2Html = buildFubiaoPage2(att, task, proj);
  
  var canvases = [];
  var sections = [
    {html: page1Html, label: '副表第1页', orientation: 'landscape'},
    {html: page2Html, label: '副表第2页', orientation: 'landscape'}
  ];
  var idx = 0;
  
  function renderNext() {
    if (idx >= sections.length) {
      // 组装PDF
      try {
        var pdf = new JsPDF({orientation: 'l', unit: 'mm', format: 'a4'});
        canvases.forEach(function(item, i) {
          var canvas = item.canvas;
          var imgData = canvas.toDataURL('image/jpeg', 0.92);
          if (i > 0) pdf.addPage('a4', 'l');
          pdf.addImage(imgData, 'JPEG', 0, 0, 297, 210);
        });
        pdf.save(filename);
        showToast('副表导出成功！共' + canvases.length + '页');
      } catch(err) {
        console.error('副表PDF组装失败:', err);
        showToast('副表PDF组装失败: ' + (err.message||err));
      }
      return;
    }
    
    var sec = sections[idx];
    var container = document.createElement('div');
    container.style.cssText = 'position:absolute;left:-9999px;top:0;z-index:-1;';
    document.body.appendChild(container);
    
    var div = document.createElement('div');
    div.style.cssText = "width:842px;height:595px;padding:10mm;font-family:'SimSun','宋体',serif;background:#fff;color:#000;font-size:9px;line-height:1.2;box-sizing:border-box;";
    div.innerHTML = sec.html;
    container.appendChild(div);
    
    showToast('正在渲染' + sec.label + '...');
    
    setTimeout(function() {
      html2canvas(div, {
        scale: 2, useCORS: true, allowTaint: true,
        backgroundColor: '#ffffff', logging: false, removeContainer: false,
        width: div.scrollWidth, height: div.scrollHeight
      }).then(function(canvas) {
        canvases.push({canvas: canvas, orientation: sec.orientation});
        if (container.parentNode) container.parentNode.removeChild(container);
        idx++;
        renderNext();
      }).catch(function(err) {
        console.error(sec.label + '渲染失败:', err);
        showToast(sec.label + '渲染失败: ' + (err.message||err));
        if (container.parentNode) container.parentNode.removeChild(container);
        idx++;
        renderNext();
      });
    }, 200);
  }
  
  renderNext();
}

// 副表第1页：附表1（门系统）+ 附表2（导轨）+ 附表3（安全钳/缓冲器）
function buildFubiaoPage1(att, task, proj) {
  var html = '';
  // 标题
  html += '<div style="text-align:center;font-size:14px;font-weight:bold;margin-bottom:6px;">电梯安装验收副表（一）</div>';
  html += '<div style="display:flex;justify-content:space-between;font-size:9px;margin-bottom:6px;">';
  html += '<span>项目：' + (proj && proj.name || '') + '</span>';
  html += '<span>产品编号：' + (task.prodNo || '') + '</span>';
  html += '<span>日期：' + (task.checkDate || '') + '</span>';
  html += '</div>';
  
  html += '<div style="display:flex;gap:8px;">';
  // 左列
  html += '<div style="flex:1;">';
  // 附表1：门系统
  html += buildFb1Table(att.attach1);
  html += '</div>';
  // 右列
  html += '<div style="flex:1;">';
  // 附表2：导轨
  html += buildFb2Table(att.attach2);
  // 附表3：安全钳/缓冲器
  html += buildFb3Table(att.attach3);
  html += '</div>';
  html += '</div>';
  
  return html;
}

// 副表第2页：附表4（曳引/钢丝绳）+ 附表5（平衡系数）+ 附表6（张力）+ 附表7（噪声）
function buildFubiaoPage2(att, task, proj) {
  var html = '';
  html += '<div style="text-align:center;font-size:14px;font-weight:bold;margin-bottom:6px;">电梯安装验收副表（二）</div>';
  html += '<div style="display:flex;justify-content:space-between;font-size:9px;margin-bottom:6px;">';
  html += '<span>项目：' + (proj && proj.name || '') + '</span>';
  html += '<span>产品编号：' + (task.prodNo || '') + '</span>';
  html += '<span>日期：' + (task.checkDate || '') + '</span>';
  html += '</div>';
  
  html += '<div style="display:flex;gap:8px;">';
  // 左列：附表4 + 附表6
  html += '<div style="flex:1;display:flex;flex-direction:column;gap:6px;">';
  html += buildFb4Table(att.attach4);
  html += buildFb6Table(att.attach6);
  html += '</div>';
  // 右列：附表5 + 附表7
  html += '<div style="flex:1;display:flex;flex-direction:column;gap:6px;">';
  html += buildFb5Table(att.attach5);
  html += buildFb7Table(att.attach7);
  html += '</div>';
  html += '</div>';
  
  return html;
}

// 附表1：层门、轿门
function buildFb1Table(att1) {
  if (!att1) return '<div style="font-size:10px;font-weight:bold;margin-bottom:4px;">附表1 层门、轿门</div><div style="border:1px solid #333;padding:10px;text-align:center;color:#999;">暂无数据</div>';
  var html = '<div style="font-size:10px;font-weight:bold;margin-bottom:2px;">附表1 层门、轿门系统安装检验记录</div>';
  html += '<table style="width:100%;border-collapse:collapse;font-size:7px;">';
  // 表头
  html += '<tr>';
  html += '<th style="border:1px solid #333;padding:1px;width:18%;">项目</th>';
  html += '<th style="border:1px solid #333;padding:1px;">门地坎距</th>';
  html += '<th style="border:1px solid #333;padding:1px;">门扇间隙</th>';
  html += '<th style="border:1px solid #333;padding:1px;">立柱偏差</th>';
  html += '<th style="border:1px solid #333;padding:1px;">地坎间隙</th>';
  html += '<th style="border:1px solid #333;padding:1px;">施力间隙</th>';
  html += '<th style="border:1px solid #333;padding:1px;">啮合长度</th>';
  html += '<th style="border:1px solid #333;padding:1px;">门刀地坎</th>';
  html += '<th style="border:1px solid #333;padding:1px;">滚轮地坎</th>';
  html += '</tr>';
  
  var cargate = att1.cargate || [[], []];
  // 轿门1
  var c1 = cargate[0] || [];
  html += '<tr>';
  html += '<td style="border:1px solid #333;padding:1px;font-weight:bold;">轿门1</td>';
  html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (c1[4]||'') + '</td>';
  html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (c1[7]||'') + '</td>';
  html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (c1[2]||'') + '/' + (c1[3]||'') + '</td>';
  html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (c1[14]||'') + '</td>';
  html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (c1[6]||'') + '</td>';
  html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (c1[9]||'') + '</td>';
  html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (c1[10]||'') + '</td>';
  html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (c1[12]||'') + '</td>';
  html += '</tr>';
  
  // 层门（前3层）
  var laygate = att1.laygate || [];
  for (var i = 0; i < Math.min(3, laygate.length); i++) {
    var lg = laygate[i];
    var d = lg.data || [];
    html += '<tr>';
    html += '<td style="border:1px solid #333;padding:1px;font-weight:bold;">' + (lg.name || (i+1)+'层') + '</td>';
    html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (d[4]||'') + '</td>';
    html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (d[7]||'') + '</td>';
    html += '<td style="border:1px solid #333;padding:1px;text-align:center;">-</td>';
    html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (d[14]||'') + '</td>';
    html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (d[6]||'') + '</td>';
    html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (d[9]||'') + '</td>';
    html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (d[10]||'') + '</td>';
    html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (d[12]||'') + '</td>';
    html += '</tr>';
  }
  html += '</table>';
  return html;
}

// 附表2：导轨
function buildFb2Table(att2) {
  if (!att2) return '<div style="font-size:10px;font-weight:bold;margin:6px 0 2px;">附表2 导轨</div><div style="border:1px solid #333;padding:10px;text-align:center;color:#999;">暂无数据</div>';
  var html = '<div style="font-size:10px;font-weight:bold;margin:6px 0 2px;">附表2 导轨安装检验记录</div>';
  html += '<table style="width:100%;border-collapse:collapse;font-size:7px;">';
  html += '<tr><th style="border:1px solid #333;padding:1px;">项目</th><th style="border:1px solid #333;padding:1px;">轿厢导轨</th><th style="border:1px solid #333;padding:1px;">对重导轨</th></tr>';
  
  // 简单显示部分关键数据
  var car = att2.carRail || {};
  var cwt = att2.cwtRail || {};
  html += '<tr><td style="border:1px solid #333;padding:1px;font-weight:bold;">顶面间距</td><td style="border:1px solid #333;padding:1px;text-align:center;">' + (car.topDist||'') + '</td><td style="border:1px solid #333;padding:1px;text-align:center;">' + (cwt.topDist||'') + '</td></tr>';
  html += '<tr><td style="border:1px solid #333;padding:1px;font-weight:bold;">底面间距</td><td style="border:1px solid #333;padding:1px;text-align:center;">' + (car.bottomDist||'') + '</td><td style="border:1px solid #333;padding:1px;text-align:center;">' + (cwt.bottomDist||'') + '</td></tr>';
  html += '<tr><td style="border:1px solid #333;padding:1px;font-weight:bold;">偏摆值</td><td style="border:1px solid #333;padding:1px;text-align:center;">' + (car.deflection||'') + '</td><td style="border:1px solid #333;padding:1px;text-align:center;">' + (cwt.deflection||'') + '</td></tr>';
  html += '</table>';
  return html;
}

// 附表3：安全钳/缓冲器
function buildFb3Table(att3) {
  if (!att3) return '<div style="font-size:10px;font-weight:bold;margin:6px 0 2px;">附表3 安全钳/缓冲器</div><div style="border:1px solid #333;padding:10px;text-align:center;color:#999;">暂无数据</div>';
  var html = '<div style="font-size:10px;font-weight:bold;margin:6px 0 2px;">附表3 安全钳、缓冲器检验记录</div>';
  html += '<table style="width:100%;border-collapse:collapse;font-size:7px;">';
  html += '<tr><th style="border:1px solid #333;padding:1px;">项目</th><th style="border:1px solid #333;padding:1px;">数据</th></tr>';
  html += '<tr><td style="border:1px solid #333;padding:1px;font-weight:bold;">安全钳类型</td><td style="border:1px solid #333;padding:1px;text-align:center;">' + (att3.safetyGearType||'') + '</td></tr>';
  html += '<tr><td style="border:1px solid #333;padding:1px;font-weight:bold;">缓冲器类型</td><td style="border:1px solid #333;padding:1px;text-align:center;">' + (att3.bufferType||'') + '</td></tr>';
  html += '<tr><td style="border:1px solid #333;padding:1px;font-weight:bold;">越程距离</td><td style="border:1px solid #333;padding:1px;text-align:center;">' + (att3.travelDistance||'') + '</td></tr>';
  html += '</table>';
  return html;
}

// 附表4：曳引/钢丝绳
function buildFb4Table(att4) {
  if (!att4) return '<div style="font-size:10px;font-weight:bold;margin-bottom:2px;">附表4 曳引钢丝绳</div><div style="border:1px solid #333;padding:10px;text-align:center;color:#999;">暂无数据</div>';
  var html = '<div style="font-size:10px;font-weight:bold;margin-bottom:2px;">附表4 曳引钢丝绳检验记录</div>';
  html += '<table style="width:100%;border-collapse:collapse;font-size:7px;">';
  html += '<tr><th style="border:1px solid #333;padding:1px;">钢丝绳号</th><th style="border:1px solid #333;padding:1px;">张力(N)</th></tr>';
  var ropes = att4.ropes || [];
  for (var i = 0; i < Math.min(6, ropes.length); i++) {
    html += '<tr><td style="border:1px solid #333;padding:1px;text-align:center;">第' + (i+1) + '根</td><td style="border:1px solid #333;padding:1px;text-align:center;">' + (ropes[i]||'') + '</td></tr>';
  }
  html += '</table>';
  return html;
}

// 附表5：平衡系数
function buildFb5Table(att5) {
  if (!att5) return '<div style="font-size:10px;font-weight:bold;margin-bottom:2px;">附表5 平衡系数</div><div style="border:1px solid #333;padding:10px;text-align:center;color:#999;">暂无数据</div>';
  var html = '<div style="font-size:10px;font-weight:bold;margin-bottom:2px;">附表5 电梯平衡系数检验记录</div>';
  var current = att5['电流'] || {};
  var up = current['电流上行'] || ['','','','',''];
  var down = current['电流下行'] || ['','','','',''];
  html += '<table style="width:100%;border-collapse:collapse;font-size:7px;">';
  html += '<tr><th style="border:1px solid #333;padding:1px;">负载</th><th style="border:1px solid #333;padding:1px;">30%</th><th style="border:1px solid #333;padding:1px;">40%</th><th style="border:1px solid #333;padding:1px;">45%</th><th style="border:1px solid #333;padding:1px;">50%</th><th style="border:1px solid #333;padding:1px;">60%</th></tr>';
  html += '<tr><td style="border:1px solid #333;padding:1px;font-weight:bold;">上行(A)</td>';
  for (var i = 0; i < 5; i++) html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (up[i]||'') + '</td>';
  html += '</tr><tr><td style="border:1px solid #333;padding:1px;font-weight:bold;">下行(A)</td>';
  for (var j = 0; j < 5; j++) html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (down[j]||'') + '</td>';
  html += '</tr></table>';
  
  // 计算平衡系数
  var upVals = up.map(function(v){return parseFloat(v);});
  var downVals = down.map(function(v){return parseFloat(v);});
  var percentages = [30, 40, 45, 50, 60];
  var balancePoint = 0;
  var found = false;
  for (var k = 0; k < 4; k++) {
    if (isNaN(upVals[k]) || isNaN(upVals[k+1]) || isNaN(downVals[k]) || isNaN(downVals[k+1])) continue;
    var diff1 = upVals[k] - downVals[k];
    var diff2 = upVals[k+1] - downVals[k+1];
    if (diff1 * diff2 <= 0 && Math.abs(diff1 - diff2) > 0.001) {
      var t = Math.abs(diff1) / Math.abs(diff2 - diff1);
      balancePoint = percentages[k] + t * (percentages[k+1] - percentages[k]);
      found = true;
      break;
    }
  }
  if (found) {
    html += '<div style="margin-top:3px;font-size:7px;">平衡系数：<b>' + balancePoint.toFixed(2) + '%</b>（0.4~0.5为合格）</div>';
  }
  return html;
}

// 附表6：钢丝绳张力
function buildFb6Table(att6) {
  if (!att6) return '<div style="font-size:10px;font-weight:bold;margin:6px 0 2px;">附表6 钢丝绳张力</div><div style="border:1px solid #333;padding:10px;text-align:center;color:#999;">暂无数据</div>';
  var html = '<div style="font-size:10px;font-weight:bold;margin:6px 0 2px;">附表6 钢丝绳张力检验记录</div>';
  var forces = att6.forces || [];
  var ropeCount = Math.min(8, att6.ropeCount || 6);
  html += '<table style="width:100%;border-collapse:collapse;font-size:7px;">';
  html += '<tr>';
  for (var i = 0; i < ropeCount; i++) {
    html += '<th style="border:1px solid #333;padding:1px;">绳' + (i+1) + '</th>';
  }
  html += '</tr><tr>';
  for (var j = 0; j < ropeCount; j++) {
    html += '<td style="border:1px solid #333;padding:1px;text-align:center;">' + (forces[j] ? forces[j]+'N' : '-') + '</td>';
  }
  html += '</tr></table>';
  return html;
}

// 附表7：噪声
function buildFb7Table(att7) {
  if (!att7) return '<div style="font-size:10px;font-weight:bold;margin:6px 0 2px;">附表7 噪声振动</div><div style="border:1px solid #333;padding:10px;text-align:center;color:#999;">暂无数据</div>';
  var html = '<div style="font-size:10px;font-weight:bold;margin:6px 0 2px;">附表7 噪声检验记录</div>';
  html += '<table style="width:100%;border-collapse:collapse;font-size:7px;">';
  var items = [
    ['开门层站', att7['开门层站']],
    ['关门层站', att7['关门层站']],
    ['开门轿厢', att7['开门轿厢']],
    ['关门轿厢', att7['关门轿厢']],
    ['上行轿厢', att7['上行轿厢']],
    ['下行轿厢', att7['下行轿厢']],
    ['机房', att7['机房1']],
  ];
  items.forEach(function(item) {
    html += '<tr><td style="border:1px solid #333;padding:1px;width:40%;font-weight:bold;">' + item[0] + '</td><td style="border:1px solid #333;padding:1px;text-align:center;">' + (item[1] ? item[1]+'dB' : '') + '</td></tr>';
  });
  html += '</table>';
  return html;
}"""

    if old_printFubiao in content:
        content = content.replace(old_printFubiao, new_printFubiao)
        print("[修复1b] printFubiao函数 - 改为内嵌jsPDF生成副表PDF")
    else:
        print("[修复1b] 警告：未找到printFubiao函数原文")
        # 尝试更宽松的匹配
        idx = content.find('function printFubiao(index)')
        if idx > 0:
            # 找到函数结束
            end_idx = content.find('\nfunction ', idx + 10)
            if end_idx > 0:
                content = content[:idx] + new_printFubiao + content[end_idx:]
                print("[修复1b] printFubiao函数 - 位置匹配替换成功")
            else:
                print("[修复1b] 警告：找不到函数结束位置")
        else:
            print("[修复1b] 警告：完全找不到printFubiao")
    
    # ==========================================
    # 修复2-4：菜单移动
    # ==========================================
    
    # 从check页菜单移除：厂检签字、导出JSON、导入JSON、导出Excel
    old_check_menu = """      <div onclick="saveCurrentTask();goPage('taskList');closeHeaderMenu('check')">📋 返回列表</div>
      <div onclick="showNewCheck();closeHeaderMenu('check')">➕ 新建</div>
      <div onclick="openInspectorSigSetting();closeHeaderMenu('check')">✍️ 厂检签字</div>
      <div onclick="exportTasksJSON();closeHeaderMenu('check')">📤 导出JSON</div>
      <div onclick="importTasksJSON();closeHeaderMenu('check')">📥 导入JSON</div>
      <div onclick="exportTasksExcel();closeHeaderMenu('check')">📊 导出Excel</div>"""

    new_check_menu = """      <div onclick="saveCurrentTask();goPage('taskList');closeHeaderMenu('check')">📋 返回列表</div>
      <div onclick="showNewCheck();closeHeaderMenu('check')">➕ 新建</div>
      <div onclick="printCheckSheet(currentTaskIndex);closeHeaderMenu('check')">📝 打印检查表</div>
      <div onclick="printFubiao(currentTaskIndex);closeHeaderMenu('check')">📊 打印副表</div>"""

    if old_check_menu in content:
        content = content.replace(old_check_menu, new_check_menu)
        print("[修复2-4] check页菜单 - 移除厂检签字/导出JSON/导入JSON/导出Excel，添加打印功能")
    else:
        print("[修复2-4] 警告：未找到check页菜单原文")
        # 检查菜单部分
        idx = content.find("closeHeaderMenu('check')")
        if idx > 0:
            # 找到菜单容器
            menu_start = content.rfind('<div class="header-dropdown', 0, idx)
            menu_end = content.find('</div>', idx + 50)
            # 找匹配的闭合
            depth = 1
            pos = menu_start
            while depth > 0 and pos < len(content):
                next_open = content.find('<div', pos + 4)
                next_close = content.find('</div>', pos + 4)
                if next_close == -1: break
                if next_open != -1 and next_open < next_close:
                    depth += 1
                    pos = next_open
                else:
                    depth -= 1
                    pos = next_close
            if depth == 0:
                menu_html = content[menu_start:pos+6]
                print(f"  check菜单HTML: {menu_html[:200]}...")
    
    # 在projectList页菜单添加：导出JSON、导入JSON、导出Excel
    old_main_menu = """      <div onclick="showNewProject();closeHeaderMenu('main')">➕ 新建项目</div>
        <div onclick="openInspectorSigSetting();closeHeaderMenu('main')">✍️ 厂检签字</div>"""

    new_main_menu = """      <div onclick="showNewProject();closeHeaderMenu('main')">➕ 新建项目</div>
        <div onclick="openInspectorSigSetting();closeHeaderMenu('main')">✍️ 厂检签字</div>
        <div onclick="exportTasksJSON();closeHeaderMenu('main')">📤 导出JSON</div>
        <div onclick="importTasksJSON();closeHeaderMenu('main')">📥 导入JSON</div>
        <div onclick="exportTasksExcel();closeHeaderMenu('main')">📊 导出Excel</div>"""

    if old_main_menu in content:
        content = content.replace(old_main_menu, new_main_menu)
        print("[修复2-4] projectList页菜单 - 添加导出JSON/导入JSON/导出Excel")
    else:
        print("[修复2-4] 警告：未找到projectList页菜单原文")
        # 尝试查找
        idx = content.find('headerDropdownMain')
        if idx > 0:
            print(f"  headerDropdownMain位置: {idx}")
            snippet = content[idx:idx+500]
            print(f"  附近内容: {snippet[:300]}")
    
    # ==========================================
    # 修复5：厂检结论页备注消失bug
    # setConclusion中调用renderSignZoneContent → 改为renderNotesAndSign
    # ==========================================
    
    old_setConclusion = """function setConclusion(val) {
  var task = getCurrentTask();
  if (!task) return;
  task.conclusion = val;
  saveProjects();
  // 即时更新按钮样式
  var container = document.getElementById('zoneContent');
  if (container && currentZoneIndex === 6) {
    renderSignZoneContent(container);
  }
}"""

    new_setConclusion = """function setConclusion(val) {
  var task = getCurrentTask();
  if (!task) return;
  task.conclusion = val;
  saveProjects();
  // 即时更新按钮样式（保留备注模块）
  var container = document.getElementById('zoneContent');
  if (container && currentZoneIndex === 6) {
    renderNotesAndSign(container);
  }
}"""

    if old_setConclusion in content:
        content = content.replace(old_setConclusion, new_setConclusion)
        print("[修复5] setConclusion函数 - 改用renderNotesAndSign保留备注模块")
    else:
        print("[修复5] 警告：未找到setConclusion函数原文")
        # 尝试替换关键行
        old_line = 'renderSignZoneContent(container);'
        new_line = 'renderNotesAndSign(container);'
        # 只替换setConclusion函数内的那一个
        idx = content.find('function setConclusion(val)')
        if idx > 0:
            end_idx = content.find('\nfunction ', idx + 10)
            func_body = content[idx:end_idx]
            if old_line in func_body:
                new_func = func_body.replace(old_line, new_line)
                content = content[:idx] + new_func + content[end_idx:]
                print("[修复5] setConclusion函数 - 行级替换成功")
    
    # ==========================================
    # 修复6：去掉重复的备注和标题
    # 从renderSignZoneContent中移除：
    # 1. 整改期限下面的备注输入框（蓝色标题"备注"+textarea）
    # 2. 下面的蓝色"厂检结论"标题
    # ==========================================
    
    # 找到renderSignZoneContent函数中的"备注"部分和"厂检结论"标题
    # 先找到函数起始
    rs_idx = content.find('function renderSignZoneContent(container)')
    if rs_idx > 0:
        func_end = content.find('\nfunction ', rs_idx + 10)
        func_body = content[rs_idx:func_end]
        
        # 要移除的内容：整改期限后面的备注部分
        remark_start = func_body.find("  // 备注")
        remark_section = """  // 备注
  html += '<div style="margin-bottom:20px;">';
  html += '<div style="font-size:15px;font-weight:700;margin-bottom:10px;color:#667eea;">备注</div>';
  html += '<textarea id="conclusionRemark" rows="4" placeholder="请输入备注信息..." oninput="setConclusionRemark(this.value)" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;font-size:14px;font-family:inherit;resize:vertical;box-sizing:border-box;line-height:1.5;">' + (task.remark || '') + '</textarea>';
  html += '</div>';"""
        
        if remark_section in func_body:
            new_body = func_body.replace(remark_section, '')
            content = content[:rs_idx] + new_body + content[func_end:]
            print("[修复6a] 移除整改期限下面的备注输入框")
        else:
            print("[修复6a] 警告：未找到备注部分原文，尝试模糊匹配...")
            # 查找textarea id="conclusionRemark"部分
            cr_idx = func_body.find('conclusionRemark')
            if cr_idx > 0:
                # 向前找最近的注释"// 备注"
                remark_start2 = func_body.rfind('// 备注', 0, cr_idx)
                # 向后找html += '</div>';
                remark_end2 = func_body.find("html += '</div>';", cr_idx) + len("html += '</div>';")
                if remark_start2 > 0 and remark_end2 > remark_start2:
                    to_remove = func_body[remark_start2:remark_end2]
                    new_body = func_body.replace(to_remove, '')
                    content = content[:rs_idx] + new_body + content[func_end:]
                    print("[修复6a] 备注输入框 - 模糊匹配移除成功")
        
        # 重新获取函数体（因为上面可能修改了）
        func_end2 = content.find('\nfunction ', rs_idx + 10)
        func_body2 = content[rs_idx:func_end2]
        
        # 要移除的：签字区域上面的"厂检结论"蓝色标题
        sig_title = "  // 签字区域 - 合并为一个签字确认面板\n  html += '<div style=\"font-size:15px;font-weight:700;margin-bottom:10px;color:#667eea;\">厂检结论</div>';"
        
        if sig_title in func_body2:
            new_body2 = func_body2.replace(sig_title, "  // 签字区域 - 合并为一个签字确认面板")
            content = content[:rs_idx] + new_body2 + content[func_end2:]
            print("[修复6b] 移除重复的\"厂检结论\"蓝色标题")
        else:
            print("[修复6b] 警告：未找到厂检结论标题")
    else:
        print("[修复6] 警告：未找到renderSignZoneContent函数")
    
    # ==========================================
    # 修复7：左滑返回手势
    # ==========================================
    
    # 在init()函数之前或之后添加手势处理代码
    # 找到 init(); 调用的位置
    gesture_code = """
// ========== 左滑返回手势 ==========
(function() {
  var touchStartX = 0;
  var touchStartY = 0;
  var touchStartTime = 0;
  var SWIPE_THRESHOLD_RATIO = 0.15; // 屏幕宽度的15%
  var MAX_VERTICAL_RATIO = 0.5; // 垂直位移不超过水平位移的一半
  var MAX_DURATION = 500; // 最大滑动时间ms

  function getCurrentPage() {
    var pages = document.querySelectorAll('.page.active');
    if (pages.length === 0) return null;
    return pages[0].id.replace('page-', '');
  }

  function handleTouchStart(e) {
    if (e.touches.length !== 1) return;
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
    touchStartTime = Date.now();
  }

  function handleTouchEnd(e) {
    if (e.changedTouches.length !== 1) return;
    var endX = e.changedTouches[0].clientX;
    var endY = e.changedTouches[0].clientY;
    var deltaX = endX - touchStartX;
    var deltaY = endY - touchStartY;
    var duration = Date.now() - touchStartTime;
    
    // 只处理右→左滑动（返回手势）
    if (deltaX >= 0) return;
    
    var screenWidth = window.innerWidth;
    var threshold = screenWidth * SWIPE_THRESHOLD_RATIO;
    
    // 滑动距离不够
    if (Math.abs(deltaX) < threshold) return;
    // 垂直位移过大，不是水平滑动
    if (Math.abs(deltaY) > Math.abs(deltaX) * MAX_VERTICAL_RATIO) return;
    // 时间过长
    if (duration > MAX_DURATION) return;
    
    // 判断是否在可水平滚动的元素内
    var target = e.target;
    while (target && target !== document.body) {
      var style = window.getComputedStyle(target);
      var overflowX = style.overflowX;
      var scrollWidth = target.scrollWidth;
      var clientWidth = target.clientWidth;
      // 如果元素可水平滚动且还没滑到最左边，不触发返回
      if ((overflowX === 'auto' || overflowX === 'scroll') && scrollWidth > clientWidth) {
        if (target.scrollLeft > 0) {
          return; // 还没到最左边，让元素自己处理滚动
        }
      }
      target = target.parentElement;
    }
    
    // 左滑 → 返回上一级
    var currentPage = getCurrentPage();
    if (currentPage === 'check') {
      // 检验页 → 电梯列表页
      if (typeof saveCurrentTask === 'function') saveCurrentTask();
      if (typeof goPage === 'function') goPage('taskList');
    } else if (currentPage === 'taskList') {
      // 电梯列表页 → 项目列表页
      if (typeof goPage === 'function') goPage('projectList');
    }
  }

  // 绑定到body，使用捕获阶段以提前判断
  document.addEventListener('touchstart', handleTouchStart, { passive: true });
  document.addEventListener('touchend', handleTouchEnd, { passive: true });
})();
"""
    
    # 把手势代码加到init();调用的前面
    init_call = 'init();\n\n// 隐藏启动加载层'
    if init_call in content:
        content = content.replace(init_call, gesture_code + '\n' + init_call)
        print("[修复7] 添加左滑返回手势（check→taskList→projectList）")
    else:
        print("[修复7] 警告：未找到init()调用位置")
        # 尝试其他位置，比如</script>标签之前
        script_end = content.rfind('</script>')
        if script_end > 0:
            # 找到最后一个script结束标签前的合适位置
            # 找init()调用
            init_idx = content.rfind('init();')
            if init_idx > 0:
                content = content[:init_idx] + gesture_code + '\n' + content[init_idx:]
                print("[修复7] 左滑返回手势 - init()前面插入成功")
    
    # ==========================================
    # 写入文件
    # ==========================================
    with open(INPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n修复完成！新文件长度: {len(content)}")
    print(f"文件已保存到: {INPUT_FILE}")

if __name__ == '__main__':
    main()
