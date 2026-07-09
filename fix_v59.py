# -*- coding: utf-8 -*-
import re

with open('print-fubiao.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 1. 顶部空间：①-④点 检验结果拆两列（左数值 右判断）
# ============================================================
# 原来：<td colspan="2" data-fb2="top-s1-result" style="text-align:center;font-weight:bold;color:#000;"></td>
# 改成两个td：
#   <td data-fb2="top-s1-value" style="text-align:center;color:#000;">m</td>
#   <td data-fb2="top-s1-result" style="text-align:center;font-weight:bold;color:#000;"></td>

for i in range(1, 5):
    old = f'<td colspan="2" data-fb2="top-s{i}-result" style="text-align:center;font-weight:bold;color:#000;"></td>'
    new = f'<td data-fb2="top-s{i}-value" style="text-align:center;color:#000;">m</td>\n            <td data-fb2="top-s{i}-result" style="text-align:center;font-weight:bold;color:#000;"></td>'
    content = content.replace(old, new)

# ============================================================
# 2. 底坑空间：①②④点 检验结果拆两列
# ============================================================
for key in ['pit-p1', 'pit-p2', 'pit-p4']:
    old = f'<td colspan="2" data-fb2="{key}-result" style="text-align:center;font-weight:bold;color:#000;"></td>'
    new = f'<td data-fb2="{key}-value" style="text-align:center;color:#000;">m</td>\n            <td data-fb2="{key}-result" style="text-align:center;font-weight:bold;color:#000;"></td>'
    content = content.replace(old, new)

# ============================================================
# 3. 底坑第③条两个小点：检验结果拆两列
# ============================================================
# 第1小点
old_p3_1 = '<td colspan="2" data-fb2="pit-p3-result1" style="text-align:center;font-weight:bold;"></td>'
new_p3_1 = '<td data-fb2="pit-p3-value1" style="text-align:center;color:#000;">m</td>\n            <td data-fb2="pit-p3-result1" style="text-align:center;font-weight:bold;"></td>'
content = content.replace(old_p3_1, new_p3_1)

# 第2小点
old_p3_2 = '<td colspan="2" data-fb2="pit-p3-result2" style="text-align:center;font-weight:bold;"></td>'
new_p3_2 = '<td data-fb2="pit-p3-value2" style="text-align:center;color:#000;">m</td>\n            <td data-fb2="pit-p3-result2" style="text-align:center;font-weight:bold;"></td>'
content = content.replace(old_p3_2, new_p3_2)

# ============================================================
# 4. JS逻辑修改：fillFb2函数
# ============================================================

# 4a. 顶部空间数值列填充（净值 = 测量值 - topSub）
# 在 setFb2Text('top-s1-result', judgeTop('s1', '0.1+0.035v2')); 之前加数值填充
old_top_result = """  setFb2Text('top-s1-result', judgeTop('s1', '0.1+0.035v2'));
  setFb2Text('top-s2-result', judgeTop('s2', '1.0+0.035v2'));
  setFb2Text('top-s3-result', judgeTop('s3', '0.3+0.035v2'));
  setFb2Text('top-s4-result', judgeTop('s4', '0.1+0.035v2'));"""

new_top_result = """  // 顶部空间数值列（净值 = 测量值 - 对重缓冲压缩量）
  function setTopValue(key) {
    var val = parseFloat(top[key]) || 0;
    if (val > 0 && topSub > 0) {
      setFb2Text('top-' + key + '-value', (val - topSub).toFixed(3));
    } else if (val > 0) {
      setFb2Text('top-' + key + '-value', val);
    }
  }
  setTopValue('s1');
  setTopValue('s2');
  setTopValue('s3');
  setTopValue('s4');
  setFb2Text('top-s1-result', judgeTop('s1', '0.1+0.035v2'));
  setFb2Text('top-s2-result', judgeTop('s2', '1.0+0.035v2'));
  setFb2Text('top-s3-result', judgeTop('s3', '0.3+0.035v2'));
  setFb2Text('top-s4-result', judgeTop('s4', '0.1+0.035v2'));"""

content = content.replace(old_top_result, new_top_result)

# 4b. 底坑①②④数值列填充 + 第③条判定逻辑修改
# 先找到底坑部分的judge函数
# 把 pit-p1/pit-p2/pit-p4 的数值列加上
old_pit_judge_section = """  function judgePit_p1() {
    var val = parseFloat(pit.p1) || 0;
    if (val <= 0 || pitSub <= 0) return '';
    var result = val - pitSub;
    return result >= 0.5 ? '符合' : '不符合';
  }
  function judgePit_p2() {
    var val = parseFloat(pit.p2) || 0;
    if (val <= 0 || pitSub <= 0) return '';
    var result = val - pitSub;
    return result >= 0.3 ? '符合' : '不符合';
  }"""

# 先看看后面还有什么
# 让我找 pit-p1-result 的赋值
old_pit_results = """  setFb2Text('pit-p1-result', judgePit_p1());
  setFb2Text('pit-p2-result', judgePit_p2());"""

# 不对，让我先看看底坑结果设置的位置
# 从之前的阅读看，judgePit_p1/p2定义后，后面应该有调用
# 让我用更稳妥的方式找

# 先替换judgeP3函数，改成第1小点两档、第2小点等比例
old_judgeP3 = """  function judgeP3(p3hVal, p3vVal) {
    if (p3vVal <= 0 || pitSub <= 0) return '';
    var std = p3hVal > 0 ? (p3hVal <= 0.15 ? 0.1 : 0.5) : 0.5;
    var result = p3vVal - pitSub;
    return result >= std ? '符合' : '不符合';
  }
  setFb2Text('pit-p3-result1', judgeP3(p3h1, p3v1Val));
  setFb2Text('pit-p3-result2', judgeP3(p3h2, p3v2Val));"""

new_judgeP3 = """  // 第③条第1小点（护脚板）：两档判定
  function judgeP3_1(p3hVal, p3vVal) {
    if (p3vVal <= 0 || pitSub <= 0) return '';
    var std = p3hVal > 0 ? (p3hVal <= 0.15 ? 0.1 : 0.5) : 0.5;
    var result = p3vVal - pitSub;
    return result >= std ? '符合' : '不符合';
  }
  // 第③条第2小点（导轨）：等比例判定（0.15m→0.1m, 0.5m→0.5m, 中间等比例）
  function judgeP3_2(p3hVal, p3vVal) {
    if (p3vVal <= 0 || pitSub <= 0) return '';
    var result = p3vVal - pitSub;
    var std;
    if (p3hVal <= 0.15) {
      std = 0.1;
    } else if (p3hVal >= 0.5) {
      std = 0.5;
    } else {
      std = 0.1 + (p3hVal - 0.15) * 0.4 / 0.35;
    }
    return result >= std ? '符合' : '不符合';
  }
  // 第③条数值列（净值）
  function setP3Value(idx, p3vVal) {
    if (p3vVal > 0 && pitSub > 0) {
      setFb2Text('pit-p3-value' + idx, (p3vVal - pitSub).toFixed(3));
    } else if (p3vVal > 0) {
      setFb2Text('pit-p3-value' + idx, p3vVal);
    }
  }
  setP3Value(1, p3v1Val);
  setP3Value(2, p3v2Val);
  setFb2Text('pit-p3-result1', judgeP3_1(p3h1, p3v1Val));
  setFb2Text('pit-p3-result2', judgeP3_2(p3h2, p3v2Val));"""

content = content.replace(old_judgeP3, new_judgeP3)

# 4c. 底坑p1/p2/p4数值列填充
# 先找到 setFb2Text('pit-p1-result', ...) 的位置
# 在 judgePit_p1 定义后，应该有调用
# 让我搜索更精确的模式

# 找 pit-p1-result 的赋值行
old_p1_result = "setFb2Text('pit-p1-result', judgePit_p1());"
new_p1_result = """// 底坑①数值列（净值）
  var _p1Val = parseFloat(pit.p1) || 0;
  if (_p1Val > 0 && pitSub > 0) {
    setFb2Text('pit-p1-value', (_p1Val - pitSub).toFixed(3));
  } else if (_p1Val > 0) {
    setFb2Text('pit-p1-value', _p1Val);
  }
  setFb2Text('pit-p1-result', judgePit_p1());"""
content = content.replace(old_p1_result, new_p1_result)

old_p2_result = "setFb2Text('pit-p2-result', judgePit_p2());"
new_p2_result = """// 底坑②数值列（净值）
  var _p2Val = parseFloat(pit.p2) || 0;
  if (_p2Val > 0 && pitSub > 0) {
    setFb2Text('pit-p2-value', (_p2Val - pitSub).toFixed(3));
  } else if (_p2Val > 0) {
    setFb2Text('pit-p2-value', _p2Val);
  }
  setFb2Text('pit-p2-result', judgePit_p2());"""
content = content.replace(old_p2_result, new_p2_result)

# 底坑④ - 找judgePit_p4函数和调用
# 先看看有没有 judgePit_p4
if 'judgePit_p4' in content:
    old_p4_result = "setFb2Text('pit-p4-result', judgePit_p4());"
    new_p4_result = """// 底坑④数值列（净值）
  var _p4Val = parseFloat(pit.p4) || 0;
  if (_p4Val > 0 && pitSub > 0) {
    setFb2Text('pit-p4-value', (_p4Val - pitSub).toFixed(3));
  } else if (_p4Val > 0) {
    setFb2Text('pit-p4-value', _p4Val);
  }
  setFb2Text('pit-p4-result', judgePit_p4());"""
    content = content.replace(old_p4_result, new_p4_result)

with open('print-fubiao.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("print-fubiao.html 修改完成")
