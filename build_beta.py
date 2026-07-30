#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 weite-service-beta.html - tab分区布局体验版 v2
基于 weite-service-v14.html 重构，保留所有功能和数据结构
"""

import re

def main():
    with open('weite-service-v14.html', 'r', encoding='utf-8') as f:
        src = f.read()
    
    # ===== 定位各个部分 =====
    head_end = src.find('</head>')
    body_start = src.find('<body>') + len('<body>')
    body_end = src.find('</body>')
    
    head_part = src[:head_end + len('</head>')]
    body_full = src[body_start:body_end]
    
    # ===== 提取 body 中的两个 script =====
    # 第一个 script（弹窗控制函数）
    first_script_start = body_full.find('<script>')
    first_script_end = body_full.find('</script>', first_script_start) + len('</script>')
    first_script = body_full[first_script_start:first_script_end]
    
    # 第二个 script（主逻辑）
    last_script_start = body_full.rfind('<script>')
    last_script_end = body_full.rfind('</script>') + len('</script>')
    last_script = body_full[last_script_start:last_script_end]
    
    # 中间的 HTML 内容（两个 script 之间）
    middle_html = body_full[first_script_end:last_script_start]
    
    # ===== 从中间 HTML 中提取所有弹窗 =====
    # 弹窗从 <!-- 基本信息弹窗 --> 开始，到 <!-- 隐藏的select存值 --> 之后的隐藏select结束
    
    # 找到第一个弹窗的开始
    modal_start = middle_html.find('<!-- 基本信息弹窗 -->')
    
    # 找到隐藏 select 结束的位置（到最后一个 </select>）
    # 在 locMo 之后有3个隐藏的 select: p1, c1, x1
    hidden_select_start = middle_html.find('<select id="p1"')
    # 找到第三个 select 的结束
    select_count = 0
    pos = hidden_select_start
    hidden_select_end = pos
    while select_count < 3:
        next_select_end = middle_html.find('</select>', pos)
        if next_select_end == -1:
            break
        hidden_select_end = next_select_end + len('</select>')
        select_count += 1
        pos = hidden_select_end
    
    all_modals = middle_html[modal_start:hidden_select_end]
    
    # ===== 提取 logo 图片 src =====
    logo_match = re.search(r'<img class="logo-img" src="([^"]+)"', middle_html)
    logo_src = logo_match.group(1) if logo_match else ''
    
    # ===== 构建新的 CSS =====
    # 找到 style 标签并替换
    style_start = head_part.find('<style>')
    style_end = head_part.find('</style>') + len('</style>')
    
    new_css = '''<style>
/* ===== 基础重置 ===== */
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','微软雅黑',sans-serif;background:#f5f7fa;padding-bottom:70px;-webkit-overflow-scrolling:touch;}

/* ===== 顶部Header ===== */
.header{padding:8px 16px 6px;background:#fff;position:sticky;top:0;z-index:50;}
.logo-area{display:flex;align-items:flex-end;gap:0;}
.logo-img{height:32px;width:auto;display:block;}
.logo-elev{font-size:18px;font-weight:900;color:#0d2137;letter-spacing:0px;margin-left:1px;font-family:'PingFang SC','Heiti SC','Microsoft YaHei',sans-serif;line-height:1;padding-bottom:1px;}
.header-sub{font-size:13px;font-weight:400;color:#555;letter-spacing:4px;font-family:'Songti SC','SimSun',serif;display:flex;align-items:center;justify-content:center;gap:10px;margin-top:3px;}
.header-sub .hl{flex:1;height:1px;background:#999;min-width:20px;}

/* ===== 进度条 ===== */
.progress-container{padding:12px 16px 10px;background:#fff;position:sticky;top:55px;z-index:49;border-bottom:1px solid #edf2f7;}
.progress-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;}
.progress-title{font-size:12px;font-weight:600;color:#718096;}
.progress-percent{font-size:15px;font-weight:800;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.progress-bar{height:5px;background:#e2e8f0;border-radius:3px;overflow:hidden;}
.progress-fill{height:100%;width:0%;background:linear-gradient(90deg,#667eea 0%,#764ba2 100%);border-radius:3px;transition:width .3s ease;}

/* ===== Tab分区栏 ===== */
.zone-tabs{display:flex;gap:0;padding:0 8px;background:#fff;overflow-x:auto;flex-shrink:0;
  -webkit-overflow-scrolling:touch;border-bottom:2px solid #edf2f7;position:sticky;top:101px;z-index:48;}
.zone-tabs::-webkit-scrollbar{display:none;}
.zone-tab{padding:12px 14px;white-space:nowrap;font-size:13px;font-weight:600;color:#718096;
  cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all .15s;flex-shrink:0;}
.zone-tab.active{color:#667eea;border-bottom-color:#667eea;}
.zone-panel{display:none;animation:fadeIn .2s ease;padding:12px;}
.zone-panel.active{display:block;}
@keyframes fadeIn{from{opacity:0;transform:translateY(4px);}to{opacity:1;transform:translateY(0);}}

/* ===== 分区小标题 ===== */
.zone-section-title{font-size:13px;font-weight:700;color:#718096;padding:8px 4px 6px;letter-spacing:1px;}

/* ===== 卡片网格 ===== */
.sec-cards{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:4px;}
.form-card{background:#fff;border-radius:12px;padding:14px 12px;border:1.5px solid #e2e8f0;cursor:pointer;position:relative;box-shadow:0 1px 4px rgba(0,0,0,.04);transition:all .2s ease;-webkit-tap-highlight-color:transparent;}
.form-card:active{transform:scale(.97);box-shadow:0 2px 8px rgba(102,126,234,.15);}
.form-card.full-width{grid-column:1/-1;}
.card-blue{border-top:3px solid #90cdf4;}
.card-purple{border-top:3px solid #b794f4;}
.card-green{border-top:3px solid #81e6d9;}
.card-orange{border-top:3px solid #f6ad55;}
.card-pink{border-top:3px solid #f687b3;}
.card-yellow{border-top:3px solid #fcd34d;}
.card-indigo{border-top:3px solid #9fa8da;}
.card-teal{border-top:3px solid #4fd1c5;}
.card-icon{font-size:20px;margin-bottom:6px;display:block;}
.card-label{color:#4a5568;font-size:13px;font-weight:600;line-height:1.3;}
.card-status{position:absolute;top:12px;right:12px;width:7px;height:7px;border-radius:50%;background:#cbd5e0;transition:background .2s;}
.card-status.filled{background:#68d391;}
.card-count{position:absolute;top:10px;right:10px;background:#edf2f7;color:#718096;font-weight:600;padding:2px 7px;border-radius:8px;font-size:10px;}

/* ===== 底部操作栏 ===== */
.btm{position:fixed;bottom:0;left:0;right:0;display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:10px 16px;background:#fff;box-shadow:0 -2px 8px rgba(0,0,0,.08);z-index:100;}
.btm .btn-primary{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;border:none;border-radius:10px;padding:14px 0;font-size:14px;font-weight:600;cursor:pointer;box-shadow:0 3px 10px rgba(102,126,234,.3);letter-spacing:1px;}
.btm .btn-primary:active{box-shadow:0 1px 4px rgba(102,126,234,.3);transform:translateY(1px);}
.btm .btn-secondary{background:#f7fafc;color:#718096;border:1.5px solid #e2e8f0;border-radius:10px;padding:14px 0;font-size:14px;font-weight:600;cursor:pointer;letter-spacing:1px;}
.btm .btn-secondary:active{background:#edf2f7;}

/* ===== 表单样式（弹窗内） ===== */
.fr{display:flex;align-items:center;margin-bottom:10px;gap:8px;}
.fr label{min-width:80px;font-size:13px;color:#333;flex-shrink:0;}
.fr input,.fr select,.fr textarea{flex:1;border:1px solid #ddd;border-radius:6px;padding:8px 10px;font-size:14px;background:#fafafa;outline:none;}
.fr input:focus,.fr textarea:focus{border-color:#667eea;background:#fff;}
.cg{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px;}
.ci{display:flex;align-items:center;gap:4px;font-size:13px;background:#f0f4f8;padding:5px 10px;border-radius:15px;cursor:pointer;}
.ci input{width:16px;height:16px;accent-color:#667eea;}
.ci.ck{background:#d4e6f1;}
.ri{background:#f8f9fa;border-radius:8px;padding:10px;margin-bottom:8px;border-left:3px solid #667eea;}
.ri input{width:100%;border:1px solid #e0e0e0;border-radius:4px;padding:6px 8px;font-size:13px;margin-bottom:4px;word-break:break-all;}
.ri select{border:1px solid #e0e0e0;border-radius:4px;padding:6px 8px;font-size:13px;}
.ar{text-align:center;padding:8px;color:#667eea;font-size:13px;cursor:pointer;border:1px dashed #667eea;border-radius:6px;margin-top:5px;}
.lr{display:flex;gap:6px;margin-bottom:8px;}
.lr select{flex:1;border:1px solid #ddd;border-radius:6px;padding:8px 4px;font-size:13px;background:#fafafa;}

/* ===== 弹窗Modal ===== */
.mo{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.5);z-index:999;}
.mi{position:absolute;bottom:0;width:100%;max-height:90vh;background:#fff;border-radius:12px 12px 0 0;overflow:hidden;display:flex;flex-direction:column;}
.mh{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid #eee;flex-shrink:0;}
.mh h3{font-size:15px;color:#fff;}
.mh button{background:none;border:none;font-size:22px;cursor:pointer;color:#fff;}
.mb{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch;padding-bottom:0;min-height:0;}
.modal-confirm{display:flex;padding:4px 16px 4px;flex-shrink:0;background:#fff;border-top:1px solid #eee;z-index:10;}
.modal-confirm button{flex:1;padding:10px;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;}

/* ===== 签名显示 ===== */
.sd{border:1px solid #e0e0e0;border-radius:6px;height:60px;display:flex;align-items:center;justify-content:center;cursor:pointer;background:#fafafa;overflow:hidden;}
.sd img{max-height:55px;max-width:90%;}
.sd span{font-size:12px;color:#bbb;}
.scw{border:1px solid #ddd;border-radius:8px;background:#fff;position:relative;height:200px;touch-action:none;margin:0 16px;}
.scw canvas{display:block;width:100%;height:200px;touch-action:none;}
.scw .sp{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:14px;color:#bbb;pointer-events:none;}
.sab{display:flex;gap:10px;padding:10px 16px;}
.sab button{flex:1;padding:10px;border:none;border-radius:6px;font-size:14px;cursor:pointer;}
.scg{background:#f0f0f0;color:#999;}
.scl{background:#eee;color:#333;}
.scf{background:#667eea;color:#fff;}

/* ===== Toast ===== */
.toast{display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,.75);color:#fff;padding:12px 24px;border-radius:8px;font-size:14px;z-index:9999;}

/* ===== 已保存记录卡片 ===== */
.rec-card{background:#fff;border-radius:12px;padding:14px;margin-bottom:10px;border:1.5px solid #e2e8f0;box-shadow:0 1px 4px rgba(0,0,0,.04);position:relative;}
.rec-card .rc-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;}
.rec-card .rc-name{color:#4a5568;font-size:14px;font-weight:700;}
.rec-card .rc-time{font-size:10px;color:#a0aec0;}
.rec-card .rc-info{font-size:12px;color:#718096;margin:2px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.rec-card .rc-btns{display:flex;gap:8px;margin-top:8px;}
.rec-card .rc-btns button{flex:1;padding:8px;border:none;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;}
.rc-btn-view{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;}
.rc-btn-del{background:#f7fafc;color:#c0392b;border:1.5px solid #fed7d7!important;}

/* ===== 信封样式详情 ===== */
.env-card{position:relative;margin:10px 0;border-radius:16px;overflow:hidden;background:#fff;box-shadow:0 4px 20px rgba(0,0,0,.12);}
.env-top{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:16px 20px 30px;color:#fff;}
.env-top h2{font-size:16px;font-weight:700;margin-bottom:4px;}
.env-top .env-sub{font-size:11px;opacity:.8;}
.env-body{background:#fff;margin:-18px 12px 0;border-radius:12px 12px 0 0;padding:16px 14px;min-height:120px;position:relative;box-shadow:0 -2px 10px rgba(0,0,0,.06);}
.env-body::before{content:'';position:absolute;top:-8px;left:0;right:0;height:8px;background:repeating-linear-gradient(90deg,transparent,transparent 8px,#fff 8px,#fff 10px);border-radius:4px 4px 0 0;}
.env-field{margin-bottom:12px;}
.env-field .env-label{font-size:11px;color:#a0aec0;margin-bottom:2px;}
.env-field .env-value{font-size:14px;color:#2d3748;font-weight:600;word-break:break-all;}
.env-progress{margin:12px 0 8px;}
.env-progress .ep-header{display:flex;justify-content:space-between;font-size:11px;color:#718096;margin-bottom:4px;}
.env-progress .ep-bar{height:6px;background:#edf2f7;border-radius:3px;overflow:hidden;}
.env-progress .ep-fill{height:100%;background:linear-gradient(90deg,#667eea,#764ba2);border-radius:3px;transition:width .3s;}
.env-btns{display:flex;gap:10px;margin-top:14px;}
.env-btns button{flex:1;padding:12px;border:none;border-radius:10px;font-size:14px;font-weight:700;cursor:pointer;letter-spacing:1px;}
.env-btn-edit{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;box-shadow:0 3px 10px rgba(102,126,234,.3);}
.env-btn-print{background:linear-gradient(135deg,#27ae60,#2ecc71);color:#fff;box-shadow:0 3px 10px rgba(39,174,96,.3);}

/* ===== 新手引导 ===== */
.guide-overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.7);z-index:10000;display:flex;align-items:center;justify-content:center;padding:20px;}
.guide-box{background:#fff;border-radius:16px;padding:24px 20px;max-width:340px;width:100%;box-shadow:0 10px 40px rgba(0,0,0,.3);}
.guide-box h2{font-size:18px;font-weight:800;color:#2d3748;margin-bottom:16px;text-align:center;}
.guide-section{margin-bottom:16px;padding:12px;background:#f7fafc;border-radius:10px;border-left:4px solid #667eea;}
.guide-section h3{font-size:14px;font-weight:700;color:#4a5568;margin-bottom:6px;}
.guide-section p{font-size:12px;color:#718096;line-height:1.6;}
.guide-section .step{display:flex;align-items:flex-start;gap:8px;margin-bottom:4px;}
.guide-section .step-num{background:#667eea;color:#fff;border-radius:50%;width:20px;height:20px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0;margin-top:1px;}
.guide-close-btn{width:100%;padding:14px;border:none;border-radius:10px;font-size:15px;font-weight:700;cursor:pointer;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;margin-top:8px;}

/* ===== 响应式微调 ===== */
@media(max-width:360px){
  .zone-tab{padding:10px 10px;font-size:12px;}
  .form-card{padding:12px 10px;}
  .card-label{font-size:12px;}
}
</style>
'''
    
    # 替换 head 中的 style
    new_head = head_part[:style_start] + new_css + head_part[style_end:]
    
    # ===== 构建新的 body HTML =====
    new_body_html = '''
<!-- 顶部Header -->
<div class="header">
  <div class="logo-area">
    <img class="logo-img" src="''' + logo_src + '''" alt="WEITE">
    <span class="logo-elev">电梯</span>
  </div>
  <div class="header-sub"><span class="hl"></span><span>技术服务单</span><span class="hl"></span></div>
</div>

<!-- 进度条 -->
<div class="progress-container">
  <div class="progress-header">
    <span class="progress-title">填写进度</span>
    <span class="progress-percent" id="progressPct">0%</span>
  </div>
  <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
</div>

<!-- Tab分区栏 -->
<div class="zone-tabs" id="zoneTabs">
  <div class="zone-tab active" onclick="switchTab(0)">基本信息</div>
  <div class="zone-tab" onclick="switchTab(1)">故障描述</div>
  <div class="zone-tab" onclick="switchTab(2)">检修记录</div>
  <div class="zone-tab" onclick="switchTab(3)">验收签字</div>
</div>

<!-- Tab内容区 -->
<div class="zone-content">
  <!-- Tab 1: 基本信息 -->
  <div class="zone-panel active" id="zonePanel_0">
    <div class="zone-section-title">基础资料</div>
    <div class="sec-cards">
      <div class="form-card card-blue" onclick="openMo('basicMo')"><span class="card-icon">📋</span><span class="card-label">申请人</span><div class="card-status" id="st_basic"></div></div>
      <div class="form-card card-purple" onclick="openMo('projectMo')"><span class="card-icon">🏗️</span><span class="card-label">项目信息</span><div class="card-status" id="st_project"></div></div>
      <div class="form-card card-green" onclick="openMo('contactMo')"><span class="card-icon">📞</span><span class="card-label">联系方式</span><div class="card-status" id="st_contact"></div></div>
      <div class="form-card card-orange" onclick="openMo('buildMo')"><span class="card-icon">🔧</span><span class="card-label">施工类别</span><div class="card-status" id="st_build"></div></div>
    </div>
  </div>

  <!-- Tab 2: 故障描述 -->
  <div class="zone-panel" id="zonePanel_1">
    <div class="zone-section-title">服务信息</div>
    <div class="sec-cards">
      <div class="form-card card-pink" onclick="openMo('serviceMo')"><span class="card-icon">📝</span><span class="card-label">服务类别</span><div class="card-status" id="st_service"></div></div>
      <div class="form-card card-yellow" onclick="openMo('flowMo')"><span class="card-icon">🔄</span><span class="card-label">服务节点</span><div class="card-status" id="st_flow"></div></div>
      <div class="form-card card-teal" onclick="openMo('impactMo')"><span class="card-icon">⚠️</span><span class="card-label">服务说明</span><div class="card-status" id="st_impact"></div></div>
    </div>
  </div>

  <!-- Tab 3: 检修记录 -->
  <div class="zone-panel" id="zonePanel_2">
    <div class="zone-section-title">服务记录</div>
    <div class="sec-cards">
      <div class="form-card card-indigo full-width" onclick="openMo('recordMo')"><span class="card-icon">💬</span><span class="card-label">服务内容/记录</span><span class="card-count" id="st_record">0条</span></div>
    </div>
  </div>

  <!-- Tab 4: 验收签字 -->
  <div class="zone-panel" id="zonePanel_3">
    <div class="zone-section-title">确认与数据</div>
    <div class="sec-cards">
      <div class="form-card card-purple" onclick="openMo('signMo')"><span class="card-icon">✍️</span><span class="card-label">签字确认</span><div class="card-status" id="st_sign"></div></div>
      <div class="form-card card-blue" onclick="openMo('historyMo')"><span class="card-icon">📂</span><span class="card-label">已保存</span><span class="card-count" id="st_history">0条</span></div>
      <div class="form-card card-green full-width" onclick="openMo('dataMo')"><span class="card-icon">📦</span><span class="card-label">数据迁移</span><div class="card-status" id="st_data"></div></div>
    </div>
  </div>
</div>

<!-- 底部操作栏 -->
<div class="btm"><button class="btn-primary" id="saveBtn">💾 保存服务单</button><button class="btn-secondary" id="clearBtn">🗑️ 清空</button></div>

<div class="toast" id="toast"></div>
'''
    
    # 添加所有弹窗
    new_body_html += '\n' + all_modals + '\n'
    
    # ===== 修改第二个 script，添加 switchTab 函数 =====
    # 在 'use strict' 之后插入
    tab_js = '''
// ===== Tab 切换函数 =====
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
}
'''
    
    # 在 last_script 中插入
    # 找到 'use strict' 的位置
    use_strict_pos = last_script.find("'use strict';")
    if use_strict_pos == -1:
        use_strict_pos = last_script.find('"use strict";')
    
    if use_strict_pos >= 0:
        insert_pos = use_strict_pos + len("'use strict';")
        new_last_script = last_script[:insert_pos] + '\n' + tab_js + last_script[insert_pos:]
    else:
        # 在 <script> 标签之后插入
        script_tag_end = last_script.find('>') + 1
        new_last_script = last_script[:script_tag_end] + '\n' + tab_js + last_script[script_tag_end:]
    
    # ===== 组装完整文件 =====
    full_html = new_head + '\n<body>\n' + first_script + '\n' + new_body_html + '\n' + new_last_script + '\n</body>\n</html>'
    
    # 写入文件
    with open('weite-service-beta.html', 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f'生成成功！')
    print(f'文件大小: {len(full_html)} 字节')
    print(f'Tab数量: 4')
    print(f'弹窗: 保留全部')

if __name__ == '__main__':
    main()
