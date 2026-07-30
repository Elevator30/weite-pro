#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 weite-service-beta-detail.html 的布局问题：
1. 改为内容区独立滚动（参考 civil-survey.html 模式）
2. 顶部层级正确顺序：logo行 → 进度条 → tab栏
3. 手风琴吸顶top值修正
4. 滑动动画只在内容滚动区内
"""

import re

FILE_PATH = '/app/data/所有对话/主对话/weite-pro-temp/weite-service-beta-detail.html'

def main():
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # ========== 1. 修改 body CSS ==========
    # 原: body{font-family:...;background:#f5f7fa;padding-top:145px;padding-bottom:70px;-webkit-overflow-scrolling:touch;}
    # 新: body{font-family:...;background:#f5f7fa;overflow:hidden;height:100vh;}
    old_body = "body{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','微软雅黑',sans-serif;background:#f5f7fa;padding-top:145px;padding-bottom:70px;-webkit-overflow-scrolling:touch;}"
    new_body = "body{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','微软雅黑',sans-serif;background:#f5f7fa;overflow:hidden;height:100vh;}"
    assert old_body in content, "body CSS not found!"
    content = content.replace(old_body, new_body)
    print("✓ 修改了 body CSS")
    
    # ========== 2. 修改 .header CSS (去掉fixed) ==========
    old_header = ".header{padding:8px 16px 6px;background:#fff;position:fixed;top:0;left:0;right:0;z-index:50;-webkit-backface-visibility:hidden;will-change:transform;}"
    new_header = ".header{padding:8px 16px 6px;background:#fff;flex-shrink:0;z-index:50;}"
    assert old_header in content, ".header CSS not found!"
    content = content.replace(old_header, new_header)
    print("✓ 修改了 .header CSS（去掉fixed）")
    
    # ========== 3. 修改 .progress-container CSS (去掉fixed) ==========
    old_progress = ".progress-container{padding:12px 16px 10px;background:#fff;position:fixed;top:55px;left:0;right:0;z-index:49;border-bottom:1px solid #edf2f7;-webkit-backface-visibility:hidden;will-change:transform;}"
    new_progress = ".progress-container{padding:12px 16px 10px;background:#fff;flex-shrink:0;z-index:49;border-bottom:1px solid #edf2f7;}"
    assert old_progress in content, ".progress-container CSS not found!"
    content = content.replace(old_progress, new_progress)
    print("✓ 修改了 .progress-container CSS（去掉fixed）")
    
    # ========== 4. 修改 .zone-tabs CSS (去掉fixed) ==========
    old_tabs = """.zone-tabs{display:flex;gap:0;padding:0 12px;background:#fff;overflow-x:auto;flex-shrink:0;
  -webkit-overflow-scrolling:touch;border-bottom:2px solid #edf2f7;position:fixed;top:101px;left:0;right:0;z-index:48;
  -webkit-backface-visibility:hidden;will-change:transform;}"""
    new_tabs = """.zone-tabs{display:flex;gap:0;padding:0 12px;background:#fff;overflow-x:auto;flex-shrink:0;
  -webkit-overflow-scrolling:touch;border-bottom:2px solid #edf2f7;z-index:48;}"""
    assert old_tabs in content, ".zone-tabs CSS not found!"
    content = content.replace(old_tabs, new_tabs)
    print("✓ 修改了 .zone-tabs CSS（去掉fixed）")
    
    # ========== 5. 添加 .app-container 和 .scroll-content CSS ==========
    # 在 .header 前面添加新的CSS
    css_insert = """/* ===== 页面容器：独立滚动布局 ===== */
.app-container{display:flex;flex-direction:column;height:100vh;overflow:hidden;}
.scroll-content{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch;padding-bottom:70px;position:relative;}
.scroll-content::-webkit-scrollbar{width:6px;}
.scroll-content::-webkit-scrollbar-thumb{background:#cbd5e0;border-radius:3px;}

"""
    content = content.replace("/* ===== 顶部Header ===== */", css_insert + "/* ===== 顶部Header ===== */")
    print("✓ 添加了 .app-container 和 .scroll-content CSS")
    
    # ========== 6. 修改 .sticky-acc top 值 ==========
    old_sticky = ".accordion-header.sticky-acc{position:sticky;top:145px;z-index:5;background:#fff;box-shadow:0 2px 4px rgba(0,0,0,.06);-webkit-backface-visibility:hidden;}"
    new_sticky = ".accordion-header.sticky-acc{position:sticky;top:0;z-index:5;background:#fff;box-shadow:0 2px 4px rgba(0,0,0,.06);-webkit-backface-visibility:hidden;}"
    assert old_sticky in content, ".sticky-acc CSS not found!"
    content = content.replace(old_sticky, new_sticky)
    print("✓ 修改了 .sticky-acc top 值 (145px → 0)")
    
    # ========== 7. 修改 zone-content 的 min-height ==========
    # 原来有两个定义，都要去掉或修改
    old_zone_content1 = ".zone-content{position:relative;overflow:hidden;min-height:calc(100vh - 215px);}"
    new_zone_content1 = ".zone-content{position:relative;overflow:hidden;}"
    # 第一个定义
    if old_zone_content1 in content:
        content = content.replace(old_zone_content1, new_zone_content1)
        print("✓ 修改了第一个 .zone-content min-height")
    
    # 第二个定义（动画部分的）
    old_zone_content2 = """.zone-content{position:relative;overflow:hidden;min-height:calc(100vh - 215px);}
.zone-panel{display:none;padding:12px;width:100%;}"""
    new_zone_content2 = """.zone-content{position:relative;overflow:hidden;}
.zone-panel{display:none;padding:12px;width:100%;}"""
    if old_zone_content2 in content:
        content = content.replace(old_zone_content2, new_zone_content2)
        print("✓ 修改了第二个 .zone-content min-height")
    
    # ========== 8. 修改 HTML 结构 ==========
    # 在 <!-- 顶部Header --> 前面添加 <div class="app-container">
    old_html_start = "<!-- 顶部Header -->\n<div class=\"header\">"
    new_html_start = "<div class=\"app-container\">\n<!-- 顶部Header -->\n<div class=\"header\">"
    assert old_html_start in content, "Header HTML not found!"
    content = content.replace(old_html_start, new_html_start, 1)
    print("✓ 添加了 app-container 开始标签")
    
    # 在 <!-- Tab内容区 --> 前面添加 <div class="scroll-content">
    old_tab_content = "<!-- Tab内容区 -->\n<div class=\"zone-content\""
    new_tab_content = "<!-- 内容滚动区 -->\n<div class=\"scroll-content\">\n<!-- Tab内容区 -->\n<div class=\"zone-content\""
    assert old_tab_content in content, "Tab内容区 HTML not found!"
    content = content.replace(old_tab_content, new_tab_content, 1)
    print("✓ 添加了 scroll-content 开始标签")
    
    # 找到 btm 那一行，在它前面关闭 scroll-content 和 app-container
    # btm 在 zone-content 后面
    old_btm = '<div class="btm">'
    new_btm = '</div>\n<!-- /scroll-content -->\n</div>\n<!-- /app-container -->\n\n<div class="btm">'
    assert old_btm in content, "btm HTML not found!"
    content = content.replace(old_btm, new_btm, 1)
    print("✓ 添加了 scroll-content 和 app-container 关闭标签")
    
    # ========== 验证修改 ==========
    assert '<div class="app-container">' in content, "app-container 未添加"
    assert '</div>\n<!-- /app-container -->' in content, "app-container 未关闭"
    assert '<div class="scroll-content">' in content, "scroll-content 未添加"
    assert '</div>\n<!-- /scroll-content -->' in content, "scroll-content 未关闭"
    
    # 确认没有遗漏的position:fixed在顶部元素上
    # header / progress-container / zone-tabs 都不应该再有 position:fixed
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '.header{' in line and 'position:fixed' in line:
            print(f"⚠ 警告: .header 仍有 position:fixed (行 {i+1})")
        if '.progress-container{' in line and 'position:fixed' in line:
            print(f"⚠ 警告: .progress-container 仍有 position:fixed (行 {i+1})")
    
    print(f"\n✓ 全部修改完成！原文件 {len(original)} 字符 → 新文件 {len(content)} 字符")
    
    # 写入文件
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ 文件已保存")

if __name__ == '__main__':
    main()
