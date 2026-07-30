#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术服务单体验版第二波优化 - 7项改动
"""

import os
import re
import shutil

BASE_DIR = '/app/data/所有对话/主对话/weite-pro-temp'
SRC_FILE = os.path.join(BASE_DIR, 'weite-service-beta.html')
DETAIL_FILE = os.path.join(BASE_DIR, 'weite-service-beta-detail.html')
LIST_FILE = os.path.join(BASE_DIR, 'weite-service-beta.html')


def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  写入: {path} ({len(content)} 字节)')


def build_detail_page():
    """创建详情页 - 实现改动1-6 + 返回列表按钮"""
    html = read_file(SRC_FILE)
    
    # ========== 改动4：顶部菜单样式 + 改动1：手风琴吸顶样式 ==========
    # 在CSS中添加新样式
    
    # 1. 手风琴标题吸顶样式
    sticky_acc_css = '''
/* ===== 手风琴标题吸顶 ===== */
.zone-panel{position:relative;}
.accordion-header.sticky-acc{position:sticky;top:145px;z-index:5;background:#fff;box-shadow:0 2px 4px rgba(0,0,0,.06);}
.accordion.active .accordion-header.sticky-acc{background:linear-gradient(135deg,#f8f9ff,#f5f3ff);}
'''
    
    # 2. 顶部菜单按钮样式
    header_menu_css = '''
/* ===== 顶部更多菜单 ===== */
.header{position:relative;}
.header-more-btn{position:absolute;right:16px;top:50%;transform:translateY(-50%);background:#f0f4f8;border:1.5px solid #cbd5e0;border-radius:8px;font-size:18px;color:#1a3a6b;cursor:pointer;padding:4px 10px;z-index:60;line-height:1;font-weight:bold;-webkit-tap-highlight-color:transparent;}
.header-more-btn:active{background:#e2e8f0;}
.header-dropdown{display:none;position:absolute;right:16px;top:48px;background:#fff;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,.15);z-index:100;min-width:160px;overflow:hidden;border:1px solid #e2e8f0;}
.header-dropdown.show{display:block;}
.header-dropdown div{padding:12px 16px;font-size:14px;color:#2d3748;cursor:pointer;border-bottom:1px solid #f0f4f8;-webkit-tap-highlight-color:transparent;}
.header-dropdown div:last-child{border-bottom:none;}
.header-dropdown div:active{background:#f7fafc;}
.header-dropdown .menu-icon{display:inline-block;width:20px;margin-right:8px;text-align:center;}

/* ===== 返回列表按钮 ===== */
.header-back-btn{position:absolute;left:12px;top:50%;transform:translateY(-50%);background:none;border:none;font-size:20px;color:#1a3a6b;cursor:pointer;padding:4px 8px;z-index:60;-webkit-tap-highlight-color:transparent;}
.logo-area{justify-content:center;position:relative;}
'''

    # 3. 签字确认tab新样式（只保留签字相关内容）
    sign_tab_css = '''
/* ===== 签字确认tab内容 ===== */
.sign-section{background:#fff;border-radius:12px;padding:16px;margin-bottom:10px;border:1.5px solid #e2e8f0;box-shadow:0 1px 4px rgba(0,0,0,.04);}
.sign-section h4{font-size:14px;font-weight:700;color:#2d3748;margin-bottom:10px;}
.sign-note{font-size:12px;color:#718096;margin-bottom:8px;}
'''
    
    # 4. 改进的tab滑动动画样式
    new_slide_css = '''
/* ===== 改进的Tab滑动动画 ===== */
.zone-content{position:relative;overflow:hidden;min-height:60vh;}
.zone-panel{display:none;padding:12px;width:100%;}
.zone-panel.active{display:block;}
.zone-content.animating .zone-panel.slide-in{display:block;position:absolute;top:0;left:0;right:0;}
@keyframes slideInFromRight{
  from{transform:translateX(100%);opacity:0.5;}
  to{transform:translateX(0);opacity:1;}
}
@-webkit-keyframes slideInFromRight{
  from{-webkit-transform:translateX(100%);opacity:0.5;}
  to{-webkit-transform:translateX(0);opacity:1;}
}
@keyframes slideInFromLeft{
  from{transform:translateX(-100%);opacity:0.5;}
  to{transform:translateX(0);opacity:1;}
}
@-webkit-keyframes slideInFromLeft{
  from{-webkit-transform:translateX(-100%);opacity:0.5;}
  to{-webkit-transform:translateX(0);opacity:1;}
}
@keyframes slideOutToLeft{
  from{transform:translateX(0);opacity:1;}
  to{transform:translateX(-30%);opacity:0;}
}
@-webkit-keyframes slideOutToLeft{
  from{-webkit-transform:translateX(0);opacity:1;}
  to{-webkit-transform:translateX(-30%);opacity:0;}
}
@keyframes slideOutToRight{
  from{transform:translateX(0);opacity:1;}
  to{transform:translateX(30%);opacity:0;}
}
@-webkit-keyframes slideOutToRight{
  from{-webkit-transform:translateX(0);opacity:1;}
  to{-webkit-transform:translateX(30%);opacity:0;}
}
'''
    
    # 替换旧的滑动动画CSS块
    old_slide_pattern = r'/\* ===== Tab滑动动画 ===== \*/.*?@-webkit-keyframes slideFromLeft\{.*?\}'
    if re.search(old_slide_pattern, html, re.DOTALL):
        html = re.sub(old_slide_pattern, new_slide_css.strip(), html, count=1, flags=re.DOTALL)
    
    # 也替换旧的 zone-content 样式
    old_zone_content = r'/\* ===== 内容区容器：固定高度防抖动 ===== \*/\n\.zone-content\{position:relative;overflow:hidden;min-height:60vh;\}\n\.zone-panel\{display:none;padding:12px;\}\n\.zone-panel\.active\{display:block;\}'
    if re.search(old_zone_content, html):
        pass  # 新的样式已经包含了这些
    
    # 在响应式微调之前插入新的CSS
    insert_point = '/* ===== 响应式微调 ===== */'
    new_css_block = sticky_acc_css + header_menu_css + sign_tab_css
    html = html.replace(insert_point, new_css_block + '\n' + insert_point)
    
    # ========== 改动4：顶部header改造 - 添加返回按钮和更多菜单 ==========
    old_header = '''<!-- 顶部Header -->
<div class="header">
  <div class="logo-area">
    <img class="logo-img" src="data:image/webp;base64,UklGRrwFAABXRUJQVlA4ILAFAADwIACdASrYAEAAPm0ulUYkIqIhLTN7oIANiWIA0XiYk6fAcypylKVfR8u8/Dbw+YDzgP9B6n95359z2hL9E7d/719M3U1HvX4z8e/yx1EW+/ZA9GXqr6AdtRxosfn/A9PH/M/wfnl+ov+x7h/8p/r/WV/ab2E/07SHbXhZHt4C8qbGczRQ+YhCP904TtF2T0CCKyarJnypB/hAK6gQjXC9iwsKwwC+OU9rHGVQYHoJ6rQgTA7XrCkoSqGEyqPx+s/JTspyE0a/wsHHmamelpQCinlWWUKPRRn2jng/2F6cIdPGnOlsdbXFcJsLUCwUtt4xh8NxuwH9RK03w+j532Ir+l0sI72fbPxXS3J23eO7gAD+/KharSACg7d/D3l4HJGQhCdQ227rBH9fuFBIE9S7KXkbv7srGfvvq8TrxYIaGqIqQ/b0R4LwFqs4veGNAtr2N/9XffjClI9y+Ns078yTGj+KSGmGoaW2Fg/yvd4F7TzYht4cvAZutRHBgxFjmYPyk/Z1thQLvhA7bIQJk3t7yUcjDBEsNXXBg1DpLtTLyUkG1b9F3vtmuHLAPrBInM7M7U/c1FeNzDPVV+6BRvH2iEWC6nY3/1H7aw0kAHQYdp42tv5GgpRGgiYmYUVL5Qd/4ijq3Rfbapv3bWVmxZKsplOi5YLgdbLkTcDBjYXWKam/rObme42a6zh11FrQw4NEOL27WA25k2pume6U/xMh4P/PDiwbukzK7WSnmwOFe0ciPINJrwLzrkAeD6BD0SWAq0Q1wWwnlYW3LUY/y8m3f+f/X/n/79m0bBWtpP5xqSkXsKoWDOqRiwoP0BAnzpBgbm894mRq0lIcL4xJBCo9bdnhraMV0K/QTKujLzuUPojKhYvfv/p70tbIdD3NBjM+qJFCBD9zPo9D482iTfk6qobTD32BQWLSMxicFoe6FYzy/oPmoP638ZRjj32Uz6ALnezqdAe7rPmGGNdjTIcgSEb5jx6vZjH2PD/lXhCFVeLX4LauAmPeFQ6h2f+s8cklG4i5Cq0lzmoy063xvLZoCPrQxnTlVru5RClIu5c9JB+MEPv59l/Ael7/Yx1PxGUL7lXtPJR4nJaLQfl2losnfjlp9kdVwsxXlk6+iLf0jX0xuGblGMMs8ud9+H1rRDUFRM6kdd7WGgH/nGnS9whJCrYMo6AiYO+SteHvU7UDlX1bDoZi+EzPtFErY2YzD7EssR7JEWpOcLeheC72VKac5Bz192vBsPf1uOnFNig0EZTR9OjSmAhxfknwgxOT47IGBghTTIbjZO6jUIanJs/JhPwzLLc2ZqbmiNX4+30SicCTM90VJVN+6i5YU4V5Puf3Asu802W45DRPchPNC9NQxrs/y3VvUDf2cqxaXmk5AP6bgaO9Ofuv5AMvDOmfSY7oDs1NLtdFkqoWjzOOax+M/uI4MHe9puGHMgqTVcP25iaQcuBHlgSqCp+iQmBoivAqM6YtWQoqlZ+fSyfSnYKbRd7DsI5CmBFvlwzdlHP1+nQybKj8mvr3IyDZpBJ10OtAnq10T2GQOXEkw1HHsm60s9vId47czppsEl+VZyrnQ5Z6i8+c1Y7m7QILvbdD+GIatZWMRNtiR+YCpX9OUp26fZTgoIjkaD3ZcEjnT4/iENcoz/7Hfq09z/newBZMpuD+1ko1UoWKpIB/jGpf/qNMYFfTe5rvRVFq+1Xdk5EsJvsgYwENrNB68IrkFpHu+2KzzABc7FqwVfAhJdqRCxeasS4dDiF0b5Lqfasg8AVMtt3biVFXL9wLKy5X69mHZaD0UtE5OafUdUcdB9xvfmW/Siv+xCmWpjo5qPnSkcOt09PGXwAYpphRp9NLPaSXlQ0XCSNh9OoC74DABb0pbu5taHZj4uzOfu9rRKUvW+fWkRUxDr2zbvFTxLY/XvUy26/eAhK9wRTlytnMF2ZwTwAA" alt="WEITE">
    <span class="logo-elev">电梯</span>
  </div>
  <div class="header-sub"><span class="hl"></span><span>技术服务单</span><span class="hl"></span></div>
</div>'''
    
    new_header = '''<!-- 顶部Header -->
<div class="header">
  <button class="header-back-btn" onclick="goBackToList()">←</button>
  <div class="logo-area">
    <img class="logo-img" src="data:image/webp;base64,UklGRrwFAABXRUJQVlA4ILAFAADwIACdASrYAEAAPm0ulUYkIqIhLTN7oIANiWIA0XiYk6fAcypylKVfR8u8/Dbw+YDzgP9B6n95359z2hL9E7d/719M3U1HvX4z8e/yx1EW+/ZA9GXqr6AdtRxosfn/A9PH/M/wfnl+ov+x7h/8p/r/WV/ab2E/07SHbXhZHt4C8qbGczRQ+YhCP904TtF2T0CCKyarJnypB/hAK6gQjXC9iwsKwwC+OU9rHGVQYHoJ6rQgTA7XrCkoSqGEyqPx+s/JTspyE0a/wsHHmamelpQCinlWWUKPRRn2jng/2F6cIdPGnOlsdbXFcJsLUCwUtt4xh8NxuwH9RK03w+j532Ir+l0sI72fbPxXS3J23eO7gAD+/KharSACg7d/D3l4HJGQhCdQ227rBH9fuFBIE9S7KXkbv7srGfvvq8TrxYIaGqIqQ/b0R4LwFqs4veGNAtr2N/9XffjClI9y+Ns078yTGj+KSGmGoaW2Fg/yvd4F7TzYht4cvAZutRHBgxFjmYPyk/Z1thQLvhA7bIQJk3t7yUcjDBEsNXXBg1DpLtTLyUkG1b9F3vtmuHLAPrBInM7M7U/c1FeNzDPVV+6BRvH2iEWC6nY3/1H7aw0kAHQYdp42tv5GgpRGgiYmYUVL5Qd/4ijq3Rfbapv3bWVmxZKsplOi5YLgdbLkTcDBjYXWKam/rObme42a6zh11FrQw4NEOL27WA25k2pume6U/xMh4P/PDiwbukzK7WSnmwOFe0ciPINJrwLzrkAeD6BD0SWAq0Q1wWwnlYW3LUY/y8m3f+f/X/n/79m0bBWtpP5xqSkXsKoWDOqRiwoP0BAnzpBgbm894mRq0lIcL4xJBCo9bdnhraMV0K/QTKujLzuUPojKhYvfv/p70tbIdD3NBjM+qJFCBD9zPo9D482iTfk6qobTD32BQWLSMxicFoe6FYzy/oPmoP638ZRjj32Uz6ALnezqdAe7rPmGGNdjTIcgSEb5jx6vZjH2PD/lXhCFVeLX4LauAmPeFQ6h2f+s8cklG4i5Cq0lzmoy063xvLZoCPrQxnTlVru5RClIu5c9JB+MEPv59l/Ael7/Yx1PxGUL7lXtPJR4nJaLQfl2losnfjlp9kdVwsxXlk6+iLf0jX0xuGblGMMs8ud9+H1rRDUFRM6kdd7WGgH/nGnS9whJCrYMo6AiYO+SteHvU7UDlX1bDoZi+EzPtFErY2YzD7EssR7JEWpOcLeheC72VKac5Bz192vBsPf1uOnFNig0EZTR9OjSmAhxfknwgxOT47IGBghTTIbjZO6jUIanJs/JhPwzLLc2ZqbmiNX4+30SicCTM90VJVN+6i5YU4V5Puf3Asu802W45DRPchPNC9NQxrs/y3VvUDf2cqxaXmk5AP6bgaO9Ofuv5AMvDOmfSY7oDs1NLtdFkqoWjzOOax+M/uI4MHe9puGHMgqTVcP25iaQcuBHlgSqCp+iQmBoivAqM6YtWQoqlZ+fSyfSnYKbRd7DsI5CmBFvlwzdlHP1+nQybKj8mvr3IyDZpBJ10OtAnq10T2GQOXEkw1HHsm60s9vId47czppsEl+VZyrnQ5Z6i8+c1Y7m7QILvbdD+GIatZWMRNtiR+YCpX9OUp26fZTgoIjkaD3ZcEjnT4/iENcoz/7Hfq09z/newBZMpuD+1ko1UoWKpIB/jGpf/qNMYFfTe5rvRVFq+1Xdk5EsJvsgYwENrNB68IrkFpHu+2KzzABc7FqwVfAhJdqRCxeasS4dDiF0b5Lqfasg8AVMtt3biVFXL9wLKy5X69mHZaD0UtE5OafUdUcdB9xvfmW/Siv+xCmWpjo5qPnSkcOt09PGXwAYpphRp9NLPaSXlQ0XCSNh9OoC74DABb0pbu5taHZj4uzOfu9rRKUvW+fWkRUxDr2zbvFTxLY/XvUy26/eAhK9wRTlytnMF2ZwTwAA" alt="WEITE">
    <span class="logo-elev">电梯</span>
  </div>
  <button class="header-more-btn" onclick="toggleHeaderMenu()">⋯</button>
  <div class="header-dropdown" id="headerDropdown">
    <div onclick="closeHeaderMenu();openMo('historyMo')"><span class="menu-icon">📂</span>已保存记录</div>
    <div onclick="closeHeaderMenu();openMo('dataMo')"><span class="menu-icon">📦</span>数据迁移</div>
  </div>
  <div class="header-sub"><span class="hl"></span><span>技术服务单</span><span class="hl"></span></div>
</div>'''
    
    html = html.replace(old_header, new_header)
    
    # ========== 改动1：手风琴标题吸顶 - 添加sticky-acc类 ==========
    # 给基本信息tab内的每个accordion-header添加sticky-acc类
    # 需要在每个accordion-header的onclick之前添加class
    html = html.replace(
        '<div class="accordion-header" onclick="toggleAccordion(\'basic\')">',
        '<div class="accordion-header sticky-acc" onclick="toggleAccordion(\'basic\')">'
    )
    html = html.replace(
        '<div class="accordion-header" onclick="toggleAccordion(\'project\')">',
        '<div class="accordion-header sticky-acc" onclick="toggleAccordion(\'project\')">'
    )
    html = html.replace(
        '<div class="accordion-header" onclick="toggleAccordion(\'contact\')">',
        '<div class="accordion-header sticky-acc" onclick="toggleAccordion(\'contact\')">'
    )
    html = html.replace(
        '<div class="accordion-header" onclick="toggleAccordion(\'build\')">',
        '<div class="accordion-header sticky-acc" onclick="toggleAccordion(\'build\')">'
    )
    
    # ========== 改动2：服务详情tab改手风琴 ==========
    # 替换服务详情tab的内容
    old_service_tab = '''  <!-- Tab 2: 服务详情 -->
  <div class="zone-panel" id="zonePanel_1">
    <div class="zone-section-title">服务信息</div>
    <div class="sec-cards">
      <div class="form-card card-pink" onclick="openMo('serviceMo')"><span class="card-icon">📝</span><span class="card-label">服务类别</span><div class="card-status" id="st_service"></div></div>
      <div class="form-card card-yellow" onclick="openMo('flowMo')"><span class="card-icon">🔄</span><span class="card-label">服务节点</span><div class="card-status" id="st_flow"></div></div>
      <div class="form-card card-indigo full-width" onclick="openMo('recordMo')"><span class="card-icon">💬</span><span class="card-label">服务内容/记录</span><span class="card-count" id="st_record">0条</span></div>
      <div class="form-card card-teal" onclick="openMo('impactMo')"><span class="card-icon">⚠️</span><span class="card-label">服务说明</span><div class="card-status" id="st_impact"></div></div>
    </div>
  </div>'''
    
    new_service_tab = '''  <!-- Tab 2: 服务详情（手风琴） -->
  <div class="zone-panel" id="zonePanel_1">
    <div class="zone-section-title">服务信息</div>
    <!-- 服务类别 -->
    <div class="accordion active" data-acc-svc="svcCategory">
      <div class="accordion-header sticky-acc" onclick="toggleSvcAccordion('svcCategory')">
        <div class="acc-left"><span class="acc-icon">📝</span><span class="acc-title">服务类别</span></div>
        <div style="display:flex;align-items:center;gap:10px;">
          <span class="card-status" id="st_service"></span>
          <span class="acc-arrow">▼</span>
        </div>
      </div>
      <div class="accordion-body">
        <div id="svcCatsBody"></div>
        <div style="text-align:center;margin-top:10px;">
          <button style="background:linear-gradient(135deg,#e74c3c,#c0392b);color:#fff;border:none;border-radius:8px;padding:8px 20px;font-size:13px;font-weight:600;cursor:pointer;" onclick="openMo('serviceMo')">编辑服务类别</button>
        </div>
      </div>
    </div>
    <!-- 服务节点 -->
    <div class="accordion" data-acc-svc="svcFlow">
      <div class="accordion-header sticky-acc" onclick="toggleSvcAccordion('svcFlow')">
        <div class="acc-left"><span class="acc-icon">🔄</span><span class="acc-title">服务节点</span></div>
        <div style="display:flex;align-items:center;gap:10px;">
          <span class="card-status" id="st_flow"></span>
          <span class="acc-arrow">▼</span>
        </div>
      </div>
      <div class="accordion-body">
        <div class="cg" id="cgFlowBody"></div>
        <div style="text-align:center;margin-top:10px;">
          <button style="background:linear-gradient(135deg,#f39c12,#f1c40f);color:#fff;border:none;border-radius:8px;padding:8px 20px;font-size:13px;font-weight:600;cursor:pointer;" onclick="openMo('flowMo')">编辑服务节点</button>
        </div>
      </div>
    </div>
    <!-- 服务内容/记录 -->
    <div class="accordion" data-acc-svc="svcRecord">
      <div class="accordion-header sticky-acc" onclick="toggleSvcAccordion('svcRecord')">
        <div class="acc-left"><span class="acc-icon">💬</span><span class="acc-title">服务内容/记录</span></div>
        <div style="display:flex;align-items:center;gap:10px;">
          <span class="card-count" id="st_record">0条</span>
          <span class="acc-arrow">▼</span>
        </div>
      </div>
      <div class="accordion-body">
        <div id="recListSummary" style="margin-bottom:8px;"></div>
        <div style="text-align:center;">
          <button style="background:linear-gradient(135deg,#2ecc71,#27ae60);color:#fff;border:none;border-radius:8px;padding:8px 20px;font-size:13px;font-weight:600;cursor:pointer;" onclick="openMo('recordMo')">编辑记录</button>
        </div>
      </div>
    </div>
  </div>'''
    
    html = html.replace(old_service_tab, new_service_tab)
    
    # ========== 改动3+4：签字确认tab改造 ==========
    # 服务说明移到签字确认tab，已保存/数据迁移移到顶部菜单
    old_sign_tab = '''  <!-- Tab 3: 签字确认 -->
  <div class="zone-panel" id="zonePanel_2">
    <div class="zone-section-title">确认与数据</div>
    <div class="sec-cards">
      <div class="form-card card-purple" onclick="openMo('signMo')"><span class="card-icon">✍️</span><span class="card-label">签字确认</span><div class="card-status" id="st_sign"></div></div>
      <div class="form-card card-blue" onclick="openMo('historyMo')"><span class="card-icon">📂</span><span class="card-label">已保存</span><span class="card-count" id="st_history">0条</span></div>
      <div class="form-card card-green full-width" onclick="openMo('dataMo')"><span class="card-icon">📦</span><span class="card-label">数据迁移</span><div class="card-status" id="st_data"></div></div>
    </div>
  </div>'''
    
    new_sign_tab = '''  <!-- Tab 3: 签字确认 -->
  <div class="zone-panel" id="zonePanel_2">
    <div class="zone-section-title">签字确认</div>
    
    <!-- 服务说明（从服务详情移过来） -->
    <div class="sign-section">
      <h4>⚠️ 服务说明</h4>
      <div class="sign-note">需尽快处理的事项及影响说明</div>
      <div id="impactSummary" style="font-size:13px;color:#4a5568;margin-bottom:8px;">
        <div style="margin-bottom:6px;"><span style="color:#718096;">紧急事项：</span><span id="impactUrgent">未填写</span></div>
        <div style="margin-bottom:6px;"><span style="color:#718096;">影响范围：</span><span id="impactScope">未选择</span></div>
        <div id="impactStopDate" style="display:none;"><span style="color:#718096;">停梯日期：</span><span id="impactStopDateVal"></span></div>
      </div>
      <div style="text-align:center;">
        <button style="background:linear-gradient(135deg,#34495e,#2c3e50);color:#fff;border:none;border-radius:8px;padding:8px 20px;font-size:13px;font-weight:600;cursor:pointer;" onclick="openMo('impactMo')">编辑服务说明</button>
      </div>
    </div>
    
    <!-- 签字确认区 -->
    <div class="sign-section">
      <h4>✍️ 签字确认</h4>
      <div class="sign-note">点击下方区域弹出手写签名</div>
      <div style="margin-bottom:10px;">
        <div style="font-size:13px;font-weight:bold;color:#555;margin-bottom:4px;">服务人签字</div>
        <div class="sd" id="sd1" onclick="openMo('signMo');setTimeout(function(){curSig=1;openSig();},100);"><span>点击签名</span></div>
      </div>
      <div>
        <div style="font-size:13px;font-weight:bold;color:#555;margin-bottom:4px;">被服务人员签字</div>
        <div class="sd" id="sd2" onclick="openMo('signMo');setTimeout(function(){curSig=2;openSig();},100);"><span>点击签名</span></div>
      </div>
      <div style="margin-top:8px;">
        <span class="card-status" id="st_sign" style="display:inline-block;vertical-align:middle;"></span>
        <span style="font-size:12px;color:#718096;margin-left:4px;">双方签字后生效</span>
      </div>
    </div>
  </div>'''
    
    html = html.replace(old_sign_tab, new_sign_tab)
    
    # ========== 改动5+6：tab滑动手势 + 动画修复 ==========
    # 替换旧的switchTab函数和添加滑动手势
    old_switch_tab = '''// ===== Tab 切换函数（全局暴露+滑动动画） =====
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
window.switchTab=switchTab;'''
    
    new_switch_tab = '''// ===== Tab 切换函数（滑动动画+手势支持） =====
var currentTabIndex = 0;
var _tabAnimating = false;

function switchTab(index){
  if(index<0||index>=3)return;
  if(index===currentTabIndex)return;
  if(_tabAnimating)return;
  _tabAnimating = true;
  
  var direction = index > currentTabIndex ? 'left' : 'right';
  var oldIndex = currentTabIndex;
  currentTabIndex = index;
  
  var tabs = document.querySelectorAll('.zone-tab');
  var panels = document.querySelectorAll('.zone-panel');
  var content = document.getElementById('zoneContent');
  
  // 更新tab激活态
  for(var i = 0; i < tabs.length; i++){
    tabs[i].classList.toggle('active', i === index);
  }
  
  // 滑动动画：旧面板滑出，新面板滑入
  if(content && panels.length >= 3){
    var oldPanel = panels[oldIndex];
    var newPanel = panels[index];
    
    // 设置动画初始状态
    content.classList.add('animating');
    newPanel.style.display = 'block';
    newPanel.style.position = 'absolute';
    newPanel.style.top = '0';
    newPanel.style.left = '0';
    newPanel.style.right = '0';
    newPanel.style.opacity = '0';
    
    if(direction === 'left'){
      newPanel.style.transform = 'translateX(100%)';
      newPanel.style.animation = 'slideInFromRight 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards';
      newPanel.style.webkitAnimation = 'slideInFromRight 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards';
      oldPanel.style.animation = 'slideOutToLeft 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards';
      oldPanel.style.webkitAnimation = 'slideOutToLeft 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards';
    } else {
      newPanel.style.transform = 'translateX(-100%)';
      newPanel.style.animation = 'slideInFromLeft 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards';
      newPanel.style.webkitAnimation = 'slideInFromLeft 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards';
      oldPanel.style.animation = 'slideOutToRight 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards';
      oldPanel.style.webkitAnimation = 'slideOutToRight 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards';
    }
    
    // 动画结束后清理
    setTimeout(function(){
      oldPanel.classList.remove('active');
      oldPanel.style.display = '';
      oldPanel.style.position = '';
      oldPanel.style.top = '';
      oldPanel.style.left = '';
      oldPanel.style.right = '';
      oldPanel.style.opacity = '';
      oldPanel.style.animation = '';
      oldPanel.style.webkitAnimation = '';
      oldPanel.style.transform = '';
      
      newPanel.classList.add('active');
      newPanel.style.display = '';
      newPanel.style.position = '';
      newPanel.style.top = '';
      newPanel.style.left = '';
      newPanel.style.right = '';
      newPanel.style.opacity = '';
      newPanel.style.animation = '';
      newPanel.style.webkitAnimation = '';
      newPanel.style.transform = '';
      
      content.classList.remove('animating');
      _tabAnimating = false;
    }, 320);
  } else {
    // fallback：直接切换
    for(var j = 0; j < panels.length; j++){
      panels[j].classList.toggle('active', j === index);
    }
    _tabAnimating = false;
  }
  
  // 滚动到tab栏位置
  var tabBar = document.getElementById('zoneTabs');
  if(tabBar){
    var tabTop = tabBar.getBoundingClientRect().top + window.scrollY;
    window.scrollTo({top: tabTop, behavior: 'smooth'});
  }
  
  // 刷新服务详情手风琴的汇总显示
  if(index === 1){
    setTimeout(updateSvcAccordionSummary, 100);
  }
  if(index === 2){
    setTimeout(updateImpactSummary, 100);
  }
}
window.switchTab = switchTab;

// ===== 服务详情手风琴切换 =====
var currentSvcAccordion = 'svcCategory';
function toggleSvcAccordion(name){
  var items = document.querySelectorAll('#zonePanel_1 .accordion');
  var target = null;
  items.forEach(function(item){
    if(item.getAttribute('data-acc-svc') === name){
      target = item;
    }
  });
  if(!target) return;
  var isActive = target.classList.contains('active');
  items.forEach(function(item){ item.classList.remove('active'); });
  if(!isActive){
    target.classList.add('active');
    currentSvcAccordion = name;
  } else {
    currentSvcAccordion = '';
  }
  updateBtnStatus();
}
window.toggleSvcAccordion = toggleSvcAccordion;

// 更新服务详情手风琴的汇总显示
function updateSvcAccordionSummary(){
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
}

// 更新签字确认tab的服务说明汇总
function updateImpactSummary(){
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
}

// ===== 顶部菜单控制 =====
function toggleHeaderMenu(){
  var dropdown = document.getElementById('headerDropdown');
  if(dropdown){
    dropdown.classList.toggle('show');
  }
}
function closeHeaderMenu(){
  var dropdown = document.getElementById('headerDropdown');
  if(dropdown){
    dropdown.classList.remove('show');
  }
}
document.addEventListener('click', function(e){
  var btn = document.querySelector('.header-more-btn');
  var dropdown = document.getElementById('headerDropdown');
  if(dropdown && btn){
    if(!dropdown.contains(e.target) && !btn.contains(e.target)){
      dropdown.classList.remove('show');
    }
  }
});
window.toggleHeaderMenu = toggleHeaderMenu;
window.closeHeaderMenu = closeHeaderMenu;

// ===== 返回列表页 =====
function goBackToList(){
  // 尝试返回列表页，如果有list页面的话
  if(window.history.length > 1 && document.referrer && document.referrer.indexOf('weite-service-beta.html') >= 0){
    window.history.back();
  } else {
    window.location.href = 'weite-service-beta.html';
  }
}
window.goBackToList = goBackToList;

// ===== Tab左右滑动手势 =====
(function(){
  var touchStartX = 0;
  var touchStartY = 0;
  var touchStartTime = 0;
  var isHorizontalSwipe = false;
  var SWIPE_THRESHOLD_RATIO = 0.2;
  var MAX_VERTICAL_RATIO = 0.5;
  var MAX_DURATION = 500;
  var LOCK_THRESHOLD = 8;

  function handleTouchStart(e){
    if(e.touches.length !== 1) return;
    // 检查是否在弹窗内
    var inModal = false;
    var modals = document.querySelectorAll('.mo');
    for(var i = 0; i < modals.length; i++){
      if(modals[i].style.display === 'block'){
        inModal = true;
        break;
      }
    }
    if(inModal) return;
    // 检查是否在签名弹窗内
    if(document.getElementById('sigMo') && document.getElementById('sigMo').style.display === 'block') return;
    // 检查是否在PDF预览内
    if(document.getElementById('pdfPreviewMo') && document.getElementById('pdfPreviewMo').style.display === 'block') return;
    
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
    touchStartTime = Date.now();
    isHorizontalSwipe = false;
  }

  function handleTouchMove(e){
    if(e.touches.length !== 1) return;
    var deltaX = e.touches[0].clientX - touchStartX;
    var deltaY = e.touches[0].clientY - touchStartY;
    
    if(isHorizontalSwipe){
      e.preventDefault();
      return;
    }
    
    if(Math.abs(deltaX) > LOCK_THRESHOLD){
      if(Math.abs(deltaX) > Math.abs(deltaY) * 1.5){
        // 检查是否在可横向滚动的元素内
        var target = e.target;
        var inScrollable = false;
        while(target && target !== document.body){
          var style = window.getComputedStyle(target);
          var overflowX = style.overflowX;
          if((overflowX === 'auto' || overflowX === 'scroll') && target.scrollWidth > target.clientWidth){
            inScrollable = true;
            break;
          }
          target = target.parentElement;
        }
        if(!inScrollable){
          isHorizontalSwipe = true;
          e.preventDefault();
        }
      }
    }
  }

  function handleTouchEnd(e){
    if(e.changedTouches.length !== 1) return;
    if(!isHorizontalSwipe) return;
    
    var endX = e.changedTouches[0].clientX;
    var endY = e.changedTouches[0].clientY;
    var deltaX = endX - touchStartX;
    var deltaY = endY - touchStartY;
    var duration = Date.now() - touchStartTime;
    
    var screenWidth = window.innerWidth;
    var threshold = screenWidth * SWIPE_THRESHOLD_RATIO;
    
    if(Math.abs(deltaX) < threshold) return;
    if(Math.abs(deltaY) > Math.abs(deltaX) * MAX_VERTICAL_RATIO) return;
    if(duration > MAX_DURATION) return;
    
    // 右滑 → 上一个tab
    if(deltaX > 0){
      if(currentTabIndex > 0){
        switchTab(currentTabIndex - 1);
      } else {
        // 已经在第一个tab，右滑返回列表
        goBackToList();
      }
    }
    // 左滑 → 下一个tab
    else {
      if(currentTabIndex < 2){
        switchTab(currentTabIndex + 1);
      }
    }
  }

  document.addEventListener('touchstart', handleTouchStart, {passive: true});
  document.addEventListener('touchmove', handleTouchMove, {passive: false});
  document.addEventListener('touchend', handleTouchEnd, {passive: true});
})();'''
    
    html = html.replace(old_switch_tab, new_switch_tab)
    
    # ========== 手风琴吸顶JS逻辑 ==========
    # 在手风琴切换后更新吸顶位置
    old_toggle_acc = '''// ===== 手风琴切换函数 =====
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
window.toggleAccordion=toggleAccordion;'''
    
    new_toggle_acc = '''// ===== 手风琴切换函数 =====
var currentAccordion = 'basic';
function toggleAccordion(name){
  var items = document.querySelectorAll('#zonePanel_0 .accordion');
  var target = null;
  items.forEach(function(item){
    if(item.getAttribute('data-acc') === name){
      target = item;
    }
  });
  if(!target) return;
  var isActive = target.classList.contains('active');
  items.forEach(function(item){ item.classList.remove('active'); });
  if(!isActive){
    target.classList.add('active');
    currentAccordion = name;
    // 滚动到手风琴标题位置（确保吸顶效果正确）
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
    }, 50);
  } else {
    currentAccordion = '';
  }
  updateBtnStatus();
}
window.toggleAccordion = toggleAccordion;'''
    
    html = html.replace(old_toggle_acc, new_toggle_acc)
    
    # ========== 修改updateBtnStatus - 增加服务详情手风琴汇总刷新 ==========
    # 在updateBtnStatus末尾添加刷新汇总的调用
    old_update_end = "  // 更新进度条\n  var pct=Math.round(filled/total*100);\n  var pctEl=document.getElementById('progressPct');\n  var fillEl=document.getElementById('progressFill');\n  if(pctEl)pctEl.textContent=pct+'%';\n  if(fillEl)fillEl.style.width=pct+'%';\n}"
    
    new_update_end = """  // 更新进度条
  var pct=Math.round(filled/total*100);
  var pctEl=document.getElementById('progressPct');
  var fillEl=document.getElementById('progressFill');
  if(pctEl)pctEl.textContent=pct+'%';
  if(fillEl)fillEl.style.width=pct+'%';
  // 刷新服务详情手风琴汇总
  if(typeof updateSvcAccordionSummary === 'function' && currentTabIndex === 1){
    updateSvcAccordionSummary();
  }
  // 刷新服务说明汇总
  if(typeof updateImpactSummary === 'function' && currentTabIndex === 2){
    updateImpactSummary();
  }
}"""
    
    html = html.replace(old_update_end, new_update_end)
    
    # ========== 修改签字弹窗的入口 ==========
    # 签字确认tab中的sd1和sd2点击直接打开签名（不通过signMo）
    # 保留signMo弹窗兼容，但主要点击直接打开签名
    
    # 修改标题
    html = html.replace('<title>威特技术服务单</title>', '<title>威特技术服务单 - 详情</title>')
    
    write_file(DETAIL_FILE, html)
    print('  详情页创建完成')
    return html


def build_list_page():
    """创建列表首页 - 实现改动7"""
    
    # 从原文件提取IndexedDB封装和存储缓存层
    src = read_file(SRC_FILE)
    
    # 提取IDB封装部分
    idb_start = src.find('// ===== IndexedDB 封装')
    idb_end = src.find('// ===== 缓存层结束 =====') + len('// ===== 缓存层结束 =====')
    idb_code = src[idb_start:idb_end]
    
    # 提取PWA manifest部分
    pwa_start = src.find('// PWA manifest & service worker')
    pwa_end = src.find('})();\n</script>', pwa_start) + len('})();')
    pwa_code = src[pwa_start:pwa_end]
    
    # 提取logo base64
    import re
    logo_match = re.search(r'<img class="logo-img" src="(data:image/webp;base64,[^"]+)"', src)
    logo_base64 = logo_match.group(1) if logo_match else ''
    
    # 构建列表页
    list_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="威特服务单">
<meta name="theme-color" content="#667eea">
<title>威特技术服务单</title>
<link rel="apple-touch-icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg" viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='20' fill='%231a3a6b'/%3E%3Ctext x='50' y='42' font-family='Arial' font-size='28' font-weight='900' text-anchor='middle' fill='white'%3EVEITE%3C/text%3E%3Ctext x='50' y='72' font-family='serif' font-size='16' font-weight='800' text-anchor='middle' fill='%23e63946'%3E电梯%3C/text%3E%3C/svg%3E">
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
</script>
<script>
{idb_code}

{pwa_code}
</script>
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','微软雅黑',sans-serif;background:#f5f7fa;padding-bottom:80px;-webkit-overflow-scrolling:touch;min-height:100vh;}}

/* 顶部Header */
.header{{padding:12px 16px 10px;background:#fff;position:sticky;top:0;z-index:50;box-shadow:0 2px 8px rgba(0,0,0,.06);}}
.logo-area{{display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:8px;}}
.logo-img{{height:36px;width:auto;display:block;}}
.logo-elev{{font-size:22px;font-weight:900;color:#0d2137;letter-spacing:0px;font-family:'PingFang SC','Heiti SC','Microsoft YaHei',sans-serif;line-height:1;}}
.header-title{{font-size:15px;font-weight:700;color:#1a3a6b;text-align:center;letter-spacing:3px;}}
.header-subtitle{{font-size:11px;color:#718096;text-align:center;margin-top:2px;letter-spacing:2px;}}

/* 统计卡片 */
.stats-bar{{background:#fff;padding:12px 16px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;border-bottom:1px solid #edf2f7;}}
.stat-item{{text-align:center;padding:8px;background:linear-gradient(135deg,#f8f9ff,#f5f3ff);border-radius:10px;}}
.stat-num{{font-size:20px;font-weight:800;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}}
.stat-label{{font-size:11px;color:#718096;margin-top:2px;}}

/* 新建按钮 */
.new-btn-bar{{padding:12px 16px;}}
.new-btn{{width:100%;padding:14px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;border:none;border-radius:12px;font-size:15px;font-weight:700;cursor:pointer;box-shadow:0 4px 12px rgba(102,126,234,.3);letter-spacing:2px;-webkit-tap-highlight-color:transparent;}}
.new-btn:active{{transform:translateY(1px);box-shadow:0 2px 6px rgba(102,126,234,.3);}}

/* 列表区 */
.list-section{{padding:0 16px;}}
.list-section-title{{font-size:13px;font-weight:700;color:#718096;padding:12px 4px 8px;letter-spacing:1px;display:flex;justify-content:space-between;align-items:center;}}
.list-count{{font-size:12px;color:#a0aec0;font-weight:400;}}

/* 记录卡片 */
.service-card{{background:#fff;border-radius:14px;padding:14px 16px;margin-bottom:12px;border:1.5px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,.04);position:relative;transition:all .2s ease;}}
.service-card:active{{transform:scale(.99);box-shadow:0 1px 4px rgba(0,0,0,.06);}}
.card-top{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;}}
.card-project{{font-size:15px;font-weight:700;color:#2d3748;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-right:8px;}}
.card-date-tag{{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;font-size:10px;padding:3px 8px;border-radius:10px;font-weight:600;flex-shrink:0;}}
.card-meta{{display:grid;grid-template-columns:1fr 1fr;gap:4px 12px;margin-bottom:10px;}}
.meta-item{{font-size:12px;color:#4a5568;display:flex;align-items:center;gap:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
.meta-label{{color:#a0aec0;flex-shrink:0;}}
.meta-value{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
.card-tags{{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:10px;}}
.tag{{font-size:10px;padding:2px 8px;border-radius:8px;background:#edf2f7;color:#718096;font-weight:500;}}
.tag-construct{{background:#e6fffa;color:#234e52;}}
.tag-service{{background:#fefcbf;color:#744210;}}
.card-btns{{display:flex;gap:8px;padding-top:10px;border-top:1px solid #edf2f7;}}
.card-btn{{flex:1;padding:8px 0;border:none;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;-webkit-tap-highlight-color:transparent;}}
.btn-view{{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;}}
.btn-print{{background:linear-gradient(135deg,#27ae60,#2ecc71);color:#fff;}}
.btn-delete{{background:#fff5f5;color:#c53030;border:1px solid #fed7d7;}}

/* 空状态 */
.empty-state{{text-align:center;padding:60px 20px;color:#a0aec0;}}
.empty-icon{{font-size:56px;margin-bottom:16px;opacity:.5;}}
.empty-title{{font-size:15px;font-weight:600;color:#718096;margin-bottom:6px;}}
.empty-desc{{font-size:12px;color:#a0aec0;}}

/* 底部操作栏 */
.bottom-bar{{position:fixed;bottom:0;left:0;right:0;background:#fff;padding:10px 16px;box-shadow:0 -2px 8px rgba(0,0,0,.08);z-index:100;display:flex;gap:10px;}}
.bottom-bar .btn{{flex:1;padding:12px;border-radius:10px;font-size:14px;font-weight:600;cursor:pointer;border:none;-webkit-tap-highlight-color:transparent;}}
.btn-export{{background:#f7fafc;color:#27ae60;border:1.5px solid #9ae6b4;}}
.btn-import{{background:#f7fafc;color:#2980b9;border:1.5px solid #90cdf4;}}

/* Toast */
.toast{{display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,.75);color:#fff;padding:12px 24px;border-radius:8px;font-size:14px;z-index:9999;}}

/* 新手引导 */
.guide-overlay{{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.7);z-index:10000;display:flex;align-items:center;justify-content:center;padding:20px;}}
.guide-box{{background:#fff;border-radius:16px;padding:24px 20px;max-width:340px;width:100%;box-shadow:0 10px 40px rgba(0,0,0,.3);}}
.guide-box h2{{font-size:18px;font-weight:800;color:#2d3748;margin-bottom:16px;text-align:center;}}
.guide-section{{margin-bottom:16px;padding:12px;background:#f7fafc;border-radius:10px;border-left:4px solid #667eea;}}
.guide-section h3{{font-size:14px;font-weight:700;color:#4a5568;margin-bottom:6px;}}
.guide-section p{{font-size:12px;color:#718096;line-height:1.6;}}
.guide-section .step{{display:flex;align-items:flex-start;gap:8px;margin-bottom:4px;}}
.guide-section .step-num{{background:#667eea;color:#fff;border-radius:50%;width:20px;height:20px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0;margin-top:1px;}}
.guide-close-btn{{width:100%;padding:14px;border:none;border-radius:10px;font-size:15px;font-weight:700;cursor:pointer;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;margin-top:8px;}}

/* 确认弹窗 */
.confirm-mask{{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.5);z-index:9999;align-items:center;justify-content:center;padding:30px;}}
.confirm-mask.show{{display:flex;}}
.confirm-box{{background:#fff;border-radius:12px;padding:20px;max-width:300px;width:100%;text-align:center;}}
.confirm-box h3{{font-size:16px;font-weight:700;color:#2d3748;margin-bottom:8px;}}
.confirm-box p{{font-size:13px;color:#718096;margin-bottom:16px;line-height:1.5;}}
.confirm-btns{{display:flex;gap:10px;}}
.confirm-cancel{{flex:1;padding:10px;border:1px solid #e2e8f0;border-radius:8px;background:#f7fafc;color:#718096;font-size:14px;cursor:pointer;}}
.confirm-ok{{flex:1;padding:10px;border:none;border-radius:8px;background:#e53e3e;color:#fff;font-size:14px;cursor:pointer;}}

@media(max-width:360px){{
  .card-project{{font-size:14px;}}
  .stat-num{{font-size:18px;}}
}}
</style>
</head>
<body>

<!-- 顶部Header -->
<div class="header">
  <div class="logo-area">
    <img class="logo-img" src="{logo_base64}" alt="WEITE">
    <span class="logo-elev">电梯</span>
  </div>
  <div class="header-title">技术服务单</div>
  <div class="header-subtitle">WEITE SERVICE</div>
</div>

<!-- 统计卡片 -->
<div class="stats-bar">
  <div class="stat-item">
    <div class="stat-num" id="statTotal">0</div>
    <div class="stat-label">总记录</div>
  </div>
  <div class="stat-item">
    <div class="stat-num" id="statMonth">0</div>
    <div class="stat-label">本月</div>
  </div>
  <div class="stat-item">
    <div class="stat-num" id="statSigned">0</div>
    <div class="stat-label">已签字</div>
  </div>
</div>

<!-- 新建按钮 -->
<div class="new-btn-bar">
  <button class="new-btn" onclick="goToDetail()">+ 新建服务单</button>
</div>

<!-- 列表区 -->
<div class="list-section">
  <div class="list-section-title">
    <span>服务记录</span>
    <span class="list-count" id="listCount">共 0 条</span>
  </div>
  <div id="serviceList"></div>
</div>

<!-- 底部操作栏 -->
<div class="bottom-bar">
  <button class="btn btn-export" onclick="exportData()">📤 导出</button>
  <button class="btn btn-import" onclick="importData()">📥 导入</button>
  <input type="file" id="importFileInput" accept=".json" style="display:none;">
</div>

<div class="toast" id="toast"></div>

<!-- 确认删除弹窗 -->
<div class="confirm-mask" id="confirmMask">
  <div class="confirm-box">
    <h3 id="confirmTitle">确认删除</h3>
    <p id="confirmMsg">确定要删除这条记录吗？</p>
    <div class="confirm-btns">
      <button class="confirm-cancel" onclick="hideConfirm()">取消</button>
      <button class="confirm-ok" id="confirmOkBtn">删除</button>
    </div>
  </div>
</div>

<script>
(function(){{
'use strict';

// ============ 工具函数 ============
function showToast(msg){{
  var t = document.getElementById('toast');
  t.textContent = msg;
  t.style.display = 'block';
  setTimeout(function(){{ t.style.display = 'none'; }}, 2000);
}}

// ============ 跳转详情页 ============
function goToDetail(idx){{
  if(idx !== undefined && idx >= 0){{
    window.location.href = 'weite-service-beta-detail.html?idx=' + idx;
  }} else {{
    window.location.href = 'weite-service-beta-detail.html';
  }}
}}

// ============ 导出数据 ============
function exportData(){{
  var list = _wtListCache;
  if(!list.length){{
    showToast('暂无记录可导出');
    return;
  }}
  var blob = new Blob([JSON.stringify(list)], {{type:'application/json'}});
  var blobUrl = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = blobUrl;
  a.download = '威特服务单记录_' + new Date().toISOString().slice(0,10) + '.json';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(blobUrl);
  showToast('已导出' + list.length + '条记录');
}}

// ============ 导入数据 ============
function importData(){{
  document.getElementById('importFileInput').click();
}}

document.getElementById('importFileInput').addEventListener('change', function(e){{
  var file = e.target.files[0];
  if(!file) return;
  var reader = new FileReader();
  reader.onload = function(ev){{
    try{{
      var data = JSON.parse(ev.target.result);
      if(!Array.isArray(data)) throw new Error('格式错误');
      var existing = _wtListCache;
      var added = 0;
      data.forEach(function(item){{
        // 简单去重：服务时间+项目名
        var dKey = (item.serviceTime || '') + '_' + (item.projectName || '');
        var dup = existing.some(function(ex){{
          var eKey = (ex.serviceTime || '') + '_' + (ex.projectName || '');
          return eKey === dKey;
        }});
        if(!dup){{
          existing.unshift(item);
          added++;
        }}
      }});
      if(added > 0){{
        _wtListCache = existing;
        _saveWtListCache();
        renderList();
        showToast('成功导入' + added + '条记录');
      }} else {{
        showToast('没有新记录（已全部存在）');
      }}
    }} catch(err){{
      showToast('导入失败：文件格式错误');
    }}
  }};
  reader.readAsText(file);
  e.target.value = '';
}});

// ============ 删除确认 ============
var _pendingDeleteIdx = -1;
function showConfirm(title, msg, onOk){{
  document.getElementById('confirmTitle').textContent = title;
  document.getElementById('confirmMsg').textContent = msg;
  document.getElementById('confirmMask').classList.add('show');
  document.getElementById('confirmOkBtn').onclick = function(){{
    hideConfirm();
    if(onOk) onOk();
  }};
}}
function hideConfirm(){{
  document.getElementById('confirmMask').classList.remove('show');
  _pendingDeleteIdx = -1;
}}

function deleteRecord(idx){{
  var list = _wtListCache;
  if(!list[idx]) return;
  var projName = list[idx].projectName || '未命名';
  showConfirm('确认删除', '确定要删除「' + projName + '」这条记录吗？', function(){{
    list.splice(idx, 1);
    _wtListCache = list;
    _saveWtListCache();
    renderList();
    showToast('已删除');
  }});
}}

// ============ 打印单条记录 ============
function printRecord(idx){{
  var list = _wtListCache;
  if(!list[idx]) return;
  // 跳转到详情页并自动打印
  window.location.href = 'weite-service-beta-detail.html?idx=' + idx + '&action=print';
}}

// ============ 渲染列表 ============
function renderList(){{
  var list = _wtListCache || [];
  var container = document.getElementById('serviceList');
  var countEl = document.getElementById('listCount');
  var statTotal = document.getElementById('statTotal');
  var statMonth = document.getElementById('statMonth');
  var statSigned = document.getElementById('statSigned');
  
  countEl.textContent = '共 ' + list.length + ' 条';
  statTotal.textContent = list.length;
  
  // 本月数
  var now = new Date();
  var yearMonth = now.getFullYear() + '-' + String(now.getMonth()+1).padStart(2,'0');
  var monthCount = 0;
  var signedCount = 0;
  
  list.forEach(function(d){{
    if(d.serviceTime && d.serviceTime.indexOf(yearMonth) === 0){{
      monthCount++;
    }}
    if(d.sig1 && d.sig2){{
      signedCount++;
    }}
  }});
  
  statMonth.textContent = monthCount;
  statSigned.textContent = signedCount;
  
  if(list.length === 0){{
    container.innerHTML = 
      '<div class="empty-state">' +
        '<div class="empty-icon">📋</div>' +
        '<div class="empty-title">暂无服务记录</div>' +
        '<div class="empty-desc">点击上方按钮新建第一条服务单</div>' +
      '</div>';
    return;
  }}
  
  var html = '';
  list.forEach(function(d, i){{
    var projName = d.projectName || '未命名项目';
    var serviceDate = d.serviceTime ? d.serviceTime.split('T')[0] : '未填写';
    var construct = (d.construction && d.construction.length) ? d.construction.join('、') : '未分类';
    var serviceTypes = [];
    ['preSale','during','afterSale','visit'].forEach(function(key){{
      if(d[key] && d[key].length){{
        d[key].forEach(function(v){{
          if(v !== '其他') serviceTypes.push(v);
        }});
      }}
    }});
    var serviceStr = serviceTypes.length > 0 ? serviceTypes.slice(0, 3).join('、') : '未选择';
    var contact = d.siteContact || d.servicePerson || '未填写';
    var phone = d.sitePhone || d.servicePhone || '';
    var hasSig = d.sig1 && d.sig2;
    
    html += '<div class="service-card">';
    html += '<div class="card-top">';
    html += '<div class="card-project" title="' + projName + '">' + projName + '</div>';
    html += '<div class="card-date-tag">' + serviceDate + '</div>';
    html += '</div>';
    
    html += '<div class="card-meta">';
    html += '<div class="meta-item"><span class="meta-label">施工：</span><span class="meta-value" title="' + construct + '">' + construct + '</span></div>';
    html += '<div class="meta-item"><span class="meta-label">联系人：</span><span class="meta-value" title="' + contact + '">' + contact + (phone ? ' ' + phone : '') + '</span></div>';
    html += '</div>';
    
    html += '<div class="card-tags">';
    if(serviceTypes.length > 0){{
      serviceTypes.slice(0, 4).forEach(function(s){{
        html += '<span class="tag tag-service">' + s + '</span>';
      }});
    }}
    if(hasSig){{
      html += '<span class="tag" style="background:#c6f6d5;color:#22543d;">✓ 已签字</span>';
    }}
    html += '</div>';
    
    html += '<div class="card-btns">';
    html += '<button class="card-btn btn-view" onclick="goToDetail(' + i + ')">查看</button>';
    html += '<button class="card-btn btn-print" onclick="printRecord(' + i + ')">打印</button>';
    html += '<button class="card-btn btn-delete" onclick="deleteRecord(' + i + ')">删除</button>';
    html += '</div>';
    html += '</div>';
  }});
  
  container.innerHTML = html;
}}

// ============ 初始化 ============
function init(){{
  _initStorage(function(){{
    renderList();
  }});
  
  // 页面可见时刷新（从详情页返回时）
  document.addEventListener('visibilitychange', function(){{
    if(!document.hidden){{
      _loadCacheFromDB(renderList);
    }}
  }});
}}

// 暴露全局函数
window.goToDetail = goToDetail;
window.exportData = exportData;
window.importData = importData;
window.deleteRecord = deleteRecord;
window.printRecord = printRecord;
window.showConfirm = showConfirm;
window.hideConfirm = hideConfirm;

init();

// 首次打开提示添加到桌面
(function(){{
  if(_wtGuideShownCache) return;
  var isStandalone = window.matchMedia('(display-mode:standalone)').matches || window.navigator.standalone;
  if(isStandalone){{ _saveGuideShown('1'); return; }}
  var overlay = document.createElement('div');
  overlay.className = 'guide-overlay';
  overlay.innerHTML = 
    '<div class="guide-box">' +
      '<h2>威特技术服务单</h2>' +
      '<div class="guide-section">' +
        '<h3>快速开始</h3>' +
        '<div class="step"><span class="step-num">1</span><p>点击<b>「新建服务单」</b>开始填写</p></div>' +
        '<div class="step"><span class="step-num">2</span><p>填写完成后点击<b>保存</b></p></div>' +
        '<div class="step"><span class="step-num">3</span><p>已保存的记录都在这里</p></div>' +
      '</div>' +
      '<div class="guide-section" style="border-left-color:#27ae60;">' +
        '<h3>添加到桌面</h3>' +
        '<div class="step"><span class="step-num" style="background:#27ae60;">📱</span><p>添加到主屏幕，下次直接打开</p></div>' +
      '</div>' +
      '<button class="guide-close-btn">开始使用</button>' +
    '</div>';
  document.body.appendChild(overlay);
  overlay.querySelector('.guide-close-btn').addEventListener('click', function(){{
    overlay.remove();
    _saveGuideShown('1');
  }});
}})();

}})();
</script>
</body>
</html>
'''
    
    write_file(LIST_FILE, list_html)
    print('  列表页创建完成')
    return list_html


def add_detail_url_params_support():
    """给详情页添加URL参数支持（从列表页跳转时自动加载数据）"""
    html = read_file(DETAIL_FILE)
    
    # 在_appStartInit函数中添加URL参数处理
    old_app_start = '''function _appStartInit() {
  _initStorage(function() {
    updateBtnStatus();
    // 如果有renderList，刷新列表显示
    if (typeof renderList === 'function') { renderList(); }
  });
}'''
    
    new_app_start = '''function _appStartInit() {
  _initStorage(function() {
    updateBtnStatus();
    
    // 处理URL参数：从列表页跳转过来
    var params = new URLSearchParams(window.location.search);
    var idx = params.get('idx');
    var action = params.get('action');
    
    if(idx !== null && idx !== '' && !isNaN(parseInt(idx))){
      var i = parseInt(idx);
      if(i >= 0 && i < _wtListCache.length){
        loadRec(i);
        // 如果是打印操作，自动触发打印
        if(action === 'print'){
          setTimeout(function(){
            genPdf(_wtListCache[i]);
          }, 800);
        }
      }
    }
    
    // 如果有renderList，刷新列表显示
    if (typeof renderList === 'function') { renderList(); }
  });
}'''
    
    html = html.replace(old_app_start, new_app_start)
    
    write_file(DETAIL_FILE, html)
    print('  详情页URL参数支持已添加')


def verify_js_syntax():
    """验证JS语法"""
    import subprocess
    
    files = [LIST_FILE, DETAIL_FILE]
    all_ok = True
    
    for fpath in files:
        print(f'\n  验证 {os.path.basename(fpath)}...')
        
        # 提取所有<script>标签内的内容
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 用正则提取script内容
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
        
        total_scripts = len(scripts)
        passed = 0
        
        for i, script in enumerate(scripts):
            # 跳过空脚本和外部src脚本
            if not script.strip() or script.strip().startswith('<!--'):
                passed += 1
                continue
            
            # 写入临时文件检查
            tmp_file = f'/tmp/check_script_{os.path.basename(fpath)}_{i}.js'
            with open(tmp_file, 'w', encoding='utf-8') as f:
                f.write(script)
            
            try:
                result = subprocess.run(
                    ['node', '--check', tmp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    passed += 1
                else:
                    print(f'    ❌ 脚本{i+1}/{total_scripts} 语法错误:')
                    print(f'       {result.stderr[:200]}')
                    all_ok = False
            except Exception as e:
                print(f'    ⚠️  脚本{i+1}/{total_scripts} 检查失败: {e}')
                all_ok = False
            
            # 清理临时文件
            try:
                os.remove(tmp_file)
            except:
                pass
        
        print(f'    脚本 {passed}/{total_scripts} 通过')
    
    return all_ok


def main():
    print('=' * 60)
    print('技术服务单体验版第二波优化')
    print('=' * 60)
    
    # 备份原文件
    backup_file = SRC_FILE + '.bak_v2_before_upgrade'
    if not os.path.exists(backup_file):
        shutil.copy2(SRC_FILE, backup_file)
        print(f'\n✅ 已备份原文件到: {os.path.basename(backup_file)}')
    
    # 1. 创建详情页
    print('\n📝 步骤1: 创建详情页 (weite-service-beta-detail.html)')
    build_detail_page()
    
    # 2. 添加URL参数支持
    print('\n📝 步骤2: 添加详情页URL参数支持')
    add_detail_url_params_support()
    
    # 3. 创建列表页
    print('\n📝 步骤3: 创建列表页 (weite-service-beta.html)')
    build_list_page()
    
    # 4. 验证JS语法
    print('\n🔍 步骤4: 验证JS语法')
    js_ok = verify_js_syntax()
    
    if js_ok:
        print('\n✅ 所有JS语法检查通过!')
    else:
        print('\n❌ JS语法检查有错误，请修复!')
        return False
    
    # 5. 检查关键字段ID是否保留
    print('\n🔍 步骤5: 检查关键字段ID兼容性')
    detail_html = read_file(DETAIL_FILE)
    required_ids = [
        'f1', 'f2', 'f3', 'f5', 'f8', 'f9', 'f10', 'f11', 'f12', 'f13', 'f14',
        'sd1', 'sd2', 'locDisplay', 'elevBox', 'recBox',
        'cgBuild', 'cgFlow', 'cgImpact',
        'svcCats', 'p1', 'c1', 'x1',
        'preSaleOther', 'duringOther', 'afterSaleOther', 'visitOther',
        'saveBtn', 'clearBtn', 'progressPct', 'progressFill'
    ]
    missing = []
    for fid in required_ids:
        if f'id="{fid}"' not in detail_html:
            missing.append(fid)
    
    if missing:
        print(f'  ❌ 缺少字段ID: {missing}')
        return False
    else:
        print(f'  ✅ 全部 {len(required_ids)} 个关键字段ID保留')
    
    # 6. 检查数据结构兼容性
    print('\n🔍 步骤6: 检查数据结构兼容性')
    collect_keywords = ['initiator', 'serviceCount', 'projectName', 'elevators',
                       'province', 'city', 'county', 'detailAddr',
                       'siteContact', 'sitePhone', 'servicePerson', 'servicePhone',
                       'serviceTime', 'construction', 'preSale', 'during', 'afterSale',
                       'visit', 'flowTo', 'impact', 'urgentItems', 'stopDate',
                       'sig1', 'sig2', 'records', 'savedAt']
    missing_data = []
    for kw in collect_keywords:
        if kw not in detail_html:
            missing_data.append(kw)
    
    if missing_data:
        print(f'  ⚠️  可能缺少的数据字段: {missing_data}')
    else:
        print(f'  ✅ 全部 {len(collect_keywords)} 个数据字段保留')
    
    print('\n' + '=' * 60)
    print('✅ 全部7项改动已完成!')
    print('=' * 60)
    print(f'  列表页: weite-service-beta.html')
    print(f'  详情页: weite-service-beta-detail.html')
    print(f'  备份: weite-service-beta.html.bak_v2_before_upgrade')
    print()
    
    return True


if __name__ == '__main__':
    success = main()
    if not success:
        exit(1)
