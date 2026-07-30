#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
weite-service-beta-detail.html 第三波优化脚本
6项改动批量处理
"""

import re

FILE_PATH = '/app/data/所有对话/主对话/weite-pro-temp/weite-service-beta-detail.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

print(f"原始文件长度: {len(html)}")

# ============================================================
# 第3、6项：顶部布局改为fixed定位，解决上下滚动和左右滑动时顶部乱动
# ============================================================

# 1. 修改 .header 从 sticky 改为 fixed
old_header_css = ".header{padding:8px 16px 6px;background:#fff;position:sticky;top:0;z-index:50;}"
new_header_css = ".header{padding:8px 16px 6px;background:#fff;position:fixed;top:0;left:0;right:0;z-index:50;-webkit-backface-visibility:hidden;will-change:transform;}"
html = html.replace(old_header_css, new_header_css)
print("✓ header改为fixed")

# 2. 修改 .progress-container 从 sticky 改为 fixed
old_progress_css = ".progress-container{padding:12px 16px 10px;background:#fff;position:sticky;top:55px;z-index:49;border-bottom:1px solid #edf2f7;}"
new_progress_css = ".progress-container{padding:12px 16px 10px;background:#fff;position:fixed;top:55px;left:0;right:0;z-index:49;border-bottom:1px solid #edf2f7;-webkit-backface-visibility:hidden;will-change:transform;}"
html = html.replace(old_progress_css, new_progress_css)
print("✓ progress-container改为fixed")

# 3. 修改 .zone-tabs 从 sticky 改为 fixed
old_tabs_css = """.zone-tabs{display:flex;gap:0;padding:0 12px;background:#fff;overflow-x:auto;flex-shrink:0;
  -webkit-overflow-scrolling:touch;border-bottom:2px solid #edf2f7;position:sticky;top:101px;z-index:48;
  -webkit-backface-visibility:hidden;will-change:transform;}"""
new_tabs_css = """.zone-tabs{display:flex;gap:0;padding:0 12px;background:#fff;overflow-x:auto;flex-shrink:0;
  -webkit-overflow-scrolling:touch;border-bottom:2px solid #edf2f7;position:fixed;top:101px;left:0;right:0;z-index:48;
  -webkit-backface-visibility:hidden;will-change:transform;}"""
html = html.replace(old_tabs_css, new_tabs_css)
print("✓ zone-tabs改为fixed")

# 4. 给body加padding-top，为固定头部腾出空间
old_body_css = "body{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','微软雅黑',sans-serif;background:#f5f7fa;padding-bottom:70px;-webkit-overflow-scrolling:touch;}"
new_body_css = "body{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','微软雅黑',sans-serif;background:#f5f7fa;padding-top:145px;padding-bottom:70px;-webkit-overflow-scrolling:touch;}"
html = html.replace(old_body_css, new_body_css)
print("✓ body增加padding-top:145px")

# 5. 修改zone-content的样式，去掉原来的min-height问题
# 找到第一个.zone-content定义并修改
old_zone_content1 = ".zone-content{position:relative;overflow:hidden;min-height:60vh;}"
new_zone_content1 = ".zone-content{position:relative;overflow:hidden;min-height:calc(100vh - 215px);}"
# 有两个重复定义，都替换
html = html.replace(old_zone_content1, new_zone_content1)
print("✓ zone-content调整min-height")

# ============================================================
# 第2项：修复手风琴标题吸顶位置
# ============================================================

# 修改sticky-acc的top值，从145px改为大约tab栏底部位置
# 因为tab栏是fixed top:101px，高度约44px，所以底部约145px
# 但由于body有padding-top:145px，内容从145px开始，所以sticky相对于滚动位置
# 实际上sticky元素在内容区内，内容区顶部在页面145px位置
# 所以sticky的top应该设为 tab栏底部 - padding-top = 0？不对
# 重新思考：body有padding-top:145px，内容从y=145px开始
# 滚动时，内容向上移动，当手风琴标题到达tab栏底部时（页面y=145px处）应该吸顶
# 但sticky的top是相对于滚动容器（body）的
# 由于body是滚动容器，sticky元素的top值是距离视口顶部的距离
# tab栏底部在视口top=145px位置（header~55px + progress~46px + tabs~44px）
# 等等，让我重新算一下：
# header: padding 8px+6px + logo 32px ≈ 46px? 不对，实际可能不同
# 让我保守估计：header约55px, progress约46px, tabs约44px = 145px
# 由于body有padding-top:145px，内容从145px开始
# 手风琴标题sticky的top应该等于tab栏底部在视口中的位置 = 145px
# 对，因为sticky的top是相对于视口顶部的
old_sticky_css = ".accordion-header.sticky-acc{position:sticky;top:145px;z-index:5;background:#fff;box-shadow:0 2px 4px rgba(0,0,0,.06);}"
new_sticky_css = ".accordion-header.sticky-acc{position:sticky;top:145px;z-index:5;background:#fff;box-shadow:0 2px 4px rgba(0,0,0,.06);-webkit-backface-visibility:hidden;}"
# 保持top:145px不变，因为tab栏底部确实在145px处
html = html.replace(old_sticky_css, new_sticky_css)
print("✓ 手风琴吸顶样式优化（top值保持145px，增加backface-visibility）")

# ============================================================
# 第1项：去掉所有外层大标题卡片
# ============================================================

# 去掉基本信息tab的"基础资料"标题
html = html.replace('<div class="zone-section-title">基础资料</div>', '')
print("✓ 去掉基本信息tab的基础资料标题")

# 去掉服务详情tab的"服务信息"标题
html = html.replace('<div class="zone-section-title">服务信息</div>', '')
print("✓ 去掉服务详情tab的服务信息标题")

# 去掉签字确认tab的"签字确认"标题
html = html.replace('<div class="zone-section-title">签字确认</div>', '')
print("✓ 去掉签字确认tab的签字确认标题")

# 手风琴面板之间增加间距（已经有margin-bottom:10px，应该够了）
# 确认一下accordion的margin-bottom
acc_margin_check = ".accordion{background:#fff;border-radius:12px;overflow:hidden;margin-bottom:10px;border:1.5px solid #e2e8f0;"
if acc_margin_check in html:
    print("✓ 手风琴间距已为10px，保持不变")

# ============================================================
# 第4项：手风琴去掉编辑按钮，选项直接展示
# ============================================================

# 服务类别手风琴：去掉"编辑服务类别"按钮，直接显示复选框
# 当前结构：
# <div class="accordion-body">
#   <div id="svcCatsBody"></div>
#   <div style="text-align:center;margin-top:10px;">
#     <button ... onclick="openMo('serviceMo')">编辑服务类别</button>
#   </div>
# </div>
#
# 改为：直接把svcCats的内容放在手风琴body里，去掉按钮
# svcCats是在JS中动态生成的，所以我们需要：
# 1. 手风琴body里直接放svcCats容器
# 2. JS初始化时把服务类别复选框渲染到手风琴body里，而不是弹窗里

# 找到服务类别手风琴的body部分，替换内容
old_svc_body = '''      <div class="accordion-body">
        <div id="svcCatsBody"></div>
        <div style="text-align:center;margin-top:10px;">
          <button style="background:linear-gradient(135deg,#e74c3c,#c0392b);color:#fff;border:none;border-radius:8px;padding:8px 20px;font-size:13px;font-weight:600;cursor:pointer;" onclick="openMo('serviceMo')">编辑服务类别</button>
        </div>
      </div>'''
new_svc_body = '''      <div class="accordion-body">
        <div id="svcCatsBody"></div>
      </div>'''
html = html.replace(old_svc_body, new_svc_body)
print("✓ 服务类别手风琴去掉编辑按钮")

# 服务节点手风琴：去掉"编辑服务节点"按钮，直接显示选项
old_flow_body = '''      <div class="accordion-body">
        <div class="cg" id="cgFlowBody"></div>
        <div style="text-align:center;margin-top:10px;">
          <button style="background:linear-gradient(135deg,#f39c12,#f1c40f);color:#fff;border:none;border-radius:8px;padding:8px 20px;font-size:13px;font-weight:600;cursor:pointer;" onclick="openMo('flowMo')">编辑服务节点</button>
        </div>
      </div>'''
new_flow_body = '''      <div class="accordion-body">
        <div class="cg" id="cgFlowBody"></div>
      </div>'''
html = html.replace(old_flow_body, new_flow_body)
print("✓ 服务节点手风琴去掉编辑按钮")

# 签字确认tab的服务说明：去掉"编辑服务说明"按钮，直接显示选项
old_impact_section = '''    <!-- 服务说明（从服务详情移过来） -->
    <div class="sign-section">
      <h4 style="display:flex;align-items:center;justify-content:space-between;">
        <span>⚠️ 服务说明</span>
        <span class="card-status" id="st_impact"></span>
      </h4>
      <div class="sign-note">需尽快处理的事项及影响说明</div>
      <div id="impactSummary" style="font-size:13px;color:#4a5568;margin-bottom:8px;">
        <div style="margin-bottom:6px;"><span style="color:#718096;">紧急事项：</span><span id="impactUrgent">未填写</span></div>
        <div style="margin-bottom:6px;"><span style="color:#718096;">影响范围：</span><span id="impactScope">未选择</span></div>
        <div id="impactStopDate" style="display:none;"><span style="color:#718096;">停梯日期：</span><span id="impactStopDateVal"></span></div>
      </div>
      <div style="text-align:center;">
        <button style="background:linear-gradient(135deg,#34495e,#2c3e50);color:#fff;border:none;border-radius:8px;padding:8px 20px;font-size:13px;font-weight:600;cursor:pointer;" onclick="openMo('impactMo')">编辑服务说明</button>
      </div>
    </div>'''
new_impact_section = '''    <!-- 服务说明 -->
    <div class="sign-section">
      <h4 style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
        <span>⚠️ 服务说明</span>
        <span class="card-status" id="st_impact"></span>
      </h4>
      <div class="sign-note">需尽快处理的事项及影响说明</div>
      <div class="fr" style="margin-top:8px;"><label>需尽快处理项</label><input type="text" id="f13" placeholder="填写序号" oninput="updateBtnStatus()"></div>
      <div style="font-size:12px;color:#666;margin:8px 0 6px;">否则将影响：</div>
      <div class="cg" id="cgImpact"></div>
      <div class="fr" id="stopRow" style="display:none;margin-top:8px;"><label>停梯日期</label><input type="date" id="f14"></div>
    </div>'''
html = html.replace(old_impact_section, new_impact_section)
print("✓ 签字确认服务说明去掉编辑按钮，直接显示表单")

# ============================================================
# 第5项：服务记录手风琴直接展示，不要弹窗
# ============================================================

# 服务记录手风琴body改造：直接展示记录列表+新增表单
old_record_body = '''      <div class="accordion-body">
        <div id="recListSummary" style="margin-bottom:8px;"></div>
        <div style="text-align:center;">
          <button style="background:linear-gradient(135deg,#2ecc71,#27ae60);color:#fff;border:none;border-radius:8px;padding:8px 20px;font-size:13px;font-weight:600;cursor:pointer;" onclick="openMo('recordMo')">编辑记录</button>
        </div>
      </div>'''
new_record_body = '''      <div class="accordion-body">
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
html = html.replace(old_record_body, new_record_body)
print("✓ 服务记录手风琴改造为面板内展示")

# 保存修改
with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nCSS/HTML结构修改完成，新文件长度: {len(html)}")
print("接下来需要修改JS部分...")
