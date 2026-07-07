// Mock browser environment
global.document = {
  getElementById: function(id) { return { value: '', innerHTML: '', style: {}, appendChild: function(){} }; },
  createElement: function(tag) { return { style: {}, innerHTML: '', appendChild: function(){}, getContext: function(){ return {}; } }; },
  body: { appendChild: function(){} },
  addEventListener: function(){}
};
global.window = global;
global.localStorage = {
  data: {},
  getItem: function(k) { return this.data[k] || null; },
  setItem: function(k, v) { this.data[k] = v; },
  removeItem: function(k) { delete this.data[k]; }
};
global.alert = function(msg) { console.log('Alert:', msg); };
global.console = console;

// Load the JS
var fs = require('fs');
var js = fs.readFileSync('/tmp/js503.js', 'utf8');

try {
  eval(js);
  console.log('JS evaluation succeeded');
  
  // Create a mock task with attachments
  var mockTask = {
    attachments: {
      attach2: {
        "轿厢缓冲距": '150',
        "对重缓冲距": '150',
        "轿厢压缩行程": '100',
        "对重压缩行程": '100',
        "顶部空间": {s1:'1.5',s2:'2.0',s3:'0.5',s4:'0.3',s5L:'1.0',s5W:'0.8',s5H:'2.0'},
        "底坑空间": {p1:'1.5',p2:'2.0',p3h:'0.2',p3v1:'0.8',p3v2:'0.6',p4:'1.2',p5L:'1.0',p5W:'0.8',p5H:'1.5'}
      }
    },
    checks: {}
  };
  
  // Mock getCurrentTask
  var origGetTask = getCurrentTask;
  getCurrentTask = function() { return mockTask; };
  
  // Mock getRatedSpeed
  var origGetSpeed = getRatedSpeed;
  getRatedSpeed = function() { return 1.6; };
  
  try {
    var container = document.createElement('div');
    renderAttach2(container);
    console.log('renderAttach2 succeeded');
    console.log('Container HTML length:', container.innerHTML.length);
  } catch(e) {
    console.log('renderAttach2 error:', e.message);
    console.log('Stack:', e.stack.split('\n').slice(0,5).join('\n'));
  }
  
} catch(e) {
  console.log('JS evaluation error:', e.message);
  console.log('Stack:', e.stack);
}
