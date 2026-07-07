// 检查表主表HTML生成（三栏独立布局，水平大类标题）- 按纸质版PDF格式
function buildCheckItemsHTML(task, project, dateStr, pageNum) {
  // 纸质版PDF布局：每页三栏独立div(float:left)，每栏内多个大类表格
  // 每栏大类结构：水平标题行(背景色) + 序|检查内容|结论 三列表格
  // Page 1: 左栏(A,B,C) 中栏(D,E) 右栏(F,G)
  // Page 2: 左栏(H,I,J) 中栏(K,L,M,N) 右栏(O,P,Q,R)

  __LOGO_LINE__

  // 构建id到item的映射
  var itemMap = {};
  checkItems.forEach(function(it) { itemMap[it.id] = it; });

  // 每页三栏的大类配置
  var pageConfig;
  if (pageNum === 1) {
    pageConfig = {
      col1: [
        {label: '技术资料与铭牌(可识别标志)的一致性检查', ids: [1,2,3,4,5,6,7,8,9,10,11,12], special: 'techdata'},
        {label: '机器空间及通道', ids: [13,14,15,16,17,18,19,20,21]},
        {label: '机房电气设备与标识', ids: [22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]}
      ],
      col2: [
        {label: '功能检查', ids: (function(){var a=[];for(var i=37;i<=68;i++)a.push(i);return a;})()},
        {label: '安全开关', ids: [69,70,71,72,73,74]}
      ],
      col3: [
        {label: '试验', ids: (function(){var a=[];for(var i=75;i<=99;i++)a.push(i);return a;})()},
        {label: '驱动主机承重及导向', ids: [100,101,102,103,104,105,106,107,108,109,110,111,112]}
      ]
    };
  } else {
    pageConfig = {
      col1: [
        {label: '层门与轿门', ids: (function(){var a=[];for(var i=113;i<=137;i++)a.push(i);return a;})()},
        {label: '导轨及固定支架', ids: [138,139,140,141,142]},
        {label: '悬挂与补偿装置', ids: [143,144,145,146,147,148,149,150,151]}
      ],
      col2: [
        {label: '轿顶设备', ids: (function(){var a=[];for(var i=152;i<=166;i++)a.push(i);return a;})()},
        {label: '轿顶护栏', ids: [167,168,169,170,171]},
        {label: '轿厢与对重', ids: [172,173,174,175,176,177,178,179]},
        {label: '轿底部件', ids: [180,181,182,183,184,185,186,187,188,189,190]}
      ],
      col3: [
        {label: '限速器与夹绳器', ids: [191,192,193,194,195,196,197,198,199]},
        {label: '井道部件及空间', ids: [200,201,202,203,204,205,206,207,208,209,210,211]},
        {label: '底坑设备', ids: [212,213,214,215,216,217,218,219]},
        {label: '感官检查', ids: [220,221,222,223,224,225,226,227,228,229]}
      ]
    };
  }

  // 附表引用标注映射
  var appendixMap = {
    113: '(附表1)', 114: '(附表1)', 115: '(附表1)', 116: '(附表1)', 117: '(附表1)',
    138: '(附表4)', 140: '(附表3)',
    143: '(附表6)',
    76: '(附表5)', 89: '(附表7)',
    209: '(附表2)', 210: '(附表2)', 211: '(附表2)'
  };

  // 生成一栏内的所有大类表格HTML
  function buildColumnHTML(groups) {
    var html = '';
    groups.forEach(function(g) {
      var items = [];
      g.ids.forEach(function(id) {
        if (itemMap[id]) {
          var it = itemMap[id];
          var c = task.checks[id] || {};
          var displayName = getPDFDisplayItemName(it, c);
          if (appendixMap[id]) displayName += appendixMap[id];
          var res = c.s === 'ok' ? '\u221a' : (c.s === 'ng' ? '\u00d7' : (c.s === 'na' ? '/' : (c.v || '')));
          items.push({id: id, name: displayName, result: res, note: c.n || ''});
        }
      });

      if (items.length === 0) return;

      // 大类标题行（水平，占满整栏宽度，背景色）
      html += '<table style="width:100%;border-collapse:collapse;font-size:8px;table-layout:fixed;margin-bottom:0;">';
      html += '<tr style="background:#e8e8e8;font-weight:bold;text-align:center;">';
      if (g.special === 'techdata') {
        html += '<td style="border:1px solid #000;padding:2px 3px;" colspan="2">' + escHtml(g.label) + '</td>';
      } else {
        html += '<td style="border:1px solid #000;padding:2px 3px;" colspan="3">' + escHtml(g.label) + '</td>';
      }
      html += '</tr>';

      // 表头行：序|检查内容|结论
      if (g.special === 'techdata') {
        html += '<tr style="background:#f5f5f5;text-align:center;font-weight:bold;">';
        html += '<td style="border:1px solid #000;padding:1px 2px;width:55%;">项目</td>';
        html += '<td style="border:1px solid #000;padding:1px 2px;width:45%;">型号编号/结论</td>';
        html += '</tr>';
      } else {
        html += '<tr style="background:#f5f5f5;text-align:center;font-weight:bold;">';
        html += '<td style="border:1px solid #000;padding:1px 2px;width:12%;">序</td>';
        html += '<td style="border:1px solid #000;padding:1px 2px;width:70%;">检查内容</td>';
        html += '<td style="border:1px solid #000;padding:1px 2px;width:18%;">结论</td>';
        html += '</tr>';
      }

      // 数据行
      items.forEach(function(item) {
        html += '<tr>';
        if (g.special === 'techdata') {
          html += '<td style="border:1px solid #000;padding:1px 2px;">' + escHtml(item.name) + '</td>';
          html += '<td style="border:1px solid #000;padding:1px 2px;text-align:center;">' + item.result + '</td>';
        } else {
          html += '<td style="border:1px solid #000;padding:1px 2px;text-align:center;">' + item.id + '</td>';
          html += '<td style="border:1px solid #000;padding:1px 2px;">' + escHtml(item.name) + (item.note ? '<br><span style="color:red;font-size:7px;">备注:'+escHtml(item.note)+'</span>' : '') + '</td>';
          html += '<td style="border:1px solid #000;padding:1px 2px;text-align:center;">' + item.result + '</td>';
        }
        html += '</tr>';
      });

      html += '</table>';
    });
    return html;
  }

  var h = '<div style="font-family:\'PingFang SC\',\'Heiti SC\',sans-serif;font-size:8px;position:relative;width:100%;">';
  // 页眉
  h += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">';
  h += '<img src="' + logoBase64 + '" style="height:20px;width:auto;">';
  h += '<span style="font-size:12px;font-weight:bold;">厂检调试记录单</span>';
  h += '<span>产品编号：' + escHtml(task.prodNo||'') + '</span>';
  h += '</div>';

  // 三栏独立布局
  h += '<div style="width:100%;overflow:hidden;">';
  // 左栏
  h += '<div style="float:left;width:33.33%;box-sizing:border-box;padding-right:2px;">';
  h += buildColumnHTML(pageConfig.col1);
  h += '</div>';
  // 中栏
  h += '<div style="float:left;width:33.33%;box-sizing:border-box;padding:0 1px;">';
  h += buildColumnHTML(pageConfig.col2);
  h += '</div>';
  // 右栏
  h += '<div style="float:left;width:33.33%;box-sizing:border-box;padding-left:2px;">';
  h += buildColumnHTML(pageConfig.col3);
  h += '</div>';
  h += '</div>';

  // 清除浮动
  h += '<div style="clear:both;"></div>';

  // 结论说明 + 页脚
  h += '<div style="margin-top:4px;font-size:7px;color:#666;">结论选项：\u221a符合 \u00d7不符合 /不适用，或写入测量值。</div>';
  h += '<div style="position:absolute;bottom:0;left:0;right:0;text-align:center;font-size:8px;">— ' + pageNum + ' —</div>';
  h += '</div>';

  return h;
}
