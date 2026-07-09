#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 print-fubiao.html 的内容同步到两个入口文件的 _fubiaoHtmlContent 变量中
"""

import re
import os

WORK_DIR = '/app/data/所有对话/主对话/weite-pro-temp/'
SOURCE_FILE = os.path.join(WORK_DIR, 'print-fubiao.html')
TARGET_FILES = [
    os.path.join(WORK_DIR, 'factory-inspection-v2.html'),
    os.path.join(WORK_DIR, '威特电梯厂检调试记录单v2.html'),
]


def html_to_js_string(html_content):
    """将HTML内容转换为JS字符串格式（与现有格式保持一致）
    
    现有格式特点：
    - < 编码为 \\u003c
    - > 编码为 \\u003e
    - & 编码为 \\u0026
    - 换行编码为 \\n（字面字符）
    - 单引号 ' 编码为 \\'
    - </script> 中的 / 编码为 \\/
    """
    # 先处理特殊的 </script> 标签中的 / 转义
    # 但因为我们会把 < 转成 \u003c，所以 </script> 会变成 \u003c/script\u003e
    # 现有格式中是 \u003c\/script\u003e，所以 / 也需要转义
    # 让我们检查一下：现有格式中只有 </script> 的 / 被转义，其他 </div> 等没有
    # 所以我们只需要转义 </script> 中的 /
    
    result = html_content
    
    # 将 </script> 替换为 <\/script>（在转义 < 之前）
    result = re.sub(r'</script>', r'<\/script>', result, flags=re.IGNORECASE)
    
    # 字符转义
    result = result.replace('\\', '\\\\')  # 先转义反斜杠本身
    result = result.replace('\u003c', '\\u003c')  # 防止已有的 < 被重复转义
    
    # 按顺序转义特殊字符
    result = result.replace('&', '\\u0026')
    result = result.replace('<', '\\u003c')
    result = result.replace('>', '\\u003e')
    result = result.replace("'", "\\'")
    result = result.replace('\n', '\\n')
    result = result.replace('\r', '')  # 去掉回车符
    
    return result


def find_variable_content(text, var_name):
    """找到变量赋值的起始和结束位置
    
    返回 (start_pos, end_pos) 其中:
    - start_pos: 变量值开始位置（即开头单引号的下一个位置）
    - end_pos: 变量值结束位置（即结尾单引号的位置）
    """
    pattern = var_name + r"\s*=\s*'"
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"找不到变量 {var_name}")
    
    start_quote = match.end() - 1  # 开头单引号的位置
    value_start = match.end()  # 值开始的位置
    
    # 寻找结束的单引号
    # 由于字符串中可能有 \' 转义，需要逐个字符检查
    pos = value_start
    while pos < len(text):
        if text[pos] == '\\':
            # 转义字符，跳过下一个字符
            pos += 2
            continue
        if text[pos] == "'":
            # 找到了结束的单引号
            return (value_start, pos)
        pos += 1
    
    raise ValueError(f"找不到变量 {var_name} 的结束位置")


def sync_file(source_content, target_file):
    """同步单个目标文件"""
    print(f"\n处理文件: {os.path.basename(target_file)}")
    
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到变量位置
    value_start, value_end = find_variable_content(content, '_fubiaoHtmlContent')
    
    old_value = content[value_start:value_end]
    print(f"  旧内容长度: {len(old_value)} 字符")
    print(f"  新内容长度: {len(source_content)} 字符")
    
    # 替换内容
    new_content = content[:value_start] + source_content + content[value_end:]
    
    # 备份原文件
    backup_file = target_file + '.bak_fubiao_sync'
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  备份文件: {os.path.basename(backup_file)}")
    
    # 写入新文件
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  ✓ 替换完成")
    return True


def main():
    print("=" * 60)
    print("副表HTML内容同步工具")
    print("=" * 60)
    
    # 读取源文件
    print(f"\n读取源文件: {os.path.basename(SOURCE_FILE)}")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()
    print(f"  原始HTML长度: {len(html_content)} 字符")
    
    # 转换为JS字符串格式
    js_string = html_to_js_string(html_content)
    print(f"  JS字符串长度: {len(js_string)} 字符")
    
    # 验证转换结果（检查格式）
    if js_string.startswith('\\u003c!DOCTYPE'):
        print("  ✓ 格式验证通过（以 \\u003c!DOCTYPE 开头）")
    else:
        print(f"  ⚠ 格式警告: 开头为 {js_string[:30]}")
    
    # 同步到每个目标文件
    success_count = 0
    for target_file in TARGET_FILES:
        if not os.path.exists(target_file):
            print(f"\n⚠ 文件不存在，跳过: {os.path.basename(target_file)}")
            continue
        
        try:
            sync_file(js_string, target_file)
            success_count += 1
        except Exception as e:
            print(f"  ✗ 失败: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"同步完成: {success_count}/{len(TARGET_FILE)} 个文件")
    print("=" * 60)


if __name__ == '__main__':
    main()
