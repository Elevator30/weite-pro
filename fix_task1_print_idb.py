#!/usr/bin/env python3
"""
Task 1: Fix print-fubiao.html - add IndexedDB support
Replace localStorage reading with IndexedDB + localStorage fallback
"""
import re

FILE_PATH = "/app/data/所有对话/主对话/weite-pro-temp/print-fubiao.html"

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# ====== 1. Add IndexedDB wrapper right after <script> tag and before "数据读取" section ======
idb_wrapper = """// ===== IndexedDB 封装 (ES5兼容, callback风格, 带localStorage降级) =====
var _idb = null;
var _idbReady = false;
var _idbQueue = [];
function _idbInit(){
  if (typeof indexedDB === 'undefined') { _idbReady = 'fallback'; return; }
  var req = indexedDB.open('WeiteKV', 1);
  req.onupgradeneeded = function(e) {
    var db = e.target.result;
    if (!db.objectStoreNames.contains('kv')) db.createObjectStore('kv');
  };
  req.onsuccess = function(e) {
    _idb = e.target.result;
    _idbReady = true;
    while (_idbQueue.length > 0) {
      try { _idbQueue.shift()(); } catch (err) { console.error('IDB队列错误', err); }
    }
  };
  req.onerror = function() {
    console.warn('IndexedDB打开失败，降级使用localStorage');
    _idbReady = 'fallback';
  };
}
function _idbExec(fn) {
  if (_idbReady === true) { try { fn(); } catch (e) { console.error('IDB执行错误', e); } }
  else if (_idbReady === 'fallback') { try { fn(); } catch (e) {} }
  else { _idbQueue.push(fn); }
}
function dbGet(key, cb) {
  _idbExec(function() {
    if (_idbReady === 'fallback') {
      try { cb(localStorage.getItem(key), null); } catch (e) { cb(null, e); }
      return;
    }
    try {
      var tx = _idb.transaction('kv', 'readonly');
      var r = tx.objectStore('kv').get(key);
      r.onsuccess = function() { cb(r.result !== undefined ? r.result : null, null); };
      r.onerror = function() { cb(null, r.error); };
    } catch (e) { cb(null, e); }
  });
}
function dbSet(key, val, cb) {
  _idbExec(function() {
    if (_idbReady === 'fallback') {
      try { localStorage.setItem(key, val); cb && cb(null); } catch (e) { cb && cb(e); }
      return;
    }
    try {
      var tx = _idb.transaction('kv', 'readwrite');
      tx.objectStore('kv').put(val, key);
      tx.oncomplete = function() { cb && cb(null); };
      tx.onerror = function() { cb && cb(tx.error); };
    } catch (e) { cb && cb(e); }
  });
}
function dbRemove(key, cb) {
  _idbExec(function() {
    if (_idbReady === 'fallback') {
      try { localStorage.removeItem(key); cb && cb(null); } catch (e) { cb && cb(e); }
      return;
    }
    try {
      var tx = _idb.transaction('kv', 'readwrite');
      tx.objectStore('kv').delete(key);
      tx.oncomplete = function() { cb && cb(null); };
      tx.onerror = function() { cb && cb(tx.error); };
    } catch (e) { cb && cb(e); }
  });
}
function dbGetMulti(keys, cb) {
  var results = {};
  var remaining = keys.length;
  if (remaining === 0) { cb({}); return; }
  keys.forEach(function(k) {
    dbGet(k, function(v, err) {
      results[k] = v;
      remaining--;
      if (remaining <= 0) cb(results);
    });
  });
}
// 从localStorage迁移到IndexedDB
function migrateFromLS(keys, cb) {
  if (_idbReady === 'fallback') { cb && cb(0); return; }
  var migrated = 0;
  var remaining = keys.length;
  if (remaining === 0) { cb && cb(0); return; }
  function check() {
    remaining--;
    if (remaining <= 0) { cb && cb(migrated); }
  }
  keys.forEach(function(k) {
    try {
      var v = localStorage.getItem(k);
      if (v !== null) {
        dbSet(k, v, function(err) {
          if (!err) {
            try { localStorage.removeItem(k); } catch (e) {}
            migrated++;
          }
          check();
        });
      } else {
        check();
      }
    } catch (e) { check(); }
  });
}
_idbInit();
// ===== IndexedDB 封装结束 =====

"""

# Insert after the first <script> tag that's followed by "数据读取"
old_section_start = "<script>\n// ============ 数据读取 ============"
new_section_start = "<script>\n" + idb_wrapper + "// ============ 数据读取 ============"

content = content.replace(old_section_start, new_section_start, 1)

# ====== 2. Replace getProjects function with async version ======
old_get_projects = """function getProjects() {
  try {
    var stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return JSON.parse(stored);
  } catch(e) {}
  return [];
}"""

new_get_projects = """function getProjects(cb) {
  // 先从 IndexedDB 读取
  dbGet(STORAGE_KEY, function(stored, err) {
    if (stored) {
      try { cb(JSON.parse(stored)); return; } catch(e) {}
    }
    // IndexedDB 没有数据，尝试从 localStorage 读取（兼容旧数据）
    try {
      var lsData = localStorage.getItem(STORAGE_KEY);
      if (lsData) {
        var parsed = JSON.parse(lsData);
        // 自动迁移到 IndexedDB
        dbSet(STORAGE_KEY, lsData, function() {
          try { localStorage.removeItem(STORAGE_KEY); } catch(e) {}
        });
        cb(parsed);
        return;
      }
    } catch(e) {}
    cb([]);
  });
}"""

