import re

# ==================== 1. 修改 print-fubiao.html ====================
with open('print-fubiao.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1.1 修改 pit-p5H 的 rowspan 从 5 改成 7（第③条多了2行）
content = content.replace(
    '<td rowspan="5" data-fb2="pit-p5H">m</td>',
    '<td rowspan="7" data-fb2="pit-p5H">m</td>'
)

# 1.2 替换第③条的2行表格为4行（每个小点2行：水平距离+垂直距离）
old_p3_rows = '''          <tr class="data-row">
            <td colspan="4" rowspan="2" class="align-left">③下述水平距离在0.15m之内时，底坑底与轿厢最低部件之间的自由垂直距离≥0.1m，<br>&nbsp;&nbsp;1)垂直滑动门的部件、护脚板和相邻井道壁<br>&nbsp;&nbsp;2)轿厢最低部件和导轨</td>
            <td colspan="2" data-fb2="pit-p3v1"></td>
            <td colspan="2" data-fb2="pit-p3-result1"></td>
          </tr>
          <tr class="data-row">
            <td colspan="2" data-fb2="pit-p3v2"></td>
            <td colspan="2" data-fb2="pit-p3-result2"></td>
          </tr>'''

new_p3_rows = '''          <tr class="data-row">
            <td colspan="4" rowspan="4" class="align-left">③下述水平距离在0.15m之内时，底坑底与轿厢最低部件之间的自由垂直距离≥0.1m，<br>&nbsp;&nbsp;1)垂直滑动门的部件、护脚板和相邻井道壁<br>&nbsp;&nbsp;2)轿厢最低部件和导轨</td>
            <td colspan="2" style="font-size:11px;">水平距离：<span data-fb2="pit-p3h1"></span> m</td>
            <td colspan="2" data-fb2="pit-p3h1-std" style="font-size:11px;text-align:center;"></td>
          </tr>
          <tr class="data-row">
            <td colspan="2" data-fb2="pit-p3v1">m</td>
            <td colspan="2" data-fb2="pit-p3-result1" style="text-align:center;font-weight:bold;"></td>
          </tr>
          <tr class="data-row">
            <td colspan="2" style="font-size:11px;">水平距离：<span data-fb2="pit-p3h2"></span> m</td>
            <td colspan="2" data-fb2="pit-p3h2-std" style="font-size:11px;text-align:center;"></td>
          </tr>
          <tr class="data-row">
            <td colspan="2" data-fb2="pit-p3v2">m</td>
            <td colspan="2" data-fb2="pit-p3-result2" style="text-align:center;font-weight:bold;"></td>
          </tr>'''

content = content.replace(old_p3_rows, new_p3_rows)

# 1.3 修改JS：添加p3h1/p3h2的显示和判定逻辑
# 找到 pit-p3v1 的 setFb2Text 附近
old_p3_js = '''  setFb2Text('pit-p3v1', pit.p3v1 || '');
  setFb2Text('pit-p3v2', pit.p3v2 || '');'''

new_p3_js = '''  // 第③条水平距离（p3h=p3h1向后兼容） + 判定
  var p3h1 = parseFloat(pit.p3h1 || pit.p3h) || 0;
  var p3h2 = parseFloat(pit.p3h2) || 0;
  if (p3h1 > 0) setFb2Text('pit-p3h1', p3h1);
  if (p3h2 > 0) setFb2Text('pit-p3h2', p3h2);
  // 标准说明
  var p3Std1 = p3h1 > 0 ? (p3h1 <= 0.15 ? '≤0.15→≥0.1m' : '>0.15→≥0.5m') : '';
  var p3Std2 = p3h2 > 0 ? (p3h2 <= 0.15 ? '≤0.15→≥0.1m' : '>0.15→≥0.5m') : '';
  setFb2Text('pit-p3h1-std', p3Std1);
  setFb2Text('pit-p3h2-std', p3Std2);
  // 垂直距离显示
  setFb2Text('pit-p3v1', pit.p3v1 || '');
  setFb2Text('pit-p3v2', pit.p3v2 || '');
  // 第③条判定
  var p3v1Val = parseFloat(pit.p3v1) || 0;
  var p3v2Val = parseFloat(pit.p3v2) || 0;
  function judgeP3(p3hVal, p3vVal) {
    if (p3vVal <= 0 || pitSub <= 0) return '';
    var std = p3hVal > 0 ? (p3hVal <= 0.15 ? 0.1 : 0.5) : 0.5;
    var result = p3vVal - pitSub;
    return result >= std ? '符合' : '不符合';
  }
  setFb2Text('pit-p3-result1', judgeP3(p3h1, p3v1Val));
  setFb2Text('pit-p3-result2', judgeP3(p3h2, p3v2Val));'''

content = content.replace(old_p3_js, new_p3_js)

with open('print-fubiao.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("print-fubiao.html 修改完成")

# ==================== 2. 修改 factory-inspection-v2.html 中的内嵌副表 ====================
with open('factory-inspection-v2.html', 'r', encoding='utf-8', errors='ignore') as f:
    main_content = f.read()

# 2.1 内嵌副表HTML中的rowspan修改
main_content = main_content.replace(
    'rowspan=\\\\"5\\\\" data-fb2=\\\\"pit-p5H\\\\"',
    'rowspan=\\\\"7\\\\" data-fb2=\\\\"pit-p5H\\\\"'
)

# 2.2 内嵌副表第③条表格行替换（注意转义）
old_main_p3 = '''<td colspan=\\\\"4\\\\" rowspan=\\\\"2\\\\" class=\\\\"align-left\\\\">③下述水平距离在0.15m之内时，底坑底与轿厢最低部件之间的自由垂直距离≥0.1m，<br>&nbsp;&nbsp;1)垂直滑动门的部件、护脚板和相邻井道壁<br>&nbsp;&nbsp;2)轿厢最低部件和导轨</td>\\n            <td colspan=\\\\"2\\\\" data-fb2=\\\\"pit-p3v1\\\\"></td>\\n            <td colspan=\\\\"2\\\\" data-fb2=\\\\"pit-p3-result1\\\\"></td>\\n          </tr>\\n          <tr class=\\\\"data-row\\\\">\\n            <td colspan=\\\\"2\\\\" data-fb2=\\\\"pit-p3v2\\\\"></td>\\n            <td colspan=\\\\"2\\\\" data-fb2=\\\\"pit-p3-result2\\\\"></td>'''

new_main_p3 = '''<td colspan=\\\\"4\\\\" rowspan=\\\\"4\\\\" class=\\\\"align-left\\\\">③下述水平距离在0.15m之内时，底坑底与轿厢最低部件之间的自由垂直距离≥0.1m，<br>&nbsp;&nbsp;1)垂直滑动门的部件、护脚板和相邻井道壁<br>&nbsp;&nbsp;2)轿厢最低部件和导轨</td>\\n            <td colspan=\\\\"2\\\\" style=\\\\"font-size:11px;\\\\">水平距离：<span data-fb2=\\\\"pit-p3h1\\\\"></span> m</td>\\n            <td colspan=\\\\"2\\\\" data-fb2=\\\\"pit-p3h1-std\\" style=\\\\"font-size:11px;text-align:center;\\\\"></td>\\n          </tr>\\n          <tr class=\\\\"data-row\\\\">\\n            <td colspan=\\\\"2\\\\" data-fb2=\\\\"pit-p3v1\\\\">m</td>\\n            <td colspan=\\\\"2\\\\" data-fb2=\\\\"pit-p3-result1\\" style=\\\\"text-align:center;font-weight:bold;\\\\"></td>\\n          </tr>\\n          <tr class=\\\\"data-row\\\\">\\n            <td colspan=\\\\"2\\\\" style=\\\\"font-size:11px;\\\\">水平距离：<span data-fb2=\\\\"pit-p3h2\\\\"></span> m</td>\\n            <td colspan=\\\\"2\\\\" data-fb2=\\\\"pit-p3h2-std\\" style=\\\\"font-size:11px;text-align:center;\\\\"></td>\\n          </tr>\\n          <tr class=\\\\"data-row\\\\">\\n            <td colspan=\\\\"2\\\\" data-fb2=\\\\"pit-p3v2\\\\">m</td>\\n            <td colspan=\\\\"2\\\\" data-fb2=\\\\"pit-p3-result2\\" style=\\\\"text-align:center;font-weight:bold;\\\\"></td>'''

if old_main_p3 in main_content:
    main_content = main_content.replace(old_main_p3, new_main_p3)
    print("factory-inspection-v2.html 内嵌副表表格替换成功")
else:
    print("WARNING: 内嵌副表表格行未找到，尝试其他方式...")
    # 尝试找位置
    idx = main_content.find('pit-p3v1')
    print(f"pit-p3v1 位置: {idx}")

# 2.3 内嵌副表JS中的p3显示和判定替换
old_main_p3_js = '''setFb2Text(\\'pit-p3v1\\', pit.p3v1 || \\'\\');\\n  setFb2Text(\\'pit-p3v2\\', pit.p3v2 || \\'\\');'''

new_main_p3_js = '''// 第③条水平距离（p3h=p3h1向后兼容） + 判定\\n  var p3h1 = parseFloat(pit.p3h1 || pit.p3h) || 0;\\n  var p3h2 = parseFloat(pit.p3h2) || 0;\\n  if (p3h1 > 0) setFb2Text(\\'pit-p3h1\\', p3h1);\\n  if (p3h2 > 0) setFb2Text(\\'pit-p3h2\\', p3h2);\\n  var p3Std1 = p3h1 > 0 ? (p3h1 <= 0.15 ? \\'≤0.15→≥0.1m\\' : \\'>0.15→≥0.5m\\') : \\'\\';\\n  var p3Std2 = p3h2 > 0 ? (p3h2 <= 0.15 ? \\'≤0.15→≥0.1m\\' : \\'>0.15→≥0.5m\\') : \\'\\';\\n  setFb2Text(\\'pit-p3h1-std\\', p3Std1);\\n  setFb2Text(\\'pit-p3h2-std\\', p3Std2);\\n  setFb2Text(\\'pit-p3v1\\', pit.p3v1 || \\'\\');\\n  setFb2Text(\\'pit-p3v2\\', pit.p3v2 || \\'\\');\\n  var p3v1Val = parseFloat(pit.p3v1) || 0;\\n  var p3v2Val = parseFloat(pit.p3v2) || 0;\\n  function judgeP3(p3hVal, p3vVal) {\\n    if (p3vVal <= 0 || pitSub <= 0) return \\'\\';\\n    var std = p3hVal > 0 ? (p3hVal <= 0.15 ? 0.1 : 0.5) : 0.5;\\n    var result = p3vVal - pitSub;\\n    return result >= std ? \\'符合\\' : \\'不符合\\';\\n  }\\n  setFb2Text(\\'pit-p3-result1\\', judgeP3(p3h1, p3v1Val));\\n  setFb2Text(\\'pit-p3-result2\\', judgeP3(p3h2, p3v2Val));'''

if old_main_p3_js in main_content:
    main_content = main_content.replace(old_main_p3_js, new_main_p3_js)
    print("factory-inspection-v2.html 内嵌副表JS替换成功")
else:
    print("WARNING: 内嵌副表JS未找到")
    idx = main_content.find("pit-p3v1\\'")
    print(f"位置: {idx}")
    if idx > 0:
        print(main_content[idx-100:idx+200])

# 2.4 数据结构增加 p3h2
old_struct1 = "底坑空间:{p1:'',p2:'',p3h:'',p3v1:'',p3v2:'',p4:'',p5L:'',p5W:'',p5H:''}"
new_struct1 = "底坑空间:{p1:'',p2:'',p3h:'',p3h1:'',p3v1:'',p3h2:'',p3v2:'',p4:'',p5L:'',p5W:'',p5H:''}"
main_content = main_content.replace(old_struct1, new_struct1)

# 2.5 初始化数据结构增加 p3h2
old_init1 = "att2.底坑空间 = {p1:'',p2:'',p3h:'',p3v1:'',p3v2:'',p4:'',p5L:'',p5W:'',p5H:''}"
new_init1 = "att2.底坑空间 = {p1:'',p2:'',p3h:'',p3h1:'',p3v1:'',p3h2:'',p3v2:'',p4:'',p5L:'',p5W:'',p5H:''}"
main_content = main_content.replace(old_init1, new_init1)

print("factory-inspection-v2.html 数据结构更新完成")

with open('factory-inspection-v2.html', 'w', encoding='utf-8') as f:
    f.write(main_content)

print("factory-inspection-v2.html 保存完成")

