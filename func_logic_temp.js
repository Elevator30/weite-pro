function escHtml(s) {
    if (s == null) return '';
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  // id->item映射
  var itemMap = {};
  if (typeof checkItems !== 'undefined') {
    checkItems.forEach(function(it) { itemMap[it.id] = it; });
  }
  var hiddenIds = (typeof hiddenCheckIds !== 'undefined') ? hiddenCheckIds : [];
  function isVisible(id) { return hiddenIds.indexOf(id) === -1; }

  // 获取结论显示
  function getResult(id) {
    var val = task.checkResults ? task.checkResults[id] : '';
    if (val === undefined || val === null || val === '') return '';
    if (val === '符合' || val === '√') return '√';
    if (val === '不符合' || val === '×') return '×';
    if (val === '不适用' || val === '/') return '/';
    return val;
  }

  // 配置
  var rowH = 16;          // 数据行行高
  var titleW = 20;        // 竖排标题列宽
  var seqW = 22;          // 序号列宽
  var resultW = 28;       // 结论列宽
  var headerH = 18;       // 表头行高
  var fontSize = 8;       // 正文字号
  var titleFontSize = 8;  // 标题字号

  // 生成范围ID数组
  function rangeIds(start, end) {
    var a = [];
    for (var i = start; i <= end; i++) a.push(i);
    return a;
  }

  // 构建一栏的SVG + HTML（竖排标题版）
  // groups: [{label, ids, special?}]
  // colWidth: 栏总宽度
  function buildColumnSvg(groups, colWidth) {
    var contentW = colWidth - titleW - seqW - resultW;
    
    // 计算总高度和每个分组的信息
    var totalRows = 0;
    var groupInfo = [];
    for (var g = 0; g < groups.length; g++) {
      var grp = groups[g];
      var visibleIds = [];
      for (var i = 0; i < grp.ids.length; i++) {
        if (isVisible(grp.ids[i])) visibleIds.push(grp.ids[i]);
      }
      var rows = visibleIds.length;
      groupInfo.push({
        label: grp.label,
        ids: visibleIds,
        rows: rows,
        startRow: totalRows,
        special: grp.special
      });
      totalRows += rows;
    }
    
    var totalH = headerH + totalRows * rowH;
    
    // SVG底图
    var svg = '';
    svg += '<svg width="' + colWidth + '" height="' + totalH + '" xmlns="http://www.w3.org/2000/svg" style="display:block;">';
    
    // 外框
    svg += '<rect x="0" y="0" width="' + colWidth + '" height="' + totalH + '" fill="none" stroke="#000" stroke-width="0.5"/>';
    
    // 表头行背景
    svg += '<rect x="0" y="0" width="' + colWidth + '" height="' + headerH + '" fill="#fff" stroke="#000" stroke-width="0.5"/>';
    
    // 竖线：标题列右边界
    svg += '<line x1="' + titleW + '" y1="0" x2="' + titleW + '" y2="' + totalH + '" stroke="#000" stroke-width="0.5"/>';
    // 竖线：序号列右边界
    svg += '<line x1="' + (titleW + seqW) + '" y1="0" x2="' + (titleW + seqW) + '" y2="' + totalH + '" stroke="#000" stroke-width="0.5"/>';
    // 竖线：内容列右边界
    var contentRight = titleW + seqW + contentW;
    svg += '<line x1="' + contentRight + '" y1="0" x2="' + contentRight + '" y2="' + totalH + '" stroke="#000" stroke-width="0.5"/>';
    
    // 表头分隔线
    svg += '<line x1="0" y1="' + headerH + '" x2="' + colWidth + '" y2="' + headerH + '" stroke="#000" stroke-width="0.5"/>';
    
    // 表头文字
    // 检查内容（跨序号+内容列）
    var checkContentX = titleW + seqW / 2 + contentW / 2;
    svg += '<text x="' + (titleW + seqW + contentW/2) + '" y="' + (headerH/2 + 3) + '" text-anchor="middle" font-size="9" font-weight="bold">检查内容</text>';
    // 结论
    svg += '<text x="' + (contentRight + resultW/2) + '" y="' + (headerH/2 + 3) + '" text-anchor="middle" font-size="9" font-weight="bold">结论</text>';
    
    // 每个分组
    for (var gi = 0; gi < groupInfo.length; gi++) {
      var info = groupInfo[gi];
      var groupTop = headerH + info.startRow * rowH;
      var groupH = info.rows * rowH;
      
      // 分组标题背景（灰色）
      svg += '<rect x="0" y="' + groupTop + '" width="' + titleW + '" height="' + groupH + '" fill="#fff" stroke="#000" stroke-width="0.5"/>';
      
      // 分组标题文字（竖排，从下到上阅读）
      var titleText = info.label;
      var titleY = groupTop + groupH / 2;
      var titleX = titleW / 2;
      // 使用writing-mode效果：用transform旋转
      svg += '<text x="' + titleX + '" y="' + titleY + '" text-anchor="middle" font-size="8" font-weight="bold" transform="rotate(-90 ' + titleX + ' ' + titleY + ')">' + escHtml(titleText) + '</text>';
      
      // 数据行横线
      for (var r = 1; r < info.rows; r++) {
        var lineY = groupTop + r * rowH;
        svg += '<line x1="' + titleW + '" y1="' + lineY + '" x2="' + colWidth + '" y2="' + lineY + '" stroke="#000" stroke-width="0.3"/>';
      }
    }
    
    svg += '</svg>';
    
    // 绝对定位的HTML文字（序号、检查内容、结论输入框）
    var html = '';
    html += '<div style="position:relative;width:' + colWidth + 'px;">';
    html += svg;
    html += '<div style="position:absolute;top:0;left:0;width:' + colWidth + 'px;height:' + totalH + 'px;pointer-events:none;">';
    
    for (var gi2 = 0; gi2 < groupInfo.length; gi2++) {
      var info2 = groupInfo[gi2];
      var groupTop2 = headerH + info2.startRow * rowH;
      
      for (var r2 = 0; r2 < info2.ids.length; r2++) {
        var id = info2.ids[r2];
        var item = itemMap[id];
        if (!item) continue;
        var rowTop = groupTop2 + r2 * rowH;
        var rowCenter = rowTop + rowH / 2 + 3;
        
        // 序号（每类独立编号，从1开始）
        var seqNum = r2 + 1;
        html += '<div style="position:absolute;top:' + rowTop + 'px;left:' + titleW + 'px;width:' + seqW + 'px;height:' + rowH + 'px;line-height:' + rowH + 'px;text-align:center;font-size:' + fontSize + 'px;">' + seqNum + '</div>';
        
        // 检查内容
        var contentLeft = titleW + seqW + 2;
        var contentWidth = contentW - 4;
        html += '<div style="position:absolute;top:' + rowTop + 'px;left:' + contentLeft + 'px;width:' + contentWidth + 'px;height:' + rowH + 'px;line-height:' + rowH + 'px;font-size:' + fontSize + 'px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;" title="' + escHtml(item.name || item.content || '') + '">' + escHtml(item.name || item.content || '') + '</div>';
        
        // 结论（可点击编辑）
        var resultLeft = contentRight + 2;
        var resultVal = getResult(id);
        html += '<div style="position:absolute;top:' + rowTop + 'px;left:' + resultLeft + 'px;width:' + (resultW - 4) + 'px;height:' + rowH + 'px;line-height:' + rowH + 'px;text-align:center;font-size:' + fontSize + 'px;pointer-events:auto;cursor:pointer;" onclick="toggleResult(' + id + ')" data-id="' + id + '" class="result-cell">' + resultVal + '</div>';
      }
    }
    
    html += '</div></div>';
    return html;
  }

  // 页面配置 - 竖排标题版
  var pageConfig;
  if (pageNum === 1) {
    pageConfig = {
      col1: [
        {label: '技术资料与铭牌(可识别标志)的一致性检查', ids: rangeIds(1,12)},
        {label: '机器空间及通道', ids: rangeIds(13,21)},
        {label: '机房电气设备与标识', ids: rangeIds(22,36)}
      ],
      col2: [
        {label: '功能检查', ids: rangeIds(37,68)},
        {label: '安全开关', ids: rangeIds(69,74)}
      ],
      col3: [
        {label: '试验', ids: rangeIds(75,99)},
        {label: '驱动主机、承重及导向', ids: rangeIds(100,112)}
      ]
    };
  } else {
    pageConfig = {
      col1: [
        {label: '层门与轿门', ids: rangeIds(113,137)},
        {label: '导轨及固定支架', ids: rangeIds(138,142)},
        {label: '悬挂与补偿装置', ids: rangeIds(143,151)}
      ],
      col2: [
        {label: '轿顶设备', ids: rangeIds(152,166)},
        {label: '轿顶护栏', ids: rangeIds(167,171)},
        {label: '轿厢与对重', ids: rangeIds(172,179)},
        {label: '轿底部件', ids: rangeIds(180,190)}
      ],
      col3: [
        {label: '限速器与夹绳器', ids: rangeIds(191,199)},
        {label: '井道部件及空间', ids: rangeIds(200,211)},
        {label: '底坑设备', ids: rangeIds(212,219)},
        {label: '感官检查', ids: rangeIds(220,229)}
      ]
    };
  }

  // 计算每栏宽度
  var colWidth = 250;
  
  // 构建页面
  var h = '';
  h += '<div style="font-family:Arial,sans-serif;font-size:9px;position:relative;padding:8px;box-sizing:border-box;width:100%;">';
  
  // 页眉
  h += '<div style="position:relative;margin-bottom:6px;padding-bottom:4px;border-bottom:1px solid #000;overflow:hidden;">';
  h += '<div style="float:left;width:20%;"><img src="' + logoBase64 + '" style="height:22px;width:auto;"></div>';
  h += '<div style="float:left;width:60%;text-align:center;font-size:14px;font-weight:bold;line-height:22px;">厂检调试记录单</div>';
  h += '<div style="float:right;width:20%;text-align:right;font-size:9px;line-height:22px;">产品编号：' + escHtml(task.prodNo || task.productNo || '') + '</div>';
  h += '</div>';
  
  // 三栏布局 - float独立，高度自适
  h += '<div style="overflow:hidden;">';
  h += '<div style="float:left;width:33.33%;padding-right:4px;box-sizing:border-box;">' + buildColumnSvg(pageConfig.col1, colWidth) + '</div>';
  h += '<div style="float:left;width:33.33%;padding:0 2px;box-sizing:border-box;">' + buildColumnSvg(pageConfig.col2, colWidth) + '</div>';
  h += '<div style="float:left;width:33.34%;padding-left:4px;box-sizing:border-box;">' + buildColumnSvg(pageConfig.col3, colWidth) + '</div>';
  h += '</div>';
  
  // 结论说明
  h += '<div style="margin-top:6px;font-size:7px;color:#333;">结论选项中，符合打"√"，不符合打"×"，不适用打"/"，或写入测量值。</div>';
  
  // 页码
  h += '<div style="text-align:center;font-size:8px;margin-top:4px;">— ' + pageNum + ' —</div>';
  
  h += '</div>';
  
  return h;
}