content = content.replace(old_get_projects, new_get_projects, 1)

# ====== 3. Replace getCurrentTask function with async version ======
old_get_current_task = """function getCurrentTask() {
  var projects = getProjects();
  if (projects.length === 0) return null;
  
  // 从URL参数获取索引
  var params = new URLSearchParams(window.location.search);
  var projIdx = parseInt(params.get('proj'));
  var taskIdx = parseInt(params.get('task'));
  
  if (isNaN(projIdx) || projIdx < 0 || projIdx >= projects.length) projIdx = 0;
  var proj = projects[projIdx];
  if (!proj || !proj.tasks || proj.tasks.length === 0) return null;
  
  if (isNaN(taskIdx) || taskIdx < 0 || taskIdx >= proj.tasks.length) taskIdx = proj.tasks.length - 1;
  
  return proj.tasks[taskIdx];
}"""

new_get_current_task = """function getCurrentTask(cb) {
  getProjects(function(projects) {
    if (projects.length === 0) { cb(null); return; }
    
    // 从URL参数获取索引
    var params = new URLSearchParams(window.location.search);
    var projIdx = parseInt(params.get('proj'));
    var taskIdx = parseInt(params.get('task'));
    
    if (isNaN(projIdx) || projIdx < 0 || projIdx >= projects.length) projIdx = 0;
    var proj = projects[projIdx];
    if (!proj || !proj.tasks || proj.tasks.length === 0) { cb(null); return; }
    
    if (isNaN(taskIdx) || taskIdx < 0 || taskIdx >= proj.tasks.length) taskIdx = proj.tasks.length - 1;
    
    cb(proj.tasks[taskIdx]);
  });
}"""

content = content.replace(old_get_current_task, new_get_current_task, 1)

# ====== 4. Replace fillData function with async version ======
old_fill_data = """function fillData() {
  var task = getCurrentTask();
  if (!task) {
    document.getElementById('content').innerHTML = '<div style="text-align:center;padding:80px 20px;color:#999;font-size:14px;"><div style="font-size:48px;margin-bottom:16px;">📋</div>暂无数据<br><span style="font-size:12px;">请先在主页面录入检查数据后再打印副表</span></div>';
    return;
  }
  
  var att = task.attachments || {};
  
  fillFb1(att.attach1);
  fillFb2(att.attach2);
  fillFb3(att.attach3);
  fillFb4(att.attach4);
  fillFb5(att.attach5);
  fillFb6(att.attach6);
  fillFb7(att.attach7);
  
  // 绘制平衡系数曲线
  drawBalanceChartSVG(att.attach5);
}"""

new_fill_data = """function fillData() {
  getCurrentTask(function(task) {
    if (!task) {
      document.getElementById('content').innerHTML = '<div style="text-align:center;padding:80px 20px;color:#999;font-size:14px;"><div style="font-size:48px;margin-bottom:16px;">📋</div>暂无数据<br><span style="font-size:12px;">请先在主页面录入检查数据后再打印副表</span></div>';
      return;
    }
    
    var att = task.attachments || {};
    
    fillFb1(att.attach1);
    fillFb2(att.attach2);
    fillFb3(att.attach3);
    fillFb4(att.attach4);
    fillFb5(att.attach5);
    fillFb6(att.attach6);
    fillFb7(att.attach7);
    
    // 绘制平衡系数曲线
    drawBalanceChartSVG(att.attach5);
    
    // 数据加载完成后触发自动打印
    var params = new URLSearchParams(window.location.search);
    var autoPrint = params.get('autoPrint');
    if (autoPrint !== '0') {
      setTimeout(function() { window.print(); }, 300);
    }
  });
}"""

content = content.replace(old_fill_data, new_fill_data, 1)

# ====== 5. Fix the exportFubiaoPDF getCurrentTask call (in PDF save filename) ======
# This one is in the PDF export function - it calls getCurrentTask() synchronously
# Need to make it async too
old_pdf_save = """    if (currentPage >= totalPages) {
      var t = getCurrentTask(); var equipNo = (t && t.prodNo || '未编号').replace(/[\\/:*?"<>|]/g, ''); pdf.save(equipNo + '_副表.pdf');"""

new_pdf_save = """    if (currentPage >= totalPages) {
      getCurrentTask(function(t) { var equipNo = (t && t.prodNo || '未编号').replace(/[\\/:*?"<>|]/g, ''); pdf.save(equipNo + '_副表.pdf'); });"""

content = content.replace(old_pdf_save, new_pdf_save, 1)

# ====== 6. Fix the initialization at the bottom ======
old_init = """document.addEventListener('DOMContentLoaded', function() {
  fillData();
  var params = new URLSearchParams(window.location.search);
  var autoPrint = params.get('autoPrint');
  if (autoPrint !== '0') {
    setTimeout(function() { window.print(); }, 300);
  }
});"""

new_init = """document.addEventListener('DOMContentLoaded', function() {
  fillData();
  // 自动打印已移到 fillData 的回调中（数据加载完成后再打印）
});"""

content = content.replace(old_init, new_init, 1)

# Write back
with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Task 1 done: print-fubiao.html updated with IndexedDB support")
print(f"File size: {len(content)} bytes")
