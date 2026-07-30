#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 weite-service-beta.html 的6项改动：
1. 修复tab点击切换失效bug
2. 大分区从4个改为3个tab
3. 基本信息tab内4个子分区做手风琴
4. tab小标题吸顶固定
5. tab切换加左右滑动动画
6. 内容区上下固定/优化，消除抖动
"""

import re

FILE_PATH = '/app/data/所有对话/主对话/weite-pro-temp/weite-service-beta.html'

def read_file():
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(content):
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    html = read_file()
    original = html
    
    # ========== 改动1+5+6: CSS - 更新tab样式、添加滑动动画、内容区固定 ==========
    old_zone_tabs_css = """/* ===== Tab分区栏 ===== */
.zone-tabs{display:flex;gap:0;padding:0 8px;background:#fff;overflow-x:auto;flex-shrink:0;
  -webkit-overflow-scrolling:touch;border-bottom:2px solid #edf2f7;position:sticky;top:101px;z-index:48;}
.zone-tabs::-webkit-scrollbar{display:none;}
.zone-tab{padding:12px 14px;white-space:nowrap;font-size:13px;font-weight:600;color:#718096;
  cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all .15s;flex-shrink:0;}
.zone-tab.active{color:#667eea;border-bottom-color:#667eea;}
.zone-panel{display:none;animation:fadeIn .2s ease;padding:12px;}
.zone-panel.active{display:block;}
@keyframes fadeIn{from{opacity:0;transform:translateY(4px);}to{opacity:1;transform:translateY(0);}}"""

    new_zone_tabs_css = """/* ===== Tab分区栏 ===== */
.zone-tabs{display:flex;gap:0;padding:0 12px;background:#fff;overflow-x:auto;flex-shrink:0;
  -webkit-overflow-scrolling:touch;border-bottom:2px solid #edf2f7;position:sticky;top:101px;z-index:48;
  -webkit-backface-visibility:hidden;will-change:transform;}
.zone-tabs::-webkit-scrollbar{display:none;}
.zone-tab{padding:12px 18px;white-space:nowrap;font-size:14px;font-weight:600;color:#718096;
  cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all .2s ease;flex-shrink:0;
  -webkit-tap-highlight-color:transparent;}
.zone-tab.active{color:#667eea;border-bottom-color:#667eea;font-weight:700;}

/* ===== 内容区容器：固定高度防抖动 ===== */
.zone-content{position:relative;overflow:hidden;min-height:60vh;}
.zone-panel{display:none;padding:12px;}
.zone-panel.active{display:block;}

/* ===== Tab滑动动画 ===== */
.zone-content.slide-left{
  animation: slideFromRight 0.32s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
  -webkit-animation: slideFromRight 0.32s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
}
.zone-content.slide-right{
  animation: slideFromLeft 0.32s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
  -webkit-animation: slideFromLeft 0.32s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
}
@keyframes slideFromRight{
  from{transform:translateX(50%);opacity:0;}
  to{transform:translateX(0);opacity:1;}
}
@-webkit-keyframes slideFromRight{
  from{-webkit-transform:translateX(50%);opacity:0;}
  to{-webkit-transform:translateX(0);opacity:1;}
}
@keyframes slideFromLeft{
  from{transform:translateX(-50%);opacity:0;}
  to{transform:translateX(0);opacity:1;}
}
@-webkit-keyframes slideFromLeft{
  from{-webkit-transform:translateX(-50%);opacity:0;}
  to{-webkit-transform:translateX(0);opacity:1;}
}

/* ===== 手风琴样式 ===== */
.accordion{background:#fff;border-radius:12px;overflow:hidden;margin-bottom:10px;border:1.5px solid #e2e8f0;
  box-shadow:0 1px 4px rgba(0,0,0,.04);}
.accordion-header{display:flex;align-items:center;justify-content:space-between;padding:14px 16px;
  cursor:pointer;background:#fff;transition:background .2s;-webkit-tap-highlight-color:transparent;}
.accordion-header:active{background:#f7fafc;}
.accordion-header .acc-left{display:flex;align-items:center;gap:10px;}
.accordion-header .acc-icon{font-size:20px;}
.accordion-header .acc-title{font-size:14px;font-weight:600;color:#2d3748;}
.accordion-header .acc-arrow{font-size:14px;color:#a0aec0;transition:transform .25s ease;flex-shrink:0;}
.accordion.active .accordion-header .acc-arrow{transform:rotate(180deg);color:#667eea;}
.accordion.active .accordion-header{background:linear-gradient(135deg,#f8f9ff,#f5f3ff);}
.accordion-body{max-height:0;overflow:hidden;transition:max-height .3s ease,padding .3s ease;padding:0 16px;}
.accordion.active .accordion-body{max-height:2000px;padding:12px 16px 16px;border-top:1px solid #edf2f7;}
.accordion .card-status{width:8px;height:8px;border-radius:50%;background:#cbd5e0;display:inline-block;}
.accordion .card-status.filled{background:#68d391;}"""

    assert old_zone_tabs_css in html, "Cannot find zone tabs CSS"
    html = html.replace(old_zone_tabs_css, new_zone_tabs_css)
    print("✓ CSS updated (tabs, slide animation, accordion)")
    
    # ========== 改动2: HTML - 4个tab改为3个 ==========
    old_tabs_html = """<!-- Tab分区栏 -->
<div class="zone-tabs" id="zoneTabs">
  <div class="zone-tab active" onclick="switchTab(0)">基本信息</div>
  <div class="zone-tab" onclick="switchTab(1)">故障描述</div>
  <div class="zone-tab" onclick="switchTab(2)">检修记录</div>
  <div class="zone-tab" onclick="switchTab(3)">验收签字</div>
</div>"""

    new_tabs_html = """<!-- Tab分区栏 -->
<div class="zone-tabs" id="zoneTabs">
  <div class="zone-tab active" onclick="switchTab(0)">基本信息</div>
  <div class="zone-tab" onclick="switchTab(1)">服务详情</div>
  <div class="zone-tab" onclick="switchTab(2)">签字确认</div>
</div>"""

    assert old_tabs_html in html, "Cannot find zone tabs HTML"
    html = html.replace(old_tabs_html, new_tabs_html)
    print("✓ Tab labels updated (3 tabs)")
    
    # ========== 改动2+3: HTML - 重构zone-content ==========
    # 先找到旧的zone-content区域
    old_zone_content_start = '<!-- Tab内容区 -->\n<div class="zone-content">'
    old_zone_content_end = '\n</div>\n\n<!-- 底部操作栏 -->'
    
    # 找到旧内容
    start_idx = html.find(old_zone_content_start)
    end_idx = html.find(old_zone_content_end, start_idx)
    assert start_idx != -1 and end_idx != -1, "Cannot find zone content"
    end_idx += len(old_zone_content_end)
    old_zone_content_full = html[start_idx:end_idx]
    
    # 构建新的zone-content：3个panel
    # Panel 0: 基本信息（手风琴）
    # Panel 1: 服务详情（卡片）
    # Panel 2: 签字确认（卡片）
    
    new_zone_content = """<!-- Tab内容区 -->
<div class="zone-content" id="zoneContent">
  <!-- Tab 1: 基本信息（手风琴） -->
  <div class="zone-panel active" id="zonePanel_0">
    <div class="zone-section-title">基础资料</div>
    <!-- 申请人 -->
    <div class="accordion active" data-acc="basic">
      <div class="accordion-header" onclick="toggleAccordion('basic')">
        <div class="acc-left"><span class="acc-icon">📋</span><span class="acc-title">申请人</span></div>
        <div style="display:flex;align-items:center;gap:10px;">
          <span class="card-status" id="st_basic"></span>
          <span class="acc-arrow">▼</span>
        </div>
      </div>
      <div class="accordion-body">
        <div class="fr"><label>服务指令发起人</label><input type="text" id="f1" oninput="updateBtnStatus()"></div>
        <div class="fr"><label>此项目第</label><input type="number" id="f2" style="max-width:80px;" oninput="updateBtnStatus()"><span style="font-size:13px;">次服务</span></div>
        <div class="fr"><label>服务时间</label><input type="datetime-local" id="f12" oninput="updateBtnStatus()"></div>
      </div>
    </div>
    <!-- 项目信息 -->
    <div class="accordion" data-acc="project">
      <div class="accordion-header" onclick="toggleAccordion('project')">
        <div class="acc-left"><span class="acc-icon">🏗️</span><span class="acc-title">项目信息</span></div>
        <div style="display:flex;align-items:center;gap:10px;">
          <span class="card-status" id="st_project"></span>
          <span class="acc-arrow">▼</span>
        </div>
      </div>
      <div class="accordion-body">
        <div class="fr"><label>项目名</label><input type="text" id="f3" oninput="updateBtnStatus()"></div>
        <div id="elevBox"></div>
        <div class="ar" id="addElevBtn" style="margin-bottom:10px;">+ 添加电梯</div>
        <div style="margin-bottom:10px;">
          <label style="font-size:13px;color:#333;display:block;margin-bottom:6px;">项目所在地</label>
          <div class="fr" style="margin-bottom:4px;">
            <input type="text" id="locDisplay" placeholder="点击选择省/市/区" readonly style="flex:1;background:#fafafa;cursor:pointer;" onclick="showLocPicker()">
          </div>
          <div class="fr" style="margin-bottom:4px;">
            <input type="text" id="f5" placeholder="详细地址" style="flex:1;" oninput="updateBtnStatus()">
          </div>
        </div>
      </div>
    </div>
    <!-- 联系方式 -->
    <div class="accordion" data-acc="contact">
      <div class="accordion-header" onclick="toggleAccordion('contact')">
        <div class="acc-left"><span class="acc-icon">📞</span><span class="acc-title">联系方式</span></div>
        <div style="display:flex;align-items:center;gap:10px;">
          <span class="card-status" id="st_contact"></span>
          <span class="acc-arrow">▼</span>
        </div>
      </div>
      <div class="accordion-body">
        <div class="fr"><label>现场联系人</label><input type="text" id="f8" oninput="updateBtnStatus()"></div>
        <div class="fr"><label>联系电话</label><input type="tel" id="f9" pattern="^1[3-9]\\d{9}$" maxlength="11" placeholder="11位手机号" oninput="updateBtnStatus()"></div>
        <div class="fr"><label>服务人</label><input type="text" id="f10" oninput="updateBtnStatus()"></div>
        <div class="fr"><label>服务电话</label><input type="tel" id="f11" pattern="^1[3-9]\\d{9}$" maxlength="11" placeholder="11位手机号" oninput="updateBtnStatus()"></div>
      </div>
    </div>
    <!-- 施工类别 -->
    <div class="accordion" data-acc="build">
      <div class="accordion-header" onclick="toggleAccordion('build')">
        <div class="acc-left"><span class="acc-icon">🔧</span><span class="acc-title">施工类别</span></div>
        <div style="display:flex;align-items:center;gap:10px;">
          <span class="card-status" id="st_build"></span>
          <span class="acc-arrow">▼</span>
        </div>
      </div>
      <div class="accordion-body">
        <div class="cg" id="cgBuild"></div>
      </div>
    </div>
  </div>

  <!-- Tab 2: 服务详情 -->
  <div class="zone-panel" id="zonePanel_1">
    <div class="zone-section-title">服务信息</div>
    <div class="sec-cards">
      <div class="form-card card-pink" onclick="openMo('serviceMo')"><span class="card-icon">📝</span><span class="card-label">服务类别</span><div class="card-status" id="st_service"></div></div>
      <div class="form-card card-yellow" onclick="openMo('flowMo')"><span class="card-icon">🔄</span><span class="card-label">服务节点</span><div class="card-status" id="st_flow"></div></div>
      <div class="form-card card-indigo full-width" onclick="openMo('recordMo')"><span class="card-icon">💬</span><span class="card-label">服务内容/记录</span><span class="card-count" id="st_record">0条</span></div>
      <div class="form-card card-teal" onclick="openMo('impactMo')"><span class="card-icon">⚠️</span><span class="card-label">服务说明</span><div class="card-status" id="st_impact"></div></div>
    </div>
  </div>

  <!-- Tab 3: 签字确认 -->
  <div class="zone-panel" id="zonePanel_2">
    <div class="zone-section-title">确认与数据</div>
    <div class="sec-cards">
      <div class="form-card card-purple" onclick="openMo('signMo')"><span class="card-icon">✍️</span><span class="card-label">签字确认</span><div class="card-status" id="st_sign"></div></div>
      <div class="form-card card-blue" onclick="openMo('historyMo')"><span class="card-icon">📂</span><span class="card-label">已保存</span><span class="card-count" id="st_history">0条</span></div>
      <div class="form-card card-green full-width" onclick="openMo('dataMo')"><span class="card-icon">📦</span><span class="card-label">数据迁移</span><div class="card-status" id="st_data"></div></div>
    </div>
  </div>
</div>

<!-- 底部操作栏 -->"""

    html = html[:start_idx] + new_zone_content + html[end_idx:]
    print("✓ Zone content restructured (3 panels + accordion)")
    
    # ========== 移除重复的底部操作栏和toast ==========
    # 第一个btm和toast在zone-content后面（我们已经保留）
    # 第二个btm和toast在数据迁移弹窗后面，需要移除
    
    # 找到第二个btm（数据迁移弹窗结束后的）
    second_btm_pattern = '\n</div>\n</div></div>\n\n<div class="btm"><button class="btn-primary" id="saveBtn">💾 保存服务单</button><button class="btn-secondary" id="clearBtn">🗑️ 清空</button></div>\n\n<div class="toast" id="toast"></div>'
    # 更精确地找：在dataMo结束后，签名弹窗前的重复btm和toast
    data_mo_end = '</div>\n</div></div>\n\n<div class="btm"><button class="btn-primary" id="saveBtn">💾 保存服务单</button><button class="btn-secondary" id="clearBtn">🗑️ 清空</button></div>\n\n<div class="toast" id="toast"></div>\n\n<!-- 签名弹窗'
    if data_mo_end in html:
        # 替换为只保留dataMo结束，去掉重复btm/toast
        html = html.replace(data_mo_end, '</div>\n</div></div>\n\n<!-- 签名弹窗')
        print("✓ Removed duplicate bottom bar and toast")
    else:
        print("⚠ Could not find duplicate btm to remove, checking alternative pattern...")
        # 尝试另一种匹配
        dup_pattern = '</div>\n</div></div>\n\n<div class="btm"><button class="btn-primary" id="saveBtn"'
        if dup_pattern in html:
            # 找到第一个出现位置（应该在zone-content后）和第二个出现位置
            first_pos = html.find(dup_pattern)
            second_pos = html.find(dup_pattern, first_pos + 1)
            if second_pos != -1:
                # 找到第二个btm的结束位置（到下一个注释或元素）
                end_marker = '\n\n<!-- 签名弹窗'
                end_pos = html.find(end_marker, second_pos)
                if end_pos != -1:
                    # 找到toast结束位置
                    toast_end = html.find('</div>\n\n<!-- 签名弹窗', second_pos)
                    if toast_end != -1:
                        html = html[:second_pos] + html[toast_end + len('</div>'):]
                        print("✓ Removed duplicate btm and toast (alt method)")
    
    # ========== 改动1+5: JS - 修复switchTab并添加滑动动画 ==========
    old_switch_tab = """// ===== Tab 切换函数 =====
var currentTabIndex = 0;
function switchTab(index){
  if(index<0||index>=4)return;
  currentTabIndex=index;
  var tabs=document.querySelectorAll('.zone-tab');
  var panels=document.querySelectorAll('.zone-panel');
  for(var i=0;i<tabs.length;i++){
    tabs[i].classList.toggle('active',i===index);
  }
  for(var i=0;i<panels.length;i++){
    panels[i].classList.toggle('active',i===index);
  }
  window.scrollTo(0,0);
}"""

    new_switch_tab = """// ===== Tab 切换函数（全局暴露+滑动动画） =====
var currentTabIndex = 0;
function switchTab(index){
  if(index<0||index>=3)return;
  if(index===currentTabIndex)return;
  var direction = index > currentTabIndex ? 'left' : 'right';
  currentTabIndex=index;
  var tabs=document.querySelectorAll('.zone-tab');
  var panels=document.querySelectorAll('.zone-panel');
  var content=document.getElementById('zoneContent');
  // 更新tab激活态
  for(var i=0;i<tabs.length;i++){
    tabs[i].classList.toggle('active',i===index);
  }
  // 更新panel激活态
  for(var i=0;i<panels.length;i++){
    panels[i].classList.toggle('active',i===index);
  }
  // 滑动动画
  if(content){
    content.classList.remove('slide-left','slide-right');
    // 强制重排
    void content.offsetWidth;
    if(direction==='left'){
      content.classList.add('slide-left');
    }else{
      content.classList.add('slide-right');
    }
  }
  // 滚动到顶部（平滑，避免抖动）
  var tabBar=document.getElementById('zoneTabs');
  if(tabBar){
    var tabTop=tabBar.getBoundingClientRect().top+window.scrollY;
    window.scrollTo({top:tabTop,behavior:'smooth'});
  }else{
    window.scrollTo(0,0);
  }
}
// 暴露到全局（修复onclick调用失效bug）
window.switchTab=switchTab;

// ===== 手风琴切换函数 =====
var currentAccordion='basic';
function toggleAccordion(name){
  var items=document.querySelectorAll('.accordion');
  var target=null;
  items.forEach(function(item){
    if(item.getAttribute('data-acc')===name){
      target=item;
    }
  });
  if(!target)return;
  var isActive=target.classList.contains('active');
  // 全部收起
  items.forEach(function(item){item.classList.remove('active');});
  // 如果之前不是展开的，则展开目标
  if(!isActive){
    target.classList.add('active');
    currentAccordion=name;
  }else{
    // 如果点击的是已展开的，保持收起，但默认展开第一个
    currentAccordion='';
  }
  updateBtnStatus();
}
window.toggleAccordion=toggleAccordion;"""

    assert old_switch_tab in html, "Cannot find switchTab function"
    html = html.replace(old_switch_tab, new_switch_tab)
    print("✓ switchTab fixed + slide animation + accordion JS added")
    
    # ========== 更新进度条 total 数量 ==========
    # updateBtnStatus 里 total=11，保持不变（字段数量没变）
    
    write_file(html)
    print("\n✅ All 6 changes applied successfully!")
    print(f"Original size: {len(original)} chars")
    print(f"New size: {len(html)} chars")

if __name__ == '__main__':
    main()
