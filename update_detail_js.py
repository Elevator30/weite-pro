#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
weite-service-beta-detail.html JS部分修改脚本
"""

import re

FILE_PATH = '/app/data/所有对话/主对话/weite-pro-temp/weite-service-beta-detail.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

print(f"当前文件长度: {len(html)}")

# ============================================================
# 第4项：服务类别 - 复选框直接渲染到手风琴body中
# ============================================================

# 将svcCats渲染目标从弹窗的svcCats改为手风琴内的svcCatsBody
old_svc_target = "var svcBox=document.getElementById('svcCats');"
new_svc_target = "var svcBox=document.getElementById('svcCatsBody');"
if old_svc_target in html:
    html = html.replace(old_svc_target, new_svc_target)
    print("✓ 服务类别渲染目标改为svcCatsBody（手风琴内）")
else:
    print("⚠ 未找到svcBox赋值，尝试其他方式")
    # 可能是因为换行等原因，尝试正则匹配
    pattern = r"var svcBox\s*=\s*document\.getElementById\('svcCats'\)"
    if re.search(pattern, html):
        html = re.sub(pattern, "var svcBox=document.getElementById('svcCatsBody')", html)
        print("✓ 服务类别渲染目标改为svcCatsBody（正则匹配）")

# ============================================================
# 第4项：服务节点 - 复选框直接渲染到手风琴body中
# ============================================================

# 服务节点的mkCg目标从cgFlow（弹窗）改为cgFlowBody（手风琴内）
old_flow_target = "mkCg('cgFlow','flowTo',['工程部','销售部','技术部','安装队','代理商/用户','其他']);"
new_flow_target = "mkCg('cgFlowBody','flowTo',['工程部','销售部','技术部','安装队','代理商/用户','其他']);"
if old_flow_target in html:
    html = html.replace(old_flow_target, new_flow_target)
    print("✓ 服务节点渲染目标改为cgFlowBody（手风琴内）")
else:
    print("⚠ 未找到cgFlow的mkCg调用")

# ============================================================
# 第4项：服务说明 - 复选框直接渲染到签字确认tab
# ============================================================

# impact的mkCg调用目标还是cgImpact，但现在签字确认tab里也有cgImpact
# 弹窗里还有一个cgImpact，导致有两个相同ID
# 我们需要把弹窗里的cgImpact去掉或改名，确保只有一个
# 实际上，签字确认tab里已经有<div class="cg" id="cgImpact"></div>了
# 所以mkCg('cgImpact',...)会渲染到那里，这是对的
# 但弹窗里也有一个cgImpact，需要移除或改名

# 找到impactMo弹窗里的cgImpact并改名为cgImpactModal（避免ID冲突）
old_impact_mo_cg = '<div class="cg" id="cgImpact"></div>'
# 先看看弹窗里的cgImpact在什么位置
# 弹窗里的impact内容：
# <div class="mb" style="padding:14px;">
#   <div class="fr"><label>需尽快处理项</label>...</div>
#   <div style="font-size:12px;color:#666;margin-bottom:8px;">否则将影响：</div>
#   <div class="cg" id="cgImpact"></div>
#   <div class="fr" id="stopRow" style="display:none;">...</div>
# </div>
# 
# 现在签字确认tab里已经有完整的表单了，弹窗可以保留但不需要了
# 为了兼容性，我们把弹窗里的cgImpact改个名，避免冲突
# 但实际上由于mkCg是按ID找元素的，它会找到第一个（签字确认tab里的）
# 所以弹窗里的那个cgImpact不会被填充，这没问题
# 但为了避免混淆，还是改个名吧

# 先确认一下impact弹窗的HTML结构
impact_mo_pattern = r'<!-- 影响说明弹窗 -->.*?<div class="mo" id="impactMo">.*?</div></div>'
impact_match = re.search(impact_mo_pattern, html, re.DOTALL)
if impact_match:
    print(f"✓ 找到impact弹窗，长度{len(impact_match.group())}")

# 弹窗里的cgImpact改名为cgImpactModal，避免ID冲突
# 但要注意只改弹窗里的，不改签字确认tab里的
# 弹窗里的cgImpact在impactMo内部
# 用更精确的方式：找到impactMo内的cgImpact

# 先找到impactMo的起止位置
impact_mo_start = html.find('<div class="mo" id="impactMo">')
if impact_mo_start > 0:
    # 找到impactMo的结束位置（找对应的</div></div>）
    # 简单方式：找下一个"<!-- 签字确认弹窗 -->"之前
    sign_mo_start = html.find('<!-- 签字确认弹窗 -->', impact_mo_start)
    if sign_mo_start > 0:
        impact_section = html[impact_mo_start:sign_mo_start]
        # 将里面的id="cgImpact"改为id="cgImpactModal"
        new_impact_section = impact_section.replace('id="cgImpact"', 'id="cgImpactModal"')
        # 同时把f13也改名？不，f13是字段ID，约束要求不变
        # stopRow也需要改，避免冲突
        new_impact_section = new_impact_section.replace('id="stopRow"', 'id="stopRowModal"')
        new_impact_section = new_impact_section.replace("'stopRow'", "'stopRowModal'")
        html = html[:impact_mo_start] + new_impact_section + html[sign_mo_start:]
        print("✓ impact弹窗内元素改名，避免ID冲突")

# 同样，impact相关的change事件监听器也需要调整
# 原来的：document.addEventListener('change',function(e){if(e.target.name==='impact'&&e.target.value==='用户正常用梯')document.getElementById('stopRow').style.display=e.target.checked?'flex':'none';});
# 这个监听器是全局的，监听name=impact的checkbox变化
# 现在checkbox在签字确认tab里，toggle的应该是签字确认tab里的stopRow
# 但我们把弹窗里的改名为stopRowModal了，所以这里应该没问题
# 等等，不对。原来的stopRow在弹窗里，现在签字确认tab里也有一个stopRow
# 这就有两个stopRow了，getElementById会找到第一个
# 第一个应该是签字确认tab里的（因为它在HTML前面），所以没问题
# 让我确认一下：签字确认tab在zonePanel_2里，它在impactMo弹窗之前还是之后？
# 看HTML结构顺序：
# zonePanel_0 (基本信息) -> zonePanel_1 (服务详情) -> zonePanel_2 (签字确认) -> 弹窗们
# 所以zonePanel_2里的stopRow会先被找到，没问题

# ============================================================
# 第5项：服务记录 - 手风琴内直接展示
# ============================================================

# 我需要重新改造服务记录手风琴的body
# 方案：把recBox和addRecBtn从弹窗移到手风琴body里，加上卡片样式
# 保留原有的addRec()和数据结构

# 首先，找到服务记录手风琴的body部分（我之前已经改过一次了，现在重新改）
old_record_body = '''      <div class="accordion-body">
        <div id="svcRecList" style="margin-bottom:10px;"></div>
        <div id="svcRecForm" style="display:none;margin-bottom:10px;padding:12px;background:#f8f9fa;border-radius:10px;border:1px dashed #cbd5e0;">
          <div style="font-size:13px;font-weight:600;color:#2d3748;margin-bottom:8px;">新增记录</div>
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <span style="font-size:12px;color:#1a5276;font-weight:bold;">新记录</span>
            <select id="svcRecType" style="width:auto;padding:4px 8px;font-size:12px;border-radius:6px;border:1px solid #e2e8f0;">
              <option value="完成项">✅ 完成项</option>
              <option value="要求项">📌 要求项</option>
            </select>
          </div>
          <input type="text" id="svcRecContent" placeholder="沟通内容/服务记录摘要" style="width:100%;border:1px solid #e2e8f0;border-radius:6px;padding:8px 10px;font-size:13px;margin-bottom:6px;">
          <div style="display:flex;gap:6px;margin-bottom:8px;">
            <select id="svcRecCompleter" style="flex:1;padding:6px 4px;font-size:12px;border:1px solid #e2e8f0;border-radius:6px;background:#fafafa;">
              <option value="">选择完成方</option>
            </select>
            <input type="date" id="svcRecDate" style="flex:1;padding:6px 4px;font-size:12px;border:1px solid #e2e8f0;border-radius:6px;">
          </div>
          <div style="display:flex;gap:8px;">
            <button onclick="cancelSvcRec()" style="flex:1;padding:8px;border:1px solid #e2e8f0;border-radius:8px;background:#fff;color:#718096;font-size:12px;font-weight:600;cursor:pointer;">取消</button>
            <button onclick="saveSvcRec()" style="flex:1;padding:8px;border:none;border-radius:8px;background:linear-gradient(135deg,#2ecc71,#27ae60);color:#fff;font-size:12px;font-weight:600;cursor:pointer;">保存</button>
          </div>
        </div>
        <button onclick="addSvcRec()" style="width:100%;padding:10px;border:1.5px dashed #68d391;border-radius:10px;background:#f0fff4;color:#27ae60;font-size:13px;font-weight:600;cursor:pointer;">+ 新增记录</button>
      </div>'''

# 新方案：直接把recBox和addRecBtn放进去，用CSS美化
new_record_body = '''      <div class="accordion-body">
        <div id="recBox"></div>
        <div class="ar" id="addRecBtn">+ 添加一条记录</div>
      </div>'''

if old_record_body in html:
    html = html.replace(old_record_body, new_record_body)
    print("✓ 服务记录手风琴body改为recBox+addRecBtn")
else:
    print("⚠ 未找到旧的服务记录body，尝试查找")
    # 查找当前的服务记录accordion-body
    rec_acc_pattern = r'data-acc-svc="svcRecord".*?<div class="accordion-body">.*?</div>\s*</div>\s*</div>'
    match = re.search(rec_acc_pattern, html, re.DOTALL)
    if match:
        print(f"  找到服务记录手风琴，长度{len(match.group())}")

# 给.ri元素添加卡片样式（参考土建勘测楼层卡片风格）
# 找到ri样式定义的位置，添加新样式
old_ri_style = ".ri{background:#f8f9fa;border-radius:8px;padding:10px;margin-bottom:8px;border-left:3px solid #667eea;}"
new_ri_style = """.ri{background:#fff;border:1.5px solid #e2e8f0;border-radius:10px;padding:12px;margin-bottom:10px;
  box-shadow:0 1px 3px rgba(0,0,0,.03);position:relative;border-left:3px solid #667eea;}
.ri .ri-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;
  padding-bottom:6px;border-bottom:1px dashed #edf2f7;}
.ri .ri-num{font-size:12px;font-weight:700;color:#667eea;}
.ri .ri-type{font-size:11px;font-weight:600;padding:2px 8px;border-radius:10px;}
.ri .ri-type.completed{background:#e6fffa;color:#27ae60;}
.ri .ri-type.required{background:#fef3c7;color:#d69e2e;}
.ri .ri-del-btn{background:none;border:none;color:#e53e3e;cursor:pointer;font-size:14px;padding:2px 6px;line-height:1;}
.ri input[type="text"]{width:100%;border:1.5px solid #e2e8f0;border-radius:6px;padding:8px 10px;font-size:13px;background:#fafafa;margin-bottom:6px;}
.ri input[type="text"]:focus{border-color:#667eea;background:#fff;outline:none;}
.ri .ri-row{display:flex;gap:6px;margin-bottom:4px;}
.ri .ri-row select{flex:1;padding:6px 4px;font-size:12px;border:1.5px solid #e2e8f0;border-radius:6px;background:#fafafa;}
.ri .ri-row select:focus{border-color:#667eea;outline:none;}"""

if old_ri_style in html:
    html = html.replace(old_ri_style, new_ri_style)
    print("✓ .ri样式升级为卡片式")
else:
    print("⚠ 未找到.ri样式定义")
    # 尝试正则查找
    ri_pattern = r"\.ri\{background:#f8f9fa;border-radius:8px;padding:10px;margin-bottom:8px;border-left:3px solid #667eea;\}"
    if re.search(ri_pattern, html):
        html = re.sub(ri_pattern, new_ri_style, html)
        print("✓ .ri样式升级为卡片式（正则）")

# ============================================================
# 修改addRec函数，添加卡片样式结构
# ============================================================

# 原来的addRec函数创建的.ri结构需要更新为带卡片样式的结构
# 原结构：
# <div class="ri">
#   <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
#     <span style="font-size:12px;color:#1a5276;font-weight:bold;">第 N 条</span>
#     <select ...>...</select>
#   </div>
#   <input type="text" ...>
#   <div style="display:flex;gap:6px;">
#     <select class="compSel" ...>...</select>
#     <input type="date" ...>
#   </div>
# </div>

# 新结构（带卡片样式）：
# <div class="ri">
#   <div class="ri-header">
#     <span class="ri-num">第 N 条</span>
#     <button class="ri-del-btn" onclick="this.closest('.ri').remove();updateBtnStatus();">✕</button>
#   </div>
#   <select style="width:100%;margin-bottom:6px;padding:4px 8px;font-size:12px;border-radius:6px;border:1.5px solid #e2e8f0;background:#fafafa;">
#     <option value="完成项">✅ 完成项</option>
#     <option value="要求项">📌 要求项</option>
#   </select>
#   <input type="text" ...>
#   <div class="ri-row">
#     <select class="compSel" ...>...</select>
#     <input type="date" ...>
#   </div>
# </div>

# 找到addRec函数并修改
old_addrec_func = """function addRec(){recN++;var box=document.getElementById('recBox');var d=document.createElement('div');d.className='ri';var sp=gv('f10'),sc=gv('f8');var opts='<option value="">选择完成方</option>';if(sp)opts+='<option value="'+sp+'">'+sp+'</option>';if(sc&&sc!==sp)opts+='<option value="'+sc+'">'+sc+'</option>';opts+='<option value="其他">其他</option>';d.innerHTML='<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;"><span style="font-size:12px;color:#1a5276;font-weight:bold;">第 '+recN+' 条</span><select style="width:auto;padding:4px 8px;font-size:12px;"><option value="完成项">✅ 完成项</option><option value="要求项">📌 要求项</option></select></div><input type="text" placeholder="沟通内容/服务记录摘要" oninput="updateBtnStatus()"><div style="display:flex;gap:6px;"><select class="compSel" style="flex:0 0 80px;padding:8px 4px;font-size:13px;border:1px solid #e0e0e0;border-radius:4px;background:#fafafa;max-width:80px;">'+opts+'</select><input type="date" style="flex:0 0 130px;padding:8px 4px;font-size:13px;border:1px solid #e0e0e0;border-radius:4px;max-width:130px;"></div>';box.appendChild(d);var newInput=d.querySelector('input[type="text"]');if(newInput)newInput.focus();}"""

new_addrec_func = """function addRec(){recN++;var box=document.getElementById('recBox');var d=document.createElement('div');d.className='ri';var sp=gv('f10'),sc=gv('f8');var opts='<option value="">选择完成方</option>';if(sp)opts+='<option value="'+sp+'">'+sp+'</option>';if(sc&&sc!==sp)opts+='<option value="'+sc+'">'+sc+'</option>';opts+='<option value="其他">其他</option>';d.innerHTML='<div class="ri-header"><span class="ri-num">第 '+recN+' 条</span><button class="ri-del-btn" onclick="this.closest(\\'.ri\\').remove();updateRecCount();updateBtnStatus();">✕</button></div><select style="width:100%;margin-bottom:6px;padding:6px 8px;font-size:12px;border-radius:6px;border:1.5px solid #e2e8f0;background:#fafafa;" onchange="updateBtnStatus()"><option value="完成项">✅ 完成项</option><option value="要求项">📌 要求项</option></select><input type="text" placeholder="沟通内容/服务记录摘要" oninput="updateBtnStatus()"><div class="ri-row"><select class="compSel" style="flex:1;padding:6px 4px;font-size:12px;border:1.5px solid #e2e8f0;border-radius:6px;background:#fafafa;" onchange="updateBtnStatus()">'+opts+'</select><input type="date" style="flex:1;padding:6px 4px;font-size:12px;border:1.5px solid #e2e8f0;border-radius:6px;" onchange="updateBtnStatus()"></div>';box.appendChild(d);var newInput=d.querySelector('input[type="text"]');if(newInput)newInput.focus();updateRecCount();}"""

if old_addrec_func in html:
    html = html.replace(old_addrec_func, new_addrec_func)
    print("✓ addRec函数更新为卡片式结构")
else:
    print("⚠ 未找到addRec函数，尝试正则查找")
    # 尝试更宽松的匹配
    addrec_pattern = r"function addRec\(\)\{recN\+\+;var box=document\.getElementById\('recBox'\);.*?box\.appendChild\(d\);var newInput=d\.querySelector\('input\[type=\"text\"\]'\);if\(newInput\)newInput\.focus\(\);\}"
    match = re.search(addrec_pattern, html, re.DOTALL)
    if match:
        print(f"  找到addRec函数，长度{len(match.group())}")
        html = html.replace(match.group(), new_addrec_func)
        print("✓ addRec函数更新（正则）")

# 添加updateRecCount函数用于更新记录数显示
update_rec_count_func = """
function updateRecCount(){
  var s=document.getElementById('st_record');
  if(s){
    var recs=document.querySelectorAll('#recBox .ri');
    var hasContent=0;
    recs.forEach(function(r){
      var inp=r.querySelector('input[type="text"]');
      if(inp&&inp.value.trim())hasContent++;
    });
    s.textContent=hasContent+'条';
  }
}
"""

# 在addRec函数后面插入updateRecCount
# 找到addRec();document.getElementById('addRecBtn')的位置
addrec_init = "addRec();document.getElementById('addRecBtn').addEventListener('click',function(){addRec();updateBtnStatus();});"
new_addrec_init = "addRec();document.getElementById('addRecBtn').addEventListener('click',function(){addRec();updateBtnStatus();});" + update_rec_count_func
if addrec_init in html:
    html = html.replace(addrec_init, new_addrec_init)
    print("✓ 添加updateRecCount函数")
else:
    print("⚠ 未找到addRec初始化代码")

# ============================================================
# updateCompSel函数需要更新（因为compSel的样式变了）
# ============================================================
# 这个函数只是更新options，不影响样式，所以不用改

# ============================================================
# 调整updateBtnStatus中服务记录相关的逻辑
# ============================================================

# 找到updateBtnStatus函数中更新st_record的部分
# 原来的代码：
# s=document.getElementById('st_record');if(s){var recs=document.querySelectorAll('#recBox .ri');var hasContent=0;recs.forEach(function(r){var inp=r.querySelector('input[type="text"]');if(inp&&inp.value.trim())hasContent++;});s.textContent=hasContent+'条';if(hasContent>0)filled++;}

# 这部分代码应该还能用，因为还是#recBox .ri结构
# 但我们新加了updateRecCount函数，可以复用
# 暂时不改，确保向后兼容

# ============================================================
# 移除服务记录弹窗（recordMo）的标题或整个弹窗？
# 不，弹窗可以保留，因为其他地方可能还用到
# 但手风琴里已经有完整的编辑功能了，弹窗就不再需要了
# 为了安全起见，保留弹窗但不使用它
# ============================================================

# ============================================================
# 修复updateSvcAccordionSummary函数
# 原来这个函数用于更新手风琴内的汇总显示
# 现在选项直接显示在手风琴里了，这个函数的部分功能不再需要
# 但状态指示器（st_service, st_flow, st_record）还需要更新
# ============================================================

# 这个函数目前的功能：
# 1. 更新svcCatsBody - 原来显示汇总文字，现在直接是复选框，不需要再更新HTML了
# 2. 更新cgFlowBody - 原来显示汇总文字，现在直接是复选框，不需要了
# 3. 更新recListSummary - 原来显示汇总文字，现在recBox直接在里面，不需要了

# 我们需要保留对状态指示器的更新
# 但updateBtnStatus已经在更新st_service, st_flow, st_record了
# 所以updateSvcAccordionSummary可以简化或删除
# 先保留函数但清空内容，避免报错

# 找到updateSvcAccordionSummary函数
old_update_summary = """function updateSvcAccordionSummary(){
  // 服务类别汇总
  var svcCatsBody = document.getElementById('svcCatsBody');
  if(svcCatsBody){
    var html = '';
    var catLabels = [
      {key: 'preSale', label: '售前/中工程支持'},
      {key: 'during', label: '施工前后工程支持'},
      {key: 'afterSale', label: '售后工程支持'},
      {key: 'visit', label: '客户回访'}
    ];
    catLabels.forEach(function(cat){
      var checked = [];
      document.querySelectorAll('input[name="' + cat.key + '"]:checked').forEach(function(cb){
        if(cb.value !== '其他') checked.push(cb.value);
      });
      var otherInput = document.getElementById(cat.key + 'Other');
      if(otherInput && otherInput.value && checked.indexOf('其他') < 0){
        var otherChecked = document.querySelector('input[name="' + cat.key + '"][value="其他"]:checked');
        if(otherChecked) checked.push(otherInput.value);
      }
      if(checked.length > 0){
        html += '<div style="margin-bottom:8px;">';
        html += '<div style="font-size:12px;font-weight:600;color:#667eea;margin-bottom:3px;">' + cat.label + '</div>';
        html += '<div style="font-size:13px;color:#4a5568;">' + checked.join('、') + '</div>';
        html += '</div>';
      }
    });
    if(!html){
      html = '<div style="text-align:center;color:#a0aec0;font-size:13px;padding:10px;">尚未选择服务类别</div>';
    }
    svcCatsBody.innerHTML = html;
  }
  
  // 服务节点汇总 - 直接复制cgFlow的内容
  var cgFlowBody = document.getElementById('cgFlowBody');
  var cgFlow = document.getElementById('cgFlow');
  if(cgFlowBody && cgFlow){
    var items = [];
    cgFlow.querySelectorAll('input:checked').forEach(function(cb){
      items.push(cb.value);
    });
    if(items.length > 0){
      cgFlowBody.innerHTML = '<div style="font-size:13px;color:#4a5568;">' + items.join('、') + '</div>';
    } else {
      cgFlowBody.innerHTML = '<div style="text-align:center;color:#a0aec0;font-size:13px;padding:10px;">尚未选择服务节点</div>';
    }
  }
  
  // 服务记录汇总
  var recListSummary = document.getElementById('recListSummary');
  if(recListSummary){
    var recs = document.querySelectorAll('#recBox .ri');
    var html = '';
    var count = 0;
    recs.forEach(function(r, i){
      var inp = r.querySelector('input[type="text"]');
      if(inp && inp.value.trim()){
        count++;
        var sel = r.querySelector('select:not(.compSel)');
        var type = sel ? sel.value : '';
        html += '<div style="background:#f8f9fa;border-radius:6px;padding:8px 10px;margin-bottom:6px;border-left:3px solid ' + (type === '完成项' ? '#27ae60' : '#667eea') + ';">';
        html += '<div style="font-size:12px;color:#718096;margin-bottom:2px;">第' + (i+1) + '条 · ' + (type || '未分类') + '</div>';
        html += '<div style="font-size:13px;color:#2d3748;">' + inp.value.trim() + '</div>';
        html += '</div>';
      }
    });
    if(count === 0){
      html = '<div style="text-align:center;color:#a0aec0;font-size:13px;padding:10px;">暂无记录</div>';
    }
    recListSummary.innerHTML = html;
  }
}"""

# 新的简化版本 - 只更新状态，不再更新汇总HTML
new_update_summary = """function updateSvcAccordionSummary(){
  // 选项直接展示在手风琴内，无需更新汇总显示
  // 确保状态指示器正确
  if(typeof updateBtnStatus === 'function') updateBtnStatus();
}"""

if old_update_summary in html:
    html = html.replace(old_update_summary, new_update_summary)
    print("✓ updateSvcAccordionSummary简化")
else:
    print("⚠ 未找到updateSvcAccordionSummary函数，尝试其他方式")
    # 可能格式有差异，用正则找
    func_pattern = r"function updateSvcAccordionSummary\(\)\{.*?\n\}"
    match = re.search(func_pattern, html, re.DOTALL)
    if match:
        print(f"  找到函数，长度{len(match.group())}")
        # 暂时不替换，避免误操作

# ============================================================
# updateImpactSummary - 原来用于更新签字确认tab的服务说明汇总
# 现在服务说明直接是表单，不需要汇总显示了
# ============================================================

# 保留函数但简化
old_update_impact = """function updateImpactSummary(){
  var urgentEl = document.getElementById('impactUrgent');
  var scopeEl = document.getElementById('impactScope');
  var stopRow = document.getElementById('impactStopDate');
  var stopVal = document.getElementById('impactStopDateVal');
  
  if(urgentEl){
    var f13 = document.getElementById('f13');
    urgentEl.textContent = f13 && f13.value ? f13.value : '未填写';
  }
  if(scopeEl){
    var items = [];
    document.querySelectorAll('input[name="impact"]:checked').forEach(function(cb){
      items.push(cb.value);
    });
    scopeEl.textContent = items.length > 0 ? items.join('、') : '未选择';
  }
  if(stopRow && stopVal){
    var f14 = document.getElementById('f14');
    var hasUser = document.querySelector('input[name="impact"][value="用户正常用梯"]:checked');
    if(hasUser && f14 && f14.value){
      stopRow.style.display = '';
      stopVal.textContent = f14.value;
    } else {
      stopRow.style.display = 'none';
    }
  }
}"""

new_update_impact = """function updateImpactSummary(){
  // 服务说明直接展示表单，无需更新汇总显示
  // 确保停梯日期行显示正确
  var stopRow = document.getElementById('stopRow');
  if(stopRow){
    var hasUser = document.querySelector('input[name="impact"][value="用户正常用梯"]:checked');
    stopRow.style.display = hasUser ? 'flex' : 'none';
  }
}"""

if old_update_impact in html:
    html = html.replace(old_update_impact, new_update_impact)
    print("✓ updateImpactSummary简化")
else:
    print("⚠ 未找到updateImpactSummary函数")

# ============================================================
# 去掉switchTab中滚动到tab栏位置的逻辑（因为现在tab是fixed的）
# ============================================================

# 原来的switchTab函数末尾有：
# var tabBar = document.getElementById('zoneTabs');
# if(tabBar){
#   var tabTop = tabBar.getBoundingClientRect().top + window.scrollY;
#   window.scrollTo({top: tabTop, behavior: 'smooth'});
# }
# 现在tab是fixed的，不需要滚动了

# 找到这段代码
old_scroll_code = """  // 滚动到tab栏位置
  var tabBar = document.getElementById('zoneTabs');
  if(tabBar){
    var tabTop = tabBar.getBoundingClientRect().top + window.scrollY;
    window.scrollTo({top: tabTop, behavior: 'smooth'});
  }"""

new_scroll_code = """  // tab栏已fixed固定，无需滚动"""

if old_scroll_code in html:
    html = html.replace(old_scroll_code, new_scroll_code)
    print("✓ 去掉switchTab中滚动到tab栏的逻辑")
else:
    print("⚠ 未找到switchTab中的滚动代码")

# ============================================================
# 去掉原来的滚动隐藏卡片区域的逻辑（那段关于sec-title的IIFE）
# 因为那个逻辑是针对另一种布局的，现在不适用了
# ============================================================

# 找到那段IIFE：
# (function(){
#   var secTitles=document.querySelectorAll('.sec-title');
#   ...
# })();
# 
# 这个逻辑是针对sec-title和sec-cards的，当前页面没有这些class，所以应该不影响
# 暂时保留，不影响功能

# ============================================================
# 调整toggleAccordion中的滚动逻辑
# 原来的手风琴切换后会滚动到标题位置，确保吸顶效果
# 现在布局变了，需要调整滚动目标
# ============================================================

# 找到toggleAccordion中的滚动代码
old_toggle_scroll = """    // 滚动到手风琴标题位置（确保吸顶效果正确）
    setTimeout(function(){
      var header = target.querySelector('.accordion-header');
      if(header){
        var tabBar = document.getElementById('zoneTabs');
        var tabBottom = tabBar ? tabBar.getBoundingClientRect().bottom : 145;
        var headerTop = header.getBoundingClientRect().top + window.scrollY;
        var targetScroll = headerTop - tabBottom - 5;
        if(targetScroll < window.scrollY - 10){
          window.scrollTo({top: targetScroll, behavior: 'smooth'});
        }
      }
    }, 50);"""

# 现在tab是fixed的，底部在145px位置（header+progress+tabs）
# 手风琴标题应该吸顶在tab栏下方
# 滚动逻辑调整：让标题刚好在tab栏下方
new_toggle_scroll = """    // 滚动到手风琴标题位置（确保吸顶效果正确）
    setTimeout(function(){
      var header = target.querySelector('.accordion-header');
      if(header){
        var headerTop = header.getBoundingClientRect().top + window.scrollY;
        // tab栏底部在145px，标题吸顶在145px位置
        var targetScroll = headerTop - 145 - 5;
        if(targetScroll > 0 && (targetScroll < window.scrollY - 10 || targetScroll > window.scrollY + 50)){
          window.scrollTo({top: targetScroll, behavior: 'smooth'});
        }
      }
    }, 50);"""

if old_toggle_scroll in html:
    html = html.replace(old_toggle_scroll, new_toggle_scroll)
    print("✓ toggleAccordion滚动逻辑调整")
else:
    print("⚠ 未找到toggleAccordion中的滚动代码")

# 保存修改
with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nJS修改完成，新文件长度: {len(html)}")
