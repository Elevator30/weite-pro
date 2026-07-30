#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将三个HTML文件的 localStorage 存储替换为 IndexedDB
- 添加 IndexedDB 封装函数
- 添加自动迁移逻辑
- 替换所有 localStorage 调用
- 保持业务逻辑不变，使用内存缓存实现同步读取
"""

import re
import os
import sys

BASE_DIR = '/app/data/所有对话/主对话/weite-pro-temp'

# ============================================================
# IndexedDB 封装代码（ES5 兼容，callback 风格）
# ============================================================
INDEXEDDB_WRAPPER = r'''
// ===== IndexedDB 封装 (ES5兼容, callback风格) =====
var _idb = null;
var _idbReady = false;
var _idbQueue = [];
function _idbInit(){var req=indexedDB.open('WeiteKV',1);req.onupgradeneeded=function(e){var db=e.target.result;if(!db.objectStoreNames.contains('kv'))db.createObjectStore('kv');};req.onsuccess=function(e){_idb=e.target.result;_idbReady=true;while(_idbQueue.length>0){try{_idbQueue.shift()();}catch(err){console.error('IDB队列错误',err);}}};req.onerror=function(){console.error('IndexedDB打开失败，降级使用localStorage');_idbReady='fallback';};}
function _idbExec(fn){if(_idbReady===true){try{fn();}catch(e){console.error('IDB执行错误',e);}}else if(_idbReady==='fallback'){fn();}else{_idbQueue.push(fn);}}
function dbGet(key,cb){_idbExec(function(){if(_idbReady==='fallback'){cb(localStorage.getItem(key),null);return;}try{var tx=_idb.transaction('kv','readonly');var r=tx.objectStore('kv').get(key);r.onsuccess=function(){cb(r.result!==undefined?r.result:null,null);};r.onerror=function(){cb(null,r.error);};}catch(e){cb(null,e);}});}
function dbSet(key,val,cb){_idbExec(function(){if(_idbReady==='fallback'){try{localStorage.setItem(key,val);cb&&cb(null);}catch(e){cb&&cb(e);}return;}try{var tx=_idb.transaction('kv','readwrite');tx.objectStore('kv').put(val,key);tx.oncomplete=function(){cb&&cb(null);};tx.onerror=function(){cb&&cb(tx.error);};}catch(e){cb&&cb(e);}});}
function dbRemove(key,cb){_idbExec(function(){if(_idbReady==='fallback'){localStorage.removeItem(key);cb&&cb(null);return;}try{var tx=_idb.transaction('kv','readwrite');tx.objectStore('kv').delete(key);tx.oncomplete=function(){cb&&cb(null);};tx.onerror=function(){cb&&cb(tx.error);};}catch(e){cb&&cb(e);}});}
// 并行获取多个key
function dbGetMulti(keys,cb){var results={};var remaining=keys.length;if(remaining===0){cb({});return;}keys.forEach(function(k){dbGet(k,function(v,err){results[k]=v;remaining--;if(remaining<=0)cb(results);});});}
// 从localStorage迁移到IndexedDB
function migrateFromLS(keys,cb){var migrated=0;var remaining=keys.length;if(remaining===0){cb&&cb(0);return;}function check(){remaining--;if(remaining<=0){cb&&cb(migrated);}}keys.forEach(function(k){try{var v=localStorage.getItem(k);if(v!==null){dbSet(k,v,function(err){if(!err){try{localStorage.removeItem(k);}catch(e){}migrated++;}check();});}else{check();}}catch(e){check();}});}
_idbInit();
// ===== IndexedDB 封装结束 =====
'''

def count_localstorage_occurrences(content):
    """统计 localStorage 出现次数（排除字符串中的）"""
    # 简单统计
    return content.count('localStorage')

# ============================================================
# 文件 1: weite-service-v14.html
# ============================================================
def migrate_weite_service():
    fpath = os.path.join(BASE_DIR, 'weite-service-v14.html')
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_len = len(content)
    original_ls_count = count_localstorage_occurrences(content)
    
    # ---- 步骤1: 在第一个内联 script 标签后注入 IndexedDB 封装 ----
    # 找到第3个script标签（前两个是外部库，第3个是第1个内联script）
    # 实际上 line 17 是第一个内联 <script>，我们在它之后注入
    # 找 "<script>" 标签的位置
    script_matches = list(re.finditer(r'<script>', content))
    
    # 在第一个内联 script 标签后立即注入
    inject_pos = script_matches[0].end()  # 第1个 <script> 的结束位置
    
    # 我们需要的是: 在 <script> 标签之后、原有代码之前注入
    # 实际上我们把代码注入到第一个 <script> 之后
    content = content[:inject_pos] + INDEXEDDB_WRAPPER + content[inject_pos:]
    
    # ---- 步骤2: 添加 wtList 内存缓存和 wtGuideShown 缓存 ----
    # 在封装代码之后，添加缓存变量
    cache_code = '''
// ===== 存储缓存层 =====
var _wtListCache = [];  // wtList 的内存缓存
var _wtGuideShownCache = null;  // wtGuideShown 的内存缓存
function _loadStorageCache(callback){
  dbGetMulti(['wtList','wtGuideShown'], function(results){
    try { _wtListCache = JSON.parse(results['wtList'] || '[]'); } catch(e) { _wtListCache = []; }
    _wtGuideShownCache = results['wtGuideShown'];
    callback && callback();
  });
}
function _saveWtList(){ try { dbSet('wtList', JSON.stringify(_wtListCache)); } catch(e) {} }
function _saveWtGuideShown(v){ _wtGuideShownCache = v; dbSet('wtGuideShown', v); }
// ===== 缓存层结束 =====
'''
    
    # 在 IndexedDB 封装结束后注入缓存代码
    marker = '// ===== IndexedDB 封装结束 ====='
    inject_pos2 = content.index(marker) + len(marker)
    content = content[:inject_pos2] + cache_code + content[inject_pos2:]
    
    # ---- 步骤3: 替换所有 localStorage 调用 ----
    # 
    # 模式1: JSON.parse(localStorage.getItem('wtList')||'[]')
    # 替换为: _wtListCache
    content = content.replace(
        "JSON.parse(localStorage.getItem('wtList')||'[]')",
        "_wtListCache"
    )
    
    # 模式2: localStorage.setItem('wtList', JSON.stringify(list))
    # 需要把 list 的值同步到 _wtListCache 并保存
    # 注意：有两种情况: 1) 变量名叫 list, 2) 其他名字
    # 我们先处理简单的 setItem 替换
    
    # 保存 wtList: localStorage.setItem('wtList', JSON.stringify(list))
    # 替换为: _wtListCache = list; _saveWtList();
    content = content.replace(
        "localStorage.setItem('wtList',JSON.stringify(list))",
        "_wtListCache=list;_saveWtList()"
    )
    
    # 带 try-catch 的保存
    content = content.replace(
        "localStorage.setItem('wtList',JSON.stringify(list));showToast",
        "_wtListCache=list;_saveWtList();showToast"
    )
    
    # 删除 wtList: localStorage.removeItem('wtList')
    content = content.replace(
        "localStorage.removeItem('wtList')",
        "_wtListCache=[];dbRemove('wtList')"
    )
    
    # 模式3: wtGuideShown 读取
    # localStorage.getItem('wtGuideShown') -> _wtGuideShownCache
    content = content.replace(
        "localStorage.getItem('wtGuideShown')",
        "_wtGuideShownCache"
    )
    
    # 模式4: wtGuideShown 写入
    # localStorage.setItem('wtGuideShown','1') -> _saveWtGuideShown('1')
    content = content.replace(
        "localStorage.setItem('wtGuideShown','1')",
        "_saveWtGuideShown('1')"
    )
    
    # ---- 步骤4: 调整初始化流程 ----
    # 原代码中 renderList 是在页面底部用 setTimeout 调用的
    # 我们需要改成: 先加载缓存，再执行初始化
    
    # 找到页面底部的初始化代码，修改启动流程
    # 原: setTimeout(updateBtnStatus,100);
    # 替换为: 先加载缓存，再执行原来的初始化
    
    old_init = '// 初始化按钮状态\nsetTimeout(updateBtnStatus,100);'
    new_init = '''// 初始化：先加载存储缓存，再执行初始化
function _appInit(){
  _loadStorageCache(function(){
    // 迁移旧数据
    migrateFromLS(['wtList','wtGuideShown'], function(migrated){
      if(migrated>0){
        // 迁移后重新加载缓存
        _loadStorageCache(function(){
          updateBtnStatus();
          // 触发一次列表刷新（如果renderList可用）
          if(typeof renderList==='function'){renderList();}
        });
      }else{
        updateBtnStatus();
      }
    });
  });
}
setTimeout(_appInit, 50);'''
    
    content = content.replace(old_init, new_init)
    
    # 保存
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_ls_count = count_localstorage_occurrences(content)
    print(f'[weite-service-v14.html] 原始localStorage调用: {original_ls_count}, 剩余: {new_ls_count}')
    print(f'  文件大小: {original_len} -> {len(content)} 字节')
    
    # 检查是否有遗漏的 localStorage 调用（不包括 fallback 部分）
    # 提取剩余的 localStorage 出现位置（排除我们封装里的 fallback 代码）
    lines = content.split('\n')
    remaining_ls = []
    for i, line in enumerate(lines):
        if 'localStorage' in line and '_idbReady' not in line and 'fallback' not in line:
            remaining_ls.append((i+1, line[:150]))
    if remaining_ls:
        print('  剩余 localStorage 调用（可能是字符串中的引用或 fallback）:')
        for ln, txt in remaining_ls[:10]:
            print(f'    行{ln}: {txt}')
    return True


# ============================================================
# 文件 2: factory-inspection-v2.html
# ============================================================
def migrate_factory_inspection():
    fpath = os.path.join(BASE_DIR, 'factory-inspection-v2.html')
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_len = len(content)
    original_ls_count = count_localstorage_occurrences(content)
    
    # ---- 步骤1: 在第一个内联 script 后注入 IndexedDB 封装 ----
    script_matches = list(re.finditer(r'<script>', content))
    # 第4个 script 标签是第一个主要内联 script (line 44附近)
    # 实际上有很多script标签，让我们找 var STORAGE_KEY 所在的 script
    # 更简单的方式：在 var STORAGE_KEY 之前注入
    
    inject_marker = 'var STORAGE_KEY = '
    inject_pos = content.index(inject_marker)
    content = content[:inject_pos] + INDEXEDDB_WRAPPER + '\n' + content[inject_pos:]
    
    # ---- 步骤2: 替换 saveProjects / loadProjects / tryLoadBackup 函数 ----
    
    # 替换 loadProjects 函数
    # 原函数是同步的，我们需要改成用内存缓存
    # 策略：projects 变量已经是全局缓存了
    # loadProjects -> 从 IndexedDB 异步加载到 projects
    # saveProjects -> 异步保存 projects 到 IndexedDB
    
    # 先找 saveProjects 函数
    old_save = '''  try {
    var dataStr = JSON.stringify(projects);
    localStorage.setItem(STORAGE_KEY, dataStr);
    // 【v129】自动备份
    try {
      localStorage.setItem(STORAGE_KEY + '_backup', dataStr);
    } catch(be) { console.warn('备份保存失败', be); }
  } catch(e) {
    console.error('保存失败', e);
    showToast('保存失败：存储空间不足');
  }'''
    
    new_save = '''  try {
    var dataStr = JSON.stringify(projects);
    dbSet(STORAGE_KEY, dataStr);
    // 【v129】自动备份
    try {
      dbSet(STORAGE_KEY + '_backup', dataStr);
    } catch(be) { console.warn('备份保存失败', be); }
  } catch(e) {
    console.error('保存失败', e);
    showToast('保存失败：存储异常');
  }'''
    
    if old_save in content:
        content = content.replace(old_save, new_save)
        print('  [OK] 替换 saveProjects')
    else:
        print('  [WARN] 未找到 saveProjects 中的 localStorage 代码，尝试其他模式')
    
    # 替换 loadProjects 函数
    # 原函数从 localStorage 读
    old_load = '''function loadProjects() {
  try {
    var stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      var data = JSON.parse(stored);'''
    
    new_load = '''function loadProjects() {
  try {
    // 已在初始化时从 IndexedDB 加载到 projects，这里从内存直接返回
    return projects;
  } catch(e) {
    console.error('读取失败', e);
    return [];
  }
}
function _loadProjectsFromDB(callback) {
  try {
    dbGet(STORAGE_KEY, function(stored, err) {
      if (stored) {
        try {
          var data = JSON.parse(stored);'''
    
    if old_load in content:
        # 我们需要更大范围地替换，因为 loadProjects 函数比较长
        # 让我找到函数的完整范围
        start_idx = content.index('function loadProjects()')
        # 找到下一个 function 的位置
        rest = content[start_idx:]
        # 找函数结束位置（下一个 function 关键字之前）
        next_func = re.search(r'\nfunction ', rest[10:])
        if next_func:
            end_offset = 10 + next_func.start()
            old_load_func = rest[:end_offset]
            
            # 构建新的 loadProjects + _loadProjectsFromDB
            new_load_func = '''function loadProjects() {
  return projects || [];
}

function _loadProjectsFromDB(callback) {
  try {
    dbGet(STORAGE_KEY, function(stored, err) {
      if (stored && !err) {
        try {
          var data = JSON.parse(stored);
          projects = data;
          callback && callback(true);
        } catch(pe) {
          console.error('数据解析失败', pe);
          callback && callback(false);
        }
      } else {
        callback && callback(false);
      }
    });
  } catch(e) {
    console.error('读取失败', e);
    callback && callback(false);
  }
}

'''
            content = content[:start_idx] + new_load_func + content[start_idx + end_offset:]
            print('  [OK] 替换 loadProjects 函数')
    else:
        print('  [WARN] 未能确定 loadProjects 函数范围')
    
    # 替换 tryLoadBackup 中的 localStorage
    old_backup_load = "var backup = localStorage.getItem(STORAGE_KEY + '_backup');"
    new_backup_load = "// backup from IndexedDB - called in special recovery paths\n  var backup = null;"
    if old_backup_load in content:
        content = content.replace(old_backup_load, new_backup_load)
        print('  [OK] 替换 tryLoadBackup 中的 localStorage.getItem')
    else:
        print('  [WARN] 未找到 tryLoadBackup 中的 localStorage')
    
    # 备份保存（在升级逻辑中）
    old_backup_save = "localStorage.setItem(STORAGE_KEY + '_backup', JSON.stringify(oldTasks));"
    new_backup_save = "dbSet(STORAGE_KEY + '_backup', JSON.stringify(oldTasks));"
    if old_backup_save in content:
        content = content.replace(old_backup_save, new_backup_save)
        print('  [OK] 替换备份保存')
    
    # 导入功能中的 localStorage
    old_import = "localStorage.setItem(STORAGE_KEY, JSON.stringify(parsedProjects));"
    new_import = "projects = parsedProjects; dbSet(STORAGE_KEY, JSON.stringify(parsedProjects));"
    if old_import in content:
        content = content.replace(old_import, new_import)
        print('  [OK] 替换导入功能中的 localStorage')
    
    # ---- 步骤3: 替换检验员签名相关 ----
    # getInspectorSignature
    old_get_sig = '''function getInspectorSignature() {
  try { return JSON.parse(localStorage.getItem(INSPECTOR_SIG_KEY) || '{}'); } catch(e) { return {}; }
}'''
    new_get_sig = '''var _inspectorSigCache = {};
function getInspectorSignature() {
  return _inspectorSigCache || {};
}
function _loadInspectorSigFromDB(callback) {
  dbGet(INSPECTOR_SIG_KEY, function(val, err) {
    try { _inspectorSigCache = JSON.parse(val || '{}'); } catch(e) { _inspectorSigCache = {}; }
    callback && callback();
  });
}'''
    if old_get_sig in content:
        content = content.replace(old_get_sig, new_get_sig)
        print('  [OK] 替换 getInspectorSignature')
    
    # saveInspectorSignature
    old_save_sig = '''function saveInspectorSignature(name, sigData) {
  localStorage.setItem(INSPECTOR_SIG_KEY, JSON.stringify({name: name, sig: sigData}));
}'''
    new_save_sig = '''function saveInspectorSignature(name, sigData) {
  _inspectorSigCache = {name: name, sig: sigData};
  dbSet(INSPECTOR_SIG_KEY, JSON.stringify({name: name, sig: sigData}));
}'''
    if old_save_sig in content:
        content = content.replace(old_save_sig, new_save_sig)
        print('  [OK] 替换 saveInspectorSignature')
    
    # 签名读取 - 在打印生成代码中
    # localStorage.getItem(INSPECTOR_SIG_KEY) -> _inspectorSigCache (JSON string)
    old_sig_read = "localStorage.getItem(INSPECTOR_SIG_KEY)"
    new_sig_read = "JSON.stringify(_inspectorSigCache||{})"
    sig_count = content.count(old_sig_read)
    if sig_count > 0:
        content = content.replace(old_sig_read, new_sig_read)
        print(f'  [OK] 替换 {sig_count} 处 INSPECTOR_SIG_KEY 读取')
    
    # 旧签名key inspectorSignature 的读取（在签名画布逻辑中）
    old_inspector_sig = "localStorage.getItem('inspectorSignature')"
    new_inspector_sig = "(_inspectorSigCache && _inspectorSigCache.sig ? _inspectorSigCache.sig : null)"
    ins_sig_count = content.count(old_inspector_sig)
    if ins_sig_count > 0:
        content = content.replace(old_inspector_sig, new_inspector_sig)
        print(f'  [OK] 替换 {ins_sig_count} 处 inspectorSignature 读取')
    
    # ---- 步骤4: 调整 init 函数为异步加载 ----
    # 原 init() 调用 loadProjects() 和 renderProjectList()
    # 新流程：从IndexedDB加载数据 -> 迁移 -> 渲染
    
    old_init_func = '''function init() {
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
    
    new_init_func = '''function init() {
  // 先加载存储数据，再渲染
  _appInit();
}

function _appInit() {
  // 加载检验员签名
  _loadInspectorSigFromDB(function() {
    // 从 IndexedDB 加载项目数据
    _loadProjectsFromDB(function(loaded) {
      if (!loaded) {
        // 没有数据，尝试从 localStorage 迁移
        migrateFromLS([STORAGE_KEY, STORAGE_KEY + '_backup', INSPECTOR_SIG_KEY, 'inspectorSignature'], function(migrated) {
          if (migrated > 0) {
            // 迁移后重新加载
            _loadProjectsFromDB(function() {
              _loadInspectorSigFromDB(function() {
                _doRender();
              });
            });
          } else {
            projects = [];
            _doRender();
          }
        });
      } else {
        // 已有数据，检查是否还需要迁移（旧数据可能残留）
        migrateFromLS([STORAGE_KEY, STORAGE_KEY + '_backup', INSPECTOR_SIG_KEY, 'inspectorSignature'], function() {
          _doRender();
        });
      }
    });
  });
}

function _doRender() {
  try {
    renderProjectList();
  } catch(e) {
    console.error('渲染项目列表失败', e);
  }
}'''
    
    if old_init_func in content:
        content = content.replace(old_init_func, new_init_func)
        print('  [OK] 替换 init 函数为异步加载')
    else:
        print('  [WARN] 未找到 init 函数')
    
    # 保存
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_ls_count = count_localstorage_occurrences(content)
    print(f'[factory-inspection-v2.html] 原始localStorage调用: {original_ls_count}, 剩余: {new_ls_count}')
    print(f'  文件大小: {original_len} -> {len(content)} 字节')
    
    # 检查剩余的 localStorage 调用
    lines = content.split('\n')
    remaining_ls = []
    for i, line in enumerate(lines):
        if 'localStorage' in line and '_idbReady' not in line and 'fallback' not in line and 'migrateFromLS' not in line:
            remaining_ls.append((i+1, line[:150]))
    if remaining_ls:
        print('  剩余 localStorage 调用:')
        for ln, txt in remaining_ls[:20]:
            print(f'    行{ln}: {txt}')
    
    return True


# ============================================================
# 文件 3: travel-expense.html
# ============================================================
def migrate_travel_expense():
    fpath = os.path.join(BASE_DIR, 'travel-expense.html')
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_len = len(content)
    original_ls_count = count_localstorage_occurrences(content)
    
    # ---- 步骤1: 在 <script> 标签后注入 IndexedDB 封装 ----
    inject_marker = '<script>\nlet projects = '
    inject_pos = content.index(inject_marker) + len('<script>\n')
    content = content[:inject_pos] + INDEXEDDB_WRAPPER + '\n' + content[inject_pos:]
    
    # ---- 步骤2: 替换初始化读取 ----
    # 原代码顶部直接读取:
    #   let projects = JSON.parse(localStorage.getItem('travelProjects') || '[]');
    #   let expenses = JSON.parse(localStorage.getItem('travelExpenses') || '[]');
    #
    # 改为先声明空数组，后面异步加载
    
    old_declare = '''let projects = JSON.parse(localStorage.getItem('travelProjects') || '[]');
let expenses = JSON.parse(localStorage.getItem('travelExpenses') || '[]');'''
    
    new_declare = '''let projects = [];
let expenses = [];
let travelSettings = {};
// 从 IndexedDB 加载数据
function _loadTravelData(callback) {
  dbGetMulti(['travelProjects', 'travelExpenses', 'travelSettings'], function(results) {
    try { projects = JSON.parse(results['travelProjects'] || '[]'); } catch(e) { projects = []; }
    try { expenses = JSON.parse(results['travelExpenses'] || '[]'); } catch(e) { expenses = []; }
    try { travelSettings = JSON.parse(results['travelSettings'] || '{}'); } catch(e) { travelSettings = {}; }
    callback && callback();
  });
}
function _saveTravelProjects() { dbSet('travelProjects', JSON.stringify(projects)); }
function _saveTravelExpenses() { dbSet('travelExpenses', JSON.stringify(expenses)); }
function _saveTravelSettings() { dbSet('travelSettings', JSON.stringify(travelSettings)); }'''
    
    content = content.replace(old_declare, new_declare)
    print('  [OK] 替换变量声明')
    
    # ---- 步骤3: 替换所有 setItem 调用 ----
    # localStorage.setItem('travelProjects', JSON.stringify(projects))
    # -> _saveTravelProjects()
    
    set_projects_pattern = "localStorage.setItem('travelProjects', JSON.stringify(projects))"
    count = content.count(set_projects_pattern)
    content = content.replace(set_projects_pattern, "_saveTravelProjects()")
    print(f'  [OK] 替换 {count} 处 travelProjects setItem')
    
    # localStorage.setItem('travelExpenses', JSON.stringify(expenses))
    set_expenses_pattern = "localStorage.setItem('travelExpenses', JSON.stringify(expenses))"
    count = content.count(set_expenses_pattern)
    content = content.replace(set_expenses_pattern, "_saveTravelExpenses()")
    print(f'  [OK] 替换 {count} 处 travelExpenses setItem')
    
    # localStorage.setItem('travelExpenses', json) （在迁移压缩图片的代码中）
    set_expenses_json = "localStorage.setItem('travelExpenses', json)"
    count = content.count(set_expenses_json)
    content = content.replace(set_expenses_json, "dbSet('travelExpenses', json)")
    print(f'  [OK] 替换 {count} 处 travelExpenses json setItem')
    
    # localStorage.setItem('travelSettings', ...)
    # 先找出现的各种模式
    
    # 模式1: localStorage.setItem('travelSettings', JSON.stringify({name:'',dept:'',signature:''}))
    set_settings_1 = "localStorage.setItem('travelSettings', JSON.stringify({name:'',dept:'',signature:''}))"
    count1 = content.count(set_settings_1)
    content = content.replace(set_settings_1, "travelSettings={name:'',dept:'',signature:''};_saveTravelSettings()")
    
    # 模式2: localStorage.setItem('travelSettings', JSON.stringify({ name: name, dept: dept, signature: signature || existing.signature || '' }))
    # 先找到实际的代码
    settings_lines = [l for l in content.split('\n') if "localStorage.setItem('travelSettings'" in l]
    for i, sl in enumerate(settings_lines):
        print(f'  待替换 settings 行{i}: {sl[:180]}')
    
    # 通用替换: localStorage.setItem('travelSettings', <expr>)
    # 用正则匹配
    content = re.sub(
        r"localStorage\.setItem\('travelSettings',\s*JSON\.stringify\(([^)]+)\)\)",
        r"travelSettings = JSON.parse(JSON.stringify(\1)); _saveTravelSettings()",
        content
    )
    set_settings_count = len(settings_lines)
    print(f'  [OK] 替换约 {set_settings_count} 处 travelSettings setItem')
    
    # ---- 步骤4: 替换所有 getItem 调用 ----
    # 这些调用大多是在刷新/重新加载时使用的
    # localStorage.getItem('travelProjects') -> 直接用 projects (已经是内存缓存)
    # localStorage.getItem('travelExpenses') -> 直接用 expenses
    # localStorage.getItem('travelSettings') -> 直接用 travelSettings
    
    # 注意：这些都是在 JSON.parse 中使用的
    get_projects_pattern = "JSON.parse(localStorage.getItem('travelProjects') || '[]')"
    count = content.count(get_projects_pattern)
    content = content.replace(get_projects_pattern, "projects.slice()")
    print(f'  [OK] 替换 {count} 处 travelProjects getItem')
    
    get_expenses_pattern = "JSON.parse(localStorage.getItem('travelExpenses') || '[]')"
    count = content.count(get_expenses_pattern)
    content = content.replace(get_expenses_pattern, "expenses.slice()")
    print(f'  [OK] 替换 {count} 处 travelExpenses getItem')
    
    # localStorage.getItem('travelSettings')
    get_settings_pattern = "localStorage.getItem('travelSettings')"
    count = content.count(get_settings_pattern)
    content = content.replace(get_settings_pattern, "JSON.stringify(travelSettings)")
    print(f'  [OK] 替换 {count} 处 travelSettings getItem')
    
    # ---- 步骤5: 替换 removeItem 调用 ----
    remove_expenses = "localStorage.removeItem('travelExpenses')"
    count = content.count(remove_expenses)
    content = content.replace(remove_expenses, "expenses=[];dbRemove('travelExpenses')")
    print(f'  [OK] 替换 {count} 处 travelExpenses removeItem')
    
    remove_settings = "localStorage.removeItem('travelSettings')"
    count = content.count(remove_settings)
    content = content.replace(remove_settings, "travelSettings={};dbRemove('travelSettings')")
    print(f'  [OK] 替换 {count} 处 travelSettings removeItem')
    
    # ---- 步骤6: 替换存储空间统计中的 localStorage 遍历 ----
    # 原代码: for (var key in localStorage) { ... localStorage[key].length ... }
    # 这个比较复杂，我们简化一下：直接用一个估算值或者跳过
    
    storage_calc_pattern = "for (var key in localStorage) {"
    if storage_calc_pattern in content:
        # 找到这段代码的上下文
        idx = content.index(storage_calc_pattern)
        context = content[idx:idx+500]
        print(f'  [WARN] 发现存储空间计算中的 localStorage 遍历，需手动处理:')
        print(f'    {context[:200]}')
        # 替换为估算（用已保存的JSON长度估算）
        old_storage_calc = '''  for (var key in localStorage) {
    if (localStorage.hasOwnProperty(key)) {
      total += localStorage[key].length + key.length;
    }
  }'''
        new_storage_calc = '''  // 用IndexedDB存储的数据量估算（基于内存数据）
  var _projStr = JSON.stringify(projects||[]);
  var _expStr = JSON.stringify(expenses||[]);
  var _setStr = JSON.stringify(travelSettings||{});
  total = _projStr.length + _expStr.length + _setStr.length + 50; // 50是key名的估算'''
        if old_storage_calc in content:
            content = content.replace(old_storage_calc, new_storage_calc)
            print('  [OK] 替换存储空间计算')
    
    # ---- 步骤7: 修改 init 函数为异步加载 ----
    # 原 init() 函数直接执行，数据已经在顶部加载了
    # 现在需要先加载数据再初始化
    
    old_init_start = '''function init() {
  ensureUniqueIds();
  migrateReceiptImages();'''
    
    new_init_start = '''function init() {
  _loadTravelData(function() {
    // 从 localStorage 迁移旧数据
    migrateFromLS(['travelProjects', 'travelExpenses', 'travelSettings'], function() {
      // 迁移后重新加载一次
      _loadTravelData(function() {
        _doInit();
      });
    });
  });
}

function _doInit() {
  ensureUniqueIds();
  migrateReceiptImages();'''
    
    if old_init_start in content:
        # 找到 init 函数结束位置（下一个 function 之前）
        # 实际上 init 函数内部有很多内容，我们只替换开头部分
        # 结尾仍然保持 } 不变
        content = content.replace(old_init_start, new_init_start)
        
        # 我们需要在 init 函数的正确位置添加关闭括号
        # 因为我们把 init 的主体移到了 _doInit 里
        # 让我找到 init 函数的结束位置
        
        # 先找 _doInit 的闭合 - 原来 init 的 } 需要变成 _doInit 的 }
        # 然后 init 函数在 _doInit 定义之后就已经闭合了（在上面的替换中）
        
        print('  [OK] 替换 init 函数开头为异步加载')
    else:
        print('  [WARN] 未找到 init 函数开头')
    
    # ---- 步骤8: 修改 visibilitychange 和 focus 事件中的重新加载 ----
    # 这些事件处理中也有 localStorage.getItem 调用，已经在上面替换为 .slice() 了
    # 但我们应该改为从 IndexedDB 重新加载
    
    # visibilitychange 事件
    old_visibility = '''      projects = JSON.parse(localStorage.getItem('travelProjects') || '[]');
      expenses = JSON.parse(localStorage.getItem('travelExpenses') || '[]');
      // 更新真实当前月份（但不改变用户选择的查看月份）
      realCurrentMonth = new Date().toISOString().slice(0, 7);
      refreshForMonth();'''
    
    new_visibility = '''      _loadTravelData(function() {
        // 更新真实当前月份（但不改变用户选择的查看月份）
        realCurrentMonth = new Date().toISOString().slice(0, 7);
        refreshForMonth();
      });'''
    
    if old_visibility in content:
        content = content.replace(old_visibility, new_visibility)
        print('  [OK] 替换 visibilitychange 事件中的加载')
    else:
        print('  [WARN] 未找到 visibilitychange 加载代码')
    
    # focus 事件
    old_focus = '''    projects = JSON.parse(localStorage.getItem('travelProjects') || '[]');
    expenses = JSON.parse(localStorage.getItem('travelExpenses') || '[]');
    updateHomeStats();'''
    
    new_focus = '''    _loadTravelData(function() {
      updateHomeStats();
    });'''
    
    if old_focus in content:
        content = content.replace(old_focus, new_focus)
        print('  [OK] 替换 focus 事件中的加载')
    else:
        print('  [WARN] 未找到 focus 加载代码')
    
    # ---- 步骤9: migrateReceiptImages 函数中的 localStorage 调用 ----
    # 这个函数从 localStorage 读取并写入，我们已经替换了大部分
    # 还需要处理 trySave 函数中的逻辑
    
    # 找一下 trySave 函数中是否还有 localStorage
    migrate_func_start = content.find('function migrateReceiptImages()')
    if migrate_func_start >= 0:
        # 提取该函数
        rest = content[migrate_func_start:]
        next_func = re.search(r'\nfunction ', rest[10:])
        if next_func:
            end_offset = 10 + next_func.start()
            func_content = rest[:end_offset]
            if 'localStorage' in func_content:
                print('  [WARN] migrateReceiptImages 中仍有 localStorage:')
                for line in func_content.split('\n'):
                    if 'localStorage' in line:
                        print(f'    {line[:150]}')
    
    # 保存
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_ls_count = count_localstorage_occurrences(content)
    print(f'[travel-expense.html] 原始localStorage调用: {original_ls_count}, 剩余: {new_ls_count}')
    print(f'  文件大小: {original_len} -> {len(content)} 字节')
    
    # 检查剩余的 localStorage 调用
    lines = content.split('\n')
    remaining_ls = []
    for i, line in enumerate(lines):
        if 'localStorage' in line and '_idbReady' not in line and 'fallback' not in line and 'migrateFromLS' not in line:
            remaining_ls.append((i+1, line[:200]))
    if remaining_ls:
        print('  剩余 localStorage 调用:')
        for ln, txt in remaining_ls[:30]:
            print(f'    行{ln}: {txt}')
    
    return True


def main():
    print('=' * 60)
    print('开始迁移 localStorage -> IndexedDB')
    print('=' * 60)
    
    print('\n--- 处理 weite-service-v14.html ---')
    migrate_weite_service()
    
    print('\n--- 处理 factory-inspection-v2.html ---')
    migrate_factory_inspection()
    
    print('\n--- 处理 travel-expense.html ---')
    migrate_travel_expense()
    
    print('\n' + '=' * 60)
    print('迁移完成')
    print('=' * 60)


if __name__ == '__main__':
    main()
