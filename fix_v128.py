#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v128: 添加PWA启动加载动画（splash screen），解决白屏问题
"""

import sys

def add_splash_screen(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # ========== 1. 在 <body> 后立即插入 splash-screen div ==========
    splash_html = '''<body>
<!-- Splash Screen - PWA启动加载层 -->
<div id="splash-screen" style="
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    z-index: 99999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    opacity: 1;
    transition: opacity 0.4s ease-out;
    -webkit-transition: opacity 0.4s ease-out;
">
    <div style="font-size: 36px; font-weight: 900; color: #fff; letter-spacing: 4px; margin-bottom: 8px; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Heiti SC', sans-serif;">WEITE</div>
    <div style="font-size: 14px; color: rgba(255,255,255,0.85); letter-spacing: 2px; margin-bottom: 24px; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif;">威特电梯</div>
    <div style="width: 36px; height: 36px; border: 3px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: splash-spin 0.8s linear infinite; -webkit-animation: splash-spin 0.8s linear infinite;"></div>
    <div style="font-size: 12px; color: rgba(255,255,255,0.7); margin-top: 16px; letter-spacing: 1px;">加载中...</div>
</div>
'''

    # 替换第一个 <body> 标签行
    old_body = '<body>\n<!-- v50.1 -->'
    new_body = splash_html + '<!-- v50.1 -->'
    
    if old_body not in content:
        print(f"ERROR: 找不到 <body> 标记在 {filepath}")
        return False
    
    content = content.replace(old_body, new_body, 1)
    print(f"✓ splash-screen div 已插入到 {filepath}")

    # ========== 2. 在 <style> 标签中添加动画关键帧 ==========
    # 找到第一个 style 标签开始位置，在最前面插入 keyframes
    style_start = content.find('<style>\n*{box-sizing:border-box;')
    if style_start == -1:
        print(f"ERROR: 找不到 style 标签在 {filepath}")
        return False
    
    splash_css = '''<style>
/* Splash Screen Animation */
@keyframes splash-spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
@-webkit-keyframes splash-spin {
    from { -webkit-transform: rotate(0deg); }
    to { -webkit-transform: rotate(360deg); }
}
#splash-screen.hidden {
    opacity: 0;
    pointer-events: none;
}
'''
    
    content = content.replace('<style>\n*{box-sizing:border-box;', splash_css + '*{box-sizing:border-box;', 1)
    print(f"✓ splash-screen CSS 动画已添加到 {filepath}")

    # ========== 3. 在 init() 调用后添加隐藏逻辑 ==========
    # 找到 init(); 调用，在后面添加隐藏splash的代码
    old_init_call = '\ninit();\n\n</script>'
    new_init_call = '''
init();

// 隐藏启动加载层
(function hideSplash() {
  function doHide() {
    var splash = document.getElementById('splash-screen');
    if (!splash) return;
    splash.classList.add('hidden');
    setTimeout(function() {
      if (splash.parentNode) {
        splash.style.display = 'none';
      }
    }, 450);
  }
  // 等待DOM和初始化完成后再隐藏，确保用户看到的是完整界面
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(doHide, 300);
  } else {
    document.addEventListener('DOMContentLoaded', function() {
      setTimeout(doHide, 300);
    });
  }
})();

</script>'''

    if old_init_call not in content:
        print(f"ERROR: 找不到 init() 调用在 {filepath}")
        return False
    
    content = content.replace(old_init_call, new_init_call, 1)
    print(f"✓ splash-screen 隐藏逻辑已添加到 {filepath}")

    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ {filepath} 修改完成！")
    return True

if __name__ == '__main__':
    files = [
        'factory-inspection-v2.html',
        '威特电梯厂检调试记录单v2.html'
    ]
    
    all_ok = True
    for f in files:
        print(f"\n{'='*50}")
        print(f"处理文件: {f}")
        print('='*50)
        if not add_splash_screen(f):
            all_ok = False
    
    if all_ok:
        print("\n🎉 所有文件修改成功！")
    else:
        print("\n❌ 部分文件修改失败！")
        sys.exit(1)
