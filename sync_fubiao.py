# -*- coding: utf-8 -*-
import re

# 读取print-fubiao.html内容
with open('print-fubiao.html', 'r', encoding='utf-8') as f:
    fb_content = f.read()

# 转义为JavaScript单引号字符串
# 1. 把 \ 换成 \\
# 2. 把 ' 换成 \'
# 3. 把换行换成 \n
js_str = fb_content.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')

# 处理每个主页面文件
for filename in ['factory-inspection-v2.html', '威特电梯厂检调试记录单v2.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到 _fubiaoHtmlContent = '...'; 的部分并替换
    # 模式：var _fubiaoHtmlContent = '...';
    pattern = r"var _fubiaoHtmlContent = '.*?';"
    replacement = f"var _fubiaoHtmlContent = '{js_str}';"
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if new_content == content:
        print(f"{filename}: 未找到_fubiaoHtmlContent，替换失败")
    else:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"{filename}: _fubiaoHtmlContent 同步完成")
    
    # 修改第③条注的文字
    old_note = "注：当水平距离在0~0.15m之间时，垂直距离要求可按等比例从0.1m增加至0.5m"
    new_note = "注：当轿厢最低部件和导轨之间的水平距离大于0.15m但小于0.5m时，此垂直距离可按等比例增加至0.5m"
    
    if old_note in new_content:
        new_content2 = new_content.replace(old_note, new_note)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_content2)
        print(f"{filename}: 第③条注文字已修改")
    else:
        print(f"{filename}: 未找到注的文字（可能在其他位置）")

print("完成")
