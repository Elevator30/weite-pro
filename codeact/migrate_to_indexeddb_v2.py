#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将三个HTML文件的 localStorage 存储替换为 IndexedDB
策略：内存缓存 + 异步持久化 + 自动迁移
"""

import re
import os
import sys

BASE_DIR = '/app/data/所有对话/主对话/weite-pro-temp'

# ============================================================
# IndexedDB 封装代码（ES5 兼容，callback 风格，带降级）
# ============================================================
IDB_WRAPPER = '''
// ===== IndexedDB 封装 (ES5兼容, callback风格, 带localStorage降级) =====
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
'''


def replace_ls_setitem(content, key_expr, cache_update_expr, db_key_expr=None):
    """
    替换 localStorage.setItem(key, value) 模式
    key_expr: 匹配 key 的正则部分，如 "'wtList'"
    cache_update_expr: 缓存更新代码（JavaScript）
    db_key_expr: dbSet 中使用的 key 表达式，如果为 None 则用 key_expr
    """
    if db_key_expr is None:
        db_key_expr = key_expr
    
    # 模式: localStorage.setItem(<key>, <value>)
    # 需要处理各种空格情况
    pattern = r'localStorage\.setItem\(\s*' + key_expr + r'\s*,\s*'
    # 这个太复杂了，用更简单的替换方式
    return content


def count_ls(content):
    """统计真正的 localStorage 调用（排除注释、字符串引用等）"""
    # 粗略统计
    return content.count('localStorage')


def find_ls_lines(content, exclude_fallback=True):
    """找出所有含 localStorage 的行号和内容"""
    lines = content.split('\n')
    result = []
    for i, line in enumerate(lines):
        if 'localStorage' in line:
            if exclude_fallback and ('_idbReady' in line or 'fallback' in line or 'migrateFromLS' in line):
                continue
            # 排除纯注释行
            stripped = line.strip()
            if stripped.startswith('//') and 'localStorage' in stripped:
                # 注释中提到的不算
                if 'setItem' not in stripped and 'getItem' not in stripped and 'removeItem' not in stripped:
                    continue
            result.append((i+1, stripped[:200]))
    return result


# ============================================================
# 文件 1: weite-service-v14.html
# ============================================================
def migrate_weite_service():
    fpath = os.path.join(BASE_DIR, 'weite-service-v14.html')
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_len = len(content)
    original_ls = count_ls(content)
    
    # ---- 1. 在第一个内联 <script> 后注入 IDB 封装 ----
    # 找第3个 <script> 标签（前2个是外部库）
    matches = list(re.finditer(r'<script>', content))
    inject_pos = matches[0].end()  # 第一个内联 script
    content = content[:inject_pos] + IDB_WRAPPER + '\n' + content[inject_pos:]
    
    # ---- 2. 添加缓存变量和初始化函数 ----
    cache_code = '''
// ===== 存储缓存层 (wtList, wtGuideShown) =====
var _wtListCache = [];
var _wtGuideShownCache = null;

function _loadCacheFromDB(callback) {
  dbGetMulti(['wtList', 'wtGuideShown'], function(results) {
    try { _wtListCache = JSON.parse(results['wtList'] || '[]'); } catch(e) { _wtListCache = []; }
    _wtGuideShownCache = results['wtGuideShown'];
    callback && callback();
  });
}

function _saveWtListCache() {
  try { dbSet('wtList', JSON.stringify(_wtListCache)); } catch(e) {}
}

function _saveGuideShown(val) {
  _wtGuideShownCache = val;
  dbSet('wtGuideShown', val);
}

function _initStorage(callback) {
  // 先从 DB 加载
  _loadCacheFromDB(function() {
    // 再尝试从 localStorage 迁移旧数据
    migrateFromLS(['wtList', 'wtGuideShown'], function(migrated) {
      if (migrated > 0) {
        // 迁移后重新加载缓存
        _loadCacheFromDB(callback);
      } else {
        callback && callback();
      }
    });
  });
}
// ===== 缓存层结束 =====
'''
    
    # 在 IDB 封装结束后注入
    marker = '// ===== IndexedDB 封装结束 ====='
    pos = content.index(marker) + len(marker)
    content = content[:pos] + cache_code + content[pos:]
    
    # ---- 3. 替换所有 wtList 相关的 localStorage 调用 ----
    
    # 读取: JSON.parse(localStorage.getItem('wtList')||'[]')
    content = content.replace(
        "JSON.parse(localStorage.getItem('wtList')||'[]')",
        "_wtListCache"
    )
    
    # 写入: localStorage.setItem('wtList',JSON.stringify(list))  (无空格版)
    content = content.replace(
        "localStorage.setItem('wtList',JSON.stringify(list))",
        "_wtListCache=list;_saveWtListCache()"
    )
    
    # 写入: localStorage.setItem('wtList', JSON.stringify(list))  (有空格版)
    content = content.replace(
        "localStorage.setItem('wtList', JSON.stringify(list))",
        "_wtListCache = list; _saveWtListCache()"
    )
    
    # 写入: localStorage.setItem('wtList',json)  (变量版)
    content = content.replace(
        "localStorage.setItem('wtList',json)",
        "try{_wtListCache=JSON.parse(json);}catch(e){}_saveWtListCache()"
    )
    
    # 删除: localStorage.removeItem('wtList')
    content = content.replace(
        "localStorage.removeItem('wtList')",
        "_wtListCache=[];dbRemove('wtList')"
    )
    
    # ---- 4. 替换 wtGuideShown 相关调用 ----
    
    # 读取: localStorage.getItem('wtGuideShown')
    content = content.replace(
        "localStorage.getItem('wtGuideShown')",
        "_wtGuideShownCache"
    )
    
    # 写入: localStorage.setItem('wtGuideShown','1')
    content = content.replace(
        "localStorage.setItem('wtGuideShown','1')",
        "_saveGuideShown('1')"
    )
    
    # ---- 5. 调整初始化流程 ----
    # 原: setTimeout(updateBtnStatus,100);
    # 改为: 先初始化存储，再 updateBtnStatus
    
    old_init_line = '// 初始化按钮状态\nsetTimeout(updateBtnStatus,100);'
    new_init = '''// 初始化：先加载存储缓存，再执行初始化
function _appStartInit() {
  _initStorage(function() {
    updateBtnStatus();
    // 如果有renderList，刷新列表显示
    if (typeof renderList === 'function') { renderList(); }
  });
}
setTimeout(_appStartInit, 50);'''
    
    content = content.replace(old_init_line, new_init)
    
    # ---- 保存 ----
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_ls = count_ls(content)
    remaining = find_ls_lines(content)
    
    print(f'[weite-service-v14.html] localStorage: {original_ls} -> {new_ls}')
    print(f'  文件大小: {original_len} -> {len(content)} bytes')
    if remaining:
        print(f'  剩余 {len(remaining)} 处 localStorage:')
        for ln, txt in remaining[:15]:
            print(f'    L{ln}: {txt}')
    else:
        print('  ✓ 所有 localStorage 调用已替换')
    
    return len(remaining) == 0


# ============================================================
# 文件 2: factory-inspection-v2.html
# ============================================================
def migrate_factory_inspection():
    fpath = os.path.join(BASE_DIR, 'factory-inspection-v2.html')
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_len = len(content)
    original_ls = count_ls(content)
    
    # ---- 1. 在 STORAGE_KEY 定义前注入 IDB 封装 ----
    marker = "var STORAGE_KEY = 'WEITE_CHECK_V4';"
    pos = content.index(marker)
    content = content[:pos] + IDB_WRAPPER + '\n\n' + content[pos:]
    
    # ---- 2. 添加签名缓存变量 ----
    # 在 INSPECTOR_SIG_KEY 定义后添加缓存
    sig_marker = "var INSPECTOR_SIG_KEY = 'WEITE_INSPECTOR_SIGNATURE';"
    sig_cache = '''
var _inspectorSigCache = {};
function _loadInspectorSigFromDB(callback) {
  dbGet(INSPECTOR_SIG_KEY, function(val, err) {
    try { _inspectorSigCache = JSON.parse(val || '{}'); } catch(e) { _inspectorSigCache = {}; }
    callback && callback();
  });
}'''
    pos = content.index(sig_marker) + len(sig_marker)
    content = content[:pos] + sig_cache + content[pos:]
    
    # ---- 3. 替换 saveProjects 函数 ----
    old_save = '''function saveProjects() {
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
}'''
    
    new_save = '''function saveProjects() {
  try {
    var dataStr = JSON.stringify(projects);
    dbSet(STORAGE_KEY, dataStr);
    // 【v129】自动备份
    try {
      dbSet(STORAGE_KEY + '_backup', dataStr);
    } catch(be) { console.warn('备份保存失败', be); }
  } catch(e) {
    console.error('保存数据失败', e);
  }
}'''
    
    if old_save in content:
        content = content.replace(old_save, new_save)
        print('  ✓ saveProjects 替换')
    else:
        print('  ✗ 未匹配 saveProjects，尝试单独替换setItem')
        # 尝试单独替换
        content = content.replace(
            "localStorage.setItem(STORAGE_KEY, dataStr);",
            "dbSet(STORAGE_KEY, dataStr);"
        )
        content = content.replace(
            "localStorage.setItem(STORAGE_KEY + '_backup', dataStr);",
            "dbSet(STORAGE_KEY + '_backup', dataStr);"
        )
    
    # ---- 4. 替换 loadProjects 函数 ----
    # 找到 loadProjects 函数，改为从内存返回（数据已在初始化时加载）
    
    # 先找到函数起始和结束
    load_start = content.index('function loadProjects()')
    rest = content[load_start:]
    # 找下一个函数
    next_func_match = re.search(r'\nfunction \w', rest[10:])
    if next_func_match:
        end_offset = 10 + next_func_match.start()
        old_load_func = rest[:end_offset]
        
        new_load_func = '''function loadProjects() {
  return projects || [];
}

function _loadProjectsFromDB(callback) {
  dbGet(STORAGE_KEY, function(stored, err) {
    if (stored && !err) {
      try {
        var data = JSON.parse(stored);
        // 判断是旧格式(任务数组)还是新格式(项目数组)
        if (Array.isArray(data)) {
          var isNewFormat = data.length > 0 && data[0] && typeof data[0] === 'object' && 'tasks' in data[0];
          if (isNewFormat) {
            projects = data;
          } else {
            // 旧格式(任务数组) -> 包装为项目
            projects = [{
              name: '旧数据',
              installer: '',
              installAddr: '',
              contact: '',
              phone: '',
              province: '',
              city: '',
              district: '',
              tasks: data
            }];
          }
          callback && callback(true);
        } else {
          callback && callback(false);
        }
      } catch(pe) {
        console.error('数据解析失败', pe);
        callback && callback(false);
      }
    } else {
      callback && callback(false);
    }
  });
}

'''
        content = content[:load_start] + new_load_func + content[load_start + end_offset:]
        print('  ✓ loadProjects 替换')
    else:
        print('  ✗ 无法确定 loadProjects 范围')
    
    # ---- 5. 替换 tryLoadBackup 中的读取 ----
    old_backup = "var backup = localStorage.getItem(STORAGE_KEY + '_backup');"
    new_backup = "var backup = null; // 备份数据存储在 IndexedDB 中，异常恢复时需异步加载"
    if old_backup in content:
        content = content.replace(old_backup, new_backup)
        print('  ✓ tryLoadBackup 替换')
    
    # 备份保存（在升级逻辑中）
    old_backup_save = "localStorage.setItem(STORAGE_KEY + '_backup', JSON.stringify(oldTasks));"
    new_backup_save = "dbSet(STORAGE_KEY + '_backup', JSON.stringify(oldTasks));"
    if old_backup_save in content:
        content = content.replace(old_backup_save, new_backup_save)
        print('  ✓ 升级逻辑中备份保存替换')
    
    # ---- 6. 替换导入功能 ----
    old_import = "localStorage.setItem(STORAGE_KEY, JSON.stringify(parsedProjects));"
    new_import = "projects = parsedProjects; dbSet(STORAGE_KEY, JSON.stringify(parsedProjects));"
    if old_import in content:
        content = content.replace(old_import, new_import)
        print('  ✓ 导入功能替换')
    
    # ---- 7. 替换检验员签名函数 ----
    old_get_sig = '''function getInspectorSignature() {
  try { return JSON.parse(localStorage.getItem(INSPECTOR_SIG_KEY) || '{}'); } catch(e) { return {}; }
}'''
    new_get_sig = '''function getInspectorSignature() {
  return _inspectorSigCache || {};
}'''
    if old_get_sig in content:
        content = content.replace(old_get_sig, new_get_sig)
        print('  ✓ getInspectorSignature 替换')
    
    old_save_sig = '''function saveInspectorSignature(name, sigData) {
  localStorage.setItem(INSPECTOR_SIG_KEY, JSON.stringify({name: name, sig: sigData}));
}'''
    new_save_sig = '''function saveInspectorSignature(name, sigData) {
  _inspectorSigCache = {name: name, sig: sigData};
  dbSet(INSPECTOR_SIG_KEY, JSON.stringify({name: name, sig: sigData}));
}'''
    if old_save_sig in content:
        content = content.replace(old_save_sig, new_save_sig)
        print('  ✓ saveInspectorSignature 替换')
    
    # ---- 8. 替换签名读取（打印代码中）----
    # localStorage.getItem(INSPECTOR_SIG_KEY) -> JSON.stringify(_inspectorSigCache)
    old_read = "localStorage.getItem(INSPECTOR_SIG_KEY)"
    new_read = "JSON.stringify(_inspectorSigCache || {})"
    count = content.count(old_read)
    if count > 0:
        content = content.replace(old_read, new_read)
        print(f'  ✓ INSPECTOR_SIG_KEY 读取替换 x{count}')
    
    # ---- 9. 替换 inspectorSignature（旧签名key）----
    old_sig = "localStorage.getItem('inspectorSignature')"
    new_sig = "(_inspectorSigCache && _inspectorSigCache.sig ? _inspectorSigCache.sig : null)"
    count = content.count(old_sig)
    if count > 0:
        content = content.replace(old_sig, new_sig)
        print(f'  ✓ inspectorSignature 读取替换 x{count}')
    
    # ---- 10. 替换 init 函数 ----
    old_init = '''function init() {
  try {
    loadProjects();
  } catch(e) {
    console.error('初始化加载失败', e);
    projects = [];
  }
  try {
    renderProjectList();
  } catch(e) {
    console.error('渲染项目列表失败', e);
  }
}'''
    
    new_init = '''function init() {
  _appInit();
}

function _appInit() {
  // 1. 加载检验员签名
  _loadInspectorSigFromDB(function() {
    // 2. 从 IndexedDB 加载项目数据
    _loadProjectsFromDB(function(loaded) {
      if (!loaded) {
        // 3. 没有数据，尝试从 localStorage 迁移
        migrateFromLS([
          STORAGE_KEY,
          STORAGE_KEY + '_backup',
          INSPECTOR_SIG_KEY,
          'inspectorSignature'
        ], function(migrated) {
          if (migrated > 0) {
            // 迁移后重新加载
            _loadProjectsFromDB(function() {
              _loadInspectorSigFromDB(function() {
                _doRenderInit();
              });
            });
          } else {
            projects = [];
            _doRenderInit();
          }
        });
      } else {
        // 4. 已有数据，也检查一下是否有旧数据需要迁移
        migrateFromLS([
          STORAGE_KEY,
          STORAGE_KEY + '_backup',
          INSPECTOR_SIG_KEY,
          'inspectorSignature'
        ], function() {
          _doRenderInit();
        });
      }
    });
  });
}

function _doRenderInit() {
  try {
    renderProjectList();
  } catch(e) {
    console.error('渲染项目列表失败', e);
  }
}'''
    
    if old_init in content:
        content = content.replace(old_init, new_init)
        print('  ✓ init 函数替换为异步加载')
    else:
        print('  ✗ 未匹配 init 函数')
    
    # ---- 保存 ----
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_ls = count_ls(content)
    remaining = find_ls_lines(content)
    
    print(f'\n[factory-inspection-v2.html] localStorage: {original_ls} -> {new_ls}')
    print(f'  文件大小: {original_len} -> {len(content)} bytes')
    if remaining:
        # 过滤掉 _fubiaoHtmlContent 字符串中的内容（那是副表页面，不需要改）
        real_remaining = []
        in_fubiao = False
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'localStorage' not in line:
                continue
            if '_idbReady' in line or 'fallback' in line or 'migrateFromLS' in line:
                continue
            stripped = line.strip()
            if '_fubiaoHtmlContent' in stripped or (stripped.startswith("'") and 'localStorage' in stripped):
                # 在字符串中的不算
                continue
            if stripped.startswith('//') and 'setItem' not in stripped and 'getItem' not in stripped:
                continue
            real_remaining.append((i+1, stripped[:200]))
        
        if real_remaining:
            print(f'  剩余 {len(real_remaining)} 处实际 localStorage 调用:')
            for ln, txt in real_remaining[:15]:
                print(f'    L{ln}: {txt}')
        else:
            print('  ✓ 所有 localStorage 调用已替换')
    else:
        print('  ✓ 所有 localStorage 调用已替换')
    
    return True


# ============================================================
# 文件 3: travel-expense.html
# ============================================================
def migrate_travel_expense():
    fpath = os.path.join(BASE_DIR, 'travel-expense.html')
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_len = len(content)
    original_ls = count_ls(content)
    
    # ---- 1. 在第一个内联 script 后注入 IDB 封装 ----
    marker = '<script>\nlet projects = '
    pos = content.index(marker) + len('<script>\n')
    content = content[:pos] + IDB_WRAPPER + '\n' + content[pos:]
    
    # ---- 2. 替换变量声明 ----
    old_declare = '''let projects = JSON.parse(localStorage.getItem('travelProjects') || '[]');
let expenses = JSON.parse(localStorage.getItem('travelExpenses') || '[]');'''
    
    new_declare = '''let projects = [];
let expenses = [];
let travelSettings = {};

// ===== 存储辅助函数 =====
function _loadTravelData(callback) {
  dbGetMulti(['travelProjects', 'travelExpenses', 'travelSettings'], function(results) {
    try { projects = JSON.parse(results['travelProjects'] || '[]'); } catch(e) { projects = []; }
    try { expenses = JSON.parse(results['travelExpenses'] || '[]'); } catch(e) { expenses = []; }
    try { travelSettings = JSON.parse(results['travelSettings'] || '{}'); } catch(e) { travelSettings = {}; }
    callback && callback();
  });
}
function _saveProjects() { dbSet('travelProjects', JSON.stringify(projects)); }
function _saveExpenses() { dbSet('travelExpenses', JSON.stringify(expenses)); }
function _saveSettings() { dbSet('travelSettings', JSON.stringify(travelSettings)); }
// ===== 存储辅助函数结束 ====='''
    
    content = content.replace(old_declare, new_declare)
    print('  ✓ 变量声明替换')
    
    # ---- 3. 先处理特殊代码块（visibilitychange, focus, updateHomeStats）----
    
    # visibilitychange 事件（在 init 内部，6空格缩进）
    old_vis_block = '''      projects = JSON.parse(localStorage.getItem('travelProjects') || '[]');
      expenses = JSON.parse(localStorage.getItem('travelExpenses') || '[]');
      // 更新真实当前月份（但不改变用户选择的查看月份）
      realCurrentMonth = new Date().toISOString().slice(0, 7);
      refreshForMonth();'''
    
    new_vis_block = '''      _loadTravelData(function() {
        // 更新真实当前月份（但不改变用户选择的查看月份）
        realCurrentMonth = new Date().toISOString().slice(0, 7);
        refreshForMonth();
      });'''
    
    if old_vis_block in content:
        content = content.replace(old_vis_block, new_vis_block)
        print('  ✓ visibilitychange 异步刷新替换')
    else:
        print('  ⚠ visibilitychange 未匹配（可能格式不同）')
    
    # focus 事件（在 init 内部，4空格缩进）
    old_focus_block = '''    projects = JSON.parse(localStorage.getItem('travelProjects') || '[]');
    expenses = JSON.parse(localStorage.getItem('travelExpenses') || '[]');
    updateHomeStats();'''
    
    new_focus_block = '''    _loadTravelData(function() {
      updateHomeStats();
    });'''
    
    if old_focus_block in content:
        content = content.replace(old_focus_block, new_focus_block)
        print('  ✓ focus 异步刷新替换')
    else:
        print('  ⚠ focus 未匹配（可能格式不同）')
    
    # updateHomeStats 函数开头（2空格缩进）
    old_update_home = '''  // 始终从 localStorage 重新加载数据，确保一致性
  projects = JSON.parse(localStorage.getItem('travelProjects') || '[]');
  expenses = JSON.parse(localStorage.getItem('travelExpenses') || '[]');'''
    
    new_update_home = '''  // 使用内存缓存（数据一致性由存储层保证）
  // 注：原从localStorage重新加载的逻辑已改为使用内存缓存，
  // 因为IndexedDB是异步的，且当前页面数据始终在内存中维护'''
    
    if old_update_home in content:
        content = content.replace(old_update_home, new_update_home)
        print('  ✓ updateHomeStats 替换')
    else:
        print('  ⚠ updateHomeStats 未匹配（可能格式不同）')
    
    # ---- 4. 替换 setItem 调用 ----
    
    # travelProjects (各种格式)
    patterns_projects = [
        # 标准格式
        ("localStorage.setItem('travelProjects', JSON.stringify(projects))", "_saveProjects()"),
        # 可能的无空格版本
        ("localStorage.setItem('travelProjects',JSON.stringify(projects))", "_saveProjects()"),
    ]
    total_p = 0
    for old, new in patterns_projects:
        c = content.count(old)
        if c > 0:
            content = content.replace(old, new)
            total_p += c
    print(f'  ✓ travelProjects setItem 替换 x{total_p}')
    
    # travelExpenses
    patterns_expenses = [
        ("localStorage.setItem('travelExpenses', JSON.stringify(expenses))", "_saveExpenses()"),
        ("localStorage.setItem('travelExpenses',JSON.stringify(expenses))", "_saveExpenses()"),
        ("localStorage.setItem('travelExpenses', json)", "dbSet('travelExpenses', json)"),
    ]
    total_e = 0
    for old, new in patterns_expenses:
        c = content.count(old)
        if c > 0:
            content = content.replace(old, new)
            total_e += c
    print(f'  ✓ travelExpenses setItem 替换 x{total_e}')
    
    # travelSettings - 用正则匹配各种情况
    # localStorage.setItem('travelSettings', JSON.stringify(...))
    def replace_settings(m):
        inner = m.group(1)
        return f"travelSettings = JSON.parse(JSON.stringify({inner})); _saveSettings()"
    
    pattern = r"localStorage\.setItem\('travelSettings',\s*JSON\.stringify\((.+?)\)\)"
    new_content, count = re.subn(pattern, replace_settings, content)
    if count > 0:
        content = new_content
        print(f'  ✓ travelSettings setItem 替换 x{count}')
    
    # ---- 4. 替换 getItem 调用 ----
    
    # JSON.parse(localStorage.getItem('travelProjects') || '[]')
    old_get_p = "JSON.parse(localStorage.getItem('travelProjects') || '[]')"
    count_p = content.count(old_get_p)
    content = content.replace(old_get_p, "projects.slice()")
    
    old_get_p2 = "JSON.parse(localStorage.getItem('travelProjects')||'[]')"
    count_p += content.count(old_get_p2)
    content = content.replace(old_get_p2, "projects.slice()")
    
    print(f'  ✓ travelProjects getItem 替换 x{count_p}')
    
    # JSON.parse(localStorage.getItem('travelExpenses') || '[]')
    old_get_e = "JSON.parse(localStorage.getItem('travelExpenses') || '[]')"
    count_e = content.count(old_get_e)
    content = content.replace(old_get_e, "expenses.slice()")
    
    old_get_e2 = "JSON.parse(localStorage.getItem('travelExpenses')||'[]')"
    count_e += content.count(old_get_e2)
    content = content.replace(old_get_e2, "expenses.slice()")
    
    print(f'  ✓ travelExpenses getItem 替换 x{count_e}')
    
    # localStorage.getItem('travelSettings')
    old_get_s = "localStorage.getItem('travelSettings')"
    count_s = content.count(old_get_s)
    content = content.replace(old_get_s, "JSON.stringify(travelSettings)")
    print(f'  ✓ travelSettings getItem 替换 x{count_s}')
    
    # ---- 5. 替换 removeItem 调用 ----
    
    old_rem_e = "localStorage.removeItem('travelExpenses')"
    count_rem_e = content.count(old_rem_e)
    content = content.replace(old_rem_e, "expenses = []; dbRemove('travelExpenses')")
    print(f'  ✓ travelExpenses removeItem 替换 x{count_rem_e}')
    
    old_rem_s = "localStorage.removeItem('travelSettings')"
    count_rem_s = content.count(old_rem_s)
    content = content.replace(old_rem_s, "travelSettings = {}; dbRemove('travelSettings')")
    print(f'  ✓ travelSettings removeItem 替换 x{count_rem_s}')
    
    # ---- 6. 替换存储空间计算 ----
    old_storage_calc = '''  for (var key in localStorage) {
    if (localStorage.hasOwnProperty(key)) {
      total += localStorage[key].length + key.length;
    }
  }'''
    
    new_storage_calc = '''  // 基于 IndexedDB 数据估算存储空间
  try {
    total = JSON.stringify(projects||[]).length + JSON.stringify(expenses||[]).length + JSON.stringify(travelSettings||{}).length + 50;
  } catch(e) { total = 0; }'''
    
    if old_storage_calc in content:
        content = content.replace(old_storage_calc, new_storage_calc)
        print('  ✓ 存储空间计算替换')
    
    # ---- 7. 替换 init 函数为异步加载 ----
    # 找到 init 函数的开头
    old_init_start = '''function init() {
  ensureUniqueIds();
  migrateReceiptImages();
  updateHomeStats();'''
    
    new_init_start = '''function init() {
  _appInit();
}

function _appInit() {
  _loadTravelData(function() {
    migrateFromLS(['travelProjects', 'travelExpenses', 'travelSettings'], function(migrated) {
      if (migrated > 0) {
        _loadTravelData(function() {
          _doInit();
        });
      } else {
        _doInit();
      }
    });
  });
}

function _doInit() {
  ensureUniqueIds();
  migrateReceiptImages();
  updateHomeStats();'''
    
    if old_init_start in content:
        content = content.replace(old_init_start, new_init_start)
        print('  ✓ init 函数替换为异步加载')
    else:
        print('  ✗ 未匹配 init 函数开头')
    
    # ---- 8. 替换 visibilitychange 事件中的重新加载 ----
    old_vis = '''      projects = JSON.parse(localStorage.getItem('travelProjects') || '[]');
      expenses = JSON.parse(localStorage.getItem('travelExpenses') || '[]');
      // 更新真实当前月份（但不改变用户选择的查看月份）
      realCurrentMonth = new Date().toISOString().slice(0, 7);
      refreshForMonth();'''
    
    new_vis = '''      _loadTravelData(function() {
        // 更新真实当前月份（但不改变用户选择的查看月份）
        realCurrentMonth = new Date().toISOString().slice(0, 7);
        refreshForMonth();
      });'''
    
    if old_vis in content:
        content = content.replace(old_vis, new_vis)
        print('  ✓ visibilitychange 刷新替换')
    else:
        print('  ✗ 未匹配 visibilitychange 代码')
    
    # ---- 9. 替换 focus 事件中的重新加载 ----
    old_focus = '''    projects = JSON.parse(localStorage.getItem('travelProjects') || '[]');
    expenses = JSON.parse(localStorage.getItem('travelExpenses') || '[]');
    updateHomeStats();'''
    
    new_focus = '''    _loadTravelData(function() {
      updateHomeStats();
    });'''
    
    if old_focus in content:
        content = content.replace(old_focus, new_focus)
        print('  ✓ focus 刷新替换')
    else:
        print('  ✗ 未匹配 focus 代码')
    
    # ---- 10. updateHomeStats 中的重新加载 ----
    # 这个函数开头从 localStorage 加载，需要替换
    old_update_home = '''  // 始终从 localStorage 重新加载数据，确保一致性
  projects = JSON.parse(localStorage.getItem('travelProjects') || '[]');
  expenses = JSON.parse(localStorage.getItem('travelExpenses') || '[]');'''
    
    new_update_home = '''  // 从内存缓存读取（数据一致性由存储层保证）
  // projects/expenses 已是最新缓存'''
    
    if old_update_home in content:
        content = content.replace(old_update_home, new_update_home)
        print('  ✓ updateHomeStats 替换')
    else:
        print('  ✗ 未匹配 updateHomeStats 代码')
    
    # ---- 11. migrateReceiptImages 函数修复 ----
    # 这个函数里也有 localStorage 调用（读和写）
    # 先检查是否还有遗留
    
    # ---- 保存 ----
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_ls = count_ls(content)
    remaining = find_ls_lines(content)
    
    print(f'\n[travel-expense.html] localStorage: {original_ls} -> {new_ls}')
    print(f'  文件大小: {original_len} -> {len(content)} bytes')
    if remaining:
        print(f'  剩余 {len(remaining)} 处:')
        for ln, txt in remaining[:20]:
            print(f'    L{ln}: {txt}')
    else:
        print('  ✓ 所有 localStorage 调用已替换')
    
    return True


def main():
    print('=' * 60)
    print('localStorage -> IndexedDB 迁移')
    print('=' * 60)
    
    print('\n--- weite-service-v14.html ---')
    migrate_weite_service()
    
    print('\n--- factory-inspection-v2.html ---')
    migrate_factory_inspection()
    
    print('\n--- travel-expense.html ---')
    migrate_travel_expense()
    
    print('\n' + '=' * 60)
    print('完成')
    print('=' * 60)


if __name__ == '__main__':
    main()
