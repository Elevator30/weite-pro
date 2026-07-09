with open('factory-inspection-v2.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到损坏的代码块并替换
old_broken = """      // 判断是旧格式(任务数组)还是新格式(项目数组)
      if (Array.isArray(data)) {
        // 新格式特征：数组元素有 tasks 字段（项目对象）
        // 旧格式特征：数组元素有 checks 字段（任务对象）
        var isNewFormat = data.length > 0 && data[0] && typeof data[0] === 'object' && 'tasks' in data[0];
        if (!isNewFormat) {
          // 旧格式: tasks 数组，需要迁移
          migrateOldTasks(data);
        return;
      }
      // 【v129】数据异常检查"""

new_fixed = """      // 判断是旧格式(任务数组)还是新格式(项目数组)
      if (Array.isArray(data)) {
        // 新格式特征：数组元素有 tasks 字段（项目对象）
        // 旧格式特征：数组元素有 checks 字段（任务对象）
        var isNewFormat = data.length > 0 && data[0] && typeof data[0] === 'object' && 'tasks' in data[0];
        if (!isNewFormat) {
          // 旧格式: tasks 数组，需要迁移
          migrateOldTasks(data);
          return;
        }
      }
      projects = data;
      // 【v129】数据异常检查"""

if old_broken in content:
    content = content.replace(old_broken, new_fixed)
    print("修复成功")
else:
    print("找不到损坏的代码块，尝试其他方式")
    # 打印周围内容看看
    pos = content.find('判断是旧格式(任务数组)')
    if pos > 0:
        print(repr(content[pos:pos+600]))

with open('factory-inspection-v2.html', 'w', encoding='utf-8') as f:
    f.write(content)
