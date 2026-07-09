import re

with open('factory-inspection-v2.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复1: loadProjects中的格式判断
# 把简单的 Array.isArray(data) 判断改成更精确的格式检测
old_load_check = """      // 判断是旧格式(数组)还是新格式
      if (Array.isArray(data)) {
        // 旧格式: tasks 数组，需要迁移
        migrateOldTasks(data);"""

new_load_check = """      // 判断是旧格式(任务数组)还是新格式(项目数组)
      if (Array.isArray(data)) {
        // 新格式特征：数组元素有 tasks 字段（项目对象）
        // 旧格式特征：数组元素有 checks 字段（任务对象）
        var isNewFormat = data.length > 0 && data[0] && typeof data[0] === 'object' && 'tasks' in data[0];
        if (!isNewFormat) {
          // 旧格式: tasks 数组，需要迁移
          migrateOldTasks(data);"""

if old_load_check in content:
    content = content.replace(old_load_check, new_load_check)
    # 还要补一个闭合大括号（因为多了一层if）
    # 找到 migrateOldTasks(data); 后面的 return; 和 }
    old_return = """        migrateOldTasks(data);
        return;
      }
      projects = data;"""
    new_return = """          migrateOldTasks(data);
          return;
        }
      }
      projects = data;"""
    if old_return in content:
        content = content.replace(old_return, new_return)
        print("修复1完成: loadProjects格式判断")
    else:
        print("修复1失败: 找不到return部分")
else:
    print("修复1失败: 找不到判断位置")

# 修复2: 数据异常检查中的判断（备份恢复处也需要同样的逻辑）
# 907943附近，检查是否需要从备份恢复
# 这里主要是判断数据是否有效，新格式项目数组也是有效的
# 先看看具体代码
backup_check_pos = content.find("【v129】数据异常检查")
if backup_check_pos > 0:
    snippet = content[backup_check_pos:backup_check_pos+500]
    print("\n备份检查区域:")
    print(snippet[:300])

with open('factory-inspection-v2.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n修改完成")
