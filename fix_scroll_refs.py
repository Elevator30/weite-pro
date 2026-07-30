#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复滚动相关的JS代码：将 window.scrollY / window.scrollTo 改为 .scroll-content 容器
"""

FILE_PATH = '/app/data/所有对话/主对话/weite-pro-temp/weite-service-beta-detail.html'

def main():
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # ========== 1. 添加获取滚动容器的辅助函数 ==========
    # 在 openMo 函数前面添加
    helper_func = """// 获取滚动容器
function _getScrollContainer(){
  return document.querySelector('.scroll-content') || document.documentElement;
}

"""
    content = content.replace("// 新增的弹窗控制函数\nfunction openMo", helper_func + "// 新增的弹窗控制函数\nfunction openMo")
    print("✓ 添加了 _getScrollContainer 辅助函数")
    
    # ========== 2. 修改 openMo 函数中的滚动位置保存 ==========
    # 原: var scrollY=window.scrollY;
    # 新: var sc=_getScrollContainer(); var scrollY=sc.scrollTop;
    old_open_scroll = "  var scrollY=window.scrollY;\n  document.body.style.position='fixed';\n  document.body.style.top='-'+scrollY+'px';\n  document.body.style.width='100%';\n  document.body.style.overflow='hidden';\n  document.body.dataset.scrollY=scrollY;"
    new_open_scroll = "  var sc=_getScrollContainer(); var scrollY=sc.scrollTop;\n  document.body.style.position='fixed';\n  document.body.style.top='-'+scrollY+'px';\n  document.body.style.width='100%';\n  document.body.style.overflow='hidden';\n  document.body.dataset.scrollY=scrollY;"
    assert old_open_scroll in content, "openMo scroll code not found!"
    content = content.replace(old_open_scroll, new_open_scroll)
    print("✓ 修改了 openMo 中的滚动位置获取")
    
    # ========== 3. 修改 closeMo 函数中的滚动位置恢复 ==========
    old_close_scroll = "  window.scrollTo(0,scrollY);"
    new_close_scroll = "  _getScrollContainer().scrollTop = scrollY;"
    assert old_close_scroll in content, "closeMo scrollTo not found!"
    content = content.replace(old_close_scroll, new_close_scroll)
    print("✓ 修改了 closeMo 中的滚动位置恢复")
    
    # ========== 4. 修改 toggleAccordion 中的滚动定位 ==========
    # 原代码块
    old_accordion_scroll = """    setTimeout(function(){
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
    # 新代码块：使用滚动容器计算
    new_accordion_scroll = """    setTimeout(function(){
      var header = target.querySelector('.accordion-header');
      if(header){
        var sc = _getScrollContainer();
        var scRect = sc.getBoundingClientRect();
        var headerRect = header.getBoundingClientRect();
        var headerTopInContainer = headerRect.top - scRect.top + sc.scrollTop;
        // 标题吸顶在滚动容器顶部
        var targetScroll = headerTopInContainer - 5;
        if(targetScroll > 0 && (targetScroll < sc.scrollTop - 10 || targetScroll > sc.scrollTop + 50)){
          sc.scrollTo({top: targetScroll, behavior: 'smooth'});
        }
      }
    }, 50);"""
    assert old_accordion_scroll in content, "toggleAccordion scroll code not found!"
    content = content.replace(old_accordion_scroll, new_accordion_scroll)
    print("✓ 修改了 toggleAccordion 中的滚动定位")
    
    # ========== 5. 修改其他 window.scrollTo(0,0) 调用 ==========
    # 清空按钮 (两处)
    old_clear_scroll = "window.scrollTo(0,0);updateBtnStatus();});"
    new_clear_scroll = "_getScrollContainer().scrollTop=0;updateBtnStatus();});"
    count = content.count(old_clear_scroll)
    if count > 0:
        content = content.replace(old_clear_scroll, new_clear_scroll)
        print(f"✓ 修改了 {count} 处清空按钮的 window.scrollTo(0,0)")
    
    # 清空按钮带toast的
    old_clear_toast = "window.scrollTo(0,0);showToast('已清空');updateBtnStatus();});"
    new_clear_toast = "_getScrollContainer().scrollTop=0;showToast('已清空');updateBtnStatus();});"
    if old_clear_toast in content:
        content = content.replace(old_clear_toast, new_clear_toast)
        print("✓ 修改了清空按钮带toast的 window.scrollTo(0,0)")
    
    # 编辑记录按钮
    old_edit_scroll = "closeMo('historyMo');loadRec(curViewIdx);window.scrollTo(0,0);});"
    new_edit_scroll = "closeMo('historyMo');loadRec(curViewIdx);_getScrollContainer().scrollTop=0;});"
    if old_edit_scroll in content:
        content = content.replace(old_edit_scroll, new_edit_scroll)
        print("✓ 修改了编辑记录按钮的 window.scrollTo(0,0)")
    
    # loadRec 中的滚动到顶部
    old_loadrec_scroll = "window.scrollTo({top:0,behavior:'smooth'});\n  showToast('已载入，修改后点保存');"
    new_loadrec_scroll = "_getScrollContainer().scrollTo({top:0,behavior:'smooth'});\n  showToast('已载入，修改后点保存');"
    if old_loadrec_scroll in content:
        content = content.replace(old_loadrec_scroll, new_loadrec_scroll)
        print("✓ 修改了 loadRec 中的 window.scrollTo")
    
    # PDF预览返回按钮
    old_pdf_back = "closeMo('historyMo');window.scrollTo(0,0);});"
    new_pdf_back = "closeMo('historyMo');_getScrollContainer().scrollTop=0;});"
    count_pdf = content.count(old_pdf_back)
    if count_pdf > 0:
        content = content.replace(old_pdf_back, new_pdf_back)
        print(f"✓ 修改了 {count_pdf} 处PDF预览相关的 window.scrollTo(0,0)")
    
    # 分享成功后
    # 已经被上面的PDF返回按钮覆盖了吗？让我检查一下
    
    # ========== 验证还有没有遗漏的 window.scroll ==========
    import re
    remaining = re.findall(r'window\.scroll[YT]o?\(?[^)]*\)?', content)
    # 去掉注释里的
    if remaining:
        print(f"\n⚠ 仍有 {len(remaining)} 处 window.scroll 调用:")
        for r in remaining[:10]:
            print(f"  - {r[:60]}")
    else:
        print("\n✓ 所有 window.scroll 调用均已替换")
    
    print(f"\n修改完成：原文件 {len(original)} 字符 → 新文件 {len(content)} 字符")
    
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ 文件已保存")

if __name__ == '__main__':
    main()
