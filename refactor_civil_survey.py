#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
土建勘测模块重构脚本：单台电梯表单改为分区tab布局，楼层测量表改为纵向卡片
"""

import re

INPUT_FILE = 'weite-pro-temp/civil-survey.html'
OUTPUT_FILE = 'weite-pro-temp/civil-survey.html'

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"原文件大小: {len(content)} 字符")

# ========== 1. 添加新的 CSS 样式 ==========
# 在 .content-area 样式之前插入新的 tab 和 楼层卡片样式

new_css = '''
/* ===== 分区Tab ===== */
.zone-tabs{display:flex;gap:0;padding:0 8px;background:#fff;overflow-x:auto;flex-shrink:0;
  -webkit-overflow-scrolling:touch;border-bottom:2px solid #edf2f7;}
.zone-tabs::-webkit-scrollbar{display:none;}
.zone-tab{padding:12px 14px;white-space:nowrap;font-size:13px;font-weight:600;color:#718096;
  cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all .15s;flex-shrink:0;}
.zone-tab.active{color:#667eea;border-bottom-color:#667eea;}
.zone-panel{display:none;animation:fadeIn .2s ease;}
.zone-panel.active{display:block;}
@keyframes fadeIn{from{opacity:0;transform:translateY(4px);}to{opacity:1;transform:translateY(0);}}

/* ===== 楼层纵向卡片 ===== */
.floor-cards{display:flex;flex-direction:column;gap:10px;}
.floor-card{background:#fff;border:1.5px solid #e2e8f0;border-radius:10px;padding:12px;
  box-shadow:0 1px 3px rgba(0,0,0,.03);position:relative;}
.floor-card-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;
  padding-bottom:8px;border-bottom:1px dashed #edf2f7;}
.floor-no-badge{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;font-size:14px;
  font-weight:700;padding:4px 12px;border-radius:20px;min-width:50px;text-align:center;}
.floor-del-btn{background:none;border:none;color:#e53e3e;cursor:pointer;font-size:18px;
  padding:2px 8px;line-height:1;}
.floor-row{display:flex;gap:8px;margin-bottom:8px;align-items:center;}
.floor-row:last-child{margin-bottom:0;}
.floor-field{flex:1;min-width:0;}
.floor-field label{display:block;font-size:11px;color:#718096;margin-bottom:3px;font-weight:500;}
.floor-field input{width:100%;border:1.5px solid #e2e8f0;border-radius:6px;padding:6px 8px;
  font-size:13px;background:#fafafa;text-align:center;}
.floor-field input:focus{border-color:#667eea;background:#fff;outline:none;}
.floor-field.w40{flex:0 0 40%;}
.floor-field.w30{flex:0 0 30%;}
.floor-field.w25{flex:0 0 25%;}
.floor-field.w20{flex:0 0 20%;}
.floor-door-pos{display:flex;gap:4px;}
.floor-door-pos button{flex:1;padding:6px 2px;border:1.5px solid #e2e8f0;border-radius:6px;
  font-size:12px;cursor:pointer;background:#fff;color:#718096;font-weight:600;}
.floor-door-pos button.active{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border-color:transparent;}
.floor-remark-field{width:100%;}
.floor-remark-field input{text-align:left;}
.floor-divider{height:1px;background:#edf2f7;margin:8px 0;}
.floor-label{font-size:11px;color:#a0aec0;margin-right:4px;flex-shrink:0;}

/* 楼层操作栏 */
.floor-toolbar{display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap;align-items:center;}
.floor-toolbar-btn{padding:7px 12px;border:none;border-radius:7px;font-size:12px;font-weight:600;
  cursor:pointer;display:flex;align-items:center;gap:4px;flex-shrink:0;}
.floor-toolbar-btn.primary{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;}
.floor-toolbar-btn.secondary{background:#f7fafc;color:#4a5568;border:1.5px solid #e2e8f0;}
.floor-toolbar-btn.danger{background:#fff5f5;color:#e53e3e;border:1.5px solid #fed7d7;}

/* 楼层统计栏 */
.floor-stats-bar{display:flex;gap:12px;margin-bottom:12px;padding:10px 12px;
  background:linear-gradient(135deg,#f0f4ff,#f7f0ff);border-radius:8px;font-size:12px;flex-wrap:wrap;}
.floor-stat{display:flex;align-items:center;gap:5px;}
.floor-stat-label{color:#718096;font-size:11px;}
.floor-stat-val{font-weight:700;color:#2d3748;}
.floor-stat-val.min{color:#38a169;}
.floor-stat-val.max{color:#e53e3e;}

/* ===== 井道结构墙组 ===== */
.wall-group{background:#f7fafc;border-radius:8px;padding:10px 12px;margin-bottom:10px;}
.wall-group-title{font-size:12px;font-weight:700;color:#667eea;margin-bottom:8px;
  display:flex;align-items:center;gap:6px;}
.wall-form-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;}
.wall-form-grid .form-row{margin-bottom:0;}
.wall-form-grid .form-row.full{grid-column:1/-1;}

/* ===== 签字日期行 ===== */
.sig-date-row{display:flex;align-items:center;gap:8px;margin-top:6px;}
.sig-date-row label{font-size:11px;color:#718096;white-space:nowrap;}
.sig-date-row input{flex:1;border:1.5px solid #e2e8f0;border-radius:6px;padding:6px 8px;
  font-size:12px;background:#fafafa;}
.sig-date-row input:focus{border-color:#667eea;background:#fff;outline:none;}

/* ===== 子分组标题 ===== */
.sub-section-title{font-size:13px;font-weight:700;color:#2d3748;margin:14px 0 8px;
  display:flex;align-items:center;gap:6px;}
.sub-section-title:first-child{margin-top:0;}
.sub-section-title::before{content:'';width:3px;height:14px;background:linear-gradient(180deg,#667eea,#764ba2);border-radius:2px;}
'''

# 插入到 /* ===== 分层测量表 ===== */ 之前
insert_point = '/* ===== 分层测量表 ===== */'
if insert_point in content:
    content = content.replace(insert_point, new_css + '\n' + insert_point)
    print("✓ 已添加新CSS样式")
else:
    print("✗ 未找到CSS插入点")

# ========== 2. 调整 content-area 和 elevatorContent 的 HTML 结构 ==========
# 在 toolbar 下方添加 zone-tabs，修改 elevatorContent 为面板结构

# 找到 content-area div 内部结构
old_content_area = '''    <div class="content-area" id="contentArea">
      <div class="empty-state" id="emptyState">
        <div class="empty-icon">🏗️</div>
        <div class="empty-text">暂无项目，点击下方按钮创建第一个勘测项目</div>
        <button class="empty-btn" onclick="showNewProject()">+ 新建项目</button>
      </div>
      <div id="elevatorContent" style="display:none;"></div>
    </div>'''

new_content_area = '''    <div class="zone-tabs no-print" id="zoneTabs" style="display:none;"></div>
    <div class="content-area" id="contentArea">
      <div class="empty-state" id="emptyState">
        <div class="empty-icon">🏗️</div>
        <div class="empty-text">暂无项目，点击下方按钮创建第一个勘测项目</div>
        <button class="empty-btn" onclick="showNewProject()">+ 新建项目</button>
      </div>
      <div id="elevatorContent" style="display:none;"></div>
    </div>'''

if old_content_area in content:
    content = content.replace(old_content_area, new_content_area)
    print("✓ 已调整content-area结构，添加zone-tabs")
else:
    print("✗ 未找到content-area替换点")
    # 尝试模糊匹配
    print("  尝试模糊查找...")

# ========== 3. 添加新的 JS 变量和函数 ==========
# 在 // ===== 电梯内容渲染 ===== 之前，添加 tab 相关变量和函数

tab_js_code = '''
// ===== 分区Tab管理 =====
var currentTabIndex = 0;
var tabNames = ['基本参数', '楼层测量', '井道结构', '机房底坑', '示意图', '签字'];

function renderZoneTabs() {
  var tabsEl = document.getElementById('zoneTabs');
  if (!tabsEl) return;
  var html = '';
  for (var i = 0; i < tabNames.length; i++) {
    var active = i === currentTabIndex ? ' active' : '';
    html += '<div class="zone-tab' + active + '" onclick="switchTab(' + i + ')">' + tabNames[i] + '</div>';
  }
  tabsEl.innerHTML = html;
}

function switchTab(index) {
  if (index < 0 || index >= tabNames.length) return;
  currentTabIndex = index;
  renderZoneTabs();
  renderElevatorContent();
  // 滚动到顶部
  var contentArea = document.getElementById('contentArea');
  if (contentArea) contentArea.scrollTop = 0;
}

'''

# 插入到 // ===== 电梯内容渲染 ===== 之前
insert_js_point = '// ===== 电梯内容渲染 ====='
if insert_js_point in content:
    content = content.replace(insert_js_point, tab_js_code + insert_js_point)
    print("✓ 已添加Tab管理JS代码")
else:
    print("✗ 未找到Tab JS插入点")

# ========== 4. 重写 renderElevatorContent 函数 ==========
# 改为 tab 面板结构

old_render_func_start = 'function renderElevatorContent() {\n  var elev = getCurrentElevator();\n  if (!elev) return;\n  \n  var html = \'\';\n  \n  // 基本参数卡片\n  html += renderBasicInfoCard(elev);\n  \n  // 分层测量表卡片\n  html += renderFloorTableCard(elev);\n  \n  // 示意图卡片\n  html += renderSketchesCard(elev);\n  \n  // 特殊说明卡片\n  html += renderNotesCard(elev);\n  \n  // 签字卡片\n  html += renderSignatureCard(elev);\n  \n  document.getElementById(\'elevatorContent\').innerHTML = html;\n  updateFloorStats();\n}'

new_render_func = '''function renderElevatorContent() {
  var elev = getCurrentElevator();
  if (!elev) return;
  
  // 显示tab栏
  var tabsEl = document.getElementById('zoneTabs');
  if (tabsEl) tabsEl.style.display = 'flex';
  renderZoneTabs();
  
  var html = '';
  
  // Tab面板
  for (var i = 0; i < tabNames.length; i++) {
    var active = i === currentTabIndex ? ' active' : '';
    html += '<div class="zone-panel' + active + '" id="zonePanel_' + i + '">';
    
    if (i === 0) html += renderBasicInfoTab(elev);
    else if (i === 1) html += renderFloorTab(elev);
    else if (i === 2) html += renderShaftStructureTab(elev);
    else if (i === 3) html += renderMachinePitTab(elev);
    else if (i === 4) html += renderSketchesTab(elev);
    else if (i === 5) html += renderSignatureTab(elev);
    
    html += '</div>';
  }
  
  document.getElementById('elevatorContent').innerHTML = html;
  updateFloorStats();
}'''

if old_render_func_start in content:
    content = content.replace(old_render_func_start, new_render_func)
    print("✓ 已重写renderElevatorContent函数")
else:
    print("✗ 未找到renderElevatorContent函数")
    # 尝试查找函数起止
    pattern = r'function renderElevatorContent\(\) \{[^}]+\}'
    match = re.search(pattern, content)
    if match:
        print(f"  找到函数: {match.group()[:100]}...")

# ========== 5. 扩展 fieldMap，添加新字段 ==========
old_fieldmap_end = """  'elev_roomWidth': 'roomWidth',
  'elev_roomDepth': 'roomDepth',
  'elev_roomHeight': 'roomHeight'
};"""

new_fieldmap = """  'elev_roomWidth': 'roomWidth',
  'elev_roomDepth': 'roomDepth',
  'elev_roomHeight': 'roomHeight',
  // 勘测信息
  'elev_wellStatus': 'wellStatus',
  'elev_controlMode': 'controlMode',
  // 井道结构 - 后墙
  'elev_backWallType': 'backWallType',
  'elev_backWallThick': 'backWallThick',
  'elev_backWallOuter': 'backWallOuter',
  'elev_backRingBeam': 'backRingBeam',
  'elev_backBracket': 'backBracket',
  // 井道结构 - 左墙
  'elev_leftWallType': 'leftWallType',
  'elev_leftWallThick': 'leftWallThick',
  'elev_leftWallOuter': 'leftWallOuter',
  'elev_leftRingBeam': 'leftRingBeam',
  'elev_leftBracket': 'leftBracket',
  // 井道结构 - 右墙
  'elev_rightWallType': 'rightWallType',
  'elev_rightWallThick': 'rightWallThick',
  'elev_rightWallOuter': 'rightWallOuter',
  'elev_rightRingBeam': 'rightRingBeam',
  'elev_rightBracket': 'rightBracket',
  // 门过梁/门垛
  'elev_hasHeaderBeam': 'hasHeaderBeam',
  'elev_pierStructure': 'pierStructure',
  'elev_pierStatus': 'pierStatus',
  'elev_pierLeftWidth': 'pierLeftWidth',
  'elev_pierRightWidth': 'pierRightWidth',
  // 其他井道
  'elev_callBoxType': 'callBoxType',
  'elev_hasCorbel': 'hasCorbel',
  'elev_isThrough': 'isThrough',
  'elev_sightseeingType': 'sightseeingType',
  'elev_sightseeingSides': 'sightseeingSides',
  'elev_powerSupply': 'powerSupply',
  // 机房底坑
  'elev_roomForm': 'roomForm',
  'elev_roomLocalRaise': 'roomLocalRaise',
  'elev_roomRaiseMm': 'roomRaiseMm',
  'elev_pitFront': 'pitFront',
  'elev_pitBack': 'pitBack',
  'elev_liftHeight': 'liftHeight',
  'elev_wellTotalHeight': 'wellTotalHeight',
  // 签字日期
  'sig_surveyorDate': 'surveyorDate',
  'sig_reviewerDate': 'reviewerDate',
  'sig_draftsmanDate': 'draftsmanDate'
};"""

if old_fieldmap_end in content:
    content = content.replace(old_fieldmap_end, new_fieldmap)
    print("✓ 已扩展fieldMap，添加新字段映射")
else:
    print("✗ 未找到fieldMap替换点")

# ========== 6. 添加新的渲染函数 ==========
# 在 renderFloorTableCard 函数之前插入所有新的tab渲染函数

new_render_functions = '''
// ===== Tab1: 基本参数 =====
function renderBasicInfoTab(elev) {
  var html = '<div class="card">';
  html += '<div class="section-header"><span>📋 项目信息</span></div>';
  html += '<div class="form-grid">';
  html += formField('楼号', 'elev_buildingName', getCurrentBuildingName(), 'text', '', false);
  html += formField('梯号', 'elev_elevatorNo', elev.elevatorNo || '', 'text', 'updateElevField');
  html += formField('单元号', 'elev_unit', elev.unit || '', 'text', 'updateElevField');
  html += formField('安装地址', 'elev_address', elev.address || '', 'text', 'updateElevField', true);
  html += '</div></div>';
  
  html += '<div class="card">';
  html += '<div class="section-header"><span>⚙️ 技术参数</span></div>';
  html += '<div class="form-grid">';
  html += formField('梯型', 'elev_elevatorType', elev.elevatorType || '客梯', 'select', 'updateElevField', false,
    [['客梯','客梯'],['货梯','货梯'],['医用梯','医用梯'],['观光梯','观光梯'],['杂物梯','杂物梯'],['其他','其他']]);
  html += formField('开门方式', 'elev_doorType', elev.doorType || '中分', 'select', 'updateElevField', false,
    [['中分','中分'],['旁开','旁开']]);
  html += formField('有无机房', 'elev_hasMachineRoom', elev.hasMachineRoom || '有', 'select', 'updateElevField', false,
    [['有','有机房'],['无','无机房']]);
  html += formField('载重(kg)', 'elev_load', elev.load || '', 'number', 'updateElevField');
  html += formField('速度(m/s)', 'elev_speed', elev.speed || '', 'number', 'updateElevField', false, null, '0.1');
  html += formField('层数', 'elev_floors', elev.floors || '', 'number', 'updateElevField');
  html += formField('站数', 'elev_stops', elev.stops || '', 'number', 'updateElevField');
  html += formField('门数', 'elev_doors', elev.doors || '', 'number', 'updateElevField');
  html += '</div></div>';
  
  html += '<div class="card">';
  html += '<div class="section-header"><span>🔍 勘测信息</span></div>';
  html += '<div class="form-grid">';
  html += formField('勘测次数', 'elev_surveyCount', getProjectSurveyCount(), 'select', 'updateSurveyCount', false,
    [['首勘1次','首勘1次'],['复勘1次','复勘1次'],['复勘2次','复勘2次'],['复勘3次','复勘3次']]);
  html += formField('井道状态', 'elev_wellStatus', elev.wellStatus || '未建', 'select', 'updateElevField', false,
    [['未建','未建'],['在建','在建'],['已建','已建']]);
  html += formField('控制方式', 'elev_controlMode', elev.controlMode || '单控', 'select', 'updateElevField', false,
    [['单控','单控'],['并联','并联'],['群控','群控']]);
  html += '</div></div>';
  
  return html;
}

function getCurrentBuildingName() {
  var proj = getProject(currentProjectId);
  var bldg = getBuilding(proj, currentBuildingId);
  return bldg ? bldg.name : '';
}

function getProjectSurveyCount() {
  var proj = getProject(currentProjectId);
  return proj ? (proj.surveyCount || '首勘1次') : '首勘1次';
}

// ===== Tab2: 楼层测量（纵向卡片） =====
function renderFloorTab(elev) {
  var html = '';
  
  // 操作栏
  html += '<div class="floor-toolbar">';
  html += '<button class="floor-toolbar-btn primary" onclick="addFloorRow()">+ 添加一层</button>';
  html += '<button class="floor-toolbar-btn secondary" onclick="showBatchFloorModal()">⚡ 批量生成</button>';
  html += '<button class="floor-toolbar-btn secondary" onclick="sortFloors()">↕️ 排序</button>';
  html += '<button class="floor-toolbar-btn danger" onclick="deleteLastFloor()">− 删除末层</button>';
  html += '</div>';
  
  // 统计栏
  html += '<div class="floor-stats-bar" id="floorStats">';
  html += '<div class="floor-stat"><span class="floor-stat-label">井道宽最小:</span><span class="floor-stat-val min" id="statWidthMin">--</span></div>';
  html += '<div class="floor-stat"><span class="floor-stat-label">井道宽最大:</span><span class="floor-stat-val max" id="statWidthMax">--</span></div>';
  html += '<div class="floor-stat"><span class="floor-stat-label">井道深最小:</span><span class="floor-stat-val min" id="statDepthMin">--</span></div>';
  html += '<div class="floor-stat"><span class="floor-stat-label">井道深最大:</span><span class="floor-stat-val max" id="statDepthMax">--</span></div>';
  html += '<div class="floor-stat" style="margin-left:auto;"><span class="floor-stat-label">共</span><span class="floor-stat-val" id="floorCountBadge">0</span><span class="floor-stat-label">层</span></div>';
  html += '</div>';
  
  // 楼层卡片列表
  html += '<div class="floor-cards" id="floorCards">';
  
  if (elev.floorData && elev.floorData.length) {
    var sorted = elev.floorData.slice().sort(function(a, b) {
      return parseFloat(a.floorNo) - parseFloat(b.floorNo);
    });
    for (var i = 0; i < sorted.length; i++) {
      html += renderFloorCard(sorted[i], i);
    }
  } else {
    html += '<div style="text-align:center;padding:40px 20px;color:#a0aec0;font-size:13px;">暂无楼层数据<br>点击上方"添加一层"或"批量生成"</div>';
  }
  
  html += '</div>';
  
  return html;
}

function renderFloorCard(floor, idx) {
  var html = '<div class="floor-card" data-idx="' + idx + '">';
  // 头部：楼层号 + 删除按钮
  html += '<div class="floor-card-header">';
  html += '<span class="floor-no-badge">';
  html += '<input type="text" value="' + escapeHtml(floor.floorNo || '') + '" ';
  html += 'onblur="updateFloorField(\\'' + idx + '\\',\\'floorNo\\',this.value)" ';
  html += 'style="background:transparent;border:none;color:#fff;font-size:14px;font-weight:700;width:50px;text-align:center;padding:0;outline:none;" placeholder="层号">';
  html += '</span>';
  html += '<button class="floor-del-btn" onclick="deleteFloorRow(\\'' + idx + '\\')" title="删除该层">×</button>';
  html += '</div>';
  
  // 第一行：层高 + 开门位置
  html += '<div class="floor-row">';
  html += '<div class="floor-field w30"><label>层高(mm)</label>';
  html += '<input type="number" value="' + (floor.floorHeight || '') + '" onblur="updateFloorField(\\'' + idx + '\\',\\'floorHeight\\',this.value)">';
  html += '</div>';
  html += '<div class="floor-field"><label>开门位置</label>';
  html += '<div class="floor-door-pos">';
  html += '<button type="button" class="' + (floor.doorPosition === '前门' ? 'active' : '') + '" onclick="setDoorPosition(\\'' + idx + '\\',\\'前门\\',this)">前门</button>';
  html += '<button type="button" class="' + (floor.doorPosition === '后门' ? 'active' : '') + '" onclick="setDoorPosition(\\'' + idx + '\\',\\'后门\\',this)">后门</button>';
  html += '<button type="button" class="' + (floor.doorPosition === '贯通' ? 'active' : '') + '" onclick="setDoorPosition(\\'' + idx + '\\',\\'贯通\\',this)">贯通</button>';
  html += '</div></div>';
  html += '</div>';
  
  // 第二行：井道宽 × 井道深
  html += '<div class="floor-row">';
  html += '<div class="floor-field"><label>井道宽(mm)</label>';
  html += '<input type="number" value="' + (floor.shaftWidth || '') + '" onblur="updateFloorField(\\'' + idx + '\\',\\'shaftWidth\\',this.value)">';
  html += '</div>';
  html += '<div class="floor-field"><label>井道深(mm)</label>';
  html += '<input type="number" value="' + (floor.shaftDepth || '') + '" onblur="updateFloorField(\\'' + idx + '\\',\\'shaftDepth\\',this.value)">';
  html += '</div>';
  html += '</div>';
  
  // 第三行：门洞宽 × 门洞高
  html += '<div class="floor-row">';
  html += '<div class="floor-field"><label>门洞宽(mm)</label>';
  html += '<input type="number" value="' + (floor.doorWidth || '') + '" onblur="updateFloorField(\\'' + idx + '\\',\\'doorWidth\\',this.value)">';
  html += '</div>';
  html += '<div class="floor-field"><label>门洞高(mm)</label>';
  html += '<input type="number" value="' + (floor.doorHeight || '') + '" onblur="updateFloorField(\\'' + idx + '\\',\\'doorHeight\\',this.value)">';
  html += '</div>';
  html += '</div>';
  
  // 第四行：门垛左/右 + 过梁高/宽
  html += '<div class="floor-row">';
  html += '<div class="floor-field w25"><label>门垛左</label>';
  html += '<input type="number" value="' + (floor.pierLeft || '') + '" onblur="updateFloorField(\\'' + idx + '\\',\\'pierLeft\\',this.value)">';
  html += '</div>';
  html += '<div class="floor-field w25"><label>门垛右</label>';
  html += '<input type="number" value="' + (floor.pierRight || '') + '" onblur="updateFloorField(\\'' + idx + '\\',\\'pierRight\\',this.value)">';
  html += '</div>';
  html += '<div class="floor-field w25"><label>过梁高</label>';
  html += '<input type="number" value="' + (floor.lintelHeight || '') + '" onblur="updateFloorField(\\'' + idx + '\\',\\'lintelHeight\\',this.value)">';
  html += '</div>';
  html += '<div class="floor-field w25"><label>过梁宽</label>';
  html += '<input type="number" value="' + (floor.lintelWidth || '') + '" onblur="updateFloorField(\\'' + idx + '\\',\\'lintelWidth\\',this.value)">';
  html += '</div>';
  html += '</div>';
  
  // 第五行：备注
  html += '<div class="floor-row">';
  html += '<div class="floor-field floor-remark-field"><label>备注</label>';
  html += '<input type="text" value="' + escapeHtml(floor.remark || '') + '" onblur="updateFloorField(\\'' + idx + '\\',\\'remark\\',this.value)" placeholder="该层特殊情况说明...">';
  html += '</div></div>';
  
  html += '</div>';
  return html;
}

function deleteLastFloor() {
  var elev = getCurrentElevator();
  if (!elev || !elev.floorData || !elev.floorData.length) return;
  var sorted = getSortedFloorData();
  var lastFloor = sorted[sorted.length - 1];
  if (!confirm('确定删除最顶层 ' + lastFloor.floorNo + ' 层吗？')) return;
  var origIdx = elev.floorData.indexOf(lastFloor);
  if (origIdx >= 0) elev.floorData.splice(origIdx, 1);
  saveCurrentProject();
  renderElevatorContent();
}

// ===== Tab3: 井道结构 =====
function renderShaftStructureTab(elev) {
  var html = '';
  
  // 四面墙结构
  html += '<div class="card">';
  html += '<div class="section-header"><span>🧱 四面墙结构</span></div>';
  
  // 后墙
  html += '<div class="wall-group">';
  html += '<div class="wall-group-title">▣ 后墙</div>';
  html += '<div class="wall-form-grid">';
  html += formField('结构类型', 'elev_backWallType', elev.backWallType || '砖混墙', 'select', 'updateElevField', false,
    [['砖混墙','砖混墙'],['混凝土墙','混凝土墙'],['钢架','钢架']]);
  html += formField('厚度(mm)', 'elev_backWallThick', elev.backWallThick || '', 'number', 'updateElevField');
  html += formField('外墙', 'elev_backWallOuter', elev.backWallOuter || '否', 'select', 'updateElevField', false,
    [['是','是'],['否','否']]);
  html += formField('圈梁间距(mm)', 'elev_backRingBeam', elev.backRingBeam || '', 'number', 'updateElevField');
  html += formField('支架间距(mm)', 'elev_backBracket', elev.backBracket || '', 'number', 'updateElevField');
  html += '</div></div>';
  
  // 左墙
  html += '<div class="wall-group">';
  html += '<div class="wall-group-title">▣ 左墙</div>';
  html += '<div class="wall-form-grid">';
  html += formField('结构类型', 'elev_leftWallType', elev.leftWallType || '砖混墙', 'select', 'updateElevField', false,
    [['砖混墙','砖混墙'],['混凝土墙','混凝土墙'],['钢架','钢架']]);
  html += formField('厚度(mm)', 'elev_leftWallThick', elev.leftWallThick || '', 'number', 'updateElevField');
  html += formField('外墙', 'elev_leftWallOuter', elev.leftWallOuter || '否', 'select', 'updateElevField', false,
    [['是','是'],['否','否']]);
  html += formField('圈梁间距(mm)', 'elev_leftRingBeam', elev.leftRingBeam || '', 'number', 'updateElevField');
  html += formField('支架间距(mm)', 'elev_leftBracket', elev.leftBracket || '', 'number', 'updateElevField');
  html += '</div></div>';
  
  // 右墙
  html += '<div class="wall-group">';
  html += '<div class="wall-group-title">▣ 右墙</div>';
  html += '<div class="wall-form-grid">';
  html += formField('结构类型', 'elev_rightWallType', elev.rightWallType || '砖混墙', 'select', 'updateElevField', false,
    [['砖混墙','砖混墙'],['混凝土墙','混凝土墙'],['钢架','钢架']]);
  html += formField('厚度(mm)', 'elev_rightWallThick', elev.rightWallThick || '', 'number', 'updateElevField');
  html += formField('外墙', 'elev_rightWallOuter', elev.rightWallOuter || '否', 'select', 'updateElevField', false,
    [['是','是'],['否','否']]);
  html += formField('圈梁间距(mm)', 'elev_rightRingBeam', elev.rightRingBeam || '', 'number', 'updateElevField');
  html += formField('支架间距(mm)', 'elev_rightBracket', elev.rightBracket || '', 'number', 'updateElevField');
  html += '</div></div>';
  
  html += '</div>';
  
  // 门过梁与门垛
  html += '<div class="card">';
  html += '<div class="section-header"><span>🚪 门过梁与门垛</span></div>';
  html += '<div class="form-grid">';
  html += formField('≥300mm门过梁', 'elev_hasHeaderBeam', elev.hasHeaderBeam || '是', 'select', 'updateElevField', false,
    [['是','有'],['否','无']]);
  html += formField('门垛结构', 'elev_pierStructure', elev.pierStructure || '混凝土', 'select', 'updateElevField', false,
    [['混凝土','混凝土'],['砖墙','砖墙'],['钢架','钢架']]);
  html += formField('门垛状态', 'elev_pierStatus', elev.pierStatus || '未建', 'select', 'updateElevField', false,
    [['未建','未建'],['在建','在建'],['已建','已建']]);
  html += formField('左门垛宽(mm)', 'elev_pierLeftWidth', elev.pierLeftWidth || '', 'number', 'updateElevField');
  html += formField('右门垛宽(mm)', 'elev_pierRightWidth', elev.pierRightWidth || '', 'number', 'updateElevField');
  html += '</div></div>';
  
  // 其他井道参数
  html += '<div class="card">';
  html += '<div class="section-header"><span>🔧 其他井道参数</span></div>';
  html += '<div class="form-grid">';
  html += formField('外呼盒形式', 'elev_callBoxType', elev.callBoxType || '有底盒', 'select', 'updateElevField', false,
    [['有底盒','有底盒'],['无底盒','无底盒']]);
  html += formField('井道预留牛腿', 'elev_hasCorbel', elev.hasCorbel || '无', 'select', 'updateElevField', false,
    [['有','有'],['无','无']]);
  html += formField('贯通', 'elev_isThrough', elev.isThrough || '否', 'select', 'updateElevField', false,
    [['是','是'],['否','否']]);
  html += formField('轿厢观光类型', 'elev_sightseeingType', elev.sightseeingType || '方形', 'select', 'updateElevField', false,
    [['方形','方形'],['半圆形','半圆形']]);
  html += formField('观光面数', 'elev_sightseeingSides', elev.sightseeingSides || '', 'text', 'updateElevField');
  html += formField('动力电源', 'elev_powerSupply', elev.powerSupply || '三相380V', 'select', 'updateElevField', false,
    [['单相220V','单相220V'],['三相380V','三相380V']]);
  html += '</div></div>';
  
  return html;
}

// ===== Tab4: 机房底坑 =====
function renderMachinePitTab(elev) {
  var html = '';
  
  html += '<div class="card">';
  html += '<div class="section-header"><span>🏢 机房参数</span></div>';
  html += '<div class="form-grid">';
  html += formField('机房形式', 'elev_roomForm', elev.roomForm || '大机房', 'select', 'updateElevField', false,
    [['大机房','大机房'],['无机房','无机房'],['小机房','小机房']]);
  html += formField('机房宽(mm)', 'elev_roomWidth', elev.roomWidth || '', 'number', 'updateElevField');
  html += formField('机房深(mm)', 'elev_roomDepth', elev.roomDepth || '', 'number', 'updateElevField');
  html += formField('机房高(mm)', 'elev_roomHeight', elev.roomHeight || '', 'number', 'updateElevField');
  html += formField('机房局部抬高', 'elev_roomLocalRaise', elev.roomLocalRaise || '无', 'select', 'updateElevField', false,
    [['有','有'],['无','无']]);
  html += formField('抬高(mm)', 'elev_roomRaiseMm', elev.roomRaiseMm || '', 'number', 'updateElevField');
  html += '</div></div>';
  
  html += '<div class="card">';
  html += '<div class="section-header"><span>⬇️ 底坑与高度</span></div>';
  html += '<div class="form-grid">';
  html += formField('底坑前(mm)', 'elev_pitFront', elev.pitFront || '', 'number', 'updateElevField');
  html += formField('底坑后(mm)', 'elev_pitBack', elev.pitBack || '', 'number', 'updateElevField');
  html += formField('底坑深(mm)', 'elev_pitDepth', elev.pitDepth || '', 'number', 'updateElevField');
  html += formField('顶层高(mm)', 'elev_topHeight', elev.topHeight || '', 'number', 'updateElevField');
  html += formField('提升高度(mm)', 'elev_liftHeight', elev.liftHeight || '', 'number', 'updateElevField');
  html += formField('井道总高(mm)', 'elev_wellTotalHeight', elev.wellTotalHeight || '', 'number', 'updateElevField');
  html += '</div></div>';
  
  // 特殊说明
  html += '<div class="card">';
  html += '<div class="section-header"><span>📝 特殊说明</span></div>';
  html += '<textarea id="elev_specialNotes" style="width:100%;min-height:100px;border:1.5px solid #e2e8f0;border-radius:8px;padding:10px;font-size:13px;font-family:inherit;resize:vertical;" onblur="updateSpecialNotes(this.value)" placeholder="填写特殊情况说明...">' + escapeHtml(elev.specialNotes || '') + '</textarea>';
  html += '</div>';
  
  return html;
}

// ===== Tab5: 示意图 =====
function renderSketchesTab(elev) {
  var html = '<div class="card">';
  html += '<div class="section-header">';
  html += '<span>🖼️ 示意图</span>';
  html += '<span class="section-count">' + (elev.sketches ? elev.sketches.length : 0) + ' 张</span>';
  html += '</div>';
  
  html += '<div class="sketch-area">';
  
  if (elev.sketches && elev.sketches.length) {
    for (var i = 0; i < elev.sketches.length; i++) {
      var sk = elev.sketches[i];
      html += '<div class="sketch-thumb">';
      html += '<img src="' + sk.data + '" alt="' + escapeHtml(sk.name || '示意图') + '" onclick="viewSketch(' + i + ')">';
      html += '<button class="sketch-del" onclick="deleteSketch(' + i + ')">×</button>';
      html += '</div>';
    }
  }
  
  html += '<div class="sketch-add" onclick="addSketch(true)" title="拍照">';
  html += '<div class="sketch-add-icon">📷</div>';
  html += '<div class="sketch-add-text">拍照</div>';
  html += '</div>';
  html += '<div class="sketch-add" onclick="addSketch(false)" title="从相册选择">';
  html += '<div class="sketch-add-icon">🖼️</div>';
  html += '<div class="sketch-add-text">上传</div>';
  html += '</div>';
  
  html += '</div>';
  html += '<div class="form-hint" style="margin-top:8px;">图片将自动压缩（最长边1280px，质量80%），点击图片可查看大图</div>';
  html += '</div>';
  return html;
}

// ===== Tab6: 签字 =====
function renderSignatureTab(elev) {
  var sigs = elev.signatures || {};
  var html = '<div class="card">';
  html += '<div class="section-header"><span>✍️ 签字确认</span></div>';
  
  var sigItems = [
    {key: 'surveyor', label: '测量及申请人'},
    {key: 'reviewer', label: '审核'},
    {key: 'draftsman', label: '绘图接收人'}
  ];
  
  for (var i = 0; i < sigItems.length; i++) {
    var item = sigItems[i];
    var dateField = item.key + 'Date';
    html += '<div style="margin-bottom:16px;">';
    html += '<div style="font-size:13px;font-weight:600;color:#4a5568;margin-bottom:6px;">' + item.label + '</div>';
    html += '<div class="sig-area" style="height:90px;" onclick="openSigModal(\\'' + item.key + '\\')">';
    if (sigs[item.key]) {
      html += '<img src="' + sigs[item.key] + '" alt="签名">';
    } else {
      html += '<span>点击签名</span>';
    }
    html += '</div>';
    html += '<div class="sig-date-row">';
    html += '<label>日期：</label>';
    html += '<input type="date" id="sig_' + item.key + 'Date" value="' + (sigs[dateField] || '') + '" onchange="updateSigDate(\\'' + item.key + 'Date\\',this.value)">';
    html += '</div>';
    html += '<button class="sig-clear-btn" onclick="clearSig(\\'' + item.key + '\\')">清除签名</button>';
    html += '</div>';
  }
  
  html += '</div>';
  return html;
}

function updateSigDate(field, value) {
  var elev = getCurrentElevator();
  if (!elev) return;
  if (!elev.signatures) elev.signatures = {};
  elev.signatures[field] = value;
  saveCurrentProject();
}

'''

# 插入到 // ===== 分层测量表 ===== 之前（JS部分）
js_insert_point = '// ===== 分层测量表 ====='
if js_insert_point in content:
    content = content.replace(js_insert_point, new_render_functions + '\n' + js_insert_point)
    print("✓ 已添加所有新的tab渲染函数")
else:
    print("✗ 未找到JS函数插入点")

# ========== 7. 修改 renderEmptyOrContent 函数，隐藏/显示tab栏 ==========
# 当没有选中电梯时，隐藏tab栏；选中时显示

old_empty_content = '''function renderEmptyOrContent() {
  var empty = document.getElementById('emptyState');
  var content = document.getElementById('elevatorContent');
  var elev = getCurrentElevator();
  
  if (elev) {
    empty.style.display = 'none';
    content.style.display = 'block';
    renderElevatorContent();
  } else {
    content.style.display = 'none';
    empty.style.display = 'flex';'''

new_empty_content = '''function renderEmptyOrContent() {
  var empty = document.getElementById('emptyState');
  var content = document.getElementById('elevatorContent');
  var tabsEl = document.getElementById('zoneTabs');
  var elev = getCurrentElevator();
  
  if (elev) {
    empty.style.display = 'none';
    content.style.display = 'block';
    if (tabsEl) tabsEl.style.display = 'flex';
    renderElevatorContent();
  } else {
    content.style.display = 'none';
    empty.style.display = 'flex';
    if (tabsEl) tabsEl.style.display = 'none';'''

if old_empty_content in content:
    content = content.replace(old_empty_content, new_empty_content)
    print("✓ 已修改renderEmptyOrContent函数，添加tab栏显示控制")
else:
    print("✗ 未找到renderEmptyOrContent替换点")

# ========== 8. 响应式样式调整 ==========
# 在移动端 media query 中添加 zone-tabs 相关

mobile_css_insert = '''  .floor-stats{flex-wrap:wrap;gap:10px;}
}'''

new_mobile_css = '''  .floor-stats{flex-wrap:wrap;gap:10px;}
  .zone-tabs{padding:0 4px;}
  .zone-tab{padding:10px 10px;font-size:12px;}
  .wall-form-grid{grid-template-columns:1fr;}
  .floor-row{flex-wrap:wrap;}
  .floor-field.w25{flex:0 0 calc(50% - 4px);}
  .floor-field.w30{flex:0 0 40%;}
  .floor-field.w40{flex:0 0 100%;}
}'''

if mobile_css_insert in content:
    # 找到最后一个@media (max-width: 768px)块的末尾
    # 更精确的方式：找到 .floor-stats 那行
    content = content.replace(mobile_css_insert, new_mobile_css)
    print("✓ 已添加移动端响应式样式")
else:
    print("✗ 未找到移动端CSS插入点")

# ========== 保存文件 ==========
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n新文件大小: {len(content)} 字符")
print(f"增加了: {len(content) - len(open('weite-pro-temp/civil-survey.html.bak_before_tabs', 'r', encoding='utf-8').read())} 字符")
print("\n重构完成！")
