#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复详情页中的几个问题：
1. sd1/sd2 ID重复（tab中和signMo弹窗中都有）
2. 签名预览同步更新
3. 点击tab中的签名区域直接打开签名画板
"""

import re

BASE_DIR = '/app/data/所有对话/主对话/weite-pro-temp'
DETAIL_FILE = BASE_DIR + '/weite-service-beta-detail.html'

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

html = read_file(DETAIL_FILE)

# ===== 修复1：签字确认tab中的签名区域改用不同的ID =====
old_sign_area = '''    <!-- 签字确认区 -->
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
    </div>'''

new_sign_area = '''    <!-- 签字确认区 -->
    <div class="sign-section">
      <h4>✍️ 签字确认</h4>
      <div class="sign-note">点击下方区域弹出手写签名</div>
      <div style="margin-bottom:10px;">
        <div style="font-size:13px;font-weight:bold;color:#555;margin-bottom:4px;">服务人签字</div>
        <div class="sd" id="signPrev1" onclick="startSign(1)"><span>点击签名</span></div>
      </div>
      <div>
        <div style="font-size:13px;font-weight:bold;color:#555;margin-bottom:4px;">被服务人员签字</div>
        <div class="sd" id="signPrev2" onclick="startSign(2)"><span>点击签名</span></div>
      </div>
      <div style="margin-top:8px;">
        <span class="card-status" id="st_sign" style="display:inline-block;vertical-align:middle;"></span>
        <span style="font-size:12px;color:#718096;margin-left:4px;">双方签字后生效</span>
      </div>
    </div>'''

html = html.replace(old_sign_area, new_sign_area)

# ===== 修复2：添加startSign函数和签名同步更新逻辑 =====
# 在签字确认相关JS之后添加
old_sig_ok = '''document.getElementById('sigOk').addEventListener('click',function(){var c=document.getElementById('sigCvs');var b=document.createElement('canvas');b.width=c.width;b.height=c.height;if(c.toDataURL()===b.toDataURL()){showToast('请先签名');return;}var rawPng=c.toDataURL('image/png');compressSigData(rawPng).then(function(data){if(curSig===1){sig1Data=data;sig1Canvas=c;}else{sig2Data=data;sig2Canvas=c;}document.getElementById('sd'+curSig).innerHTML='<img src="'+data+'">';closeSigMo();updateBtnStatus();});});'''

new_sig_ok = '''document.getElementById('sigOk').addEventListener('click',function(){var c=document.getElementById('sigCvs');var b=document.createElement('canvas');b.width=c.width;b.height=c.height;if(c.toDataURL()===b.toDataURL()){showToast('请先签名');return;}var rawPng=c.toDataURL('image/png');compressSigData(rawPng).then(function(data){if(curSig===1){sig1Data=data;sig1Canvas=c;}else{sig2Data=data;sig2Canvas=c;}document.getElementById('sd'+curSig).innerHTML='<img src="'+data+'">';var prev=document.getElementById('signPrev'+curSig);if(prev)prev.innerHTML='<img src="'+data+'">';closeSigMo();updateBtnStatus();});});'''

html = html.replace(old_sig_ok, new_sig_ok)

# 添加startSign函数
old_start_sig_marker = '''// 暴露到全局（修复onclick调用失效bug）
window.switchTab = switchTab;'''

new_start_sig = '''// 暴露到全局（修复onclick调用失效bug）
window.switchTab = switchTab;

// 从tab中直接开始签名
function startSign(n){
  curSig = n;
  openSig();
}
window.startSign = startSign;'''

html = html.replace(old_start_sig_marker, new_start_sig)

# ===== 修复3：loadRec时也更新signPrev的显示 =====
old_load_sig = '''  if(d.sig1){sig1Data=d.sig1;sig1Canvas=null;document.getElementById('sd1').innerHTML='<img src="'+d.sig1+'">';}
  if(d.sig2){sig2Data=d.sig2;sig2Canvas=null;document.getElementById('sd2').innerHTML='<img src="'+d.sig2+'">';}'''

new_load_sig = '''  if(d.sig1){sig1Data=d.sig1;sig1Canvas=null;document.getElementById('sd1').innerHTML='<img src="'+d.sig1+'">';var p1=document.getElementById('signPrev1');if(p1)p1.innerHTML='<img src="'+d.sig1+'">';}
  if(d.sig2){sig2Data=d.sig2;sig2Canvas=null;document.getElementById('sd2').innerHTML='<img src="'+d.sig2+'">';var p2=document.getElementById('signPrev2');if(p2)p2.innerHTML='<img src="'+d.sig2+'">';}'''

html = html.replace(old_load_sig, new_load_sig)

# ===== 修复4：清空时也清空signPrev =====
old_clear_sig = '''document.querySelectorAll('.sd').forEach(function(el){el.innerHTML='<span>点击签名</span>';});sig1Data='';sig2Data='';sig1Canvas=null;sig2Canvas=null;'''

new_clear_sig = '''document.querySelectorAll('.sd').forEach(function(el){el.innerHTML='<span>点击签名</span>';});sig1Data='';sig2Data='';sig1Canvas=null;sig2Canvas=null;
  var sp1=document.getElementById('signPrev1');if(sp1)sp1.innerHTML='<span>点击签名</span>';
  var sp2=document.getElementById('signPrev2');if(sp2)sp2.innerHTML='<span>点击签名</span>';'''

html = html.replace(old_clear_sig, new_clear_sig)

# ===== 修复5：服务详情手风琴中，记录汇总从recBox读取改为从弹窗中读取 =====
# 原代码中recListSummary读取的是#recBox .ri，但recBox在recordMo弹窗里
# 这个应该是对的，因为数据在弹窗里，关闭弹窗后数据还在DOM中
# 所以这个不需要改

# ===== 修复6：确保impactMo关闭后更新签字确认tab的汇总 =====
# 在closeMo函数中添加更新impactSummary的调用
old_close_mo_end = '''  updateBtnStatus();
}'''

# 找到closeMo函数的结尾（只有一个updateBtnStatus();\n}的地方是closeMo）
# 实际上有多个地方有updateBtnStatus()，需要精确定位
# 让我用更精确的方式匹配

close_mo_pattern = r'(function closeMo\(id\)\{.*?updateBtnStatus\(\);\n\})'
match = re.search(close_mo_pattern, html, re.DOTALL)
if match:
    old_close = match.group(1)
    new_close = old_close.replace('  updateBtnStatus();\n}', 
        '''  updateBtnStatus();
  // 如果关闭的是impactMo，刷新服务说明汇总
  if(id === 'impactMo' && typeof updateImpactSummary === 'function'){
    updateImpactSummary();
  }
}''')
    html = html.replace(old_close, new_close)

# ===== 修复7：关闭recordMo时刷新服务记录汇总 =====
# 在closeMo中也添加对recordMo的处理
# 已经在上面的修改中通过updateBtnStatus间接处理了，但再确保一下
# updateBtnStatus已经调用了updateSvcAccordionSummary（当在tab 1时）

# ===== 修复8：tab动画中确保内容区高度正确 =====
# 动画结束后设置正确的高度，避免内容跳动
# 在switchTab的动画结束清理中添加
old_anim_end = '''      content.classList.remove('animating');
      _tabAnimating = false;'''

new_anim_end = '''      content.classList.remove('animating');
      // 确保内容区高度正确
      content.style.height = '';
      _tabAnimating = false;'''

html = html.replace(old_anim_end, new_anim_end)

# 动画开始时设置内容区高度
old_anim_start = '''    // 设置动画初始状态
    content.classList.add('animating');
    newPanel.style.display = 'block';'''

new_anim_start = '''    // 设置动画初始状态
    content.classList.add('animating');
    // 设置内容区高度为当前面板高度，防止动画期间高度跳动
    content.style.height = oldPanel.offsetHeight + 'px';
    newPanel.style.display = 'block';'''

html = html.replace(old_anim_start, new_anim_start)

write_file(DETAIL_FILE, html)
print('✅ 详情页修复完成')
print(f'   文件大小: {len(html)} 字节')

# 验证语法
import subprocess
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
passed = 0
for i, script in enumerate(scripts):
    if not script.strip() or script.strip().startswith('<!--'):
        passed += 1
        continue
    tmp = f'/tmp/fix_detail_{i}.js'
    with open(tmp, 'w') as f:
        f.write(script)
    r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
    if r.returncode == 0:
        passed += 1
    else:
        print(f'  ❌ 脚本{i+1} 错误: {r.stderr[:150]}')
    import os
    os.remove(tmp)
print(f'   JS语法: {passed}/{len(scripts)} 通过')
